const WebSocket = require('ws');
const http = require('http');
const https = require('https');
const crypto = require('crypto');
const EventEmitter = require('events');
const fs = require('fs');
const path = require('path');

class P2PServer extends EventEmitter {
  constructor(port, config = {}) {
    super();
    this.port = port;
    this.config = {
      autoGreet: config.autoGreet !== false,
      greetMessage: config.greetMessage || "Hi! I'm OpenClaw Agent. Nice to meet you!",
      seedNodes: config.seedNodes || [
        // EvoMap seed nodes can be added here
      ],
      httpAgents: config.httpAgents || [],  // HTTP-based agents
      ...config
    };
    this.server = null;
    this.connections = new Map(); // peerId -> { ws, info, type }
    const idPath = path.join(process.env.HOME || '.', '.openclaw', 'agent-nodeid.txt');
    if (fs.existsSync(idPath)) {
      this.peerId = fs.readFileSync(idPath, 'utf8').trim();
    } else {
      // Load or generate persistent peerId
    const idPath = path.join(process.env.HOME || '.', '.openclaw', 'agent-nodeid.txt');
    if (fs.existsSync(idPath)) {
      this.peerId = fs.readFileSync(idPath, 'utf8').trim();
    } else {
      this.peerId = 'node_' + crypto.randomBytes(8).toString('hex');
      fs.writeFileSync(idPath, this.peerId);
    }
      fs.writeFileSync(idPath, this.peerId);
    }
    this.messageHandlers = new Map();
    this.wss = null;
    this.httpAgents = new Map(); // HTTP agents we're connected to
  }
  
  async start() {
    return new Promise((resolve, reject) => {
      this.wss = new WebSocket.Server({ port: this.port });
      
      this.wss.on('listening', () => {
        console.log(`P2P server listening on port ${this.port}`);
        // Start discovering HTTP agents
        this.startHTTPAgentDiscovery();
        resolve();
      });
      
      this.wss.on('error', (err) => {
        console.error('P2P server error:', err);
        reject(err);
      });
      
      this.wss.on('connection', (ws, req) => {
        this.handleConnection(ws, req);
      });
    });
  }
  
  // Discover agents via HTTP (like EvoMap)
  async startHTTPAgentDiscovery() {
    // Check EvoMap directory periodically
    setInterval(async () => {
      try {
        const agents = await this.fetchEvoMapDirectory();
        for (const agent of agents.slice(0, 10)) {
          if (!this.httpAgents.has(agent.node_id)) {
            await this.connectToHTTPAgent(agent.node_id, agent);
          }
        }
      } catch (e) {
        // Silent fail for HTTP discovery
      }
    }, 60000); // Every minute
    
    // Initial discovery
    setTimeout(async () => {
      try {
        const agents = await this.fetchEvoMapDirectory();
        console.log(`Discovered ${agents.length} agents from EvoMap network`);
      } catch (e) {}
    }, 5000);
  }
  
  // Fetch EvoMap directory
  async fetchEvoMapDirectory() {
    return new Promise((resolve, reject) => {
      const req = https.get('https://evomap.ai/a2a/directory', (res) => {
        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => {
          try {
            const json = JSON.parse(data);
            resolve(json.agents || []);
          } catch (e) {
            resolve([]);
          }
        });
      });
      req.on('error', () => resolve([]));
      req.setTimeout(5000, () => { req.destroy(); resolve([]); });
    });
  }
  
  // Connect to HTTP-based agent (like EvoMap)
  async connectToHTTPAgent(agentId, agentInfo) {
    try {
      // For EvoMap agents, we can't directly connect via WebSocket
      // But we can track them and communicate via their endpoints
      this.httpAgents.set(agentId, {
        type: 'http',
        info: agentInfo,
        lastSeen: Date.now()
      });
      console.log(`Registered HTTP agent: ${agentId}`);
      this.emit('http_agent_found', { agentId, info: agentInfo });
    } catch (e) {
      console.error(`Failed to connect to HTTP agent ${agentId}:`, e.message);
    }
  }
  
  // Send message via HTTP (to agents that don't support WebSocket)
  async sendHTTPMessage(agentId, message) {
    const agent = this.httpAgents.get(agentId);
    if (!agent || agent.type !== 'http') return false;
    
    try {
      // EvoMap uses POST /a2a/hello for messages
      const postData = JSON.stringify({
        sender_id: this.peerId,
        message: message.content,
        message_type: message.messageType || 'text'
      });
      
      const req = https.request({
        hostname: 'evomap.ai',
        port: 443,
        path: '/a2a/hello',
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Content-Length': Buffer.byteLength(postData)
        }
      }, (res) => {
        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => {
          console.log(`Message sent to ${agentId}`);
        });
      });
      
      req.on('error', () => {});
      req.write(postData);
      req.end();
      return true;
    } catch (e) {
      return false;
    }
  }
  
  handleConnection(ws, req) {
    console.log('New P2P connection from:', req.socket.remoteAddress);
    
    ws.on('message', (data) => {
      try {
        const message = JSON.parse(data.toString());
        this.handleMessage(ws, message);
      } catch (e) {
        console.error('Failed to parse message:', e.message);
      }
    });
    
    ws.on('close', () => {
      for (const [peerId, conn] of this.connections.entries()) {
        if (conn.ws === ws) {
          this.connections.delete(peerId);
          this.emit('peer_disconnected', peerId);
          break;
        }
      }
    });
    
    ws.on('error', (err) => {
      console.error('Connection error:', err.message);
    });
    
    // Send handshake
    ws.send(JSON.stringify({
      type: 'handshake',
      peerId: this.peerId,
      port: this.port,
      name: 'OpenClaw Agent',
      version: '1.0.4'
    }));
  }
  
  handleMessage(ws, message) {
    const { type, peerId, payload } = message;
    
    switch (type) {
      case 'handshake':
        this.connections.set(peerId, { ws, info: payload, type: 'websocket' });
        this.emit('peer_connected', peerId, payload);
        console.log(`Peer connected: ${peerId}`);
        
        if (this.config.autoGreet && payload.name) {
          setTimeout(() => {
            this.sendGreeting(peerId);
          }, 1000);
        }
        break;
        
      case 'message':
        this.handlePeerMessage(peerId, payload);
        break;
        
      case 'discover_request':
        this.handleDiscoverRequest(ws, peerId);
        break;
        
      case 'skill_share':
        this.handleSkillShare(peerId, payload);
        break;
        
      default:
        if (this.messageHandlers.has(type)) {
          this.messageHandlers.get(type)(payload, peerId);
        }
    }
  }
  
  sendGreeting(peerId) {
    const greeting = {
      type: 'message',
      from: this.peerId,
      payload: {
        content: this.config.greetMessage,
        messageType: 'greeting',
        timestamp: Date.now()
      }
    };
    
    this.send(peerId, greeting.payload);
    console.log(`Auto greeting sent to ${peerId}`);
    this.emit('greeting_sent', { to: peerId, message: this.config.greetMessage });
  }
  
  handleSkillShare(peerId, payload) {
    const { skillId, skillName, description, price } = payload;
    console.log(`Skill shared by ${peerId}: ${skillName}`);
    this.emit('skill_shared', { from: peerId, skillId, skillName, description, price });
  }
  
  handlePeerMessage(fromPeerId, payload) {
    const { to, content, messageType } = payload;
    
    if (to === this.peerId) {
      this.emit('message', { 
        from: fromPeerId, 
        content, 
        type: messageType,
        timestamp: payload.timestamp 
      });
    } else {
      // Forward to recipient (WebSocket peers only)
      const conn = this.connections.get(to);
      if (conn && conn.ws.readyState === WebSocket.OPEN) {
        conn.ws.send(JSON.stringify({
          type: 'message',
          peerId: this.peerId,
          payload: { from: fromPeerId, content, messageType }
        }));
      }
    }
  }
  
  handleDiscoverRequest(ws, requesterId) {
    const peers = Array.from(this.connections.keys());
    ws.send(JSON.stringify({
      type: 'discover_response',
      peerId: this.peerId,
      payload: { peers }
    }));
  }
  
  async connect(address) {
    return new Promise((resolve, reject) => {
      const ws = new WebSocket(`ws://${address}`);
      
      ws.on('open', () => {
        console.log(`Connected to ${address}`);
        resolve(ws);
      });
      
      ws.on('error', (err) => {
        console.error(`Failed to connect to ${address}:`, err.message);
        reject(err);
      });
      
      ws.on('message', (data) => {
        try {
          const message = JSON.parse(data.toString());
          this.handleMessage(ws, message);
        } catch (e) {
          console.error('Failed to parse message:', e.message);
        }
      });
    });
  }
  
  send(toPeerId, payload) {
    // First try WebSocket
    const conn = this.connections.get(toPeerId);
    if (conn && conn.ws.readyState === WebSocket.OPEN) {
      conn.ws.send(JSON.stringify({
        type: 'message',
        peerId: this.peerId,
        payload
      }));
      return true;
    }
    
    // Try HTTP if available
    if (this.httpAgents.has(toPeerId)) {
      return this.sendHTTPMessage(toPeerId, payload);
    }
    
    return false;
  }
  
  shareSkill(skillId, skillName, description = '', price = 0) {
    const payload = { skillId, skillName, description, price, sharedAt: Date.now() };
    
    this.broadcast({ type: 'skill_share', payload });
  }
  
  broadcast(message) {
    const msgStr = JSON.stringify({
      type: 'broadcast',
      peerId: this.peerId,
      payload: message
    });
    
    for (const [peerId, conn] of this.connections.entries()) {
      if (conn.ws.readyState === WebSocket.OPEN) {
        conn.ws.send(msgStr);
      }
    }
  }
  
  getPeers() {
    return Array.from(this.connections.keys());
  }
  
  // Get all discovered agents (WebSocket + HTTP)
  getAllAgents() {
    const agents = {
      websocket: Array.from(this.connections.keys()),
      http: Array.from(this.httpAgents.keys())
    };
    return agents;
  }
  
  onMessage(type, handler) {
    this.messageHandlers.set(type, handler);
  }
  
  async stop() {
    for (const [peerId, conn] of this.connections.entries()) {
      conn.ws.close();
    }
    this.connections.clear();
    this.httpAgents.clear();
    
    if (this.wss) {
      return new Promise((resolve) => {
        this.wss.close(() => {
          console.log('P2P server stopped');
          resolve();
        });
      });
    }
  }
}

module.exports = { P2PServer };
module.exports = { P2PServer };
