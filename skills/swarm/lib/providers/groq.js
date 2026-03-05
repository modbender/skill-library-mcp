/**
 * Groq Provider
 * FREE tier available! Very fast inference.
 * Llama 3.1 70B, Mixtral, etc.
 */

const { BaseLLMProvider } = require('./base');

class GroqProvider extends BaseLLMProvider {
  constructor(config = {}) {
    super(config);
    this.name = 'groq';
    this.model = config.model || 'llama-3.1-70b-versatile';
    this.endpoint = 'https://api.groq.com/openai/v1/chat/completions';
    
    // Groq pricing (very cheap, has free tier)
    this.pricing = {
      'llama-3.1-70b-versatile': { input: 0.59, output: 0.79 },
      'llama-3.1-8b-instant': { input: 0.05, output: 0.08 },
      'mixtral-8x7b-32768': { input: 0.24, output: 0.24 },
      'gemma2-9b-it': { input: 0.20, output: 0.20 },
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
      throw new Error(`Groq API error: ${response.status} - ${error}`);
    }

    const data = await response.json();
    
    // Track usage
    const usage = data.usage || {};
    this.trackTokens(usage.prompt_tokens || 0, usage.completion_tokens || 0);
    
    return data.choices[0].message.content;
  }

  getEstimatedCost() {
    const modelPricing = this.pricing[this.model] || this.pricing['llama-3.1-70b-versatile'];
    const inputCost = (this.tokenCount.input / 1_000_000) * modelPricing.input;
    const outputCost = (this.tokenCount.output / 1_000_000) * modelPricing.output;
    return {
      inputTokens: this.tokenCount.input,
      outputTokens: this.tokenCount.output,
      inputCost: inputCost.toFixed(6),
      outputCost: outputCost.toFixed(6),
      totalCost: (inputCost + outputCost).toFixed(6),
      currency: 'USD',
      note: 'Groq has a free tier with rate limits',
    };
  }
}

module.exports = { GroqProvider };
