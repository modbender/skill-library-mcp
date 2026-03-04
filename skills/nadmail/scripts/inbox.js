#!/usr/bin/env node
/**
 * NadMail Inbox Script
 *
 * Usage:
 *   node inbox.js              # List inbox
 *   node inbox.js <email_id>   # Read specific email
 */

const fs = require('fs');
const path = require('path');

const API_BASE = 'https://api.nadmail.ai';
const CONFIG_DIR = path.join(process.env.HOME, '.nadmail');
const TOKEN_FILE = path.join(CONFIG_DIR, 'token.json');
const AUDIT_FILE = path.join(CONFIG_DIR, 'audit.log');

function logAudit(action, details = {}) {
  try {
    if (!fs.existsSync(CONFIG_DIR)) return;
    const entry = {
      timestamp: new Date().toISOString(),
      action,
      success: details.success ?? true,
    };
    fs.appendFileSync(AUDIT_FILE, JSON.stringify(entry) + '\n', { mode: 0o600 });
  } catch (e) {
    // Silently ignore audit errors
  }
}

function getToken() {
  if (process.env.NADMAIL_TOKEN) {
    return process.env.NADMAIL_TOKEN;
  }

  if (!fs.existsSync(TOKEN_FILE)) {
    console.error('Not registered yet. Run register.js first.');
    process.exit(1);
  }

  const data = JSON.parse(fs.readFileSync(TOKEN_FILE, 'utf8'));

  if (data.saved_at) {
    const hoursSinceSaved = (Date.now() - new Date(data.saved_at).getTime()) / 1000 / 60 / 60;
    if (hoursSinceSaved > 20) {
      console.log('Warning: Token may be expiring soon. Run register.js again if you get auth errors.');
    }
  }

  return data.token;
}

async function listInbox(token) {
  const res = await fetch(`${API_BASE}/api/inbox`, {
    headers: { 'Authorization': `Bearer ${token}` },
  });

  const data = await res.json();

  if (data.error) {
    console.error('Error:', data.error);
    logAudit('inbox_list', { success: false });
    process.exit(1);
  }

  console.log(`Inbox (${data.unread} unread / ${data.total} total)`);
  console.log('='.repeat(60));

  const emails = data.emails || [];

  if (emails.length === 0) {
    console.log('No emails.');
    return;
  }

  for (const email of emails) {
    const unread = email.read ? ' ' : '*';
    const date = email.created_at || email.date;
    const displayDate = date ? new Date(date * 1000).toLocaleString() : 'Unknown';
    console.log(`${unread} [${email.id || 'N/A'}]`);
    console.log(`  From: ${email.from || email.from_addr || 'Unknown'}`);
    console.log(`  Subject: ${email.subject || 'No subject'}`);
    console.log(`  Date: ${displayDate}`);
    console.log(`  Preview: ${(email.snippet || '').slice(0, 80)}...`);
    console.log('');
  }

  logAudit('inbox_list', { success: true });
}

async function readEmail(token, emailId) {
  try {
    const res = await fetch(`${API_BASE}/api/inbox/${emailId}`, {
      headers: { 'Authorization': `Bearer ${token}` },
    });

    const data = await res.json();

    if (data.error) {
      console.error('Error:', data.error);
      logAudit('inbox_read', { success: false });
      process.exit(1);
    }

    console.log('Email');
    console.log('='.repeat(60));
    console.log(`From: ${data.from || data.from_addr}`);
    console.log(`To: ${data.to || data.to_addr}`);
    console.log(`Subject: ${data.subject}`);
    console.log(`Date: ${data.created_at ? new Date(data.created_at * 1000).toLocaleString() : 'Unknown'}`);
    if (data.microbuy_tx) {
      console.log(`Micro-buy TX: ${data.microbuy_tx}`);
    }
    if (data.emo_amount && data.emo_amount > 0) {
      console.log(`Emo-Boost: +${data.emo_amount} MON`);
    }
    console.log('='.repeat(60));
    console.log(data.body || data.text || 'No content');

    logAudit('inbox_read', { success: true });
  } catch (err) {
    console.error('Error reading email:', err.message);
    logAudit('inbox_read', { success: false });
    process.exit(1);
  }
}

async function main() {
  const emailId = process.argv[2];
  const token = getToken();

  if (emailId) {
    await readEmail(token, emailId);
  } else {
    await listInbox(token);
  }
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
