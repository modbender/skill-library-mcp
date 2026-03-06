#!/usr/bin/env node
// WhatsApp Common Groups - Find shared groups and check membership
// MIT License

const fs = require('fs');
const path = require('path');
const os = require('os');

const CREDS_PATH = path.join(
  process.env.OPENCLAW_STATE_DIR || path.join(os.homedir(), '.openclaw'),
  'credentials', 'whatsapp', 'default'
);

/**
 * Find all groups that a phone number participates in
 * @param {string} phone - Phone number to search for
 */
function findCommonGroups(phone) {
  const cleanPhone = phone.replace(/\D/g, '');
  const groups = [];

  try {
    const files = fs.readdirSync(CREDS_PATH);
    const memberFiles = files.filter(f =>
      f.startsWith('sender-key-') && f.includes('@g.us') && f.includes(cleanPhone)
    );

    const groupIds = new Set();
    for (const file of memberFiles) {
      const match = file.match(/sender-key-(.+@g\.us)--/);
      if (match && !groupIds.has(match[1])) {
        groupIds.add(match[1]);
        groups.push({ id: match[1], name: null });
      }
    }

    // Enrich with names
    try {
      const contactsPath = path.join(CREDS_PATH, 'contacts.json');
      if (fs.existsSync(contactsPath)) {
        const contacts = JSON.parse(fs.readFileSync(contactsPath, 'utf8'));
        for (const group of groups) {
          if (contacts[group.id]) {
            group.name = contacts[group.id].name || contacts[group.id].subject;
          }
        }
      }
    } catch (e) { /* contacts not available */ }

  } catch (error) {
    console.log(JSON.stringify({ error: error.message }));
    return;
  }

  console.log(JSON.stringify({ phone: cleanPhone, totalGroups: groups.length, groups }, null, 2));
}

/**
 * Check if a phone number is a member of a specific group
 * @param {string} phone - Phone number
 * @param {string} groupId - Group JID
 */
function checkInGroup(phone, groupId) {
  const cleanPhone = phone.replace(/\D/g, '');

  try {
    const files = fs.readdirSync(CREDS_PATH);
    const found = files.some(f =>
      f.startsWith('sender-key-') && f.includes(groupId) && f.includes(cleanPhone)
    );

    console.log(JSON.stringify({
      phone: cleanPhone,
      groupId,
      isMember: found,
      note: found ? 'Number found in group' : 'Number not found in group'
    }, null, 2));
  } catch (error) {
    console.log(JSON.stringify({ error: error.message }));
  }
}

/**
 * List all known members across all groups, sorted by group count
 * @param {number} limit - Maximum results
 */
function listAllMembers(limit = 50) {
  const members = new Map();

  try {
    const files = fs.readdirSync(CREDS_PATH);

    for (const file of files) {
      if (file.startsWith('sender-key-') && file.includes('@g.us')) {
        const match = file.match(/--(\d+)_/);
        if (match) {
          const phone = match[1];
          if (!members.has(phone)) {
            members.set(phone, { phone, groupCount: 0 });
          }
          members.get(phone).groupCount++;
        }
      }
    }
  } catch (error) {
    console.log(JSON.stringify({ error: error.message }));
    return;
  }

  const result = Array.from(members.values())
    .sort((a, b) => b.groupCount - a.groupCount)
    .slice(0, parseInt(limit));

  console.log(JSON.stringify({ total: members.size, showing: result.length, members: result }, null, 2));
}

// CLI
const cmd = process.argv[2];
const arg1 = process.argv[3];
const arg2 = process.argv[4];

switch (cmd) {
  case 'find':
    if (!arg1) { console.error('Usage: common.js find <phone>'); process.exit(1); }
    findCommonGroups(arg1); break;
  case 'check':
    if (!arg1 || !arg2) { console.error('Usage: common.js check <phone> <groupId>'); process.exit(1); }
    checkInGroup(arg1, arg2); break;
  case 'all-members': listAllMembers(arg1 || 50); break;
  default:
    console.log(JSON.stringify({
      usage: 'common.js [find|check|all-members] [args]',
      commands: {
        find: 'Find common groups: find <phone>',
        check: 'Check membership: check <phone> <groupId>',
        'all-members': 'List all members: all-members [limit]'
      }
    }, null, 2));
}
