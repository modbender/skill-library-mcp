/**
 * SealVera OpenClaw interceptor
 * Drop-in patch for OpenAI / Anthropic / OpenRouter clients used by OpenClaw agents.
 * Require this file at the top of your agent entry point, or let the skill auto-load it.
 *
 * Usage:
 *   require('./scripts/intercept');   // patches global SDK instances
 *
 * Or via env auto-load (NODE_OPTIONS):
 *   NODE_OPTIONS="--require /path/to/intercept.js" node agent.js
 */
'use strict';

const fs   = require('fs');
const path = require('path');

// Load config — .sealvera.json or env
let config = {};
const configPath = path.join(process.cwd(), '.sealvera.json');
if (fs.existsSync(configPath)) {
  try { config = JSON.parse(fs.readFileSync(configPath, 'utf8')); } catch(_) {}
}

const ENDPOINT      = process.env.SEALVERA_ENDPOINT || config.endpoint || 'https://app.sealvera.com';
const API_KEY       = process.env.SEALVERA_API_KEY  || '';
const AGENT         = process.env.SEALVERA_AGENT    || config.agent    || 'openclaw-agent';
const AUTO_REASONING = process.env.SEALVERA_AUTO_REASONING !== 'false' && config.autoReasoning !== false;

if (!API_KEY) {
  // Silent — don't crash the agent, just skip logging
  return;
}

let SealVera;
try {
  SealVera = require('sealvera');
  SealVera.init({ endpoint: ENDPOINT, apiKey: API_KEY, autoReasoning: AUTO_REASONING });
} catch(e) {
  // SDK not installed — skip silently
  return;
}

// Patch OpenAI if loaded
try {
  const openaiMod = require.cache[require.resolve('openai')];
  if (openaiMod) {
    const { OpenAI } = openaiMod.exports;
    if (OpenAI && !OpenAI.__sealvera_patched) {
      const orig = OpenAI.prototype.constructor;
      // Wrap createClient on any instantiated OpenAI instance
      const origCreate = OpenAI.prototype?.chat?.completions?.create;
      if (origCreate) {
        SealVera.patchOpenAI(new OpenAI(), { agent: AGENT });
      }
      OpenAI.__sealvera_patched = true;
    }
  }
} catch(_) {}

// Patch Anthropic if loaded
try {
  const anthropicMod = require.cache[require.resolve('@anthropic-ai/sdk')];
  if (anthropicMod) {
    const Anthropic = anthropicMod.exports?.default || anthropicMod.exports?.Anthropic;
    if (Anthropic && !Anthropic.__sealvera_patched) {
      SealVera.patchAnthropic(new Anthropic(), { agent: AGENT });
      Anthropic.__sealvera_patched = true;
    }
  }
} catch(_) {}

// Export for manual use
module.exports = { SealVera, AGENT, ENDPOINT };
