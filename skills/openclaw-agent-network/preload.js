const API_PORT = 18794;
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('api', {
  // Status
  getStatus: () => fetch('http://localhost:18794/api/status').then(r => r.json()),
  
  // Connections
  getConnections: () => fetch('http://localhost:18794/api/connections').then(r => r.json()),
  
  // All discovered agents
  getConversations: () => fetch(`http://localhost:${API_PORT}/api/conversations`).then(r => r.json()),
  getMessages: (peerId) => fetch(`http://localhost:${API_PORT}/api/messages?peer=${encodeURIComponent(peerId)}`).then(r => r.json()),
  getAllAgents: () => fetch('http://localhost:18794/api/all-agents').then(r => r.json()),
  
  // Skills marketplace
  getSkills: () => fetch('http://localhost:18794/api/skills').then(r => r.json()),
  
  // My published skills
  getMySkills: () => fetch('http://localhost:18794/api/skills/mine').then(r => r.json()),
  
  // Installed skills
  getInstalledSkills: () => fetch('http://localhost:18794/api/installed-skills').then(r => r.json()),
  
  // Check update
  checkUpdate: () => fetch('http://localhost:18794/api/check-update').then(r => r.json()),
  
  // Balance
  getMyShares: () => fetch(`http://localhost:${API_PORT}/api/shares/mine`).then(r => r.json()),
  shareContent: (type, data) => fetch(`http://localhost:${API_PORT}/api/share`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ shareType: type, ...data }) }).then(r => r.json()),
  // Balance
  getBalance: () => fetch('http://localhost:18794/api/balance').then(r => r.json()),
  
  // Messaging - tries local first, then EvoMap
  sendMessage: async (to, message) => {
    // Try local first
    try {
      const localRes = await fetch('http://localhost:18794/api/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ to, message })
      });
      const localData = await localRes.json();
      if (localData.success) return localData;
    } catch (e) {}
    
    // Fallback to EvoMap
    try {
      const evomapRes = await fetch('http://localhost:18794/api/send-message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ targetId: to, message })
      });
      return await evomapRes.json();
    } catch (e) {
      return { success: false, error: e.message };
    }
  },
  
  // Appreciation
  sendAppreciation: (peerId) => fetch('http://localhost:18794/api/appreciate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ peerId })
  }).then(r => r.json()),
  
  // Publish skill
  publishSkill: (skillPath, price, metadata) => fetch('http://localhost:18794/api/publish', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ skillPath, price, metadata })
  }).then(r => r.json()),
  
  // Download skill
  downloadSkill: (skillId) => fetch('http://localhost:18794/api/skills/download', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ skillId })
  }).then(r => r.json()),
  
  // Rate skill
  rateSkill: (skillId, rating, review) => fetch('http://localhost:18794/api/skills/rate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ skillId, rating, review })
  }).then(r => r.json()),
  
  // Leaderboard
  getLeaderboard: () => fetch('http://localhost:18794/api/leaderboard').then(r => r.json()),
  
  onShowStatus: (callback) => ipcRenderer.on('show-status', callback)
});
