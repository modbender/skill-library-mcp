/**
 * Node Scaling Configuration
 * 
 * This file contains DEFAULT settings.
 * User-specific settings (including API keys) go in:
 *   ~/.config/clawdbot/node-scaling.yaml
 * 
 * Run `node bin/setup.js` to configure.
 */

const fs = require('fs');
const path = require('path');

// Try to load user config
function loadUserConfig() {
  const configPaths = [
    path.join(process.env.HOME, '.config/clawdbot/node-scaling.yaml'),
    path.join(process.env.HOME, '.config/clawdbot/node-scaling.json'),
    path.join(__dirname, 'node-scaling.local.yaml'),
  ];
  
  for (const configPath of configPaths) {
    if (fs.existsSync(configPath)) {
      try {
        const content = fs.readFileSync(configPath, 'utf8');
        if (configPath.endsWith('.yaml') || configPath.endsWith('.yml')) {
          const yaml = require('js-yaml');
          return yaml.load(content);
        }
        return JSON.parse(content);
      } catch (e) {
        console.warn(`Failed to load config from ${configPath}:`, e.message);
      }
    }
  }
  return null;
}

// Get API key from environment or config
function getApiKey(provider = 'gemini') {
  const envVars = {
    gemini: 'GEMINI_API_KEY',
    openai: 'OPENAI_API_KEY',
    anthropic: 'ANTHROPIC_API_KEY',
    groq: 'GROQ_API_KEY',
  };
  
  // Check environment variable
  const envVar = envVars[provider];
  if (envVar && process.env[envVar]) {
    return process.env[envVar];
  }
  
  // Check key file
  const keyFile = path.join(process.env.HOME, '.config/clawdbot', `${provider}-key.txt`);
  if (fs.existsSync(keyFile)) {
    return fs.readFileSync(keyFile, 'utf8').trim();
  }
  
  return null;
}

// Load user config or use defaults
const userConfig = loadUserConfig();

// Security policy for all workers
const { securePrompt } = require('./lib/security');

module.exports = {
  // Provider settings (from user config or defaults)
  provider: {
    name: userConfig?.node_scaling?.provider?.name || 'gemini',
    model: userConfig?.node_scaling?.provider?.model || 'gemini-2.0-flash',
    get apiKey() {
      return getApiKey(this.name);
    },
  },

  // Scaling limits
  scaling: {
    maxNodes: userConfig?.node_scaling?.limits?.max_nodes || 10,
    maxConcurrentApi: userConfig?.node_scaling?.limits?.max_concurrent_api || 5,
    timeoutMs: 60000,
    retries: 1,
  },

  // Cost controls
  cost: {
    maxDailySpend: userConfig?.node_scaling?.cost?.max_daily_spend || 5.00,
    warnAt: userConfig?.node_scaling?.cost?.warn_at || 1.00,
  },

  // Smart routing — auto-select model tier based on complexity
  routing: {
    enabled: userConfig?.node_scaling?.routing?.enabled ?? true,
    threshold: userConfig?.node_scaling?.routing?.threshold ?? 8,
    proModel: userConfig?.node_scaling?.routing?.pro_model || 'gemini-2.5-flash',
  },

  // Web Search (Google Search grounding via Gemini API)
  webSearch: {
    enabled: userConfig?.node_scaling?.web_search?.enabled ?? false,
    parallelDefault: userConfig?.node_scaling?.web_search?.parallel_default ?? false,
  },

  // Node specializations and their tools
  // All system prompts are wrapped with security policy
  nodeTypes: {
    search: {
      description: 'Web search specialist - finds relevant sources',
      tools: ['web_search'],
      systemPrompt: securePrompt('You are a search specialist. Find the most relevant and authoritative sources for the query. Return structured search results.'),
    },
    fetch: {
      description: 'Content fetcher - extracts readable content from URLs',
      tools: ['web_fetch'],
      systemPrompt: securePrompt('You are a content extraction specialist. Extract and clean the main content from web pages.'),
    },
    analyze: {
      description: 'Content analyzer - summarizes and extracts insights',
      tools: ['analyze'],
      systemPrompt: securePrompt('You are an analysis specialist. Summarize content, identify key points, and extract actionable insights. Be concise but thorough.'),
    },
    extract: {
      description: 'Data extractor - pulls structured data from text',
      tools: ['extract'],
      systemPrompt: securePrompt('You are a data extraction specialist. Extract structured data, facts, figures, and entities from text.'),
    },
    synthesize: {
      description: 'Synthesizer - combines multiple sources into coherent output',
      tools: ['synthesize'],
      systemPrompt: securePrompt('You are a synthesis specialist. Combine multiple pieces of information into a coherent, well-organized report.'),
    },
  },
  
  // Helper to check if configured
  isConfigured() {
    return !!this.provider.apiKey;
  },
};
