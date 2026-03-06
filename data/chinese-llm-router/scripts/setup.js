#!/usr/bin/env node
/**
 * Chinese LLM Router - Interactive Setup
 * Guides user through configuring API keys for Chinese LLM providers
 */

const fs = require('fs');
const path = require('path');
const readline = require('readline');

const CONFIG_DIR = path.join(process.env.HOME || process.env.USERPROFILE, '.chinese-llm-router');
const CONFIG_FILE = path.join(CONFIG_DIR, 'config.json');

const PROVIDERS = [
  {
    id: 'deepseek',
    name: 'DeepSeek',
    baseUrl: 'https://api.deepseek.com/v1',
    models: ['deepseek-chat', 'deepseek-reasoner'],
    signup: 'https://platform.deepseek.com',
    desc: 'Best open-source, cheapest flagship model'
  },
  {
    id: 'qwen',
    name: 'Qwen (Alibaba/通义千问)',
    baseUrl: 'https://dashscope.aliyuncs.com/compatible-mode/v1',
    models: ['qwen3-max', 'qwen3-max-thinking', 'qwen3-coder-plus', 'qwen-turbo-latest'],
    signup: 'https://dashscope.console.aliyun.com',
    desc: 'Strong all-rounder, free tier available'
  },
  {
    id: 'glm',
    name: 'GLM (智谱AI)',
    baseUrl: 'https://open.bigmodel.cn/api/paas/v4',
    models: ['glm-5', 'glm-4-plus'],
    signup: 'https://open.bigmodel.cn',
    desc: 'Top coding & agent, just launched GLM-5'
  },
  {
    id: 'kimi',
    name: 'Kimi (月之暗面/Moonshot)',
    baseUrl: 'https://api.moonshot.cn/v1',
    models: ['kimi-k2.5', 'kimi-k2.5-thinking', 'moonshot-v1-128k'],
    signup: 'https://platform.moonshot.cn',
    desc: 'Great long context & vision, open source'
  },
  {
    id: 'doubao',
    name: 'Doubao Seed 2.0 (字节豆包)',
    baseUrl: 'https://ark.cn-beijing.volces.com/api/v3',
    models: ['doubao-seed-2.0-pro', 'doubao-seed-2.0-lite', 'doubao-seed-2.0-mini'],
    signup: 'https://console.volcengine.com/ark',
    desc: 'ByteDance, fast & cheap, just launched 2.0'
  },
  {
    id: 'minimax',
    name: 'MiniMax',
    baseUrl: 'https://api.minimax.chat/v1',
    models: ['minimax-m2.5'],
    signup: 'https://platform.minimaxi.com',
    desc: 'Lightweight powerhouse, can run locally'
  },
  {
    id: 'step',
    name: 'Step (阶跃星辰)',
    baseUrl: 'https://api.stepfun.com/v1',
    models: ['step-3.5-flash', 'step-2-16k'],
    signup: 'https://platform.stepfun.com',
    desc: 'Blazing fast inference, trending on OpenRouter'
  },
  {
    id: 'baichuan',
    name: 'Baichuan (百川)',
    baseUrl: 'https://api.baichuan-ai.com/v1',
    models: ['baichuan4-turbo'],
    signup: 'https://platform.baichuan-ai.com',
    desc: 'Strong Chinese language understanding'
  },
  {
    id: 'spark',
    name: 'Spark (讯飞星火)',
    baseUrl: 'https://spark-api-open.xf-yun.com/v1',
    models: ['spark-v4.0-ultra'],
    signup: 'https://console.xfyun.cn',
    desc: 'Speech & Chinese NLP specialist'
  },
  {
    id: 'hunyuan',
    name: 'Hunyuan (腾讯混元)',
    baseUrl: 'https://api.hunyuan.cloud.tencent.com/v1',
    models: ['hunyuan-turbo-s'],
    signup: 'https://cloud.tencent.com/product/hunyuan',
    desc: 'Tencent, WeChat ecosystem'
  }
];

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

function ask(question) {
  return new Promise(resolve => rl.question(question, resolve));
}

async function main() {
  console.log('\n🇨🇳 Chinese LLM Router - Setup\n');
  console.log('Configure API keys for Chinese AI models.');
  console.log('Skip any provider by pressing Enter.\n');

  // Load existing config
  let config = { providers: {}, default: 'qwen3-max', fallback: ['deepseek-chat'] };
  if (fs.existsSync(CONFIG_FILE)) {
    try {
      config = JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf8'));
      console.log('Found existing config. Will update.\n');
    } catch (e) { /* ignore */ }
  }

  for (const provider of PROVIDERS) {
    const existing = config.providers[provider.id]?.apiKey;
    const hint = existing ? ` [current: ${existing.slice(0, 8)}...]` : '';
    console.log(`\n--- ${provider.name} ---`);
    console.log(`  ${provider.desc}`);
    console.log(`  Models: ${provider.models.join(', ')}`);
    console.log(`  Sign up: ${provider.signup}`);

    const key = await ask(`  API Key${hint}: `);
    if (key.trim()) {
      config.providers[provider.id] = {
        apiKey: key.trim(),
        baseUrl: provider.baseUrl,
        models: provider.models
      };
    } else if (existing) {
      console.log('  (keeping existing key)');
    } else {
      console.log('  (skipped)');
    }
  }

  // Choose default
  const configured = Object.keys(config.providers);
  if (configured.length > 0) {
    console.log(`\nConfigured providers: ${configured.join(', ')}`);
    const allModels = configured.flatMap(p => config.providers[p].models);
    console.log(`Available models: ${allModels.join(', ')}`);
    const def = await ask(`\nDefault model [${config.default}]: `);
    if (def.trim()) config.default = def.trim();

    const fb = await ask(`Fallback model(s), comma-separated [${config.fallback.join(',')}]: `);
    if (fb.trim()) config.fallback = fb.trim().split(',').map(s => s.trim());
  }

  // Save
  if (!fs.existsSync(CONFIG_DIR)) fs.mkdirSync(CONFIG_DIR, { recursive: true });
  fs.writeFileSync(CONFIG_FILE, JSON.stringify(config, null, 2));
  console.log(`\n✅ Config saved to ${CONFIG_FILE}`);
  console.log(`\nConfigured ${configured.length} provider(s). Your OpenClaw can now use Chinese LLMs!`);

  rl.close();
}

main().catch(err => {
  console.error('Setup failed:', err);
  rl.close();
  process.exit(1);
});
