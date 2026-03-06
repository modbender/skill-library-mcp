#!/usr/bin/env node
/**
 * RentAPerson Webhook Bridge - SIMPLIFIED
 * 
 * What it does:
 * 1. Receives webhook from RentAPerson
 * 2. Adds API key to the message
 * 3. Forwards to OpenClaw
 * 4. Returns OpenClaw's response
 * 
 * That's it. No complex session management.
 */

const http = require('http');
const fs = require('fs');
const path = require('path');

// Load credentials
const credPath = path.join(__dirname, '..', 'rentaperson-agent.json');
let credentials = {};

if (fs.existsSync(credPath)) {
  try {
    credentials = JSON.parse(fs.readFileSync(credPath, 'utf8'));
  } catch (e) {
    console.error('[bridge] Failed to load credentials:', e.message);
    process.exit(1);
  }
}

const API_KEY = credentials.apiKey || process.env.RENTAPERSON_API_KEY;
const AGENT_ID = credentials.agentId || process.env.RENTAPERSON_AGENT_ID;
const AGENT_NAME = credentials.agentName || process.env.RENTAPERSON_AGENT_NAME;
// Prefer apiBase from webhook payload (so dev.rentaperson.ai sends correct origin); fallback to credentials/env
const DEFAULT_API_BASE = credentials.apiBase || process.env.RENTAPERSON_API_BASE || 'https://rentaperson.ai';
const OPENCLAW_URL = process.env.OPENCLAW_URL || 'http://127.0.0.1:18789';
const OPENCLAW_TOKEN = credentials.openclawToken || process.env.OPENCLAW_TOKEN || '';
const BRIDGE_PORT = parseInt(process.env.BRIDGE_PORT || '3001', 10);
// If main session has RENTAPERSON_API_KEY in env (set during setup), set INJECT_API_KEY=false to skip injection
const INJECT_API_KEY = process.env.INJECT_API_KEY !== 'false' && credentials.injectApiKey !== false;

if (!API_KEY) {
  console.error('[bridge] ERROR: RENTAPERSON_API_KEY required');
  console.error('[bridge] Set it in rentaperson-agent.json or environment variable');
  process.exit(1);
}

console.log(`[bridge] Starting...`);
console.log(`[bridge] Default API Base: ${DEFAULT_API_BASE}`);
console.log(`[bridge] OpenClaw: ${OPENCLAW_URL}`);
console.log(`[bridge] Agent: ${AGENT_NAME || AGENT_ID || 'unknown'}`);
console.log(`[bridge] API key injection: ${INJECT_API_KEY ? 'ENABLED' : 'DISABLED'} (set INJECT_API_KEY=false if main session has key in env)`);
if (!credentials.mainSessionKey) {
  console.log(`[bridge] Note: mainSessionKey not in credentials; will use agent:main:main. Re-run setup to set main session.`);
}

/**
 * Build the message that the MAIN session will process (full webhook context + optional API key).
 * This is what the webhook session forwards via sessions_send.
 * 
 * If the main session has RENTAPERSON_API_KEY in env (set during setup), you can skip key injection
 * by setting INJECT_API_KEY=false or injectApiKey: false in credentials.
 */
function buildMessageForMainSession(payload) {
  const event = payload.event || 'unknown';
  const apiBase = payload.apiBase && payload.apiBase.startsWith('http') ? payload.apiBase.replace(/\/+$/, '') : DEFAULT_API_BASE;
  const skillUrl = `${apiBase}/skill.md`;

  let task;
  if (event === 'message.received') {
    const convId = payload.conversationId || '';
    const userId = payload.humanId || 'user';
    const content = payload.contentPreview || '';
    // Bridge only forwards message data. Agent (with AI) replies or creates calendar event per skill.
    task = `[RentAPerson] New message — reply or create calendar event per skill.

**Message data:**
- Conversation ID: ${convId}
- From: ${userId}
- Content preview: "${content}"

**Your task:** Read the full thread (GET ${apiBase}/api/conversations/${convId}/messages?limit=100), then reply or—if they provide availability/time—create a calendar event and set bounty in progress. See the skill for the full workflow.

**API:** GET ${apiBase}/api/conversations/${convId}/messages?limit=100 | GET ${apiBase}/api/conversations/${convId} | POST ${apiBase}/api/calendar/events | POST ${apiBase}/api/conversations/${convId}/messages`;
  } else if (event === 'application.received') {
    const bountyId = payload.bountyId || '';
    const appId = payload.applicationId || '';
    const title = payload.bountyTitle || 'Bounty';
    const name = payload.humanName || 'Someone';
    const humanId = payload.humanId || '';
    const coverPreview = payload.coverLetterPreview || '';
    const proposedPrice = payload.proposedPrice;
    // Bridge only forwards application data. Agent (with AI) evaluates and decides.
    task = `[RentAPerson] New application — evaluate and act.

**Application data (use this to evaluate):**
- Bounty: "${title}" (bountyId: ${bountyId})
- Applicant: ${name} (humanId: ${humanId})
- Application ID: ${appId}
- Cover letter: ${coverPreview}${proposedPrice != null && proposedPrice !== '' ? `\n- Proposed price: $${proposedPrice}` : ''}

**Your task:** Using the application data above, evaluate the application (determine confidence: HIGH / MEDIUM / LOW) and either accept or message for more details. See the skill for the full workflow (check existing conversation, create if needed, send message, or PATCH to accept).

**API endpoints:**
- Check existing conversation: GET ${apiBase}/api/conversations?humanId=${humanId}&agentId=<your-agentId>&bountyId=${bountyId}
- Create conversation: POST ${apiBase}/api/conversations
- Send message: POST ${apiBase}/api/conversations/{conversationId}/messages
- View applications: GET ${apiBase}/api/bounties/${bountyId}/applications
- Accept: PATCH ${apiBase}/api/bounties/${bountyId}/applications/${appId} with {"status": "accepted"}`;
  } else {
    task = `Webhook event: ${event}\n\nPayload: ${JSON.stringify(payload, null, 2)}`;
  }

  // Only inject API key if INJECT_API_KEY is true (default) or not explicitly disabled
  // If main session has RENTAPERSON_API_KEY in env, set INJECT_API_KEY=false to skip injection
  const apiKeyNote = INJECT_API_KEY && API_KEY
    ? `\n\n🔑 API KEY: ${API_KEY}\nUse this header: X-API-Key: ${API_KEY}`
    : '';

  return `[RentAPerson agent. API docs: ${skillUrl}]

${task}${apiKeyNote}`;
}

/**
 * Build the message sent TO the webhook session: instruct it to forward to main via sessions_send.
 * Main session has the full skill and is where the user interacts; webhook session only forwards.
 */
function buildMessage(payload) {
  const messageForMain = buildMessageForMainSession(payload);
  const mainKey = normalizeSessionKeyForOpenClaw(credentials.mainSessionKey || 'agent:main:main');

  return `You are the RentAPerson webhook receiver. Your ONLY job is to forward this webhook to the main session using sessions_send.

**Do this now:**
1. Call \`sessions_send\` with:
   - \`sessionKey\`: "${mainKey}"
   - \`message\`: (the content below between the --- lines)
   - \`timeoutSeconds\`: 0 (fire-and-forget)
2. Do NOT process the webhook yourself. The main session has the full skill and will process it and reply via the RentAPerson API.

**Message to send to main session:**
---
${messageForMain}
---`;
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

function forwardToOpenClaw(payload, callback) {
  const message = buildMessage(payload);
  
  // Use webhook session key (dedicated session for webhook processing)
  // This session will spawn subagents to process webhooks automatically
  const rawSessionKey = credentials.webhookSessionKey || credentials.sessionKey || 'agent:main:rentaperson';
  // Strip agent:main: prefix - OpenClaw adds it automatically
  const sessionKey = normalizeSessionKeyForOpenClaw(rawSessionKey);
  
  const body = {
    message,
    name: 'RentAPerson',
    sessionKey: sessionKey, // CRITICAL: Use dedicated webhook session (normalized)
    wakeMode: 'now',
    deliver: false, // Don't send to messaging channels
  };
  
  // Try /hooks/rentaperson first if mapping is configured (match.path = rentaperson); else use /hooks/agent
  const client = (OPENCLAW_URL || '').startsWith('https') ? require('https') : http;
  const headers = {
    'Content-Type': 'application/json',
    ...(OPENCLAW_TOKEN && { 'Authorization': `Bearer ${OPENCLAW_TOKEN}` }),
  };

  function post(path, done) {
    const url = new URL(`${OPENCLAW_URL}${path}`);
    const options = {
      method: 'POST',
      hostname: url.hostname,
      port: url.port || (url.protocol === 'https:' ? 443 : 80),
      path: url.pathname,
      headers,
    };
    console.log(`[bridge] Forwarding to: ${OPENCLAW_URL}${path}`);
    console.log(`[bridge] Using sessionKey: "${sessionKey}"`);
    const req = client.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        console.log(`[bridge] OpenClaw → ${res.statusCode}`);
        if (data) console.log(`[bridge] Response:`, data.substring(0, 200));
        if (res.statusCode === 404 && path === '/hooks/rentaperson') {
          console.log(`[bridge] /hooks/rentaperson not mapped; using /hooks/agent`);
          post('/hooks/agent', done);
        } else {
          done(null, { statusCode: res.statusCode, body: data });
        }
      });
    });
    req.on('error', (err) => {
      console.error(`[bridge] OpenClaw request failed:`, err.message);
      done(err);
    });
    req.write(JSON.stringify(body));
    req.end();
  }

  post('/hooks/rentaperson', callback);
}

const server = http.createServer((req, res) => {
  if (req.method === 'OPTIONS') {
    res.writeHead(200, {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST',
      'Access-Control-Allow-Headers': 'Content-Type',
    });
    res.end();
    return;
  }
  
  if (req.method !== 'POST') {
    res.writeHead(405, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'Method not allowed' }));
    return;
  }
  
  let body = '';
  req.on('data', chunk => body += chunk);
  req.on('end', () => {
    try {
      const payload = JSON.parse(body);
      console.log(`[bridge] ← RentAPerson: ${payload.event || 'unknown event'}`);
      
      forwardToOpenClaw(payload, (err, result) => {
        if (err) {
          console.error('[bridge] Error:', err);
          res.writeHead(502, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ error: 'Failed to forward', message: err.message }));
          return;
        }
        const statusCode = result.statusCode || 200;
        const body = result.body != null && result.body !== '' ? result.body : '{}';
        res.writeHead(statusCode, { 'Content-Type': 'application/json' });
        res.end(body);
      });
    } catch (e) {
      console.error('[bridge] Parse error:', e);
      res.writeHead(400, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'Invalid JSON', message: e.message }));
    }
  });
});

server.listen(BRIDGE_PORT, () => {
  console.log(`[bridge] ✅ Listening on http://127.0.0.1:${BRIDGE_PORT}`);
  console.log(`[bridge] Ready to receive webhooks from RentAPerson`);
});

process.on('SIGTERM', () => {
  console.log('[bridge] Shutting down...');
  server.close(() => process.exit(0));
});

process.on('SIGINT', () => {
  console.log('[bridge] Shutting down...');
  server.close(() => process.exit(0));
});
