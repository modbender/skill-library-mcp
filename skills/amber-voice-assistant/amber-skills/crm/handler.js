/**
 * CRM Skill — Contact memory and interaction logging for Amber voice calls
 *
 * Uses SQLite (better-sqlite3) to store contacts and interactions locally.
 * All functions are synchronous — fast, no latency for voice calls.
 */

const Database = require('better-sqlite3');
const fs = require('fs');
const path = require('path');
const os = require('os');

// ============================================================================
// Database Initialization
// ============================================================================

let _db = null;

/**
 * Simple ULID implementation (timestamp + random)
 * ULIDs sort chronologically and are sortable in databases.
 * Format: 10-char timestamp + 6-char random = 16 chars total.
 * This is much simpler than pulling in a package.
 */
function ulid() {
  const timestamp = Date.now().toString(36).padStart(10, '0');
  const random = Math.random().toString(36).slice(2, 8).padEnd(6, '0');
  return (timestamp + random).slice(0, 16);
}

/**
 * Get or initialize the SQLite database connection.
 */
function getDb() {
  if (!_db) {
    const dbPath = process.env.AMBER_CRM_DB_PATH || 
      path.join(os.homedir(), '.config/amber/crm.sqlite');
    
    // Create directory if it doesn't exist
    fs.mkdirSync(path.dirname(dbPath), { recursive: true });
    
    // Open DB with WAL mode for concurrent reads + serialized writes
    _db = new Database(dbPath, { verbose: null });
    _db.pragma('journal_mode = WAL');
    _db.pragma('foreign_keys = ON');
    
    // Initialize schema if needed
    migrate(_db);
  }
  return _db;
}

/**
 * Schema migration. Run this once at startup.
 */
function migrate(db) {
  // Check current schema version
  const userVersion = db.pragma('user_version')[0].user_version;
  if (userVersion >= 1) return; // Already migrated

  // Create tables
  db.exec(`
    CREATE TABLE IF NOT EXISTS contacts (
      id          TEXT PRIMARY KEY,
      phone       TEXT UNIQUE,
      email       TEXT,
      name        TEXT,
      company     TEXT,
      notes       TEXT,
      context_notes TEXT,
      tags        TEXT DEFAULT '[]',
      source      TEXT DEFAULT 'inbound_call',
      external_id TEXT,
      created_at  TEXT NOT NULL,
      updated_at  TEXT NOT NULL
    );

    CREATE INDEX IF NOT EXISTS idx_contacts_phone ON contacts(phone);
    CREATE INDEX IF NOT EXISTS idx_contacts_email ON contacts(email) WHERE email IS NOT NULL;
    CREATE INDEX IF NOT EXISTS idx_contacts_name ON contacts(name) WHERE name IS NOT NULL;

    CREATE TABLE IF NOT EXISTS interactions (
      id           TEXT PRIMARY KEY,
      contact_id   TEXT NOT NULL REFERENCES contacts(id),
      call_sid     TEXT,
      direction    TEXT NOT NULL DEFAULT 'inbound',
      summary      TEXT,
      outcome      TEXT,
      details      TEXT DEFAULT '{}',
      duration_sec INTEGER,
      created_at   TEXT NOT NULL
    );

    CREATE INDEX IF NOT EXISTS idx_interactions_contact ON interactions(contact_id);
    CREATE INDEX IF NOT EXISTS idx_interactions_call_sid ON interactions(call_sid) WHERE call_sid IS NOT NULL;
  `);

  // Mark migration complete
  db.pragma('user_version = 1');
}

// ============================================================================
// Input Validation Helpers (same pattern as calendar skill)
// ============================================================================

/** Strip control characters and limit length */
function safeFreeText(val, maxLen = 200) {
  if (typeof val !== 'string') return null;
  const cleaned = val.replace(/[\x00-\x1f\x7f]/g, '').slice(0, maxLen);
  return cleaned || null;
}

/** Validate E.164 phone format */
function validatePhone(phone) {
  if (!phone) return false;
  return /^\+[1-9]\d{6,14}$/.test(phone);
}

/** Check if a phone number is blocked/private and should be skipped */
function isPrivateNumber(phone) {
  if (!phone) return true;
  // Skip: null, empty, 'anonymous', 'blocked', 'unknown', or TCPA-type placeholder
  const lower = phone.toLowerCase();
  if (lower === 'anonymous' || lower === 'blocked' || lower === 'unknown') return true;
  if (!phone.startsWith('+')) return true; // Not E.164 format
  if (phone === '+12661234567' || phone === '+18005551212') return true; // Known TCPA placeholders
  return false;
}

/** Parse JSON safely */
function parseJSON(str, defaultVal = {}) {
  if (!str) return defaultVal;
  try {
    return JSON.parse(str);
  } catch (_) {
    return defaultVal;
  }
}

// ============================================================================
// Action Handlers
// ============================================================================

/**
 * Action: lookup_contact
 * Fetch a contact by phone or name. Returns contact + last 5 interactions.
 */
async function handleLookupContact(params, context) {
  const { phone, name } = params;

  try {
    const db = getDb();

    // Check if phone is private/blocked — skip CRM entirely for these
    if (phone && isPrivateNumber(phone)) {
      return {
        success: false,
        skipped: true,
        reason: 'private_number',
        message: 'Private or blocked number — skipping CRM lookup.'
      };
    }

    // Lookup by phone (primary) or name (fallback)
    let contact = null;
    if (phone) {
      const stmt = db.prepare('SELECT * FROM contacts WHERE phone = ?');
      contact = stmt.get(phone);
    } else if (name) {
      const safeSearch = safeFreeText(name, 100);
      if (safeSearch) {
        const stmt = db.prepare('SELECT * FROM contacts WHERE name LIKE ?');
        contact = stmt.get(`%${safeSearch}%`);
      }
    }

    if (!contact) {
      return {
        success: true,
        result: null,
        message: 'Contact not found.'
      };
    }

    // Fetch last 5 interactions
    const stmt = db.prepare(`
      SELECT * FROM interactions 
      WHERE contact_id = ? 
      ORDER BY created_at DESC 
      LIMIT 5
    `);
    const interactions = stmt.all(contact.id);

    // Parse details and context_notes
    contact.tags = parseJSON(contact.tags, []);
    const interactionsWithDetails = interactions.map(i => ({
      ...i,
      details: parseJSON(i.details)
    }));

    return {
      success: true,
      result: {
        contact,
        interactions: interactionsWithDetails
      },
      message: `Found contact: ${contact.name || contact.phone}`
    };
  } catch (e) {
    try {
      context.callLog?.write({
        type: 'skill.crm.error',
        action: 'lookup_contact',
        error: e.message
      });
    } catch (_) {}
    return {
      success: false,
      error: e.message,
      message: 'Error looking up contact. Continuing anyway.'
    };
  }
}

/**
 * Action: upsert_contact
 * Create or update a contact. Phone is the merge key.
 * Only provided fields are updated; missing/null fields are left unchanged.
 */
async function handleUpsertContact(params, context) {
  const { phone, name, email, company, context_notes } = params;

  try {
    if (!phone || !validatePhone(phone)) {
      return {
        success: false,
        error: 'Invalid or missing phone number',
        message: 'Phone number required in E.164 format.'
      };
    }

    // Skip private numbers
    if (isPrivateNumber(phone)) {
      return {
        success: false,
        skipped: true,
        reason: 'private_number',
        message: 'Private number — not saving to CRM.'
      };
    }

    const db = getDb();
    const now = new Date().toISOString();

    // Check if contact exists
    const existing = db.prepare('SELECT * FROM contacts WHERE phone = ?').get(phone);

    if (existing) {
      // Update existing contact (only provided fields)
      const updates = {};
      if (name !== undefined && name !== null) updates.name = safeFreeText(name, 200);
      if (email !== undefined && email !== null) updates.email = safeFreeText(email, 200);
      if (company !== undefined && company !== null) updates.company = safeFreeText(company, 200);
      if (context_notes !== undefined) updates.context_notes = safeFreeText(context_notes, 1000);
      updates.updated_at = now;

      if (Object.keys(updates).length > 0) {
        const cols = Object.keys(updates);
        const values = Object.values(updates);
        const setClause = cols.map(c => `${c} = ?`).join(', ');
        db.prepare(`UPDATE contacts SET ${setClause} WHERE phone = ?`)
          .run(...values, phone);
      }

      const updated = db.prepare('SELECT * FROM contacts WHERE phone = ?').get(phone);
      updated.tags = parseJSON(updated.tags, []);
      return {
        success: true,
        result: updated,
        message: `Updated contact: ${updated.name || phone}`
      };
    } else {
      // Create new contact
      const id = ulid();
      const safeName = name ? safeFreeText(name, 200) : null;
      const safeEmail = email ? safeFreeText(email, 200) : null;
      const safeCompany = company ? safeFreeText(company, 200) : null;
      const safeContextNotes = context_notes ? safeFreeText(context_notes, 1000) : null;

      db.prepare(`
        INSERT INTO contacts (id, phone, name, email, company, context_notes, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
      `).run(id, phone, safeName, safeEmail, safeCompany, safeContextNotes, now, now);

      const contact = db.prepare('SELECT * FROM contacts WHERE id = ?').get(id);
      contact.tags = parseJSON(contact.tags, []);
      return {
        success: true,
        result: contact,
        message: `Created contact: ${contact.name || phone}`
      };
    }
  } catch (e) {
    try {
      context.callLog?.write({
        type: 'skill.crm.error',
        action: 'upsert_contact',
        error: e.message
      });
    } catch (_) {}
    return {
      success: false,
      error: e.message,
      message: 'Error saving contact.'
    };
  }
}

/**
 * Action: log_interaction
 * Log a call interaction. Auto-creates contact if phone not found.
 */
async function handleLogInteraction(params, context) {
  const { phone, summary, outcome, details } = params;

  try {
    if (!phone || !validatePhone(phone)) {
      return {
        success: false,
        error: 'Invalid or missing phone number',
        message: 'Phone number required.'
      };
    }

    // Skip private numbers
    if (isPrivateNumber(phone)) {
      return {
        success: false,
        skipped: true,
        reason: 'private_number',
        message: 'Private number — not logging.'
      };
    }

    const db = getDb();
    const now = new Date().toISOString();

    // Ensure contact exists
    let contact = db.prepare('SELECT id FROM contacts WHERE phone = ?').get(phone);
    if (!contact) {
      const id = ulid();
      db.prepare(`
        INSERT INTO contacts (id, phone, created_at, updated_at)
        VALUES (?, ?, ?, ?)
      `).run(id, phone, now, now);
      contact = { id };
    }

    // Log the interaction
    const interactionId = ulid();
    const safeSummary = summary ? safeFreeText(summary, 500) : null;
    const safeOutcome = (outcome && ['message_left', 'appointment_booked', 'info_provided', 'callback_requested', 'transferred', 'other'].includes(outcome)) 
      ? outcome 
      : 'other';
    const detailsStr = details ? JSON.stringify(details) : '{}';
    const direction = context.direction || 'inbound';
    const callSid = context.callSid || null;

    db.prepare(`
      INSERT INTO interactions (id, contact_id, call_sid, direction, summary, outcome, details, created_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    `).run(interactionId, contact.id, callSid, direction, safeSummary, safeOutcome, detailsStr, now);

    return {
      success: true,
      result: { interactionId, contactId: contact.id },
      message: `Logged interaction for ${phone}`
    };
  } catch (e) {
    try {
      context.callLog?.write({
        type: 'skill.crm.error',
        action: 'log_interaction',
        error: e.message
      });
    } catch (_) {}
    return {
      success: false,
      error: e.message,
      message: 'Error logging interaction.'
    };
  }
}

/**
 * Action: get_history
 * Get interaction history for a contact.
 */
async function handleGetHistory(params, context) {
  const { phone, limit = 10 } = params;

  try {
    if (!phone || !validatePhone(phone)) {
      return {
        success: false,
        error: 'Invalid phone number'
      };
    }

    const db = getDb();
    const contact = db.prepare('SELECT id FROM contacts WHERE phone = ?').get(phone);

    if (!contact) {
      return {
        success: true,
        result: [],
        message: 'No interactions found.'
      };
    }

    const stmt = db.prepare(`
      SELECT * FROM interactions 
      WHERE contact_id = ? 
      ORDER BY created_at DESC 
      LIMIT ?
    `);
    const interactions = stmt.all(contact.id, Math.min(limit, 50));
    const withDetails = interactions.map(i => ({
      ...i,
      details: parseJSON(i.details)
    }));

    return {
      success: true,
      result: withDetails,
      message: `Found ${withDetails.length} interactions.`
    };
  } catch (e) {
    return {
      success: false,
      error: e.message
    };
  }
}

/**
 * Action: search_contacts
 * Search contacts by name, email, company, notes.
 */
async function handleSearchContacts(params, context) {
  const { query, limit = 10 } = params;

  try {
    if (!query) {
      return {
        success: false,
        error: 'Query required'
      };
    }

    const db = getDb();
    const safeQuery = safeFreeText(query, 200);
    const pattern = `%${safeQuery}%`;

    const stmt = db.prepare(`
      SELECT * FROM contacts 
      WHERE name LIKE ? OR email LIKE ? OR company LIKE ? OR notes LIKE ?
      LIMIT ?
    `);
    const contacts = stmt.all(pattern, pattern, pattern, pattern, Math.min(limit, 50));
    const withTags = contacts.map(c => ({
      ...c,
      tags: parseJSON(c.tags, [])
    }));

    return {
      success: true,
      result: withTags,
      message: `Found ${withTags.length} contacts.`
    };
  } catch (e) {
    return {
      success: false,
      error: e.message
    };
  }
}

/**
 * Action: tag_contact
 * Add or remove tags from a contact.
 */
async function handleTagContact(params, context) {
  const { phone, add = [], remove = [] } = params;

  try {
    if (!phone || !validatePhone(phone)) {
      return {
        success: false,
        error: 'Invalid phone number'
      };
    }

    const db = getDb();
    const contact = db.prepare('SELECT id, tags FROM contacts WHERE phone = ?').get(phone);

    if (!contact) {
      return {
        success: false,
        error: 'Contact not found'
      };
    }

    let tags = parseJSON(contact.tags, []);

    // Add tags
    for (const tag of add) {
      const safeTag = safeFreeText(tag, 50);
      if (safeTag && !tags.includes(safeTag)) {
        tags.push(safeTag);
      }
    }

    // Remove tags
    for (const tag of remove) {
      tags = tags.filter(t => t !== tag);
    }

    const now = new Date().toISOString();
    db.prepare('UPDATE contacts SET tags = ?, updated_at = ? WHERE phone = ?')
      .run(JSON.stringify(tags), now, phone);

    return {
      success: true,
      result: { tags },
      message: `Updated tags for ${phone}`
    };
  } catch (e) {
    return {
      success: false,
      error: e.message
    };
  }
}

// ============================================================================
// Main Handler
// ============================================================================

module.exports = async function crmHandler(params, context) {
  const { action } = params;

  try {
    switch (action) {
      case 'lookup_contact':
        return await handleLookupContact(params, context);
      case 'upsert_contact':
        return await handleUpsertContact(params, context);
      case 'log_interaction':
        return await handleLogInteraction(params, context);
      case 'get_history':
        return await handleGetHistory(params, context);
      case 'search_contacts':
        return await handleSearchContacts(params, context);
      case 'tag_contact':
        return await handleTagContact(params, context);
      default:
        return {
          success: false,
          error: `Unknown action: ${action}`,
          message: `CRM supports: lookup_contact, upsert_contact, log_interaction, get_history, search_contacts, tag_contact`
        };
    }
  } catch (e) {
    try {
      context.callLog?.write({
        type: 'skill.crm.fatal',
        action,
        error: e.message
      });
    } catch (_) {}
    return {
      success: false,
      error: e.message,
      message: 'CRM error. Continuing call.'
    };
  }
};
