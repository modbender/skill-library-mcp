/**
 * Memory Manager - LanceDB + Pure JS Embedding
 * No native modules required, works everywhere
 */

const { PureJSEmbedding } = require('./purejs-embedding');
const path = require('path');

class MemoryManager {
  constructor(config) {
    this.config = {
      dbPath: config.dbPath || './memory/vectors',
      ...config
    };
    this.db = null;
    this.lancedb = null;
    this.table = null;
    this.embedder = new PureJSEmbedding({ dim: 384 });
  }

  async init() {
    if (this.db) return;
    
    // Initialize embedding
    await this.embedder.init();
    
    // Dynamically import LanceDB
    const lancedb = await import('@lancedb/lancedb');
    this.lancedb = lancedb;
    
    this.db = await lancedb.connect(this.config.dbPath);
    
    // Check if table exists
    const tables = await this.db.tableNames();
    if (tables.includes('memories')) {
      this.table = await this.db.openTable('memories');
    } else {
      // Create table with schema (384 dims)
      this.table = await this.db.createTable('memories', [
        {
          id: 'schema-init',
          text: '',
          vector: Array(384).fill(0),
          importance: 0,
          category: 'other',
          createdAt: Date.now()
        }
      ]);
      await this.table.delete("id = 'schema-init'");
    }
  }

  async embed(text) {
    return this.embedder.embed(text);
  }

  async store(text, options = {}) {
    await this.init();
    
    const { importance = 0.7, category = 'other' } = options;
    const vector = await this.embed(text);
    
    // Check for duplicates
    const existing = await this.search(vector, 1, 0.95);
    if (existing.length > 0 && existing[0].score > 0.95) {
      return { id: existing[0].entry.id, duplicate: true };
    }
    
    const entry = {
      id: this.generateId(),
      text,
      vector,
      importance,
      category,
      createdAt: Date.now()
    };
    
    await this.table.add([entry]);
    return { id: entry.id, duplicate: false };
  }

  async search(queryOrVector, limit = 5, minScore = 0.5) {
    await this.init();
    
    let vector;
    if (Array.isArray(queryOrVector)) {
      vector = queryOrVector;
    } else {
      vector = await this.embed(queryOrVector);
    }
    
    const results = await this.table
      .vectorSearch(vector)
      .limit(limit)
      .toArray();
    
    // Convert L2 distance to similarity score
    return results
      .map(row => ({
        entry: {
          id: row.id,
          text: row.text,
          importance: row.importance,
          category: row.category,
          createdAt: row.createdAt
        },
        score: 1 / (1 + (row._distance || 0))
      }))
      .filter(r => r.score >= minScore)
      .sort((a, b) => b.score - a.score);
  }

  async delete(id) {
    await this.init();
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
    if (!uuidRegex.test(id)) {
      throw new Error(`Invalid memory ID format: ${id}`);
    }
    await this.table.delete(`id = '${id}'`);
    return true;
  }

  async count() {
    await this.init();
    return await this.table.countRows();
  }

  async close() {
    this.db = null;
    this.table = null;
  }

  generateId() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      const r = Math.random() * 16 | 0;
      const v = c === 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  }
}

module.exports = { MemoryManager };
