/**
 * Simple Embedding - Using local computation without external services
 * Falls back to simple hashing when no model is available
 */

class SimpleEmbedding {
  constructor(config = {}) {
    this.dim = config.dim || 384;
  }

  async init() {
    // No initialization needed for simple embedding
    return true;
  }

  async embed(text) {
    // Simple but effective embedding using character n-grams
    // This is not as good as neural embeddings but works without any downloads
    const vector = new Array(this.dim).fill(0);
    
    // Character trigrams
    const normalized = text.toLowerCase().trim();
    for (let i = 0; i < normalized.length - 2; i++) {
      const trigram = normalized.substring(i, i + 3);
      const hash = this.hashString(trigram);
      vector[hash % this.dim] += 1;
    }
    
    // Word-level features
    const words = normalized.split(/\s+/);
    for (const word of words) {
      const hash = this.hashString(word);
      vector[hash % this.dim] += 2;
      
      // Prefix/suffix features
      if (word.length > 3) {
        vector[this.hashString(word.slice(0, 3)) % this.dim] += 0.5;
        vector[this.hashString(word.slice(-3)) % this.dim] += 0.5;
      }
    }
    
    // Normalize
    const norm = Math.sqrt(vector.reduce((sum, v) => sum + v * v, 0));
    if (norm > 0) {
      return vector.map(v => v / norm);
    }
    
    return vector;
  }

  hashString(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32bit integer
    }
    return Math.abs(hash);
  }
}

module.exports = { SimpleEmbedding };
