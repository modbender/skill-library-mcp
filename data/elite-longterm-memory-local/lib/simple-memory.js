/**
 * Simple Memory Manager - File-based with text search
 * Fallback when LanceDB is not available
 */

const fs = require('fs').promises;
const path = require('path');

class SimpleMemoryManager {
  constructor(config) {
    this.config = {
      memoryPath: config.memoryPath || './memory',
      ...config
    };
    this.memories = [];
    this.initialized = false;
  }

  async init() {
    if (this.initialized) return;
    
    // Ensure memory directory exists
    await fs.mkdir(this.config.memoryPath, { recursive: true });
    
    // Load existing memories
    await this.loadMemories();
    
    this.initialized = true;
  }

  async loadMemories() {
    const memoriesFile = path.join(this.config.memoryPath, 'memories.json');
    try {
      const data = await fs.readFile(memoriesFile, 'utf-8');
      this.memories = JSON.parse(data);
    } catch (err) {
      // File doesn't exist yet, start empty
      this.memories = [];
    }
  }

  async saveMemories() {
    const memoriesFile = path.join(this.config.memoryPath, 'memories.json');
    await fs.writeFile(memoriesFile, JSON.stringify(this.memories, null, 2));
  }

  async store(text, options = {}) {
    await this.init();
    
    const { importance = 0.7, category = 'other' } = options;
    
    // Check for duplicates (simple text similarity)
    const existing = this.memories.find(m => 
      m.text.toLowerCase().includes(text.toLowerCase()) ||
      text.toLowerCase().includes(m.text.toLowerCase())
    );
    
    if (existing) {
      return { id: existing.id, duplicate: true };
    }
    
    const entry = {
      id: this.generateId(),
      text,
      importance,
      category,
      createdAt: Date.now()
    };
    
    this.memories.push(entry);
    await this.saveMemories();
    
    return { id: entry.id, duplicate: false };
  }

  async search(query, limit = 5, minScore = 0.3) {
    await this.init();
    
    const queryLower = query.toLowerCase();
    const queryWords = queryLower.split(/\s+/).filter(w => w.length > 2);
    
    const results = this.memories
      .map(memory => {
        const textLower = memory.text.toLowerCase();
        
        // Calculate simple relevance score
        let score = 0;
        
        // Exact match bonus
        if (textLower.includes(queryLower)) {
          score += 0.5;
        }
        
        // Word match
        queryWords.forEach(word => {
          if (textLower.includes(word)) {
            score += 0.2;
          }
        });
        
        // Importance boost
        score += memory.importance * 0.3;
        
        return {
          entry: memory,
          score: Math.min(score, 1.0)
        };
      })
      .filter(r => r.score >= minScore)
      .sort((a, b) => b.score - a.score)
      .slice(0, limit);
    
    return results;
  }

  async delete(id) {
    await this.init();
    
    const index = this.memories.findIndex(m => m.id === id);
    if (index === -1) {
      throw new Error(`Memory not found: ${id}`);
    }
    
    this.memories.splice(index, 1);
    await this.saveMemories();
    
    return true;
  }

  async count() {
    await this.init();
    return this.memories.length;
  }

  async close() {
    // Nothing to close for file-based storage
    this.initialized = false;
  }

  generateId() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      const r = Math.random() * 16 | 0;
      const v = c === 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  }
}

module.exports = { SimpleMemoryManager };
