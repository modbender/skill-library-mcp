#!/usr/bin/env node

/**
 * Venice AI API Integration
 * 
 * Provides commands for interacting with Venice's private AI inference API.
 * Pay with DIEM (staked on Base) for uncensored, private AI access.
 * 
 * Usage:
 *   node src/venice.js models              - List available models
 *   node src/venice.js balance             - Check DIEM balance & allocation
 *   node src/venice.js chat <prompt>       - Send a chat completion request
 *   node src/venice.js generate <prompt>   - Generate an image
 */

import { readFileSync, existsSync } from 'fs';
import { homedir } from 'os';
import { join } from 'path';

// Venice API Configuration
const VENICE_API_BASE = 'https://api.venice.ai/api/v1';
const DIEM_TOKEN_ADDRESS = '0xf4d97f2da56e8c3098f3a8d538db630a2606a024';
const DIEM_CHAIN = 'base';

// Load Venice API key from config file
function getVeniceApiKey() {
  const configPath = join(homedir(), '.venice-api.json');
  
  if (!existsSync(configPath)) {
    return null;
  }
  
  try {
    const config = JSON.parse(readFileSync(configPath, 'utf8'));
    return config.apiKey || null;
  } catch {
    return null;
  }
}

// Save Venice API key to config file
function saveVeniceApiKey(apiKey) {
  const configPath = join(homedir(), '.venice-api.json');
  const config = { apiKey };
  
  const fs = await import('fs');
  fs.writeFileSync(configPath, JSON.stringify(config, null, 2), { mode: 0o600 });
  
  return configPath;
}

// Make authenticated request to Venice API
async function veniceRequest(endpoint, options = {}) {
  const apiKey = getVeniceApiKey();
  
  if (!apiKey) {
    throw new Error('Venice API key not configured. Run: node src/venice.js setup <api_key>');
  }
  
  const url = `${VENICE_API_BASE}${endpoint}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      'Authorization': `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });
  
  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Venice API error (${response.status}): ${error}`);
  }
  
  return response.json();
}

// Commands

async function setupApiKey(apiKey) {
  if (!apiKey) {
    console.log('Usage: node src/venice.js setup <api_key>');
    console.log('');
    console.log('Get your API key at: https://venice.ai/settings/api');
    process.exit(1);
  }
  
  // Validate the API key by making a test request
  const testUrl = `${VENICE_API_BASE}/models`;
  const response = await fetch(testUrl, {
    headers: { 'Authorization': `Bearer ${apiKey}` },
  });
  
  if (!response.ok) {
    throw new Error('Invalid API key. Get yours at https://venice.ai/settings/api');
  }
  
  const configPath = join(homedir(), '.venice-api.json');
  const { writeFileSync } = await import('fs');
  writeFileSync(configPath, JSON.stringify({ apiKey }, null, 2), { mode: 0o600 });
  
  return { success: true, message: 'API key saved', configPath };
}

async function listModels(type = 'text') {
  const data = await veniceRequest(`/models?type=${type}`);
  
  return data.data.map(model => ({
    id: model.id,
    name: model.model_spec?.name || model.id,
    privacy: model.model_spec?.privacy || 'unknown',
    context: model.model_spec?.availableContextTokens,
    capabilities: {
      vision: model.model_spec?.capabilities?.supportsVision,
      reasoning: model.model_spec?.capabilities?.supportsReasoning,
      functionCalling: model.model_spec?.capabilities?.supportsFunctionCalling,
      webSearch: model.model_spec?.capabilities?.supportsWebSearch,
    },
    pricing: model.model_spec?.pricing,
  }));
}

async function getBalance() {
  const data = await veniceRequest('/api_keys/self');
  
  return {
    consumptionCurrency: data.consumptionCurrency,
    balances: data.balances,
    diemEpochAllocation: data.diemEpochAllocation,
    // Calculate remaining DIEM if staking
    diemRemaining: data.balances?.diem ?? null,
    diemUsedPercent: data.diemEpochAllocation 
      ? ((data.diemEpochAllocation - (data.balances?.diem || 0)) / data.diemEpochAllocation * 100).toFixed(1)
      : null,
  };
}

async function chatCompletion(prompt, options = {}) {
  const model = options.model || 'zai-org-glm-4.7'; // GLM 4.7 - Private, fast, good default
  const systemPrompt = options.system || null;
  
  const messages = [];
  if (systemPrompt) {
    messages.push({ role: 'system', content: systemPrompt });
  }
  messages.push({ role: 'user', content: prompt });
  
  const requestBody = {
    model,
    messages,
    stream: false,
    ...(options.veniceParams && { venice_parameters: options.veniceParams }),
  };
  
  const data = await veniceRequest('/chat/completions', {
    method: 'POST',
    body: JSON.stringify(requestBody),
  });
  
  return {
    model: data.model,
    response: data.choices?.[0]?.message?.content,
    usage: data.usage,
    finishReason: data.choices?.[0]?.finish_reason,
  };
}

async function generateImage(prompt, options = {}) {
  const model = options.model || 'flux-2-pro';
  
  const requestBody = {
    model,
    prompt,
    n: options.count || 1,
    size: options.size || '1024x1024',
  };
  
  const data = await veniceRequest('/images/generations', {
    method: 'POST',
    body: JSON.stringify(requestBody),
  });
  
  return {
    model: data.data?.[0]?.model || model,
    images: data.data?.map(img => ({
      url: img.url,
      revisedPrompt: img.revised_prompt,
    })),
  };
}

// CLI

const args = process.argv.slice(2);
const command = args[0];
const jsonOutput = args.includes('--json');

function output(data) {
  if (jsonOutput) {
    console.log(JSON.stringify(data, null, 2));
  } else {
    console.log(data);
  }
}

async function main() {
  try {
    switch (command) {
      case 'setup': {
        const apiKey = args[1];
        const result = await setupApiKey(apiKey);
        output(result);
        break;
      }
      
      case 'models': {
        const type = args[1] || 'text';
        const models = await listModels(type);
        if (jsonOutput) {
          output(models);
        } else {
          console.log(`\nVenice ${type.charAt(0).toUpperCase() + type.slice(1)} Models:\n`);
          for (const m of models) {
            const privacy = m.privacy === 'private' ? '🔒' : '👤';
            console.log(`  ${privacy} ${m.name} (${m.id})`);
            if (m.context) console.log(`     Context: ${m.context.toLocaleString()} tokens`);
          }
          console.log('');
        }
        break;
      }
      
      case 'balance': {
        const balance = await getBalance();
        if (jsonOutput) {
          output(balance);
        } else {
          console.log('\nVenice Account Balance:\n');
          console.log(`  Currency: ${balance.consumptionCurrency}`);
          if (balance.diemRemaining !== null) {
            console.log(`  DIEM Remaining: ${balance.diemRemaining}`);
            console.log(`  DIEM Allocation: ${balance.diemEpochAllocation}`);
            console.log(`  Usage: ${balance.diemUsedPercent}%`);
          }
          if (balance.balances?.usd !== undefined) {
            console.log(`  USD Balance: $${balance.balances.usd}`);
          }
          console.log('');
        }
        break;
      }
      
      case 'chat': {
        const prompt = args.slice(1).filter(a => !a.startsWith('--')).join(' ');
        if (!prompt) {
          console.error('Usage: node src/venice.js chat <prompt> [--model <model>] [--json]');
          process.exit(1);
        }
        
        const modelArg = args.find((a, i) => args[i-1] === '--model');
        const result = await chatCompletion(prompt, { model: modelArg });
        
        if (jsonOutput) {
          output(result);
        } else {
          console.log(`\n[${result.model}]:\n`);
          console.log(result.response);
          console.log(`\n(${result.usage?.total_tokens || '?'} tokens)\n`);
        }
        break;
      }
      
      case 'generate':
      case 'image': {
        const prompt = args.slice(1).filter(a => !a.startsWith('--')).join(' ');
        if (!prompt) {
          console.error('Usage: node src/venice.js generate <prompt> [--model <model>] [--json]');
          process.exit(1);
        }
        
        const modelArg = args.find((a, i) => args[i-1] === '--model');
        const result = await generateImage(prompt, { model: modelArg });
        
        if (jsonOutput) {
          output(result);
        } else {
          console.log(`\nGenerated with ${result.model}:\n`);
          for (const img of result.images) {
            console.log(`  ${img.url}`);
          }
          console.log('');
        }
        break;
      }
      
      case 'help':
      default: {
        console.log(`
Venice AI API Integration

Commands:
  setup <api_key>      Save your Venice API key (get it at venice.ai/settings/api)
  models [type]        List available models (text, image, video)
  balance              Check DIEM balance and allocation
  chat <prompt>        Send a chat completion request
  generate <prompt>    Generate an image

Options:
  --model <id>         Specify model to use
  --json               Output as JSON

Payment with DIEM:
  Venice uses DIEM tokens for compute. 1 staked DIEM = $1/day of inference.
  
  DIEM token (Base): ${DIEM_TOKEN_ADDRESS}
  
  To pay with crypto:
  1. Get VVV tokens on Base
  2. Stake VVV to receive DIEM at venice.ai/staking
  3. Staked DIEM automatically enables API access

Examples:
  node src/venice.js setup vn_abc123...
  node src/venice.js models
  node src/venice.js chat "Explain quantum computing" --model zai-org-glm-4.7
  node src/venice.js generate "A cyberpunk cat" --model flux-2-pro --json
`);
        break;
      }
    }
  } catch (error) {
    if (jsonOutput) {
      output({ error: error.message });
    } else {
      console.error(`Error: ${error.message}`);
    }
    process.exit(1);
  }
}

main();
