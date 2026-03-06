#!/usr/bin/env node
/**
 * Fetch real IDs from RentAPerson (dev or prod) for local webhook testing.
 * Uses rentaperson-agent.json or RENTAPERSON_API_KEY + RENTAPERSON_AGENT_ID.
 *
 * Usage:
 *   node fetch-test-ids.js              # use apiBase from credentials (or prod)
 *   node fetch-test-ids.js --dev        # force https://dev.rentaperson.ai
 *   node fetch-test-ids.js --prod       # force https://rentaperson.ai
 */

const fs = require('fs');
const path = require('path');

const skillDir = path.resolve(__dirname, '..');
const credPath = path.join(skillDir, 'rentaperson-agent.json');
let credentials = {};
if (fs.existsSync(credPath)) {
  try {
    credentials = JSON.parse(fs.readFileSync(credPath, 'utf8'));
  } catch (e) {
    console.error('Failed to load credentials:', e.message);
    process.exit(1);
  }
}

const apiKey = credentials.apiKey || process.env.RENTAPERSON_API_KEY;
const agentId = credentials.agentId || process.env.RENTAPERSON_AGENT_ID;

const arg = process.argv[2];
let apiBase = credentials.apiBase || process.env.RENTAPERSON_API_BASE || 'https://rentaperson.ai';
if (arg === '--dev') apiBase = 'https://dev.rentaperson.ai';
else if (arg === '--prod') apiBase = 'https://rentaperson.ai';

if (!apiKey) {
  console.error('Missing API key. Set in rentaperson-agent.json or RENTAPERSON_API_KEY');
  process.exit(1);
}

const headers = {
  'Content-Type': 'application/json',
  'X-API-Key': apiKey,
};

async function get(url) {
  const res = await fetch(url, { headers });
  const text = await res.text();
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}: ${text.slice(0, 200)}`);
  return text ? JSON.parse(text) : null;
}

async function main() {
  console.log('Fetching from:', apiBase);
  console.log('Agent ID (from credentials):', agentId || '(will use from /agents/me)');
  console.log('');

  const me = await get(`${apiBase}/api/agents/me`).catch((e) => {
    console.error('GET /api/agents/me failed:', e.message);
    process.exit(1);
  });
  const effectiveAgentId = me?.agentId || agentId;
  if (!effectiveAgentId) {
    console.error('Could not determine agentId');
    process.exit(1);
  }
  console.log('--- Agent ---');
  console.log('agentId:', effectiveAgentId);
  console.log('webhookUrl:', me?.webhookUrl ?? '(not set)');
  console.log('');

  let conversations = [];
  try {
    conversations = await get(
      `${apiBase}/api/conversations?agentId=${encodeURIComponent(effectiveAgentId)}&limit=10`
    );
  } catch (e) {
    console.log('Conversations: (failed)', e.message);
  }
  if (Array.isArray(conversations) && conversations.length > 0) {
    console.log('--- Conversations (use for message.received test) ---');
    conversations.slice(0, 5).forEach((c, i) => {
      console.log(`  [${i + 1}] conversationId: ${c.id}`);
      console.log(`      humanId: ${c.humanId}`);
      console.log(`      humanName: ${c.humanName || '(n/a)'}`);
    });
    const first = conversations[0];
    console.log('');
    console.log('Example curl (bridge) with first conversation:');
    console.log(
      `curl -X POST http://127.0.0.1:3001 -H "Content-Type: application/json" -d '${JSON.stringify({
        event: 'message.received',
        agentId: effectiveAgentId,
        conversationId: first.id,
        humanId: first.humanId,
        humanName: first.humanName || 'Human',
        contentPreview: 'Test message for local webhook',
        createdAt: new Date().toISOString(),
      })}'`
    );
  } else {
    console.log('--- Conversations ---');
    console.log('  (none found; start a conversation on the site first)');
  }
  console.log('');

  let bounties = [];
  try {
    bounties = await get(
      `${apiBase}/api/bounties?agentId=${encodeURIComponent(effectiveAgentId)}&limit=10`
    );
  } catch (e) {
    console.log('Bounties: (failed)', e.message);
  }
  if (Array.isArray(bounties) && bounties.length > 0) {
    console.log('--- Bounties ---');
    for (const b of bounties.slice(0, 5)) {
      console.log(`  bountyId: ${b.id}  title: ${(b.title || '').slice(0, 40)}`);
      let apps = [];
      try {
        apps = await get(`${apiBase}/api/bounties/${b.id}/applications?limit=5`);
      } catch (_) {}
      if (Array.isArray(apps) && apps.length > 0) {
        apps.forEach((a) => {
          console.log(`    applicationId: ${a.id}  humanId: ${a.humanId}  status: ${a.status}`);
        });
      }
    }
    const withApp = bounties.find((b) => true);
    if (withApp) {
      let apps = [];
      try {
        apps = await get(`${apiBase}/api/bounties/${withApp.id}/applications?limit=1`);
      } catch (_) {}
      if (Array.isArray(apps) && apps.length > 0) {
        const app = apps[0];
        console.log('');
        console.log('Example curl (bridge) for application.received:');
        console.log(
          `curl -X POST http://127.0.0.1:3001 -H "Content-Type: application/json" -d '${JSON.stringify({
            event: 'application.received',
            agentId: effectiveAgentId,
            bountyId: withApp.id,
            bountyTitle: withApp.title,
            applicationId: app.id,
            humanId: app.humanId,
            humanName: app.humanName || 'Applicant',
            coverLetterPreview: (app.coverLetter || '').slice(0, 100),
            createdAt: new Date().toISOString(),
          })}'`
        );
      }
    }
  } else {
    console.log('--- Bounties ---');
    console.log('  (none found)');
  }
  console.log('');
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
