/**
 * Session Analyzer - ML-based Session Importance Scoring
 *
 * Analyzes sessions to determine their importance and likelihood
 * of being needed in the future using various heuristics and scoring
 */

const fs = require('fs');

class SessionAnalyzer {
  constructor(config = {}) {
    this.config = {
      minMessagesForImportant: config.minMessagesForImportant || 10,
      toolUsageWeight: config.toolUsageWeight || 0.3,
      conversationDepthWeight: config.conversationDepthWeight || 0.25,
      recencyWeight: config.recencyWeight || 0.25,
      engagementWeight: config.engagementWeight || 0.2,
      ...config
    };

    this.analysisCache = new Map();
  }

  /**
   * Analyze a session and calculate importance score
   * @param {Object} session - Session object with path and metadata
   * @returns {Promise<Object>} Analysis result
   */
  async analyzeSession(session) {
    // Check cache
    const cacheKey = `${session.sessionId}-${session.lastActive.getTime()}`;
    if (this.analysisCache.has(cacheKey)) {
      return this.analysisCache.get(cacheKey);
    }

    try {
      const sessionData = await this._loadSessionData(session.path);

      const analysis = {
        sessionId: session.sessionId,
        importanceScore: 0,
        factors: {},
        classification: '',
        recommendation: '',
        details: {}
      };

      // Calculate various importance factors
      analysis.factors.recency = this._calculateRecencyScore(session.lastActive);
      analysis.factors.engagement = this._calculateEngagementScore(sessionData);
      analysis.factors.toolUsage = this._calculateToolUsageScore(sessionData);
      analysis.factors.conversationDepth = this._calculateConversationDepth(sessionData);
      analysis.factors.complexity = this._calculateComplexityScore(sessionData);
      analysis.factors.errorRate = this._calculateErrorRate(sessionData);
      analysis.factors.uniqueness = this._calculateUniquenessScore(sessionData);

      // Calculate weighted importance score (0-100)
      analysis.importanceScore = this._calculateImportanceScore(analysis.factors);

      // Classify session
      analysis.classification = this._classifySession(analysis.importanceScore, analysis.factors);

      // Generate recommendation
      analysis.recommendation = this._generateRecommendation(analysis);

      // Add detailed metrics
      analysis.details = {
        messageCount: sessionData.messages.length,
        toolCalls: this._countToolCalls(sessionData),
        avgMessageLength: this._calculateAvgMessageLength(sessionData),
        conversationThreads: this._detectConversationThreads(sessionData),
        hasErrors: analysis.factors.errorRate > 0.2,
        isActive: analysis.factors.recency > 80,
        isComplex: analysis.factors.complexity > 60
      };

      // Cache result
      this.analysisCache.set(cacheKey, analysis);

      // Limit cache size
      if (this.analysisCache.size > 1000) {
        const firstKey = this.analysisCache.keys().next().value;
        this.analysisCache.delete(firstKey);
      }

      return analysis;
    } catch (error) {
      return {
        sessionId: session.sessionId,
        importanceScore: 0,
        classification: 'unknown',
        recommendation: 'error',
        error: error.message
      };
    }
  }

  /**
   * Analyze multiple sessions and rank by importance
   * @param {Array} sessions - Array of session objects
   * @returns {Promise<Array>} Ranked sessions with analysis
   */
  async analyzeSessions(sessions) {
    const analyses = await Promise.all(
      sessions.map(session => this.analyzeSession(session))
    );

    // Sort by importance score (descending)
    return analyses.sort((a, b) => b.importanceScore - a.importanceScore);
  }

  /**
   * Get sessions recommended for preservation
   * @param {Array} sessions - Array of session objects
   * @returns {Promise<Array>} Sessions to preserve
   */
  async getSessionsToPreserve(sessions) {
    const analyses = await this.analyzeSessions(sessions);

    return analyses.filter(analysis =>
      analysis.importanceScore >= 60 ||
      analysis.classification === 'critical' ||
      analysis.classification === 'important'
    );
  }

  /**
   * Get sessions safe to prune
   * @param {Array} sessions - Array of session objects
   * @returns {Promise<Array>} Sessions safe to prune
   */
  async getSessionsToPrune(sessions) {
    const analyses = await this.analyzeSessions(sessions);

    return analyses.filter(analysis =>
      analysis.importanceScore < 40 &&
      analysis.classification !== 'critical' &&
      analysis.recommendation === 'safe_to_prune'
    );
  }

  /**
   * Load session data from file
   * @private
   */
  async _loadSessionData(sessionPath) {
    const content = await fs.promises.readFile(sessionPath, 'utf-8');
    return JSON.parse(content);
  }

  /**
   * Calculate recency score (0-100)
   * More recent = higher score
   * @private
   */
  _calculateRecencyScore(lastActive) {
    const ageMs = Date.now() - lastActive.getTime();
    const ageHours = ageMs / (1000 * 60 * 60);

    if (ageHours < 1) return 100;
    if (ageHours < 6) return 90;
    if (ageHours < 24) return 80;
    if (ageHours < 72) return 60;
    if (ageHours < 168) return 40; // 1 week
    if (ageHours < 336) return 20; // 2 weeks
    return 10;
  }

  /**
   * Calculate engagement score based on message count and quality
   * @private
   */
  _calculateEngagementScore(sessionData) {
    if (!sessionData.messages || sessionData.messages.length === 0) {
      return 0;
    }

    const messageCount = sessionData.messages.length;

    // Base score from message count
    let score = Math.min(100, messageCount * 5);

    // Bonus for sustained conversation
    if (messageCount > 20) score += 10;
    if (messageCount > 50) score += 10;

    // Check for back-and-forth interaction
    const userMessages = sessionData.messages.filter(m => m.role === 'user').length;
    const assistantMessages = sessionData.messages.filter(m => m.role === 'assistant').length;

    if (userMessages > 5 && assistantMessages > 5) {
      score += 15; // Good interaction
    }

    return Math.min(100, score);
  }

  /**
   * Calculate tool usage score
   * Sessions with tool usage are often more important
   * @private
   */
  _calculateToolUsageScore(sessionData) {
    if (!sessionData.messages) return 0;

    let toolCallCount = 0;
    const uniqueTools = new Set();

    for (const message of sessionData.messages) {
      if (message.tool_calls) {
        toolCallCount += message.tool_calls.length;

        for (const call of message.tool_calls) {
          if (call.function?.name) {
            uniqueTools.add(call.function.name);
          }
        }
      }
    }

    let score = 0;

    // Base score from tool usage
    if (toolCallCount > 0) score += 30;
    if (toolCallCount > 5) score += 20;
    if (toolCallCount > 10) score += 20;

    // Bonus for diverse tool usage
    score += uniqueTools.size * 5;

    return Math.min(100, score);
  }

  /**
   * Calculate conversation depth
   * Deeper conversations are more valuable
   * @private
   */
  _calculateConversationDepth(sessionData) {
    if (!sessionData.messages || sessionData.messages.length === 0) {
      return 0;
    }

    let depth = 0;

    // Check for multi-turn conversations
    const turns = Math.floor(sessionData.messages.length / 2);
    depth += Math.min(50, turns * 5);

    // Check for long messages (indicate detailed discussion)
    let longMessages = 0;
    for (const message of sessionData.messages) {
      const content = typeof message.content === 'string'
        ? message.content
        : JSON.stringify(message.content);

      if (content.length > 1000) {
        longMessages++;
      }
    }
    depth += Math.min(30, longMessages * 10);

    // Check for code blocks (indicate technical discussion)
    let codeBlocks = 0;
    for (const message of sessionData.messages) {
      const content = typeof message.content === 'string'
        ? message.content
        : JSON.stringify(message.content);

      if (content.includes('```')) {
        codeBlocks++;
      }
    }
    depth += Math.min(20, codeBlocks * 5);

    return Math.min(100, depth);
  }

  /**
   * Calculate complexity score
   * Complex sessions are more valuable
   * @private
   */
  _calculateComplexityScore(sessionData) {
    if (!sessionData.messages || sessionData.messages.length === 0) {
      return 0;
    }

    let complexity = 0;

    // Check for code
    let hasCode = false;
    for (const message of sessionData.messages) {
      const content = typeof message.content === 'string'
        ? message.content
        : JSON.stringify(message.content);

      if (content.includes('```') || content.includes('function') || content.includes('class')) {
        hasCode = true;
        break;
      }
    }
    if (hasCode) complexity += 30;

    // Check for tool usage
    const toolCalls = this._countToolCalls(sessionData);
    complexity += Math.min(30, toolCalls * 3);

    // Check for long messages (detailed explanations)
    const avgLength = this._calculateAvgMessageLength(sessionData);
    if (avgLength > 500) complexity += 20;
    if (avgLength > 1000) complexity += 10;

    // Check for errors and debugging
    let hasErrors = false;
    for (const message of sessionData.messages) {
      const content = typeof message.content === 'string'
        ? message.content
        : JSON.stringify(message.content);

      if (content.toLowerCase().includes('error') ||
          content.toLowerCase().includes('debug') ||
          content.toLowerCase().includes('fix')) {
        hasErrors = true;
        break;
      }
    }
    if (hasErrors) complexity += 10;

    return Math.min(100, complexity);
  }

  /**
   * Calculate error rate in session
   * High error rate might indicate abandoned/failed session
   * @private
   */
  _calculateErrorRate(sessionData) {
    if (!sessionData.messages || sessionData.messages.length === 0) {
      return 0;
    }

    let errorCount = 0;

    for (const message of sessionData.messages) {
      const content = typeof message.content === 'string'
        ? message.content
        : JSON.stringify(message.content);

      if (content.toLowerCase().includes('error:') ||
          content.toLowerCase().includes('failed') ||
          content.toLowerCase().includes('exception')) {
        errorCount++;
      }

      if (message.tool_results) {
        for (const result of message.tool_results) {
          if (result.is_error || result.error) {
            errorCount++;
          }
        }
      }
    }

    return errorCount / sessionData.messages.length;
  }

  /**
   * Calculate uniqueness score
   * Unique sessions are more valuable
   * @private
   */
  _calculateUniquenessScore(sessionData) {
    // Simple heuristic: sessions with unique tool combinations or topics
    let score = 50; // Base score

    // Check for unique tool combinations
    const tools = new Set();
    if (sessionData.messages) {
      for (const message of sessionData.messages) {
        if (message.tool_calls) {
          for (const call of message.tool_calls) {
            if (call.function?.name) {
              tools.add(call.function.name);
            }
          }
        }
      }
    }

    // More unique tools = higher score
    score += Math.min(30, tools.size * 5);

    return Math.min(100, score);
  }

  /**
   * Calculate weighted importance score
   * @private
   */
  _calculateImportanceScore(factors) {
    const weights = {
      recency: this.config.recencyWeight,
      engagement: this.config.engagementWeight,
      toolUsage: this.config.toolUsageWeight,
      conversationDepth: this.config.conversationDepthWeight,
      complexity: 0.15,
      uniqueness: 0.1
    };

    let score = 0;
    score += factors.recency * weights.recency;
    score += factors.engagement * weights.engagement;
    score += factors.toolUsage * weights.toolUsage;
    score += factors.conversationDepth * weights.conversationDepth;
    score += factors.complexity * weights.complexity;
    score += factors.uniqueness * weights.uniqueness;

    // Penalize high error rate
    score *= (1 - factors.errorRate * 0.5);

    return Math.min(100, Math.max(0, score));
  }

  /**
   * Classify session based on importance score
   * @private
   */
  _classifySession(score, factors) {
    if (score >= 80) return 'critical';
    if (score >= 60) return 'important';
    if (score >= 40) return 'moderate';
    if (score >= 20) return 'low';
    return 'minimal';
  }

  /**
   * Generate recommendation for session
   * @private
   */
  _generateRecommendation(analysis) {
    const { importanceScore, classification, factors } = analysis;

    if (importanceScore >= 80) {
      return 'preserve';
    }

    if (importanceScore >= 60) {
      return 'preserve_if_space';
    }

    if (importanceScore < 20) {
      return 'safe_to_prune';
    }

    if (factors.recency < 30 && factors.engagement < 30) {
      return 'safe_to_prune';
    }

    if (factors.errorRate > 0.5) {
      return 'candidate_for_pruning';
    }

    return 'evaluate_case_by_case';
  }

  /**
   * Count tool calls in session
   * @private
   */
  _countToolCalls(sessionData) {
    if (!sessionData.messages) return 0;

    let count = 0;
    for (const message of sessionData.messages) {
      if (message.tool_calls) {
        count += message.tool_calls.length;
      }
    }
    return count;
  }

  /**
   * Calculate average message length
   * @private
   */
  _calculateAvgMessageLength(sessionData) {
    if (!sessionData.messages || sessionData.messages.length === 0) {
      return 0;
    }

    let totalLength = 0;
    for (const message of sessionData.messages) {
      const content = typeof message.content === 'string'
        ? message.content
        : JSON.stringify(message.content);

      totalLength += content.length;
    }

    return totalLength / sessionData.messages.length;
  }

  /**
   * Detect conversation threads
   * @private
   */
  _detectConversationThreads(sessionData) {
    // Simple heuristic: count user-assistant exchanges
    if (!sessionData.messages) return 0;

    let threads = 0;
    let lastRole = null;

    for (const message of sessionData.messages) {
      if (message.role !== lastRole && lastRole !== null) {
        threads++;
      }
      lastRole = message.role;
    }

    return Math.ceil(threads / 2);
  }

  /**
   * Clear analysis cache
   */
  clearCache() {
    this.analysisCache.clear();
  }

  /**
   * Get cache statistics
   */
  getCacheStats() {
    return {
      size: this.analysisCache.size,
      entries: Array.from(this.analysisCache.keys())
    };
  }
}

module.exports = SessionAnalyzer;
