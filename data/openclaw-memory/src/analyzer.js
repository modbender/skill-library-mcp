/**
 * MemoryAnalyzer for OpenClaw Memory System
 *
 * Extracts important information from requests/responses and decides what to remember.
 * Classifies memory types, calculates importance scores, extracts metadata, and detects redundancy.
 */

import { randomUUID } from 'crypto';
import { cosineSimilarity } from './embeddings.js';

/**
 * MemoryAnalyzer class
 * Analyzes interactions to extract memorable information
 */
export class MemoryAnalyzer {
  constructor(storage, embeddingProvider) {
    this.storage = storage;
    this.embeddingProvider = embeddingProvider;

    // Common phrases to filter out (low value)
    this.commonPhrases = new Set([
      'thank you',
      'thanks',
      'please',
      'ok',
      'okay',
      'yes',
      'no',
      'hello',
      'hi',
      'bye',
      'goodbye',
      'how are you',
      'what is',
      'tell me',
      'can you',
      'could you',
      'would you'
    ]);

    // Memory type indicators
    this.typeIndicators = {
      fact: ['is', 'are', 'was', 'were', 'has', 'have', 'called', 'named', 'located', 'works at'],
      preference: ['prefer', 'like', 'love', 'hate', 'dislike', 'favorite', 'always', 'never', 'usually'],
      pattern: ['every time', 'whenever', 'always', 'typically', 'usually', 'tend to', 'often'],
      conversation: ['said', 'asked', 'mentioned', 'discussed', 'talked about', 'explained']
    };
  }

  /**
   * Analyze request/response interaction and extract memories
   * @param {object} request - Request data
   * @param {object} response - Response data
   * @returns {Promise<Array>} Array of memory objects
   */
  async analyzeInteraction(request, response) {
    const memories = [];

    try {
      // Extract facts from request (user statements)
      const requestMemories = await this.extractFromRequest(request);
      memories.push(...requestMemories);

      // Extract facts from response (important information)
      const responseMemories = await this.extractFromResponse(response);
      memories.push(...responseMemories);

      // Detect patterns across interaction
      const patternMemories = await this.detectPatterns(request, response);
      memories.push(...patternMemories);

      // Filter out redundant memories
      const deduplicatedMemories = await this.deduplicateMemories(memories);

      // Generate embeddings for all memories
      for (const memory of deduplicatedMemories) {
        if (!memory.embedding_vector) {
          memory.embedding_vector = await this.generateEmbedding(memory.content);
        }
      }

      return deduplicatedMemories;
    } catch (error) {
      console.error('[MemoryAnalyzer] Error analyzing interaction:', error);
      return [];
    }
  }

  /**
   * Extract memories from user request
   * @param {object} request - Request data
   * @returns {Promise<Array>} Extracted memories
   */
  async extractFromRequest(request) {
    const memories = [];
    const prompt = request.prompt || request.message || '';

    if (!prompt || prompt.trim().length === 0) {
      return memories;
    }

    // Extract explicit preferences
    const preferences = this.extractPreferences(prompt);
    for (const pref of preferences) {
      memories.push({
        memory_id: randomUUID(),
        content: pref,
        memory_type: 'preference',
        importance_score: 0.7,
        context_metadata: JSON.stringify(await this.extractMetadata(pref)),
        timestamp: new Date().toISOString()
      });
    }

    // Extract factual statements
    const facts = this.extractFacts(prompt);
    for (const fact of facts) {
      memories.push({
        memory_id: randomUUID(),
        content: fact,
        memory_type: 'fact',
        importance_score: 0.6,
        context_metadata: JSON.stringify(await this.extractMetadata(fact)),
        timestamp: new Date().toISOString()
      });
    }

    return memories;
  }

  /**
   * Extract memories from agent response
   * @param {object} response - Response data
   * @returns {Promise<Array>} Extracted memories
   */
  async extractFromResponse(response) {
    const memories = [];
    const content = response.content || response.text || '';

    if (!content || content.trim().length === 0) {
      return memories;
    }

    // Extract important facts from response (e.g., code snippets, key information)
    const facts = this.extractImportantFacts(content);
    for (const fact of facts) {
      memories.push({
        memory_id: randomUUID(),
        content: fact,
        memory_type: 'conversation',
        importance_score: 0.5,
        context_metadata: JSON.stringify(await this.extractMetadata(fact)),
        timestamp: new Date().toISOString()
      });
    }

    return memories;
  }

  /**
   * Detect patterns from request/response
   * @param {object} request - Request data
   * @param {object} response - Response data
   * @returns {Promise<Array>} Pattern memories
   */
  async detectPatterns(request, response) {
    const memories = [];

    // Pattern detection is simplified for MVP
    // Future: Analyze historical interactions to detect recurring patterns
    const prompt = request.prompt || request.message || '';

    if (prompt.toLowerCase().includes('always') || prompt.toLowerCase().includes('every time')) {
      const patternText = this.extractSentence(prompt, ['always', 'every time']);
      if (patternText) {
        memories.push({
          memory_id: randomUUID(),
          content: patternText,
          memory_type: 'pattern',
          importance_score: 0.8,
          context_metadata: JSON.stringify(await this.extractMetadata(patternText)),
          timestamp: new Date().toISOString()
        });
      }
    }

    return memories;
  }

  /**
   * Extract preference statements
   * @param {string} text - Text to analyze
   * @returns {Array<string>} Preference statements
   */
  extractPreferences(text) {
    const preferences = [];
    const sentences = this.splitIntoSentences(text);

    for (const sentence of sentences) {
      const lower = sentence.toLowerCase();

      // Check for preference indicators
      for (const indicator of this.typeIndicators.preference) {
        if (lower.includes(indicator)) {
          const cleaned = this.cleanSentence(sentence);
          if (cleaned && !this.isCommonPhrase(cleaned)) {
            preferences.push(cleaned);
            break;
          }
        }
      }
    }

    return preferences;
  }

  /**
   * Extract factual statements
   * @param {string} text - Text to analyze
   * @returns {Array<string>} Fact statements
   */
  extractFacts(text) {
    const facts = [];
    const sentences = this.splitIntoSentences(text);

    for (const sentence of sentences) {
      const lower = sentence.toLowerCase();

      // Check for fact indicators
      for (const indicator of this.typeIndicators.fact) {
        if (lower.includes(indicator)) {
          const cleaned = this.cleanSentence(sentence);
          if (cleaned && !this.isCommonPhrase(cleaned) && this.containsEntity(cleaned)) {
            facts.push(cleaned);
            break;
          }
        }
      }
    }

    return facts;
  }

  /**
   * Extract important facts from text
   * @param {string} text - Text to analyze
   * @returns {Array<string>} Important facts
   */
  extractImportantFacts(text) {
    const facts = [];

    // Extract code blocks (important technical information)
    const codeBlocks = text.match(/```[\s\S]*?```/g);
    if (codeBlocks && codeBlocks.length > 0) {
      for (const block of codeBlocks) {
        const language = block.match(/```(\w+)/)?.[1] || 'code';
        facts.push(`Code example in ${language}: ${block.substring(0, 200)}...`);
      }
    }

    // Extract numbered/bulleted lists (structured information)
    const listItems = text.match(/^[\s]*[-*•]\s+.+$/gm);
    if (listItems && listItems.length > 2) {
      facts.push(`Key points discussed: ${listItems.slice(0, 3).join('; ')}`);
    }

    return facts;
  }

  /**
   * Classify memory type
   * @param {string} content - Memory content
   * @returns {string} Memory type
   */
  classifyMemoryType(content) {
    const lower = content.toLowerCase();

    // Check each type's indicators
    for (const [type, indicators] of Object.entries(this.typeIndicators)) {
      for (const indicator of indicators) {
        if (lower.includes(indicator)) {
          return type;
        }
      }
    }

    // Default to conversation
    return 'conversation';
  }

  /**
   * Calculate importance score (0.0 to 1.0)
   * @param {object} memory - Memory object
   * @param {object} context - Context data
   * @returns {number} Importance score
   */
  calculateImportance(memory, context = {}) {
    let score = 0.5; // Base score

    // Boost for explicit facts
    if (memory.memory_type === 'fact') {
      score += 0.2;
    }

    // Boost for user preferences
    if (memory.memory_type === 'preference') {
      score += 0.3;
    }

    // Boost for patterns
    if (memory.memory_type === 'pattern') {
      score += 0.3;
    }

    // Penalize common phrases
    if (this.isCommonPhrase(memory.content)) {
      score -= 0.2;
    }

    // Boost for named entities
    const metadata = typeof memory.context_metadata === 'string'
      ? JSON.parse(memory.context_metadata)
      : memory.context_metadata;

    if (metadata?.entities && metadata.entities.length > 0) {
      score += 0.1 * Math.min(metadata.entities.length, 3);
    }

    // Boost for keywords
    if (metadata?.keywords && metadata.keywords.length > 0) {
      score += 0.05 * Math.min(metadata.keywords.length, 2);
    }

    // Ensure score is between 0.0 and 1.0
    return Math.max(0.0, Math.min(1.0, score));
  }

  /**
   * Extract metadata (tags, entities, keywords)
   * @param {string} content - Content to analyze
   * @returns {Promise<object>} Metadata object
   */
  async extractMetadata(content) {
    const metadata = {
      tags: [],
      entities: [],
      keywords: []
    };

    // Extract potential entities (capitalized words/phrases)
    const entities = content.match(/\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b/g);
    if (entities) {
      metadata.entities = [...new Set(entities)].slice(0, 5);
    }

    // Extract keywords (meaningful words)
    const words = content.toLowerCase().match(/\b[a-z]{4,}\b/g);
    if (words) {
      const filtered = words.filter(word => !this.commonPhrases.has(word));
      const frequency = {};
      for (const word of filtered) {
        frequency[word] = (frequency[word] || 0) + 1;
      }
      metadata.keywords = Object.keys(frequency)
        .sort((a, b) => frequency[b] - frequency[a])
        .slice(0, 5);
    }

    // Extract tags based on content type
    if (content.includes('```')) {
      metadata.tags.push('code');
    }
    if (content.match(/\b(python|javascript|typescript|java|rust|go)\b/i)) {
      metadata.tags.push('programming');
    }
    if (content.match(/\b(api|endpoint|request|response)\b/i)) {
      metadata.tags.push('api');
    }

    return metadata;
  }

  /**
   * Generate embedding vector
   * @param {string} text - Text to embed
   * @returns {Promise<Buffer>} Serialized embedding vector
   */
  async generateEmbedding(text) {
    try {
      const vector = await this.embeddingProvider.generate(text);
      // Convert Float32Array to Buffer for storage
      return Buffer.from(vector.buffer);
    } catch (error) {
      console.error('[MemoryAnalyzer] Error generating embedding:', error);
      return null;
    }
  }

  /**
   * Detect redundancy using cosine similarity
   * @param {object} newMemory - New memory to check
   * @param {Array} existingMemories - Existing memories to compare against
   * @returns {Promise<boolean>} True if redundant
   */
  async isRedundant(newMemory, existingMemories) {
    if (!newMemory.embedding_vector || existingMemories.length === 0) {
      return false;
    }

    const newVector = new Float32Array(newMemory.embedding_vector.buffer || newMemory.embedding_vector);

    for (const existing of existingMemories) {
      if (!existing.embedding_vector) {
        continue;
      }

      const existingVector = new Float32Array(
        existing.embedding_vector.buffer || existing.embedding_vector
      );

      const similarity = cosineSimilarity(newVector, existingVector);

      // If similarity > 0.95, consider it redundant
      if (similarity > 0.95) {
        return true;
      }
    }

    return false;
  }

  /**
   * Deduplicate memories within a batch
   * @param {Array} memories - Memories to deduplicate
   * @returns {Promise<Array>} Deduplicated memories
   */
  async deduplicateMemories(memories) {
    if (memories.length <= 1) {
      return memories;
    }

    const unique = [];

    for (const memory of memories) {
      // Generate embedding if not present
      if (!memory.embedding_vector) {
        memory.embedding_vector = await this.generateEmbedding(memory.content);
      }

      // Check if redundant with existing unique memories
      const isRedundant = await this.isRedundant(memory, unique);

      if (!isRedundant) {
        unique.push(memory);
      }
    }

    return unique;
  }

  /**
   * Split text into sentences
   * @param {string} text - Text to split
   * @returns {Array<string>} Sentences
   */
  splitIntoSentences(text) {
    return text
      .split(/[.!?]+/)
      .map(s => s.trim())
      .filter(s => s.length > 0);
  }

  /**
   * Clean sentence for storage
   * @param {string} sentence - Sentence to clean
   * @returns {string} Cleaned sentence
   */
  cleanSentence(sentence) {
    return sentence
      .trim()
      .replace(/\s+/g, ' ')
      .replace(/[^\w\s.,!?'-]/g, '');
  }

  /**
   * Check if text is a common phrase
   * @param {string} text - Text to check
   * @returns {boolean} True if common phrase
   */
  isCommonPhrase(text) {
    const lower = text.toLowerCase().trim();
    return this.commonPhrases.has(lower) || lower.split(' ').length < 3;
  }

  /**
   * Check if text contains named entities
   * @param {string} text - Text to check
   * @returns {boolean} True if contains entities
   */
  containsEntity(text) {
    return /\b[A-Z][a-z]+/.test(text);
  }

  /**
   * Extract sentence containing keywords
   * @param {string} text - Text to search
   * @param {Array<string>} keywords - Keywords to find
   * @returns {string|null} Extracted sentence
   */
  extractSentence(text, keywords) {
    const sentences = this.splitIntoSentences(text);

    for (const sentence of sentences) {
      const lower = sentence.toLowerCase();
      for (const keyword of keywords) {
        if (lower.includes(keyword.toLowerCase())) {
          return this.cleanSentence(sentence);
        }
      }
    }

    return null;
  }
}
