#!/usr/bin/env node
// WhatsApp Labels - Manage WhatsApp Business labels/tags
// MIT License

const fs = require('fs');
const path = require('path');
const os = require('os');

const CREDS_PATH = path.join(
  process.env.OPENCLAW_STATE_DIR || path.join(os.homedir(), '.openclaw'),
  'credentials', 'whatsapp', 'default'
);

/**
 * List all known labels from the session cache
 */
function listLabels() {
  try {
    const files = ['store.json', 'labels.json'];
    let labels = [];

    for (const file of files) {
      const filePath = path.join(CREDS_PATH, file);
      if (fs.existsSync(filePath)) {
        const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
        if (data.labels) {
          labels = Object.entries(data.labels).map(([id, label]) => ({
            id,
            name: label.name || label,
            color: label.color || null
          }));
          break;
        }
      }
    }

    if (labels.length === 0) {
      // Attempt to extract from contacts that have labels
      const contactsPath = path.join(CREDS_PATH, 'contacts.json');
      if (fs.existsSync(contactsPath)) {
        const contacts = JSON.parse(fs.readFileSync(contactsPath, 'utf8'));
        const labelSet = new Set();

        for (const contact of Object.values(contacts)) {
          if (contact.labels && Array.isArray(contact.labels)) {
            contact.labels.forEach(l => labelSet.add(l));
          }
        }

        labels = Array.from(labelSet).map(l => ({ id: l, name: l }));
      }
    }

    console.log(JSON.stringify({
      total: labels.length,
      labels,
      note: labels.length === 0 ? 'No labels found in cache' : null
    }, null, 2));
  } catch (error) {
    console.log(JSON.stringify({ error: error.message }));
  }
}

/**
 * Find contacts/chats that have a specific label
 * @param {string} labelName - Label name to search for
 */
function findByLabel(labelName) {
  try {
    const results = [];
    const labelLower = labelName.toLowerCase();

    const contactsPath = path.join(CREDS_PATH, 'contacts.json');
    if (fs.existsSync(contactsPath)) {
      const contacts = JSON.parse(fs.readFileSync(contactsPath, 'utf8'));

      for (const [id, contact] of Object.entries(contacts)) {
        if (contact.labels && Array.isArray(contact.labels)) {
          const hasLabel = contact.labels.some(l => l.toLowerCase().includes(labelLower));
          if (hasLabel) {
            results.push({
              id,
              name: contact.name || contact.notify,
              labels: contact.labels
            });
          }
        }
      }
    }

    console.log(JSON.stringify({ query: labelName, total: results.length, contacts: results }, null, 2));
  } catch (error) {
    console.log(JSON.stringify({ error: error.message }));
  }
}

// CLI
const cmd = process.argv[2];
const arg = process.argv[3];

switch (cmd) {
  case 'list': listLabels(); break;
  case 'chats':
  case 'find':
    if (!arg) { console.error('Usage: labels.js chats <labelName>'); process.exit(1); }
    findByLabel(arg); break;
  default:
    console.log(JSON.stringify({
      usage: 'labels.js [list|chats] [args]',
      commands: {
        list: 'List all labels',
        chats: 'Find chats by label: chats <labelName>'
      }
    }, null, 2));
}
