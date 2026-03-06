const WebSocket = require('ws');
const crypto = require('crypto');
const EventEmitter = require('events');

const DEFAULT_RELAYS = [
  'wss://relay.doctormcfly.com',
  'wss://relay.olas.app',
  'wss://nos.lol',
  'wss://eden.nostr.land',
  'wss://relay.nostr.band'
];

class NostrClient extends EventEmitter {
  constructor(config = {}) {
    super();
    this.config = {
      relays: config.relays || DEFAULT_RELAYS,
      ...config
    };
    
    // Generate keypair
    this.privateKey = crypto.randomBytes(32).toString('hex');
    this.publicKey = crypto.createHash('sha256').update(this.privateKey).digest('hex');
    this.nodeId = 'nostr_' + this.publicKey.substring(0, 16);
    
    this.sockets = new Map();
    this.subscriptions = new Map();
    this.connected = false;
  }
  
  async connect() {
    console.log('Nostr: Connecting to relays...');
    
    for (const relay of this.config.relays) {
      try {
        const ws = new WebSocket(relay);
        
        ws.on('open', () => {
          console.log(`Nostr: Connected to ${relay.substring(5, 30)}...`);
          this.connected = true;
          this.subscribe('openclaw_agents');
        });
        
        ws.on('message', (data) => {
          try {
            const msg = JSON.parse(data.toString());
            this.handleMessage(msg);
          } catch (e) {}
        });
        
        ws.on('error', (err) => {});
        ws.on('close', () => {
          this.sockets.delete(relay);
        });
        
        this.sockets.set(relay, { ws, subscribed: [] });
      } catch (e) {}
    }
  }
  
  subscribe(filter) {
    const subscriptionId = 'sub_' + Date.now();
    const msg = ['REQ', subscriptionId, { kinds: [1, 4, 30023], '#t': [filter] }];
    
    for (const [relay, conn] of this.sockets) {
      if (conn.ws.readyState === WebSocket.OPEN) {
        conn.ws.send(JSON.stringify(msg));
        conn.subscribed.push(subscriptionId);
      }
    }
    
    this.subscriptions.set(subscriptionId, filter);
  }
  
  handleMessage(msg) {
    if (!Array.isArray(msg) || msg.length < 3) return;
    
    const [type, subId, event] = msg;
    
    if (type === 'EVENT' && event && event.tags) {
      // Check for agent discovery
      const tag = event.tags.find(t => t[0] === 't' && t[1] === 'openclaw_agents');
      if (tag) {
        try {
          const data = JSON.parse(event.content);
          this.emit('agentFound', {
            pubkey: event.pubkey,
            ...data
          });
        } catch (e) {}
      }
    }
  }
  
  async broadcast(type = 'openclaw_agents', content = {}) {
    const event = {
      kind: 1,
      created_at: Math.floor(Date.now() / 1000),
      tags: [['t', type]],
      content: JSON.stringify({
        nodeId: this.nodeId,
        protocol: 'agent-network',
        version: '1.0.7',
        services: ['p2p', 'chat', 'skills'],
        ...content
      })
    };
    
    event.sig = crypto.createHash('sha256').update(JSON.stringify(event)).digest('hex');
    
    for (const [relay, conn] of this.sockets) {
      if (conn.ws.readyState === WebSocket.OPEN) {
        conn.ws.send(JSON.stringify(['EVENT', event]));
      }
    }
  }
  
  isConnected() {
    return this.connected;
  }
  
  getPublicKey() {
    return this.publicKey;
  }
  
  getNodeId() {
    return this.nodeId;
  }
  
  disconnect() {
    for (const [relay, conn] of this.sockets) {
      conn.ws.close();
    }
  }
}

module.exports = { NostrClient, DEFAULT_RELAYS };
