/**
 * OpenAI Provider
 * GPT-4o-mini: ~$0.15/1M input tokens
 */

const { BaseLLMProvider } = require('./base');

class OpenAIProvider extends BaseLLMProvider {
  constructor(config = {}) {
    super(config);
    this.name = 'openai';
    this.model = config.model || 'gpt-4o-mini';
    this.endpoint = 'https://api.openai.com/v1/chat/completions';
    
    // Pricing per 1M tokens
    this.pricing = {
      'gpt-4o-mini': { input: 0.15, output: 0.60 },
      'gpt-4o': { input: 2.50, output: 10.00 },
      'gpt-3.5-turbo': { input: 0.50, output: 1.50 },
    };
  }

  async complete(prompt, options = {}) {
    const response = await fetch(this.endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.apiKey}`,
      },
      body: JSON.stringify({
        model: this.model,
        messages: [{ role: 'user', content: prompt }],
        max_tokens: options.maxTokens || this.maxTokens,
        temperature: options.temperature || this.temperature,
      }),
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`OpenAI API error: ${response.status} - ${error}`);
    }

    const data = await response.json();
    
    // Track usage
    const usage = data.usage || {};
    this.trackTokens(usage.prompt_tokens || 0, usage.completion_tokens || 0);
    
    return data.choices[0].message.content;
  }

  getEstimatedCost() {
    const modelPricing = this.pricing[this.model] || this.pricing['gpt-4o-mini'];
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

module.exports = { OpenAIProvider };
