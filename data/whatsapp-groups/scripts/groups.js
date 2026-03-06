#!/usr/bin/env node
// WhatsApp Groups - Discover and manage groups from Baileys session data
// MIT License

const fs = require('fs');
const path = require('path');
const os = require('os');

const STATE_DIR = process.env.OPENCLAW_STATE_DIR || path.join(os.homedir(), '.openclaw');

const CREDS_PATH = path.join(STATE_DIR, 'credentials', 'whatsapp', 'default');
const CONFIG_PATH = path.join(STATE_DIR, 'openclaw.json');

/**
 * Discover groups from sender-key files in the Baileys session
 * @returns {Array} List of discovered group objects
 */
function discoverGroups() {
  const groups = new Map();

  try {
    const files = fs.readdirSync(CREDS_PATH);

    // Find sender-key files containing @g.us (groups)
    const groupFiles = files.filter(f => f.startsWith('sender-key-') && f.includes('@g.us'));

    for (const file of groupFiles) {
      // Extract group ID from filename: sender-key-GROUPID@g.us--SENDERID.json
      const match = file.match(/sender-key-(.+@g\.us)--/);
      if (match) {
        const groupId = match[1];
        if (!groups.has(groupId)) {
          groups.set(groupId, { id: groupId, name: null, discoveredFrom: file });
        }
      }
    }

    // Enrich with metadata from store
    try {
      const storePath = path.join(CREDS_PATH, 'store.json');
      if (fs.existsSync(storePath)) {
        const store = JSON.parse(fs.readFileSync(storePath, 'utf8'));
        if (store.chats) {
          for (const [chatId, chatData] of Object.entries(store.chats)) {
            if (chatId.endsWith('@g.us') && groups.has(chatId)) {
              groups.get(chatId).name = chatData.name || chatData.subject || null;
            }
          }
        }
      }
    } catch (e) { /* store not available */ }

    // Try loading names from contacts file
    try {
      const contactsPath = path.join(CREDS_PATH, 'contacts.json');
      if (fs.existsSync(contactsPath)) {
        const contacts = JSON.parse(fs.readFileSync(contactsPath, 'utf8'));
        for (const [id, contact] of Object.entries(contacts)) {
          if (id.endsWith('@g.us') && groups.has(id)) {
            const group = groups.get(id);
            if (!group.name) {
              group.name = contact.name || contact.notify || contact.subject || null;
            }
          }
        }
      }
    } catch (e) { /* contacts not available */ }

  } catch (error) {
    console.error(JSON.stringify({ error: `Failed to discover groups: ${error.message}` }));
    process.exit(1);
  }

  return Array.from(groups.values());
}

/**
 * Load OpenClaw configuration
 * @returns {Object|null} Config object or null
 */
function loadConfig() {
  try {
    if (fs.existsSync(CONFIG_PATH)) {
      return JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
    }
  } catch (e) { /* config not available */ }
  return null;
}

/**
 * Extract a readable name from a group ID
 * @param {string} groupId - Group JID
 * @returns {string} Human-readable fallback name
 */
function extractNameFromId(groupId) {
  const parts = groupId.replace('@g.us', '').split('-');
  if (parts.length >= 2) {
    return `Group ${parts[0].slice(-4)}`;
  }
  return 'Unknown Group';
}

/**
 * List all discovered groups
 */
function listGroups() {
  const groups = discoverGroups();
  const config = loadConfig();
  const activeGroups = config?.channels?.whatsapp?.groups || {};

  const enrichedGroups = groups.map(g => ({
    id: g.id,
    name: g.name || extractNameFromId(g.id),
    isActive: !!activeGroups[g.id]
  }));

  console.log(JSON.stringify({ total: enrichedGroups.length, groups: enrichedGroups }, null, 2));
}

/**
 * Search groups by name
 * @param {string} query - Search term
 */
function searchGroups(query) {
  const groups = discoverGroups();
  const queryLower = query.toLowerCase();

  const results = groups
    .filter(g => {
      const name = (g.name || extractNameFromId(g.id)).toLowerCase();
      return name.includes(queryLower) || g.id.includes(query);
    })
    .map(g => ({ id: g.id, name: g.name || extractNameFromId(g.id) }));

  console.log(JSON.stringify({ query, total: results.length, results }, null, 2));
}

/**
 * Get the ID of a group by name
 * @param {string} query - Group name to search for
 */
function getGroupId(query) {
  const groups = discoverGroups();
  const queryLower = query.toLowerCase();

  const found = groups.find(g => {
    const name = (g.name || '').toLowerCase();
    return name.includes(queryLower);
  });

  if (found) {
    console.log(JSON.stringify({
      id: found.id,
      name: found.name || extractNameFromId(found.id),
      copyPaste: found.id
    }, null, 2));
  } else {
    console.log(JSON.stringify({
      error: `Group "${query}" not found`,
      hint: 'Use the "list" command to see all available groups'
    }, null, 2));
  }
}

/**
 * Sync discovered groups with openclaw.json config
 */
function syncGroups() {
  const groups = discoverGroups();
  const config = loadConfig();

  if (!config) {
    console.log(JSON.stringify({ error: 'Could not load openclaw.json' }));
    return;
  }

  if (!config.channels) config.channels = {};
  if (!config.channels.whatsapp) config.channels.whatsapp = {};
  if (!config.channels.whatsapp.groups) config.channels.whatsapp.groups = {};

  const existingGroups = config.channels.whatsapp.groups;
  const newGroups = [];

  for (const group of groups) {
    if (!existingGroups[group.id]) {
      existingGroups[group.id] = {
        enabled: false,
        name: group.name || extractNameFromId(group.id),
        requireMention: true
      };
      newGroups.push(group.id);
    }
  }

  if (newGroups.length > 0) {
    fs.writeFileSync(CONFIG_PATH, JSON.stringify(config, null, 2), 'utf8');
  }

  console.log(JSON.stringify({
    totalDiscovered: groups.length,
    newGroupsAdded: newGroups.length,
    newGroups,
    message: newGroups.length > 0
      ? `Added ${newGroups.length} new groups. Edit openclaw.json to enable them.`
      : 'No new groups discovered.'
  }, null, 2));
}

// CLI
const cmd = process.argv[2];
const arg = process.argv[3];

switch (cmd) {
  case 'list': listGroups(); break;
  case 'search':
    if (!arg) { console.error('Usage: groups.js search <query>'); process.exit(1); }
    searchGroups(arg); break;
  case 'get-id':
    if (!arg) { console.error('Usage: groups.js get-id <group-name>'); process.exit(1); }
    getGroupId(arg); break;
  case 'sync': syncGroups(); break;
  default:
    console.log(JSON.stringify({
      usage: 'groups.js [list|search|get-id|sync] [args]',
      commands: {
        list: 'List all discovered groups',
        search: 'Search groups by name: search <query>',
        'get-id': 'Get group ID by name: get-id <name>',
        sync: 'Sync groups with openclaw.json'
      }
    }, null, 2));
}
