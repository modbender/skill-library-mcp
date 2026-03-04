#!/usr/bin/env node
// WhatsApp Contacts - List, search, and lookup contacts from Baileys session cache
// MIT License

const fs = require('fs');
const path = require('path');
const os = require('os');

const CREDS_PATH = path.join(
  process.env.OPENCLAW_STATE_DIR || path.join(os.homedir(), '.openclaw'),
  'credentials', 'whatsapp', 'default'
);

/**
 * Load contacts from the Baileys session store
 * @returns {Object} Map of JID -> contact data
 */
function loadContacts() {
  try {
    const storePath = path.join(CREDS_PATH, 'store.json');
    if (fs.existsSync(storePath)) {
      const store = JSON.parse(fs.readFileSync(storePath, 'utf8'));
      return store.contacts || {};
    }

    const contactsPath = path.join(CREDS_PATH, 'contacts.json');
    if (fs.existsSync(contactsPath)) {
      return JSON.parse(fs.readFileSync(contactsPath, 'utf8'));
    }

    return {};
  } catch (error) {
    console.error(JSON.stringify({ error: `Failed to load contacts: ${error.message}` }));
    process.exit(1);
  }
}

/**
 * List contacts with optional limit
 * @param {number} limit - Maximum number of contacts to return
 */
function listContacts(limit = 50) {
  const contacts = loadContacts();
  const contactList = Object.entries(contacts)
    .slice(0, parseInt(limit))
    .map(([id, contact]) => ({
      id,
      name: contact.name || contact.notify || 'Unknown',
      phone: id.replace('@s.whatsapp.net', '').replace('@g.us', ''),
      isGroup: id.endsWith('@g.us')
    }));

  console.log(JSON.stringify({
    total: Object.keys(contacts).length,
    showing: contactList.length,
    contacts: contactList
  }, null, 2));
}

/**
 * Search contacts by name or phone number
 * @param {string} query - Search term
 */
function searchContacts(query) {
  const contacts = loadContacts();
  const queryLower = query.toLowerCase();

  const results = Object.entries(contacts)
    .filter(([id, contact]) => {
      const name = (contact.name || contact.notify || '').toLowerCase();
      const phone = id.replace('@s.whatsapp.net', '').replace('@g.us', '');
      return name.includes(queryLower) || phone.includes(query);
    })
    .map(([id, contact]) => ({
      id,
      name: contact.name || contact.notify || 'Unknown',
      phone: id.replace('@s.whatsapp.net', '').replace('@g.us', ''),
      isGroup: id.endsWith('@g.us')
    }));

  console.log(JSON.stringify({ query, results }, null, 2));
}

/**
 * Get detailed info for a specific contact
 * @param {string} phone - Phone number or JID
 */
function getContact(phone) {
  const contacts = loadContacts();
  const jid = phone.includes('@') ? phone : `${phone}@s.whatsapp.net`;

  const contact = contacts[jid];
  if (contact) {
    console.log(JSON.stringify({
      id: jid,
      name: contact.name || contact.notify || 'Unknown',
      phone: jid.replace('@s.whatsapp.net', ''),
      status: contact.status || null,
      imgUrl: contact.imgUrl || null
    }, null, 2));
  } else {
    console.log(JSON.stringify({ error: `Contact ${phone} not found in cache` }));
  }
}

// CLI
const cmd = process.argv[2];
switch (cmd) {
  case 'list': listContacts(process.argv[3] || 50); break;
  case 'search': searchContacts(process.argv[3]); break;
  case 'get': getContact(process.argv[3]); break;
  default:
    console.log(JSON.stringify({
      usage: 'contacts.js [list|search|get] [args]',
      commands: {
        list: 'List contacts: list [limit]',
        search: 'Search contacts: search <query>',
        get: 'Get contact info: get <phone>'
      }
    }, null, 2));
}
