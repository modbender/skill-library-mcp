/**
 * ContextAnalyzer for OpenClaw Context Optimizer
 *
 * Analyzes context to identify patterns that can be compressed or removed.
 * Learns over time what context is important and what can be safely pruned.
 */

import { randomUUID } from 'crypto';

/**
 * ContextAnalyzer class
 * Analyzes context to identify compression opportunities and learn patterns
 */
export class ContextAnalyzer {
  constructor(storage) {
    this.storage = storage;

    // Common boilerplate phrases (low value)
    this.boilerplatePhrases = new Set([
      'as an ai assistant',
      'i am here to help',
      'let me help you',
      'of course',
      'certainly',
      'i understand',
      'thank you for',
      'you are welcome',
      'feel free to ask',
      'is there anything else',
      'how can i help',
      'what can i do for you'
    ]);

    // Pattern type indicators
    this.patternIndicators = {
      redundant: ['repeated', 'duplicate', 'again', 'once more'],
      high_value: ['error', 'warning', 'critical', 'important', 'key', 'must', 'required'],
      low_value: ['maybe', 'perhaps', 'might', 'could', 'possibly'],
      template: ['template', 'boilerplate', 'standard', 'default', 'example']
    };

    // Code language indicators (high value)
    this.codeLanguages = new Set([
      'javascript', 'typescript', 'python', 'java', 'rust', 'go', 'c++', 'c#',
      'ruby', 'php', 'swift', 'kotlin', 'sql', 'bash', 'shell'
    ]);
  }

  /**
   * Analyze context and identify patterns
   * @param {string|object} context - Context to analyze (string or object with text)
   * @returns {Promise<object>} Analysis results
   */
  async analyzeContext(context) {
    const contextText = typeof context === 'string' ? context : context.text || '';

    if (!contextText || contextText.trim().length === 0) {
      return {
        sections: [],
        patterns: [],
        totalTokens: 0,
        redundantTokens: 0,
        lowValueTokens: 0
      };
    }

    try {
      // Extract sections from context
      const sections = this.extractSections(contextText);

      // Analyze each section for importance
      const analyzedSections = sections.map(section => ({
        ...section,
        importance: this.calculateImportance(section.text, context)
      }));

      // Identify patterns
      const redundantPatterns = await this.identifyRedundantPatterns(contextText);
      const highValuePatterns = await this.identifyHighValuePatterns(contextText);
      const templatePatterns = await this.identifyTemplates(contextText);

      // Estimate token counts (rough approximation: 1 token ≈ 4 characters)
      const totalTokens = Math.ceil(contextText.length / 4);
      const redundantTokens = redundantPatterns.reduce((sum, p) => sum + (p.tokenImpact || 0), 0);
      const lowValueSections = analyzedSections.filter(s => s.importance < 0.3);
      const lowValueTokens = lowValueSections.reduce((sum, s) => sum + Math.ceil(s.text.length / 4), 0);

      return {
        sections: analyzedSections,
        patterns: {
          redundant: redundantPatterns,
          highValue: highValuePatterns,
          template: templatePatterns
        },
        totalTokens,
        redundantTokens,
        lowValueTokens,
        compressionPotential: (redundantTokens + lowValueTokens) / totalTokens
      };
    } catch (error) {
      console.error('[ContextAnalyzer] Error analyzing context:', error);
      return {
        sections: [],
        patterns: { redundant: [], highValue: [], template: [] },
        totalTokens: 0,
        redundantTokens: 0,
        lowValueTokens: 0
      };
    }
  }

  /**
   * Calculate importance score for text (0.0 to 1.0)
   * @param {string} text - Text to analyze
   * @param {object} context - Additional context metadata
   * @returns {number} Importance score
   */
  calculateImportance(text, context = {}) {
    let score = 0.5; // Base score

    // Boost for code snippets
    if (text.includes('```') || text.match(/^\s*(function|class|const|let|var|def|import|from)\s+/m)) {
      score += 0.3;
    }

    // Boost for numbers/data
    if (text.match(/\b\d+(?:\.\d+)?(?:[a-z%]+)?\b/gi)) {
      score += 0.2;
    }

    // Boost for short and specific text (50-200 chars)
    if (text.length >= 50 && text.length <= 200) {
      score += 0.2;
    }

    // Boost for user-provided context (if metadata indicates this)
    if (context.source === 'user' || context.userProvided) {
      score += 0.3;
    }

    // Penalty for very long text (>500 chars)
    if (text.length > 500) {
      score -= 0.2;
    }

    // Penalty for generic/boilerplate
    const lowerText = text.toLowerCase();
    if (this.isBoilerplate(lowerText)) {
      score -= 0.3;
    }

    // Penalty for no specific entities
    if (!this.containsEntity(text)) {
      score -= 0.1;
    }

    // Boost for high-value indicators
    for (const indicator of this.patternIndicators.high_value) {
      if (lowerText.includes(indicator)) {
        score += 0.1;
        break;
      }
    }

    // Penalty for low-value indicators
    for (const indicator of this.patternIndicators.low_value) {
      if (lowerText.includes(indicator)) {
        score -= 0.1;
        break;
      }
    }

    // Ensure score is between 0.0 and 1.0
    return Math.max(0.0, Math.min(1.0, score));
  }

  /**
   * Identify redundant patterns in context
   * @param {string} context - Context text to analyze
   * @returns {Promise<Array>} Array of redundant patterns
   */
  async identifyRedundantPatterns(context) {
    const patterns = [];
    const sections = this.extractSections(context);

    // Find duplicate or near-duplicate sections
    const seen = new Map();

    for (let i = 0; i < sections.length; i++) {
      const section = sections[i];
      const normalized = this.normalizeText(section.text);

      if (normalized.length < 20) continue; // Skip very short sections

      // Check for exact duplicates
      if (seen.has(normalized)) {
        const existingPattern = patterns.find(p => p.text === normalized);
        if (existingPattern) {
          existingPattern.frequency += 1;
          existingPattern.tokenImpact += Math.ceil(section.text.length / 4);
        } else {
          patterns.push({
            pattern_id: randomUUID(),
            pattern_type: 'redundant',
            pattern_text: section.text.substring(0, 200),
            frequency: 2,
            token_impact: Math.ceil(section.text.length / 4),
            importance_score: 0.1
          });
        }
      } else {
        seen.set(normalized, i);

        // Check for similar sections
        for (const [existingNormalized, existingIdx] of seen.entries()) {
          if (existingNormalized === normalized) continue;

          const similarity = this.calculateSimilarity(normalized, existingNormalized);
          if (similarity > 0.85) {
            patterns.push({
              pattern_id: randomUUID(),
              pattern_type: 'redundant',
              pattern_text: section.text.substring(0, 200),
              frequency: 2,
              token_impact: Math.ceil(section.text.length / 4),
              importance_score: 0.1
            });
            break;
          }
        }
      }
    }

    return patterns;
  }

  /**
   * Identify high-value patterns (should keep)
   * @param {string} context - Context text to analyze
   * @returns {Promise<Array>} Array of high-value patterns
   */
  async identifyHighValuePatterns(context) {
    const patterns = [];
    const sections = this.extractSections(context);

    for (const section of sections) {
      const text = section.text;
      const lowerText = text.toLowerCase();

      // Code blocks are high value
      if (text.includes('```')) {
        patterns.push({
          pattern_id: randomUUID(),
          pattern_type: 'high_value',
          pattern_text: text.substring(0, 200),
          frequency: 1,
          token_impact: Math.ceil(text.length / 4),
          importance_score: 0.9
        });
        continue;
      }

      // Error messages and warnings
      if (lowerText.match(/\b(error|warning|exception|failed|critical)\b/)) {
        patterns.push({
          pattern_id: randomUUID(),
          pattern_type: 'high_value',
          pattern_text: text.substring(0, 200),
          frequency: 1,
          token_impact: Math.ceil(text.length / 4),
          importance_score: 0.85
        });
        continue;
      }

      // Specific data and numbers
      if (text.match(/\b\d+(?:\.\d+)?(?:%|ms|MB|GB|KB)?\b/) && text.length < 300) {
        patterns.push({
          pattern_id: randomUUID(),
          pattern_type: 'high_value',
          pattern_text: text.substring(0, 200),
          frequency: 1,
          token_impact: Math.ceil(text.length / 4),
          importance_score: 0.75
        });
        continue;
      }

      // Named entities and specific references
      if (this.containsEntity(text) && text.length < 250) {
        const importance = this.calculateImportance(text);
        if (importance > 0.7) {
          patterns.push({
            pattern_id: randomUUID(),
            pattern_type: 'high_value',
            pattern_text: text.substring(0, 200),
            frequency: 1,
            token_impact: Math.ceil(text.length / 4),
            importance_score: importance
          });
        }
      }
    }

    return patterns;
  }

  /**
   * Identify template/boilerplate patterns
   * @param {string} context - Context text to analyze
   * @returns {Promise<Array>} Array of template patterns
   */
  async identifyTemplates(context) {
    const patterns = [];
    const sections = this.extractSections(context);

    for (const section of sections) {
      const text = section.text;
      const lowerText = text.toLowerCase();

      // Check for boilerplate phrases
      if (this.isBoilerplate(lowerText)) {
        patterns.push({
          pattern_id: randomUUID(),
          pattern_type: 'template',
          pattern_text: text.substring(0, 200),
          frequency: 1,
          token_impact: Math.ceil(text.length / 4),
          importance_score: 0.1
        });
        continue;
      }

      // Common greeting/closing patterns
      if (lowerText.match(/^(hello|hi|hey|goodbye|bye|thanks|thank you)/)) {
        patterns.push({
          pattern_id: randomUUID(),
          pattern_type: 'template',
          pattern_text: text.substring(0, 200),
          frequency: 1,
          token_impact: Math.ceil(text.length / 4),
          importance_score: 0.15
        });
        continue;
      }

      // Generic filler text
      if (lowerText.match(/\b(basically|essentially|actually|literally|just|simply|really)\b/g)?.length > 3) {
        patterns.push({
          pattern_id: randomUUID(),
          pattern_type: 'template',
          pattern_text: text.substring(0, 200),
          frequency: 1,
          token_impact: Math.ceil(text.length / 4),
          importance_score: 0.2
        });
      }
    }

    return patterns;
  }

  /**
   * Learn from compression feedback
   * @param {string} sessionId - Compression session ID
   * @param {object} feedback - Feedback data
   * @returns {Promise<void>}
   */
  async learnFromFeedback(sessionId, feedback) {
    try {
      // Store feedback
      const stmt = this.storage.db.prepare(`
        INSERT INTO compression_feedback (session_id, feedback_type, feedback_score, notes)
        VALUES (?, ?, ?, ?)
      `);

      stmt.run(
        sessionId,
        feedback.type || 'success',
        feedback.score || 0.5,
        feedback.notes || null
      );

      // Get session details
      const session = this.storage.db.prepare(`
        SELECT * FROM compression_sessions WHERE session_id = ?
      `).get(sessionId);

      if (!session) return;

      // Update pattern importance based on feedback
      // If compression was successful (score > 0.7), boost high-value patterns
      // If compression failed (score < 0.3), penalize patterns that were removed
      const feedbackScore = feedback.score || 0.5;

      if (feedbackScore > 0.7) {
        // Good compression - patterns we kept were valuable
        // This is implicitly learned via usage frequency
      } else if (feedbackScore < 0.3) {
        // Bad compression - we may have removed important context
        // Reduce importance of 'low_value' patterns for this agent
        this.storage.db.prepare(`
          UPDATE compression_patterns
          SET importance_score = importance_score * 0.9
          WHERE agent_wallet = ? AND pattern_type = 'low_value'
        `).run(session.agent_wallet);
      }

      // Update session quality score
      this.storage.db.prepare(`
        UPDATE compression_sessions
        SET quality_score = ?
        WHERE session_id = ?
      `).run(feedbackScore, sessionId);

    } catch (error) {
      console.error('[ContextAnalyzer] Error learning from feedback:', error);
    }
  }

  /**
   * Get learned patterns for an agent
   * @param {string} agentWallet - Agent wallet address
   * @returns {Promise<object>} Learned patterns by type
   */
  async getLearnedPatterns(agentWallet) {
    try {
      const patterns = this.storage.db.prepare(`
        SELECT * FROM compression_patterns
        WHERE agent_wallet = ? OR agent_wallet IS NULL
        ORDER BY importance_score DESC, frequency DESC
      `).all(agentWallet);

      // Group by pattern type
      const grouped = {
        redundant: [],
        low_value: [],
        high_value: [],
        template: []
      };

      for (const pattern of patterns) {
        if (grouped[pattern.pattern_type]) {
          grouped[pattern.pattern_type].push(pattern);
        }
      }

      return grouped;
    } catch (error) {
      console.error('[ContextAnalyzer] Error getting learned patterns:', error);
      return {
        redundant: [],
        low_value: [],
        high_value: [],
        template: []
      };
    }
  }

  /**
   * Extract text sections/blocks from context
   * @param {string} context - Context text
   * @returns {Array<object>} Array of sections
   */
  extractSections(context) {
    const sections = [];

    // Split by double newlines (paragraphs)
    const paragraphs = context.split(/\n\s*\n/);

    for (const paragraph of paragraphs) {
      const trimmed = paragraph.trim();
      if (trimmed.length === 0) continue;

      sections.push({
        text: trimmed,
        type: this.detectSectionType(trimmed)
      });
    }

    // If no paragraphs found, split by sentences
    if (sections.length === 0) {
      const sentences = this.splitIntoSentences(context);
      for (const sentence of sentences) {
        if (sentence.length > 10) {
          sections.push({
            text: sentence,
            type: this.detectSectionType(sentence)
          });
        }
      }
    }

    return sections;
  }

  /**
   * Detect section type
   * @param {string} text - Section text
   * @returns {string} Section type
   */
  detectSectionType(text) {
    if (text.includes('```')) return 'code';
    if (text.match(/^\s*[-*•]\s+/)) return 'list';
    if (text.match(/^\s*\d+\.\s+/)) return 'numbered_list';
    if (text.match(/\b(error|warning|exception)\b/i)) return 'error';
    if (text.length < 50) return 'short';
    return 'text';
  }

  /**
   * Calculate text similarity using cosine similarity
   * @param {string} text1 - First text
   * @param {string} text2 - Second text
   * @returns {number} Similarity score (0.0 to 1.0)
   */
  calculateSimilarity(text1, text2) {
    const tokens1 = this.tokenize(text1);
    const tokens2 = this.tokenize(text2);

    if (tokens1.length === 0 || tokens2.length === 0) {
      return 0.0;
    }

    // Create vocabulary
    const vocabulary = new Set([...tokens1, ...tokens2]);

    // Create frequency vectors
    const vector1 = new Map();
    const vector2 = new Map();

    for (const token of tokens1) {
      vector1.set(token, (vector1.get(token) || 0) + 1);
    }

    for (const token of tokens2) {
      vector2.set(token, (vector2.get(token) || 0) + 1);
    }

    // Calculate cosine similarity
    let dotProduct = 0;
    let magnitude1 = 0;
    let magnitude2 = 0;

    for (const token of vocabulary) {
      const freq1 = vector1.get(token) || 0;
      const freq2 = vector2.get(token) || 0;

      dotProduct += freq1 * freq2;
      magnitude1 += freq1 * freq1;
      magnitude2 += freq2 * freq2;
    }

    magnitude1 = Math.sqrt(magnitude1);
    magnitude2 = Math.sqrt(magnitude2);

    if (magnitude1 === 0 || magnitude2 === 0) {
      return 0.0;
    }

    return dotProduct / (magnitude1 * magnitude2);
  }

  /**
   * Simple tokenization for similarity calculation
   * @param {string} text - Text to tokenize
   * @returns {Array<string>} Array of tokens
   */
  tokenize(text) {
    return text
      .toLowerCase()
      .replace(/[^\w\s]/g, ' ')
      .split(/\s+/)
      .filter(token => token.length > 2 && !this.isStopWord(token));
  }

  /**
   * Normalize text for comparison
   * @param {string} text - Text to normalize
   * @returns {string} Normalized text
   */
  normalizeText(text) {
    return text
      .toLowerCase()
      .replace(/\s+/g, ' ')
      .replace(/[^\w\s]/g, '')
      .trim();
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
   * Check if text is boilerplate
   * @param {string} text - Text to check (lowercase)
   * @returns {boolean} True if boilerplate
   */
  isBoilerplate(text) {
    for (const phrase of this.boilerplatePhrases) {
      if (text.includes(phrase)) {
        return true;
      }
    }
    return false;
  }

  /**
   * Check if text contains named entities
   * @param {string} text - Text to check
   * @returns {boolean} True if contains entities
   */
  containsEntity(text) {
    // Check for capitalized words (potential names, places, etc.)
    return /\b[A-Z][a-z]+/.test(text);
  }

  /**
   * Check if word is a stop word
   * @param {string} word - Word to check
   * @returns {boolean} True if stop word
   */
  isStopWord(word) {
    const stopWords = new Set([
      'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
      'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
      'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
      'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their'
    ]);
    return stopWords.has(word);
  }
}
