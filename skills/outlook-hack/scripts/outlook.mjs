#!/usr/bin/env node
/**
 * outlook.mjs — Full Microsoft Graph API CLI for Outlook
 * 
 * Zero external deps. Pure Node.js (v18+).
 * SEND-BLOCKED: Cannot send emails. Can only create drafts.
 * 
 * Subcommands:
 *   token extract          — Extract refresh token from Chrome relay (Teams tab)
 *   token test             — Verify token works
 *   token status           — Show token info
 *   mail list [--top N] [--folder inbox|sent|drafts|...] [--unread] [--from X] [--subject X]
 *   mail read <id>         — Read full email body
 *   mail search <query>    — Search emails (KQL)
 *   mail draft --to <addr> --subject <subj> --body <body> [--cc X] [--bcc X] [--importance high|low]
 *   mail reply-draft <id> [--body <text>] [--reply-all]
 *   mail forward-draft <id> --to <addr> [--body <text>]
 *   mail move <id> --folder <name>
 *   mail flag <id> [--remove]
 *   mail delete <id>
 *   mail attachments <id>  — List attachments
 *   mail attachment <id> <attachmentId> --save <path>  — Download attachment
 *   folders list
 *   calendar [--days N]
 *   contacts [--top N] [--search X]
 *   me                     — Show profile info
 */

import { readFileSync, writeFileSync, mkdirSync, existsSync, chmodSync } from 'fs';
import { join } from 'path';
import { homedir } from 'os';

// ═══════════════════════════════════════════════════════════════════
// SEND BLOCK — HARD-CODED, NON-NEGOTIABLE
// These Graph endpoints are NEVER called. Period.
// ═══════════════════════════════════════════════════════════════════
const BLOCKED_PATHS = ['/sendmail', '/send', '/reply', '/replyall', '/forward', '/createreply', '/createreplyall', '/createforward'];

const CREDS_DIR = join(homedir(), '.openclaw/credentials');
const TOKEN_FILE = join(CREDS_DIR, 'outlook-msal.json');
const GRAPH = 'https://graph.microsoft.com/v1.0';

mkdirSync(CREDS_DIR, { recursive: true });

// ─── Config ───
function loadCreds() {
  if (!existsSync(TOKEN_FILE)) return {};
  return JSON.parse(readFileSync(TOKEN_FILE, 'utf8'));
}

function saveCreds(creds) {
  writeFileSync(TOKEN_FILE, JSON.stringify(creds, null, 2), { mode: 0o600 });
  try { chmodSync(TOKEN_FILE, 0o600); } catch {}
}

function getConfig(creds) {
  return {
    clientId: creds.client_id || '5e3ce6c0-2b1f-4285-8d4b-75ee78787346',
    tenantId: creds.tenant_id || 'common',
    origin: creds.origin || 'https://teams.cloud.microsoft',
    scope: creds.scope || 'https://graph.microsoft.com/.default offline_access',
  };
}

// ─── Token Management ───
let _accessToken = null;

async function refreshAccessToken() {
  const creds = loadCreds();
  const cfg = getConfig(creds);

  // Check if current access token is still valid
  if (creds.access_token && creds.access_token !== 'pending' && creds.expires_at) {
    const expiresAt = new Date(creds.expires_at);
    if (expiresAt > new Date(Date.now() + 5 * 60 * 1000)) {
      _accessToken = creds.access_token;
      return _accessToken;
    }
  }

  const rt = creds.refresh_token;
  if (!rt) throw new Error('No refresh token. Run: outlook token extract');

  const tokenUrl = `https://login.microsoftonline.com/${cfg.tenantId}/oauth2/v2.0/token`;
  const body = new URLSearchParams({
    client_id: cfg.clientId,
    grant_type: 'refresh_token',
    refresh_token: rt,
    scope: cfg.scope,
  });

  const resp = await fetch(tokenUrl, {
    method: 'POST',
    body,
    headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'Origin': cfg.origin },
  });
  const data = await resp.json();
  if (data.error) throw new Error(`Token refresh failed: ${data.error_description || data.error}`);

  _accessToken = data.access_token;

  // Save rotated tokens
  const updated = { ...creds };
  updated.access_token = data.access_token;
  if (data.refresh_token) updated.refresh_token = data.refresh_token;
  updated.expires_at = new Date(Date.now() + (data.expires_in || 3600) * 1000).toISOString();
  updated.updated_at = new Date().toISOString();
  saveCreds(updated);

  return _accessToken;
}

async function getToken() {
  if (_accessToken) return _accessToken;
  return refreshAccessToken();
}

// ─── Graph API ───
async function graphRequest(method, path, body = null, retried = false) {
  // SEND BLOCK CHECK
  const pathLower = path.toLowerCase();
  for (const blocked of BLOCKED_PATHS) {
    if (pathLower.includes(blocked)) {
      throw new Error(`🚫 BLOCKED: "${blocked}" operations are disabled. This skill cannot send emails.`);
    }
  }

  const token = await getToken();
  const url = path.startsWith('http') ? path : `${GRAPH}${path}`;
  const headers = {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
    'Prefer': 'outlook.body-content-type="text"',
  };

  const opts = { method, headers };
  if (body) opts.body = JSON.stringify(body);

  const resp = await fetch(url, opts);

  if (resp.status === 401 && !retried) {
    _accessToken = null;
    await refreshAccessToken();
    return graphRequest(method, path, body, true);
  }
  if (resp.status === 204) return null; // No content (delete, etc.)
  if (!resp.ok) {
    const errText = await resp.text();
    throw new Error(`Graph API ${resp.status}: ${errText}`);
  }
  return resp.json();
}

const graphGet = (path) => graphRequest('GET', path);
const graphPost = (path, body) => graphRequest('POST', path, body);
const graphPatch = (path, body) => graphRequest('PATCH', path, body);
const graphDelete = (path) => graphRequest('DELETE', path);

// ─── Helpers ───
function parseArgs(argv) {
  const result = { _: [], flags: {} };
  let i = 0;
  while (i < argv.length) {
    if (argv[i].startsWith('--')) {
      const key = argv[i].slice(2);
      if (i + 1 < argv.length && !argv[i + 1].startsWith('--')) {
        result.flags[key] = argv[++i];
      } else {
        result.flags[key] = true;
      }
    } else {
      result._.push(argv[i]);
    }
    i++;
  }
  return result;
}

function out(data) {
  if (typeof data === 'string') console.log(data);
  else console.log(JSON.stringify(data, null, 2));
}

function emailSummary(m) {
  const date = m.receivedDateTime?.slice(0, 16).replace('T', ' ') || '';
  const from = m.from?.emailAddress?.address || '';
  const fromName = m.from?.emailAddress?.name || '';
  const att = m.hasAttachments ? ' 📎' : '';
  const unread = m.isRead === false ? ' 🔴' : '';
  const flag = m.flag?.flagStatus === 'flagged' ? ' 🚩' : '';
  const imp = m.importance === 'high' ? ' ❗' : '';
  return { id: m.id, date, from, fromName, subject: m.subject || '(no subject)', att, unread, flag, imp, preview: m.bodyPreview?.slice(0, 200) };
}

// ─── Well-known folder mapping ───
const FOLDER_MAP = {
  inbox: 'inbox',
  sent: 'sentitems',
  sentitems: 'sentitems',
  drafts: 'drafts',
  deleted: 'deleteditems',
  deleteditems: 'deleteditems',
  junk: 'junkemail',
  junkemail: 'junkemail',
  archive: 'archive',
  outbox: 'outbox',
};

function folderPath(name) {
  if (!name) return '';
  const mapped = FOLDER_MAP[name.toLowerCase()] || name;
  // If it looks like an ID (long alphanumeric), use directly
  if (mapped.length > 30) return `/me/mailFolders/${mapped}/messages`;
  return `/me/mailFolders/${mapped}/messages`;
}

// ═══════════════════════════════════════════════════════════════════
// COMMANDS
// ═══════════════════════════════════════════════════════════════════

async function cmdTokenExtract(args) {
  // Reads from stdin: expects JSON with refresh_token (and optionally tenant_id)
  // Or from --refresh-token flag
  const rt = args.flags['refresh-token'];
  if (!rt) {
    console.error('Usage: outlook token extract --refresh-token <token> [--tenant-id <id>]');
    console.error('');
    console.error('To get the token from Teams localStorage:');
    console.error('  1. Open Teams in Chrome with OpenClaw browser relay');
    console.error('  2. Run: outlook token extract-browser');
    process.exit(1);
  }

  const tenantId = args.flags['tenant-id'] || 'common';
  const creds = {
    client_id: '5e3ce6c0-2b1f-4285-8d4b-75ee78787346',
    tenant_id: tenantId,
    refresh_token: rt,
    origin: 'https://teams.cloud.microsoft',
    scope: 'https://graph.microsoft.com/.default offline_access',
    api: 'graph',
    updated_at: new Date().toISOString(),
  };
  saveCreds(creds);
  console.error('✅ Token saved. Testing...');

  try {
    await refreshAccessToken();
    const me = await graphGet('/me?$select=displayName,mail');
    out({ status: 'ok', user: me.displayName, email: me.mail });
  } catch (e) {
    console.error(`❌ Token test failed: ${e.message}`);
    process.exit(1);
  }
}

async function cmdTokenTest() {
  const me = await graphGet('/me?$select=displayName,mail,userPrincipalName');
  out({ status: 'ok', user: me.displayName, email: me.mail || me.userPrincipalName });
}

async function cmdTokenStatus() {
  const creds = loadCreds();
  out({
    hasRefreshToken: !!creds.refresh_token,
    hasAccessToken: !!(creds.access_token && creds.access_token !== 'pending'),
    expiresAt: creds.expires_at || null,
    updatedAt: creds.updated_at || null,
    tenantId: creds.tenant_id || 'not set',
    clientId: creds.client_id || 'default (Teams)',
  });
}

async function cmdMailList(args) {
  const top = parseInt(args.flags.top) || 25;
  const folder = args.flags.folder;
  const unreadOnly = args.flags.unread;
  const fromFilter = args.flags.from;
  const subjectFilter = args.flags.subject;

  const basePath = folder ? folderPath(folder) : '/me/messages';
  const select = 'id,subject,from,receivedDateTime,hasAttachments,bodyPreview,isRead,importance,flag';

  const filters = [];
  if (unreadOnly) filters.push('isRead eq false');
  if (fromFilter) filters.push(`from/emailAddress/address eq '${fromFilter}'`);

  let url = `${basePath}?$top=${top}&$select=${select}&$orderby=receivedDateTime desc`;
  if (filters.length > 0) url += `&$filter=${filters.join(' and ')}`;

  const data = await graphGet(url);
  const emails = (data.value || []).map(emailSummary);

  // Apply subject filter client-side (Graph $filter doesn't support subject contains well)
  const filtered = subjectFilter
    ? emails.filter(e => e.subject.toLowerCase().includes(subjectFilter.toLowerCase()))
    : emails;

  out(filtered);
}

async function cmdMailRead(args) {
  const id = args._[0];
  if (!id) { console.error('Usage: outlook mail read <messageId>'); process.exit(1); }

  const select = 'id,subject,from,toRecipients,ccRecipients,bccRecipients,receivedDateTime,sentDateTime,hasAttachments,body,bodyPreview,importance,isRead,flag,categories,conversationId,internetMessageHeaders';
  const m = await graphGet(`/me/messages/${id}?$select=${select}`);

  out({
    id: m.id,
    subject: m.subject,
    from: m.from?.emailAddress,
    to: (m.toRecipients || []).map(r => r.emailAddress),
    cc: (m.ccRecipients || []).map(r => r.emailAddress),
    bcc: (m.bccRecipients || []).map(r => r.emailAddress),
    date: m.receivedDateTime,
    sent: m.sentDateTime,
    importance: m.importance,
    isRead: m.isRead,
    flag: m.flag?.flagStatus,
    categories: m.categories,
    conversationId: m.conversationId,
    hasAttachments: m.hasAttachments,
    body: m.body?.content,
  });
}

async function cmdMailSearch(args) {
  const query = args._[0];
  if (!query) { console.error('Usage: outlook mail search "<query>"'); process.exit(1); }
  const top = parseInt(args.flags.top) || 25;

  // Graph $search uses KQL (Keyword Query Language)
  const data = await graphGet(`/me/messages?$search="${encodeURIComponent(query)}"&$top=${top}&$select=id,subject,from,receivedDateTime,hasAttachments,bodyPreview,isRead,importance,flag`);
  const emails = (data.value || []).map(emailSummary);
  out(emails);
}

async function cmdMailDraft(args) {
  const to = args.flags.to;
  const subject = args.flags.subject || '';
  const body = args.flags.body || '';
  const cc = args.flags.cc;
  const bcc = args.flags.bcc;
  const importance = args.flags.importance || 'normal';

  if (!to) { console.error('Usage: outlook mail draft --to <addr> --subject <subj> --body <text> [--cc X] [--bcc X]'); process.exit(1); }

  const toRecipients = to.split(',').map(addr => ({ emailAddress: { address: addr.trim() } }));
  const msg = {
    subject,
    body: { contentType: 'text', content: body },
    toRecipients,
    importance,
  };
  if (cc) msg.ccRecipients = cc.split(',').map(addr => ({ emailAddress: { address: addr.trim() } }));
  if (bcc) msg.bccRecipients = bcc.split(',').map(addr => ({ emailAddress: { address: addr.trim() } }));

  const draft = await graphPost('/me/messages', msg);
  out({ status: 'draft_created', id: draft.id, subject: draft.subject, webLink: draft.webLink });
}

async function cmdMailReplyDraft(args) {
  const id = args._[0];
  if (!id) { console.error('Usage: outlook mail reply-draft <messageId> [--body <text>] [--reply-all]'); process.exit(1); }
  const body = args.flags.body || '';
  const replyAll = args.flags['reply-all'];

  // Create reply draft (NOT send)
  // Graph: POST /me/messages/{id}/createReply creates a draft reply
  // BUT createReply is in our BLOCKED_PATHS... we need a different approach.
  // We'll build the reply manually as a new draft.

  // First, read the original message
  const orig = await graphGet(`/me/messages/${id}?$select=subject,from,toRecipients,ccRecipients,conversationId,body`);

  const toRecipients = [{ emailAddress: orig.from.emailAddress }];
  const msg = {
    subject: orig.subject?.startsWith('Re:') ? orig.subject : `Re: ${orig.subject}`,
    body: {
      contentType: 'text',
      content: body + `\n\n--- Original message ---\nFrom: ${orig.from?.emailAddress?.name} <${orig.from?.emailAddress?.address}>\n\n${orig.body?.content?.slice(0, 2000) || ''}`,
    },
    toRecipients,
    conversationId: orig.conversationId,
  };

  if (replyAll && orig.toRecipients) {
    msg.toRecipients = [...msg.toRecipients, ...orig.toRecipients.filter(r => r.emailAddress.address !== orig.from?.emailAddress?.address)];
    if (orig.ccRecipients) msg.ccRecipients = orig.ccRecipients;
  }

  const draft = await graphPost('/me/messages', msg);
  out({ status: 'reply_draft_created', id: draft.id, subject: draft.subject, to: msg.toRecipients.map(r => r.emailAddress.address) });
}

async function cmdMailForwardDraft(args) {
  const id = args._[0];
  const to = args.flags.to;
  if (!id || !to) { console.error('Usage: outlook mail forward-draft <messageId> --to <addr> [--body <text>]'); process.exit(1); }
  const body = args.flags.body || '';

  const orig = await graphGet(`/me/messages/${id}?$select=subject,from,body`);

  const msg = {
    subject: orig.subject?.startsWith('Fw:') ? orig.subject : `Fw: ${orig.subject}`,
    body: {
      contentType: 'text',
      content: body + `\n\n--- Forwarded message ---\nFrom: ${orig.from?.emailAddress?.name} <${orig.from?.emailAddress?.address}>\nSubject: ${orig.subject}\n\n${orig.body?.content?.slice(0, 3000) || ''}`,
    },
    toRecipients: to.split(',').map(addr => ({ emailAddress: { address: addr.trim() } })),
  };

  const draft = await graphPost('/me/messages', msg);
  out({ status: 'forward_draft_created', id: draft.id, subject: draft.subject });
}

async function cmdMailMove(args) {
  const id = args._[0];
  const folder = args.flags.folder;
  if (!id || !folder) { console.error('Usage: outlook mail move <messageId> --folder <name>'); process.exit(1); }

  const mapped = FOLDER_MAP[folder.toLowerCase()] || folder;
  const result = await graphPost(`/me/messages/${id}/move`, { destinationId: mapped });
  out({ status: 'moved', id: result.id, folder: mapped });
}

async function cmdMailFlag(args) {
  const id = args._[0];
  if (!id) { console.error('Usage: outlook mail flag <messageId> [--remove]'); process.exit(1); }
  const remove = args.flags.remove;

  await graphPatch(`/me/messages/${id}`, {
    flag: { flagStatus: remove ? 'notFlagged' : 'flagged' },
  });
  out({ status: remove ? 'unflagged' : 'flagged', id });
}

async function cmdMailDelete(args) {
  const id = args._[0];
  if (!id) { console.error('Usage: outlook mail delete <messageId>'); process.exit(1); }
  await graphDelete(`/me/messages/${id}`);
  out({ status: 'deleted', id });
}

async function cmdMailAttachments(args) {
  const id = args._[0];
  if (!id) { console.error('Usage: outlook mail attachments <messageId>'); process.exit(1); }

  const data = await graphGet(`/me/messages/${id}/attachments?$select=id,name,contentType,size,isInline`);
  out((data.value || []).map(a => ({
    id: a.id,
    name: a.name,
    contentType: a.contentType,
    size: a.size,
    sizeKB: Math.round(a.size / 1024),
    isInline: a.isInline,
  })));
}

async function cmdMailAttachmentDownload(args) {
  const msgId = args._[0];
  const attId = args._[1];
  const savePath = args.flags.save;
  if (!msgId || !attId || !savePath) {
    console.error('Usage: outlook mail attachment <messageId> <attachmentId> --save <path>');
    process.exit(1);
  }

  const att = await graphGet(`/me/messages/${msgId}/attachments/${attId}`);
  if (att.contentBytes) {
    const buf = Buffer.from(att.contentBytes, 'base64');
    writeFileSync(savePath, buf);
    out({ status: 'saved', path: savePath, size: buf.length, name: att.name });
  } else {
    throw new Error('Attachment has no content (might be a reference attachment)');
  }
}

async function cmdFoldersList() {
  const data = await graphGet('/me/mailFolders?$top=50&$select=id,displayName,totalItemCount,unreadItemCount,parentFolderId');
  const folders = (data.value || []).map(f => ({
    id: f.id,
    name: f.displayName,
    total: f.totalItemCount,
    unread: f.unreadItemCount,
  }));
  out(folders);

  // Also get child folders for each
  for (const f of folders) {
    try {
      const children = await graphGet(`/me/mailFolders/${f.id}/childFolders?$select=id,displayName,totalItemCount,unreadItemCount`);
      if (children.value?.length > 0) {
        f.children = children.value.map(c => ({
          id: c.id,
          name: c.displayName,
          total: c.totalItemCount,
          unread: c.unreadItemCount,
        }));
      }
    } catch {}
  }
  // Re-output with children
  out(folders);
}

async function cmdCalendar(args) {
  const days = parseInt(args.flags.days) || 7;
  const start = new Date().toISOString();
  const end = new Date(Date.now() + days * 86400000).toISOString();

  const data = await graphGet(`/me/calendarView?startDateTime=${start}&endDateTime=${end}&$top=50&$select=subject,start,end,location,organizer,isAllDay,isCancelled,showAs,importance&$orderby=start/dateTime`);
  const events = (data.value || []).map(e => ({
    id: e.id,
    subject: e.subject,
    start: e.start?.dateTime,
    end: e.end?.dateTime,
    timezone: e.start?.timeZone,
    location: e.location?.displayName,
    organizer: e.organizer?.emailAddress?.address,
    isAllDay: e.isAllDay,
    isCancelled: e.isCancelled,
    showAs: e.showAs,
  }));
  out(events);
}

async function cmdContacts(args) {
  const top = parseInt(args.flags.top) || 50;
  const search = args.flags.search;

  let url = `/me/contacts?$top=${top}&$select=id,displayName,emailAddresses,mobilePhone,businessPhones,companyName,jobTitle`;
  if (search) url += `&$search="${encodeURIComponent(search)}"`;
  url += '&$orderby=displayName';

  const data = await graphGet(url);
  const contacts = (data.value || []).map(c => ({
    id: c.id,
    name: c.displayName,
    emails: (c.emailAddresses || []).map(e => e.address),
    mobile: c.mobilePhone,
    phone: c.businessPhones?.[0],
    company: c.companyName,
    title: c.jobTitle,
  }));
  out(contacts);
}

async function cmdMe() {
  const me = await graphGet('/me?$select=displayName,mail,userPrincipalName,jobTitle,department,officeLocation,mobilePhone,businessPhones');
  out(me);
}

// ─── Bulk Fetch (from original script) ───
async function cmdMailFetchAll(args) {
  const months = parseInt(args.flags.months) || 6;
  const OUTPUT_DIR = join(homedir(), '.openclaw/workspace/data/outlook-emails');
  mkdirSync(OUTPUT_DIR, { recursive: true });

  const since = new Date();
  since.setMonth(since.getMonth() - months);
  const sinceISO = since.toISOString();

  console.error(`Fetching emails since ${sinceISO} (${months} months)...`);

  const { appendFileSync: appendFile } = await import('fs');
  const rawFile = join(OUTPUT_DIR, 'raw-emails.jsonl');
  writeFileSync(rawFile, '');

  const select = 'id,subject,from,toRecipients,receivedDateTime,hasAttachments,bodyPreview,body,importance,isRead,categories,conversationId';
  let url = `/me/messages?$filter=receivedDateTime ge ${sinceISO}&$orderby=receivedDateTime desc&$top=50&$select=${select}`;
  let page = 0, total = 0;

  while (url) {
    page++;
    process.stderr.write(`  Page ${page}...`);
    const data = await graphGet(url);
    const emails = data.value || [];
    if (emails.length === 0) break;

    for (const m of emails) {
      const line = JSON.stringify({
        id: m.id, subject: m.subject,
        from: m.from?.emailAddress?.address, fromName: m.from?.emailAddress?.name,
        to: (m.toRecipients || []).map(r => r.emailAddress?.address),
        date: m.receivedDateTime, hasAttachments: m.hasAttachments,
        importance: m.importance, isRead: m.isRead,
        categories: m.categories, conversationId: m.conversationId,
        preview: m.bodyPreview,
        bodyText: m.body?.content ? m.body.content.replace(/\r\n/g, '\n').replace(/\n{3,}/g, '\n\n').replace(/<[^>]*>/g, ' ').replace(/\s{2,}/g, ' ').slice(0, 3000) : null
      });
      appendFile(rawFile, line + '\n');
    }

    total += emails.length;
    console.error(` ${emails.length} emails (total: ${total})`);

    const nextLink = data['@odata.nextLink'];
    url = nextLink ? (nextLink.startsWith('http') ? nextLink : null) : null;
  }

  console.error(`\nTotal emails fetched: ${total}`);
  console.error(`Output: ${rawFile}`);
  out({ status: 'done', total, file: rawFile });
}

// ═══════════════════════════════════════════════════════════════════
// ROUTER
// ═══════════════════════════════════════════════════════════════════

const args = parseArgs(process.argv.slice(2));
const [cmd, sub, ...rest] = args._;
// Rebuild args for sub-commands
const subArgs = { _: rest, flags: args.flags };

try {
  switch (cmd) {
    case 'token':
      if (sub === 'extract') await cmdTokenExtract(subArgs);
      else if (sub === 'test') await cmdTokenTest();
      else if (sub === 'status') await cmdTokenStatus();
      else { console.error('Usage: outlook token [extract|test|status]'); process.exit(1); }
      break;

    case 'mail':
      if (sub === 'list') await cmdMailList(subArgs);
      else if (sub === 'read') await cmdMailRead(subArgs);
      else if (sub === 'search') await cmdMailSearch(subArgs);
      else if (sub === 'draft') await cmdMailDraft(subArgs);
      else if (sub === 'reply-draft') await cmdMailReplyDraft(subArgs);
      else if (sub === 'forward-draft') await cmdMailForwardDraft(subArgs);
      else if (sub === 'move') await cmdMailMove(subArgs);
      else if (sub === 'flag') await cmdMailFlag(subArgs);
      else if (sub === 'delete') await cmdMailDelete(subArgs);
      else if (sub === 'attachments') await cmdMailAttachments(subArgs);
      else if (sub === 'attachment') await cmdMailAttachmentDownload(subArgs);
      else if (sub === 'fetch-all') await cmdMailFetchAll(subArgs);
      else { console.error('Usage: outlook mail [list|read|search|draft|reply-draft|forward-draft|move|flag|delete|attachments|attachment|fetch-all]'); process.exit(1); }
      break;

    case 'folders':
      await cmdFoldersList();
      break;

    case 'calendar':
      await cmdCalendar(subArgs);
      break;

    case 'contacts':
      await cmdContacts(subArgs);
      break;

    case 'me':
      await cmdMe();
      break;

    default:
      console.log(`outlook — Microsoft Graph API CLI for Outlook

Commands:
  token extract --refresh-token <token> [--tenant-id <id>]
  token test
  token status
  mail list [--top N] [--folder inbox|sent|drafts] [--unread] [--from X] [--subject X]
  mail read <messageId>
  mail search "<query>"
  mail draft --to <addr> --subject <subj> --body <text> [--cc X] [--bcc X]
  mail reply-draft <messageId> [--body <text>] [--reply-all]
  mail forward-draft <messageId> --to <addr> [--body <text>]
  mail move <messageId> --folder <name>
  mail flag <messageId> [--remove]
  mail delete <messageId>
  mail attachments <messageId>
  mail attachment <messageId> <attachmentId> --save <path>
  mail fetch-all [--months 6]
  folders list
  calendar [--days 7]
  contacts [--top 50] [--search X]
  me

🚫 SEND-BLOCKED: This tool cannot send emails. Only drafts.`);
      break;
  }
} catch (e) {
  console.error(`❌ ${e.message}`);
  process.exit(1);
}
