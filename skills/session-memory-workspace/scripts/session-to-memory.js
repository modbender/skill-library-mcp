#!/usr/bin/env node
/**
 * session-to-memory.js
 * Find sessions for a given date, extract user/assistant messages, build a short
 * summary markdown, and write/append to workspace/memory/YYYY-MM-DD.md.
 * Usage: node session-to-memory.js --date YYYY-MM-DD [--workspace path] [--sessions-dir path] [--append] [--max-messages N]
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

function parseArgs() {
  const args = process.argv.slice(2);
  const out = {
    date: null,
    workspace: process.cwd(),
    sessionsDir: path.join(os.homedir(), '.openclaw', 'agents', 'main', 'sessions'),
    append: true,
    maxMessages: 200,
  };
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--date' && args[i + 1]) {
      out.date = args[++i];
    } else if (args[i] === '--workspace' && args[i + 1]) {
      out.workspace = args[++i];
    } else if (args[i] === '--sessions-dir' && args[i + 1]) {
      out.sessionsDir = args[++i];
    } else if (args[i] === '--append') {
      out.append = true;
    } else if (args[i] === '--replace') {
      out.append = false;
    } else if (args[i] === '--max-messages' && args[i + 1]) {
      out.maxMessages = parseInt(args[++i], 10) || 200;
    }
  }
  if (!out.date) {
    const d = new Date();
    d.setDate(d.getDate() - 1);
    out.date = d.toISOString().slice(0, 10);
  }
  return out;
}

function readJsonlLines(filePath, maxLines = 5000) {
  const content = fs.readFileSync(filePath, 'utf-8');
  const lines = content.split('\n').filter((l) => l.trim());
  const out = [];
  for (let i = 0; i < lines.length && out.length < maxLines; i++) {
    try {
      out.push(JSON.parse(lines[i]));
    } catch (_) {
      // skip bad lines
    }
  }
  return out;
}

function getSessionDate(firstLine) {
  if (!firstLine || firstLine.type !== 'session' || !firstLine.timestamp) return null;
  return firstLine.timestamp.slice(0, 10);
}

function extractMessages(lines, maxMessages) {
  const messages = [];
  for (const obj of lines) {
    if (obj.type !== 'message' || !obj.message) continue;
    const role = obj.message.role;
    if (role !== 'user' && role !== 'assistant') continue;
    const parts = obj.message.content || [];
    for (const p of parts) {
      if (p.type === 'text' && p.text && typeof p.text === 'string') {
        const text = p.text.trim();
        if (text.length > 0) messages.push({ role, text, ts: obj.timestamp });
        if (messages.length >= maxMessages) return messages;
      }
    }
  }
  return messages;
}

function buildSummaryMarkdown(sessionId, date, messages) {
  const lines = [
    `### Session ${sessionId.slice(0, 8)}`,
    '',
  ];
  for (const m of messages) {
    const label = m.role === 'user' ? '**User**' : '**Assistant**';
    const preview = m.text.slice(0, 800) + (m.text.length > 800 ? '…' : '');
    lines.push(`- ${label}: ${preview.replace(/\n/g, ' ')}`);
  }
  lines.push('');
  return lines.join('\n');
}

function main() {
  const opts = parseArgs();
  const date = opts.date;
  const memoryDir = path.join(opts.workspace, 'memory');
  const memoryFile = path.join(memoryDir, `${date}.md`);

  if (!fs.existsSync(opts.sessionsDir)) {
    console.error(JSON.stringify({ ok: false, error: `sessions dir not found: ${opts.sessionsDir}` }));
    process.exit(1);
  }

  const files = fs.readdirSync(opts.sessionsDir).filter((f) => f.endsWith('.jsonl'));
  const sessionsForDate = [];
  for (const f of files) {
    const filePath = path.join(opts.sessionsDir, f);
    const sessionId = f.replace(/\.jsonl$/, '');
    const lines = readJsonlLines(filePath, opts.maxMessages + 100);
    const first = lines[0];
    const sessionDate = getSessionDate(first);
    if (sessionDate === date) {
      const messages = extractMessages(lines, opts.maxMessages);
      sessionsForDate.push({ sessionId, messages });
    }
  }

  if (sessionsForDate.length === 0) {
    console.error(JSON.stringify({
      ok: false,
      error: `no sessions found for date ${date}`,
      hint: 'Check ~/.openclaw/agents/main/sessions/*.jsonl first line .timestamp',
    }));
    process.exit(1);
  }

  let body = '';
  for (const { sessionId, messages } of sessionsForDate) {
    body += buildSummaryMarkdown(sessionId, date, messages);
  }
  const newSection = `## Session summary\n\n${body}`;

  try {
    if (!fs.existsSync(memoryDir)) fs.mkdirSync(memoryDir, { recursive: true });
  } catch (e) {
    console.error(JSON.stringify({ ok: false, error: `mkdir memory: ${e.message}` }));
    process.exit(1);
  }

  let finalContent;
  if (opts.append && fs.existsSync(memoryFile)) {
    const existing = fs.readFileSync(memoryFile, 'utf-8');
    if (existing.match(/\n## Session summary\n/i)) {
      finalContent = existing.replace(/\n## Session summary\n[\s\S]*/i, '\n' + newSection);
    } else {
      finalContent = existing.trimEnd() + '\n\n' + newSection;
    }
  } else {
    finalContent = `# ${date}\n\n${newSection}`;
  }

  fs.writeFileSync(memoryFile, finalContent, 'utf-8');
  console.log(JSON.stringify({
    ok: true,
    date,
    memoryFile,
    sessionsCount: sessionsForDate.length,
    message: `Wrote session summary to ${memoryFile}`,
  }));
}

main();
