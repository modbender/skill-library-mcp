#!/usr/bin/env node
/**
 * ModelRouter 9001 Provider Sync
 * Nightly script to discover live models from providers and sync config.json
 * 
 * Usage: node provider-sync.js [--dry-run]
 */

const fs = require('fs');
const path = require('path');
const https = require('https');
const http = require('http');

// Paths
const SKILL_DIR = path.dirname(__dirname);
const CONFIG_PATH = path.join(SKILL_DIR, 'config.json');
const REPORT_PATH = path.join(SKILL_DIR, 'sync-report.json');
const SECRETS_DIR = path.join(process.env.HOME, '.openclaw', 'workspace', '.secrets');

// Config
const TELEGRAM_BOT_TOKEN = '8547915559:AAGqJlIiflFVBayXwT5GS5DsWyBTW_vlfw8';
const TELEGRAM_CHAT_ID = '1156712793';
const DRY_RUN = process.argv.includes('--dry-run');

// --- Utility Functions ---

function loadApiKey(envName, fileName) {
  // Try environment variable first
  if (process.env[envName]) {
    return process.env[envName];
  }
  
  // Try .secrets file
  const secretPath = path.join(SECRETS_DIR, fileName);
  if (fs.existsSync(secretPath)) {
    const content = fs.readFileSync(secretPath, 'utf8');
    const match = content.match(new RegExp(`${envName}=(.+)`));
    if (match) return match[1].trim();
  }
  
  return null;
}

function httpsGet(url, headers = {}) {
  return new Promise((resolve, reject) => {
    const parsedUrl = new URL(url);
    const options = {
      hostname: parsedUrl.hostname,
      port: parsedUrl.port || 443,
      path: parsedUrl.pathname + parsedUrl.search,
      method: 'GET',
      headers
    };
    
    https.get(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          try {
            resolve(JSON.parse(data));
          } catch (e) {
            reject(new Error(`Invalid JSON response: ${e.message}`));
          }
        } else {
          reject(new Error(`HTTP ${res.statusCode}: ${data}`));
        }
      });
    }).on('error', reject);
  });
}

function httpGet(url, headers = {}) {
  return new Promise((resolve, reject) => {
    const parsedUrl = new URL(url);
    const options = {
      hostname: parsedUrl.hostname,
      port: parsedUrl.port || 80,
      path: parsedUrl.pathname + parsedUrl.search,
      method: 'GET',
      headers
    };
    
    http.get(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          try {
            resolve(JSON.parse(data));
          } catch (e) {
            reject(new Error(`Invalid JSON response: ${e.message}`));
          }
        } else {
          reject(new Error(`HTTP ${res.statusCode}: ${data}`));
        }
      });
    }).on('error', reject);
  });
}

function sendTelegramMessage(text) {
  const url = `https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`;
  const payload = JSON.stringify({
    chat_id: TELEGRAM_CHAT_ID,
    text,
    parse_mode: 'Markdown'
  });
  
  return new Promise((resolve, reject) => {
    const parsedUrl = new URL(url);
    const options = {
      hostname: parsedUrl.hostname,
      port: 443,
      path: parsedUrl.pathname,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(payload)
      }
    };
    
    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve(data));
    });
    
    req.on('error', reject);
    req.write(payload);
    req.end();
  });
}

// --- Provider Fetchers ---

async function fetchAnthropicModels(apiKey) {
  if (!apiKey) return null;
  
  try {
    const data = await httpsGet('https://api.anthropic.com/v1/models', {
      'x-api-key': apiKey,
      'anthropic-version': '2023-06-01'
    });
    
    // Extract model IDs
    const models = (data.data || []).map(m => ({
      id: m.id,
      name: m.display_name || m.id,
      type: m.type
    }));
    
    return models;
  } catch (e) {
    console.error(`Anthropic fetch failed: ${e.message}`);
    return null;
  }
}

async function fetchOpenAIModels(apiKey) {
  if (!apiKey) return null;
  
  try {
    const data = await httpsGet('https://api.openai.com/v1/models', {
      'Authorization': `Bearer ${apiKey}`
    });
    
    // Filter to just chat models (exclude embeddings, whisper, etc.)
    const models = (data.data || [])
      .filter(m => m.id.includes('gpt') || m.id.includes('o1') || m.id.includes('o3'))
      .map(m => ({
        id: m.id,
        created: m.created,
        owned_by: m.owned_by
      }));
    
    return models;
  } catch (e) {
    console.error(`OpenAI fetch failed: ${e.message}`);
    return null;
  }
}

async function fetchOpenRouterModels(apiKey) {
  if (!apiKey) return null;
  
  try {
    const data = await httpsGet('https://openrouter.ai/api/v1/models', {
      'Authorization': `Bearer ${apiKey}`
    });
    
    // Extract relevant models with pricing
    const models = (data.data || []).map(m => ({
      id: m.id,
      name: m.name,
      pricing: {
        prompt: parseFloat(m.pricing?.prompt || 0),
        completion: parseFloat(m.pricing?.completion || 0)
      },
      context_length: m.context_length
    }));
    
    return models;
  } catch (e) {
    console.error(`OpenRouter fetch failed: ${e.message}`);
    return null;
  }
}

async function fetchOllamaModels(baseUrl) {
  try {
    const data = await httpGet(`${baseUrl}/api/tags`);
    
    const models = (data.models || []).map(m => ({
      id: m.name,
      size: m.size,
      modified_at: m.modified_at
    }));
    
    return models;
  } catch (e) {
    console.error(`Ollama (${baseUrl}) fetch failed: ${e.message}`);
    return null;
  }
}

// --- Model Comparison Logic ---

function normalizeModelId(id) {
  // Normalize for fuzzy matching: remove version suffixes, dates, etc.
  return id.toLowerCase()
    .replace(/-\d{8}$/, '')  // Remove date stamps
    .replace(/-v\d+/, '')    // Remove version numbers
    .replace(/[._-]/g, '');  // Remove separators
}

function fuzzyMatch(id1, id2) {
  const norm1 = normalizeModelId(id1);
  const norm2 = normalizeModelId(id2);
  
  // Exact normalized match
  if (norm1 === norm2) return true;
  
  // Check if one contains the other (for version upgrades)
  if (norm1.includes(norm2) || norm2.includes(norm1)) {
    // But make sure they're not wildly different
    const lenDiff = Math.abs(norm1.length - norm2.length);
    return lenDiff < 5;
  }
  
  return false;
}

function findConfigModel(config, provider, modelId) {
  for (const [tier, models] of Object.entries(config.tiers)) {
    for (const m of models) {
      if (m.provider === provider && m.model === modelId) {
        return { tier, model: m };
      }
    }
  }
  return null;
}

function compareModels(config, liveModels) {
  const report = {
    new_models: [],
    deprecated_models: [],
    pricing_updates: [],
    renamed_candidates: []
  };
  
  // Build map of all config models by provider
  const configModelsByProvider = {};
  for (const [tier, models] of Object.entries(config.tiers)) {
    for (const m of models) {
      if (!configModelsByProvider[m.provider]) {
        configModelsByProvider[m.provider] = [];
      }
      configModelsByProvider[m.provider].push({ ...m, tier });
    }
  }
  
  // Check each provider's live models
  for (const [provider, live] of Object.entries(liveModels)) {
    if (!live || !Array.isArray(live)) continue;
    
    const configModels = configModelsByProvider[provider] || [];
    const liveIds = live.map(m => m.id);
    const configIds = configModels.map(m => m.model);
    
    // Find new models
    for (const liveModel of live) {
      const exists = configModels.find(cm => cm.model === liveModel.id);
      if (!exists) {
        // Check for fuzzy match (renamed?)
        const fuzzy = configModels.find(cm => fuzzyMatch(cm.model, liveModel.id));
        if (fuzzy) {
          report.renamed_candidates.push({
            provider,
            old: fuzzy.model,
            new: liveModel.id,
            tier: fuzzy.tier
          });
        } else {
          report.new_models.push({
            provider,
            model: liveModel.id,
            ...(liveModel.pricing && { pricing: liveModel.pricing })
          });
        }
      }
    }
    
    // Find deprecated models
    for (const configModel of configModels) {
      const stillExists = liveIds.includes(configModel.model);
      const fuzzyExists = live.find(lm => fuzzyMatch(lm.id, configModel.model));
      
      if (!stillExists && !fuzzyExists) {
        report.deprecated_models.push({
          provider,
          model: configModel.model,
          tier: configModel.tier
        });
      }
    }
    
    // Check pricing updates (OpenRouter only)
    if (provider === 'openrouter') {
      for (const liveModel of live) {
        const configModel = configModels.find(cm => cm.model === liveModel.id);
        if (configModel && liveModel.pricing) {
          const liveCost = {
            input: liveModel.pricing.prompt * 1000000,  // Convert to per-1M tokens
            output: liveModel.pricing.completion * 1000000
          };
          
          const configCost = {
            input: configModel.inputCost,
            output: configModel.outputCost
          };
          
          const inputChanged = Math.abs(liveCost.input - configCost.input) > 0.01;
          const outputChanged = Math.abs(liveCost.output - configCost.output) > 0.01;
          
          if (inputChanged || outputChanged) {
            report.pricing_updates.push({
              provider,
              model: liveModel.id,
              tier: configModel.tier,
              old: configCost,
              new: liveCost
            });
          }
        }
      }
    }
  }
  
  return report;
}

// --- Config Update Logic ---

function updateConfig(config, comparison) {
  const updated = JSON.parse(JSON.stringify(config)); // Deep clone
  
  // Mark deprecated models
  for (const dep of comparison.deprecated_models) {
    const found = findConfigModel(updated, dep.provider, dep.model);
    if (found) {
      found.model.status = 'deprecated';
      found.model.deprecated_at = new Date().toISOString();
    }
  }
  
  // Update pricing
  for (const pricingUpdate of comparison.pricing_updates) {
    const found = findConfigModel(updated, pricingUpdate.provider, pricingUpdate.model);
    if (found) {
      found.model.inputCost = pricingUpdate.new.input;
      found.model.outputCost = pricingUpdate.new.output;
      found.model.pricing_updated_at = new Date().toISOString();
    }
  }
  
  // Add discovered models to a separate section (don't auto-add to tiers)
  if (comparison.new_models.length > 0 || comparison.renamed_candidates.length > 0) {
    if (!updated.discovered) updated.discovered = [];
    
    for (const newModel of comparison.new_models) {
      updated.discovered.push({
        provider: newModel.provider,
        model: newModel.model,
        discovered_at: new Date().toISOString(),
        ...(newModel.pricing && {
          pricing: {
            input: newModel.pricing.prompt * 1000000,
            output: newModel.pricing.completion * 1000000
          }
        })
      });
    }
    
    for (const renamed of comparison.renamed_candidates) {
      updated.discovered.push({
        provider: renamed.provider,
        model: renamed.new,
        possibly_renamed_from: renamed.old,
        discovered_at: new Date().toISOString()
      });
    }
  }
  
  // Add sync metadata
  updated.last_sync = {
    at: new Date().toISOString(),
    deprecated_count: comparison.deprecated_models.length,
    new_count: comparison.new_models.length,
    pricing_updates: comparison.pricing_updates.length
  };
  
  return updated;
}

// --- Main Logic ---

async function main() {
  console.log('🔄 ModelRouter 9001 Provider Sync');
  console.log(`Mode: ${DRY_RUN ? 'DRY RUN' : 'LIVE'}\n`);
  
  // Load API keys
  const anthropicKey = loadApiKey('ANTHROPIC_API_KEY', 'anthropic.env');
  const openaiKey = loadApiKey('OPENAI_API_KEY', 'openai.env');
  const openrouterKey = loadApiKey('OPENROUTER_API_KEY', 'openrouter.env');
  
  console.log('API Keys:');
  console.log(`  Anthropic: ${anthropicKey ? '✓' : '✗'}`);
  console.log(`  OpenAI: ${openaiKey ? '✓' : '✗'}`);
  console.log(`  OpenRouter: ${openrouterKey ? '✓' : '✗'}`);
  console.log('  Ollama Local: ✓ (no auth)');
  console.log('  Ollama Forge: ✓ (no auth)\n');
  
  // Fetch from all providers
  const liveModels = {};
  const providersChecked = [];
  const providersFailed = [];
  
  console.log('Fetching live models...\n');
  
  // Anthropic
  const anthropicModels = await fetchAnthropicModels(anthropicKey);
  if (anthropicModels) {
    liveModels.anthropic = anthropicModels;
    providersChecked.push('anthropic');
    console.log(`✓ Anthropic: ${anthropicModels.length} models`);
  } else {
    providersFailed.push('anthropic');
    console.log('✗ Anthropic: failed');
  }
  
  // OpenAI
  const openaiModels = await fetchOpenAIModels(openaiKey);
  if (openaiModels) {
    liveModels.openai = openaiModels;
    liveModels['openai-codex'] = openaiModels;  // Same models for both providers
    liveModels['openai-responses'] = openaiModels;
    providersChecked.push('openai', 'openai-codex', 'openai-responses');
    console.log(`✓ OpenAI: ${openaiModels.length} models`);
  } else {
    providersFailed.push('openai');
    console.log('✗ OpenAI: failed');
  }
  
  // OpenRouter
  const openrouterModels = await fetchOpenRouterModels(openrouterKey);
  if (openrouterModels) {
    liveModels.openrouter = openrouterModels;
    providersChecked.push('openrouter');
    console.log(`✓ OpenRouter: ${openrouterModels.length} models`);
  } else {
    providersFailed.push('openrouter');
    console.log('✗ OpenRouter: failed');
  }
  
  // Ollama Local
  const ollamaLocalModels = await fetchOllamaModels('http://localhost:11434');
  if (ollamaLocalModels) {
    liveModels['ollama-local'] = ollamaLocalModels;
    providersChecked.push('ollama-local');
    console.log(`✓ Ollama Local: ${ollamaLocalModels.length} models`);
  } else {
    providersFailed.push('ollama-local');
    console.log('✗ Ollama Local: failed');
  }
  
  // Ollama Forge
  const ollamaForgeModels = await fetchOllamaModels('http://100.118.158.58:11434');
  if (ollamaForgeModels) {
    liveModels['ollama-teseract'] = ollamaForgeModels;
    providersChecked.push('ollama-teseract');
    console.log(`✓ Ollama Forge: ${ollamaForgeModels.length} models`);
  } else {
    providersFailed.push('ollama-teseract');
    console.log('✗ Ollama Forge: failed');
  }
  
  // Google (from config - we don't have API access to list models dynamically)
  liveModels['google-antigravity'] = [
    { id: 'gemini-3.1-flash' },
    { id: 'gemini-3.1-pro' }
  ];
  providersChecked.push('google-antigravity');
  console.log('✓ Google: 2 models (static)');
  
  // Groq (from config - free tier, no dynamic listing)
  liveModels.groq = [
    { id: 'llama-3.3-70b-versatile' }
  ];
  providersChecked.push('groq');
  console.log('✓ Groq: 1 model (static)');
  
  // DeepSeek (from config - no dynamic listing API)
  liveModels.deepseek = [
    { id: 'deepseek-chat' },
    { id: 'deepseek-reasoner' }
  ];
  providersChecked.push('deepseek');
  console.log('✓ DeepSeek: 2 models (static)\n');
  
  // Load current config
  const config = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
  
  // Compare and generate report
  console.log('Analyzing differences...\n');
  const comparison = compareModels(config, liveModels);
  
  // Build sync report
  const syncReport = {
    synced_at: new Date().toISOString(),
    dry_run: DRY_RUN,
    providers_checked: providersChecked,
    providers_failed: providersFailed,
    new_models: comparison.new_models,
    deprecated_models: comparison.deprecated_models,
    renamed_candidates: comparison.renamed_candidates,
    pricing_updates: comparison.pricing_updates,
    summary: `${providersChecked.length} providers checked, ${comparison.new_models.length} new models, ${comparison.deprecated_models.length} deprecated, ${comparison.pricing_updates.length} pricing updates`
  };
  
  // Display results
  console.log('=== SYNC RESULTS ===\n');
  console.log(`New models found: ${comparison.new_models.length}`);
  if (comparison.new_models.length > 0) {
    for (const m of comparison.new_models) {
      console.log(`  + ${m.provider}/${m.model}`);
    }
  }
  
  console.log(`\nDeprecated models: ${comparison.deprecated_models.length}`);
  if (comparison.deprecated_models.length > 0) {
    for (const m of comparison.deprecated_models) {
      console.log(`  - ${m.provider}/${m.model} (${m.tier})`);
    }
  }
  
  console.log(`\nRenamed candidates: ${comparison.renamed_candidates.length}`);
  if (comparison.renamed_candidates.length > 0) {
    for (const m of comparison.renamed_candidates) {
      console.log(`  ~ ${m.provider}/${m.old} → ${m.new}`);
    }
  }
  
  console.log(`\nPricing updates: ${comparison.pricing_updates.length}`);
  if (comparison.pricing_updates.length > 0) {
    for (const m of comparison.pricing_updates) {
      console.log(`  $ ${m.provider}/${m.model}`);
      console.log(`    Input: ${m.old.input} → ${m.new.input}`);
      console.log(`    Output: ${m.old.output} → ${m.new.output}`);
    }
  }
  
  // Save sync report
  fs.writeFileSync(REPORT_PATH, JSON.stringify(syncReport, null, 2));
  console.log(`\n✓ Sync report saved to ${REPORT_PATH}`);
  
  // Update config if not dry-run
  if (!DRY_RUN) {
    const updatedConfig = updateConfig(config, comparison);
    fs.writeFileSync(CONFIG_PATH, JSON.stringify(updatedConfig, null, 2));
    console.log(`✓ Config updated at ${CONFIG_PATH}`);
  } else {
    console.log('⚠ DRY RUN - config.json not modified');
  }
  
  // Send Telegram notification if significant changes
  const hasSignificantChanges = 
    comparison.new_models.length > 0 || 
    comparison.deprecated_models.length > 0 ||
    comparison.renamed_candidates.length > 0;
  
  if (hasSignificantChanges && !DRY_RUN) {
    const message = `🔄 *ModelRouter Sync*\n\n${syncReport.summary}\n\n` +
      (comparison.new_models.length > 0 ? `➕ New: ${comparison.new_models.map(m => m.model).join(', ')}\n` : '') +
      (comparison.deprecated_models.length > 0 ? `➖ Deprecated: ${comparison.deprecated_models.map(m => m.model).join(', ')}\n` : '') +
      (comparison.renamed_candidates.length > 0 ? `🔄 Renamed: ${comparison.renamed_candidates.length}\n` : '');
    
    try {
      await sendTelegramMessage(message);
      console.log('\n✓ Telegram notification sent');
    } catch (e) {
      console.error(`\n✗ Telegram notification failed: ${e.message}`);
    }
  }
  
  console.log('\n✓ Sync complete!');
}

// Run
main().catch(e => {
  console.error('Fatal error:', e);
  process.exit(1);
});
