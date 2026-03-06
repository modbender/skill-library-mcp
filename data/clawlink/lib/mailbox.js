/**
 * ClawLink Mailbox
 * 
 * Persists messages to inbox/ and outbox/ folders as markdown files.
 * Provides a clear audit trail of all ClawLink communications.
 */

import { existsSync, mkdirSync, writeFileSync, readdirSync, readFileSync } from 'fs';
import { homedir } from 'os';
import { join } from 'path';

const DATA_DIR = join(homedir(), '.openclaw', 'clawlink');
const INBOX_DIR = join(DATA_DIR, 'inbox');
const OUTBOX_DIR = join(DATA_DIR, 'outbox');

/**
 * Ensure mailbox directories exist
 */
export function ensureDirectories() {
  if (!existsSync(INBOX_DIR)) {
    mkdirSync(INBOX_DIR, { recursive: true });
  }
  if (!existsSync(OUTBOX_DIR)) {
    mkdirSync(OUTBOX_DIR, { recursive: true });
  }
}

/**
 * Generate a filename from timestamp and sender/recipient
 * Format: YYYY-MM-DD-HHMMSS-name.md
 */
function generateFilename(timestamp, name) {
  const date = new Date(timestamp);
  const dateStr = date.toISOString()
    .replace(/T/, '-')
    .replace(/:/g, '')
    .replace(/\..+/, '')
    .slice(0, 17); // YYYY-MM-DD-HHMMSS
  
  const safeName = name
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '')
    .slice(0, 30);
  
  return `${dateStr}-${safeName}.md`;
}

/**
 * Save a sent message to the outbox
 * 
 * @param {Object} params
 * @param {string} params.to - Recipient name
 * @param {string} params.text - Message text
 * @param {string} params.timestamp - ISO timestamp
 * @param {Object} params.options - Message options (urgency, context)
 * @param {string} params.messageId - ID from relay
 */
export function saveToOutbox({ to, text, timestamp, options = {}, messageId }) {
  ensureDirectories();
  
  const filename = generateFilename(timestamp, to);
  const filepath = join(OUTBOX_DIR, filename);
  
  const content = `---
to: ${to}
timestamp: ${timestamp}
messageId: ${messageId || 'unknown'}
urgency: ${options.urgency || 'normal'}
context: ${options.context || 'personal'}
---

# Message to ${to}

**Sent:** ${new Date(timestamp).toLocaleString()}

---

${text}
`;
  
  writeFileSync(filepath, content);
  return { filename, filepath };
}

/**
 * Save a received message to the inbox
 * 
 * @param {Object} params
 * @param {string} params.from - Sender name
 * @param {string} params.text - Message text  
 * @param {string} params.timestamp - ISO timestamp
 * @param {Object} params.metadata - Additional metadata
 */
export function saveToInbox({ from, text, timestamp, metadata = {} }) {
  ensureDirectories();
  
  const filename = generateFilename(timestamp, from);
  const filepath = join(INBOX_DIR, filename);
  
  const urgency = metadata.urgency || 'normal';
  const context = metadata.context || 'personal';
  
  const content = `---
from: ${from}
timestamp: ${timestamp}
urgency: ${urgency}
context: ${context}
---

# Message from ${from}

**Received:** ${new Date(timestamp).toLocaleString()}
${urgency !== 'normal' ? `**Urgency:** ${urgency}` : ''}
${context !== 'personal' ? `**Context:** ${context}` : ''}

---

${text}
`;
  
  writeFileSync(filepath, content);
  return { filename, filepath };
}

/**
 * List messages in inbox
 * 
 * @param {number} limit - Max messages to return
 * @returns {Array} List of message summaries
 */
export function listInbox(limit = 20) {
  ensureDirectories();
  
  const files = readdirSync(INBOX_DIR)
    .filter(f => f.endsWith('.md'))
    .sort()
    .reverse()
    .slice(0, limit);
  
  return files.map(filename => {
    const filepath = join(INBOX_DIR, filename);
    const content = readFileSync(filepath, 'utf8');
    
    // Parse frontmatter
    const match = content.match(/^---\n([\s\S]*?)\n---/);
    const meta = {};
    if (match) {
      match[1].split('\n').forEach(line => {
        const [key, ...val] = line.split(': ');
        if (key && val.length) meta[key] = val.join(': ');
      });
    }
    
    // Get message body after the --- separator in content
    const body = content.replace(/^---[\s\S]*?---\n/, '').trim();
    const lines = body.split('\n').filter(l => l && !l.startsWith('#') && !l.startsWith('**') && !l.startsWith('---'));
    const preview = lines[0]?.slice(0, 100) || '';
    
    return {
      filename,
      from: meta.from,
      timestamp: meta.timestamp,
      preview
    };
  });
}

/**
 * List messages in outbox
 * 
 * @param {number} limit - Max messages to return
 * @returns {Array} List of message summaries
 */
export function listOutbox(limit = 20) {
  ensureDirectories();
  
  const files = readdirSync(OUTBOX_DIR)
    .filter(f => f.endsWith('.md'))
    .sort()
    .reverse()
    .slice(0, limit);
  
  return files.map(filename => {
    const filepath = join(OUTBOX_DIR, filename);
    const content = readFileSync(filepath, 'utf8');
    
    // Parse frontmatter
    const match = content.match(/^---\n([\s\S]*?)\n---/);
    const meta = {};
    if (match) {
      match[1].split('\n').forEach(line => {
        const [key, ...val] = line.split(': ');
        if (key && val.length) meta[key] = val.join(': ');
      });
    }
    
    // Get message body after the --- separator in content
    const body = content.replace(/^---[\s\S]*?---\n/, '').trim();
    const lines = body.split('\n').filter(l => l && !l.startsWith('#') && !l.startsWith('**') && !l.startsWith('---'));
    const preview = lines[0]?.slice(0, 100) || '';
    
    return {
      filename,
      to: meta.to,
      timestamp: meta.timestamp,
      preview
    };
  });
}

/**
 * Get full message content by filename
 * 
 * @param {string} box - 'inbox' or 'outbox'
 * @param {string} filename - Message filename
 * @returns {string} Full message content
 */
export function getMessage(box, filename) {
  const dir = box === 'inbox' ? INBOX_DIR : OUTBOX_DIR;
  const filepath = join(dir, filename);
  
  if (!existsSync(filepath)) {
    throw new Error(`Message not found: ${filename}`);
  }
  
  return readFileSync(filepath, 'utf8');
}

export default {
  ensureDirectories,
  saveToOutbox,
  saveToInbox,
  listInbox,
  listOutbox,
  getMessage
};
