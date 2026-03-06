/**
 * Provider Factory
 * Creates the appropriate LLM provider based on config
 */

const { GeminiProvider } = require('./gemini');
const { OpenAIProvider } = require('./openai');
const { AnthropicProvider } = require('./anthropic');
const { GroqProvider } = require('./groq');

const PROVIDERS = {
  gemini: GeminiProvider,
  openai: OpenAIProvider,
  anthropic: AnthropicProvider,
  groq: GroqProvider,
};

// Recommended models for node scaling (cheap & fast)
const RECOMMENDED_MODELS = {
  gemini: 'gemini-2.0-flash',
  openai: 'gpt-4o-mini',
  anthropic: 'claude-3-haiku-20240307',
  groq: 'llama-3.1-70b-versatile',
};

// Cost ranking (cheapest first)
const COST_RANKING = [
  { provider: 'groq', model: 'llama-3.1-8b-instant', cost: 0.05 },
  { provider: 'gemini', model: 'gemini-2.0-flash', cost: 0.075 },
  { provider: 'openai', model: 'gpt-4o-mini', cost: 0.15 },
  { provider: 'groq', model: 'mixtral-8x7b-32768', cost: 0.24 },
  { provider: 'anthropic', model: 'claude-3-haiku-20240307', cost: 0.25 },
];

/**
 * Create a provider instance
 * @param {object} config - Provider configuration
 * @param {string} config.provider - Provider name (gemini, openai, etc.)
 * @param {string} config.apiKey - API key
 * @param {string} config.model - Model name (optional, uses recommended)
 */
function createProvider(config) {
  const providerName = config.provider?.toLowerCase() || 'gemini';
  const ProviderClass = PROVIDERS[providerName];
  
  if (!ProviderClass) {
    throw new Error(`Unknown provider: ${providerName}. Supported: ${Object.keys(PROVIDERS).join(', ')}`);
  }
  
  if (!config.apiKey) {
    throw new Error(`API key required for ${providerName} provider`);
  }
  
  return new ProviderClass({
    apiKey: config.apiKey,
    model: config.model || RECOMMENDED_MODELS[providerName],
    maxTokens: config.maxTokens,
    temperature: config.temperature,
  });
}

/**
 * Get API key from environment or file
 */
function getApiKey(config) {
  // Try environment variable first
  if (config.apiKeyEnv && process.env[config.apiKeyEnv]) {
    return process.env[config.apiKeyEnv];
  }
  
  // Try file
  if (config.apiKeyFile) {
    const fs = require('fs');
    const path = require('path');
    const keyPath = config.apiKeyFile.replace('~', process.env.HOME);
    if (fs.existsSync(keyPath)) {
      return fs.readFileSync(keyPath, 'utf8').trim();
    }
  }
  
  // Direct key (not recommended, but supported)
  if (config.apiKey) {
    return config.apiKey;
  }
  
  return null;
}

/**
 * Load provider from node-scaling config file
 */
function loadProviderFromConfig(configPath = null) {
  const fs = require('fs');
  const path = require('path');
  const yaml = require('js-yaml');
  
  // Default config locations
  const configLocations = configPath ? [configPath] : [
    path.join(process.env.HOME, '.config/clawdbot/node-scaling.yaml'),
    path.join(process.env.HOME, '.config/clawdbot/node-scaling.json'),
    path.join(process.cwd(), 'node-scaling.yaml'),
    path.join(process.cwd(), 'node-scaling.json'),
  ];
  
  for (const loc of configLocations) {
    if (fs.existsSync(loc)) {
      const content = fs.readFileSync(loc, 'utf8');
      const config = loc.endsWith('.yaml') || loc.endsWith('.yml')
        ? yaml.load(content)
        : JSON.parse(content);
      
      const providerConfig = config.node_scaling?.provider || config.provider || {};
      const apiKey = getApiKey(providerConfig);
      
      if (apiKey) {
        return createProvider({
          provider: providerConfig.name || 'gemini',
          apiKey,
          model: providerConfig.model,
        });
      }
    }
  }
  
  throw new Error('No node-scaling configuration found. Run setup: npx node-scaling-setup');
}

module.exports = {
  createProvider,
  loadProviderFromConfig,
  getApiKey,
  PROVIDERS,
  RECOMMENDED_MODELS,
  COST_RANKING,
};
