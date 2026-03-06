/**
 * Base LLM Provider Class
 * All providers extend this for consistent interface
 */

class BaseLLMProvider {
  constructor(config = {}) {
    this.name = 'base';
    this.model = config.model;
    this.apiKey = config.apiKey;
    this.maxTokens = config.maxTokens || 4096;
    this.temperature = config.temperature || 0.7;
    this.requestCount = 0;
    this.tokenCount = { input: 0, output: 0 };
  }

  /**
   * Complete a prompt - must be implemented by subclasses
   * @param {string} prompt - The prompt to complete
   * @param {object} options - Additional options
   * @returns {Promise<string>} The completion text
   */
  async complete(prompt, options = {}) {
    throw new Error('complete() must be implemented by subclass');
  }

  /**
   * Validate the API key works
   * @returns {Promise<boolean>}
   */
  async validateKey() {
    try {
      await this.complete('Say "ok" and nothing else.', { maxTokens: 10 });
      return true;
    } catch (error) {
      return false;
    }
  }

  /**
   * Get estimated cost for tokens used
   * @returns {object} { inputCost, outputCost, totalCost }
   */
  getEstimatedCost() {
    // Override in subclass with actual pricing
    return {
      inputTokens: this.tokenCount.input,
      outputTokens: this.tokenCount.output,
      inputCost: 0,
      outputCost: 0,
      totalCost: 0,
    };
  }

  /**
   * Track token usage
   */
  trackTokens(input, output) {
    this.tokenCount.input += input;
    this.tokenCount.output += output;
    this.requestCount++;
  }

  /**
   * Get provider info
   */
  getInfo() {
    return {
      name: this.name,
      model: this.model,
      requests: this.requestCount,
      tokens: this.tokenCount,
      cost: this.getEstimatedCost(),
    };
  }
}

module.exports = { BaseLLMProvider };
