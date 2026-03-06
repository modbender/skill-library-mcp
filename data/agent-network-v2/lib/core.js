const crypto = require('crypto');
const EventEmitter = require('events');

class AgentNetwork extends EventEmitter {
  constructor(db, p2p) {
    super();
    this.db = db;
    this.p2p = p2p;
    this.nodeId = p2p.peerId;
    this.connections = new Map();
  }
  
  async start() {
    // Register message handlers
    this.p2p.onMessage('message', this.handleMessage.bind(this));
    this.p2p.onMessage('appreciation', this.handleAppreciation.bind(this));
    this.p2p.onMessage('skill_update', this.handleSkillUpdate.bind(this));
    this.p2p.onMessage('skill_share', this.handleSkillShare.bind(this));
    
    // Register peer event handlers
    this.p2p.on('peer_connected', this.handlePeerConnected.bind(this));
    this.p2p.on('peer_disconnected', this.handlePeerDisconnected.bind(this));
    this.p2p.on('greeting_sent', this.handleGreetingSent.bind(this));
    this.p2p.on('message', this.handleIncomingMessage.bind(this));
    
    // Ensure we have a balance record
    const balance = this.db.get('SELECT * FROM balances WHERE agent_id = ?', [this.nodeId]);
    if (!balance) {
      this.db.run('INSERT INTO balances (agent_id, points) VALUES (?, ?)', [this.nodeId, 100]);
    }
    
    console.log('Core module started, nodeId:', this.nodeId);
  }
  
  // Handle incoming messages (auto-reply to greetings)
  handleIncomingMessage(payload) {
    const { from, content, type } = payload;
    
    // Store in database
    this.db.run(
      'INSERT INTO messages (from_agent, to_agent, content, message_type) VALUES (?, ?, ?, ?)',
      [from, this.nodeId, content, type || 'text']
    );
    
    // Auto reply to greetings
    if (type === 'greeting') {
      // Simple auto-reply logic
      const replies = [
        "Nice to meet you too!",
        "Hello! Happy to connect with you!",
        "Hi there! Welcome to the network!",
        "Greetings! Let's share knowledge!"
      ];
      const reply = replies[Math.floor(Math.random() * replies.length)];
      
      setTimeout(() => {
        this.sendMessage(from, reply, 'auto_reply');
      }, 1500);
    }
    
    // Emit event
    this.emit('new_message', { from, to: this.nodeId, content, type });
  }
  
  // Handle greeting sent confirmation
  handleGreetingSent(payload) {
    console.log(`Auto greeting sent to ${payload.to}`);
  }
  
  // Handle skill sharing from peers
  handleSkillShare(payload, fromPeerId) {
    const { skillId, skillName, description, price } = payload;
    
    console.log(`Received skill share from ${fromPeerId}: ${skillName}`);
    
    // Emit event for UI updates
    this.emit('skill_received', { 
      from: fromPeerId, 
      skillId, 
      skillName, 
      description, 
      price 
    });
  }
  
  // Handle incoming messages
  handleMessage(payload, fromPeerId) {
    const { from, to, content, messageType } = payload;
    
    // Store in database
    this.db.run(
      'INSERT INTO messages (from_agent, to_agent, content, message_type) VALUES (?, ?, ?, ?)',
      [from, to || this.nodeId, content, messageType || 'text']
    );
    
    // Emit event
    this.emit('new_message', { from, to: to || this.nodeId, content, type: messageType });
  }
  
  // Handle appreciation requests
  handleAppreciation(payload, fromPeerId) {
    const { from, to, action } = payload;
    
    if (action === 'request') {
      const existing = this.db.get(
        'SELECT * FROM connections WHERE agent_id = ? AND peer_id = ?',
        [to, from]
      );
      
      if (!existing) {
        this.db.run(
          'INSERT INTO connections (agent_id, peer_id, status) VALUES (?, ?, ?)',
          [to, from, 'pending']
        );
      }
      
      this.emit('appreciation_request', { from, to });
    } else if (action === 'accept') {
      this.db.run(
        'UPDATE connections SET status = ? WHERE agent_id = ? AND peer_id = ?',
        ['accepted', to, from]
      );
      
      this.db.run(
        'UPDATE agents SET reputation_score = reputation_score + 10 WHERE id = ?',
        [from]
      );
      
      this.emit('connection_established', { from, to });
    }
  }
  
  // Handle skill updates
  handleSkillUpdate(payload, fromPeerId) {
    const { action, skillId, owner, name, price } = payload;
    
    if (action === 'published') {
      console.log(`Skill published: ${name} (${skillId})`);
    }
    
    this.emit('skill_update', payload);
  }
  
  // Handle peer connected
  async handlePeerConnected(peerId, info) {
    console.log(`Peer connected: ${peerId}`);
    
    // Add to agents table if not exists
    const existing = this.db.get('SELECT * FROM agents WHERE id = ?', [peerId]);
    if (!existing) {
      this.db.run(
        'INSERT INTO agents (id, name, last_active) VALUES (?, ?, ?)',
        [peerId, info.name || peerId, new Date().toISOString()]
      );
    }
  }
  
  // Handle peer disconnected
  handlePeerDisconnected(peerId) {
    console.log(`Peer disconnected: ${peerId}`);
    this.db.run(
      'UPDATE agents SET last_active = ? WHERE id = ?',
      [new Date().toISOString(), peerId]
    );
  }
  
  // Send appreciation request
  async sendAppreciation(peerId) {
    const message = {
      type: 'appreciation',
      from: this.nodeId,
      to: peerId,
      action: 'request',
      timestamp: Date.now()
    };
    
    this.p2p.broadcast(message);
    
    this.db.run(
      'INSERT OR REPLACE INTO connections (agent_id, peer_id, status) VALUES (?, ?, ?)',
      [this.nodeId, peerId, 'pending']
    );
    
    return true;
  }
  
  // Accept appreciation
  async acceptAppreciation(peerId) {
    const message = {
      type: 'appreciation',
      from: this.nodeId,
      to: peerId,
      action: 'accept',
      timestamp: Date.now()
    };
    
    this.p2p.broadcast(message);
    
    this.db.run(
      'UPDATE connections SET status = ? WHERE agent_id = ? AND peer_id = ?',
      ['accepted', peerId, this.nodeId]
    );
    
    return true;
  }
  
  // Send message to a peer
  async sendMessage(to, content, type = 'text') {
    const message = {
      from: this.nodeId,
      to,
      content,
      messageType: type,
      timestamp: Date.now()
    };
    
    const sent = this.p2p.send(to, message);
    
    this.db.run(
      'INSERT INTO messages (from_agent, to_agent, content, message_type) VALUES (?, ?, ?, ?)',
      [this.nodeId, to, content, type]
    );
    
    return sent;
  }
  
  // Get message history with a peer
  async getMessageHistory(peerId, limit = 50) {
    return this.db.all(
      `SELECT * FROM messages 
       WHERE (from_agent = ? AND to_agent = ?) OR (from_agent = ? AND to_agent = ?)
       ORDER BY created_at DESC LIMIT ?`,
      [this.nodeId, peerId, peerId, this.nodeId, limit]
    );
  }
  
  // Get connection list
  async getConnections() {
    return this.db.all(
      `SELECT * FROM connections WHERE status = 'accepted' 
       AND (agent_id = ? OR peer_id = ?)`,
      [this.nodeId, this.nodeId]
    );
  }
  
  // Get pending appreciation requests
  async getPendingRequests() {
    return this.db.all(
      `SELECT * FROM connections WHERE status = 'pending' AND peer_id = ?`,
      [this.nodeId]
    );
  }
  
  // Discover peers
  async discoverPeers() {
    this.p2p.broadcast({ type: 'discover_request' });
    return this.p2p.getPeers();
  }
  
  // Share skill with all connected peers
  async shareSkill(skillId, skillName, description = '', price = 0) {
    this.p2p.shareSkill(skillId, skillName, description, price);
    return true;
  }
  
  async stop() {
    console.log('Core module stopped');
  }
}

module.exports = { AgentNetwork };
