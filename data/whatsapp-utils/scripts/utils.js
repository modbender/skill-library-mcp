#!/usr/bin/env node
// WhatsApp Utils - Miscellaneous utilities for WhatsApp automation
// MIT License

const fs = require('fs');
const path = require('path');
const os = require('os');

const CREDS_PATH = path.join(
  process.env.OPENCLAW_STATE_DIR || path.join(os.homedir(), '.openclaw'),
  'credentials', 'whatsapp', 'default'
);

/**
 * Format a phone number for WhatsApp use
 * @param {string} input - Raw phone number input
 */
function formatNumber(input) {
  let clean = input.replace(/\D/g, '');

  // Remove leading zero
  if (clean.startsWith('0')) {
    clean = clean.slice(1);
  }

  // Add country code if missing (defaults to +55 Brazil)
  if (clean.length === 10 || clean.length === 11) {
    clean = '55' + clean;
  }

  console.log(JSON.stringify({
    original: input,
    cleaned: clean,
    jid: `${clean}@s.whatsapp.net`,
    formatted: `+${clean.slice(0, 2)} (${clean.slice(2, 4)}) ${clean.slice(4, 9)}-${clean.slice(9)}`
  }, null, 2));
}

/**
 * Remove all non-digit characters from a phone number
 * @param {string} input - Raw phone number input
 */
function cleanNumber(input) {
  const clean = input.replace(/\D/g, '');
  console.log(JSON.stringify({ original: input, clean, length: clean.length }, null, 2));
}

/**
 * Display cache directory statistics
 */
function cacheInfo() {
  try {
    const files = fs.readdirSync(CREDS_PATH);

    let totalSize = 0;
    const types = {
      'creds.json': 0, 'contacts.json': 0, 'store.json': 0,
      'session-': 0, 'sender-key-': 0, 'device-list-': 0, other: 0
    };

    for (const file of files) {
      const filePath = path.join(CREDS_PATH, file);
      const stats = fs.statSync(filePath);
      totalSize += stats.size;

      let matched = false;
      for (const prefix of Object.keys(types)) {
        if (file.startsWith(prefix) || file === prefix) {
          types[prefix]++;
          matched = true;
          break;
        }
      }
      if (!matched) types.other++;
    }

    console.log(JSON.stringify({
      path: CREDS_PATH,
      totalFiles: files.length,
      totalSize: formatBytes(totalSize),
      breakdown: {
        credentials: types['creds.json'],
        contacts: types['contacts.json'],
        store: types['store.json'],
        sessions: types['session-'],
        senderKeys: types['sender-key-'],
        deviceLists: types['device-list-'],
        other: types.other
      }
    }, null, 2));
  } catch (error) {
    console.log(JSON.stringify({ error: error.message }));
  }
}

/**
 * Format bytes into a human-readable string
 * @param {number} bytes - Byte count
 * @returns {string} Formatted string
 */
function formatBytes(bytes) {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Export contacts to a clean JSON list
 */
function exportContacts() {
  try {
    const contactsPath = path.join(CREDS_PATH, 'contacts.json');
    if (!fs.existsSync(contactsPath)) {
      console.log(JSON.stringify({ error: 'Contacts file not found' }));
      return;
    }

    const contacts = JSON.parse(fs.readFileSync(contactsPath, 'utf8'));
    const exported = Object.entries(contacts)
      .filter(([id]) => id.endsWith('@s.whatsapp.net'))
      .map(([id, c]) => ({
        phone: id.replace('@s.whatsapp.net', ''),
        name: c.name || c.notify || null,
        isBusiness: c.isBusiness || false
      }));

    console.log(JSON.stringify({ total: exported.length, contacts: exported }, null, 2));
  } catch (error) {
    console.log(JSON.stringify({ error: error.message }));
  }
}

/**
 * Generate a random WhatsApp-style message ID
 */
function generateMessageId() {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
  let id = '';
  for (let i = 0; i < 22; i++) {
    id += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  console.log(JSON.stringify({ messageId: id, fullId: `true_${id}` }, null, 2));
}

// CLI
const cmd = process.argv[2];
const arg = process.argv.slice(3).join(' ');

switch (cmd) {
  case 'format':
    if (!arg) { console.error('Usage: utils.js format <phone>'); process.exit(1); }
    formatNumber(arg); break;
  case 'clean':
    if (!arg) { console.error('Usage: utils.js clean <phone>'); process.exit(1); }
    cleanNumber(arg); break;
  case 'cache-info': cacheInfo(); break;
  case 'export-contacts': exportContacts(); break;
  case 'gen-id': generateMessageId(); break;
  default:
    console.log(JSON.stringify({
      usage: 'utils.js [format|clean|cache-info|export-contacts|gen-id] [args]',
      commands: {
        format: 'Format phone number: format <phone>',
        clean: 'Strip non-digits: clean <phone>',
        'cache-info': 'Session cache statistics',
        'export-contacts': 'Export contacts to JSON',
        'gen-id': 'Generate random message ID'
      }
    }, null, 2));
}
