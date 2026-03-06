/**
 * Anthropic Provider
 * Claude Haiku: ~$0.25/1M input tokens (fast & cheap)
 */

const { BaseLLMProvider } = require('./base');

class AnthropicProvider extends BaseLLMProvider {
  constructor(config = {}) {
    super(config);
    this.name = 'anthropic';
    this.model = config.model || 'claude-3-5-haiku-latest';
    this.endpoint = 'https://api.anthropic.com/v1/messages';
    
    // Pricing per 1M tokens
    this.pricing = {
      'claude-3-5-haiku-latest': { input: 0.80, output: 4.00 },
      'claude-3-haiku-20240307': { input: 0.25, output: 1.25 },
      'claude-3-5-sonnet-latest': { input: 3.00, output: 15.00 },
    };
  }

  async complete(prompt, options = {}) {
    const response = await fetch(this.endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': this.apiKey,
        'anthropic-version': '2023-06-01',
      },
      body: JSON.stringify({
        model: this.model,
        max_tokens: options.maxTokens || this.maxTokens,
        messages: [{ role: 'user', content: prompt }],
      }),
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Anthropic API error: ${response.status} - ${error}`);
    }

    const data = await response.json();
    
    // Track usage
    const usage = data.usage || {};
    this.trackTokens(usage.input_tokens || 0, usage.output_tokens || 0);
    
    return data.content[0].text;
  }

  getEstimatedCost() {
    const modelPricing = this.pricing[this.model] || this.pricing['claude-3-5-haiku-latest'];
    const inputCost = (this.tokenCount.input / 1_000_000) * modelPricing.input;
    const outputCost = (this.tokenCount.output / 1_000_000) * modelPricing.output;
    return {
      inputTokens: this.tokenCount.input,
      outputTokens: this.tokenCount.output,
      inputCost: inputCost.toFixed(6),
      outputCost: outputCost.toFixed(6),
      totalCost: (inputCost + outputCost).toFixed(6),
      currency: 'USD',
    };
  }
}

module.exports = { AnthropicProvider };
