const initSqlJs = require('sql.js');
const path = require('path');
const fs = require('fs');

class Database {
  constructor(dbPath = null) {
    this.dbPath = dbPath || path.join(process.env.HOME || '.', '.openclaw', 'data', 'agent-network.db');
    this.db = null;
    this.SQL = null;
  }
  
  async initialize() {
    const dbDir = path.dirname(this.dbPath);
    if (!fs.existsSync(dbDir)) {
      fs.mkdirSync(dbDir, { recursive: true });
    }
    
    this.SQL = await initSqlJs();
    
    // Load existing database or create new
    if (fs.existsSync(this.dbPath)) {
      const fileBuffer = fs.readFileSync(this.dbPath);
      this.db = new this.SQL.Database(fileBuffer);
    } else {
      this.db = new this.SQL.Database();
    }
    
    this.createTables();
    this.save();
  }
  
  createTables() {
    this.db.run(`
      CREATE TABLE IF NOT EXISTS agents (
        id TEXT PRIMARY KEY,
        name TEXT,
        description TEXT,
        reputation_score REAL DEFAULT 50,
        total_contributions INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        last_active TEXT
      )
    `);
    
    this.db.run(`
      CREATE TABLE IF NOT EXISTS connections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        agent_id TEXT,
        peer_id TEXT,
        status TEXT CHECK(status IN ('pending', 'accepted', 'rejected')),
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(agent_id, peer_id)
      )
    `);
    
    this.db.run(`
      CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        from_agent TEXT,
        to_agent TEXT,
        content TEXT,
        message_type TEXT DEFAULT 'text',
        read INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
      )
    `);
    
    this.db.run(`
      CREATE TABLE IF NOT EXISTS skills (
        id TEXT PRIMARY KEY,
        owner_agent TEXT,
        name TEXT,
        description TEXT,
        category TEXT,
        price INTEGER DEFAULT 0,
        downloads INTEGER DEFAULT 0,
        avg_rating REAL DEFAULT 0,
        rating_count INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT
      )
    `);
    
    this.db.run(`
      CREATE TABLE IF NOT EXISTS skill_ratings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        skill_id TEXT,
        rater_agent TEXT,
        rating INTEGER CHECK(rating BETWEEN 1 AND 5),
        review TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(skill_id, rater_agent)
      )
    `);
    
    this.db.run(`
      CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        from_agent TEXT,
        to_agent TEXT,
        amount INTEGER,
        type TEXT,
        reference_id TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
      )
    `);
    
    this.db.run(`
      CREATE TABLE IF NOT EXISTS balances (
        agent_id TEXT PRIMARY KEY,
        points INTEGER DEFAULT 100
      )
    `);
    
    // Sharing tables
    this.db.run(`
      CREATE TABLE IF NOT EXISTS experiences (
        id TEXT PRIMARY KEY,
        node_id TEXT,
        title TEXT,
        content TEXT,
        tags TEXT,
        credit_level TEXT DEFAULT 'bronze',
        created_at INTEGER
      )
    `);
    
    this.db.run(`
      CREATE TABLE IF NOT EXISTS shared_skills (
        id TEXT PRIMARY KEY,
        node_id TEXT,
        skill_id TEXT,
        skill_name TEXT,
        description TEXT,
        version TEXT,
        credit_level TEXT DEFAULT 'silver',
        created_at INTEGER
      )
    `);
    
    this.db.run(`
      CREATE TABLE IF NOT EXISTS shared_memories (
        id TEXT PRIMARY KEY,
        node_id TEXT,
        title TEXT,
        content TEXT,
        tags TEXT,
        credit_level TEXT DEFAULT 'gold',
        created_at INTEGER
      )
    `);
  }
  
  save() {
    const data = this.db.export();
    const buffer = Buffer.from(data);
    fs.writeFileSync(this.dbPath, buffer);
  }
  
  run(sql, params = []) {
    try {
      this.db.run(sql, params);
      this.save();
      return { changes: this.db.getRowsModified() };
    } catch (e) {
      console.error('DB run error:', e.message);
      throw e;
    }
  }
  
  get(sql, params = []) {
    try {
      const stmt = this.db.prepare(sql);
      stmt.bind(params);
      if (stmt.step()) {
        const row = stmt.getAsObject();
        stmt.free();
        return row;
      }
      stmt.free();
      return null;
    } catch (e) {
      console.error('DB get error:', e.message);
      return null;
    }
  }
  
  all(sql, params = []) {
    try {
      const results = [];
      const stmt = this.db.prepare(sql);
      stmt.bind(params);
      while (stmt.step()) {
        results.push(stmt.getAsObject());
      }
      stmt.free();
      return results;
    } catch (e) {
      console.error('DB all error:', e.message);
      return [];
    }
  }
  
  close() {
    if (this.db) {
      this.save();
      this.db.close();
    }
  }
}

module.exports = { Database };
