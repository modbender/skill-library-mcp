/**
 * TaskAnalyzer for OpenClaw Smart Router
 *
 * Analyzes incoming requests to determine task complexity and type.
 * This informs model selection to optimize for quality and cost.
 */

import { randomUUID } from 'crypto';

/**
 * TaskAnalyzer class
 * Analyzes tasks to determine complexity, type, and requirements
 */
export class TaskAnalyzer {
  constructor(storage) {
    this.storage = storage;

    // Reasoning keywords that indicate complex cognitive tasks
    this.reasoningKeywords = new Set([
      'analyze', 'explain', 'why', 'how', 'reasoning', 'logic', 'understand',
      'evaluate', 'compare', 'decide', 'determine', 'strategy', 'approach',
      'consider', 'implications', 'tradeoffs', 'optimize', 'design', 'architect',
      'plan', 'solve', 'debug', 'troubleshoot', 'diagnose', 'investigate'
    ]);

    // Error/debugging indicators
    this.errorKeywords = new Set([
      'error', 'exception', 'failed', 'failure', 'bug', 'issue', 'problem',
      'warning', 'crash', 'broken', 'fix', 'debug', 'troubleshoot', 'stacktrace',
      'traceback', 'unexpected', 'incorrect', 'wrong'
    ]);

    // Code-related indicators
    this.codeKeywords = new Set([
      'function', 'class', 'method', 'variable', 'import', 'export', 'const',
      'let', 'var', 'def', 'async', 'await', 'return', 'if', 'else', 'for',
      'while', 'try', 'catch', 'throw', 'interface', 'type', 'struct'
    ]);

    // Data/analysis indicators
    this.dataKeywords = new Set([
      'data', 'dataset', 'analysis', 'metrics', 'statistics', 'performance',
      'benchmark', 'measure', 'calculate', 'compute', 'aggregate', 'sum',
      'average', 'count', 'query', 'filter', 'transform'
    ]);

    // Simple query patterns (low complexity)
    this.simplePatterns = [
      /^what is/i,
      /^define/i,
      /^explain (briefly|simply)/i,
      /^list/i,
      /^show me/i,
      /^how do i/i,
      /^can you/i,
      /^tell me about/i
    ];

    // Generic question patterns (low complexity)
    this.genericPatterns = [
      /^(hi|hello|hey)/i,
      /^(thanks|thank you)/i,
      /^(yes|no|ok|okay)/i,
      /^help$/i
    ];
  }

  /**
   * Analyze a task to determine its complexity and type
   * @param {object} requestData - The request data to analyze
   * @returns {Promise<object>} Analysis results
   */
  async analyzeTask(requestData) {
    try {
      const prompt = requestData.prompt || requestData.message || '';
      const context = requestData.context || '';
      const combinedText = `${prompt}\n${context}`;

      // Calculate complexity score
      const complexity = this.calculateComplexity(requestData);

      // Classify task type
      const taskType = this.classifyTaskType(requestData);

      // Extract keywords for pattern learning
      const keywords = this.extractKeywords(combinedText);

      // Estimate token count
      const estimatedTokens = this.estimateTokens(combinedText);

      // Determine if this is a multi-turn conversation
      const isMultiTurn = requestData.conversation_history?.length > 0 || false;

      // Create analysis result
      const analysis = {
        analysis_id: randomUUID(),
        timestamp: new Date().toISOString(),
        complexity_score: complexity,
        task_type: taskType,
        estimated_tokens: estimatedTokens,
        has_code: this.hasCodeBlocks(combinedText),
        has_errors: this.hasErrorMessages(combinedText),
        has_reasoning: this.hasReasoningKeywords(combinedText),
        is_multi_turn: isMultiTurn,
        keywords: keywords.slice(0, 10), // Top 10 keywords
        prompt_length: prompt.length,
        context_length: context.length
      };

      return analysis;
    } catch (error) {
      console.error('[TaskAnalyzer] Error analyzing task:', error);
      // Return default analysis on error
      return {
        analysis_id: randomUUID(),
        timestamp: new Date().toISOString(),
        complexity_score: 0.5,
        task_type: 'query',
        estimated_tokens: 100,
        has_code: false,
        has_errors: false,
        has_reasoning: false,
        is_multi_turn: false,
        keywords: [],
        prompt_length: 0,
        context_length: 0
      };
    }
  }

  /**
   * Calculate complexity score (0.0 to 1.0)
   * @param {object} requestData - Request data
   * @returns {number} Complexity score
   */
  calculateComplexity(requestData) {
    const prompt = requestData.prompt || requestData.message || '';
    const context = requestData.context || '';
    const combinedText = `${prompt}\n${context}`;

    let score = 0.5; // Base complexity

    // Code blocks increase complexity significantly
    if (this.hasCodeBlocks(combinedText)) {
      score += 0.3;
    }

    // Error messages suggest debugging tasks (complex)
    if (this.hasErrorMessages(combinedText)) {
      score += 0.2;
    }

    // Reasoning keywords indicate analytical work
    if (this.hasReasoningKeywords(combinedText)) {
      score += 0.25;
    }

    // Large context suggests complex task
    if (combinedText.length > 5000) {
      score += 0.15;
    }

    // Data and numbers suggest analytical work
    if (this.hasDataPatterns(combinedText)) {
      score += 0.2;
    }

    // Simple queries are less complex
    if (prompt.length < 500 && this.isSimpleQuery(prompt)) {
      score -= 0.3;
    }

    // Generic greetings/responses are very simple
    if (this.isGenericQuestion(prompt)) {
      score -= 0.2;
    }

    // Multi-file or multi-step tasks are more complex
    if (requestData.files && requestData.files.length > 3) {
      score += 0.15;
    }

    // Explicit task complexity hints
    if (prompt.toLowerCase().includes('complex') || prompt.toLowerCase().includes('detailed')) {
      score += 0.1;
    }

    // Ensure score is between 0.0 and 1.0
    return Math.max(0.0, Math.min(1.0, score));
  }

  /**
   * Classify the task type
   * @param {object} requestData - Request data
   * @returns {string} Task type: 'code', 'debugging', 'reasoning', 'query', 'writing'
   */
  classifyTaskType(requestData) {
    const prompt = requestData.prompt || requestData.message || '';
    const context = requestData.context || '';
    const combinedText = `${prompt}\n${context}`.toLowerCase();

    // Debugging takes priority
    if (this.hasErrorMessages(combinedText)) {
      return 'debugging';
    }

    // Code-related tasks
    if (this.hasCodeBlocks(combinedText) || this.hasCodeKeywords(combinedText)) {
      return 'code';
    }

    // Reasoning/analytical tasks
    if (this.hasReasoningKeywords(combinedText)) {
      return 'reasoning';
    }

    // Writing tasks (documentation, content creation)
    if (combinedText.match(/\b(write|create|draft|compose|document|readme|blog|article)\b/)) {
      return 'writing';
    }

    // Default to query for simple questions
    return 'query';
  }

  /**
   * Check if text contains code blocks
   * @param {string} text - Text to check
   * @returns {boolean} True if contains code blocks
   */
  hasCodeBlocks(text) {
    // Check for markdown code blocks
    if (text.includes('```')) {
      return true;
    }

    // Check for inline code patterns
    if (text.match(/`[^`]+`/g)?.length > 3) {
      return true;
    }

    // Check for code-like structures
    if (text.match(/^\s*(function|class|const|let|var|def|import|from|export)\s+/m)) {
      return true;
    }

    // Check for common code patterns
    if (text.match(/[{}\[\]();]/) && text.match(/\b(if|for|while|return)\b/)) {
      return true;
    }

    return false;
  }

  /**
   * Check if text contains error messages
   * @param {string} text - Text to check
   * @returns {boolean} True if contains errors
   */
  hasErrorMessages(text) {
    const lowerText = text.toLowerCase();

    for (const keyword of this.errorKeywords) {
      if (lowerText.includes(keyword)) {
        return true;
      }
    }

    // Check for stack trace patterns
    if (text.match(/at .+\(.+:\d+:\d+\)/)) {
      return true;
    }

    // Check for error code patterns
    if (text.match(/\b(E[A-Z]+|[A-Z]+Error)\b/)) {
      return true;
    }

    return false;
  }

  /**
   * Check if text contains reasoning keywords
   * @param {string} text - Text to check
   * @returns {boolean} True if contains reasoning keywords
   */
  hasReasoningKeywords(text) {
    const lowerText = text.toLowerCase();
    const words = lowerText.split(/\s+/);

    let count = 0;
    for (const word of words) {
      if (this.reasoningKeywords.has(word)) {
        count++;
      }
    }

    // Need at least 2 reasoning keywords for significant reasoning
    return count >= 2;
  }

  /**
   * Check if text has code-related keywords
   * @param {string} text - Text to check
   * @returns {boolean} True if has code keywords
   */
  hasCodeKeywords(text) {
    const lowerText = text.toLowerCase();
    const words = lowerText.split(/\s+/);

    let count = 0;
    for (const word of words) {
      if (this.codeKeywords.has(word)) {
        count++;
      }
    }

    return count >= 3;
  }

  /**
   * Check if text has data/analytics patterns
   * @param {string} text - Text to check
   * @returns {boolean} True if has data patterns
   */
  hasDataPatterns(text) {
    const lowerText = text.toLowerCase();

    // Check for data keywords
    for (const keyword of this.dataKeywords) {
      if (lowerText.includes(keyword)) {
        return true;
      }
    }

    // Check for numbers and units (measurements, metrics)
    if (text.match(/\b\d+(?:\.\d+)?(?:%|ms|MB|GB|KB|TB|s|m|h|days?|weeks?|months?|years?)\b/gi)) {
      return true;
    }

    // Check for data structures (JSON, arrays)
    if (text.match(/\{[^}]+\}/) || text.match(/\[[^\]]+\]/)) {
      return true;
    }

    return false;
  }

  /**
   * Check if query is simple
   * @param {string} text - Text to check
   * @returns {boolean} True if simple query
   */
  isSimpleQuery(text) {
    for (const pattern of this.simplePatterns) {
      if (pattern.test(text)) {
        return true;
      }
    }
    return false;
  }

  /**
   * Check if question is generic
   * @param {string} text - Text to check
   * @returns {boolean} True if generic
   */
  isGenericQuestion(text) {
    for (const pattern of this.genericPatterns) {
      if (pattern.test(text.trim())) {
        return true;
      }
    }
    return false;
  }

  /**
   * Estimate token count (approximation: text.length / 4)
   * @param {string} text - Text to estimate
   * @returns {number} Estimated token count
   */
  estimateTokens(text) {
    if (!text || text.length === 0) {
      return 0;
    }

    // Rough approximation: 1 token ≈ 4 characters
    // This matches the approach used in Context Optimizer
    return Math.ceil(text.length / 4);
  }

  /**
   * Extract keywords from text for pattern learning
   * @param {string} text - Text to extract keywords from
   * @returns {Array<string>} Array of keywords
   */
  extractKeywords(text) {
    if (!text || text.length === 0) {
      return [];
    }

    // Tokenize and filter
    const words = text
      .toLowerCase()
      .replace(/[^\w\s]/g, ' ')
      .split(/\s+/)
      .filter(word => word.length > 3 && !this.isStopWord(word));

    // Count frequency
    const frequency = new Map();
    for (const word of words) {
      frequency.set(word, (frequency.get(word) || 0) + 1);
    }

    // Sort by frequency and return top keywords
    return Array.from(frequency.entries())
      .sort((a, b) => b[1] - a[1])
      .map(([word]) => word);
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
      'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their',
      'what', 'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go',
      'me', 'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know',
      'take', 'people', 'into', 'year', 'your', 'good', 'some', 'could', 'them',
      'see', 'other', 'than', 'then', 'now', 'look', 'only', 'come', 'its', 'over',
      'think', 'also', 'back', 'after', 'use', 'two', 'how', 'our', 'work', 'first',
      'well', 'way', 'even', 'new', 'want', 'because', 'any', 'these', 'give', 'day',
      'most', 'us'
    ]);
    return stopWords.has(word);
  }

  /**
   * Get historical task patterns for an agent
   * Uses routing_decisions table to find similar past tasks
   * @param {string} agentWallet - Agent wallet address
   * @param {object} currentAnalysis - Current task analysis to match against
   * @param {number} limit - Number of recent analyses to retrieve
   * @returns {Promise<Array>} Historical task analyses
   */
  async getHistoricalPatterns(agentWallet, currentAnalysis, limit = 50) {
    try {
      const stmt = this.storage.db.prepare(`
        SELECT * FROM routing_decisions
        WHERE agent_wallet = ?
          AND task_type = ?
          AND timestamp >= datetime('now', '-30 days')
        ORDER BY timestamp DESC
        LIMIT ?
      `);

      const decisions = stmt.all(agentWallet, currentAnalysis.task_type, limit);

      return decisions.map(d => ({
        complexity_score: d.task_complexity,
        task_type: d.task_type,
        has_code: Boolean(d.has_code),
        has_errors: Boolean(d.has_errors),
        estimated_tokens: d.context_length,
        selected_model: d.selected_model,
        was_successful: Boolean(d.was_successful)
      }));
    } catch (error) {
      console.error('[TaskAnalyzer] Error getting historical patterns:', error);
      return [];
    }
  }
}
