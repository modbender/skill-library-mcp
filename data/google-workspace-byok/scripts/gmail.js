/**
 * Gmail script — read emails via Gmail API.
 * 
 * Usage:
 *   node gmail.js --account <label> --action <action> [options]
 * 
 * Actions:
 *   list                        List recent emails
 *   read                        Read a specific email
 *   labels                      List all labels
 *   attachment                  Download an attachment
 * 
 * Options:
 *   --query <text>              Gmail search query (e.g., "is:unread", "from:someone@example.com")
 *   --max <number>              Max results (default: 10)
 *   --message-id <id>           Message ID (for read/attachment)
 *   --attachment-id <id>        Attachment ID (for attachment action)
 *   --filename <name>           Filename to save attachment as
 *   --out-dir <path>            Output directory for attachment (default: /tmp)
 *   --label <id>                Label ID filter (default: INBOX)
 */

const fs = require('fs');
const path = require('path');
const { google } = require('googleapis');
const { getAuthClient, parseArgs } = require('./shared');

const args = parseArgs(process.argv);

if (!args.account) {
  console.error('Usage: node gmail.js --account <label> --action <action>');
  process.exit(1);
}

const action = args.action || 'list';
const maxResults = parseInt(args.max || '10', 10);

/**
 * Decode base64url encoded string
 */
function decodeBase64Url(str) {
  if (!str) return '';
  const base64 = str.replace(/-/g, '+').replace(/_/g, '/');
  return Buffer.from(base64, 'base64').toString('utf8');
}

/**
 * Extract the plain text body from a message payload.
 */
function extractBody(payload) {
  // Simple message with body data
  if (payload.body && payload.body.data) {
    return decodeBase64Url(payload.body.data);
  }

  // Multipart message — look for text/plain first, then text/html
  if (payload.parts) {
    // Try text/plain first
    for (const part of payload.parts) {
      if (part.mimeType === 'text/plain' && part.body && part.body.data) {
        return decodeBase64Url(part.body.data);
      }
    }
    // Recurse into nested multipart
    for (const part of payload.parts) {
      if (part.parts) {
        const nested = extractBody(part);
        if (nested) return nested;
      }
    }
    // Fall back to text/html
    for (const part of payload.parts) {
      if (part.mimeType === 'text/html' && part.body && part.body.data) {
        const html = decodeBase64Url(part.body.data);
        // Strip HTML tags for readability
        return html.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
      }
    }
  }

  return '(no readable body)';
}

/**
 * Get header value by name
 */
function getHeader(headers, name) {
  const h = headers.find(h => h.name.toLowerCase() === name.toLowerCase());
  return h ? h.value : null;
}

async function run() {
  const auth = getAuthClient(args.account);
  const gmail = google.gmail({ version: 'v1', auth });

  switch (action) {
    case 'list': {
      const params = {
        userId: 'me',
        maxResults,
      };

      if (args.query) {
        params.q = args.query;
      }

      if (args.label) {
        params.labelIds = [args.label];
      }

      const res = await gmail.users.messages.list(params);
      const messageList = res.data.messages || [];

      if (messageList.length === 0) {
        console.log(JSON.stringify({
          account: args.account,
          query: args.query || null,
          count: 0,
          messages: [],
        }, null, 2));
        break;
      }

      // Fetch metadata for each message
      const messages = await Promise.all(
        messageList.map(async (m) => {
          const msg = await gmail.users.messages.get({
            userId: 'me',
            id: m.id,
            format: 'metadata',
            metadataHeaders: ['From', 'To', 'Subject', 'Date'],
          });
          const headers = msg.data.payload.headers;
          return {
            id: msg.data.id,
            threadId: msg.data.threadId,
            snippet: msg.data.snippet,
            from: getHeader(headers, 'From'),
            to: getHeader(headers, 'To'),
            subject: getHeader(headers, 'Subject'),
            date: getHeader(headers, 'Date'),
            labelIds: msg.data.labelIds,
            isUnread: (msg.data.labelIds || []).includes('UNREAD'),
          };
        })
      );

      console.log(JSON.stringify({
        account: args.account,
        query: args.query || null,
        count: messages.length,
        messages,
      }, null, 2));
      break;
    }

    case 'read': {
      if (!args['message-id']) {
        console.error('--message-id is required for read');
        process.exit(1);
      }

      const res = await gmail.users.messages.get({
        userId: 'me',
        id: args['message-id'],
        format: 'full',
      });

      const msg = res.data;
      const headers = msg.payload.headers;
      const body = extractBody(msg.payload);

      // Truncate very long bodies
      const maxBodyLength = 5000;
      const truncated = body.length > maxBodyLength;

      console.log(JSON.stringify({
        id: msg.id,
        threadId: msg.threadId,
        from: getHeader(headers, 'From'),
        to: getHeader(headers, 'To'),
        cc: getHeader(headers, 'Cc'),
        subject: getHeader(headers, 'Subject'),
        date: getHeader(headers, 'Date'),
        labelIds: msg.labelIds,
        isUnread: (msg.labelIds || []).includes('UNREAD'),
        body: truncated ? body.substring(0, maxBodyLength) : body,
        bodyTruncated: truncated,
        attachments: (msg.payload.parts || [])
          .filter(p => p.filename && p.filename.length > 0)
          .map(p => ({
            filename: p.filename,
            mimeType: p.mimeType,
            size: p.body ? p.body.size : null,
            attachmentId: p.body ? p.body.attachmentId : null,
          })),
      }, null, 2));
      break;
    }

    case 'attachment': {
      if (!args['message-id']) {
        console.error('--message-id is required for attachment');
        process.exit(1);
      }

      const outDir = args['out-dir'] || '/tmp';

      // If no attachment-id given, download all attachments from the message
      const msgRes = await gmail.users.messages.get({
        userId: 'me',
        id: args['message-id'],
        format: 'full',
      });

      const allParts = [];
      function collectParts(parts) {
        for (const p of (parts || [])) {
          if (p.filename && p.filename.length > 0 && p.body && p.body.attachmentId) {
            allParts.push(p);
          }
          if (p.parts) collectParts(p.parts);
        }
      }
      collectParts(msgRes.data.payload.parts);

      let targetParts = allParts;
      if (args['attachment-id']) {
        targetParts = allParts.filter(p => p.body.attachmentId === args['attachment-id']);
        if (targetParts.length === 0) {
          console.error('Attachment ID not found. Available attachments:');
          allParts.forEach(p => console.error(`  ${p.filename}: ${p.body.attachmentId}`));
          process.exit(1);
        }
      }

      const downloaded = [];
      for (const part of targetParts) {
        const attRes = await gmail.users.messages.attachments.get({
          userId: 'me',
          messageId: args['message-id'],
          id: part.body.attachmentId,
        });

        const data = attRes.data.data;
        const buf = Buffer.from(data.replace(/-/g, '+').replace(/_/g, '/'), 'base64');
        const fname = args.filename || part.filename;
        const outPath = path.join(outDir, fname);
        fs.writeFileSync(outPath, buf);
        downloaded.push({ filename: fname, path: outPath, size: buf.length, mimeType: part.mimeType });
      }

      console.log(JSON.stringify({
        account: args.account,
        messageId: args['message-id'],
        downloaded,
      }, null, 2));
      break;
    }

    case 'labels': {
      const res = await gmail.users.labels.list({ userId: 'me' });
      const labels = (res.data.labels || []).map(l => ({
        id: l.id,
        name: l.name,
        type: l.type,
      }));
      console.log(JSON.stringify({
        account: args.account,
        count: labels.length,
        labels,
      }, null, 2));
      break;
    }

    default:
      console.error(`Unknown action: ${action}`);
      console.error('Available: list, read, labels');
      process.exit(1);
  }
}

run().catch((err) => {
  console.error(`Gmail error: ${err.message}`);
  if (err.message.includes('invalid_grant') || err.message.includes('Token has been expired')) {
    console.error(`\nToken may be expired. Re-authorize:\n  node auth.js --account ${args.account}`);
  }
  process.exit(1);
});
