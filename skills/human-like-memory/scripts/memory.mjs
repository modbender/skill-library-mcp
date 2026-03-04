#!/usr/bin/env node
/**
 * Human-Like Memory CLI for OpenClaw Skill
 *
 * Usage:
 *   node memory.mjs recall "query"
 *   node memory.mjs save "user message" "assistant response"
 *   node memory.mjs save-batch                    # reads JSON from stdin
 *   node memory.mjs search "query"
 *   node memory.mjs config
 */

import { readFile } from 'fs/promises';
import { homedir } from 'os';
import { join } from 'path';
import { createInterface } from 'readline';

const SKILL_VERSION = '0.4.0';

// Configuration paths
const OPENCLAW_DIR = join(homedir(), '.openclaw');
const SECRETS_FILE = join(OPENCLAW_DIR, 'secrets.json');
const CONFIG_FILE = join(OPENCLAW_DIR, 'skills', 'human-like-memory', 'config.json');

/**
 * Upgrade notification from server
 */
let upgradeNotification = null;

/**
 * Load secrets from OpenClaw secrets store
 */
async function loadSecrets() {
  try {
    const data = await readFile(SECRETS_FILE, 'utf-8');
    const secrets = JSON.parse(data);
    return secrets['human-like-memory'] || {};
  } catch (error) {
    // Fallback to environment variables
    return {
      apiKey: process.env.HUMAN_LIKE_MEM_API_KEY,
      baseUrl: process.env.HUMAN_LIKE_MEM_BASE_URL,
      userId: process.env.HUMAN_LIKE_MEM_USER_ID,
    };
  }
}

/**
 * Load skill configuration
 */
async function loadConfig() {
  try {
    const data = await readFile(CONFIG_FILE, 'utf-8');
    return JSON.parse(data);
  } catch {
    return {};
  }
}

/**
 * Build configuration from secrets and config
 */
async function buildConfig() {
  const secrets = await loadSecrets();
  const config = await loadConfig();

  const saveTriggerTurns = config.saveTriggerTurns || 5;

  return {
    baseUrl: secrets.baseUrl || secrets.HUMAN_LIKE_MEM_BASE_URL || process.env.HUMAN_LIKE_MEM_BASE_URL || 'https://human-like.me',
    apiKey: secrets.apiKey || secrets.HUMAN_LIKE_MEM_API_KEY || process.env.HUMAN_LIKE_MEM_API_KEY,
    userId: secrets.userId || secrets.HUMAN_LIKE_MEM_USER_ID || process.env.HUMAN_LIKE_MEM_USER_ID || 'openclaw-user',
    memoryLimitNumber: config.memoryLimitNumber || 6,
    minScore: config.minScore || 0.1,
    timeoutMs: config.timeoutMs || 30000,
    scenario: secrets.scenario || secrets.HUMAN_LIKE_MEM_SCENARIO || process.env.HUMAN_LIKE_MEM_SCENARIO || 'openclaw-skill',
    // New: conversation storage settings
    saveTriggerTurns: saveTriggerTurns,
    saveMaxTurns: saveTriggerTurns * 2,
  };
}

/**
 * Build actionable guidance when API key is missing
 */
function buildMissingApiKeyError() {
  return {
    success: false,
    error: 'API Key not configured. HUMAN_LIKE_MEM_API_KEY is required.',
    nextSteps: [
      'If installed from ClawHub: open OpenClaw skill settings and fill the secret form.',
      'Or run setup script: bash ~/.openclaw/skills/human-like-memory/scripts/setup.sh',
      'Then verify config: node ~/.openclaw/skills/human-like-memory/scripts/memory.mjs config',
    ],
    helpUrl: 'https://human-like.me',
  };
}

/**
 * Make HTTP request with timeout
 */
async function httpRequest(url, options, timeoutMs = 5000) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    // Check for upgrade notification in response headers
    checkUpgradeHeaders(response);

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`HTTP ${response.status}: ${errorText.substring(0, 200)}`);
    }

    const jsonResult = await response.json();

    // Also check for upgrade notification in response body
    checkUpgradeBody(jsonResult);

    return jsonResult;
  } catch (error) {
    clearTimeout(timeoutId);
    if (error.name === 'AbortError') {
      throw new Error(`Request timeout after ${timeoutMs}ms`);
    }
    throw error;
  }
}

/**
 * Check response headers for upgrade notification
 */
function checkUpgradeHeaders(response) {
  const upgradeRequired = response.headers.get('X-Upgrade-Required');
  const upgradeVersion = response.headers.get('X-Upgrade-Version');
  const upgradeMessage = response.headers.get('X-Upgrade-Message');
  const upgradeUrl = response.headers.get('X-Upgrade-Url');

  if (upgradeRequired === 'true' || upgradeVersion) {
    upgradeNotification = {
      required: upgradeRequired === 'true',
      version: upgradeVersion || 'latest',
      message: upgradeMessage || `Please upgrade to version ${upgradeVersion || 'latest'}`,
      url: upgradeUrl || 'https://clawhub.dev/skills/human-like-memory',
      currentVersion: SKILL_VERSION,
    };
  }
}

/**
 * Check response body for upgrade notification
 */
function checkUpgradeBody(result) {
  if (result && result._upgrade) {
    const upgrade = result._upgrade;
    upgradeNotification = {
      required: upgrade.required === true,
      version: upgrade.version || 'latest',
      message: upgrade.message || `Please upgrade to version ${upgrade.version || 'latest'}`,
      url: upgrade.url || 'https://clawhub.dev/skills/human-like-memory',
      currentVersion: SKILL_VERSION,
    };
  }
}

/**
 * Format upgrade notification for output
 */
function formatUpgradeNotification() {
  if (!upgradeNotification) return null;

  const { required, version, message, url, currentVersion } = upgradeNotification;

  return {
    upgradeRequired: required,
    currentVersion,
    latestVersion: version,
    message,
    upgradeUrl: url,
    upgradeCommand: 'openclaw skill upgrade human-like-memory',
  };
}

/**
 * Recall memories based on query
 */
async function recallMemory(query) {
  const cfg = await buildConfig();

  if (!cfg.apiKey) {
    console.error(JSON.stringify(buildMissingApiKeyError()));
    process.exit(1);
  }

  const url = `${cfg.baseUrl}/plugin/v1/search/memory`;
  const payload = {
    query: query,
    user_id: cfg.userId,
    memory_limit_number: cfg.memoryLimitNumber,
    min_score: cfg.minScore,
  };

  try {
    const result = await httpRequest(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': cfg.apiKey,
        'x-request-id': `openclaw-skill-${Date.now()}`,
      },
      body: JSON.stringify(payload),
    }, cfg.timeoutMs);

    if (!result.success) {
      console.error(JSON.stringify({
        success: false,
        error: result.error || 'Memory retrieval failed',
      }));
      process.exit(1);
    }

    const memories = result.memories || [];

    // Format output for agent consumption
    const output = {
      success: true,
      count: memories.length,
      memories: memories.map(m => ({
        content: m.description || m.event || '',
        timestamp: m.timestamp,
        score: m.score,
      })),
    };

    // Also output human-readable format for context injection
    if (memories.length > 0) {
      output.context = formatMemoriesForContext(memories);
    }

    // Add upgrade notification if present
    const upgradeInfo = formatUpgradeNotification();
    if (upgradeInfo) {
      output._upgrade = upgradeInfo;
      upgradeNotification = null; // Clear after showing
    }

    console.log(JSON.stringify(output, null, 2));
  } catch (error) {
    const errorOutput = {
      success: false,
      error: error.message,
    };

    // Add upgrade notification even on error
    const upgradeInfo = formatUpgradeNotification();
    if (upgradeInfo) {
      errorOutput._upgrade = upgradeInfo;
      upgradeNotification = null;
    }

    console.error(JSON.stringify(errorOutput));
    process.exit(1);
  }
}

/**
 * Save messages to memory
 */
async function saveMemory(userMessage, assistantResponse) {
  const cfg = await buildConfig();

  if (!cfg.apiKey) {
    console.error(JSON.stringify(buildMissingApiKeyError()));
    process.exit(1);
  }

  const url = `${cfg.baseUrl}/plugin/v1/add/message`;
  const sessionId = `session-${Date.now()}`;
  const messages = [];

  if (userMessage) {
    messages.push({ role: 'user', content: userMessage });
  }
  if (assistantResponse) {
    messages.push({ role: 'assistant', content: assistantResponse });
  }

  if (messages.length === 0) {
    console.error(JSON.stringify({
      success: false,
      error: 'No messages to save',
    }));
    process.exit(1);
  }

  const payload = {
    user_id: cfg.userId,
    conversation_id: sessionId,
    messages: messages,
    tags: ['openclaw-skill'],
    async_mode: true,
    custom_workflows: {
      stream_params: {
        metadata: JSON.stringify({
          user_ids: [cfg.userId],
          session_id: sessionId,
          scenario: cfg.scenario || 'openclaw-skill',
        }),
      },
    },
  };

  try {
    const result = await httpRequest(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': cfg.apiKey,
        'x-request-id': `openclaw-skill-${Date.now()}`,
      },
      body: JSON.stringify(payload),
    }, cfg.timeoutMs);

    const output = {
      success: true,
      message: 'Memory saved successfully',
      memoriesCount: result.memories_count || 0,
    };

    // Add upgrade notification if present
    const upgradeInfo = formatUpgradeNotification();
    if (upgradeInfo) {
      output._upgrade = upgradeInfo;
      upgradeNotification = null;
    }

    console.log(JSON.stringify(output));
  } catch (error) {
    const errorOutput = {
      success: false,
      error: error.message,
    };

    // Add upgrade notification even on error
    const upgradeInfo = formatUpgradeNotification();
    if (upgradeInfo) {
      errorOutput._upgrade = upgradeInfo;
      upgradeNotification = null;
    }

    console.error(JSON.stringify(errorOutput));
    process.exit(1);
  }
}

/**
 * Search memories (alias for recall with different output format)
 */
async function searchMemory(query) {
  await recallMemory(query);
}

/**
 * Read JSON from stdin
 */
async function readStdin() {
  return new Promise((resolve, reject) => {
    let data = '';
    const rl = createInterface({
      input: process.stdin,
      terminal: false,
    });

    rl.on('line', (line) => {
      data += line;
    });

    rl.on('close', () => {
      resolve(data.trim());
    });

    rl.on('error', reject);

    // Timeout after 5 seconds if no input
    setTimeout(() => {
      rl.close();
      if (!data) {
        reject(new Error('No input received from stdin'));
      }
    }, 5000);
  });
}

/**
 * Save batch messages to memory (from stdin JSON)
 */
async function saveBatchMemory() {
  const cfg = await buildConfig();

  if (!cfg.apiKey) {
    console.error(JSON.stringify(buildMissingApiKeyError()));
    process.exit(1);
  }

  let inputData;
  try {
    inputData = await readStdin();
  } catch (error) {
    console.error(JSON.stringify({
      success: false,
      error: `Failed to read stdin: ${error.message}`,
      usage: 'echo \'[{"role":"user","content":"..."}, {"role":"assistant","content":"..."}]\' | node memory.mjs save-batch',
    }));
    process.exit(1);
  }

  let messages;
  try {
    messages = JSON.parse(inputData);
  } catch (error) {
    console.error(JSON.stringify({
      success: false,
      error: `Invalid JSON: ${error.message}`,
      received: inputData.substring(0, 200),
    }));
    process.exit(1);
  }

  if (!Array.isArray(messages) || messages.length === 0) {
    console.error(JSON.stringify({
      success: false,
      error: 'Messages must be a non-empty array',
    }));
    process.exit(1);
  }

  // Validate message format
  for (const msg of messages) {
    if (!msg.role || !msg.content) {
      console.error(JSON.stringify({
        success: false,
        error: 'Each message must have "role" and "content" fields',
        invalid: msg,
      }));
      process.exit(1);
    }
    if (!['user', 'assistant'].includes(msg.role)) {
      console.error(JSON.stringify({
        success: false,
        error: 'Role must be "user" or "assistant"',
        invalid: msg.role,
      }));
      process.exit(1);
    }
  }

  // Limit to saveMaxTurns
  const maxMessages = cfg.saveMaxTurns * 2; // Each turn has 2 messages
  const messagesToSave = messages.slice(-maxMessages);

  const url = `${cfg.baseUrl}/plugin/v1/add/message`;
  const sessionId = `session-${Date.now()}`;

  const payload = {
    user_id: cfg.userId,
    conversation_id: sessionId,
    messages: messagesToSave.map(m => ({
      role: m.role,
      content: m.content.substring(0, 20000), // Truncate if too long
    })),
    tags: ['openclaw-skill'],
    async_mode: true,
    custom_workflows: {
      stream_params: {
        metadata: JSON.stringify({
          user_ids: [cfg.userId],
          session_id: sessionId,
          scenario: cfg.scenario || 'openclaw-skill',
        }),
      },
    },
  };

  try {
    const result = await httpRequest(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': cfg.apiKey,
        'x-request-id': `openclaw-skill-${Date.now()}`,
      },
      body: JSON.stringify(payload),
    }, cfg.timeoutMs);

    const turnCount = Math.floor(messagesToSave.length / 2);
    const output = {
      success: true,
      message: `Saved ${turnCount} turns (${messagesToSave.length} messages) to memory`,
      memoriesCount: result.memories_count || 0,
      config: {
        saveTriggerTurns: cfg.saveTriggerTurns,
        saveMaxTurns: cfg.saveMaxTurns,
      },
    };

    // Add upgrade notification if present
    const upgradeInfo = formatUpgradeNotification();
    if (upgradeInfo) {
      output._upgrade = upgradeInfo;
      upgradeNotification = null;
    }

    console.log(JSON.stringify(output));
  } catch (error) {
    const errorOutput = {
      success: false,
      error: error.message,
    };

    // Add upgrade notification even on error
    const upgradeInfo = formatUpgradeNotification();
    if (upgradeInfo) {
      errorOutput._upgrade = upgradeInfo;
      upgradeNotification = null;
    }

    console.error(JSON.stringify(errorOutput));
    process.exit(1);
  }
}

/**
 * Show current configuration (without sensitive data)
 */
async function showConfig() {
  const cfg = await buildConfig();

  console.log(JSON.stringify({
    baseUrl: cfg.baseUrl,
    userId: cfg.userId,
    apiKeyConfigured: !!cfg.apiKey,
    memoryLimitNumber: cfg.memoryLimitNumber,
    minScore: cfg.minScore,
    saveTriggerTurns: cfg.saveTriggerTurns,
    saveMaxTurns: cfg.saveMaxTurns,
  }, null, 2));
}

/**
 * Format memories for context injection
 */
function formatMemoriesForContext(memories) {
  if (!memories || memories.length === 0) return '';

  const lines = memories
    .map(m => {
      const date = formatTime(m.timestamp);
      const content = m.description || m.event || '';
      const score = m.score ? ` (${(m.score * 100).toFixed(0)}% relevant)` : '';
      if (date) return `- [${date}] ${content}${score}`;
      return `- ${content}${score}`;
    })
    .filter(Boolean);

  return [
    '## Relevant Memories',
    '',
    ...lines,
    '',
  ].join('\n');
}

/**
 * Format timestamp for display
 */
function formatTime(value) {
  if (!value) return '';
  if (typeof value === 'number') {
    const date = new Date(value);
    if (isNaN(date.getTime())) return '';
    const pad = (v) => String(v).padStart(2, '0');
    return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`;
  }
  return String(value);
}

/**
 * Print usage information
 */
function printUsage() {
  console.log(`
Human-Like Memory CLI for OpenClaw

Usage:
  node memory.mjs <command> [arguments]

Commands:
  recall <query>                    Retrieve relevant memories for a query
  save <user_msg> [assistant_msg]   Save single conversation turn to memory
  save-batch                        Save multiple turns from stdin (JSON array)
  search <query>                    Search memories (alias for recall)
  config                            Show current configuration

Examples:
  node memory.mjs recall "What projects am I working on?"
  node memory.mjs save "I'm working on Project X" "Great, I'll remember that."
  node memory.mjs search "meeting notes"
  node memory.mjs config

  # Save batch (pipe JSON array of messages):
  echo '[{"role":"user","content":"Hi"},{"role":"assistant","content":"Hello!"}]' | node memory.mjs save-batch

Configuration:
  Set these in OpenClaw secrets or environment variables:
  - HUMAN_LIKE_MEM_API_KEY (required)
  - HUMAN_LIKE_MEM_BASE_URL (optional, default: https://human-like.me)
  - HUMAN_LIKE_MEM_USER_ID (optional, default: openclaw-user)

  Conversation storage settings (in config.json):
  - saveTriggerTurns: Number of turns before auto-save (default: 5)
  - saveMaxTurns: Max turns to save = saveTriggerTurns × 2 (default: 10)
`);
}

// Main entry point
const [,, command, ...args] = process.argv;

switch (command) {
  case 'recall':
    if (!args[0]) {
      console.error('Error: Query is required for recall command');
      process.exit(1);
    }
    await recallMemory(args.join(' '));
    break;

  case 'save':
    if (!args[0]) {
      console.error('Error: At least one message is required for save command');
      process.exit(1);
    }
    await saveMemory(args[0], args[1]);
    break;

  case 'save-batch':
    await saveBatchMemory();
    break;

  case 'search':
    if (!args[0]) {
      console.error('Error: Query is required for search command');
      process.exit(1);
    }
    await searchMemory(args.join(' '));
    break;

  case 'config':
    await showConfig();
    break;

  case 'help':
  case '--help':
  case '-h':
    printUsage();
    break;

  default:
    if (command) {
      console.error(`Unknown command: ${command}`);
    }
    printUsage();
    process.exit(1);
}
