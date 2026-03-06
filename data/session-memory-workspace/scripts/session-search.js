#!/usr/bin/env node
/**
 * session-search.js
 * Search session JSONL files by keyword and optional date range; output JSON array of snippets.
 * Usage: node session-search.js --query "phrase" [--since YYYY-MM-DD] [--until YYYY-MM-DD] [--limit N] [--sessions-dir path]
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

function parseArgs() {
  const args = process.argv.slice(2);
  const out = {
    query: null,
    since: null,
    until: null,
    limit: 20,
    sessionsDir: path.join(os.homedir(), '.openclaw', 'agents', 'main', 'sessions'),
  };
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--query' && args[i + 1]) {
      out.query = args[++i];
    } else if (args[i] === '--since' && args[i + 1]) {
      out.since = args[++i];
    } else if (args[i] === '--until' && args[i + 1]) {
      out.until = args[++i];
    } else if (args[i] === '--limit' && args[i + 1]) {
      out.limit = parseInt(args[++i], 10) || 20;
    } else if (args[i] === '--sessions-dir' && args[i + 1]) {
      out.sessionsDir = args[++i];
    }
  }
  return out;
}

function readJsonlLines(filePath, onLine) {
  const content = fs.readFileSync(filePath, 'utf-8');
  const lines = content.split('\n').filter((l) => l.trim());
  for (const line of lines) {
    try {
      const obj = JSON.parse(line);
      if (onLine(obj) === false) break;
    } catch (_) {}
  }
}

function extractTextFromMessage(msg) {
  if (!msg || !msg.content) return [];
  const out = [];
  for (const p of msg.content) {
    if (p.type === 'text' && p.text && typeof p.text === 'string') {
      out.push(p.text.trim());
    }
  }
  return out;
}

function snippetAround(text, query, maxLen = 300) {
  const q = query.toLowerCase();
  const t = text.toLowerCase();
  const idx = t.indexOf(q);
  if (idx === -1) return text.slice(0, maxLen) + (text.length > maxLen ? '…' : '');
  const start = Math.max(0, idx - 60);
  const end = Math.min(text.length, idx + query.length + 200);
  const slice = text.slice(start, end);
  return (start > 0 ? '…' : '') + slice + (end < text.length ? '…' : '');
}

function main() {
  const opts = parseArgs();
  if (!opts.query || opts.query.length === 0) {
    console.error(JSON.stringify({ ok: false, error: 'missing --query' }));
    process.exit(1);
  }
  if (!fs.existsSync(opts.sessionsDir)) {
    console.error(JSON.stringify({ ok: false, error: `sessions dir not found: ${opts.sessionsDir}` }));
    process.exit(1);
  }

  const query = opts.query;
  const results = [];
  const files = fs.readdirSync(opts.sessionsDir).filter((f) => f.endsWith('.jsonl'));

  for (const f of files) {
    if (results.length >= opts.limit) break;
    const filePath = path.join(opts.sessionsDir, f);
    const sessionId = f.replace(/\.jsonl$/, '');
    let sessionDate = null;
    const firstLine = fs.readFileSync(filePath, 'utf-8').split('\n').find((l) => l.trim());
    if (firstLine) {
      try {
        const first = JSON.parse(firstLine);
        if (first.type === 'session' && first.timestamp) sessionDate = first.timestamp.slice(0, 10);
      } catch (_) {}
    }
    if (opts.since && sessionDate && sessionDate < opts.since) continue;
    if (opts.until && sessionDate && sessionDate > opts.until) continue;

    readJsonlLines(filePath, (obj) => {
      if (obj.type === 'session' && obj.timestamp && !sessionDate) sessionDate = obj.timestamp.slice(0, 10);
      if (obj.type !== 'message' || !obj.message) return;
      const role = obj.message.role;
      if (role !== 'user' && role !== 'assistant') return;
      const texts = extractTextFromMessage(obj.message);
      for (const text of texts) {
        if (text.length === 0) continue;
        if (!text.toLowerCase().includes(query.toLowerCase())) continue;
        results.push({
          sessionId,
          date: sessionDate || undefined,
          role,
          snippet: snippetAround(text, query),
          timestamp: obj.timestamp,
        });
        if (results.length >= opts.limit) return false;
      }
    });
  }

  console.log(JSON.stringify({ ok: true, query, count: results.length, results }, null, 2));
}

main();
