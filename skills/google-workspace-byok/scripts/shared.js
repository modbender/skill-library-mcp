/**
 * Shared Google OAuth2 utilities for google-workspace skill.
 * Handles credential storage, token refresh, and authenticated API clients.
 */

const fs = require('fs');
const path = require('path');
const { google } = require('googleapis');

const CONFIG_DIR = path.join(process.env.HOME || '~', '.openclaw', 'google-workspace-byok');
const CREDENTIALS_PATH = path.join(CONFIG_DIR, 'credentials.json');
const TOKENS_DIR = path.join(CONFIG_DIR, 'tokens');

const SCOPES_READONLY = [
  'https://www.googleapis.com/auth/calendar.readonly',
  'https://www.googleapis.com/auth/gmail.readonly',
];

const SCOPES_READWRITE = [
  'https://www.googleapis.com/auth/calendar',          // Full calendar read/write
  'https://www.googleapis.com/auth/gmail.readonly',
];

function ensureDirs() {
  fs.mkdirSync(CONFIG_DIR, { recursive: true });
  fs.mkdirSync(TOKENS_DIR, { recursive: true });
}

function loadCredentials() {
  if (!fs.existsSync(CREDENTIALS_PATH)) {
    throw new Error(
      `No credentials found at ${CREDENTIALS_PATH}\n` +
      `Run: node setup.js --credentials /path/to/credentials.json`
    );
  }
  const raw = JSON.parse(fs.readFileSync(CREDENTIALS_PATH, 'utf8'));
  // Google credentials JSON can have the client info under "installed" or "web"
  const creds = raw.installed || raw.web;
  if (!creds) {
    throw new Error('Invalid credentials.json — expected "installed" or "web" key');
  }
  return creds;
}

function tokenPath(accountLabel) {
  return path.join(TOKENS_DIR, `${accountLabel}.json`);
}

function loadToken(accountLabel) {
  const tp = tokenPath(accountLabel);
  if (!fs.existsSync(tp)) {
    throw new Error(
      `No token found for account "${accountLabel}"\n` +
      `Run: node auth.js --account ${accountLabel}`
    );
  }
  return JSON.parse(fs.readFileSync(tp, 'utf8'));
}

function saveToken(accountLabel, token) {
  ensureDirs();
  fs.writeFileSync(tokenPath(accountLabel), JSON.stringify(token, null, 2));
}

function listAccounts() {
  ensureDirs();
  if (!fs.existsSync(TOKENS_DIR)) return [];
  return fs.readdirSync(TOKENS_DIR)
    .filter(f => f.endsWith('.json'))
    .map(f => f.replace('.json', ''));
}

/**
 * Get an authenticated OAuth2 client for the given account.
 * Automatically refreshes expired tokens.
 */
function getAuthClient(accountLabel) {
  const creds = loadCredentials();
  const token = loadToken(accountLabel);

  const oauth2 = new google.auth.OAuth2(
    creds.client_id,
    creds.client_secret,
    creds.redirect_uris ? creds.redirect_uris[0] : 'http://localhost'
  );

  oauth2.setCredentials(token);

  // Listen for token refresh events and persist
  oauth2.on('tokens', (newTokens) => {
    const updated = { ...token, ...newTokens };
    saveToken(accountLabel, updated);
  });

  return oauth2;
}

/**
 * Create a new OAuth2 client for the authorization flow (no tokens yet).
 */
function getOAuth2ClientForAuth() {
  const creds = loadCredentials();
  const redirectUri = creds.redirect_uris ? creds.redirect_uris[0] : 'http://localhost';
  return new google.auth.OAuth2(
    creds.client_id,
    creds.client_secret,
    redirectUri
  );
}

function parseArgs(argv) {
  const args = {};
  for (let i = 2; i < argv.length; i++) {
    if (argv[i].startsWith('--')) {
      const key = argv[i].slice(2);
      const next = argv[i + 1];
      if (next && !next.startsWith('--')) {
        args[key] = next;
        i++;
      } else {
        args[key] = true;
      }
    }
  }
  return args;
}

module.exports = {
  CONFIG_DIR,
  CREDENTIALS_PATH,
  TOKENS_DIR,
  SCOPES_READONLY,
  SCOPES_READWRITE,
  ensureDirs,
  loadCredentials,
  tokenPath,
  loadToken,
  saveToken,
  listAccounts,
  getAuthClient,
  getOAuth2ClientForAuth,
  parseArgs,
};
