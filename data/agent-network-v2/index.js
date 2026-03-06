const { Database } = require('./lib/db');
const { P2PServer } = require('./lib/network');
const { LocalNetworkDiscovery } = require('./lib/discovery');
const { AutoHandshake } = require('./lib/network'); // Commented out
const { NostrClient } = require('./lib/nostr');
const { EvoMapClient } = require('./lib/evomap');
const { AgentNetwork } = require('./lib/core');
const { SkillsManager } = require('./lib/skills');
const { SharingManager } = require('./lib/sharing');
const http = require('http');

class AgentNetworkSkill {
  constructor(config = {}) {
    this.config = {
      port: config.port || 18794,
      window: config.window || { enabled: false },
      ...config
    };
    
    this.db = null;
    this.p2p = null;
    this.core = null;
    this.skills = null;
    this.running = false;
    this.httpServer = null;
    this.localDiscovery = null;
    this.nostr = null;
    this.evomap = null;
  }
  
  async start() {
    try {
      console.log('Starting Agent Network...');
      
      // Initialize database
      this.db = new Database();
      await this.db.initialize();
      console.log('✓ Database initialized');
      
      // Initialize P2P server
      this.p2p = new P2PServer(this.config.port);
      await this.p2p.start();
      console.log(`✓ P2P server started on port ${this.config.port}`);
    
    // Start Nostr network
    try {
      this.nostr = new NostrClient();
      await this.nostr.connect();
      // Broadcast presence
      await this.nostr.broadcast();
      console.log(`✓ Nostr connected, pubkey: ${this.nostr.getPublicKey().substring(0, 8)}...`);
    } catch(e) {
      console.log(` Nostr error: ${e.message}`);
    }
    
    // Initialize EvoMap client
    try {
      this.evomap = new EvoMapClient(this.nodeId);
      await this.evomap.hello(['chat', 'skills', 'p2p'], { services: ['p2p', 'chat', 'skills'] });
      console.log('✓ EvoMap registered');
      
      // Auto-handshake with discovered agents
      const agents = await this.evomap.discoverAgents();
      console.log(`Discovered ${agents.length} agents from EvoMap network`);
      
      for (const agent of agents.slice(0, 3)) {
        setTimeout(async () => {
          try {
            await this.evomap.handshake(agent.node_id);
            console.log(`🤝 Auto-handshake sent to ${agent.node_id}`);
            this.core.db.run(`INSERT OR IGNORE INTO connections (peer_id, status, connected_at) VALUES (?, 'accepted', ?)`, [agent.node_id, Date.now()]);
          } catch(e) {}
        }, Math.random() * 3000 + 1000);
      }
    } catch(e) {
      console.log(` EvoMap error: ${e.message}`);
    }
    
    // Start local network discovery
    this.localDiscovery = new LocalNetworkDiscovery(this.p2p);
    this.localDiscovery.start();
    
    // Start auto-handshake
      
      // Initialize core module
      this.core = new AgentNetwork(this.db, this.p2p);
      await this.core.start();
      console.log('✓ Core module started');
      
      // Initialize skills manager
      this.skills = new SkillsManager(this.db, this.p2p);
      await this.skills.start();
      console.log('✓ Skills manager started');
      
      // Start HTTP API server
      this.startHttpServer();
      
      this.running = true;
      console.log('\n🎉 Agent Network v1.2.0 is running!');
      console.log(`   Node ID: ${this.p2p.peerId}`);
      console.log(`   P2P Port: ${this.config.port}`);
      console.log(`   HTTP API: ${this.config.port + 1}`);
      
      const balance = await this.skills.getBalance(this.p2p.peerId);
      console.log(`   Points: ${balance}\n`);
      
    } catch (error) {
      console.error('Failed to start:', error);
      throw error;
    }
  }
  
  startHttpServer() {
    this.httpServer = http.createServer(async (req, res) => {
      res.setHeader('Access-Control-Allow-Origin', '*');
      res.setHeader('Content-Type', 'application/json');
      
      const sendError = (msg) => {
        res.end(JSON.stringify({ error: msg }));
      };
      
      const sendSuccess = (data) => {
        res.end(JSON.stringify(data));
      };
      
      try {
        // Status
        if (req.url === '/api/status' && req.method === 'GET') {
          const balance = await this.skills.getBalance(this.p2p.peerId);
          const connections = await this.core.getConnections();
          sendSuccess({
            nodeId: this.p2p.peerId,
            version: '1.2.0',
            balance,
            connections: connections.length,
            peers: this.p2p.getPeers().length
          });
        }
        // Connections list
        else if (req.url === '/api/connections' && req.method === 'GET') {
          const connections = await this.core.getConnections();
          sendSuccess(connections);
        }
        // Get all conversations
        else if (req.url === '/api/conversations' && req.method === 'GET') {
          const messages = this.db.all(`
            SELECT from_agent as peer_id FROM messages WHERE to_agent = ? 
            UNION 
            SELECT to_agent as peer_id FROM messages WHERE from_agent = ? 
          `, [this.nodeId, this.nodeId]);
          const peers = [...new Set(messages.map(m => m.peer_id))];
          const conversations = [];
          for (const peerId of peers) {
            const lastMsg = this.db.get(`SELECT * FROM messages WHERE (from_agent = ? AND to_agent = ?) OR (from_agent = ? AND to_agent = ?) ORDER BY created_at DESC LIMIT 1`, [this.nodeId, peerId, peerId, this.nodeId]);
            conversations.push({ peer_id: peerId, last_message: lastMsg?.content, last_time: lastMsg?.created_at, type: lastMsg?.message_type });
          }
          conversations.sort((a, b) => (b.last_time || 0) - (a.last_time || 0));
          sendSuccess(conversations);
        }
        // Get messages for a conversation
        else if (req.url.startsWith('/api/messages') && req.method === 'GET') {
          const urlObj = require('url').parse(req.url, true);
          const peerId = urlObj.query.peer;
          const messages = this.db.all(`
            SELECT * FROM messages WHERE 
            (from_agent = ? AND to_agent = ?) OR 
            (from_agent = ? AND to_agent = ?) 
            ORDER BY created_at ASC
          `, [this.nodeId, peerId, peerId, this.nodeId]);
          sendSuccess(messages);
        }
        // All discovered agents from all protocols
        else if (req.url === '/api/all-agents' && req.method === 'GET') {
          const wsPeers = this.p2p.getPeers ? this.p2p.getPeers() : [];
          const allAgents = this.p2p.getAllAgents ? this.p2p.getAllAgents() : { websocket: [], http: [], local: [] };
          const nostrInfo = this.nostr ? { pubkey: (this.nostr.getPublicKey ? this.nostr.getPublicKey() : this.nostr.publicKey || '').substring(0, 16), connected: this.nostr.connected || false } : null;
          const localPeers = this.localDiscovery ? this.localDiscovery.getPeers() : [];
          
          const discovered = [];
          
          // Add local UDP peers
          for (const peer of localPeers) {
            discovered.push({ id: peer.nodeId, type: 'local', ip: peer.ip, port: peer.port, version: peer.version, services: peer.services });
          }
          
          // Add WebSocket peers
          for (const peerId of allAgents.websocket) {
            discovered.push({ id: peerId, type: 'websocket' });
          }
          
          // Add HTTP/EvoMap peers
          for (const peerId of allAgents.http) {
            discovered.push({ id: peerId, type: 'evomap' });
          }
          
          sendSuccess({ nostr: nostrInfo, discovered });
        }
        // Send message via EvoMap
        else if (req.url === '/api/send-message' && req.method === 'POST') {
          let body = '';
          req.on('data', chunk => body += chunk);
          req.on('end', async () => {
            try {
              const { targetId, message, type } = JSON.parse(body);
              if (this.evomap) {
                const result = await this.evomap.sendMessage(targetId, message, type || 'text');
                
                // Save to local database
                this.db.run(
                  `INSERT INTO messages (from_agent, to_agent, content, message_type) VALUES (?, ?, ?, ?)`,
                  [this.nodeId, targetId, message, type || 'text']
                );
                
                sendSuccess({ sent: true, result });
              } else {
                sendSuccess({ sent: false, error: 'EvoMap not initialized' });
              }
            } catch(e) {
              sendError(e.message);
            }
          });
        }
        // All skills marketplace
        else if (req.url === '/api/skills' && req.method === 'GET') {
          const skills = await this.skills.listSkills({ limit: 20 });
          sendSuccess(skills);
        }
        // My published skills
        else if (req.url === '/api/skills/mine' && req.method === 'GET') {
          const skills = await this.skills.getMySkills();
          sendSuccess(skills);
        }
        // Get my shares
        else if (req.url === '/api/shares/mine' && req.method === 'GET') {
          const balance = await this.skills.getBalance(this.p2p.peerId);
          if (!this.sharing) {
            this.sharing = new SharingManager(this.db, this.p2p.peerId);
          }
          const shares = this.sharing.getMyShares();
          sendSuccess({ ...shares, myLevel: this.sharing.getCreditLevel(balance) });
        }
        // Share content
        else if (req.url === '/api/share' && req.method === 'POST') {
          let body = '';
          req.on('data', chunk => body += chunk);
          req.on('end', async () => {
            try {
              const { shareType, title, content, tags, skillId, skillName, description, version } = JSON.parse(body);
              if (!this.sharing) {
                this.sharing = new SharingManager(this.db, this.p2p.peerId);
              }
              let result;
              if (shareType === 'experience') result = this.sharing.shareExperience(title, content, tags);
              else if (shareType === 'skill') result = this.sharing.shareSkill(skillId, skillName, description, version);
              else if (shareType === 'memory') result = this.sharing.shareMemory(title, content, tags);
              sendSuccess(result);
            } catch(e) { sendError(e.message); }
          });
        }
        // Download skill
        else if (req.url === '/api/skills/download' && req.method === 'POST') {
          let body = '';
          req.on('data', chunk => body += chunk);
          req.on('end', async () => {
            const { skillId } = JSON.parse(body);
            const skill = await this.skills.download(skillId);
            sendSuccess(skill);
          });
        }
        // Rate skill
        else if (req.url === '/api/skills/rate' && req.method === 'POST') {
          let body = '';
          req.on('data', chunk => body += chunk);
          req.on('end', async () => {
            const { skillId, rating, review } = JSON.parse(body);
            await this.skills.rate(skillId, rating, review);
            sendSuccess({ success: true });
          });
        }
        // Balance
        else if (req.url === '/api/balance' && req.method === 'GET') {
          const balance = await this.skills.getBalance(this.p2p.peerId);
          sendSuccess({ points: balance });
        }
        // Leaderboard
        else if (req.url === '/api/leaderboard' && req.method === 'GET') {
          const leaderboard = await this.skills.getLeaderboard('skills', 10);
          sendSuccess(leaderboard);
        }
        // Send message
        else if (req.url === '/api/send' && req.method === 'POST') {
          let body = '';
          req.on('data', chunk => body += chunk);
          req.on('end', async () => {
            const { to, message } = JSON.parse(body);
            await this.core.sendMessage(to, message);
            sendSuccess({ success: true });
          });
        }
        // Appreciate
        else if (req.url === '/api/appreciate' && req.method === 'POST') {
          let body = '';
          req.on('data', chunk => body += chunk);
          req.on('end', async () => {
            const { peerId } = JSON.parse(body);
            await this.core.sendAppreciation(peerId);
            sendSuccess({ success: true });
          });
        }
        // Publish skill
        else if (req.url === '/api/publish' && req.method === 'POST') {
          let body = '';
          req.on('data', chunk => body += chunk);
          req.on('end', async () => {
            const { skillPath, price, metadata } = JSON.parse(body);
            const skillId = await this.skills.publish(skillPath, price, metadata);
            // Share with P2P network
            await this.core.shareSkill(skillId, metadata.name || skillPath, metadata.description, price);
            sendSuccess({ success: true, skillId });
          });
        }
        // Share skill (broadcast to P2P)
        else if (req.url === '/api/share' && req.method === 'POST') {
          let body = '';
          req.on('data', chunk => body += chunk);
          req.on('end', async () => {
            const { skillId, skillName, description, price } = JSON.parse(body);
            await this.core.shareSkill(skillId, skillName, description, price);
            sendSuccess({ success: true });
          });
        }
        // Get installed OpenClaw skills
        else if (req.url === '/api/installed-skills' && req.method === 'GET') {
          const fs = require('fs');
          const skillsDir = (process.env.HOME || process.env.USERPROFILE) + '/.openclaw/workspace/skills';
          let skills = [];
          try {
            const dirs = fs.readdirSync(skillsDir);
            for (const dir of dirs) {
              const skillPath = skillsDir + '/' + dir;
              const stat = fs.statSync(skillPath);
              if (stat.isDirectory()) {
                let version = '1.0.0';
                try {
                  const pkgPath = skillPath + '/package.json';
                  if (fs.existsSync(pkgPath)) {
                    const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));
                    version = pkg.version || version;
                  }
                } catch(e) {}
                skills.push({ name: dir, version: version, path: skillPath });
              }
            }
          } catch(e) {}
          sendSuccess(skills);
        }
        // Check for updates
        // Get all discovered agents
        else if (req.url === '/api/discovered-agents' && req.method === 'GET') {
          const allAgents = this.p2p.getAllAgents();
          const localPeers = this.localDiscovery ? this.localDiscovery.getPeers() : [];
          const nostrInfo = this.nostr ? { pubkey: this.nostr.getPublicKey ? this.nostr.getPublicKey().substring(0, 16) : this.nostr.publicKey ? this.nostr.publicKey.substring(0, 16) : null, connected: this.nostr.connected || false } : null;
          sendSuccess({ websocket: allAgents.websocket, http: allAgents.http, local: localPeers, nostr: nostrInfo });
        }
        else if (req.url === '/api/check-update' && req.method === 'GET') {
          sendSuccess({ currentVersion: '1.0.5', latestVersion: '1.0.5', updateUrl: 'https://github.com/zerta1231/agent-network' });
        }
        else {
          res.writeHead(404);
          res.end(JSON.stringify({ error: 'Not found' }));
        }
      } catch (e) {
        sendError(e.message);
      }
    });
    
    this.httpServer.listen(this.config.port + 1, () => {
      console.log(`HTTP API server listening on port ${this.config.port + 1}`);
    });
  }
  
  async stop() {
    if (this.skills) await this.skills.stop();
    if (this.core) await this.core.stop();
    if (this.p2p) await this.p2p.stop();
    if (this.httpServer) {
      this.httpServer.close();
    }
    if (this.db) await this.db.close();
    this.running = false;
    console.log('Agent Network stopped');
  }
  
  get nodeId() {
    return this.p2p ? this.p2p.peerId : null;
  }
}

module.exports = { AgentNetworkSkill };

// Run directly if called from command line
if (require.main === module) {
  const skill = new AgentNetworkSkill({
    port: 18794,
    window: { enabled: false }
  });
  
  skill.start().catch(console.error);
  
  process.on('SIGINT', async () => {
    console.log('\nShutting down...');
    await skill.stop();
    process.exit(0);
  });
}
