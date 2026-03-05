#!/usr/bin/env node
/**
 * Chinese LLM Router - Core Router
 * Routes chat completions to configured Chinese LLM providers
 * All providers use OpenAI-compatible API format
 */

const fs = require('fs');
const path = require('path');
const https = require('https');
const http = require('http');

const CONFIG_FILE = path.join(
  process.env.HOME || process.env.USERPROFILE,
  '.chinese-llm-router', 'config.json'
);

// Model → Provider mapping (auto-built from config)
const MODEL_ALIASES = {
  // DeepSeek
  'deepseek': 'deepseek-chat',
  'deepseek-v3': 'deepseek-chat',
  'deepseek-v3.2': 'deepseek-chat',
  'deepseek-r1': 'deepseek-reasoner',
  // Qwen
  'qwen': 'qwen3-max',
  'qwen3': 'qwen3-max',
  'qwen-thinking': 'qwen3-max-thinking',
  'qwen-coder': 'qwen3-coder-plus',
  'qwen-turbo': 'qwen-turbo-latest',
  // GLM
  'glm': 'glm-5',
  'zhipu': 'glm-5',
  'chatglm': 'glm-5',
  // Kimi
  'kimi': 'kimi-k2.5',
  'moonshot': 'kimi-k2.5',
  'kimi-thinking': 'kimi-k2.5-thinking',
  // Doubao
  'doubao': 'doubao-seed-2.0-pro',
  'doubao-pro': 'doubao-seed-2.0-pro',
  'doubao-lite': 'doubao-seed-2.0-lite',
  'doubao-mini': 'doubao-seed-2.0-mini',
  '豆包': 'doubao-seed-2.0-pro',
  // MiniMax
  'minimax': 'minimax-m2.5',
  // Step
  'step': 'step-3.5-flash',
  '阶跃': 'step-3.5-flash',
  // Baichuan
  'baichuan': 'baichuan4-turbo',
  '百川': 'baichuan4-turbo',
  // Spark
  'spark': 'spark-v4.0-ultra',
  '星火': 'spark-v4.0-ultra',
  // Hunyuan
  'hunyuan': 'hunyuan-turbo-s',
  '混元': 'hunyuan-turbo-s'
};

// Task → Model recommendations
const TASK_RECOMMENDATIONS = {
  'coding': ['glm-5', 'kimi-k2.5', 'qwen3-coder-plus', 'deepseek-chat'],
  'math': ['deepseek-reasoner', 'qwen3-max-thinking', 'kimi-k2.5-thinking'],
  'reasoning': ['deepseek-reasoner', 'qwen3-max-thinking', 'kimi-k2.5-thinking'],
  'writing': ['qwen3-max', 'doubao-seed-2.0-pro', 'kimi-k2.5'],
  'translation': ['qwen3-max', 'baichuan4-turbo', 'deepseek-chat'],
  'chat': ['qwen3-max', 'doubao-seed-2.0-pro', 'deepseek-chat'],
  'fast': ['step-3.5-flash', 'doubao-seed-2.0-mini', 'qwen-turbo-latest'],
  'cheap': ['deepseek-chat', 'doubao-seed-2.0-mini', 'step-3.5-flash'],
  'long': ['kimi-k2.5', 'deepseek-chat', 'qwen3-max'],
  'agent': ['glm-5', 'qwen3-max', 'doubao-seed-2.0-pro'],
  'vision': ['kimi-k2.5', 'qwen3-max', 'glm-5']
};

function loadConfig() {
  if (!fs.existsSync(CONFIG_FILE)) {
    throw new Error(`Config not found. Run: node scripts/setup.js`);
  }
  return JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf8'));
}

function resolveModel(name) {
  const lower = name.toLowerCase().trim();
  return MODEL_ALIASES[lower] || lower;
}

function findProvider(config, modelId) {
  for (const [providerId, provider] of Object.entries(config.providers)) {
    if (provider.models.includes(modelId)) {
      return { providerId, ...provider };
    }
  }
  return null;
}

function chatCompletion(provider, model, messages, options = {}) {
  return new Promise((resolve, reject) => {
    const url = new URL(provider.baseUrl + '/chat/completions');
    const isHttps = url.protocol === 'https:';
    const client = isHttps ? https : http;

    const body = JSON.stringify({
      model,
      messages,
      temperature: options.temperature ?? 0.7,
      max_tokens: options.max_tokens ?? 4096,
      stream: options.stream ?? false,
      ...options.extra
    });

    const req = client.request({
      hostname: url.hostname,
      port: url.port || (isHttps ? 443 : 80),
      path: url.pathname + '/chat/completions',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${provider.apiKey}`,
        'Content-Length': Buffer.byteLength(body)
      }
    }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        if (res.statusCode >= 400) {
          reject(new Error(`${res.statusCode}: ${data}`));
        } else {
          try { resolve(JSON.parse(data)); }
          catch (e) { reject(new Error(`Parse error: ${data.slice(0, 200)}`)); }
        }
      });
    });

    req.on('error', reject);
    req.write(body);
    req.end();
  });
}

async function route(modelName, messages, options = {}) {
  const config = loadConfig();
  const modelId = resolveModel(modelName);
  const provider = findProvider(config, modelId);

  if (!provider) {
    // Try fallback
    for (const fb of (config.fallback || [])) {
      const fbProvider = findProvider(config, fb);
      if (fbProvider) {
        console.warn(`⚠️ Model "${modelName}" not configured, falling back to ${fb}`);
        return chatCompletion(fbProvider, fb, messages, options);
      }
    }
    throw new Error(`Model "${modelName}" not found. Run: node scripts/setup.js`);
  }

  return chatCompletion(provider, modelId, messages, options);
}

function listModels() {
  const config = loadConfig();
  const result = [];
  for (const [id, provider] of Object.entries(config.providers)) {
    for (const model of provider.models) {
      result.push({ provider: id, model, baseUrl: provider.baseUrl });
    }
  }
  return result;
}

function recommend(task) {
  const config = loadConfig();
  const recs = TASK_RECOMMENDATIONS[task.toLowerCase()] || TASK_RECOMMENDATIONS['chat'];
  return recs.filter(m => findProvider(config, m)).map(m => ({
    model: m,
    provider: findProvider(config, m)?.providerId
  }));
}

// CLI mode
if (require.main === module) {
  const args = process.argv.slice(2);
  const cmd = args[0];

  if (cmd === 'list') {
    const models = listModels();
    console.log('\n🇨🇳 Available Chinese LLMs:\n');
    for (const m of models) {
      console.log(`  ${m.model} (${m.provider})`);
    }
    console.log(`\nTotal: ${models.length} models from ${new Set(models.map(m => m.provider)).size} providers`);
  } else if (cmd === 'recommend') {
    const task = args[1] || 'chat';
    const recs = recommend(task);
    console.log(`\n🎯 Recommended for "${task}":\n`);
    recs.forEach((r, i) => console.log(`  ${i + 1}. ${r.model} (${r.provider})`));
  } else if (cmd === 'test') {
    const model = args[1] || 'qwen3-max';
    console.log(`\n🧪 Testing ${model}...`);
    route(model, [{ role: 'user', content: '你好，请用一句话介绍你自己。' }])
      .then(r => {
        console.log(`✅ ${model}: ${r.choices[0].message.content}`);
        if (r.usage) console.log(`   Tokens: ${r.usage.prompt_tokens} in / ${r.usage.completion_tokens} out`);
      })
      .catch(e => console.error(`❌ ${model}: ${e.message}`));
  } else {
    console.log('Usage: node router.js <command>');
    console.log('  list              - List all configured models');
    console.log('  recommend <task>  - Get model recommendation (coding/math/writing/fast/cheap/...)');
    console.log('  test <model>      - Test a model with a simple prompt');
  }
}

module.exports = { route, listModels, recommend, resolveModel, MODEL_ALIASES, TASK_RECOMMENDATIONS };
