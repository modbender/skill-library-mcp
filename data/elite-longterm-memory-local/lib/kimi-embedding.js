/**
 * Kimi API Embedding - Using Kimi's embedding endpoint
 * No local models required
 */

const axios = require('/usr/lib/node_modules/openclaw/node_modules/axios');

class KimiEmbedding {
  constructor(config = {}) {
    this.apiKey = config.apiKey || process.env.KIMI_API_KEY || process.env.KIMI_PLUGIN_API_KEY;
    this.baseUrl = config.baseUrl || 'https://api.kimi.com/coding';
    this.model = config.model || 'k2p5';
  }

  async init() {
    // No initialization needed
    if (!this.apiKey) {
      throw new Error('KIMI_API_KEY or KIMI_PLUGIN_API_KEY environment variable required');
    }
    return true;
  }

  async embed(text) {
    try {
      // Kimi API doesn't have a dedicated embedding endpoint yet
      // Use the chat completion with a special prompt to get embeddings
      // This is a workaround - in production, use a proper embedding API
      
      const response = await axios.post(
        `${this.baseUrl}/v1/chat/completions`,
        {
          model: this.model,
          messages: [
            {
              role: 'system',
              content: 'You are a text embedding generator. Given any input text, output a fixed-length vector representation as a JSON array of 384 floating point numbers between -1 and 1. Output ONLY the JSON array, no other text.'
            },
            {
              role: 'user',
              content: `Generate embedding for: "${text}"`
            }
          ],
          temperature: 0,
          max_tokens: 2000
        },
        {
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json'
          }
        }
      );

      const content = response.data.choices[0].message.content;
      
      // Parse the JSON array from the response
      const match = content.match(/\[[\s\S]*?\]/);
      if (match) {
        const vector = JSON.parse(match[0]);
        // Ensure correct dimension
        if (vector.length !== 384) {
          // Pad or truncate to 384
          if (vector.length < 384) {
            return [...vector, ...new Array(384 - vector.length).fill(0)];
          } else {
            return vector.slice(0, 384);
          }
        }
        return vector;
      }
      
      throw new Error('Failed to parse embedding from response');
    } catch (err) {
      // Fallback: use simple hashing if API fails
      console.warn('Kimi API embedding failed, using fallback:', err.message);
      return this.fallbackEmbed(text);
    }
  }

  fallbackEmbed(text) {
    // Simple but effective embedding using character n-grams
    const vector = new Array(384).fill(0);
    const normalized = text.toLowerCase().trim();
    
    // Character trigrams
    for (let i = 0; i < normalized.length - 2; i++) {
      const trigram = normalized.substring(i, i + 3);
      const hash = this.hashString(trigram);
      vector[hash % 384] += 1;
    }
    
    // Word-level features
    const words = normalized.split(/\s+/);
    for (const word of words) {
      const hash = this.hashString(word);
      vector[hash % 384] += 2;
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
      hash = hash & hash;
    }
    return Math.abs(hash);
  }
}

module.exports = { KimiEmbedding };
