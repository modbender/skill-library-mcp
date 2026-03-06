#!/usr/bin/env node
// WhatsApp Group Admin - Administrative utilities for WhatsApp groups
// MIT License

const fs = require('fs');
const path = require('path');
const os = require('os');

const CREDS_PATH = path.join(
  process.env.OPENCLAW_STATE_DIR || path.join(os.homedir(), '.openclaw'),
  'credentials', 'whatsapp', 'default'
);

/**
 * Extract creation timestamp from a group ID
 * @param {string} groupId - Group JID
 * @returns {string|null} ISO date string or null
 */
function extractTimestamp(groupId) {
  const match = groupId.match(/-(\\d{10,13})@g\\.us/);
  if (match) {
    const ts = parseInt(match[1]);
    const date = new Date(ts.toString().length === 10 ? ts * 1000 : ts);
    return date.toISOString();
  }
  return null;
}

/**
 * Get detailed information about a specific group
 * @param {string} groupId - Group JID
 */
function groupInfo(groupId) {
  if (!groupId) {
    console.log(JSON.stringify({ error: 'Group ID is required' }));
    return;
  }

  try {
    const files = fs.readdirSync(CREDS_PATH);
    const memberFiles = files.filter(f => f.startsWith('sender-key-') && f.includes(groupId));

    const members = new Set();
    for (const file of memberFiles) {
      const match = file.match(/--(\\d+)_/);
      if (match) members.add(match[1]);
    }

    let name = null;
    try {
      const contactsPath = path.join(CREDS_PATH, 'contacts.json');
      if (fs.existsSync(contactsPath)) {
        const contacts = JSON.parse(fs.readFileSync(contactsPath, 'utf8'));
        if (contacts[groupId]) {
          name = contacts[groupId].name || contacts[groupId].subject;
        }
      }
    } catch (e) { /* contacts not available */ }

    console.log(JSON.stringify({
      id: groupId,
      name,
      memberCount: members.size,
      isGroup: groupId.endsWith('@g.us'),
      createdAt: extractTimestamp(groupId)
    }, null, 2));
  } catch (error) {
    console.log(JSON.stringify({ error: error.message }));
  }
}

/**
 * Generate a template for creating a new group
 * @param {string} name - Desired group name
 */
function createTemplate(name) {
  const template = {
    subject: name || 'New Group',
    participants: ['5511999999999@s.whatsapp.net'],
    description: 'Group description'
  };

  console.log(JSON.stringify({
    info: 'Template for creating a group via API',
    template,
    note: 'Requires an active connection to execute'
  }, null, 2));
}

/**
 * Parse a WhatsApp group invite link
 * @param {string} link - Invite URL
 */
function parseInviteLink(link) {
  const match = link.match(/chat\\.whatsapp\\.com\\/([A-Za-z0-9]+)/);

  if (match) {
    console.log(JSON.stringify({
      valid: true,
      code: match[1],
      fullLink: `https://chat.whatsapp.com/${match[1]}`
    }, null, 2));
  } else {
    console.log(JSON.stringify({
      valid: false,
      error: 'Invalid invite link',
      example: 'https://chat.whatsapp.com/ABC123XYZ'
    }, null, 2));
  }
}

/**
 * List all groups with member count statistics
 */
function listGroupsWithStats() {
  const groups = [];

  try {
    const files = fs.readdirSync(CREDS_PATH);
    const groupData = new Map();

    for (const file of files) {
      if (file.startsWith('sender-key-') && file.includes('@g.us')) {
        const match = file.match(/sender-key-(.+@g\.us)--(\d+)/);
        if (match) {
          const groupId = match[1];
          const memberId = match[2];
          if (!groupData.has(groupId)) {
            groupData.set(groupId, { id: groupId, members: new Set() });
          }
          groupData.get(groupId).members.add(memberId);
        }
      }
    }

    // Enrich with names
    try {
      const contactsPath = path.join(CREDS_PATH, 'contacts.json');
      if (fs.existsSync(contactsPath)) {
        const contacts = JSON.parse(fs.readFileSync(contactsPath, 'utf8'));
        for (const [id, data] of groupData) {
          if (contacts[id]) {
            data.name = contacts[id].name || contacts[id].subject;
          }
        }
      }
    } catch (e) { /* contacts not available */ }

    for (const [id, data] of groupData) {
      groups.push({
        id,
        name: data.name || null,
        memberCount: data.members.size,
        createdAt: extractTimestamp(id)
      });
    }

    groups.sort((a, b) => b.memberCount - a.memberCount);
  } catch (error) {
    console.log(JSON.stringify({ error: error.message }));
    return;
  }

  console.log(JSON.stringify({ total: groups.length, groups }, null, 2));
}

// CLI
const cmd = process.argv[2];
const arg = process.argv.slice(3).join(' ');

switch (cmd) {
  case 'info': groupInfo(arg); break;
  case 'create-template': createTemplate(arg); break;
  case 'parse-link': parseInviteLink(arg); break;
  case 'list': listGroupsWithStats(); break;
  default:
    console.log(JSON.stringify({
      usage: 'admin.js [info|create-template|parse-link|list] [args]',
      commands: {
        info: 'Group info: info <groupId>',
        'create-template': 'Creation template: create-template "Name"',
        'parse-link': 'Parse invite link: parse-link <url>',
        list: 'List groups with statistics'
      }
    }, null, 2));
}
