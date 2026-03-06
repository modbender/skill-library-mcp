#!/usr/bin/env node
// WhatsApp Chats - List, search, and analyze conversations
// MIT License

const fs = require('fs');
const path = require('path');
const os = require('os');

const CREDS_PATH = path.join(
  process.env.OPENCLAW_STATE_DIR || path.join(os.homedir(), '.openclaw'),
  'credentials', 'whatsapp', 'default'
);

/**
 * List all known chats (contacts and groups)
 * @param {number} limit - Maximum results
 */
function listChats(limit = 30) {
  const chats = [];

  try {
    const files = fs.readdirSync(CREDS_PATH);
    const seen = new Set();

    // Individual contacts from session files
    for (const file of files) {
      if (file.startsWith('session-') && !file.includes('_1.')) {
        const match = file.match(/session-(\d+)_/);
        if (match) {
          const jid = `${match[1]}@s.whatsapp.net`;
          if (!seen.has(jid)) {
            seen.add(jid);
            chats.push({ id: jid, type: 'contact', phone: match[1] });
          }
        }
      }
    }

    // Groups from sender-key files
    for (const file of files) {
      if (file.startsWith('sender-key-') && file.includes('@g.us')) {
        const match = file.match(/sender-key-(.+@g\.us)--/);
        if (match && !seen.has(match[1])) {
          seen.add(match[1]);
          chats.push({ id: match[1], type: 'group' });
        }
      }
    }

    // Enrich with names
    try {
      const contactsPath = path.join(CREDS_PATH, 'contacts.json');
      if (fs.existsSync(contactsPath)) {
        const contacts = JSON.parse(fs.readFileSync(contactsPath, 'utf8'));
        for (const chat of chats) {
          if (contacts[chat.id]) {
            chat.name = contacts[chat.id].name || contacts[chat.id].notify;
          }
        }
      }
    } catch (e) { /* contacts not available */ }

  } catch (error) {
    console.error(JSON.stringify({ error: error.message }));
    process.exit(1);
  }

  const result = chats.slice(0, parseInt(limit));
  console.log(JSON.stringify({ total: chats.length, showing: result.length, chats: result }, null, 2));
}

/**
 * Search chats by name or number
 * @param {string} query - Search term
 */
function searchChats(query) {
  const results = [];
  const queryLower = query.toLowerCase();

  try {
    const contactsPath = path.join(CREDS_PATH, 'contacts.json');
    if (fs.existsSync(contactsPath)) {
      const contacts = JSON.parse(fs.readFileSync(contactsPath, 'utf8'));

      for (const [id, contact] of Object.entries(contacts)) {
        const name = (contact.name || contact.notify || '').toLowerCase();
        const phone = id.replace('@s.whatsapp.net', '').replace('@g.us', '');

        if (name.includes(queryLower) || phone.includes(query) || id.includes(query)) {
          results.push({
            id,
            name: contact.name || contact.notify,
            type: id.endsWith('@g.us') ? 'group' : 'contact'
          });
        }
      }
    }
  } catch (error) {
    console.error(JSON.stringify({ error: error.message }));
    process.exit(1);
  }

  console.log(JSON.stringify({ query, total: results.length, results }, null, 2));
}

/**
 * Get chat statistics
 */
function chatStats() {
  let groups = 0;
  let contacts = 0;
  let fileCount = 0;

  try {
    const allFiles = fs.readdirSync(CREDS_PATH);
    fileCount = allFiles.length;

    const groupIds = new Set();
    const contactIds = new Set();

    for (const file of allFiles) {
      if (file.startsWith('sender-key-') && file.includes('@g.us')) {
        const match = file.match(/sender-key-(.+@g\.us)--/);
        if (match) groupIds.add(match[1]);
      }
      if (file.startsWith('session-')) {
        const match = file.match(/session-(\d+)_/);
        if (match) contactIds.add(match[1]);
      }
    }

    groups = groupIds.size;
    contacts = contactIds.size;
  } catch (error) {
    console.error(JSON.stringify({ error: error.message }));
    process.exit(1);
  }

  console.log(JSON.stringify({
    summary: { groups, contacts, total: groups + contacts },
    storage: { files: fileCount, path: CREDS_PATH }
  }, null, 2));
}

// CLI
const cmd = process.argv[2];
const arg = process.argv[3];

switch (cmd) {
  case 'list': listChats(arg || 30); break;
  case 'search':
    if (!arg) { console.error('Usage: chats.js search <query>'); process.exit(1); }
    searchChats(arg); break;
  case 'stats': chatStats(); break;
  default:
    console.log(JSON.stringify({
      usage: 'chats.js [list|search|stats] [args]',
      commands: {
        list: 'List chats: list [limit]',
        search: 'Search: search <query>',
        stats: 'Chat statistics'
      }
    }, null, 2));
}
