#!/usr/bin/env node
// Comms Hub Bridge Client — universal agent-to-agent messaging
// Works with any Comms Hub instance. Configure via environment or config.json.

const https = require('https');
const http = require('http');
const fs = require('fs');
const path = require('path');

// --- Configuration ---
// Priority: env vars > config.json > defaults
const CONFIG_PATH = path.join(__dirname, '..', 'config.json');
let fileConfig = {};
try { fileConfig = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8')); } catch {}

const HUB_IP       = process.env.BRIDGE_HUB_IP       || fileConfig.hubIp       || '';
const HUB_HOST     = process.env.BRIDGE_HUB_HOST     || fileConfig.hubHost     || '';
const HUB_PORT     = process.env.BRIDGE_HUB_PORT     || fileConfig.hubPort     || 443;
const HUB_PROTO    = process.env.BRIDGE_HUB_PROTO    || fileConfig.hubProto    || 'https';
const MY_NAME      = process.env.BRIDGE_AGENT_NAME   || fileConfig.agentName   || 'unknown';

if (!HUB_IP && !HUB_HOST) {
  console.error('ERROR: Set hubIp or hubHost in config.json (or BRIDGE_HUB_IP / BRIDGE_HUB_HOST env vars)');
  process.exit(1);
}

function request(method, apiPath, body) {
  return new Promise((resolve, reject) => {
    const data = body ? JSON.stringify(body) : null;
    const mod = HUB_PROTO === 'https' ? https : http;
    const opts = {
      hostname: HUB_IP || HUB_HOST,
      port: HUB_PORT,
      path: apiPath,
      method,
      headers: {
        ...(HUB_HOST && HUB_IP ? { 'Host': HUB_HOST } : {}),
        'Content-Type': 'application/json',
        ...(data ? { 'Content-Length': Buffer.byteLength(data) } : {})
      },
      rejectUnauthorized: true
    };
    const req = mod.request(opts, res => {
      let chunks = '';
      res.on('data', c => chunks += c);
      res.on('end', () => {
        try { resolve(JSON.parse(chunks)); }
        catch { resolve(chunks); }
      });
    });
    req.on('error', reject);
    if (data) req.write(data);
    req.end();
  });
}

// --- API Methods ---
const api = {
  health:      ()                                 => request('GET',    '/api/health'),
  send:        (to, subject, body, priority)      => request('POST',   '/api/bridge/message', { from: MY_NAME, to, subject, body, priority: priority || 'normal' }),
  inbox:       ()                                 => request('GET',    `/api/bridge/inbox/${MY_NAME}`),
  allMessages: ()                                 => request('GET',    '/api/bridge/all-messages'),
  ack:         (messageId)                        => request('DELETE', `/api/bridge/inbox/${MY_NAME}/${messageId}`),
  files:       ()                                 => request('GET',    '/api/bridge/files'),
  state:       ()                                 => request('GET',    '/api/bridge/state'),
};

// --- File Upload ---
function uploadFile(filePath) {
  return new Promise((resolve, reject) => {
    const fileName = path.basename(filePath);
    const fileContent = fs.readFileSync(filePath);
    const boundary = '----FormBoundary' + Date.now();
    const parts = [
      `--${boundary}\r\nContent-Disposition: form-data; name="from"\r\n\r\n${MY_NAME}`,
      `--${boundary}\r\nContent-Disposition: form-data; name="file"; filename="${fileName}"\r\nContent-Type: application/octet-stream\r\n\r\n`
    ];
    const tail = `\r\n--${boundary}--\r\n`;
    const head = Buffer.from(parts.join('\r\n') + '\r\n');
    const end = Buffer.from(tail);
    const body = Buffer.concat([head, fileContent, end]);
    const mod = HUB_PROTO === 'https' ? https : http;
    const opts = {
      hostname: HUB_IP || HUB_HOST,
      port: HUB_PORT,
      path: '/api/bridge/files',
      method: 'POST',
      headers: {
        ...(HUB_HOST && HUB_IP ? { 'Host': HUB_HOST } : {}),
        'Content-Type': `multipart/form-data; boundary=${boundary}`,
        'Content-Length': body.length
      },
      rejectUnauthorized: true
    };
    const req = mod.request(opts, res => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => {
        try { resolve(JSON.parse(data)); }
        catch { resolve({ status: res.statusCode, response: data }); }
      });
    });
    req.on('error', reject);
    req.write(body);
    req.end();
  });
}

// --- CLI ---
if (require.main === module) {
  const cmd = process.argv[2];
  const args = process.argv.slice(3);
  (async () => {
    try {
      switch (cmd) {
        case 'health':
          console.log(JSON.stringify(await api.health(), null, 2)); break;
        case 'send':
          if (args.length < 3) { console.log('Usage: send <to> "<subject>" "<body>" [priority]'); process.exit(1); }
          console.log(JSON.stringify(await api.send(args[0], args[1], args[2], args[3]), null, 2)); break;
        case 'inbox':
          const msgs = await api.inbox();
          console.log(Array.isArray(msgs) && msgs.length === 0 ? 'Inbox empty.' : JSON.stringify(msgs, null, 2)); break;
        case 'all':
          console.log(JSON.stringify(await api.allMessages(), null, 2)); break;
        case 'ack':
          if (!args[0]) { console.log('Usage: ack <messageId>'); process.exit(1); }
          console.log(JSON.stringify(await api.ack(args[0]), null, 2)); break;
        case 'files':
          console.log(JSON.stringify(await api.files(), null, 2)); break;
        case 'upload':
          if (!args[0]) { console.log('Usage: upload <file-path>'); process.exit(1); }
          console.log(JSON.stringify(await uploadFile(args[0]), null, 2)); break;
        case 'state':
          console.log(JSON.stringify(await api.state(), null, 2)); break;
        default:
          console.log(`
Comms Hub Bridge Client (${MY_NAME})
${'='.repeat(40)}
Commands:
  health                                  Check hub status
  send <to> "<subj>" "<body>" [priority]  Send a message
  inbox                                   Check your inbox
  all                                     View all bridge messages
  ack <messageId>                         Acknowledge/remove a message
  files                                   List shared files
  upload <file-path>                      Upload a file to shared storage
  state                                   View bridge state
`);
      }
    } catch (err) {
      console.error('Bridge error:', err.message);
      process.exit(1);
    }
  })();
}

module.exports = { ...api, uploadFile, request };
