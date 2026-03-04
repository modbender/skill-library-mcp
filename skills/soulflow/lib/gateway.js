/**
 * lib/gateway.js - WebSocket Gateway Client
 * Connects to OpenClaw gateway and provides methods for chat/sessions
 */

import fs from 'fs';
import path from 'path';
import os from 'os';
import { EventEmitter } from 'events';

export class GatewayClient extends EventEmitter {
  constructor() {
    super();
    this.ws = null;
    this.connected = false;
    this.authenticated = false;
    this.requestId = 0;
    this.pendingRequests = new Map();
    this.chatBuffers = new Map();
    this.config = null;
  }

  /**
   * Load OpenClaw config
   */
  loadConfig() {
    const configPath = path.join(os.homedir(), '.openclaw', 'openclaw.json');
    
    if (!fs.existsSync(configPath)) {
      throw new Error(`OpenClaw config not found at ${configPath}`);
    }
    
    const content = fs.readFileSync(configPath, 'utf8');
    this.config = JSON.parse(content);
    
    if (!this.config.gateway?.auth?.token) {
      throw new Error('No gateway auth token found in config');
    }
    
    return this.config;
  }

  /**
   * Connect to gateway WebSocket
   */
  async connect() {
    if (!this.config) {
      this.loadConfig();
    }
    
    const port = this.config.gateway?.port || 18789;
    const wsUrl = `ws://127.0.0.1:${port}`;
    
    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        if (this.ws) {
          this.ws.close();
        }
        reject(new Error('Connection timeout - gateway may not be responding'));
      }, 10000);
      
      let challenged = false;
      
      try {
        this.ws = new WebSocket(wsUrl);
        
        this.ws.onopen = () => {
          this.connected = true;
          // Wait for connect.challenge event from gateway
        };
        
        this.ws.onmessage = (event) => {
          let msg;
          try { msg = JSON.parse(event.data); } catch { return; }
          
          // Handle the connect.challenge → connect handshake
          if (msg.type === 'event' && msg.event === 'connect.challenge' && !challenged) {
            challenged = true;
            const token = this.config.gateway.auth.token;
            this.ws.send(JSON.stringify({
              type: 'req',
              id: String(++this.requestId),
              method: 'connect',
              params: {
                minProtocol: 3,
                maxProtocol: 3,
                client: { id: 'cli', version: '2026.2.9', platform: 'linux', mode: 'cli' },
                role: 'operator',
                scopes: ['operator.read', 'operator.write', 'operator.admin'],
                caps: [],
                commands: [],
                permissions: {},
                auth: { token },
                locale: 'en-US',
                userAgent: 'soulflow/1.0.0'
              }
            }));
            this._connectId = String(this.requestId);
            return;
          }
          
          // Handle connect response
          if (msg.type === 'res' && msg.id === this._connectId) {
            if (msg.ok) {
              this.authenticated = true;
              clearTimeout(timeout);
              // Switch to normal message handler
              this.ws.onmessage = (ev) => this.handleMessage(ev.data);
              resolve();
            } else {
              clearTimeout(timeout);
              reject(new Error(`Connect failed: ${msg.error?.message || 'unknown'}`));
            }
            return;
          }
        };
        
        this.ws.onerror = (error) => {
          clearTimeout(timeout);
          this.emit('error', error);
          reject(new Error(`WebSocket error: ${error.message || 'unknown'}`));
        };
        
        this.ws.onclose = (event) => {
          clearTimeout(timeout);
          this.connected = false;
          this.authenticated = false;
          this.emit('close');
          if (!this.authenticated) {
            reject(new Error(`Connection closed: ${event.reason || 'unknown'}`));
          }
        };
      } catch (err) {
        clearTimeout(timeout);
        reject(err);
      }
    });
  }

  /**
   * Handle incoming WebSocket message
   */
  handleMessage(data) {
    let msg;
    try {
      msg = JSON.parse(data);
    } catch (e) {
      console.error('[gateway] Invalid JSON:', data);
      return;
    }
    
    // Handle response to a pending request
    if (msg.type === 'res' && msg.id && this.pendingRequests.has(msg.id)) {
      const { resolve, reject } = this.pendingRequests.get(msg.id);
      this.pendingRequests.delete(msg.id);
      
      if (!msg.ok) {
        reject(new Error(msg.error?.message || 'Request failed'));
      } else {
        resolve(msg.payload || msg.result || { ok: true });
      }
      return;
    }
    
    // Handle chat events
    if (msg.type === 'event' && msg.event === 'chat' && msg.payload) {
      this.handleChatEvent(msg.payload);
      return;
    }
    
    // Other events
    this.emit('message', msg);
  }

  /**
   * Handle chat streaming events
   */
  handleChatEvent(payload) {
    const { sessionKey, state, message } = payload;
    
    if (!sessionKey) return;
    
    // Initialize buffer for this session if needed
    if (!this.chatBuffers.has(sessionKey)) {
      this.chatBuffers.set(sessionKey, {
        chunks: [],
        complete: false
      });
    }
    
    const buffer = this.chatBuffers.get(sessionKey);
    
    // Extract text from message content
    if (message?.content) {
      for (const part of message.content) {
        if (part.type === 'text' && part.text) {
          if (state === 'delta') {
            // Delta contains the FULL text so far (cumulative), not incremental
            // Just store the latest — we'll use the final one
            buffer.latestText = part.text;
          }
        }
      }
    }
    
    // Check for stream end — state "final" means complete
    if (state === 'final') {
      buffer.complete = true;
      // Use the final message text (most complete version)
      let fullText = '';
      if (message?.content) {
        for (const part of message.content) {
          if (part.type === 'text' && part.text) {
            fullText = part.text;
          }
        }
      }
      // Fallback to latest delta if final has no text
      if (!fullText && buffer.latestText) fullText = buffer.latestText;
      buffer.fullText = fullText;
      this.emit('chat_complete', { sessionKey, text: buffer.fullText });
    }
  }

  /**
   * Call a gateway method
   */
  async call(method, params = {}) {
    if (!this.connected) {
      throw new Error('Not connected to gateway');
    }
    
    return new Promise((resolve, reject) => {
      const id = String(++this.requestId);
      
      this.pendingRequests.set(id, { resolve, reject });
      
      const frame = JSON.stringify({ type: 'req', id, method, params });
      this.ws.send(frame);
      
      // Timeout after 30 seconds
      setTimeout(() => {
        if (this.pendingRequests.has(id)) {
          this.pendingRequests.delete(id);
          reject(new Error(`Request ${method} timed out`));
        }
      }, 30000);
    });
  }

  /**
   * Send a chat message and wait for complete response
   */
  async sendChat(sessionKey, message, agentId = 'main') {
    // Clear any existing buffer
    this.chatBuffers.delete(sessionKey);
    
    const idempotencyKey = `soulflow-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
    
    // Send the chat message — agentId is encoded in sessionKey, not as a param
    await this.call('chat.send', {
      sessionKey,
      message,
      idempotencyKey
    });
    
    // Wait for the response to complete
    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        reject(new Error('Chat response timeout'));
      }, 600000); // 10 minute timeout
      
      const checkComplete = () => {
        const buffer = this.chatBuffers.get(sessionKey);
        if (buffer && buffer.complete) {
          clearTimeout(timeout);
          this.removeListener('chat_complete', onComplete);
          resolve(buffer.fullText);
        }
      };
      
      const onComplete = (data) => {
        if (data.sessionKey === sessionKey) {
          clearTimeout(timeout);
          this.removeListener('chat_complete', onComplete);
          resolve(data.text);
        }
      };
      
      this.on('chat_complete', onComplete);
      
      // Check if already complete
      checkComplete();
    });
  }

  /**
   * Close connection
   */
  close() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.connected = false;
    this.authenticated = false;
  }
}
