#!/usr/bin/env node
/**
 * Operator Inbox — zero-dependency slow-channel for agent→operator messages.
 * Storage: {workspace}/inbox/messages.json (atomic writes)
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

// --- Config ---
const WORKSPACE = process.env.OPENCLAW_WORKSPACE || process.env.HOME || '.';
const INBOX_DIR = path.join(WORKSPACE, 'inbox');
const INBOX_FILE = path.join(INBOX_DIR, 'messages.json');

// --- Storage ---
function ensureDir() {
  if (!fs.existsSync(INBOX_DIR)) fs.mkdirSync(INBOX_DIR, { recursive: true });
}

function load() {
  try {
    if (fs.existsSync(INBOX_FILE)) return JSON.parse(fs.readFileSync(INBOX_FILE, 'utf8'));
  } catch (e) { /* corrupt — start fresh */ }
  return { messages: [], version: 1 };
}

function save(data) {
  ensureDir();
  data.lastUpdated = new Date().toISOString();
  const tmp = INBOX_FILE + '.tmp';
  fs.writeFileSync(tmp, JSON.stringify(data, null, 2));
  fs.renameSync(tmp, INBOX_FILE);
}

// --- Commands ---
function add(title, message) {
  const data = load();

  let priority = 'normal';
  let cleanTitle = title;
  if (title.startsWith('[URGENT]')) { priority = 'urgent'; cleanTitle = title.replace('[URGENT]', '').trim(); }
  else if (title.startsWith('[IMPORTANT]')) { priority = 'important'; cleanTitle = title.replace('[IMPORTANT]', '').trim(); }

  const entry = {
    id: crypto.randomBytes(6).toString('hex'),
    title: cleanTitle,
    message,
    priority,
    read: false,
    archived: false,
    createdAt: new Date().toISOString(),
    readAt: null
  };

  data.messages.unshift(entry);
  save(data);
  console.log(JSON.stringify({ ok: true, id: entry.id, title: cleanTitle, priority }));
}

function list(filter = 'unread', jsonMode = false) {
  const data = load();
  let msgs = data.messages || [];

  if (filter === 'unread') msgs = msgs.filter(m => !m.read && !m.archived);
  else if (filter === 'archived') msgs = msgs.filter(m => m.archived);
  else if (filter === 'all') msgs = msgs.filter(m => !m.archived);

  // Sort: urgent first, then important, then by date desc
  const prioOrder = { urgent: 0, important: 1, normal: 2 };
  msgs.sort((a, b) => {
    if (!a.read && b.read) return -1;
    if (a.read && !b.read) return 1;
    const pa = prioOrder[a.priority] ?? 2, pb = prioOrder[b.priority] ?? 2;
    if (pa !== pb) return pa - pb;
    return new Date(b.createdAt) - new Date(a.createdAt);
  });

  const unreadCount = (data.messages || []).filter(m => !m.read && !m.archived).length;
  const totalCount = (data.messages || []).filter(m => !m.archived).length;
  const archivedCount = (data.messages || []).filter(m => m.archived).length;

  if (jsonMode) {
    console.log(JSON.stringify({ messages: msgs, unread: unreadCount, total: totalCount, archived: archivedCount }));
    return;
  }

  console.log(`\n📬 Inbox (${unreadCount} unread · ${totalCount} total · ${archivedCount} archived)\n`);
  if (msgs.length === 0) { console.log('  ✅ All caught up.\n'); return; }

  for (const m of msgs.slice(0, 20)) {
    const icon = m.priority === 'urgent' ? '🔴' : m.priority === 'important' ? '🟡' : '⚪';
    const status = m.read ? '✓' : '•';
    const date = new Date(m.createdAt).toLocaleDateString();
    console.log(`${status} ${icon} [${date}] ${m.title}  (${m.id})`);
    if (!m.read) console.log(`     ${m.message.substring(0, 100)}${m.message.length > 100 ? '…' : ''}`);
  }
  console.log('');
}

function markRead(id) {
  const data = load();
  const m = data.messages.find(m => m.id === id);
  if (!m) { console.log(JSON.stringify({ ok: false, error: 'not found' })); return; }
  m.read = true; m.readAt = new Date().toISOString();
  save(data);
  console.log(JSON.stringify({ ok: true }));
}

function markAllRead() {
  const data = load();
  const now = new Date().toISOString();
  let count = 0;
  for (const m of data.messages) {
    if (!m.read && !m.archived) { m.read = true; m.readAt = now; count++; }
  }
  save(data);
  console.log(JSON.stringify({ ok: true, count }));
}

function archive(id) {
  const data = load();
  const m = data.messages.find(m => m.id === id);
  if (!m) { console.log(JSON.stringify({ ok: false, error: 'not found' })); return; }
  m.archived = true; m.read = true; m.readAt = m.readAt || new Date().toISOString();
  save(data);
  console.log(JSON.stringify({ ok: true }));
}

function archiveRead() {
  const data = load();
  let count = 0;
  for (const m of data.messages) {
    if (m.read && !m.archived) { m.archived = true; count++; }
  }
  save(data);
  console.log(JSON.stringify({ ok: true, count }));
}

// --- Rendering ---
function esc(s) { return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }

function render(filter = 'unread', format = 'auto') {
  const data = load();
  let msgs = data.messages || [];

  if (filter === 'unread') msgs = msgs.filter(m => !m.read && !m.archived);
  else if (filter === 'archived') msgs = msgs.filter(m => m.archived);
  else if (filter === 'all') msgs = msgs.filter(m => !m.archived);

  const prioOrder = { urgent: 0, important: 1, normal: 2 };
  msgs.sort((a, b) => {
    if (!a.read && b.read) return -1;
    if (a.read && !b.read) return 1;
    const pa = prioOrder[a.priority] ?? 2, pb = prioOrder[b.priority] ?? 2;
    if (pa !== pb) return pa - pb;
    return new Date(b.createdAt) - new Date(a.createdAt);
  });

  const unreadCount = (data.messages || []).filter(m => !m.read && !m.archived).length;
  const totalCount = (data.messages || []).filter(m => !m.archived).length;

  // Auto-detect format from OPENCLAW_CHANNEL env
  if (format === 'auto') {
    const ch = (process.env.OPENCLAW_CHANNEL || '').toLowerCase();
    if (['telegram', 'webchat'].includes(ch)) format = 'html';
    else if (['discord', 'slack'].includes(ch)) format = 'md';
    else format = 'text';
  }

  if (format === 'html') console.log(renderHTML(msgs, unreadCount, totalCount, filter));
  else if (format === 'md') console.log(renderMD(msgs, unreadCount, totalCount, filter));
  else console.log(renderText(msgs, unreadCount, totalCount, filter));
}

function renderHTML(msgs, unread, total, filter) {
  const filterLabel = filter === 'unread' ? 'Unread' : filter === 'archived' ? 'Archived' : 'All';

  if (msgs.length === 0) {
    return `<b>📬 Inbox</b> <i>(${filterLabel})</i>\n\n✅ ${filter === 'unread' ? 'All caught up!' : 'No messages.'}`;
  }

  let html = `<b>📬 Inbox</b> — <i>${unread} unread · ${total} total · ${filterLabel}</i>\n`;

  for (const m of msgs.slice(0, 15)) {
    const prioIcon = m.priority === 'urgent' ? '🔴' : m.priority === 'important' ? '🟡' : '';
    const prioTag = m.priority === 'urgent'
      ? ' <b>[URGENT]</b>'
      : m.priority === 'important'
        ? ' <b>[IMPORTANT]</b>'
        : '';
    const readStyle = m.read ? '<i>' : '';
    const readEnd = m.read ? '</i>' : '';
    const date = fmtDate(m.createdAt);

    html += `\n${readStyle}${prioIcon}${prioTag} <b>${esc(m.title)}</b>\n`;
    html += `${esc(m.message)}\n`;
    html += `<code>${date}</code> · <code>${m.id}</code>${readEnd}\n`;
  }

  if (msgs.length > 15) html += `\n<i>…and ${msgs.length - 15} more</i>`;
  return html;
}

function renderMD(msgs, unread, total, filter) {
  const filterLabel = filter === 'unread' ? 'Unread' : filter === 'archived' ? 'Archived' : 'All';

  if (msgs.length === 0) {
    return `**📬 Inbox** *(${filterLabel})*\n\n✅ ${filter === 'unread' ? 'All caught up!' : 'No messages.'}`;
  }

  let md = `**📬 Inbox** — *${unread} unread · ${total} total · ${filterLabel}*\n`;

  for (const m of msgs.slice(0, 15)) {
    const prioIcon = m.priority === 'urgent' ? '🔴 ' : m.priority === 'important' ? '🟡 ' : '';
    const prioTag = m.priority !== 'normal' ? ` **[${m.priority.toUpperCase()}]**` : '';
    const bullet = m.read ? '  ✓' : '  •';
    const date = fmtDate(m.createdAt);

    md += `\n${bullet} ${prioIcon}**${m.title}**${prioTag}\n`;
    md += `  ${m.message}\n`;
    md += `  \`${date}\` · \`${m.id}\`\n`;
  }

  if (msgs.length > 15) md += `\n*…and ${msgs.length - 15} more*`;
  return md;
}

function renderText(msgs, unread, total, filter) {
  const filterLabel = filter === 'unread' ? 'Unread' : filter === 'archived' ? 'Archived' : 'All';

  if (msgs.length === 0) {
    return `INBOX (${filterLabel})\n\nAll caught up.`;
  }

  let txt = `INBOX — ${unread} unread / ${total} total (${filterLabel})\n${'─'.repeat(50)}\n`;

  for (const m of msgs.slice(0, 15)) {
    const prioIcon = m.priority === 'urgent' ? '[!!!] ' : m.priority === 'important' ? '[!!] ' : '';
    const status = m.read ? '[read]' : '[NEW] ';
    const date = fmtDate(m.createdAt);

    txt += `\n${status}${prioIcon}${m.title}\n`;
    txt += `  ${m.message}\n`;
    txt += `  ${date} | ${m.id}\n`;
  }

  if (msgs.length > 15) txt += `\n...and ${msgs.length - 15} more`;
  return txt;
}

function fmtDate(iso) {
  const d = new Date(iso);
  const mo = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][d.getMonth()];
  return `${mo} ${d.getDate()}, ${d.getHours().toString().padStart(2,'0')}:${d.getMinutes().toString().padStart(2,'0')}`;
}

// --- CLI ---
const args = process.argv.slice(2);
const cmd = args[0] || 'list';

switch (cmd) {
  case 'add':
    if (args.length < 3) { console.error('Usage: inbox.js add "Title" "Message"'); process.exit(1); }
    add(args[1], args[2]);
    break;
  case 'list':
    list(args[1] || 'unread', args.includes('--json'));
    break;
  case 'read':
    if (!args[1]) { console.error('Usage: inbox.js read <id>'); process.exit(1); }
    markRead(args[1]);
    break;
  case 'read-all':
    markAllRead();
    break;
  case 'archive':
    if (!args[1]) { console.error('Usage: inbox.js archive <id>'); process.exit(1); }
    archive(args[1]);
    break;
  case 'archive-read':
    archiveRead();
    break;
  case 'render': {
    let filter = 'unread', format = 'auto';
    for (const a of args.slice(1)) {
      if (a === '--html') format = 'html';
      else if (a === '--md') format = 'md';
      else if (a === '--text') format = 'text';
      else if (['unread', 'all', 'archived'].includes(a)) filter = a;
    }
    render(filter, format);
    break;
  }
  default:
    console.log('Commands: add, list, read, read-all, archive, archive-read, render');
    console.log('Run with no args for unread list.');
}
