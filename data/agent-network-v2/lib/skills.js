const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

class SkillsManager {
  constructor(db, p2p) {
    this.db = db;
    this.p2p = p2p;
    this.skillsDir = path.join(process.env.HOME || '.', '.openclaw', 'workspace', 'skills');
    this.nodeId = p2p.peerId;
  }
  
  async start() {
    // Ensure skills directory exists
    const agentNetworkDir = path.join(this.skillsDir, 'agent-network');
    if (!fs.existsSync(agentNetworkDir)) {
      fs.mkdirSync(agentNetworkDir, { recursive: true });
    }
    
    console.log('Skills manager started');
  }
  
  // Publish a skill
  async publish(skillPath, price = 0, metadata = {}) {
    const skillDir = path.join(this.skillsDir, skillPath);
    
    if (!fs.existsSync(skillDir)) {
      throw new Error('Skill not found: ' + skillPath);
    }
    
    const skillMdPath = path.join(skillDir, 'SKILL.md');
    let description = '';
    
    if (fs.existsSync(skillMdPath)) {
      const content = fs.readFileSync(skillMdPath, 'utf-8');
      // Extract first 200 chars as description
      description = content.substring(0, 200);
    }
    
    // Generate skill ID
    const skillId = crypto.createHash('sha256')
      .update(skillPath + Date.now())
      .digest('hex')
      .substring(0, 16);
    
    // Save to database
    this.db.run(
      `INSERT INTO skills (id, owner_agent, name, description, category, price, created_at)
       VALUES (?, ?, ?, ?, ?, ?, ?)`,
      [
        skillId,
        this.nodeId,
        metadata.name || path.basename(skillPath),
        description,
        metadata.category || 'general',
        price,
        new Date().toISOString()
      ]
    );
    
    // Broadcast to network
    this.p2p.broadcast({
      type: 'skill_update',
      action: 'published',
      skillId,
      owner: this.nodeId,
      name: metadata.name || path.basename(skillPath),
      price
    });
    
    // Add points for publishing
    await this.addPoints(this.nodeId, 50, 'publish', skillId);
    
    return skillId;
  }
  
  // List skills
  async listSkills(filter = {}) {
    let query = 'SELECT * FROM skills WHERE 1=1';
    const params = [];
    
    if (filter.category) {
      query += ' AND category = ?';
      params.push(filter.category);
    }
    
    if (filter.keyword) {
      query += ' AND (name LIKE ? OR description LIKE ?)';
      params.push(`%${filter.keyword}%`, `%${filter.keyword}%`);
    }
    
    if (filter.owner) {
      query += ' AND owner_agent = ?';
      params.push(filter.owner);
    }
    
    query += ' ORDER BY avg_rating DESC, downloads DESC LIMIT ?';
    params.push(filter.limit || 50);
    
    return this.db.all(query, params);
  }
  
  // Get skill by ID
  async getSkill(skillId) {
    return this.db.get('SELECT * FROM skills WHERE id = ?', [skillId]);
  }
  
  // Download skill (in this demo, just returns info)
  async download(skillId) {
    const skill = await this.getSkill(skillId);
    
    if (!skill) {
      throw new Error('Skill not found');
    }
    
    const balance = await this.getBalance(this.nodeId);
    
    if (balance < skill.price) {
      throw new Error('Insufficient points. Need ' + skill.price + ', have ' + balance);
    }
    
    // Deduct points
    await this.addPoints(this.nodeId, -skill.price, 'download', skillId);
    
    // Add points to owner
    if (skill.owner_agent !== this.nodeId) {
      await this.addPoints(skill.owner_agent, 20, 'download', skillId);
    }
    
    // Update download count
    this.db.run(
      'UPDATE skills SET downloads = downloads + 1 WHERE id = ?',
      [skillId]
    );
    
    return skill;
  }
  
  // Rate a skill
  async rate(skillId, rating, review = '') {
    if (rating < 1 || rating > 5) {
      throw new Error('Rating must be between 1 and 5');
    }
    
    const existing = this.db.get(
      'SELECT * FROM skill_ratings WHERE skill_id = ? AND rater_agent = ?',
      [skillId, this.nodeId]
    );
    
    if (existing) {
      throw new Error('Already rated this skill');
    }
    
    // Add rating
    this.db.run(
      'INSERT INTO skill_ratings (skill_id, rater_agent, rating, review) VALUES (?, ?, ?, ?)',
      [skillId, this.nodeId, rating, review]
    );
    
    // Update average rating
    const result = this.db.get(
      'SELECT AVG(rating) as avg, COUNT(*) as cnt FROM skill_ratings WHERE skill_id = ?',
      [skillId]
    );
    
    if (result) {
      this.db.run(
        'UPDATE skills SET avg_rating = ?, rating_count = ? WHERE id = ?',
        [result.avg || rating, result.cnt, skillId]
      );
    }
    
    // Add points to skill owner
    const skill = await this.getSkill(skillId);
    if (skill && skill.owner_agent !== this.nodeId) {
      await this.addPoints(skill.owner_agent, 5, 'rating', skillId);
    }
    
    return true;
  }
  
  // Add/remove points
  async addPoints(agentId, amount, type, referenceId) {
    // Update balance
    const existing = this.db.get('SELECT * FROM balances WHERE agent_id = ?', [agentId]);
    
    if (existing) {
      this.db.run(
        'UPDATE balances SET points = points + ? WHERE agent_id = ?',
        [amount, agentId]
      );
    } else {
      this.db.run(
        'INSERT INTO balances (agent_id, points) VALUES (?, ?)',
        [agentId, 100 + amount]
      );
    }
    
    // Record transaction
    this.db.run(
      `INSERT INTO transactions (from_agent, to_agent, amount, type, reference_id)
       VALUES (?, ?, ?, ?, ?)`,
      [this.nodeId, agentId, amount, type, referenceId]
    );
  }
  
  // Get balance
  async getBalance(agentId) {
    const result = this.db.get('SELECT points FROM balances WHERE agent_id = ?', [agentId]);
    return result ? result.points : 100;
  }
  
  // Get transaction history
  async getTransactions(agentId, limit = 20) {
    return this.db.all(
      `SELECT * FROM transactions 
       WHERE from_agent = ? OR to_agent = ?
       ORDER BY created_at DESC LIMIT ?`,
      [agentId, agentId, limit]
    );
  }
  
  // Leaderboard
  async getLeaderboard(type = 'skills', limit = 20) {
    if (type === 'skills') {
      return this.db.all(
        'SELECT * FROM skills ORDER BY avg_rating DESC, downloads DESC LIMIT ?',
        [limit]
      );
    } else {
      return this.db.all(
        'SELECT * FROM agents ORDER BY reputation_score DESC, total_contributions DESC LIMIT ?',
        [limit]
      );
    }
  }
  
  // Get my skills
  async getMySkills() {
    return this.db.all(
      'SELECT * FROM skills WHERE owner_agent = ? ORDER BY created_at DESC',
      [this.nodeId]
    );
  }
  
  async stop() {
    console.log('Skills manager stopped');
  }
}

module.exports = { SkillsManager };
