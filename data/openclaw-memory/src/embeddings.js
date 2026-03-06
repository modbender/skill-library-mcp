/**
 * Embedding Providers for OpenClaw Memory System
 *
 * Provides two embedding options:
 * 1. OpenAI API (text-embedding-3-small) - Fast, high quality
 * 2. Local (@xenova/transformers) - Free, no API key needed
 */

import { pipeline } from '@xenova/transformers';

/**
 * OpenAI Embedding Provider
 * Uses text-embedding-3-small model (512 dimensions)
 * Cost: $0.00002 per 1K tokens (~$0.0001 per memory)
 */
export class OpenAIEmbeddingProvider {
  constructor(apiKey = null) {
    this.apiKey = apiKey || process.env.OPENAI_API_KEY;
    this.model = 'text-embedding-3-small';
    this.apiUrl = 'https://api.openai.com/v1/embeddings';
    this.dimensions = 512;
  }

  /**
   * Generate embedding vector for text
   * @param {string} text - Text to embed
   * @returns {Promise<Float32Array>} Embedding vector
   */
  async generate(text) {
    if (!this.apiKey) {
      throw new Error('OpenAI API key not found. Set OPENAI_API_KEY environment variable.');
    }

    if (!text || typeof text !== 'string' || text.trim().length === 0) {
      throw new Error('Invalid text input for embedding generation');
    }

    try {
      const response = await fetch(this.apiUrl, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          model: this.model,
          input: text.substring(0, 8000), // Truncate to avoid token limits
          dimensions: this.dimensions
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          `OpenAI API error (${response.status}): ${errorData.error?.message || response.statusText}`
        );
      }

      const data = await response.json();

      if (!data.data || !data.data[0] || !data.data[0].embedding) {
        throw new Error('Invalid response from OpenAI API');
      }

      return new Float32Array(data.data[0].embedding);
    } catch (error) {
      if (error.message.includes('fetch')) {
        throw new Error(`Network error connecting to OpenAI API: ${error.message}`);
      }
      throw error;
    }
  }

  /**
   * Get embedding dimensions
   * @returns {number} Dimension count
   */
  getDimensions() {
    return this.dimensions;
  }

  /**
   * Get provider name
   * @returns {string} Provider identifier
   */
  getProviderName() {
    return 'openai';
  }
}

/**
 * Local Embedding Provider
 * Uses Xenova/all-MiniLM-L6-v2 model (384 dimensions)
 * Free, runs locally, no API key needed
 */
export class LocalEmbeddingProvider {
  constructor() {
    this.model = null;
    this.modelName = 'Xenova/all-MiniLM-L6-v2';
    this.dimensions = 384;
    this.initialized = false;
  }

  /**
   * Initialize the local model (lazy loading)
   * @returns {Promise<void>}
   */
  async initialize() {
    if (this.initialized) {
      return;
    }

    try {
      console.log('[LocalEmbedding] Loading model (this may take a moment on first run)...');
      this.model = await pipeline('feature-extraction', this.modelName);
      this.initialized = true;
      console.log('[LocalEmbedding] Model loaded successfully');
    } catch (error) {
      throw new Error(`Failed to initialize local embedding model: ${error.message}`);
    }
  }

  /**
   * Generate embedding vector for text
   * @param {string} text - Text to embed
   * @returns {Promise<Float32Array>} Embedding vector
   */
  async generate(text) {
    if (!text || typeof text !== 'string' || text.trim().length === 0) {
      throw new Error('Invalid text input for embedding generation');
    }

    // Lazy initialization
    if (!this.initialized) {
      await this.initialize();
    }

    try {
      // Truncate text to avoid memory issues
      const truncatedText = text.substring(0, 5000);

      // Generate embedding with mean pooling and normalization
      const output = await this.model(truncatedText, {
        pooling: 'mean',
        normalize: true
      });

      if (!output || !output.data) {
        throw new Error('Invalid output from local embedding model');
      }

      return new Float32Array(output.data);
    } catch (error) {
      throw new Error(`Failed to generate local embedding: ${error.message}`);
    }
  }

  /**
   * Get embedding dimensions
   * @returns {number} Dimension count
   */
  getDimensions() {
    return this.dimensions;
  }

  /**
   * Get provider name
   * @returns {string} Provider identifier
   */
  getProviderName() {
    return 'local';
  }

  /**
   * Check if model is initialized
   * @returns {boolean} Initialization status
   */
  isInitialized() {
    return this.initialized;
  }
}

/**
 * Factory function to create embedding provider
 * @param {string} type - 'openai' or 'local'
 * @param {object} options - Configuration options
 * @returns {OpenAIEmbeddingProvider|LocalEmbeddingProvider}
 */
export function createEmbeddingProvider(type = 'openai', options = {}) {
  switch (type.toLowerCase()) {
    case 'openai':
      return new OpenAIEmbeddingProvider(options.apiKey);
    case 'local':
      return new LocalEmbeddingProvider();
    default:
      throw new Error(`Unknown embedding provider type: ${type}. Use 'openai' or 'local'.`);
  }
}

/**
 * Calculate cosine similarity between two vectors
 * @param {Float32Array} vecA - First vector
 * @param {Float32Array} vecB - Second vector
 * @returns {number} Similarity score (0 to 1)
 */
export function cosineSimilarity(vecA, vecB) {
  if (!vecA || !vecB || vecA.length !== vecB.length) {
    throw new Error('Invalid vectors for cosine similarity calculation');
  }

  let dotProduct = 0;
  let magnitudeA = 0;
  let magnitudeB = 0;

  for (let i = 0; i < vecA.length; i++) {
    dotProduct += vecA[i] * vecB[i];
    magnitudeA += vecA[i] * vecA[i];
    magnitudeB += vecB[i] * vecB[i];
  }

  magnitudeA = Math.sqrt(magnitudeA);
  magnitudeB = Math.sqrt(magnitudeB);

  if (magnitudeA === 0 || magnitudeB === 0) {
    return 0;
  }

  return dotProduct / (magnitudeA * magnitudeB);
}
