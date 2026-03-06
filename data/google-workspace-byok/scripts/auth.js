/**
 * Auth script — runs the OAuth2 consent flow for a Google account.
 * 
 * Uses a manual code-paste flow:
 *   1. Generates an auth URL with redirect to http://localhost
 *   2. User opens URL in browser, authorizes, gets redirected
 *   3. Google redirects to http://localhost (which won't load — that's fine)
 *   4. User copies the full redirect URL (or just the code param) and pastes it back
 *   5. Script exchanges the code for tokens
 * 
 * Usage: node auth.js --account <label>
 */

const readline = require('readline');
const { URL } = require('url');
const {
  SCOPES_READONLY,
  SCOPES_READWRITE,
  loadCredentials,
  saveToken,
  parseArgs,
} = require('./shared');
const { google } = require('googleapis');

const args = parseArgs(process.argv);

if (!args.account) {
  console.error('Usage: node auth.js --account <label>');
  console.error('  label: friendly name like "ken", "household", "work"');
  process.exit(1);
}

const accountLabel = args.account;

// Use a fixed redirect URI for the manual flow
const REDIRECT_URI = 'http://localhost';

async function run() {
  const creds = loadCredentials();

  // Use read/write scopes by default; pass --readonly for read-only
  const scopes = args.readonly ? SCOPES_READONLY : SCOPES_READWRITE;

  const oauth2 = new google.auth.OAuth2(
    creds.client_id,
    creds.client_secret,
    REDIRECT_URI
  );

  const authUrl = oauth2.generateAuthUrl({
    access_type: 'offline',
    scope: scopes,
    prompt: 'consent',
    redirect_uri: REDIRECT_URI,
  });

  console.log(`\nAuthorize the "${accountLabel}" account:\n`);
  console.log(`1. Open this URL in your browser:\n`);
  console.log(authUrl);
  console.log(`\n2. Sign in and grant access.`);
  console.log(`3. You'll be redirected to a page that won't load (http://localhost/...) — that's expected.`);
  console.log(`4. Copy the FULL URL from your browser's address bar and paste it below.\n`);
  console.log(`   (Or just paste the "code" parameter value if you prefer)\n`);

  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  const input = await new Promise((resolve) => {
    rl.question('Paste URL or code here: ', (answer) => {
      rl.close();
      resolve(answer.trim());
    });
  });

  // Extract the authorization code
  let code;
  try {
    // Try parsing as a full URL first
    const url = new URL(input);
    code = url.searchParams.get('code');
    if (!code) {
      throw new Error('No "code" parameter found in URL');
    }
  } catch {
    // Not a valid URL — treat the entire input as the code
    code = input;
  }

  if (!code) {
    console.error('No authorization code provided.');
    process.exit(1);
  }

  console.log('\nExchanging code for tokens...');

  try {
    const { tokens } = await oauth2.getToken({ code, redirect_uri: REDIRECT_URI });
    saveToken(accountLabel, tokens);

    console.log(`\n✓ Account "${accountLabel}" authorized and tokens saved!`);
    console.log(`  Scopes: ${scopes.join(', ')}`);
  } catch (err) {
    console.error(`\n✗ Token exchange failed: ${err.message}`);
    if (err.message.includes('invalid_grant')) {
      console.error('  The code may have expired. Try again with a fresh URL.');
    }
    process.exit(1);
  }
}

run().catch((err) => {
  console.error('Auth error:', err.message);
  process.exit(1);
});
