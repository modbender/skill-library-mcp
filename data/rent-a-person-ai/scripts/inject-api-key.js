#!/usr/bin/env node
/**
 * RentAPerson API key shim for the webhook session.
 * Run first to validate env; use as a curl wrapper so every request gets the key.
 *
 * Validate only (run at start of session):
 *   node scripts/inject-api-key.js
 *   → Exits 0 if RENTAPERSON_API_KEY is set, 1 otherwise (logs to stderr).
 *
 * Wrap curl (so the key is always included):
 *   node scripts/inject-api-key.js -- curl -s "https://rentaperson.ai/api/conversations?agentId=..."
 *   → Runs curl with -H "X-API-Key: $RENTAPERSON_API_KEY" prepended.
 */

const { spawnSync } = require('child_process');

const key = process.env.RENTAPERSON_API_KEY;

function validate() {
  if (!key || !String(key).trim()) {
    process.stderr.write(
      'inject-api-key: RENTAPERSON_API_KEY is not set. Set it in skills.entries["rent-a-person-ai"].env (e.g. run scripts/setup.js) and restart the gateway.\n'
    );
    process.exit(1);
  }
  process.exit(0);
}

function wrapCurl(args) {
  if (!key || !String(key).trim()) {
    process.stderr.write(
      'inject-api-key: RENTAPERSON_API_KEY is not set. Aborting so the request does not go out without the key (and fall back to WhatsApp).\n'
    );
    process.exit(1);
  }
  // Prepend -H "X-API-Key: <key>" to the curl arguments
  const curlArgs = ['-H', `X-API-Key: ${key}`, ...args];
  const result = spawnSync('curl', curlArgs, {
    stdio: 'inherit',
    shell: false,
  });
  process.exit(result.status !== null ? result.status : 1);
}

const argv = process.argv.slice(2);
const dashDash = argv.indexOf('--');
if (dashDash === -1) {
  // No "--" → validate only
  validate();
}
const after = argv.slice(dashDash + 1);
if (after.length === 0 || after[0] !== 'curl') {
  validate();
}
// after = ["curl", "-s", "https://..."] → pass ["-s", "https://..."] to curl with key header
wrapCurl(after.slice(1));
