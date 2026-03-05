/**
 * Database module for Agent Network Server
 * Uses SQLite for simplicity
 */

const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs');

class Database {
  constructor() {
    const dbDir = path.join(__dirname, '..', 'data');
    if (!fs.existsSync(dbDir)) {
      fs.mkdirSync(dbDir, { recursive: true });
    }
    
    this.db = new sqlite3.Database(path.join(dbDir, 'agent_network.db'));
    this.init();
  }
  
  init() {
    this.db.serialize(() => {
      // Agents table
      this.db.run(`
        CREATE TABLE IF NOT EXISTS agents (
          id TEXT PRIMARY KEY,
          name TEXT NOT NULL,
          role TEXT,
          device TEXT,
          status TEXT DEFAULT 'offline',
          last_seen TEXT,
          created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
      `);
      
      // Groups table
      this.db.run(`
        CREATE TABLE IF NOT EXISTS groups (
          id TEXT PRIMARY KEY,
          name TEXT NOT NULL,
          description TEXT,
          owner_id TEXT,
          created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
      `);
      
      // Group members
      this.db.run(`
        CREATE TABLE IF NOT EXISTS group_members (
          group_id TEXT,
          agent_id TEXT,
          joined_at TEXT DEFAULT CURRENT_TIMESTAMP,
          PRIMARY KEY (group_id, agent_id)
        )
      `);
      
      // Messages table
      this.db.run(`
        CREATE TABLE IF NOT EXISTS messages (
          id TEXT PRIMARY KEY,
          type TEXT DEFAULT 'message',
          from_id TEXT,
          from_name TEXT,
          group_id TEXT,
          content TEXT,
          timestamp TEXT,
          created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
      `);
      
      // Offline messages
      this.db.run(`
        CREATE TABLE IF NOT EXISTS offline_messages (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          agent_id TEXT,
          message TEXT,
          created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
      `);
      
      // Tasks table
      this.db.run(`
        CREATE TABLE IF NOT EXISTS tasks (
          id TEXT PRIMARY KEY,
          title TEXT NOT NULL,
          description TEXT,
          assigner_id TEXT,
          assignee_id TEXT,
          group_id TEXT,
          status TEXT DEFAULT 'pending',
          priority TEXT DEFAULT 'normal',
          created_at TEXT DEFAULT CURRENT_TIMESTAMP,
          updated_at TEXT
        )
      `);
      
      // Inbox table
      this.db.run(`
        CREATE TABLE IF NOT EXISTS inbox (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          agent_id TEXT,
          message_id TEXT,
          is_read BOOLEAN DEFAULT 0,
          created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
      `);
    });
  }
  
  // Groups
  async createGroup(name, description, ownerId) {
    const id = `group-${Date.now()}`;
    return new Promise((resolve, reject) => {
      this.db.run(
        'INSERT INTO groups (id, name, description, owner_id) VALUES (?, ?, ?, ?)',
        [id, name, description, ownerId],
        (err) => {
          if (err) reject(err);
          else resolve({ id, name, description, ownerId });
        }
      );
    });
  }
  
  async getGroups() {
    return new Promise((resolve, reject) => {
      this.db.all('SELECT * FROM groups ORDER BY created_at DESC', (err, rows) => {
        if (err) reject(err);
        else resolve(rows);
      });
    });
  }
  
  // Messages
  async saveMessage(message) {
    return new Promise((resolve, reject) => {
      this.db.run(
        'INSERT INTO messages (id, type, from_id, from_name, group_id, content, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)',
        [message.id, message.type, message.from, message.fromName, message.groupId, message.content, message.timestamp],
        (err) => {
          if (err) reject(err);
          else resolve(message);
        }
      );
    });
  }
  
  async getGroupMessages(groupId, limit = 50) {
    return new Promise((resolve, reject) => {
      this.db.all(
        'SELECT * FROM messages WHERE group_id = ? ORDER BY timestamp DESC LIMIT ?',
        [groupId, limit],
        (err, rows) => {
          if (err) reject(err);
          else resolve(rows.reverse());
        }
      );
    });
  }
  
  // Offline messages
  async saveOfflineMessage(agentId, message) {
    return new Promise((resolve, reject) => {
      this.db.run(
        'INSERT INTO offline_messages (agent_id, message) VALUES (?, ?)',
        [agentId, JSON.stringify(message)],
        (err) => {
          if (err) reject(err);
          else resolve();
        }
      );
    });
  }
  
  async getOfflineMessages(agentId) {
    return new Promise((resolve, reject) => {
      this.db.all(
        'SELECT * FROM offline_messages WHERE agent_id = ? ORDER BY created_at',
        [agentId],
        (err, rows) => {
          if (err) reject(err);
          else resolve(rows.map(r => JSON.parse(r.message)));
        }
      );
    });
  }
  
  async clearOfflineMessages(agentId) {
    return new Promise((resolve, reject) => {
      this.db.run(
        'DELETE FROM offline_messages WHERE agent_id = ?',
        [agentId],
        (err) => {
          if (err) reject(err);
          else resolve();
        }
      );
    });
  }
  
  // Tasks
  async createTask(task) {
    const id = `task-${Date.now()}`;
    const taskWithId = { ...task, id, created_at: new Date().toISOString() };
    
    return new Promise((resolve, reject) => {
      this.db.run(
        'INSERT INTO tasks (id, title, description, assigner_id, assignee_id, group_id, priority) VALUES (?, ?, ?, ?, ?, ?, ?)',
        [id, task.title, task.description, task.assignerId, task.assigneeId, task.groupId, task.priority || 'normal'],
        (err) => {
          if (err) reject(err);
          else resolve(taskWithId);
        }
      );
    });
  }
  
  async getTasks() {
    return new Promise((resolve, reject) => {
      this.db.all('SELECT * FROM tasks ORDER BY created_at DESC', (err, rows) => {
        if (err) reject(err);
        else resolve(rows);
      });
    });
  }
  
  // Inbox
  async getAgentInbox(agentId) {
    return new Promise((resolve, reject) => {
      this.db.all(
        `SELECT i.*, m.content, m.from_name, m.timestamp 
         FROM inbox i 
         JOIN messages m ON i.message_id = m.id 
         WHERE i.agent_id = ? 
         ORDER BY i.created_at DESC`,
        [agentId],
        (err, rows) => {
          if (err) reject(err);
          else resolve(rows);
        }
      );
    });
  }
}

module.exports = Database;
