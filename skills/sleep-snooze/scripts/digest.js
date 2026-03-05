#!/usr/bin/env node
/**
 * digest.js
 * Reads all undelivered queued messages, formats a morning digest,
 * and outputs it as JSON for OpenClaw to deliver via the active provider(s).
 *
 * Called automatically by cron at WAKE_TIME.
 * OpenClaw reads stdout JSON and sends the digest message.
 *
 * Exit codes:
 *   0 — digest output ready on stdout
 *   1 — error
 *   3 — queue is empty (nothing to deliver)
 */

const fs   = require('fs');
const path = require('path');

const DATA_DIR   = path.join(process.env.HOME, '.openclaw', 'skills', 'sleep-snooze', 'data');
const DB_FILE    = path.join(DATA_DIR, 'queue.db');
const STATE_FILE = path.join(DATA_DIR, 'state.json');

// ── Greeting based on time of day ─────────────────────────────────────────────
function greeting() {
  const h = new Date().getHours();
  if (h < 12) return 'Good morning';
  if (h < 17) return 'Good afternoon';
  return 'Good evening';
}

// ── Format digest text ────────────────────────────────────────────────────────
function formatDigest(rows) {
  // Group by sender
  const grouped = {};
  for (const row of rows) {
    const key = `${row.provider}:${row.sender_id}`;
    if (!grouped[key]) {
      grouped[key] = { senderName: row.sender_name || row.sender_id, messages: [] };
    }
    grouped[key].messages.push(row.message);
  }

  const senders = Object.values(grouped);
  const totalCount = rows.length;

  let text = `🌅 ${greeting()}! Here's what arrived while you slept:\n\n`;

  for (const { senderName, messages } of senders) {
    const count = messages.length;
    text += `📬 ${count} message${count !== 1 ? 's' : ''} from ${senderName}\n`;
    // Show up to 3 previews per sender
    for (const msg of messages.slice(0, 3)) {
      const preview = msg.length > 80 ? msg.slice(0, 77) + '…' : msg;
      text += `  • "${preview}"\n`;
    }
    if (messages.length > 3) {
      text += `  • … and ${messages.length - 3} more\n`;
    }
    text += '\n';
  }

  if (senders.length > 1) {
    text += `💬 ${totalCount} total messages from ${senders.length} senders.`;
  }

  return text.trim();
}

// ── Main ──────────────────────────────────────────────────────────────────────
try {
  const Database = require('better-sqlite3');
  const db       = new Database(DB_FILE);

  const rows = db.prepare(`
    SELECT * FROM queue WHERE delivered = 0 ORDER BY received_at ASC
  `).all();

  if (rows.length === 0) {
    console.log(JSON.stringify({ action: 'no_digest', reason: 'queue_empty' }));
    db.close();
    process.exit(3);
  }

  const digestText = formatDigest(rows);

  // Mark all as delivered
  const ids = rows.map(r => r.id);
  db.prepare(`UPDATE queue SET delivered = 1 WHERE id IN (${ids.join(',')})`).run();
  db.close();

  // Update lastDigestAt in state
  try {
    const state = JSON.parse(fs.readFileSync(STATE_FILE, 'utf8'));
    state.lastDigestAt = new Date().toISOString();
    fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
  } catch { /* non-fatal */ }

  // Output digest for OpenClaw to deliver
  console.log(JSON.stringify({
    action: 'deliver_digest',
    messageCount: rows.length,
    text: digestText,
  }));

  process.exit(0);

} catch (err) {
  console.error('Digest error:', err.message);
  process.exit(1);
}
