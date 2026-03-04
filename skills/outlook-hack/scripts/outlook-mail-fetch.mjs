#!/usr/bin/env node
/**
 * outlook-mail-fetch.mjs — Fetch Oscar's SERRA Outlook emails via MSAL refresh token
 * Zero external deps. Uses Graph API with refresh token rotation.
 * 
 * Usage:
 *   node outlook-mail-fetch.mjs --store-refresh-token <token>
 *   node outlook-mail-fetch.mjs --test
 *   node outlook-mail-fetch.mjs --fetch-all [--months 6]
 */
import { readFileSync, writeFileSync, mkdirSync, appendFileSync, existsSync } from 'fs';
import { join } from 'path';
import { homedir } from 'os';

const CREDS_DIR = join(homedir(), '.openclaw/credentials');
const OUTPUT_DIR = join(homedir(), '.openclaw/workspace/data/outlook-emails');
const TOKEN_FILE = join(CREDS_DIR, 'outlook-msal.json');

mkdirSync(CREDS_DIR, { recursive: true });
mkdirSync(OUTPUT_DIR, { recursive: true });

// Read config from credentials file (supports Teams FOCI hack or custom app)
const credsRaw = existsSync(TOKEN_FILE) ? JSON.parse(readFileSync(TOKEN_FILE, 'utf8')) : {};
const CLIENT_ID = credsRaw.client_id || '5e3ce6c0-2b1f-4285-8d4b-75ee78787346';
const TENANT_ID = credsRaw.tenant_id || 'f00f60b1-b967-4c0b-91ce-eb200dab0604';
const ORIGIN = credsRaw.origin || 'https://teams.cloud.microsoft';
const TOKEN_URL = `https://login.microsoftonline.com/${TENANT_ID}/oauth2/v2.0/token`;
const GRAPH = 'https://graph.microsoft.com/v1.0';
const SCOPE = credsRaw.scope || 'https://graph.microsoft.com/.default offline_access';

// --- Token Management ---

function saveTokens(accessToken, refreshToken) {
  writeFileSync(TOKEN_FILE, JSON.stringify({
    access_token: accessToken,
    refresh_token: refreshToken,
    client_id: CLIENT_ID,
    tenant_id: TENANT_ID,
    updated_at: new Date().toISOString()
  }, null, 2), { mode: 0o600 });
}

async function getAccessToken() {
  if (!existsSync(TOKEN_FILE)) throw new Error('No token file. Run --store-refresh-token first.');
  const creds = JSON.parse(readFileSync(TOKEN_FILE, 'utf8'));

  // If we have a valid access token, use it directly
  if (creds.access_token && creds.access_token !== 'pending' && creds.expires_at) {
    const expiresAt = new Date(creds.expires_at);
    if (expiresAt > new Date(Date.now() + 5 * 60 * 1000)) {
      return creds.access_token;
    }
  }

  // Try refresh if we have a refresh token
  const rt = creds.refresh_token;
  if (!rt) throw new Error('Access token expired and no refresh token available. Re-extract from browser.');

  const body = new URLSearchParams({
    client_id: CLIENT_ID,
    grant_type: 'refresh_token',
    refresh_token: rt,
    scope: SCOPE
  });

  const resp = await fetch(TOKEN_URL, { method: 'POST', body, headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'Origin': ORIGIN } });
  const data = await resp.json();

  if (data.error) throw new Error(`Token refresh failed: ${data.error_description || data.error}`);

  saveTokens(data.access_token, data.refresh_token || rt);
  return data.access_token;
}

// --- Graph API helpers ---

let currentToken = null;

async function graphGet(url, retried = false) {
  if (!currentToken) currentToken = await getAccessToken();
  const resp = await fetch(url, {
    headers: {
      'Authorization': `Bearer ${currentToken}`,
      'Prefer': 'outlook.body-content-type="text"'
    }
  });
  if (resp.status === 401 && !retried) {
    console.error('  Token expired, refreshing...');
    currentToken = await getAccessToken();
    return graphGet(url, true);
  }
  if (!resp.ok) throw new Error(`Graph API ${resp.status}: ${await resp.text()}`);
  return resp.json();
}

// --- Email Fetching ---

async function fetchAllEmails(months) {
  const since = new Date();
  since.setMonth(since.getMonth() - months);
  const sinceISO = since.toISOString();

  console.error(`Fetching emails since ${sinceISO} (${months} months)...`);

  const rawFile = join(OUTPUT_DIR, 'raw-emails.jsonl');
  writeFileSync(rawFile, ''); // truncate

  const select = 'id,subject,from,toRecipients,receivedDateTime,hasAttachments,bodyPreview,body,importance,isRead,categories,conversationId';
  let url = `${GRAPH}/me/messages?$filter=receivedDateTime ge ${sinceISO}&$orderby=receivedDateTime desc&$top=50&$select=${select}`;
  let page = 0, total = 0;

  while (url) {
    page++;
    process.stderr.write(`  Page ${page}...`);
    const data = await graphGet(url);
    const emails = data.value || [];
    if (emails.length === 0) break;

    for (const m of emails) {
      const line = JSON.stringify({
        id: m.id,
        subject: m.subject,
        from: m.from?.emailAddress?.address,
        fromName: m.from?.emailAddress?.name,
        to: (m.toRecipients || []).map(r => r.emailAddress?.address),
        date: m.receivedDateTime,
        hasAttachments: m.hasAttachments,
        importance: m.importance,
        isRead: m.isRead,
        categories: m.categories,
        conversationId: m.conversationId,
        preview: m.bodyPreview,
        bodyText: m.body?.content ? m.body.content.replace(/\r\n/g, '\n').replace(/\n{3,}/g, '\n\n').replace(/<[^>]*>/g, ' ').replace(/\s{2,}/g, ' ').slice(0, 3000) : null
      });
      appendFileSync(rawFile, line + '\n');
    }

    total += emails.length;
    console.error(` ${emails.length} emails (total: ${total})`);
    url = data['@odata.nextLink'] || null;
  }

  console.error(`Total emails fetched: ${total}`);
  return rawFile;
}

async function fetchAttachmentsIndex() {
  const rawFile = join(OUTPUT_DIR, 'raw-emails.jsonl');
  const attFile = join(OUTPUT_DIR, 'attachments-index.jsonl');
  writeFileSync(attFile, '');

  const lines = readFileSync(rawFile, 'utf8').split('\n').filter(Boolean);
  const withAtt = lines.map(l => JSON.parse(l)).filter(e => e.hasAttachments);

  console.error(`Indexing attachments for ${withAtt.length} emails...`);
  let count = 0;

  for (const email of withAtt) {
    try {
      const data = await graphGet(`${GRAPH}/me/messages/${email.id}/attachments?$select=id,name,contentType,size,isInline`);
      for (const att of (data.value || [])) {
        appendFileSync(attFile, JSON.stringify({
          messageId: email.id,
          subject: email.subject,
          date: email.date,
          name: att.name,
          contentType: att.contentType,
          size: att.size,
          isInline: att.isInline,
          attachmentId: att.id
        }) + '\n');
      }
    } catch (e) {
      console.error(`  Failed for ${email.subject}: ${e.message}`);
    }
    count++;
    if (count % 20 === 0) console.error(`  Indexed ${count}/${withAtt.length}...`);
  }

  console.error(`Attachment index complete: ${count} messages`);
  return attFile;
}

function generateSummary(months) {
  const rawFile = join(OUTPUT_DIR, 'raw-emails.jsonl');
  const attFile = join(OUTPUT_DIR, 'attachments-index.jsonl');
  const summaryFile = join(OUTPUT_DIR, 'email-summary.md');

  const emails = readFileSync(rawFile, 'utf8').split('\n').filter(Boolean).map(l => JSON.parse(l));
  const attachments = existsSync(attFile)
    ? readFileSync(attFile, 'utf8').split('\n').filter(Boolean).map(l => JSON.parse(l))
    : [];

  // Build attachment lookup
  const attByMsg = {};
  for (const a of attachments) {
    if (!attByMsg[a.messageId]) attByMsg[a.messageId] = [];
    attByMsg[a.messageId].push(a);
  }

  const total = emails.length;
  const unread = emails.filter(e => !e.isRead).length;
  const withAtt = emails.filter(e => e.hasAttachments).length;

  // Top senders
  const senderCounts = {};
  for (const e of emails) {
    const addr = e.from || 'unknown';
    senderCounts[addr] = (senderCounts[addr] || 0) + 1;
  }
  const topSenders = Object.entries(senderCounts).sort((a, b) => b[1] - a[1]).slice(0, 25);

  let md = `# Outlook Email Analysis — Last ${months} Months\n\n`;
  md += `_Generated: ${new Date().toISOString()}_\n`;
  md += `_Account: o.serra@serra.com.es_\n\n`;

  md += `## Stats\n`;
  md += `- **Total emails:** ${total}\n`;
  md += `- **Unread:** ${unread}\n`;
  md += `- **With attachments:** ${withAtt}\n`;
  md += `- **Unique senders:** ${Object.keys(senderCounts).length}\n\n`;

  md += `## Top 25 Senders\n\n`;
  md += `| Sender | Count |\n|--------|-------|\n`;
  for (const [addr, count] of topSenders) {
    md += `| ${addr} | ${count} |\n`;
  }
  md += `\n`;

  md += `## Email Digest (newest first)\n\n`;
  for (const e of emails) {
    const att = e.hasAttachments ? ' 📎' : '';
    const read = e.isRead ? '' : ' 🔴';
    const d = new Date(e.date).toISOString().slice(0, 16).replace('T', ' ');
    const attList = attByMsg[e.id];

    md += `### ${e.subject || '(no subject)'}${att}${read}\n`;
    md += `**From:** ${e.fromName || ''} <${e.from}> | **Date:** ${d}\n`;
    if (attList && attList.length > 0) {
      md += `**Attachments:** ${attList.map(a => `${a.name} (${(a.size / 1024).toFixed(0)}KB)`).join(', ')}\n`;
    }
    md += `> ${(e.preview || '').slice(0, 250).replace(/\n/g, ' ')}\n\n`;
  }

  writeFileSync(summaryFile, md);
  console.error(`Summary written: ${summaryFile} (${(md.length / 1024).toFixed(0)}KB)`);
  return summaryFile;
}

// --- Main ---

const args = process.argv.slice(2);
const cmd = args[0];

try {
  if (cmd === '--store-refresh-token') {
    saveTokens('pending', args[1]);
    console.error('Refresh token stored. Testing token exchange...');
    const at = await getAccessToken();
    console.log(`✅ Token exchange successful. Access token length: ${at.length}`);

  } else if (cmd === '--test') {
    const data = await graphGet(`${GRAPH}/me/messages?$top=5&$select=subject,from,receivedDateTime,hasAttachments&$orderby=receivedDateTime desc`);
    for (const m of data.value || []) {
      console.log(`${m.receivedDateTime?.slice(0, 16)} | ${m.from?.emailAddress?.address} | ${m.subject}${m.hasAttachments ? ' 📎' : ''}`);
    }

  } else if (cmd === '--fetch-all') {
    const monthsIdx = args.indexOf('--months');
    const months = monthsIdx >= 0 ? parseInt(args[monthsIdx + 1]) : 6;
    await fetchAllEmails(months);
    await fetchAttachmentsIndex();
    generateSummary(months);

  } else {
    console.log('Usage:');
    console.log('  node outlook-mail-fetch.mjs --store-refresh-token <token>');
    console.log('  node outlook-mail-fetch.mjs --test');
    console.log('  node outlook-mail-fetch.mjs --fetch-all [--months 6]');
  }
} catch (e) {
  console.error(`❌ ${e.message}`);
  process.exit(1);
}
