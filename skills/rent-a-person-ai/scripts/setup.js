#!/usr/bin/env node
/**
 * RentAPerson one-click setup for OpenClaw.
 * Run from the skill directory: node scripts/setup.js
 * Or, if the skill is installed via ClawHub: node <skill-dir>/scripts/setup.js
 *
 * Does everything hands-off:
 * - Prompts for env (prod vs dev), agent name, email, gateway base URL, session key, hooks token
 * - Registers agent, saves credentials
 * - Injects skill env into openclaw.json
 * - Ensures hooks/transforms dir, copies rentaperson-inject-key-transform (with overwrite prompt)
 * - Patches openclaw.json hooks (transformsDir + mapping for /hooks/rentaperson)
 * - Registers webhook at <gateway>/hooks/rentaperson with webhookSessionKey, webhookFormat, webhookBearerToken
 * - Optional: restart gateway, optional verify
 */

const fs = require('fs');
const path = require('path');
const readline = require('readline');
const { spawn } = require('child_process');
const net = require('net');

const OPENCLAW_CONFIG_PATH =
  process.env.OPENCLAW_CONFIG ||
  path.join(process.env.HOME || process.env.USERPROFILE || '', '.openclaw', 'openclaw.json');

const ENVS = {
  prod: 'https://rentaperson.ai',
  dev: 'https://dev.rentaperson.ai',
};

const TRANSFORM_FILENAME = 'rentaperson-inject-key-transform.js';
const HOOK_NAME = 'rentaperson';

function ask(rl, question, defaultVal = '') {
  const suffix = defaultVal ? ` [${defaultVal}]` : '';
  return new Promise((resolve) => {
    rl.question(`${question}${suffix}: `, (answer) => {
      resolve((answer && answer.trim()) || defaultVal);
    });
  });
}

function askYesNo(rl, question, defaultNo = true) {
  const def = defaultNo ? 'y/N' : 'Y/n';
  return new Promise((resolve) => {
    rl.question(`${question} [${def}]: `, (answer) => {
      const trimmed = (answer && answer.trim().toLowerCase()) || '';
      if (defaultNo) resolve(trimmed === 'y' || trimmed === 'yes');
      else resolve(trimmed !== 'n' && trimmed !== 'no');
    });
  });
}

async function registerAgent(apiBase, agentName, contactEmail) {
  const res = await fetch(`${apiBase}/api/agents/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      agentName,
      agentType: 'openclaw',
      description: `OpenClaw agent: ${agentName}`,
      contactEmail,
    }),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Register failed ${res.status}: ${text}`);
  }
  return res.json();
}

async function patchAgentMe(apiBase, apiKey, body) {
  const res = await fetch(`${apiBase}/api/agents/me`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': apiKey,
    },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`PATCH /api/agents/me failed ${res.status}: ${text}`);
  }
  return res.json();
}

async function getAgentMe(apiBase, apiKey) {
  const res = await fetch(`${apiBase}/api/agents/me`, {
    headers: {
      'X-API-Key': apiKey,
    },
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`GET /api/agents/me failed ${res.status}: ${text}`);
  }
  return res.json();
}

/**
 * Strip agent:main: prefix if present - OpenClaw adds it automatically
 * This prevents double prefixing: agent:main:agent:main:main -> agent:main:main
 */
function normalizeSessionKeyForOpenClaw(sessionKey) {
  const OPENCLAW_SESSION_PREFIX = 'agent:main:';
  const trimmed = sessionKey.trim();
  // If it already starts with agent:main:, strip it (OpenClaw will add it back)
  if (trimmed.startsWith(OPENCLAW_SESSION_PREFIX)) {
    return trimmed.slice(OPENCLAW_SESSION_PREFIX.length);
  }
  return trimmed;
}

async function sendMessageToOpenClawSession(sessionKey, message, openclawUrl, token) {
  const url = `${openclawUrl}/hooks/agent`;
  const headers = {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` }),
  };
  // Strip agent:main: prefix - OpenClaw adds it automatically
  const normalizedSessionKey = normalizeSessionKeyForOpenClaw(sessionKey);
  const body = {
    message,
    name: 'RentAPerson Setup',
    sessionKey: normalizedSessionKey,
    wakeMode: 'now',
    deliver: false, // Don't send to messaging channels
  };
  
  try {
    const res = await fetch(url, {
      method: 'POST',
      headers,
      body: JSON.stringify(body),
    });
    if (!res.ok) {
      const text = await res.text();
      throw new Error(`Failed to send message: ${res.status} ${text}`);
    }
    return true;
  } catch (err) {
    throw new Error(`Error sending message to session: ${err.message}`);
  }
}

function loadOpenClawConfig() {
  const raw = safeReadFile(OPENCLAW_CONFIG_PATH);
  if (!raw) return {};
  try {
    return JSON.parse(raw);
  } catch (e) {
    // OpenClaw config may use JSON5 format (unquoted keys, comments, trailing commas)
    // Try to parse it leniently by fixing common JSON5 -> JSON issues
    if (e instanceof SyntaxError) {
      try {
        let fixed = raw;
        
        // Fix unquoted keys (e.g., hooks: -> "hooks":)
        // Match: { or , followed by whitespace, then identifier, then :
        fixed = fixed.replace(/([{,]\s*)([a-zA-Z_$][a-zA-Z0-9_$]*)\s*:/g, '$1"$2":');
        
        // Remove single-line comments (// ...)
        fixed = fixed.replace(/\/\/.*$/gm, '');
        
        // Remove trailing commas before } or ]
        fixed = fixed.replace(/,(\s*[}\]])/g, '$1');
        
        // Try parsing the fixed version
        const parsed = JSON.parse(fixed);
        console.log('⚠️  Note: Config uses JSON5 format (unquoted keys). Auto-converted to strict JSON for update.');
        return parsed;
      } catch (e2) {
        // If auto-fix fails, fall through to show error
      }
    }
    if (e instanceof SyntaxError) {
      const msg = e.message.match(/position (\d+)/);
      const pos = msg ? parseInt(msg[1], 10) : 0;
      const line = pos ? raw.slice(0, pos).split('\n').length : 0;
      const lines = raw.split('\n');
      const contextStart = Math.max(0, line - 3);
      const contextEnd = Math.min(lines.length, line + 2);
      const context = lines.slice(contextStart, contextEnd);
      
      // Show error - config uses JSON5 format that we couldn't auto-fix
      console.error(`\n⚠️  Warning: ${OPENCLAW_CONFIG_PATH} uses JSON5 format (unquoted keys, etc.)`);
      console.error(`   OpenClaw accepts this format, but we couldn't auto-convert it to strict JSON.`);
      console.error(`\nOriginal error: ${e.message}`);
      console.error('\nProblematic area (around line ' + line + '):');
      context.forEach((l, i) => {
        const lineNum = contextStart + i + 1;
        const marker = lineNum === line ? ' >>> ' : '     ';
        console.error(`${marker}${lineNum}: ${l}`);
      });
      console.error('\n💡 Tip: Your config is valid for OpenClaw (it uses JSON5 format).');
      console.error('   We\'ll skip updating it automatically, but you can update it manually if needed.');
      throw new Error(`Cannot auto-convert JSON5 config to strict JSON (config is valid for OpenClaw)`);
    }
    throw e;
  }
}

function saveOpenClawConfig(config) {
  const success = safeWriteFile(OPENCLAW_CONFIG_PATH, JSON.stringify(config, null, 2));
  if (!success) {
    throw new Error(`Failed to save config to ${OPENCLAW_CONFIG_PATH}`);
  }
}

function getStateDir() {
  return (
    process.env.OPENCLAW_STATE_DIR ||
    path.dirname(OPENCLAW_CONFIG_PATH) ||
    path.join(process.env.HOME || process.env.USERPROFILE || '', '.openclaw')
  );
}

function isPortAvailable(port) {
  return new Promise((resolve) => {
    const server = net.createServer();
    server.listen(port, () => {
      server.once('close', () => resolve(true));
      server.close();
    });
    server.on('error', () => resolve(false));
  });
}

async function findAvailablePort(startPort = 3001, maxAttempts = 10) {
  for (let i = 0; i < maxAttempts; i++) {
    const port = startPort + i;
    if (await isPortAvailable(port)) {
      return port;
    }
  }
  return null;
}

function safeReadFile(filePath, defaultValue = null) {
  try {
    return fs.readFileSync(filePath, 'utf8');
  } catch (e) {
    if (e.code === 'ENOENT') return defaultValue;
    throw e;
  }
}

function safeWriteFile(filePath, content) {
  try {
    const dir = path.dirname(filePath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
    fs.writeFileSync(filePath, content, 'utf8');
    return true;
  } catch (e) {
    console.error(`Failed to write ${filePath}:`, e.message);
    return false;
  }
}

function safeFileExists(filePath) {
  try {
    return fs.existsSync(filePath);
  } catch {
    return false;
  }
}

function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

async function checkOpenClawInstalled() {
  return new Promise((resolve) => {
    const child = spawn('openclaw', ['--version'], { stdio: 'pipe', shell: true });
    child.on('close', (code) => resolve(code === 0));
    child.on('error', () => resolve(false));
    setTimeout(() => {
      child.kill();
      resolve(false);
    }, 2000);
  });
}

async function checkGatewayRunning() {
  return new Promise((resolve) => {
    const client = net.createConnection({ port: 18789, host: '127.0.0.1' }, () => {
      client.end();
      resolve(true);
    });
    client.on('error', () => resolve(false));
    setTimeout(() => {
      client.destroy();
      resolve(false);
    }, 1000);
  });
}

function printWelcome() {
  console.log('\n' + '='.repeat(70));
  console.log('  🎉  Thank you for installing the RentAPerson skill!');
  console.log('='.repeat(70));
  console.log('\nYour agent will be able to:');
  console.log('  • Reply to messages from humans on RentAPerson');
  console.log('  • Review and respond to bounty applications');
  console.log('  • Manage conversations and applications via the RentAPerson API');
  console.log('  • Stay always-on for webhook events');
  console.log('\nLet\'s set up your agent. This will take just a few minutes.\n');
}

async function main() {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });

  printWelcome();
  
  // Pre-flight checks
  console.log('🔍 Pre-flight checks...');
  console.log('─'.repeat(70));
  const openclawInstalled = await checkOpenClawInstalled();
  if (!openclawInstalled) {
    console.warn('⚠️  Warning: OpenClaw CLI not found in PATH');
    console.warn('   Make sure OpenClaw is installed: https://docs.openclaw.ai/install');
    console.warn('   Setup will continue, but gateway restart may fail.\n');
  } else {
    console.log('✓ OpenClaw CLI found');
  }
  
  const gatewayRunning = await checkGatewayRunning();
  if (gatewayRunning) {
    console.log('✓ OpenClaw gateway is running on port 18789');
  } else {
    console.warn('⚠️  OpenClaw gateway not running (port 18789 not accessible)');
    console.warn('   Start it with: openclaw gateway start');
    console.warn('   Or restart after setup completes.\n');
  }
  
  const configExists = safeFileExists(OPENCLAW_CONFIG_PATH);
  if (!configExists) {
    console.log('ℹ️  Config file will be created:', OPENCLAW_CONFIG_PATH);
  } else {
    console.log('✓ Config file exists:', OPENCLAW_CONFIG_PATH);
  }
  console.log('');
  
  // Show OpenClaw profile and config path
  const profile = process.env.OPENCLAW_PROFILE || '';
  console.log('📌 OpenClaw configuration:');
  if (profile) {
    console.log(`   Profile: ${profile}`);
  } else {
    console.log('   Profile: (default)');
  }
  console.log(`   Config: ${OPENCLAW_CONFIG_PATH}`);
  console.log('');

  // 1. Base URL (prod vs dev)
  console.log('📋 Step 1: Choose your environment');
  console.log('─'.repeat(70));
  const envChoice = await ask(rl, 'Environment (prod | dev)', 'prod');
  const apiBase = ENVS[envChoice.toLowerCase()] || envChoice.trim() || ENVS.prod;
  if (!apiBase.startsWith('http')) {
    console.error('\n❌ Error: API base must be a full URL (e.g. https://rentaperson.ai or https://dev.rentaperson.ai).');
    rl.close();
    process.exit(1);
  }
  console.log(`✓ Using API base: ${apiBase}\n`);

  // 2. Agent details
  console.log('👤 Step 2: Agent details');
  console.log('─'.repeat(70));
  let agentName = await ask(rl, 'Friendly agent name', 'my-openclaw-agent');
  let contactEmail = await ask(rl, 'Contact email', '');
  if (!contactEmail) {
    console.error('\n❌ Error: Contact email is required.');
    rl.close();
    process.exit(1);
  }
  if (!isValidEmail(contactEmail)) {
    console.warn('⚠️  Warning: Email format looks invalid. Continuing anyway...');
    console.warn(`   Email: ${contactEmail}\n`);
  }
  console.log(`✓ Agent name: ${agentName}`);
  console.log(`✓ Contact email: ${contactEmail}`);
  console.log('  (If you sign up on the site with this email later, this agent will appear in Dashboard → Agents.)\n');

  // Resolve skill directory once (used throughout setup)
  const skillDir = path.resolve(__dirname, '..');

  // 3. Session configuration
  console.log('🔑 Step 3: Session configuration');
  console.log('─'.repeat(70));
  console.log('Architecture: Two-agent setup');
  console.log('  • Main session: Handles all chat correspondence');
  console.log('  • Webhook subagent: Processes webhooks automatically');
  console.log('');
  console.log('Main session key:');
  console.log('  • Your primary chat session (recommended: agent:main:main)');
  console.log('  • This is where you interact with the agent normally');
  console.log('');
  const mainSessionKeyInput = await ask(rl, 'Main session key (or press Enter for: agent:main:main)', 'agent:main:main');
  const mainSessionKey = mainSessionKeyInput || 'agent:main:main';
  
  console.log('');
  console.log('Webhook session key:');
  console.log('  • Dedicated session for webhook processing (recommended: agent:main:rentaperson)');
  console.log('  • Webhooks will spawn subagents from this session');
  console.log('  • This session stays focused on RentAPerson webhook handling');
  console.log('');
  const webhookSessionKeyInput = await ask(rl, 'Webhook session key (or press Enter for: agent:main:rentaperson)', 'agent:main:rentaperson');
  const webhookSessionKey = webhookSessionKeyInput || 'agent:main:rentaperson';
  
  const hooksToken = await ask(rl, 'OpenClaw hooks token (for Authorization: Bearer)', '');
  console.log(`✓ Main session: ${mainSessionKey}`);
  console.log(`✓ Webhook session: ${webhookSessionKey}`);
  if (hooksToken) {
    console.log(`✓ Hooks token: ${'*'.repeat(Math.min(hooksToken.length, 20))}...`);
  }
  console.log('');

  // 4. Choose approach: bridge vs transform
  console.log('🌐 Step 4: Webhook delivery method');
  console.log('─'.repeat(70));
  console.log('Choose how webhooks will be delivered to OpenClaw:');
  console.log('');
  console.log('  1. Bridge service (recommended)');
  console.log('     • Separate Node.js service running on its own port');
  console.log('     • More secure: API key never appears in OpenClaw transcripts');
  console.log('     • More reliable: doesn\'t depend on OpenClaw transform system');
  console.log('     • Better for production use');
  console.log('');
  console.log('  2. Transform');
  console.log('     • Uses OpenClaw\'s built-in transform system');
  console.log('     • Simpler setup (no separate service)');
  console.log('     • ⚠️  API key will appear in session transcripts');
  console.log('');
  const approachChoice = await ask(rl, 'Choose approach (1=bridge, 2=transform)', '1');
  const useBridge = approachChoice.trim() === '1' || approachChoice.trim() === 'bridge';
  console.log(`✓ Selected: ${useBridge ? 'Bridge service' : 'Transform'}\n`);

  let webhookUrl = '';
  if (!useBridge) {
    // Transform approach: need gateway base URL
    const gatewayBase = await ask(
      rl,
      'Gateway base URL (e.g. https://abc123.ngrok.io)',
      ''
    );
    if (!gatewayBase) {
      console.error('Gateway base URL is required so we can register webhook at /hooks/rentaperson.');
      rl.close();
      process.exit(1);
    }
    webhookUrl = gatewayBase.trim().replace(/\/$/, '');
    if (!webhookUrl.includes('/hooks/')) {
      webhookUrl += '/hooks/' + HOOK_NAME;
      console.log('Webhook URL will be:', webhookUrl);
    }
  } else {
    // Bridge approach: need public URL (ngrok) that will point to bridge
    console.log('\n📡 You\'ll need to expose the bridge with ngrok after setup.');
    console.log('   For now, enter the ngrok URL you plan to use (or leave empty to set later):');
    const ngrokUrl = await ask(rl, 'Public webhook URL (e.g. https://abc123.ngrok.io)', '');
    if (ngrokUrl) {
      webhookUrl = ngrokUrl.trim().replace(/\/$/, '');
      console.log(`✓ Will register webhook URL: ${webhookUrl}\n`);
    } else {
      console.log('⚠️  No webhook URL provided. You\'ll need to set it manually after exposing bridge.\n');
    }
  }

  let bridgePort = null;
  if (useBridge) {
    console.log('🔍 Checking for available port...');
    bridgePort = await findAvailablePort(3001);
    if (!bridgePort) {
      console.warn('⚠️  Could not find available port starting from 3001. Using 3001 anyway.');
      bridgePort = 3001;
    } else {
      console.log(`✓ Bridge will use port: ${bridgePort}\n`);
    }
  } else {
    // Transform approach: copy transform file
    const stateDir = getStateDir();
    const transformsDir = path.join(stateDir, 'hooks', 'transforms');
    const examplePath = path.join(skillDir, 'scripts', 'rentaperson-inject-key-transform.example.js');
    const destPath = path.join(transformsDir, TRANSFORM_FILENAME);

    if (!safeFileExists(examplePath)) {
      console.error(`\n❌ Error: Example transform not found: ${examplePath}`);
      rl.close();
      process.exit(1);
    }
    if (safeFileExists(destPath)) {
      const overwrite = await askYesNo(rl, `Transform ${TRANSFORM_FILENAME} already exists. Overwrite?`, true);
      if (!overwrite) {
        console.log('⏭️  Skipping transform copy.\n');
      } else {
        const success = safeWriteFile(destPath, safeReadFile(examplePath, ''));
        if (success) {
          console.log(`✓ Copied transform to ${destPath}\n`);
        } else {
          console.warn('⚠️  Failed to copy transform. Continuing anyway...\n');
        }
      }
    } else {
      const success = safeWriteFile(destPath, safeReadFile(examplePath, ''));
      if (success) {
        console.log(`✓ Copied transform to ${destPath}\n`);
      } else {
        console.warn('⚠️  Failed to copy transform. Continuing anyway...\n');
      }
    }
  }

  // 4b. Use existing agent or register new
  console.log('🤖 Step 4b: Agent (new or existing)');
  console.log('─'.repeat(70));
  console.log('You can register a new agent or use one you already created (e.g. from Dashboard → Agents).');
  const useExisting = await askYesNo(rl, 'Use an existing agent? (enter agent ID + API key)', false);

  let agentId, apiKey;
  if (useExisting) {
    const existingAgentId = await ask(rl, 'Agent ID (e.g. agent_abc123...)', '');
    const existingApiKey = await ask(rl, 'API key (rap_...)', '');
    if (!existingAgentId?.trim() || !existingApiKey?.trim()) {
      console.error('\n❌ Agent ID and API key are required.');
      rl.close();
      process.exit(1);
    }
    console.log('Verifying agent...');
    try {
      const res = await fetch(`${apiBase}/api/agents/me`, {
        headers: { 'X-API-Key': existingApiKey.trim() },
      });
      if (!res.ok) {
        const text = await res.text();
        console.error(`\n❌ Invalid API key or agent not found (${res.status}). Check Agent ID and key from Dashboard → Agents.`);
        rl.close();
        process.exit(1);
      }
      const data = await res.json();
      agentId = data.agent?.agentId || existingAgentId.trim();
      apiKey = existingApiKey.trim();
      if (data.agent?.agentName) agentName = data.agent.agentName;
      console.log(`✓ Using existing agent: ${agentId}`);
      console.log(`  Name: ${agentName}\n`);
    } catch (err) {
      console.error(`\n❌ Error verifying agent: ${err.message}`);
      rl.close();
      process.exit(1);
    }
  } else {
    // Register new agent
    console.log('Registering new agent with RentAPerson...');
    try {
      const reg = await registerAgent(apiBase, agentName, contactEmail);
      agentId = reg.agent?.agentId;
      apiKey = reg.apiKey;
      if (!agentId || !apiKey) {
        console.error('\n❌ Error: Unexpected response from registration:', reg);
        rl.close();
        process.exit(1);
      }
      console.log(`✓ Agent registered successfully!`);
      console.log(`  Agent ID: ${agentId}`);
      console.log(`  API Key: ${apiKey.substring(0, 10)}...${apiKey.substring(apiKey.length - 4)}\n`);
    } catch (err) {
      console.error(`\n❌ Error registering agent: ${err.message}`);
      rl.close();
      process.exit(1);
    }
  }

  rl.close();

  // 5. (Registration done above) Continue with config and webhook

  // Store credentials in memory (only write to file if user wants)
  const credentialsPath = path.join(skillDir, 'rentaperson-agent.json');
  const credentials = {
    agentId,
    apiKey,
    agentName,
    contactEmail,
    webhookUrl: webhookUrl || (useBridge ? `http://127.0.0.1:${bridgePort || 3001}` : ''),
    mainSessionKey,
    webhookSessionKey,
    apiBase,
    bridgePort: useBridge ? (bridgePort || 3001) : undefined,
    useBridge,
    openclawToken: hooksToken || undefined, // Save token for bridge to use
  };

  // 6. Save credentials (optional for bridge)
  if (useBridge) {
    const rlCreds = readline.createInterface({ input: process.stdin, output: process.stdout });
    const saveCreds = await askYesNo(rlCreds, 'Save credentials to file? (recommended for bridge service)', true);
    rlCreds.close();
    if (saveCreds) {
      const success = safeWriteFile(credentialsPath, JSON.stringify(credentials, null, 2));
      if (success) {
        console.log(`✓ Credentials saved to ${credentialsPath}\n`);
      } else {
        console.warn('⚠️  Failed to save credentials file. Bridge service will need env vars.\n');
      }
    } else {
      console.log('⏭️  Credentials stored in memory only. Bridge service will need env vars.\n');
    }
  }

  // 7. Update OpenClaw configuration
  console.log('⚙️  Step 6: Updating OpenClaw configuration');
  console.log('─'.repeat(70));
  let config;
  try {
    config = loadOpenClawConfig();
  } catch (err) {
    console.error(`\n❌ Cannot update OpenClaw config: ${err.message}`);
    console.error('\nPlease fix the JSON file and run setup again, or continue without updating config.');
    const rlConfig = readline.createInterface({ input: process.stdin, output: process.stdout });
    const continueAnyway = await askYesNo(rlConfig, 'Continue without updating OpenClaw config?', true);
    rlConfig.close();
    if (!continueAnyway) {
      console.log('\nExiting. Fix the JSON file and run setup again.');
      process.exit(1);
    }
    console.log('⚠️  Continuing without updating OpenClaw config. You\'ll need to update it manually.\n');
    config = {}; // Use empty config
  }
  if (!config.skills) config.skills = {};
  if (!config.skills.entries) config.skills.entries = {};
  if (!config.skills.entries['rent-a-person-ai']) config.skills.entries['rent-a-person-ai'] = {};
  
  // Ensure skill is enabled so gateway loads SKILL.md and instructions
  config.skills.entries['rent-a-person-ai'].enabled = true;
  
  // Set env vars (API key, agent details) so webhook sessions have them
  config.skills.entries['rent-a-person-ai'].env = {
    RENTAPERSON_API_KEY: apiKey,
    RENTAPERSON_AGENT_ID: agentId,
    RENTAPERSON_AGENT_NAME: agentName,
    RENTAPERSON_AGENT_TYPE: 'openclaw',
    ...(config.skills.entries['rent-a-person-ai'].env || {}),
  };
  
  // Ensure skill directory is discoverable by OpenClaw
  // OpenClaw auto-discovers from: <workspace>/skills, ~/.openclaw/skills, or skills.load.extraDirs
  const stateDir = getStateDir();
  const managedSkillsDir = path.join(stateDir, 'skills');
  const skillName = 'rent-a-person-ai';
  const managedSkillPath = path.join(managedSkillsDir, skillName);
  const skillInManaged = skillDir === managedSkillPath || fs.existsSync(path.join(managedSkillPath, 'SKILL.md'));
  
  // Check if skill is in workspace (would be <workspace>/skills/rent-a-person-ai)
  const workspaceDir = config.agents?.defaults?.workspace || path.join(stateDir, 'workspace');
  const workspaceSkillsDir = path.join(workspaceDir, 'skills');
  const workspaceSkillPath = path.join(workspaceSkillsDir, skillName);
  const skillInWorkspace = skillDir === workspaceSkillPath || fs.existsSync(path.join(workspaceSkillPath, 'SKILL.md'));
  
  if (!skillInManaged && !skillInWorkspace) {
    // Skill is not in a standard location; add to extraDirs so OpenClaw can find it
    if (!config.skills.load) config.skills.load = {};
    if (!Array.isArray(config.skills.load.extraDirs)) config.skills.load.extraDirs = [];
    if (!config.skills.load.extraDirs.includes(skillDir)) {
      config.skills.load.extraDirs.push(skillDir);
      console.log(`✓ Added skill directory to skills.load.extraDirs: ${skillDir}`);
    }
  } else {
    console.log(`✓ Skill directory is in standard location (will be auto-discovered)`);
  }

  // Configure hooks mapping for POST /hooks/rentaperson (see docs: match.path = URL segment)
  // Config examples: https://docs.openclaw.ai/gateway/configuration-examples — mappings array, match: { path: "name" }
  if (!config.hooks) config.hooks = {};
  if (!config.hooks.enabled) config.hooks.enabled = true;
  if (!config.hooks.token && hooksToken) config.hooks.token = hooksToken;
  if (!config.hooks.path) config.hooks.path = '/hooks';

  if (!Array.isArray(config.hooks.mappings)) {
    config.hooks.mappings = typeof config.hooks.mappings === 'object' && config.hooks.mappings !== null
      ? Object.entries(config.hooks.mappings).map(([p, v]) => ({ match: { path: p }, ...v }))
      : [];
  }
  let rentapersonMapping = config.hooks.mappings.find(
    (m) => (m.match && m.match.path === HOOK_NAME) || m.name === HOOK_NAME
  );
  if (!rentapersonMapping) {
    rentapersonMapping = { match: { path: HOOK_NAME }, name: 'RentAPerson' };
    config.hooks.mappings.push(rentapersonMapping);
  } else {
    if (!rentapersonMapping.match) rentapersonMapping.match = {};
    rentapersonMapping.match.path = HOOK_NAME;
    if (!rentapersonMapping.name) rentapersonMapping.name = 'RentAPerson';
  }

  rentapersonMapping.action = 'agent';
  rentapersonMapping.allowUnsafeExternalContent = true;
  // Use normalized key (suffix only) so OpenClaw doesn't double-prefix
  rentapersonMapping.sessionKey = normalizeSessionKeyForOpenClaw(webhookSessionKey);
  rentapersonMapping.wakeMode = 'now';

  if (!useBridge) {
    // Transform approach: also configure transform module (reuse stateDir from above)
    const transformsDir = path.join(stateDir, 'hooks', 'transforms');
    config.hooks.transformsDir = config.hooks.transformsDir || path.resolve(transformsDir);
    if (!rentapersonMapping.transform) {
      rentapersonMapping.transform = { module: TRANSFORM_FILENAME };
    } else if (typeof rentapersonMapping.transform === 'string') {
      rentapersonMapping.transform = { module: rentapersonMapping.transform };
    }
  }

  // Verify SKILL.md exists so OpenClaw can load the skill instructions
  const skillMdPath = path.join(skillDir, 'SKILL.md');
  if (!fs.existsSync(skillMdPath)) {
    console.warn(`⚠️  Warning: SKILL.md not found at ${skillMdPath}`);
    console.warn('  OpenClaw needs SKILL.md to load skill instructions. Make sure the skill directory is correct.\n');
  } else {
    console.log(`✓ Verified SKILL.md exists at ${skillMdPath}`);
  }

  try {
    saveOpenClawConfig(config);
    console.log(`✓ Updated ${OPENCLAW_CONFIG_PATH}`);
    console.log(`  • Skill enabled: rent-a-person-ai`);
    console.log(`  • Skill environment variables configured (RENTAPERSON_API_KEY, etc.)`);
    console.log(`  • Skill directory discoverable (in standard location or extraDirs)`);
    console.log(`  • Hooks mapping configured: /hooks/${HOOK_NAME} (allowUnsafeExternalContent: true)`);
    if (!useBridge) {
      console.log(`  • Transform module configured`);
    }
    console.log('');
    console.log('⚠️  IMPORTANT: Restart OpenClaw gateway so it loads the skill and new config.');
    console.log('   The gateway must restart to:');
    console.log('   - Discover and load the RentAPerson skill (SKILL.md)');
    console.log('   - Apply the env vars (RENTAPERSON_API_KEY) to webhook sessions');
    console.log('   - Register the /hooks/rentaperson mapping');
    console.log('');
  } catch (e) {
    console.warn(`⚠️  Failed to update openclaw.json: ${e.message}`);
    console.warn('  You may need to manually update the config file.\n');
  }

  // 8. Register webhook with RentAPerson
  console.log('🔗 Step 7: Registering webhook');
  console.log('─'.repeat(70));
  const finalWebhookUrl = webhookUrl.trim();
  if (!finalWebhookUrl) {
    console.log('⚠️  No webhook URL provided. Skipping webhook registration.');
    console.log('   You can register it later after exposing your bridge/gateway with ngrok.\n');
  } else {
    // Validate HTTPS
    if (!finalWebhookUrl.startsWith('https://')) {
      console.error(`\n❌ Error: webhookUrl must be HTTPS (got: ${finalWebhookUrl})`);
      console.error('   RentAPerson requires HTTPS URLs for webhooks.');
      console.error('   Use ngrok or another HTTPS tunnel to expose your bridge/gateway.\n');
    } else {
      const patch = {
        webhookUrl: finalWebhookUrl,
        webhookFormat: 'openclaw',
        webhookSessionKey: webhookSessionKey.trim(),
      };
      if (hooksToken) patch.webhookBearerToken = hooksToken.trim();
      try {
        await patchAgentMe(apiBase, apiKey, patch);
        console.log(`✓ Webhook registered with RentAPerson`);
        console.log(`  Webhook URL: ${finalWebhookUrl}\n`);
      } catch (err) {
        console.error(`\n❌ Error registering webhook: ${err.message}`);
        console.error('  You may need to register it manually via PATCH /api/agents/me\n');
      }
    }
  }

  // 9. Optional restart
  console.log('🔄 Step 8: Gateway restart (optional)');
  console.log('─'.repeat(70));
  const rl2 = readline.createInterface({ input: process.stdin, output: process.stdout });
  const doRestart = await askYesNo(rl2, 'Restart OpenClaw gateway now? (recommended)', true);
  rl2.close();
  if (doRestart) {
    const profile = process.env.OPENCLAW_PROFILE || '';
    if (profile) {
      console.log(`📌 Using OpenClaw profile: ${profile}`);
    }
    const args = profile ? ['--profile', profile, 'gateway', 'restart'] : ['gateway', 'restart'];
    console.log(`Running: openclaw ${args.join(' ')}`);
    try {
      const child = spawn('openclaw', args, { stdio: 'inherit', shell: true });
      await new Promise((resolve, reject) => {
        child.on('close', (code) => (code === 0 ? resolve() : reject(new Error(`openclaw exited ${code}`))));
      });
      console.log('✓ Gateway restart completed.\n');
      console.log('📋 To watch gateway logs:');
      console.log('   openclaw logs --follow');
      console.log('   # Or tail directly: tail -f /tmp/openclaw/openclaw-*.log');
      console.log('');
    } catch (err) {
      console.warn(`⚠️  Gateway restart failed: ${err.message}`);
      console.warn('  Restart manually when ready: openclaw gateway restart\n');
      console.log('📋 To watch gateway logs after restart:');
      console.log('   openclaw logs --follow');
      console.log('   # Or tail directly: tail -f /tmp/openclaw/openclaw-*.log');
      console.log('');
    }
  } else {
    console.log('⏭️  Skipped restart. Restart manually when ready: openclaw gateway restart\n');
    console.log('📋 To watch gateway logs after restart:');
    console.log('   openclaw logs --follow');
    console.log('   # Or tail directly: tail -f /tmp/openclaw/openclaw-*.log');
    console.log('');
  }

  // 10. Send concise agent brief (workflows + API usage) to sessions (optional)
  console.log('📚 Step 9: Loading agent brief into sessions');
  console.log('─'.repeat(70));
  const rl3 = readline.createInterface({ input: process.stdin, output: process.stdout });
  const doLoadSkill = await askYesNo(rl3, 'Send workflows + API usage brief to sessions? (recommended)', true);
  rl3.close();
  if (doLoadSkill) {
    const briefPath = path.join(skillDir, 'AGENT_BRIEF.md');
    const skillMdPath = path.join(skillDir, 'SKILL.md');
    let briefContent = '';
    if (fs.existsSync(briefPath)) {
      briefContent = fs.readFileSync(briefPath, 'utf8');
    } else if (fs.existsSync(skillMdPath)) {
      console.warn('⚠️  AGENT_BRIEF.md not found, using short inline brief.');
      briefContent = `# RentAPerson — Agent brief\n\nYou process webhooks and reply via the RentAPerson API only. One flow per event (<30s).\n\n**Workflows:** message.received → read thread, if time then POST calendar event else POST reply. application.received → evaluate; if HIGH accept (PATCH status accepted) and calendar/message, else GET/POST conversation and message. work_evidence.submitted → find/create conversation, POST reply ack; optional PATCH bounty completed.\n\n**APIs:** Headers: X-API-Key, Content-Type: application/json. Body: one JSON object, double quotes, no trailing commas. Send message: {"senderType":"agent","senderId":"AGENT_ID","senderName":"Name","content":"..."}. Accept: {"status":"accepted"}. Calendar: {"title","startTime","endTime","humanId","agentId","bountyId"}.\n\nFull docs: SKILL.md or https://rentaperson.ai/skill.md`;
    }
    if (briefContent) {
      try {
        const openclawUrl = process.env.OPENCLAW_URL || 'http://127.0.0.1:18789';
        const credentialsSection = `🔑 Your RentAPerson Credentials (use these for all API calls):

- **API Key**: ${apiKey}
- **Agent ID**: ${agentId}
- **Agent Name**: ${agentName}
- **API Base URL**: ${apiBase}
- **Webhook Session**: ${webhookSessionKey}

**IMPORTANT**: Use the API key in the \`X-API-Key\` header for ALL RentAPerson API calls.
Example: \`curl -H "X-API-Key: ${apiKey}" "${apiBase}/api/conversations"\`

---
`;

        const message = `📚 RentAPerson — Workflows & API usage

${credentialsSection}

${briefContent}

---
Setup complete. Use the credentials above and the workflows/API bodies in this message. Full reference: SKILL.md or ${apiBase.replace(/\/$/, '')}/skill.md`;

        console.log(`Sending agent brief to main session: ${mainSessionKey}...`);
        await sendMessageToOpenClawSession(mainSessionKey, message, openclawUrl, hooksToken);
        console.log('✓ Agent brief loaded into main session');

        const webhookMessage = `📚 RentAPerson — Workflows & API usage (webhook session)

${credentialsSection}

${briefContent}

---
This session processes RentAPerson webhooks. Use the credentials and API bodies above. Full reference: SKILL.md or ${apiBase.replace(/\/$/, '')}/skill.md`;

        console.log(`Sending agent brief to webhook session: ${webhookSessionKey}...`);
        await sendMessageToOpenClawSession(webhookSessionKey, webhookMessage, openclawUrl, hooksToken);
        console.log('✓ Agent brief loaded into webhook session');
        console.log(`  Main session: ${mainSessionKey}`);
        console.log(`  Webhook session: ${webhookSessionKey}\n`);

        console.log('⚠️  Note: If you see a session named "agent:main:agent:main:rentaperson",');
        console.log('   that is a stale session from before the fix. The correct session is:');
        console.log(`   ${webhookSessionKey}`);
        console.log('   New webhooks will use the correct session.\n');
      } catch (err) {
        console.warn(`⚠️  Failed to send agent brief: ${err.message}`);
        console.warn('  You can manually send AGENT_BRIEF.md or SKILL.md to your sessions later.\n');
      }
    } else {
      console.warn('⚠️  AGENT_BRIEF.md and SKILL.md not found. Skipping.\n');
    }
  } else {
    console.log('⏭️  Skipped loading agent brief.\n');
  }

  // 11. Verification (optional)
  console.log('✅ Step 10: Verification (optional)');
  console.log('─'.repeat(70));
  const rl4 = readline.createInterface({ input: process.stdin, output: process.stdout });
  const doVerify = await askYesNo(rl4, 'Verify webhook registration? (checks RentAPerson API)', false);
  rl4.close();
  if (doVerify && finalWebhookUrl && apiKey) {
    try {
      const me = await getAgentMe(apiBase, apiKey);
      if (me?.webhookUrl === finalWebhookUrl) {
        console.log('✓ Webhook URL registered correctly');
      } else {
        console.warn(`⚠️  Webhook URL mismatch:`);
        console.warn(`   Expected: ${finalWebhookUrl}`);
        console.warn(`   Found: ${me?.webhookUrl || '(not set)'}`);
      }
      if (me?.webhookSessionKey === webhookSessionKey) {
        console.log('✓ Webhook session key registered correctly');
      } else {
        console.warn(`⚠️  Webhook session key mismatch:`);
        console.warn(`   Expected: ${webhookSessionKey}`);
        console.warn(`   Found: ${me?.webhookSessionKey || '(not set)'}`);
      }
    } catch (err) {
      console.warn(`⚠️  Verification failed: ${err.message}`);
    }
    console.log('');
  }

  // 12. Next steps
  console.log('✨ Setup complete! Next steps:');
  console.log('═'.repeat(70));
  
  console.log('\n📋 Monitor gateway logs:');
  console.log('   openclaw logs --follow');
  console.log('   # Or tail directly: tail -f /tmp/openclaw/openclaw-*.log');
  console.log('   # Look for: "Loaded skill: rent-a-person-ai" and webhook activity');
  console.log('');
  
  if (useBridge) {
    console.log('📦 To start the bridge service:');
    console.log('');
    console.log(`   1. cd ${path.join(skillDir, 'bridge')}`);
    if (safeFileExists(credentialsPath)) {
      console.log(`   2. node server.js  # (auto-loads credentials from ${credentialsPath})`);
    } else {
      console.log('   2. Set environment variables:');
      console.log(`      export RENTAPERSON_API_KEY="${apiKey}"`);
      console.log(`      export RENTAPERSON_AGENT_ID="${agentId}"`);
      console.log(`      export RENTAPERSON_AGENT_NAME="${agentName}"`);
      console.log(`      export OPENCLAW_URL="${process.env.OPENCLAW_URL || 'http://127.0.0.1:18789'}"`);
      if (hooksToken) console.log(`      export OPENCLAW_TOKEN="${hooksToken}"`);
      console.log(`      export BRIDGE_PORT=${bridgePort || 3001}`);
      console.log('   3. node server.js');
    }
    console.log('');
    console.log('🌐 To expose the bridge:');
    console.log('');
    console.log(`   ngrok http ${bridgePort || 3001}`);
    console.log('');
    console.log('🔗 Then update your RentAPerson webhook URL to your ngrok URL');
    console.log('');
    console.log('🧪 To test:');
    console.log('   Send a message or apply to a bounty on RentAPerson');
    console.log('   Your agent should respond via the RentAPerson API');
  } else {
    console.log('\n🌐 To expose your OpenClaw gateway:');
    console.log('');
    console.log('   ngrok http 18789');
    console.log('');
    console.log('🔗 Then update your RentAPerson webhook URL to:');
    console.log(`   <your-ngrok-url>/hooks/rentaperson`);
    console.log('');
    console.log('🧪 To test:');
    console.log('   Send a message or apply to a bounty on RentAPerson');
    console.log('   Check your webhook session - it should contain:');
    console.log('   [RENTAPERSON] Use for all API calls: X-API-Key: ...');
  }
  console.log('');
  console.log('═'.repeat(70));
  console.log('📋 Setup Summary');
  console.log('═'.repeat(70));
  console.log(`   Agent ID: ${agentId}`);
  console.log(`   Agent Name: ${agentName}`);
  console.log(`   API Base: ${apiBase}`);
  console.log(`   Main Session: ${mainSessionKey}`);
  console.log(`   Webhook Session: ${webhookSessionKey}`);
  console.log(`   Webhook URL: ${finalWebhookUrl || '(not set - configure after exposing bridge/gateway)'}`);
  console.log(`   Method: ${useBridge ? 'Bridge service' : 'Transform'}`);
  if (useBridge) {
    console.log(`   Bridge Port: ${bridgePort || 3001}`);
  }
  console.log('');
  console.log('═'.repeat(70));
  console.log('🎉 Your RentAPerson agent is ready to go!');
  console.log('═'.repeat(70));
  console.log('');
  console.log('💡 Quick test command (after starting bridge/gateway and ngrok):');
  console.log('');
  if (useBridge) {
    console.log(`   curl -X POST http://127.0.0.1:${bridgePort || 3001} \\`);
  } else {
    console.log(`   curl -X POST http://127.0.0.1:18789/hooks/rentaperson \\`);
  }
  console.log('     -H "Content-Type: application/json" \\');
  console.log('     -d \'{"event":"message.received","agentId":"' + agentId + '","conversationId":"test","humanId":"test","contentPreview":"Hello"}\'');
  console.log('');
  console.log('🔍 After restart, verify in logs:');
  console.log('   1. Skill loaded: grep "rent-a-person-ai" /tmp/openclaw/openclaw-*.log');
  console.log('   2. Hook registered: grep "rentaperson" /tmp/openclaw/openclaw-*.log');
  console.log('   3. Or use: openclaw logs --follow | grep -E "skill|rentaperson"');
  console.log('');
  console.log('📚 Need help? See:');
  console.log('   - INSTALLATION.md for detailed setup');
  console.log('   - scripts/verify-setup.md for troubleshooting');
  console.log('   - SKILL.md for API reference');
  console.log('');
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
