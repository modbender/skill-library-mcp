/**
 * Google Gemini Provider
 * Cheapest option: ~$0.075/1M input tokens
 */

const { BaseLLMProvider } = require('./base');
const { globalLimiter } = require('../rate-limiter');

class GeminiProvider extends BaseLLMProvider {
  constructor(config = {}) {
    super(config);
    this.name = 'gemini';
    this.model = config.model || 'gemini-2.0-flash';
    this.endpoint = 'https://generativelanguage.googleapis.com/v1beta/models';
    
    // Pricing per 1M tokens (as of 2024)
    this.pricing = {
      input: 0.075,   // $0.075 per 1M input tokens
      output: 0.30,   // $0.30 per 1M output tokens
    };
  }

  async complete(prompt, options = {}) {
    // Rate limiting - wait for token
    await globalLimiter.acquire();
    
    const model = options.model || this.model;
    const url = `${this.endpoint}/${model}:generateContent?key=${this.apiKey}`;
    
    const body = {
      contents: [{
        parts: [{ text: prompt }]
      }],
      generationConfig: {
        maxOutputTokens: options.maxTokens || this.maxTokens,
        temperature: options.temperature || this.temperature,
      }
    };

    // Structured output — force JSON via response_mime_type
    if (options.responseSchema) {
      body.generationConfig.responseMimeType = 'application/json';
      body.generationConfig.responseSchema = options.responseSchema;
    } else if (options.jsonMode) {
      body.generationConfig.responseMimeType = 'application/json';
    }

    // Enable Google Search grounding when requested or for research-type tasks
    if (options.webSearch || options.grounding) {
      body.tools = [{ google_search: {} }];
    }

    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const error = await response.text();
      
      // Handle rate limiting
      if (response.status === 429) {
        const retryAfter = response.headers.get('retry-after');
        const backoffMs = retryAfter ? parseInt(retryAfter) * 1000 : 10000;
        globalLimiter.backoff(backoffMs);
        throw new Error(`Rate limited - backing off for ${backoffMs}ms`);
      }
      
      throw new Error(`Gemini API error: ${response.status} - ${error}`);
    }

    const data = await response.json();
    
    // Track usage
    const inputTokens = data.usageMetadata?.promptTokenCount || Math.ceil(prompt.length / 4);
    const outputTokens = data.usageMetadata?.candidatesTokenCount || 0;
    this.trackTokens(inputTokens, outputTokens);
    
    // Extract text
    try {
      return data.candidates[0].content.parts[0].text;
    } catch (e) {
      throw new Error('Failed to extract text from Gemini response');
    }
  }

  getEstimatedCost() {
    const inputCost = (this.tokenCount.input / 1_000_000) * this.pricing.input;
    const outputCost = (this.tokenCount.output / 1_000_000) * this.pricing.output;
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

module.exports = { GeminiProvider };
