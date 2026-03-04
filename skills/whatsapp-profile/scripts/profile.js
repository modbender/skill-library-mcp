#!/usr/bin/env node
// WhatsApp Profile - View bot profile and contact profile information
// MIT License

const fs = require('fs');
const path = require('path');
const os = require('os');

const CREDS_PATH = path.join(
  process.env.OPENCLAW_STATE_DIR || path.join(os.homedir(), '.openclaw'),
  'credentials', 'whatsapp', 'default'
);

/**
 * Get the connected bot's own profile information
 */
function getMe() {
  try {
    const credsPath = path.join(CREDS_PATH, 'creds.json');
    if (!fs.existsSync(credsPath)) {
      console.log(JSON.stringify({ error: 'Credentials not found' }));
      return;
    }

    const creds = JSON.parse(fs.readFileSync(credsPath, 'utf8'));
    console.log(JSON.stringify({
      id: creds.me?.id,
      name: creds.me?.name,
      phone: creds.me?.id?.split(':')[0],
      platform: creds.platform,
      registered: creds.registered,
      businessName: creds.me?.verifiedName
    }, null, 2));
  } catch (error) {
    console.log(JSON.stringify({ error: error.message }));
  }
}

/**
 * Get profile information for a specific contact
 * @param {string} phone - Phone number or JID
 */
function getContact(phone) {
  try {
    const cleanPhone = phone.replace(/\D/g, '');
    const jid = cleanPhone.includes('@') ? cleanPhone : `${cleanPhone}@s.whatsapp.net`;

    const contactsPath = path.join(CREDS_PATH, 'contacts.json');
    if (!fs.existsSync(contactsPath)) {
      console.log(JSON.stringify({ phone: cleanPhone, jid, inCache: false, note: 'Contacts file not found' }));
      return;
    }

    const contacts = JSON.parse(fs.readFileSync(contactsPath, 'utf8'));
    const contact = contacts[jid];

    if (contact) {
      console.log(JSON.stringify({
        phone: cleanPhone,
        jid,
        inCache: true,
        name: contact.name || null,
        notify: contact.notify || null,
        status: contact.status || null,
        imgUrl: contact.imgUrl || null
      }, null, 2));
    } else {
      console.log(JSON.stringify({ phone: cleanPhone, jid, inCache: false, note: 'Contact not found in cache' }, null, 2));
    }
  } catch (error) {
    console.log(JSON.stringify({ error: error.message }));
  }
}

/**
 * List contacts that have a known name
 * @param {number} limit - Maximum results
 */
function listContacts(limit = 50) {
  try {
    const contactsPath = path.join(CREDS_PATH, 'contacts.json');
    if (!fs.existsSync(contactsPath)) {
      console.log(JSON.stringify({ error: 'Contacts file not found' }));
      return;
    }

    const contacts = JSON.parse(fs.readFileSync(contactsPath, 'utf8'));
    const result = Object.entries(contacts)
      .filter(([, c]) => c.name || c.notify)
      .slice(0, parseInt(limit))
      .map(([id, c]) => ({
        jid: id,
        name: c.name || c.notify,
        phone: id.replace('@s.whatsapp.net', '').replace('@g.us', '')
      }));

    console.log(JSON.stringify({ total: result.length, contacts: result }, null, 2));
  } catch (error) {
    console.log(JSON.stringify({ error: error.message }));
  }
}

// CLI
const cmd = process.argv[2];
const arg = process.argv[3];

switch (cmd) {
  case 'me': getMe(); break;
  case 'contact':
    if (!arg) { console.error('Usage: profile.js contact <phone>'); process.exit(1); }
    getContact(arg); break;
  case 'list': listContacts(arg || 50); break;
  default:
    console.log(JSON.stringify({
      usage: 'profile.js [me|contact|list] [args]',
      commands: {
        me: 'Show bot profile info',
        contact: 'Get contact profile: contact <phone>',
        list: 'List named contacts: list [limit]'
      }
    }, null, 2));
}
