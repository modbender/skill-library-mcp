#!/usr/bin/env node
/**
 * subagent-watcher.js
 *
 * Gap 3 backstop: scans completed sub-agent sessions and logs any that
 * are missing from SealVera. Runs as a cron job every few minutes.
 *
 * Strategy:
 *   1. Read sessions.json → find sub-agent sessions completed in the last window
 *   2. Check SealVera for logs matching that session's run window
 *   3. For any session with no matching log → read its transcript → synthesize + log
 *
 * This is a backstop, not the primary enforcement path.
 * Primary path: MANDATORY footer in task prompt.
 * This catches anything that slipped through.
 */
'use strict';

const fs   = require('fs');
const path = require('path');
const os   = require('os');

const SV_KEY      = process.env.SEALVERA_API_KEY || 'sv_5e4735b26826de94931a00d9718dcafd162c01498cd8d3be';
const SV_ENDPOINT = (process.env.SEALVERA_ENDPOINT || 'https://app.sealvera.com').replace(/\/$/, '');
const SESSIONS_DIR = path.join(os.homedir(), '.openclaw', 'agents', 'main', 'sessions');
const SESSIONS_JSON = path.join(SESSIONS_DIR, 'sessions.json');
const STATE_FILE   = path.join(__dirname, '.watcher-state.json');

// How far back to look (ms)
const WINDOW_MS = 10 * 60 * 1000; // 10 minutes

const https = require('https');
const http  = require('http');

function request(urlStr, headers = {}, method = 'GET', body = null) {
  return new Promise((resolve, reject) => {
    const url = new URL(urlStr);
    const mod = url.protocol === 'https:' ? https : http;
    const opts = {
      hostname: url.hostname,
      port: url.port || (url.protocol === 'https:' ? 443 : 80),
      path: url.pathname + (url.search || ''),
      method,
      headers: { 'Content-Type': 'application/json', ...headers },
    };
    const req = mod.request(opts, res => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => {
        try { resolve({ status: res.statusCode, body: JSON.parse(data) }); }
        catch(_) { resolve({ status: res.statusCode, body: {} }); }
      });
    });
    req.on('error', reject);
    if (body) req.write(JSON.stringify(body));
    req.end();
  });
}

// Read already-seen session keys to avoid double-logging
function loadState() {
  try { return JSON.parse(fs.readFileSync(STATE_FILE, 'utf8')); }
  catch(_) { return { seen: [] }; }
}

function saveState(state) {
  // Keep last 500 seen keys
  state.seen = state.seen.slice(-500);
  fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
}

// Extract a useful summary from a sub-agent transcript
function summariseTranscript(transcriptPath) {
  try {
    const lines = fs.readFileSync(transcriptPath, 'utf8').trim().split('\n');
    const messages = lines.map(l => { try { return JSON.parse(l); } catch(_) { return null; } }).filter(Boolean);

    // Find the last assistant text reply
    let lastReply = '';
    let taskText  = '';
    for (const msg of messages) {
      const m = msg.message || {};
      if (m.role === 'user') {
        const parts = Array.isArray(m.content) ? m.content : [{ text: m.content }];
        for (const p of parts) {
          if (p.type === 'text' || typeof p === 'string') {
            taskText = (p.text || p).slice(0, 200);
          }
        }
      }
      if (m.role === 'assistant') {
        const parts = Array.isArray(m.content) ? m.content : [{ text: m.content }];
        for (const p of parts) {
          if (p.type === 'text' && p.text) {
            lastReply = p.text.slice(0, 300);
          }
        }
      }
    }
    return { task: taskText, result: lastReply };
  } catch(e) {
    return { task: 'unknown', result: 'could not read transcript: ' + e.message };
  }
}

async function run() {
  if (!fs.existsSync(SESSIONS_JSON)) {
    console.log('[watcher] sessions.json not found — skipping');
    return;
  }

  const state = loadState();
  const now   = Date.now();
  const cutoff = now - WINDOW_MS;

  let sessions;
  try {
    sessions = JSON.parse(fs.readFileSync(SESSIONS_JSON, 'utf8'));
  } catch(e) {
    console.error('[watcher] Failed to read sessions.json:', e.message);
    return;
  }

  // Find completed sub-agent sessions in the window
  const subagents = Object.entries(sessions)
    .filter(([key]) => key.includes(':subagent:'))
    .filter(([key, val]) => {
      const updatedAt = val.updatedAt || 0;
      return updatedAt >= cutoff && updatedAt <= now;
    })
    .filter(([key]) => !state.seen.includes(key));

  if (subagents.length === 0) {
    console.log('[watcher] No new sub-agent completions in window');
    return;
  }

  console.log(`[watcher] Found ${subagents.length} sub-agent session(s) to check`);

  // Fetch recent SealVera logs to cross-reference
  let recentLogs = [];
  try {
    const { body } = await request(`${SV_ENDPOINT}/api/logs?limit=50`, { 'x-sealvera-key': SV_KEY });
    recentLogs = body.logs || [];
  } catch(e) {
    console.error('[watcher] Failed to fetch SealVera logs:', e.message);
  }

  // Get timestamps of recently logged entries
  const recentLogTimes = new Set(recentLogs.map(l => l.timestamp ? new Date(l.timestamp).getTime() : 0));

  for (const [sessionKey, sessionData] of subagents) {
    state.seen.push(sessionKey);
    const sessionId = sessionData.sessionId;
    const updatedAt = sessionData.updatedAt || now;

    // Check if there's a SealVera log within 60s of this session completing
    const hasLog = recentLogs.some(l => {
      const logTime = new Date(l.timestamp).getTime();
      return Math.abs(logTime - updatedAt) < 60000;
    });

    if (hasLog) {
      console.log(`[watcher] ✓ ${sessionKey.slice(-20)} — already logged`);
      continue;
    }

    // No matching log — find and read transcript
    const transcriptPath = path.join(SESSIONS_DIR, `${sessionId}.jsonl`);
    const { task, result } = fs.existsSync(transcriptPath)
      ? summariseTranscript(transcriptPath)
      : { task: sessionKey, result: 'transcript not found' };

    console.log(`[watcher] ✗ ${sessionKey.slice(-20)} — missing log, synthesising...`);

    // Log it as a backstop entry
    try {
      const { body } = await request(
        `${SV_ENDPOINT}/api/ingest`,
        { 'x-sealvera-key': SV_KEY },
        'POST',
        {
          agent:   'subagent-watcher',
          action:  'subagent_run',
          decision: 'COMPLETED',
          input:   { task: task.slice(0, 500), sessionKey },
          output:  { result: result.slice(0, 500) },
          reasoning_steps: [{
            factor:      'watcher_backstop',
            value:       'auto_logged',
            signal:      'safe',
            explanation: 'Sub-agent completed without logging — captured by watcher backstop',
          }],
        }
      );
      if (body.ok) {
        console.log(`[watcher] ✓ Backstop log created: ${body.id}`);
      }
    } catch(e) {
      console.error('[watcher] Failed to log backstop entry:', e.message);
    }
  }

  saveState(state);
}

run().catch(e => {
  console.error('[watcher] Fatal error:', e.message);
  process.exit(1);
});
