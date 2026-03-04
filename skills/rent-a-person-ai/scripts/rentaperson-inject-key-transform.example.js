/**
 * OpenClaw webhook transform: inject RENTAPERSON_API_KEY from config into message.
 * Supports multiple possible OpenClaw transform API signatures.
 *
 * Copy this to your OpenClaw hooks.transformsDir and wire your mapping
 * (e.g. POST /hooks/rentaperson) to use it.
 *
 * Input body: { message, name, sessionKey, wakeMode, deliver, ... }
 * Returns: same body with message augmented with one line containing key/id/name.
 */

const fs = require('fs');
const path = require('path');

function getConfig() {
  // Try to load config from default location
  const configPath =
    process.env.OPENCLAW_CONFIG ||
    path.join(process.env.HOME || process.env.USERPROFILE || '', '.openclaw', 'openclaw.json');
  try {
    const raw = fs.readFileSync(configPath, 'utf8');
    return JSON.parse(raw);
  } catch (e) {
    if (e.code !== 'ENOENT') {
      console.error('[rentaperson-transform] Error loading config:', e.message);
    }
    return {};
  }
}

function injectKey(body, config) {
  const env = config?.skills?.entries?.['rent-a-person-ai']?.env || {};
  const key = env.RENTAPERSON_API_KEY;
  const agentId = env.RENTAPERSON_AGENT_ID || '';
  const agentName = env.RENTAPERSON_AGENT_NAME || '';

  if (!key) {
    console.warn('[rentaperson-transform] RENTAPERSON_API_KEY not found in config');
    return body;
  }

  const inject = `[RENTAPERSON] Use for all API calls: X-API-Key: ${key}. AgentId: ${agentId}. AgentName: ${agentName}.`;
  const message = typeof body.message === 'string' ? body.message + '\n\n' + inject : inject;

  return { ...body, message };
}

// Support multiple possible API signatures:
// 1. transform(body, config)
// 2. transform(payload, context) where context.config exists
// 3. transform(payload) - load config from file
function transform(payload, context) {
  let body = payload;
  let config = context;

  // If context has config property, use it
  if (context && typeof context === 'object' && context.config) {
    config = context.config;
  }

  // If config is not provided or doesn't have skills, load from file
  if (!config || !config.skills) {
    config = getConfig();
  }

  return injectKey(body, config);
}

module.exports = transform;
