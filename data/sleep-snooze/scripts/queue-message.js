#!/usr/bin/env node
/**
 * queue-message.js
 * Called by OpenClaw when a message arrives during sleep hours.
 * Stores the message in the SQLite queue for morning digest delivery.
 *
 * Usage:
 *   node queue-message.js --provider telegram --sender-id 123456 --sender-name "Alex" --message "Hey!"
 *
 * Or pipe JSON:
 *   echo '{"provider":"telegram","senderId":"123456","senderName":"Alex","message":"Hey!"}' | node queue-message.js
 */

const fs   = require('fs');
const path = require('path');

const DATA_DIR = path.join(process.env.HOME, '.openclaw', 'skills', 'sleep-snooze', 'data');
const DB_FILE  = path.join(DATA_DIR, 'queue.db');
const VIP_FILE = path.join(DATA_DIR, 'vip-contacts.json');

const URGENT_KEYWORDS = ['urgent', 'emergency', 'critical', '911', 'help me'];

// ── Parse input (CLI args or stdin JSON) ──────────────────────────────────────
async function parseInput() {
  const args = process.argv.slice(2);
  const get  = (flag) => { const i = args.indexOf(flag); return i !== -1 ? args[i + 1] : null; };

  if (args.length > 0) {
    return {
      provider:   get('--provider')    || 'unknown',
      senderId:   get('--sender-id')   || 'unknown',
      senderName: get('--sender-name') || null,
      message:    get('--message')     || '',
    };
  }

  // Fallback: read JSON from stdin
  return new Promise((resolve, reject) => {
    let data = '';
    process.stdin.on('data', chunk => { data += chunk; });
    process.stdin.on('end', () => {
      try { resolve(JSON.parse(data)); }
      catch (e) { reject(new Error('Invalid JSON on stdin')); }
    });
  });
}

// ── Check urgency ─────────────────────────────────────────────────────────────
function isUrgent(message, senderId) {
  const lower = message.toLowerCase();
  if (URGENT_KEYWORDS.some(kw => lower.includes(kw))) return true;

  try {
    const vip = JSON.parse(fs.readFileSync(VIP_FILE, 'utf8'));
    if (vip.contacts.includes(senderId)) return true;
  } catch { /* no VIP file yet */ }

  return false;
}

// ── Main ──────────────────────────────────────────────────────────────────────
(async () => {
  const payload = await parseInput();
  const { provider, senderId, senderName, message } = payload;

  if (!message) {
    console.error('No message content provided.');
    process.exit(1);
  }

  const urgent = isUrgent(message, senderId);

  if (urgent) {
    // Signal to OpenClaw that this message must be delivered immediately
    console.log(JSON.stringify({ action: 'deliver_now', urgent: true, payload }));
    process.exit(2); // exit code 2 = urgent, deliver now
  }

  // Queue the message
  try {
    const Database = require('better-sqlite3');
    const db       = new Database(DB_FILE);

    const insert = db.prepare(`
      INSERT INTO queue (provider, sender_id, sender_name, message, received_at)
      VALUES (?, ?, ?, ?, datetime('now'))
    `);
    const result = insert.run(provider, senderId, senderName || senderId, message);
    db.close();

    const queued = { action: 'queued', id: result.lastInsertRowid, provider, senderName };
    console.log(JSON.stringify(queued));
    process.exit(0); // exit code 0 = queued successfully

  } catch (err) {
    console.error('Failed to queue message:', err.message);
    process.exit(1);
  }
})();
