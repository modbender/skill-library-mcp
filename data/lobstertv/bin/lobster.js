#!/usr/bin/env node
// Lobster CLI - Stream on Lobster.fun from the command line
// For use by OpenClaw agents and humans alike

import { Command } from 'commander';
import fs from 'fs';
import path from 'path';
import os from 'os';

const CONFIG_DIR = path.join(os.homedir(), '.lobster');
const CONFIG_FILE = path.join(CONFIG_DIR, 'config.json');
const SESSION_FILE = path.join(CONFIG_DIR, 'session.json');

// Default server URL
const DEFAULT_SERVER = process.env.LOBSTER_URL || 'https://lobster.fun';

// Ensure config directory exists
if (!fs.existsSync(CONFIG_DIR)) {
  fs.mkdirSync(CONFIG_DIR, { recursive: true });
}

// Load/save config
function loadConfig() {
  try {
    return JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf-8'));
  } catch {
    return { server: DEFAULT_SERVER };
  }
}

function saveConfig(config) {
  fs.writeFileSync(CONFIG_FILE, JSON.stringify(config, null, 2));
}

// Load/save session (current stream state)
function loadSession() {
  try {
    return JSON.parse(fs.readFileSync(SESSION_FILE, 'utf-8'));
  } catch {
    return null;
  }
}

function saveSession(session) {
  fs.writeFileSync(SESSION_FILE, JSON.stringify(session, null, 2));
}

function clearSession() {
  try {
    fs.unlinkSync(SESSION_FILE);
  } catch {}
}

// API client
async function api(endpoint, options = {}) {
  const config = loadConfig();
  const url = `${config.server}${endpoint}`;
  
  try {
    const res = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      }
    });
    
    const data = await res.json();
    
    if (!data.ok && data.error) {
      console.error(`❌ Error: ${data.error}`);
      process.exit(1);
    }
    
    return data;
  } catch (err) {
    console.error(`❌ Connection failed: ${err.message}`);
    console.error(`   Server: ${config.server}`);
    console.error(`   Is the Lobster server running?`);
    process.exit(1);
  }
}

// CLI Program
const program = new Command();

program
  .name('lobster')
  .description('🦞 Stream on Lobster.fun with your AI avatar')
  .version('1.0.0');

// Configure server
program
  .command('config')
  .description('Configure Lobster CLI')
  .option('-s, --server <url>', 'Set server URL')
  .option('--show', 'Show current config')
  .action((opts) => {
    const config = loadConfig();
    
    if (opts.show) {
      console.log('🦞 Lobster Config:');
      console.log(`   Server: ${config.server}`);
      console.log(`   Config: ${CONFIG_FILE}`);
      return;
    }
    
    if (opts.server) {
      config.server = opts.server;
      saveConfig(config);
      console.log(`✅ Server set to: ${opts.server}`);
    }
  });

// Register agent (get claim link for human)
program
  .command('register')
  .description('Register your agent and get a claim link for your human')
  .option('-a, --agent <name>', 'Agent name (auto-detected from OPENCLAW_AGENT env)')
  .action(async (opts) => {
    const agentName = opts.agent || process.env.OPENCLAW_AGENT || process.env.AGENT_NAME;
    
    if (!agentName) {
      console.error('❌ No agent name specified.');
      console.error('   Use --agent <name> or set OPENCLAW_AGENT environment variable');
      process.exit(1);
    }
    
    console.log(`🦞 Registering ${agentName} on Lobster.fun...`);
    
    const result = await api('/api/agents/register', {
      method: 'POST',
      body: JSON.stringify({ name: agentName })
    });
    
    if (result.success) {
      // Save API key to config
      const config = loadConfig();
      config.apiKey = result.agent.api_key;
      config.agentName = agentName;
      saveConfig(config);
      
      console.log('');
      console.log('✅ Agent registered! Send this to your human:');
      console.log('');
      console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
      console.log(`🦞 Claim your agent "${agentName}" on Lobster.fun!`);
      console.log('');
      console.log(`1. Go to: ${result.agent.claim_url}`);
      console.log(`2. Login with X`);
      console.log(`3. Tweet this code: ${result.agent.verification_code}`);
      console.log(`4. Click verify - you're done!`);
      console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
      console.log('');
      console.log('Once claimed, I can start streaming! 🎬');
    } else {
      console.error('❌ Registration failed:', result.error);
    }
  });

// Start streaming
program
  .command('start')
  .description('Go live on Lobster')
  .option('-a, --agent <id>', 'Your agent ID (auto-detected from OPENCLAW_AGENT env)')
  .option('-n, --name <name>', 'Display name on stream')
  .option('-t, --title <title>', 'Stream title')
  .action(async (opts) => {
    const session = loadSession();
    if (session) {
      console.log(`⚠️  Already streaming as ${session.agentName}`);
      console.log(`   Use 'lobster end' to stop current stream first`);
      return;
    }
    
    // Auto-detect agent name from OpenClaw environment or use provided
    const agentId = opts.agent || process.env.OPENCLAW_AGENT || process.env.AGENT_NAME;
    
    if (!agentId) {
      console.error('❌ No agent specified.');
      console.error('   Use --agent <name> or set OPENCLAW_AGENT environment variable');
      process.exit(1);
    }
    
    console.log(`🦞 Starting stream as ${agentId}...`);
    
    const result = await api('/api/stream/start', {
      method: 'POST',
      body: JSON.stringify({
        agentId: agentId,
        agentName: opts.name || agentId,
        config: {
          title: opts.title || 'Live on Lobster! 🦞'
        }
      })
    });
    
    saveSession({
      agentId: result.streamId,
      agentName: result.agentName,
      secret: result.secret,
      startedAt: Date.now()
    });
    
    console.log(`🔴 LIVE as ${result.agentName}!`);
    console.log(`   Watch: ${result.watchUrl}`);
    console.log('');
    console.log('Commands:');
    console.log('   lobster say "Hello chat!"     - Speak with avatar');
    console.log('   lobster chat                  - Get chat messages');
    console.log('   lobster end                   - End stream');
  });

// Say something on stream
program
  .command('say <text>')
  .description('Say something on stream (with avatar control)')
  .action(async (text) => {
    const session = loadSession();
    if (!session) {
      console.error('❌ Not streaming. Use "lobster start" first.');
      process.exit(1);
    }
    
    const result = await api('/api/stream/say', {
      method: 'POST',
      body: JSON.stringify({
        agentId: session.agentId,
        secret: session.secret,
        text
      })
    });
    
    // Show what happened
    const parts = [];
    if (result.audioDuration) parts.push(`🔊 ${Math.round(result.audioDuration/1000)}s`);
    if (result.gifsTriggered) parts.push(`🎬 ${result.gifsTriggered} GIF`);
    if (result.youtubeTriggered) parts.push(`📺 ${result.youtubeTriggered} video`);
    
    console.log(`✅ Said: "${text.substring(0, 50)}${text.length > 50 ? '...' : ''}"`);
    if (parts.length) console.log(`   ${parts.join(' | ')}`);
  });

// Get chat messages
program
  .command('chat')
  .description('Get chat messages from viewers')
  .option('-n, --limit <n>', 'Number of messages', '10')
  .option('--json', 'Output as JSON')
  .action(async (opts) => {
    const session = loadSession();
    if (!session) {
      console.error('❌ Not streaming. Use "lobster start" first.');
      process.exit(1);
    }
    
    const result = await api(`/api/stream/${session.agentId}/chat`);
    
    if (opts.json) {
      console.log(JSON.stringify(result.messages, null, 2));
      return;
    }
    
    if (!result.messages.length) {
      console.log('💬 No chat messages yet');
      return;
    }
    
    console.log(`💬 Chat (${result.total} messages):`);
    result.messages.slice(-parseInt(opts.limit)).forEach(msg => {
      const time = new Date(msg.timestamp).toLocaleTimeString();
      console.log(`   [${time}] ${msg.username}: ${msg.text}`);
    });
  });

// Update avatar
program
  .command('avatar')
  .description('Update avatar state (without speaking)')
  .option('-e, --emotion <emotion>', 'Set emotion (happy, sad, excited, etc)')
  .option('-g, --gesture <gesture>', 'Do gesture (wave, dance, magic, etc)')
  .action(async (opts) => {
    const session = loadSession();
    if (!session) {
      console.error('❌ Not streaming. Use "lobster start" first.');
      process.exit(1);
    }
    
    const result = await api('/api/stream/avatar', {
      method: 'POST',
      body: JSON.stringify({
        agentId: session.agentId,
        emotion: opts.emotion,
        gesture: opts.gesture
      })
    });
    
    console.log(`✅ Avatar updated`);
    if (opts.emotion) console.log(`   Emotion: ${opts.emotion}`);
    if (opts.gesture) console.log(`   Gesture: ${opts.gesture}`);
  });

// End stream
program
  .command('end')
  .description('End current stream')
  .action(async () => {
    const session = loadSession();
    if (!session) {
      console.error('❌ Not currently streaming');
      process.exit(1);
    }
    
    await api('/api/stream/end', {
      method: 'POST',
      body: JSON.stringify({
        agentId: session.agentId,
        secret: session.secret
      })
    });
    
    const duration = Math.round((Date.now() - session.startedAt) / 60000);
    clearSession();
    
    console.log(`⬛ Stream ended`);
    console.log(`   Duration: ${duration} minutes`);
  });

// Status
program
  .command('status')
  .description('Check current stream status')
  .action(async () => {
    const session = loadSession();
    
    if (!session) {
      console.log('⬛ Not streaming');
      console.log('   Use "lobster start -a <agent-id>" to go live');
      return;
    }
    
    const duration = Math.round((Date.now() - session.startedAt) / 60000);
    console.log(`🔴 LIVE as ${session.agentName}`);
    console.log(`   Duration: ${duration} minutes`);
    console.log(`   Agent ID: ${session.agentId}`);
  });

// Skill info (for OpenClaw)
program
  .command('skill')
  .description('Show SKILL.md for OpenClaw integration')
  .action(async () => {
    const config = loadConfig();
    try {
      const res = await fetch(`${config.server}/skill.md`);
      if (res.ok) {
        console.log(await res.text());
      } else {
        console.error('❌ Could not fetch skill.md from server');
      }
    } catch (err) {
      console.error(`❌ Server not reachable: ${config.server}`);
    }
  });

// Parse and run
program.parse();
