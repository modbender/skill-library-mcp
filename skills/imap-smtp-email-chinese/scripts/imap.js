#!/usr/bin/env node

/**
 * IMAP Email CLI - imapflow version
 * Works with any standard IMAP server (QQ, 163, Gmail, Fastmail, etc.)
 * Better UTF-8/Chinese support with imapflow
 */

const { ImapFlow } = require('imapflow');
const { simpleParser } = require('mailparser');
const path = require('path');
const fs = require('fs');
require('dotenv').config({ path: path.resolve(__dirname, '../.env') });

// IMAP ID information for server compatibility (163.com, QQ, etc.)
const IMAP_ID = {
  name: 'moltbot',
  version: '0.0.1',
  vendor: 'netease',
  'support-email': 'kefu@188.com'
};

const DEFAULT_MAILBOX = process.env.IMAP_MAILBOX || 'INBOX';

// Parse command-line arguments
function parseArgs() {
  const args = process.argv.slice(2);
  const command = args[0];
  const options = {};
  const positional = [];

  for (let i = 1; i < args.length; i++) {
    const arg = args[i];
    if (arg.startsWith('--')) {
      const key = arg.slice(2);
      const value = args[i + 1];
      options[key] = value || true;
      if (value && !value.startsWith('--')) i++;
    } else {
      positional.push(arg);
    }
  }

  return { command, options, positional };
}

// Create imapflow connection config
function createImapConfig() {
  return {
    host: process.env.IMAP_HOST || '127.0.0.1',
    port: parseInt(process.env.IMAP_PORT) || 993,
    secure: process.env.IMAP_TLS === 'true',
    auth: {
      user: process.env.IMAP_USER,
      pass: process.env.IMAP_PASS,
    },
    // Enable UTF-8 acceptance for better Chinese support
    enableUTF8Accept: true,
    // Connection timeouts
    connectionTimeout: 10000,
    authTimeout: 10000,
    // Skip TLS verification if needed (for testing)
    tls: {
      rejectUnauthorized: process.env.IMAP_REJECT_UNAUTHORIZED !== 'false',
    },
    // IMAP ID extension for server compatibility
    id: IMAP_ID,
    logger: false,
  };
}

// Connect to IMAP server
async function connect() {
  const config = createImapConfig();

  if (!config.auth.user || !config.auth.pass) {
    throw new Error('Missing IMAP_USER or IMAP_PASS environment variables');
  }

  const client = new ImapFlow(config);
  await client.connect();
  return client;
}

// Open mailbox (folder)
async function openMailbox(client, mailbox, readOnly = true) {
  //return await client.mailboxOpen(mailbox, { readOnly });
  return await client.getMailboxLock(mailbox, { readOnly: readOnly });
}

// Parse email from raw source or structured data
async function parseEmail(source, includeAttachments = false) {
  const parsed = await simpleParser(source);

  return {
    from: parsed.from?.text || 'Unknown',
    to: parsed.to?.text,
    subject: parsed.subject || '(no subject)',
    date: parsed.date,
    text: parsed.text,
    html: parsed.html,
    snippet: parsed.text
      ? parsed.text.slice(0, 200)
      : (parsed.html ? parsed.html.slice(0, 200).replace(/<[^>]*>/g, '') : ''),
    attachments: parsed.attachments?.map((a) => ({
      filename: a.filename,
      contentType: a.contentType,
      size: a.size,
      content: includeAttachments ? a.content : undefined,
      cid: a.cid,
    })),
  };
}

// Build search criteria for imapflow (SearchObject format)
function buildSearchCriteria(options) {
  const criteria = {};  // 🔑 用对象而非数组

  // Status flags
  if (options.unseen) criteria.seen = false;  // ✅ unseen = seen: false
  if (options.seen) criteria.seen = true;
  if (options.flagged) criteria.flagged = true;
  if (options.answered) criteria.answered = true;

  // Header-based searches (imapflow handles UTF-8)
  if (options.from) criteria.from = options.from;
  if (options.subject) criteria.subject = options.subject;  // ✅ 中文直接写
  if (options.to) criteria.to = options.to;

  // Date-based searches
  if (options.recent) {
    // 🔑 parseRelativeTime 应返回 "DD-Mmm-YYYY" 格式
    criteria.since = parseRelativeTime(options.recent);
  } else {
    if (options.since) {
      const d = new Date(options.since);
      criteria.since = formatImapDate(d);  // 🔑 转 IMAP 格式
    }
    if (options.before) {
      const d = new Date(options.before);
      criteria.before = formatImapDate(d);
    }
  }

  // UID search
  if (options.uid) {
    criteria.uid = options.uid;  // 可以是数字或范围字符串 "123:456"
  }

  // 🔑 默认返回 ALL（字符串或对象均可）
  if (Object.keys(criteria).length === 0) {
    return { all: true };  // 或 return 'ALL'
  }

  // 🔑 直接返回扁平对象，imapflow 自动按 AND 组合
  return criteria;
}

// Fetch and parse messages from UIDs
async function fetchAndParseMessages(client, uids, limit = 25) {
  const results = [];

  for (const uid of uids) {
    try {
      //console.log('message uid:', uid);
      // Fetch message with source for parsing
      const message = await client.fetchOne(uid, {
        source: true,
        envelope: true,
        flags: true,
        uid: true,
      }, { uid: true });

      if (!message || !message.source) continue;

      const parsed = await parseEmail(message.source);
     
      results.push({
        uid: message.uid,
        seq: message.seq,
        flags: message.flags,
        ...parsed,
      });
      //console.log('Parsed message:', message.uid);
    } catch (err) {
      console.warn(`Failed to fetch UID ${uid}: ${err.message}`);
    }
  }
  // Sort messages by date (newest first)
  results.sort((a, b) => new Date(b.date) - new Date(a.date));
  return results.slice(0, limit);
}

function formatImapDate(date) {
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  
  const d = new Date(date);
  const day = String(d.getUTCDate()).padStart(2, '0');
  const month = months[d.getUTCMonth()];
  const year = d.getUTCFullYear();
  
  return `${day}-${month}-${year}`;
}

// Parse relative time (e.g., "2h", "30m", "7d") to Date
function parseRelativeTime(timeStr) {
  const match = timeStr.match(/^(\d+)(m|h|d)$/);
  if (!match) {
    throw new Error('Invalid time format. Use: 30m, 2h, 7d');
  }

  const value = parseInt(match[1]);
  const unit = match[2];
  const now = new Date();

  let past;
  switch (unit) {
    case 'm': past = new Date(now.getTime() - value * 60 * 1000); break;
    case 'h': past = new Date(now.getTime() - value * 60 * 60 * 1000); break;
    case 'd': past = new Date(now.getTime() - value * 24 * 60 * 60 * 1000); break;
    default: throw new Error('Unknown time unit');
  }
  
  // 🔑 关键：返回 IMAP 标准格式字符串，而非 Date 对象或 ISO 字符串
  return formatImapDate(past);
}

// Check for new/unread emails
async function checkEmails(mailbox = DEFAULT_MAILBOX, limit = 10, recentTime = null, unreadOnly = false) {
  const client = await connect();
  //打印 unreadOnly
  //console.log('recentTime:', recentTime);
  try {
    const lock = await openMailbox(client, mailbox, { readOnly: true });  

    const criteria = {};
    if (unreadOnly) {
      criteria.unseen = true; 
    }
    if (recentTime) {
       criteria.since = parseRelativeTime(recentTime);
    }
    if (Object.keys(criteria).length === 0) {
      criteria.all = true;
    }
      
    console.log('🔍 Search criteria:', JSON.stringify(criteria, null, 2));
    const searchResult = await client.search(criteria, { uid: true });
    const uids = Array.isArray(searchResult) ? searchResult : [];
    
    if (uids.length === 0) {
        return [];
    }
    
    // Sort by date (newest first) - imapflow returns in arbitrary order
    const messages = await fetchAndParseMessages(client, uids, limit);

    return messages;
  } finally {
    await client.logout();
  }
}

// Fetch full email by UID
async function fetchEmail(uid, mailbox = DEFAULT_MAILBOX) {
  const client = await connect();
  const results = [];
  try {
    const lock = await openMailbox(client, mailbox);
    
    // Fetch message with source for parsing
    const message = await client.fetchOne(uid, {
      source: true,
      envelope: true,
      flags: true,
      uid: true,
    }, { uid: true });
    const parsed = await parseEmail(message.source);
    
    results.push({
      uid: message.uid,
      seq: message.seq,
      flags: message.flags,
      ...parsed,
    });
  

    return results;
  } finally {
    await client.logout();
  }
}

// Download attachments from email
async function downloadAttachments(uid, mailbox = DEFAULT_MAILBOX, outputDir = '.', specificFilename = null) {
  const client = await connect();

  try {
    await openMailbox(client, mailbox);

    // Fetch message with attachments
    const message = await client.fetchOne(uid, {
      source: true,
      attachments: true,
      envelope: true,
    }, { uid: true });

    if (!message) {
      throw new Error(`Message UID ${uid} not found`);
    }

    const parsed = await parseEmail(message.source, true);

    if (!parsed.attachments || parsed.attachments.length === 0) {
      return {
        uid,
        downloaded: [],
        message: 'No attachments found',
      };
    }

    // Create output directory
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }

    const downloaded = [];

    for (const attachment of parsed.attachments) {
      if (specificFilename && attachment.filename !== specificFilename) {
        continue;
      }
      if (attachment.content) {
        const filePath = path.join(outputDir, attachment.filename);
        fs.writeFileSync(filePath, attachment.content);
        downloaded.push({
          filename: attachment.filename,
          path: filePath,
          size: attachment.size,
        });
      }
    }

    if (specificFilename && downloaded.length === 0) {
      const availableFiles = parsed.attachments.map(a => a.filename).join(', ');
      return {
        uid,
        downloaded: [],
        message: `File "${specificFilename}" not found. Available: ${availableFiles}`,
      };
    }

    return {
      uid,
      downloaded,
      message: `Downloaded ${downloaded.length} attachment(s)`,
    };
  } finally {
    await client.logout();
  }
}

// Search emails with criteria
async function searchEmails(options) {
  const client = await connect();

  try {
    const mailbox = options.mailbox || DEFAULT_MAILBOX;
    const lock = await openMailbox(client, mailbox, { readOnly: true });

    const criteria = buildSearchCriteria(options);
    console.log('🔍 Search criteria:', JSON.stringify(criteria, null, 2));
    const searchResult = await client.search(criteria, { uid: true });
    console.log('Found', searchResult);
    // Convert to array (imapflow returns Set or Map)
    const uids =  Array.isArray(searchResult) ? searchResult : [];
    
    if (uids.length === 0) {
        return [];
    }
    
    const limit = parseInt(options.limit) || 100;
    const results = await fetchAndParseMessages(client, uids, limit);
    return results;
  } finally {
    await client.logout();
  }
}

// Mark message(s) as read/unread
async function updateFlags(uids, flags, action, mailbox = DEFAULT_MAILBOX) {
  const client = await connect();

  try {
    // 🔑 使用 getMailboxLock（可写）
    const lock = await client.getMailboxLock(mailbox, { readOnly: false });

    try {
      // 🔑 转为字符串范围格式 "123,456,789"
      const uidArray = Array.isArray(uids) ? uids.map(Number) : [Number(uids)];
      const range = uidArray.join(',');

      // 🔑 标志可以是字符串或数组
      const flagArray = Array.isArray(flags) ? flags : [flags];

      if (action === 'add') {
        await client.messageFlagsAdd(range, flagArray, { uid: true });
      } else if (action === 'remove') {
        await client.messageFlagsRemove(range, flagArray, { uid: true });
      } else if (action === 'set') {
        await client.messageFlagsSet(range, flagArray, { uid: true });
      }

      return { 
        success: true, 
        uids: uidArray, 
        action: `${action} ${flags}`,
        count: uidArray.length
      };
    } finally {
      lock.release();  // 🔑 释放锁
    }
  } finally {
    await client.logout();
  }
}

async function markAsRead(uids, mailbox = DEFAULT_MAILBOX) {
  return updateFlags(uids, '\\Seen', 'add', mailbox);
}

async function markAsUnread(uids, mailbox = DEFAULT_MAILBOX) {
  return updateFlags(uids, '\\Seen', 'remove', mailbox);
}

// List all mailboxes
async function listMailboxes() {
  const client = await connect();

  try {
    const mailboxes = await client.list();
    return mailboxes.map(box => ({
      name: box.path,
      delimiter: box.delimiter,
      attributes: Array.from(box.flags),
      specialUse: box.specialUse || null,
    }));
  } finally {
    await client.logout();
  }
}

// Main CLI handler
async function main() {
  const { command, options, positional } = parseArgs();

  try {
    let result;

    switch (command) {
      case 'check':
        result = await checkEmails(
          options.mailbox || DEFAULT_MAILBOX,
          parseInt(options.limit) || 10,
          options.recent || null,
          options.unseen === 'true'
        );
        break;

      case 'fetch':
        if (!positional[0]) {
          throw new Error('UID required: node imap.js fetch <uid>');
        }
        result = await fetchEmail(positional[0], options.mailbox);
        break;

      case 'download':
        if (!positional[0]) {
          throw new Error('UID required: node imap.js download <uid>');
        }
        result = await downloadAttachments(
          positional[0],
          options.mailbox,
          options.dir || '.',
          options.file || null
        );
        break;

      case 'search':
        result = await searchEmails(options);
        break;

      case 'mark-read':
        if (positional.length === 0) {
          throw new Error('UID(s) required: node imap.js mark-read <uid> [uid2...]');
        }
        result = await markAsRead(positional, options.mailbox);
        break;

      case 'mark-unread':
        if (positional.length === 0) {
          throw new Error('UID(s) required: node imap.js mark-unread <uid> [uid2...]');
        }
        result = await markAsUnread(positional, options.mailbox);
        break;

      case 'list-mailboxes':
        result = await listMailboxes();
        break;

      default:
        console.error('Unknown command:', command);
        console.error('Available commands: check, fetch, download, search, mark-read, mark-unread, list-mailboxes');
        process.exit(1);
    }

    console.log(JSON.stringify(result, null, 2));
  } catch (err) {
    console.error('Error:', err.message);
    process.exit(1);
  }
}

main();