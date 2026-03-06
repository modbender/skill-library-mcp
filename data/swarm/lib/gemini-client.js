/**
 * Gemini Client for Worker Nodes
 * Now uses the provider system from config
 */

const config = require('../config');
const { createProvider } = require('./providers');

class GeminiClient {
  constructor(options = {}) {
    // Use provider system
    const providerName = options.provider || config.provider.name || 'gemini';
    const apiKey = options.apiKey || config.provider.apiKey;
    const model = options.model || config.provider.model;
    
    if (!apiKey) {
      throw new Error(
        `No API key found for ${providerName}. ` +
        `Run 'node bin/setup.js' or set the appropriate environment variable.`
      );
    }
    
    this.provider = createProvider({
      provider: providerName,
      apiKey,
      model,
      maxTokens: options.maxTokens || 4096,
      temperature: options.temperature || 0.7,
    });
  }

  async complete(prompt, options = {}) {
    return this.provider.complete(prompt, options);
  }

  // Batch multiple prompts in parallel
  async batch(prompts, options = {}) {
    const results = await Promise.allSettled(
      prompts.map(p => this.complete(p, options))
    );
    
    return results.map((r, i) => ({
      prompt: prompts[i],
      success: r.status === 'fulfilled',
      result: r.status === 'fulfilled' ? r.value : null,
      error: r.status === 'rejected' ? r.reason.message : null,
    }));
  }

  getStats() {
    return this.provider.getInfo();
  }
}

module.exports = { GeminiClient };
