#!/usr/bin/env node

/**
 * KKClaw Server - Optimized for Ubuntu/Raspbian as remote server
 * 
 * Features:
 * - Heartbeat mechanism
 * - Auto-reconnect
 * - Auto-recovery
 * - Auto queue management
 * - Model switching
 */

const fs = require('fs');
const path = require('path');
const { EventEmitter } = require('events');
const https = require('https');
const http = require('http');
const readline = require('readline');

// Colors
const C = {
  reset: '\x1b[0m', bright: '\x1b[1m', dim: '\x1b[2m',
  green: '\x1b[32m', red: '\x1b[31m', yellow: '\x1b[33m',
  cyan: '\x1b[36m', magenta: '\x1b[35m', gray: '\x1b[90m'
};

const log = (msg, color = 'reset') => console.log(`${C[color]}${msg}${C.reset}`);

// Default config
const DEFAULT_CONFIG = {
  gateway: {
    url: 'http://localhost:18789',
    apiKey: ''
  },
  heartbeat: {
    enabled: true,
    interval: 30000, // 30 seconds
    timeout: 10000
  },
  reconnect: {
    enabled: true,
    maxRetries: 10,
    baseDelay: 1000,
    maxDelay: 60000
  },
  recovery: {
    enabled: true,
    maxRestarts: 5,
    restartDelay: 5000
  },
  queue: {
    maxSize: 100,
    retryDelay: 5000,
    maxRetries: 3
  },
  models: {
    default: 'claude-opus-4-6',
    fallback: 'minimax-portal/MiniMax-M2.5',
    switchTimeout: 30000
  },
  logging: {
    level: 'info',
    maxFiles: 10,
    maxSize: '10M'
  }
};

class KKClawServer extends EventEmitter {
  constructor(config = {}) {
    super();
    this.config = { ...DEFAULT_CONFIG, ...config };
    this.connected = false;
    this.heartbeatTimer = null;
    this.reconnectAttempts = 0;
    this.recoveryAttempts = 0;
    this.messageQueue = [];
    this.currentModel = this.config.models.default;
    this.lastHeartbeat = null;
    this.status = 'disconnected';
  }

  // ============ Heartbeat Mechanism ============
  
  startHeartbeat() {
    if (!this.config.heartbeat.enabled) return;
    
    log('Starting heartbeat mechanism...', 'cyan');
    
    this.heartbeatTimer = setInterval(() => {
      this.sendHeartbeat();
    }, this.config.heartbeat.interval);
    
    // Initial heartbeat
    this.sendHeartbeat();
  }

  stopHeartbeat() {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }

  async sendHeartbeat() {
    const payload = {
      type: 'heartbeat',
      timestamp: Date.now(),
      status: this.status,
      model: this.currentModel,
      queueLength: this.messageQueue.length,
      uptime: process.uptime(),
      memory: process.memoryUsage()
    };
    
    try {
      const response = await this.apiRequest('/api/heartbeat', 'POST', payload);
      this.lastHeartbeat = Date.now();
      this.emit('heartbeat', response);
      log(`Heartbeat sent: ${response.status}`, 'green');
    } catch (e) {
      log(`Heartbeat failed: ${e.message}`, 'yellow');
      this.handleConnectionLoss();
    }
  }

  // ============ Auto Reconnect ============

  async connect() {
    if (this.connected) return;
    
    log(`Connecting to ${this.config.gateway.url}...`, 'cyan');
    
    try {
      const response = await this.apiRequest('/api/status', 'GET');
      this.connected = true;
      this.reconnectAttempts = 0;
      this.status = 'connected';
      log('Connected successfully!', 'green');
      this.emit('connected', response);
      this.startHeartbeat();
    } catch (e) {
      log(`Connection failed: ${e.message}`, 'red');
      this.handleConnectionLoss();
    }
  }

  handleConnectionLoss() {
    this.connected = false;
    this.status = 'disconnected';
    this.stopHeartbeat();
    this.emit('disconnected');
    
    if (this.config.reconnect.enabled) {
      this.scheduleReconnect();
    }
  }

  scheduleReconnect() {
    if (this.reconnectAttempts >= this.config.reconnect.maxRetries) {
      log('Max reconnection attempts reached', 'red');
      this.status = 'failed';
      this.emit('reconnectFailed');
      return;
    }
    
    this.reconnectAttempts++;
    const delay = Math.min(
      this.config.reconnect.baseDelay * Math.pow(2, this.reconnectAttempts - 1),
      this.config.reconnect.maxDelay
    );
    
    log(`Reconnecting in ${delay/1000}s (attempt ${this.reconnectAttempts}/${this.config.reconnect.maxRetries})...`, 'yellow');
    
    setTimeout(() => {
      this.connect();
    }, delay);
  }

  // ============ Auto Recovery ============

  async recover() {
    if (!this.config.recovery.enabled) return;
    
    log('Starting recovery process...', 'yellow');
    this.status = 'recovering';
    
    try {
      // Clear failed state
      await this.apiRequest('/api/session/clear', 'POST');
      
      // Restore queue
      await this.restoreQueue();
      
      // Switch to fallback model if needed
      if (this.currentModel !== this.config.models.default) {
        await this.switchModel(this.config.models.default);
      }
      
      this.recoveryAttempts = 0;
      this.status = 'connected';
      log('Recovery complete!', 'green');
      this.emit('recovered');
    } catch (e) {
      this.recoveryAttempts++;
      log(`Recovery failed: ${e.message}`, 'red');
      
      if (this.recoveryAttempts < this.config.recovery.maxRestarts) {
        setTimeout(() => this.recover(), this.config.recovery.restartDelay);
      } else {
        this.status = 'failed';
        this.emit('recoveryFailed');
      }
    }
  }

  // ============ Queue Management ============

  async sendMessage(message) {
    const queueItem = {
      id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      message,
      timestamp: Date.now(),
      retries: 0
    };
    
    // Check queue size
    if (this.messageQueue.length >= this.config.queue.maxSize) {
      log('Queue full, removing oldest message', 'yellow');
      this.messageQueue.shift();
    }
    
    this.messageQueue.push(queueItem);
    
    if (this.connected) {
      return this.processQueue();
    } else {
      log('Not connected, message queued', 'yellow');
      return { queued: true, queueId: queueItem.id };
    }
  }

  async processQueue() {
    const results = [];
    
    while (this.messageQueue.length > 0 && this.connected) {
      const item = this.messageQueue[0];
      
      try {
        const response = await this.apiRequest('/api/message', 'POST', {
          content: item.message
        });
        
        this.messageQueue.shift();
        results.push({ id: item.id, success: true, response });
        
        // Small delay between messages
        await this.delay(100);
      } catch (e) {
        item.retries++;
        
        if (item.retries >= this.config.queue.maxRetries) {
          log(`Message ${item.id} failed after ${item.retries} retries, removing`, 'red');
          this.messageQueue.shift();
          results.push({ id: item.id, success: false, error: e.message });
        } else {
          // Move to end of queue
          this.messageQueue.shift();
          this.messageQueue.push(item);
          log(`Message ${item.id} failed, will retry`, 'yellow');
          break;
        }
      }
    }
    
    return results;
  }

  async restoreQueue() {
    log(`Restoring queue: ${this.messageQueue.length} messages`, 'cyan');
    return this.processQueue();
  }

  // ============ Model Switching ============

  async switchModel(model) {
    log(`Switching to model: ${model}`, 'cyan');
    this.status = 'switching';
    
    const previousModel = this.currentModel;
    
    try {
      // Notify gateway
      await this.apiRequest('/api/model/switch', 'POST', {
        model,
        previousModel
      });
      
      this.currentModel = model;
      this.status = 'connected';
      log(`Model switched to: ${model}`, 'green');
      this.emit('modelSwitched', { from: previousModel, to: model });
      
      return { success: true, model };
    } catch (e) {
      log(`Model switch failed: ${e.message}`, 'red');
      
      // Auto rollback
      if (previousModel !== model) {
        log('Auto-rollback to previous model...', 'yellow');
        this.currentModel = previousModel;
      }
      
      this.status = 'connected';
      this.emit('modelSwitchFailed', { model, error: e.message });
      
      return { success: false, error: e.message };
    }
  }

  async getAvailableModels() {
    try {
      const response = await this.apiRequest('/api/models', 'GET');
      return response.models || [];
    } catch (e) {
      log(`Failed to get models: ${e.message}`, 'red');
      return [];
    }
  }

  // ============ API Helper ============

  async apiRequest(endpoint, method = 'GET', data = null) {
    return new Promise((resolve, reject) => {
      const url = new URL(endpoint, this.config.gateway.url);
      
      const options = {
        hostname: url.hostname,
        port: url.port,
        path: url.pathname + url.search,
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.config.gateway.apiKey}`
        },
        timeout: this.config.heartbeat.timeout
      };
      
      const req = (url.protocol === 'https:' ? https : http).request(options, (res) => {
        let body = '';
        res.on('data', c => body += c);
        res.on('end', () => {
          try {
            const json = JSON.parse(body);
            if (res.statusCode >= 200 && res.statusCode < 300) {
              resolve(json);
            } else {
              reject(new Error(`HTTP ${res.statusCode}: ${json.error || body}`));
            }
          } catch (e) {
            reject(new Error(`Invalid JSON: ${body}`));
          }
        });
      });
      
      req.on('error', reject);
      req.on('timeout', () => {
        req.destroy();
        reject(new Error('Request timeout'));
      });
      
      if (data) {
        req.write(JSON.stringify(data));
      }
      
      req.end();
    });
  }

  delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // ============ Status ============

  getStatus() {
    return {
      status: this.status,
      connected: this.connected,
      currentModel: this.currentModel,
      queueLength: this.messageQueue.length,
      reconnectAttempts: this.reconnectAttempts,
      recoveryAttempts: this.recoveryAttempts,
      lastHeartbeat: this.lastHeartbeat,
      uptime: process.uptime()
    };
  }

  // ============ Lifecycle ============

  start() {
    log(C.bright + '\n=== KKClaw Server Started ===' + C.reset, 'cyan');
    log(`Mode: ${this.config.heartbeat.enabled ? 'Server/Headless' : 'Client'}`);
    log(`Heartbeat: ${this.config.heartbeat.enabled ? 'Enabled' : 'Disabled'}`);
    log(`Auto-reconnect: ${this.config.reconnect.enabled ? 'Enabled' : 'Disabled'}`);
    log(`Auto-recovery: ${this.config.recovery.enabled ? 'Enabled' : 'Disabled'}`);
    log(`Default model: ${this.config.models.default}\n`);
    
    this.connect();
    
    // Graceful shutdown
    process.on('SIGINT', () => this.shutdown());
    process.on('SIGTERM', () => this.shutdown());
  }

  shutdown() {
    log('\nShutting down...', 'yellow');
    this.stopHeartbeat();
    this.connected = false;
    process.exit(0);
  }
}

// CLI
function main() {
  const args = process.argv.slice(2);
  const cmd = args[0];
  
  // Load config
  const configPath = path.join(process.env.HOME || '/home/crix', '.kkclaw/config.json');
  let config = DEFAULT_CONFIG;
  
  if (fs.existsSync(configPath)) {
    try {
      config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
    } catch (e) {
      log(`Failed to load config: ${e.message}`, 'yellow');
    }
  }
  
  const server = new KKClawServer(config);
  
  switch (cmd) {
    case 'start':
    case 'run':
      server.start();
      break;
      
    case 'status':
      console.log(JSON.stringify(server.getStatus(), null, 2));
      break;
      
    case 'connect':
      server.connect();
      break;
      
    case 'model':
      const model = args[1];
      if (!model) {
        log('Usage: kkclaw-server model <model-name>');
        process.exit(1);
      }
      server.connect().then(() => server.switchModel(model));
      break;
      
    case 'queue':
      console.log(`Queue length: ${server.messageQueue.length}`);
      break;
      
    case 'init':
      // Create config
      const configDir = path.dirname(configPath);
      if (!fs.existsSync(configDir)) {
        fs.mkdirSync(configDir, { recursive: true });
      }
      fs.writeFileSync(configPath, JSON.stringify(DEFAULT_CONFIG, null, 2));
      log(`Config created at ${configPath}`, 'green');
      break;
      
    default:
      log(C.bright + `
KKClaw Server - Optimized for Ubuntu/Raspbian

USAGE:
  kkclaw-server init          Create default config
  kkclaw-server start        Start server
  kkclaw-server status       Show status
  kkclaw-server connect      Manual connect
  kkclaw-server model <name> Switch model

CONFIG:
  ~/.kkclaw/config.json
      ` + C.reset, 'cyan');
  }
}

main();
