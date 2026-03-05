const crypto = require('crypto');

const CREDIT_LEVELS = { bronze: 0, silver: 100, gold: 500, platinum: 1000 };
const LEVELS = ['bronze', 'silver', 'gold', 'platinum'];

class SharingManager {
  constructor(db, nodeId) {
    this.db = db;
    this.nodeId = nodeId;
  }
  
  getCreditLevel(balance = 100) {
    if (balance >= CREDIT_LEVELS.platinum) return 'platinum';
    if (balance >= CREDIT_LEVELS.gold) return 'gold';
    if (balance >= CREDIT_LEVELS.silver) return 'silver';
    return 'bronze';
  }
  
  shareExperience(title, content, tags = []) {
    const id = 'exp_' + crypto.randomBytes(6).toString('hex');
    const level = this.getCreditLevel();
    this.db.run(`INSERT INTO experiences (id, node_id, title, content, tags, credit_level, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)`,
      [id, this.nodeId, title, content, JSON.stringify(tags), level, Date.now()]);
    return { id, type: 'experience', title, credit_level: level };
  }
  
  shareSkill(skillId, skillName, description, version) {
    const id = 'skl_' + crypto.randomBytes(6).toString('hex');
    const level = this.getCreditLevel();
    this.db.run(`INSERT INTO shared_skills (id, node_id, skill_id, skill_name, description, version, credit_level, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
      [id, this.nodeId, skillId, skillName, description, version, level, Date.now()]);
    return { id, type: 'skill', skillName, credit_level: level };
  }
  
  shareMemory(title, content, tags = []) {
    const id = 'mem_' + crypto.randomBytes(6).toString('hex');
    const level = this.getCreditLevel();
    this.db.run(`INSERT INTO shared_memories (id, node_id, title, content, tags, credit_level, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)`,
      [id, this.nodeId, title, content, JSON.stringify(tags), level, Date.now()]);
    return { id, type: 'memory', title, credit_level: level };
  }
  
  getMyShares() {
    return {
      experiences: this.db.all(`SELECT * FROM experiences WHERE node_id = ?`, [this.nodeId]),
      skills: this.db.all(`SELECT * FROM shared_skills WHERE node_id = ?`, [this.nodeId]),
      memories: this.db.all(`SELECT * FROM shared_memories WHERE node_id = ?`, [this.nodeId])
    };
  }
}

module.exports = { SharingManager };
