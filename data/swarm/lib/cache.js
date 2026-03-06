/**
 * Swarm Prompt Cache
 * 
 * LRU cache for LLM responses. Keyed by hash of (prompt + input + perspective).
 * Dramatically reduces cost and latency for repeated/similar queries.
 * 
 * Conservative by design:
 * - TTL-based expiry (default 1 hour)
 * - Max entries cap (default 500)
 * - Cache hits logged for observability
 * - Optional per-request cache bypass
 * - File-backed persistence across daemon restarts
 */

const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

const CACHE_DIR = path.join(process.env.HOME, '.config/clawdbot/swarm-cache');
const CACHE_FILE = path.join(CACHE_DIR, 'prompt-cache.json');

class PromptCache {
  constructor(options = {}) {
    this.maxEntries = options.maxEntries || 500;
    this.defaultTTLMs = options.ttlMs || 60 * 60 * 1000; // 1 hour
    this.entries = new Map();
    this.stats = { hits: 0, misses: 0, evictions: 0, persisted: 0 };
    
    // Load persisted cache
    this._load();
  }

  /**
   * Generate cache key from prompt components
   */
  key(instruction, input, perspective) {
    const raw = JSON.stringify({
      i: (instruction || '').trim(),
      d: (input || '').trim().substring(0, 2000), // Only hash first 2K of input for key
      p: (perspective || '').trim(),
    });
    return crypto.createHash('sha256').update(raw).digest('hex').substring(0, 16);
  }

  /**
   * Get cached response if available and not expired
   */
  get(instruction, input, perspective) {
    const k = this.key(instruction, input, perspective);
    const entry = this.entries.get(k);
    
    if (!entry) {
      this.stats.misses++;
      return null;
    }
    
    // Check TTL
    if (Date.now() > entry.expiresAt) {
      this.entries.delete(k);
      this.stats.misses++;
      return null;
    }
    
    // LRU: move to end
    this.entries.delete(k);
    this.entries.set(k, entry);
    
    entry.hits++;
    this.stats.hits++;
    return entry.response;
  }

  /**
   * Store response in cache
   */
  set(instruction, input, perspective, response, ttlMs) {
    const k = this.key(instruction, input, perspective);
    const ttl = ttlMs || this.defaultTTLMs;
    
    // Evict if at capacity
    if (this.entries.size >= this.maxEntries && !this.entries.has(k)) {
      // Remove oldest (first entry in Map)
      const oldest = this.entries.keys().next().value;
      this.entries.delete(oldest);
      this.stats.evictions++;
    }
    
    this.entries.set(k, {
      response,
      createdAt: Date.now(),
      expiresAt: Date.now() + ttl,
      hits: 0,
      instruction: instruction?.substring(0, 80),
    });
  }

  /**
   * Clear all entries
   */
  clear() {
    this.entries.clear();
  }

  /**
   * Remove expired entries
   */
  prune() {
    const now = Date.now();
    let pruned = 0;
    for (const [k, entry] of this.entries) {
      if (now > entry.expiresAt) {
        this.entries.delete(k);
        pruned++;
      }
    }
    return pruned;
  }

  /**
   * Get cache statistics
   */
  getStats() {
    const total = this.stats.hits + this.stats.misses;
    return {
      entries: this.entries.size,
      maxEntries: this.maxEntries,
      hits: this.stats.hits,
      misses: this.stats.misses,
      hitRate: total > 0 ? (this.stats.hits / total * 100).toFixed(1) + '%' : 'N/A',
      evictions: this.stats.evictions,
      ttlMs: this.defaultTTLMs,
    };
  }

  /**
   * Persist cache to disk (called periodically or on shutdown)
   */
  persist() {
    try {
      if (!fs.existsSync(CACHE_DIR)) {
        fs.mkdirSync(CACHE_DIR, { recursive: true });
      }
      
      // Only persist non-expired entries
      const now = Date.now();
      const data = {};
      for (const [k, entry] of this.entries) {
        if (now < entry.expiresAt) {
          data[k] = entry;
        }
      }
      
      fs.writeFileSync(CACHE_FILE, JSON.stringify(data));
      this.stats.persisted = Object.keys(data).length;
    } catch (e) {
      // Non-critical
    }
  }

  /**
   * Load cache from disk
   */
  _load() {
    try {
      if (!fs.existsSync(CACHE_FILE)) return;
      
      const data = JSON.parse(fs.readFileSync(CACHE_FILE, 'utf8'));
      const now = Date.now();
      let loaded = 0;
      
      for (const [k, entry] of Object.entries(data)) {
        if (now < entry.expiresAt && loaded < this.maxEntries) {
          this.entries.set(k, entry);
          loaded++;
        }
      }
      
      if (loaded > 0) {
        console.log(`📦 Cache: loaded ${loaded} entries from disk`);
      }
    } catch (e) {
      // Non-critical — start fresh
    }
  }
}

// Singleton
const promptCache = new PromptCache();

module.exports = { PromptCache, promptCache };
