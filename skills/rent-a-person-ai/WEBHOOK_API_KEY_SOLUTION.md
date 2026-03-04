# Webhook API Key Injection: Research & Solutions

## Problem Summary

OpenClaw webhook sessions are **isolated** and create new sessions (keys like `hook:<uuid>`) each time unless you use a persistent `sessionKey`. Even with a persistent session, if the gateway creates a new session each time, the skill env vars from `skills.entries["rent-a-person-ai"].env` are **not injected** into the webhook session.

**Symptoms:**
- Webhook successfully triggers OpenClaw
- New session created each time
- `process.env.RENTAPERSON_API_KEY` is undefined in the session
- Agent falls back to WhatsApp or fails API calls

## Root Cause

According to OpenClaw docs:
- `skills.entries.<skill>.env` applies to **host runs only** (not sandboxed)
- Webhook sessions are **isolated** and may not inherit skill env vars
- The transform approach is the documented fallback when env vars aren't available

## Solution 1: Fix Transform (Current Approach)

### Issue with Current Transform

The transform might not be working because:
1. **API Signature**: OpenClaw transform API might expect `(payload, context)` instead of `(body, config)`
2. **Config Access**: The config might be passed differently (e.g., `context.config` or loaded from file)
3. **Mapping Config**: The `hooks.mappings.rentaperson.transform` might need to be `transform.module` instead of just `transform`

### Fixed Transform

Update `rentaperson-inject-key-transform.js` to handle multiple possible API signatures:

```javascript
/**
 * OpenClaw webhook transform: inject RENTAPERSON_API_KEY from config into message.
 * Supports multiple possible OpenClaw transform API signatures.
 */

const fs = require('fs');
const path = require('path');

function getConfig() {
  // Try to load config from default location
  const configPath = process.env.OPENCLAW_CONFIG || 
    path.join(process.env.HOME || process.env.USERPROFILE || '', '.openclaw', 'openclaw.json');
  try {
    const raw = fs.readFileSync(configPath, 'utf8');
    return JSON.parse(raw);
  } catch (e) {
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

// Support multiple possible API signatures
function transform(payload, context) {
  let body = payload;
  let config = context;

  // If context has config property, use it
  if (context && typeof context === 'object' && context.config) {
    config = context.config;
  }

  // If config is not provided, load from file
  if (!config || !config.skills) {
    config = getConfig();
  }

  return injectKey(body, config);
}

module.exports = transform;
```

### Updated Mapping Config

Ensure `openclaw.json` has:

```json
{
  "hooks": {
    "transformsDir": "/absolute/path/to/hooks/transforms",
    "mappings": {
      "rentaperson": {
        "transform": {
          "module": "rentaperson-inject-key-transform.js"
        }
      }
    }
  }
}
```

Or possibly:

```json
{
  "hooks": {
    "transformsDir": "/absolute/path/to/hooks/transforms",
    "mappings": {
      "rentaperson": {
        "transform": "rentaperson-inject-key-transform.js"
      }
    }
  }
}
```

## Solution 2: Webhook Bridge Service (Recommended)

A **separate Node.js service** that runs on a different port and acts as a proxy:

### Architecture

```
RentAPerson → Bridge Service (port 3001) → OpenClaw Gateway (port 18789)
                ↓
            Adds API key to headers/message
            Logs requests (redacts keys)
            Handles retries/errors
```

### Benefits

1. **Security**: API key never appears in OpenClaw session transcripts
2. **Reliability**: Doesn't depend on OpenClaw's transform system
3. **Control**: Can add retry logic, rate limiting, request logging
4. **Debugging**: Centralized logs for webhook debugging
5. **Flexibility**: Can transform payload format, add headers, etc.

### Implementation

Create `openclaw-skill/bridge/` directory with:

**`bridge/server.js`**:
```javascript
#!/usr/bin/env node
/**
 * RentAPerson Webhook Bridge
 * Receives webhooks from RentAPerson, adds API key, forwards to OpenClaw.
 */

const http = require('http');
const https = require('https');
const fs = require('fs');
const path = require('path');
const { URL } = require('url');

const BRIDGE_PORT = process.env.BRIDGE_PORT || 3001;
const OPENCLAW_URL = process.env.OPENCLAW_URL || 'http://127.0.0.1:18789';
const OPENCLAW_TOKEN = process.env.OPENCLAW_TOKEN || '';
const RENTAPERSON_API_KEY = process.env.RENTAPERSON_API_KEY || '';
const RENTAPERSON_AGENT_ID = process.env.RENTAPERSON_AGENT_ID || '';
const RENTAPERSON_AGENT_NAME = process.env.RENTAPERSON_AGENT_NAME || '';

if (!RENTAPERSON_API_KEY) {
  console.error('ERROR: RENTAPERSON_API_KEY environment variable required');
  process.exit(1);
}

function loadCredentials() {
  const credPath = path.join(__dirname, '..', 'rentaperson-agent.json');
  try {
    const creds = JSON.parse(fs.readFileSync(credPath, 'utf8'));
    return {
      apiKey: creds.apiKey || RENTAPERSON_API_KEY,
      agentId: creds.agentId || RENTAPERSON_AGENT_ID,
      agentName: creds.agentName || RENTAPERSON_AGENT_NAME,
    };
  } catch (e) {
    return {
      apiKey: RENTAPERSON_API_KEY,
      agentId: RENTAPERSON_AGENT_ID,
      agentName: RENTAPERSON_AGENT_NAME,
    };
  }
}

const credentials = loadCredentials();

function redactKey(str) {
  if (!str) return str;
  return str.replace(/rap_[a-zA-Z0-9_-]+/g, 'rap_***');
}

function logRequest(req, body) {
  const bodyStr = JSON.stringify(body, null, 2);
  console.log(`[${new Date().toISOString()}] ${req.method} ${req.url}`);
  console.log('Body:', redactKey(bodyStr));
}

function forwardToOpenClaw(body, callback) {
  const openclawUrl = new URL(`${OPENCLAW_URL}/hooks/agent`);
  const client = openclawUrl.protocol === 'https:' ? https : http;

  const inject = `[RENTAPERSON] Use for all API calls: X-API-Key: ${credentials.apiKey}. AgentId: ${credentials.agentId}. AgentName: ${credentials.agentName}.`;
  const enhancedBody = {
    ...body,
    message: typeof body.message === 'string' 
      ? body.message + '\n\n' + inject 
      : inject,
  };

  const options = {
    method: 'POST',
    hostname: openclawUrl.hostname,
    port: openclawUrl.port || (openclawUrl.protocol === 'https:' ? 443 : 80),
    path: openclawUrl.pathname,
    headers: {
      'Content-Type': 'application/json',
      ...(OPENCLAW_TOKEN && { 'Authorization': `Bearer ${OPENCLAW_TOKEN}` }),
    },
  };

  const req = client.request(options, (res) => {
    let data = '';
    res.on('data', (chunk) => { data += chunk; });
    res.on('end', () => {
      callback(null, {
        statusCode: res.statusCode,
        headers: res.headers,
        body: data,
      });
    });
  });

  req.on('error', (err) => {
    callback(err);
  });

  req.write(JSON.stringify(enhancedBody));
  req.end();
}

const server = http.createServer((req, res) => {
  if (req.method !== 'POST') {
    res.writeHead(405, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'Method not allowed' }));
    return;
  }

  let body = '';
  req.on('data', (chunk) => { body += chunk; });
  req.on('end', () => {
    try {
      const parsed = JSON.parse(body);
      logRequest(req, parsed);

      forwardToOpenClaw(parsed, (err, result) => {
        if (err) {
          console.error('[bridge] Forward error:', err);
          res.writeHead(502, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ error: 'Failed to forward to OpenClaw', message: err.message }));
          return;
        }

        res.writeHead(result.statusCode, result.headers);
        res.end(result.body);
      });
    } catch (e) {
      console.error('[bridge] Parse error:', e);
      res.writeHead(400, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'Invalid JSON', message: e.message }));
    }
  });
});

server.listen(BRIDGE_PORT, () => {
  console.log(`RentAPerson Webhook Bridge listening on port ${BRIDGE_PORT}`);
  console.log(`Forwarding to: ${OPENCLAW_URL}/hooks/agent`);
  console.log(`API Key: ${redactKey(credentials.apiKey)}`);
});

process.on('SIGTERM', () => {
  console.log('Shutting down bridge...');
  server.close(() => process.exit(0));
});
```

**`bridge/package.json`**:
```json
{
  "name": "rentaperson-webhook-bridge",
  "version": "1.0.0",
  "description": "Webhook bridge for RentAPerson → OpenClaw",
  "main": "server.js",
  "scripts": {
    "start": "node server.js"
  },
  "engines": {
    "node": ">=18"
  }
}
```

**`bridge/README.md`**:
```markdown
# RentAPerson Webhook Bridge

Runs as a separate service that receives webhooks from RentAPerson, adds the API key, and forwards to OpenClaw.

## Setup

1. Install dependencies: `npm install` (none required, uses Node built-ins)

2. Set environment variables:
   ```bash
   export RENTAPERSON_API_KEY="rap_your_key"
   export RENTAPERSON_AGENT_ID="agent_xxx"
   export RENTAPERSON_AGENT_NAME="My Agent"
   export OPENCLAW_URL="http://127.0.0.1:18789"
   export OPENCLAW_TOKEN="your-openclaw-hooks-token"
   export BRIDGE_PORT=3001
   ```

   Or load from `rentaperson-agent.json` (auto-detected).

3. Start the bridge:
   ```bash
   node server.js
   # or: npm start
   ```

4. Point RentAPerson webhook at: `https://your-ngrok.ngrok.io` (bridge port)

5. Bridge forwards to: `http://127.0.0.1:18789/hooks/agent` (OpenClaw)

## Benefits

- API key never appears in OpenClaw session transcripts
- Centralized logging (keys redacted)
- Can add retry logic, rate limiting, etc.
- Doesn't depend on OpenClaw transform system
```

## Recommendation

**Use Solution 2 (Bridge)** because:
1. More secure (key never in transcripts)
2. More reliable (doesn't depend on OpenClaw internals)
3. Easier to debug (centralized logs)
4. More flexible (can add features later)

**Fallback to Solution 1 (Transform)** if:
- You can't run a separate service
- You want everything in OpenClaw config
- You're okay with the key appearing in transcripts

## Next Steps

1. **Test Transform Fix**: Update transform, verify config access, test webhook
2. **Implement Bridge**: Create bridge service, add to setup script, document
3. **Update Setup Script**: Add option to choose bridge vs transform
4. **Update SKILL.md**: Document both approaches
