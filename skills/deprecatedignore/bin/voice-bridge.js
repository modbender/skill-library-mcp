#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const readline = require('readline');
const { RelayClient } = require('../lib/relay-client');
const { AgentBridge } = require('../lib/agent-bridge');

// --- Config ---

const CONFIG_PATH = path.join(require('os').homedir(), '.hotbutter');

function loadConfig() {
  try {
    return JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
  } catch {
    return null;
  }
}

function saveConfig(config) {
  fs.writeFileSync(CONFIG_PATH, JSON.stringify(config, null, 2) + '\n');
}

function ask(question) {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  return new Promise((resolve) => {
    rl.question(question, (answer) => {
      rl.close();
      resolve(answer.trim());
    });
  });
}

// --- Parse args ---

const args = process.argv.slice(2);
const command = args[0];

function getFlag(name, fallback) {
  const idx = args.indexOf(name);
  if (idx === -1 || idx + 1 >= args.length) return fallback;
  return args[idx + 1];
}

if (command !== 'start') {
  console.log('Usage: voice-bridge start [--relay-url <url>] [--agent-name <name>]');
  process.exit(0);
}

const relayUrl = getFlag('--relay-url', 'wss://hotbutter.ai');
const agentName = getFlag('--agent-name', 'Agent');

// --- First-run setup ---

async function firstRunSetup() {
  let config = loadConfig();
  if (config) return config;

  console.log('');
  console.log('  Welcome to Hotbutter Voice!');
  console.log('');
  console.log('  Hotbutter gives your AI agent a voice interface.');
  console.log('  It connects your terminal agent to a browser-based');
  console.log('  voice chat at https://hotbutter.ai');
  console.log('');
  console.log('  Skill name: hotbutter');
  console.log('');

  const email = await ask('  Email (optional, press Enter to skip): ');

  config = { email: email || null, createdAt: new Date().toISOString() };
  saveConfig(config);

  console.log('');
  if (email) {
    console.log(`  Saved to ~/.hotbutter. Welcome, ${email}!`);
  } else {
    console.log('  Saved to ~/.hotbutter. You can add your email later.');
  }
  console.log('');

  return config;
}

// --- Start ---

async function main() {
  await firstRunSetup();

  const relay = new RelayClient({ relayUrl, agentName });
  const bridge = new AgentBridge();

  console.log(`[voice-bridge] Connecting to relay: ${relayUrl}`);

  relay.on('connected', () => {
    console.log('[voice-bridge] Connected to relay, waiting for pairing code...');
  });

  relay.on('code', (code) => {
    const appUrl = `https://hotbutter.ai/app?code=${code}`;
    console.log('');
    console.log('  ┌──────────────────────────────────────────────┐');
    console.log('  │                                                │');
    console.log(`  │  Pairing code:  ${code}                          │`);
    console.log('  │                                                │');
    console.log(`  │  Open in browser to start talking:             │`);
    console.log(`  │  ${appUrl}  │`);
    console.log('  │                                                │');
    console.log('  └──────────────────────────────────────────────┘');
    console.log('');
  });

  relay.on('paired', ({ sessionId }) => {
    console.log(`[voice-bridge] Client paired! Session: ${sessionId}`);
  });

  relay.on('message', async ({ sessionId, text }) => {
    console.log(`[voice-bridge] User said: "${text}"`);
    relay.sendTyping(true);

    try {
      const response = await bridge.sendMessage(sessionId, text);
      console.log(`[voice-bridge] Agent response: "${response}"`);
      relay.sendMessage(response);
      relay.sendTyping(false);
    } catch (err) {
      console.error(`[voice-bridge] Error sending to agent:`, err.message);
      relay.sendMessage('Sorry, I encountered an error processing your message.');
      relay.sendTyping(false);
    }
  });

  relay.on('client-disconnected', ({ sessionId }) => {
    console.log(`[voice-bridge] Client disconnected (session: ${sessionId})`);
  });

  relay.on('disconnected', () => {
    console.log('[voice-bridge] Disconnected from relay');
  });

  relay.on('reconnecting', ({ attempt, delay }) => {
    console.log(`[voice-bridge] Reconnecting (attempt ${attempt}, delay ${delay}ms)...`);
  });

  relay.on('error', ({ error }) => {
    console.error(`[voice-bridge] Error: ${error}`);
  });

  relay.connect();

  // Graceful shutdown
  process.on('SIGINT', () => {
    console.log('\n[voice-bridge] Shutting down...');
    relay.disconnect();
    process.exit(0);
  });

  process.on('SIGTERM', () => {
    relay.disconnect();
    process.exit(0);
  });
}

main().catch((err) => {
  console.error('[voice-bridge] Fatal error:', err);
  process.exit(1);
});
