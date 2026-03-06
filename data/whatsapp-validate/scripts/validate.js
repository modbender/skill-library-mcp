#!/usr/bin/env node
// WhatsApp Validate - Check phone numbers against the Baileys session cache
// MIT License

const fs = require('fs');
const path = require('path');
const os = require('os');

const CREDS_PATH = path.join(
  process.env.OPENCLAW_STATE_DIR || path.join(os.homedir(), '.openclaw'),
  'credentials', 'whatsapp', 'default'
);

/**
 * Load all known phone numbers from the Baileys cache
 * @returns {Set<string>} Set of phone number strings
 */
function loadKnownNumbers() {
  const numbers = new Set();

  try {
    const files = fs.readdirSync(CREDS_PATH);

    for (const file of files) {
      // session-NUMBER.json
      if (file.startsWith('session-')) {
        const match = file.match(/session-(\d+)_/);
        if (match) numbers.add(match[1]);
      }
      // device-list-NUMBER.json
      if (file.startsWith('device-list-')) {
        const match = file.match(/device-list-(\d+)\.json/);
        if (match) numbers.add(match[1]);
      }
    }

    // Also load from contacts file
    try {
      const contactsPath = path.join(CREDS_PATH, 'contacts.json');
      if (fs.existsSync(contactsPath)) {
        const contacts = JSON.parse(fs.readFileSync(contactsPath, 'utf8'));
        for (const jid of Object.keys(contacts)) {
          if (jid.endsWith('@s.whatsapp.net')) {
            numbers.add(jid.replace('@s.whatsapp.net', ''));
          }
        }
      }
    } catch (e) { /* contacts not available */ }

  } catch (error) {
    console.error(JSON.stringify({ error: error.message }));
    process.exit(1);
  }

  return numbers;
}

/**
 * Check if a single number is in the cache
 * @param {string} phone - Phone number
 */
function checkNumber(phone) {
  const cleanPhone = phone.replace(/\D/g, '');
  const numbers = loadKnownNumbers();
  const found = numbers.has(cleanPhone);

  console.log(JSON.stringify({
    phone: cleanPhone,
    inCache: found,
    status: found ? 'known' : 'unknown',
    jid: found ? `${cleanPhone}@s.whatsapp.net` : null,
    note: found
      ? 'Number found in cache — has previously interacted with the bot'
      : 'Number not found in cache — may or may not have WhatsApp'
  }, null, 2));
}

/**
 * Batch check multiple numbers
 * @param {string} phoneList - Comma-separated phone numbers
 */
function batchCheck(phoneList) {
  const phones = phoneList.split(',').map(p => p.trim().replace(/\D/g, ''));
  const numbers = loadKnownNumbers();

  const results = phones.map(phone => ({
    phone,
    inCache: numbers.has(phone),
    jid: numbers.has(phone) ? `${phone}@s.whatsapp.net` : null
  }));

  const known = results.filter(r => r.inCache).length;
  console.log(JSON.stringify({ total: phones.length, known, unknown: phones.length - known, results }, null, 2));
}

/**
 * List all known numbers
 * @param {number} limit - Maximum results
 */
function listKnown(limit = 50) {
  const numbers = Array.from(loadKnownNumbers()).slice(0, parseInt(limit));
  console.log(JSON.stringify({
    total: numbers.length,
    numbers: numbers.map(n => ({ phone: n, jid: `${n}@s.whatsapp.net` }))
  }, null, 2));
}

// CLI
const cmd = process.argv[2];
const arg = process.argv[3];

switch (cmd) {
  case 'check':
    if (!arg) { console.error('Usage: validate.js check <phone>'); process.exit(1); }
    checkNumber(arg); break;
  case 'batch':
    if (!arg) { console.error('Usage: validate.js batch <phone1,phone2,...>'); process.exit(1); }
    batchCheck(arg); break;
  case 'list': listKnown(arg || 50); break;
  default:
    console.log(JSON.stringify({
      usage: 'validate.js [check|batch|list] [args]',
      commands: {
        check: 'Check a number: check <phone>',
        batch: 'Check multiple: batch <phone1,phone2>',
        list: 'List known numbers: list [limit]'
      }
    }, null, 2));
}
