/**
 * Pure JavaScript Embedding - No native modules required
 * Uses character n-grams and word features
 * Quality is lower than neural embeddings but works everywhere
 */

class PureJSEmbedding {
  constructor(config = {}) {
    this.dim = config.dim || 384;
    // Vocabulary for common words
    this.vocab = this.buildVocabulary();
  }

  async init() {
    // No async initialization needed
    return true;
  }

  buildVocabulary() {
    // Common English and Chinese words/patterns
    const commonWords = [
      'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
      'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
      '用户', '喜欢', '使用', '项目', '时间', '决定', '偏好', '界面',
      'user', 'like', 'prefer', 'use', 'project', 'time', 'decide',
      'dark', 'light', 'mode', 'theme', 'color', 'style', 'ui', 'ux'
    ];
    
    const vocab = {};
    commonWords.forEach((word, i) => {
      vocab[word] = i + 1000; // Reserve 0-999 for special tokens
    });
    return vocab;
  }

  async embed(text) {
    const vector = new Array(this.dim).fill(0);
    const normalized = text.toLowerCase().trim();
    
    // 1. Character trigrams (local structure)
    for (let i = 0; i < normalized.length - 2; i++) {
      const trigram = normalized.substring(i, i + 3);
      const hash = this.hashString(trigram);
      vector[hash % this.dim] += 0.5;
    }
    
    // 2. Word-level features (semantic)
    const words = normalized.split(/\s+/);
    for (const word of words) {
      // Exact word match from vocabulary
      if (this.vocab[word]) {
        vector[this.vocab[word] % this.dim] += 2.0;
      }
      
      // Word hash for unknown words
      const hash = this.hashString(word);
      vector[hash % this.dim] += 1.0;
      
      // Prefix/suffix features
      if (word.length >= 3) {
        const prefix = word.slice(0, 3);
        const suffix = word.slice(-3);
        vector[this.hashString(prefix) % this.dim] += 0.3;
        vector[this.hashString(suffix) % this.dim] += 0.3;
      }
      
      // Character-level features
      for (let i = 0; i < word.length; i++) {
        const char = word[i];
        const charCode = char.charCodeAt(0);
        vector[(charCode * 7) % this.dim] += 0.1;
      }
    }
    
    // 3. Position-weighted features (word order matters)
    words.forEach((word, pos) => {
      const weight = 1.0 / (pos + 1); // Earlier words more important
      const hash = this.hashString(word);
      vector[hash % this.dim] += weight * 0.5;
    });
    
    // 4. Length features
    vector[normalized.length % this.dim] += 0.2;
    vector[words.length % this.dim] += 0.2;
    
    // L2 normalize
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
      hash = hash & hash;
    }
    return Math.abs(hash);
  }
}

module.exports = { PureJSEmbedding };
