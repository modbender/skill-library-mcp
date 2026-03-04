const https = require('https');
const crypto = require('crypto');

const EVOMAP_API = 'https://evomap.ai';

class EvoMapClient {
  constructor(nodeId) {
    this.nodeId = nodeId || 'node_' + crypto.randomBytes(4).toString('hex');
    this.baseUrl = EVOMAP_API;
  }
  
  buildEnvelope(messageType, payload = {}) {
    return {
      protocol: 'gep-a2a',
      protocol_version: '1.0.0',
      message_type: messageType,
      message_id: 'msg_' + Date.now() + '_' + crypto.randomBytes(4).toString('hex'),
      sender_id: this.nodeId,
      timestamp: new Date().toISOString(),
      payload
    };
  }
  
  request(endpoint, method = 'GET', data = null) {
    return new Promise((resolve) => {
      try {
        const url = new URL(endpoint, this.baseUrl);
        const options = {
          hostname: url.hostname,
          port: 443,
          path: url.pathname,
          method: method,
          headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' }
        };
        
        const req = https.request(options, (res) => {
          let body = '';
          res.on('data', chunk => body += chunk);
          res.on('end', () => {
            try { resolve(JSON.parse(body)); } 
            catch (e) { resolve({ raw: body }); }
          });
        });
        
        req.on('error', () => resolve({ error: 'network' }));
        req.setTimeout(3000, () => { req.destroy(); resolve({ error: 'timeout' }); });
        
        if (data) req.write(JSON.stringify(data));
        req.end();
      } catch (e) {
        resolve({ error: e.message });
      }
    });
  }
  
  async hello(capabilities = [], metadata = {}) {
    const envelope = this.buildEnvelope('hello', {
      capabilities,
      metadata: { ...metadata, version: '1.0.9', protocol: 'agent-network' }
    });
    return this.request('/a2a/hello', 'POST', envelope);
  }
  
  async sendMessage(targetNodeId, message, messageType = 'text') {
    const envelope = this.buildEnvelope('hello', {
      target_id: targetNodeId,
      content: message,
      message_type: messageType
    });
    return this.request('/a2a/hello', 'POST', envelope);
  }
  
  // Auto-handshake with discovered agents
  async handshake(targetNodeId) {
    const envelope = this.buildEnvelope('hello', {
      target_id: targetNodeId,
      action: 'handshake',
      info: {
        nodeId: this.nodeId,
        version: '1.1.0',
        capabilities: ['chat', 'skills', 'p2p'],
        services: { p2p: { port: 18793 }, api: { port: 18794 } }
      }
    });
    return this.request('/a2a/hello', 'POST', envelope);
  }
  
  async getDirectory(limit = 50) {
    return this.request(`/a2a/directory?limit=${limit}`);
  }
  
  async discoverAgents() {
    try {
      const result = await this.getDirectory(50);
      return result.agents || [];
    } catch (e) { return []; }
  }
}

module.exports = { EvoMapClient };
