/**
 * Setup script — copies Google OAuth credentials into the config directory.
 * Usage: node setup.js --credentials /path/to/credentials.json
 */

const fs = require('fs');
const { CREDENTIALS_PATH, ensureDirs, parseArgs } = require('./shared');

const args = parseArgs(process.argv);

if (!args.credentials) {
  console.error('Usage: node setup.js --credentials /path/to/credentials.json');
  process.exit(1);
}

if (!fs.existsSync(args.credentials)) {
  console.error(`File not found: ${args.credentials}`);
  process.exit(1);
}

// Validate the file
try {
  const raw = JSON.parse(fs.readFileSync(args.credentials, 'utf8'));
  const creds = raw.installed || raw.web;
  if (!creds || !creds.client_id || !creds.client_secret) {
    console.error('Invalid credentials file — missing client_id or client_secret');
    process.exit(1);
  }
  console.log(`✓ Valid credentials for client: ${creds.client_id.substring(0, 20)}...`);
} catch (e) {
  console.error(`Failed to parse credentials file: ${e.message}`);
  process.exit(1);
}

ensureDirs();
fs.copyFileSync(args.credentials, CREDENTIALS_PATH);
console.log(`✓ Credentials saved to ${CREDENTIALS_PATH}`);
console.log('\nNext: Authorize a Google account:');
console.log('  node auth.js --account <label>');
