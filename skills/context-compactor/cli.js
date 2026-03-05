#!/usr/bin/env node
/**
 * Jasper Context Compactor CLI
 * Setup script with interactive token limit configuration
 */

const fs = require('fs');
const path = require('path');
const os = require('os');
const readline = require('readline');

const OPENCLAW_CONFIG = path.join(os.homedir(), '.openclaw', 'openclaw.json');
const OPENCLAW_BACKUPS = path.join(os.homedir(), '.openclaw', 'backups');
const OPENCLAW_EXTENSIONS = path.join(os.homedir(), '.openclaw', 'extensions', 'context-compactor');
const OLD_EXTENSIONS = path.join(os.homedir(), '.openclaw', 'extensions', 'openclaw-context-compactor');

function log(msg) {
  console.log(`📦 ${msg}`);
}

function error(msg) {
  console.error(`❌ ${msg}`);
}

function prompt(question) {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });
  
  return new Promise(resolve => {
    rl.question(question, answer => {
      rl.close();
      resolve(answer.trim());
    });
  });
}

function backupConfig() {
  if (!fs.existsSync(OPENCLAW_CONFIG)) return null;
  
  fs.mkdirSync(OPENCLAW_BACKUPS, { recursive: true });
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const backupPath = path.join(OPENCLAW_BACKUPS, `openclaw-${timestamp}.json`);
  
  fs.copyFileSync(OPENCLAW_CONFIG, backupPath);
  return backupPath;
}

// Local model providers that benefit from context compaction
const LOCAL_PROVIDER_NAMES = ['ollama', 'lmstudio', 'llamacpp', 'mlx', 'friend-gpu', 'openrouter'];

// URLs that indicate local/Ollama endpoints
const LOCAL_URL_PATTERNS = [
  ':11434',           // Ollama default port
  'localhost',
  '127.0.0.1',
  '0.0.0.0',
  /100\.\d+\.\d+\.\d+/,  // Tailscale
  /192\.168\.\d+\.\d+/,  // Local network
  /10\.\d+\.\d+\.\d+/,   // Private network
];

function isLocalProvider(providerId, providers = {}) {
  if (!providerId) return false;
  const lower = providerId.toLowerCase();
  
  // Check provider name
  if (LOCAL_PROVIDER_NAMES.some(p => lower.includes(p))) {
    return true;
  }
  
  // Check provider's baseUrl for local patterns
  const provider = providers[providerId];
  if (provider?.baseUrl) {
    const url = provider.baseUrl.toLowerCase();
    for (const pattern of LOCAL_URL_PATTERNS) {
      if (pattern instanceof RegExp) {
        if (pattern.test(url)) return true;
      } else {
        if (url.includes(pattern)) return true;
      }
    }
  }
  
  return false;
}

async function detectModelContextWindow(config) {
  const modelConfig = config?.agents?.defaults?.model;
  if (!modelConfig) return null;
  
  const providers = config?.models?.providers || {};
  
  // Collect all model candidates: primary first, then fallbacks
  const candidates = [];
  if (modelConfig.primary) candidates.push(modelConfig.primary);
  if (modelConfig.fallbacks) candidates.push(...modelConfig.fallbacks);
  
  // Track if any local models are in the chain
  let hasLocalModel = false;
  let localModelInfo = null;
  
  // Find the first candidate that has a contextWindow defined in its provider
  for (const modelId of candidates) {
    if (!modelId.includes('/')) continue; // Skip if no provider prefix
    
    const [providerName, ...modelParts] = modelId.split('/');
    const modelName = modelParts.join('/'); // e.g., "qwen2.5"
    
    // Check if this is a local provider (by name or baseUrl)
    if (isLocalProvider(providerName, providers)) {
      hasLocalModel = true;
      
      const provider = providers[providerName];
      const found = provider?.models?.find(m => m.id === modelName);
      
      if (!localModelInfo || found?.contextWindow) {
        localModelInfo = {
          model: modelId,
          tokens: found?.contextWindow || null,
          source: found?.contextWindow ? 'config' : 'unknown',
          maxTokens: found?.maxTokens,
          isLocal: true
        };
      }
    }
    
    const provider = providers[providerName];
    if (!provider?.models) continue;
    
    // Find model by ID in this provider's models array
    const found = provider.models.find(m => m.id === modelName);
    
    if (found?.contextWindow) {
      return {
        model: modelId,
        tokens: found.contextWindow,
        source: 'config',
        maxTokens: found.maxTokens,
        hasLocalModel,
        localModelInfo
      };
    }
  }
  
  // If we have local model info but no contextWindow from config, return that
  if (localModelInfo) {
    return {
      ...localModelInfo,
      hasLocalModel: true
    };
  }
  
  // No contextWindow found in config - try known defaults
  const primaryId = modelConfig.primary || '';
  const knownContexts = {
    'anthropic/claude': 200000,
    'openai/gpt-4': 128000,
    'openai/gpt-3.5': 16000,
  };
  
  for (const [pattern, tokens] of Object.entries(knownContexts)) {
    if (primaryId.toLowerCase().includes(pattern.toLowerCase())) {
      return { model: primaryId, tokens, source: 'fallback', hasLocalModel };
    }
  }
  
  return { model: primaryId, tokens: null, source: 'unknown', hasLocalModel };
}

async function setup() {
  console.log('');
  log('Jasper Context Compactor — Setup');
  console.log('='.repeat(55));
  
  // Explain what we're going to do
  console.log('');
  console.log('  This setup will:');
  console.log('');
  console.log('  1. Copy plugin files to ~/.openclaw/extensions/');
  console.log('  2. Add plugin config to your openclaw.json');
  console.log('  3. Help you configure token limits for your model');
  console.log('');
  console.log('  🔒 Privacy: Everything runs locally. Nothing is sent externally.');
  console.log('  📁 Your config will be backed up before any changes.');
  console.log('');
  
  const proceed = await prompt('  Continue? (y/n): ');
  if (proceed.toLowerCase() !== 'y' && proceed.toLowerCase() !== 'yes') {
    console.log('\n  Setup cancelled.\n');
    process.exit(0);
  }
  
  // Check if OpenClaw is installed
  const openclawDir = path.join(os.homedir(), '.openclaw');
  if (!fs.existsSync(openclawDir)) {
    console.log('');
    error('OpenClaw not detected (~/.openclaw not found)');
    console.log('  Install OpenClaw first: https://docs.openclaw.ai');
    process.exit(1);
  }
  
  // Backup config FIRST
  console.log('');
  log('Backing up config...');
  const backupPath = backupConfig();
  if (backupPath) {
    console.log(`  ✓ Backup saved: ${backupPath}`);
    console.log('  → Restore with: cp "' + backupPath + '" ~/.openclaw/openclaw.json');
  } else {
    console.log('  ⚠ No existing config to backup');
  }
  
  // Copy plugin files
  console.log('');
  log('Installing plugin files...');
  fs.mkdirSync(OPENCLAW_EXTENSIONS, { recursive: true });
  
  const pluginDir = path.dirname(__filename);
  const filesToCopy = ['index.ts', 'openclaw.plugin.json'];
  
  for (const file of filesToCopy) {
    const src = path.join(pluginDir, file);
    const dest = path.join(OPENCLAW_EXTENSIONS, file);
    if (fs.existsSync(src)) {
      fs.copyFileSync(src, dest);
      console.log(`  ✓ Copied: ${file}`);
    }
  }
  
  // Clean up old package name
  if (fs.existsSync(OLD_EXTENSIONS)) {
    try {
      fs.rmSync(OLD_EXTENSIONS, { recursive: true });
      console.log('  ✓ Removed old openclaw-context-compactor extension');
    } catch (e) {
      console.log(`  ⚠ Could not remove old extension: ${e.message}`);
    }
  }
  
  // Load existing config
  let config = {};
  if (fs.existsSync(OPENCLAW_CONFIG)) {
    try {
      config = JSON.parse(fs.readFileSync(OPENCLAW_CONFIG, 'utf8'));
    } catch (e) {
      error(`Could not parse openclaw.json: ${e.message}`);
      process.exit(1);
    }
  }
  
  // Determine token limit
  console.log('');
  log('Configuring token limits...');
  console.log('');
  console.log('  To set the right limit, I can check your OpenClaw config');
  console.log('  to see what model you\'re using.');
  console.log('');
  
  const checkConfig = await prompt('  Check your config for model info? (y/n): ');
  
  let maxTokens = 16000;  // OpenClaw minimum
  let detectedInfo = null;
  
  if (checkConfig.toLowerCase() === 'y' || checkConfig.toLowerCase() === 'yes') {
    detectedInfo = await detectModelContextWindow(config);
    
    // Debug: show what we found
    if (process.env.DEBUG) {
      console.log('  [DEBUG] detectedInfo:', JSON.stringify(detectedInfo, null, 2));
    }
    
    // Show local model recommendation
    if (detectedInfo?.hasLocalModel || detectedInfo?.isLocal) {
      console.log('');
      console.log('  🎯 Local model detected in your config!');
      const localModel = detectedInfo.localModelInfo?.model || detectedInfo.model;
      console.log(`     → ${localModel}`);
      console.log('');
      console.log('  Local models (Ollama, llama.cpp, MLX, LM Studio) don\'t report');
      console.log('  context overflow errors — they silently truncate or produce garbage.');
      console.log('  This plugin is HIGHLY recommended for your setup.');
    }
    
    if (detectedInfo && detectedInfo.tokens) {
      console.log('');
      console.log(`  ✓ Detected model: ${detectedInfo.model}`);
      console.log(`  ✓ Context window: ${detectedInfo.tokens.toLocaleString()} tokens (from ${detectedInfo.source})`);
      
      // Use the actual contextWindow, apply minimum
      let suggested = detectedInfo.tokens;
      if (suggested < 16000) {
        console.log(`  ⚠ Model context (${suggested}) is below OpenClaw minimum (16000)`);
        console.log(`  → Will use 16,000 tokens to prevent agent failures`);
        suggested = 16000;
      }
      console.log('');
      
      const useDetected = await prompt(`  Use ${suggested.toLocaleString()} tokens? (y/n, or enter custom): `);
      
      if (useDetected.toLowerCase() === 'y' || useDetected.toLowerCase() === 'yes' || useDetected === '') {
        maxTokens = suggested;
      } else if (/^\d+$/.test(useDetected)) {
        maxTokens = parseInt(useDetected, 10);
      } else {
        maxTokens = suggested; // Default to suggested on invalid input
      }
    } else if (detectedInfo && detectedInfo.model) {
      console.log('');
      console.log(`  ⚠ Found model: ${detectedInfo.model}`);
      console.log('  ⚠ No contextWindow defined in your config for this model.');
      console.log('  💡 Add contextWindow to your model config in openclaw.json');
    }
  }
  
  // Manual entry only if we couldn't detect context window at all
  if (!detectedInfo?.tokens) {
    console.log('');
    console.log('  Could not auto-detect context window from your config.');
    console.log('');
    console.log('  Common context windows:');
    console.log('    • Ollama / llama.cpp (small): 8,000 - 16,000');
    console.log('    • Mistral / Qwen (medium):    32,000');
    console.log('    • Claude / GPT-4 (large):     128,000+');
    console.log('');
    console.log('  💡 Tip: Check your model config in ~/.openclaw/openclaw.json');
    console.log('     Look for: models.providers.<provider>.models[].contextWindow');
    console.log('');
    console.log('  ⚠️  Minimum: 16,000 tokens (OpenClaw requirement)');
    console.log('');
    
    const customTokens = await prompt('  Enter maxTokens (default 16000, minimum 16000): ');
    if (/^\d+$/.test(customTokens)) {
      maxTokens = parseInt(customTokens, 10);
    }
  }
  
  // Enforce minimum
  const MIN_TOKENS = 16000;
  if (maxTokens < MIN_TOKENS) {
    console.log('');
    console.log(`  ⚠️  Warning: ${maxTokens} tokens is below OpenClaw's minimum of ${MIN_TOKENS}.`);
    console.log(`     Increasing to ${MIN_TOKENS} to prevent agent failures.`);
    console.log('');
    console.log('  If your model truly has a smaller context window, consider:');
    console.log('    • Using a larger model (Qwen 7B+ or Mistral 7B+)');
    console.log('    • Using the cloud fallback for complex tasks');
    console.log('');
    maxTokens = MIN_TOKENS;
  }
  
  // Calculate derived values
  const keepRecentTokens = Math.floor(maxTokens * 0.25);
  const summaryMaxTokens = Math.floor(maxTokens * 0.125);
  
  console.log('');
  console.log('  Final configuration:');
  console.log(`    maxTokens:        ${maxTokens.toLocaleString()}`);
  console.log(`    keepRecentTokens: ${keepRecentTokens.toLocaleString()} (25%)`);
  console.log(`    summaryMaxTokens: ${summaryMaxTokens.toLocaleString()} (12.5%)`);
  
  // Update openclaw.json
  console.log('');
  log('Updating OpenClaw config...');
  
  if (!config.plugins) config.plugins = {};
  if (!config.plugins.entries) config.plugins.entries = {};
  
  config.plugins.entries['context-compactor'] = {
    enabled: true,
    config: {
      maxTokens,
      keepRecentTokens,
      summaryMaxTokens,
      charsPerToken: 4
    }
  };
  
  fs.writeFileSync(OPENCLAW_CONFIG, JSON.stringify(config, null, 2) + '\n');
  console.log('  ✓ Saved to openclaw.json');
  
  // Done!
  console.log('');
  console.log('='.repeat(55));
  log('Setup complete!');
  console.log('');
  console.log('  Next steps:');
  console.log('    1. Restart OpenClaw: openclaw gateway restart');
  console.log('    2. Check status in chat: /context-stats');
  console.log('');
  console.log('  To adjust later:');
  console.log('    Edit ~/.openclaw/openclaw.json');
  console.log('    Look for plugins.entries["context-compactor"].config');
  console.log('');
  if (backupPath) {
    console.log('  To restore original config:');
    console.log(`    cp "${backupPath}" ~/.openclaw/openclaw.json`);
    console.log('');
  }
}

function showHelp() {
  console.log(`
Jasper Context Compactor
Token-based context compaction for local models (MLX, llama.cpp, Ollama)

USAGE:
  npx jasper-context-compactor setup    Install and configure plugin
  npx jasper-context-compactor help     Show this help

WHAT IT DOES:
  Local LLMs don't report context overflow errors like cloud APIs.
  This plugin estimates tokens client-side and proactively summarizes
  older messages before hitting your model's context limit.

SETUP PROCESS:
  1. Backs up your openclaw.json (with restore instructions)
  2. Copies plugin files to ~/.openclaw/extensions/
  3. Asks permission before reading your config
  4. Detects your model and suggests appropriate token limits
  5. Lets you customize or enter values manually
  6. Updates openclaw.json with the plugin config

PRIVACY:
  Everything runs 100% locally. Nothing is sent to external servers.
  We only read your local config file (with your permission).

COMMANDS (in chat after setup):
  /context-stats    Show current token usage
  /compact-now      Force fresh compaction
`);
}

// Main
const command = process.argv[2];

switch (command) {
  case 'setup':
  case 'install':
    setup().catch(err => {
      error(err.message);
      process.exit(1);
    });
    break;
  case 'help':
  case '--help':
  case '-h':
  case undefined:
    showHelp();
    break;
  default:
    error(`Unknown command: ${command}`);
    showHelp();
    process.exit(1);
}
