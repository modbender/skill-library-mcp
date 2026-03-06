#!/usr/bin/env node
/**
 * Praxis Google Workspace CLI
 * Official Google APIs wrapper for Gmail, Calendar, Drive
 */

const fs = require('fs');
const path = require('path');
const readline = require('readline');
const googleapisPath = path.join(process.env.PREFIX || '/usr/local', 'lib/node_modules/googleapis/build/src/index.js');
const { google } = require(googleapisPath);

// Simple base64url encoding for Gmail
const Base64 = {
  encodeURI: (str) => Buffer.from(str).toString('base64').replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '')
};

const CONFIG_DIR = path.join(process.env.HOME || '/tmp', '.config', 'praxis-gws');
const TOKEN_PATH = path.join(CONFIG_DIR, 'token.json');
const CREDENTIALS_PATH = path.join(CONFIG_DIR, 'credentials.json');

// Ensure config directory exists
fs.mkdirSync(CONFIG_DIR, { recursive: true });

// Load credentials
function loadCredentials() {
  if (!fs.existsSync(CREDENTIALS_PATH)) {
    console.error('Error: credentials.json not found.');
    console.error('Run: praxis-gws auth credentials /path/to/client_secret.json');
    process.exit(1);
  }
  return JSON.parse(fs.readFileSync(CREDENTIALS_PATH, 'utf8'));
}

// Load or refresh token
async function getAuthClient() {
  const credentials = loadCredentials();
  const { client_id, client_secret, redirect_uris } = credentials.installed || credentials.web;
  
  const oAuth2Client = new google.auth.OAuth2(client_id, client_secret, redirect_uris[0]);
  
  if (fs.existsSync(TOKEN_PATH)) {
    const token = JSON.parse(fs.readFileSync(TOKEN_PATH, 'utf8'));
    oAuth2Client.setCredentials(token);
    return oAuth2Client;
  }
  
  return await authorize(oAuth2Client);
}

// OAuth flow
async function authorize(oAuth2Client) {
  const authUrl = oAuth2Client.generateAuthUrl({
    access_type: 'offline',
    scope: [
      'https://www.googleapis.com/auth/gmail.modify',
      'https://www.googleapis.com/auth/calendar',
      'https://www.googleapis.com/auth/drive.readonly',
    ],
  });
  
  console.log('Authorize this app by visiting this URL:');
  console.log(authUrl);
  console.log('');
  
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });
  
  return new Promise((resolve) => {
    rl.question('Enter the code from that page here: ', (code) => {
      rl.close();
      oAuth2Client.getToken(code, (err, token) => {
        if (err) {
          console.error('Error retrieving access token', err);
          process.exit(1);
        }
        oAuth2Client.setCredentials(token);
        fs.writeFileSync(TOKEN_PATH, JSON.stringify(token));
        console.log('Token stored to', TOKEN_PATH);
        resolve(oAuth2Client);
      });
    });
  });
}

// Gmail commands
const gmail = {
  async search(query, options = {}) {
    const auth = await getAuthClient();
    const gmail = google.gmail({ version: 'v1', auth });
    
    const res = await gmail.users.messages.list({
      userId: 'me',
      q: query,
      maxResults: options.max || 10,
    });
    
    const messages = res.data.messages || [];
    console.log(JSON.stringify(messages, null, 2));
  },
  
  async get(id) {
    const auth = await getAuthClient();
    const gmail = google.gmail({ version: 'v1', auth });
    
    const res = await gmail.users.messages.get({
      userId: 'me',
      id: id,
      format: 'full',
    });
    
    console.log(JSON.stringify(res.data, null, 2));
  },
  
  async send(to, subject, body, options = {}) {
    const auth = await getAuthClient();
    const gmail = google.gmail({ version: 'v1', auth });
    
    const utf8Subject = `=?utf-8?B?${Buffer.from(subject).toString('base64')}?=`;
    const messageParts = [
      `To: ${to}`,
      `Subject: ${utf8Subject}`,
      'MIME-Version: 1.0',
      'Content-Type: text/plain; charset=utf-8',
      'Content-Transfer-Encoding: 7bit',
      '',
      body,
    ];
    
    const message = messageParts.join('\n');
    const encodedMessage = Base64.encodeURI(message);
    
    const res = await gmail.users.messages.send({
      userId: 'me',
      requestBody: {
        raw: encodedMessage,
      },
    });
    
    console.log('Message sent:', res.data.id);
  },
  
  async labels() {
    const auth = await getAuthClient();
    const gmail = google.gmail({ version: 'v1', auth });
    
    const res = await gmail.users.labels.list({ userId: 'me' });
    console.log(JSON.stringify(res.data.labels, null, 2));
  },
  
  async modify(id, addLabels, removeLabels) {
    const auth = await getAuthClient();
    const gmail = google.gmail({ version: 'v1', auth });
    
    const res = await gmail.users.messages.modify({
      userId: 'me',
      id: id,
      requestBody: {
        addLabelIds: addLabels ? addLabels.split(',') : [],
        removeLabelIds: removeLabels ? removeLabels.split(',') : [],
      },
    });
    
    console.log('Message modified:', res.data.id);
  },
  
  async draft(to, subject, body) {
    const auth = await getAuthClient();
    const gmail = google.gmail({ version: 'v1', auth });
    
    const utf8Subject = `=?utf-8?B?${Buffer.from(subject).toString('base64')}?=`;
    const messageParts = [
      `To: ${to}`,
      `Subject: ${utf8Subject}`,
      'MIME-Version: 1.0',
      'Content-Type: text/plain; charset=utf-8',
      '',
      body,
    ];
    
    const message = messageParts.join('\n');
    const encodedMessage = Base64.encodeURI(message);
    
    const res = await gmail.users.drafts.create({
      userId: 'me',
      requestBody: {
        message: {
          raw: encodedMessage,
        },
      },
    });
    
    console.log('Draft created:', res.data.id);
  },
};

// Calendar commands
const calendar = {
  async list(calendarId = 'primary', options = {}) {
    const auth = await getAuthClient();
    const cal = google.calendar({ version: 'v3', auth });
    
    const now = new Date();
    const timeMin = options.from || now.toISOString();
    const timeMax = options.to || new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000).toISOString();
    
    const res = await cal.events.list({
      calendarId,
      timeMin,
      timeMax,
      maxResults: options.max || 10,
      singleEvents: true,
      orderBy: 'startTime',
    });
    
    console.log(JSON.stringify(res.data.items, null, 2));
  },
  
  async create(calendarId, summary, options = {}) {
    const auth = await getAuthClient();
    const cal = google.calendar({ version: 'v3', auth });
    
    const event = {
      summary,
      start: {
        dateTime: options.from || new Date().toISOString(),
        timeZone: options.timezone || 'America/Phoenix',
      },
      end: {
        dateTime: options.to || new Date(Date.now() + 60 * 60 * 1000).toISOString(),
        timeZone: options.timezone || 'America/Phoenix',
      },
    };
    
    if (options.description) event.description = options.description;
    if (options.location) event.location = options.location;
    
    const res = await cal.events.insert({
      calendarId,
      requestBody: event,
    });
    
    console.log('Event created:', res.data.htmlLink);
  },
};

// Drive commands
const drive = {
  async search(query, options = {}) {
    const auth = await getAuthClient();
    const drv = google.drive({ version: 'v3', auth });
    
    const res = await drv.files.list({
      q: query,
      pageSize: options.max || 10,
      fields: 'files(id, name, mimeType, modifiedTime)',
    });
    
    console.log(JSON.stringify(res.data.files, null, 2));
  },
  
  async get(fileId) {
    const auth = await getAuthClient();
    const drv = google.drive({ version: 'v3', auth });
    
    const res = await drv.files.get({
      fileId,
      fields: '*',
    });
    
    console.log(JSON.stringify(res.data, null, 2));
  },
};

// Auth commands
const auth = {
  credentials(srcPath) {
    if (!fs.existsSync(srcPath)) {
      console.error('Error: File not found:', srcPath);
      process.exit(1);
    }
    fs.copyFileSync(srcPath, CREDENTIALS_PATH);
    console.log('Credentials saved to', CREDENTIALS_PATH);
    console.log('Run any command to start OAuth flow');
  },
  
  async status() {
    if (!fs.existsSync(CREDENTIALS_PATH)) {
      console.log('Status: No credentials configured');
      return;
    }
    if (!fs.existsSync(TOKEN_PATH)) {
      console.log('Status: Credentials configured, authentication needed');
      return;
    }
    console.log('Status: Authenticated');
    console.log('Token:', TOKEN_PATH);
  },
};

// CLI
async function main() {
  const args = process.argv.slice(2);
  const command = args[0];
  const subcommand = args[1];
  
  if (!command || command === '--help' || command === '-h') {
    console.log('Praxis Google Workspace CLI');
    console.log('');
    console.log('Usage:');
    console.log('  praxis-gws auth credentials <path>     - Set OAuth credentials');
    console.log('  praxis-gws auth status                 - Check auth status');
    console.log('');
    console.log('Gmail:');
    console.log('  praxis-gws gmail search <query>        - Search messages');
    console.log('  praxis-gws gmail get <id>              - Get message by ID');
    console.log('  praxis-gws gmail send <to> <subject> <body>');
    console.log('  praxis-gws gmail draft <to> <subject> <body>');
    console.log('  praxis-gws gmail labels                - List labels');
    console.log('  praxis-gws gmail modify <id> --add <labels> --remove <labels>');
    console.log('');
    console.log('Calendar:');
    console.log('  praxis-gws calendar list [calendarId]  - List events');
    console.log('  praxis-gws calendar create <calendarId> <summary> --from <iso> --to <iso>');
    console.log('');
    console.log('Drive:');
    console.log('  praxis-gws drive search <query>        - Search files');
    console.log('  praxis-gws drive get <fileId>          - Get file metadata');
    console.log('');
    console.log('Examples:');
    console.log('  praxis-gws gmail search "is:unread from:arnoldventures.org"');
    console.log('  praxis-gws calendar create primary "FAIR Coalition Meeting" --from 2026-02-25T14:00:00 --to 2026-02-25T15:00:00');
    process.exit(0);
  }
  
  try {
    if (command === 'auth') {
      if (subcommand === 'credentials') {
        auth.credentials(args[2]);
      } else if (subcommand === 'status') {
        await auth.status();
      } else {
        console.error('Unknown auth command:', subcommand);
      }
      return;
    }
    
    if (command === 'gmail') {
      if (subcommand === 'search') {
        const query = args.slice(2).join(' ') || '';
        const maxIndex = args.indexOf('--max');
        const max = maxIndex > -1 ? parseInt(args[maxIndex + 1]) : 10;
        await gmail.search(query, { max });
      } else if (subcommand === 'get') {
        await gmail.get(args[2]);
      } else if (subcommand === 'send') {
        await gmail.send(args[2], args[3], args.slice(4).join(' '));
      } else if (subcommand === 'draft') {
        await gmail.draft(args[2], args[3], args.slice(4).join(' '));
      } else if (subcommand === 'labels') {
        await gmail.labels();
      } else if (subcommand === 'modify') {
        const addIndex = args.indexOf('--add');
        const removeIndex = args.indexOf('--remove');
        const addLabels = addIndex > -1 ? args[addIndex + 1] : '';
        const removeLabels = removeIndex > -1 ? args[removeIndex + 1] : '';
        await gmail.modify(args[2], addLabels, removeLabels);
      } else {
        console.error('Unknown gmail command:', subcommand);
      }
      return;
    }
    
    if (command === 'calendar') {
      if (subcommand === 'list') {
        const calendarId = args[2] || 'primary';
        const fromIndex = args.indexOf('--from');
        const toIndex = args.indexOf('--to');
        const maxIndex = args.indexOf('--max');
        await calendar.list(calendarId, {
          from: fromIndex > -1 ? args[fromIndex + 1] : undefined,
          to: toIndex > -1 ? args[toIndex + 1] : undefined,
          max: maxIndex > -1 ? parseInt(args[maxIndex + 1]) : 10,
        });
      } else if (subcommand === 'create') {
        const calendarId = args[2];
        const summary = args[3];
        const fromIndex = args.indexOf('--from');
        const toIndex = args.indexOf('--to');
        const tzIndex = args.indexOf('--timezone');
        await calendar.create(calendarId, summary, {
          from: fromIndex > -1 ? args[fromIndex + 1] : undefined,
          to: toIndex > -1 ? args[toIndex + 1] : undefined,
          timezone: tzIndex > -1 ? args[tzIndex + 1] : 'America/Phoenix',
        });
      } else {
        console.error('Unknown calendar command:', subcommand);
      }
      return;
    }
    
    if (command === 'drive') {
      if (subcommand === 'search') {
        const query = args.slice(2).join(' ') || '';
        const maxIndex = args.indexOf('--max');
        await drive.search(query, { max: maxIndex > -1 ? parseInt(args[maxIndex + 1]) : 10 });
      } else if (subcommand === 'get') {
        await drive.get(args[2]);
      } else {
        console.error('Unknown drive command:', subcommand);
      }
      return;
    }
    
    console.error('Unknown command:', command);
  } catch (err) {
    console.error('Error:', err.message);
    process.exit(1);
  }
}

main();
