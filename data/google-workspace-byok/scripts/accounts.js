/**
 * Account management script — list and check status of configured accounts.
 * 
 * Usage:
 *   node accounts.js --action <action> [options]
 * 
 * Actions:
 *   list                        List all configured accounts
 *   status                      Check token status for an account
 * 
 * Options:
 *   --account <label>           Account label (for status)
 */

const fs = require('fs');
const { google } = require('googleapis');
const {
  CREDENTIALS_PATH,
  listAccounts,
  getAuthClient,
  loadToken,
  parseArgs,
} = require('./shared');

const args = parseArgs(process.argv);
const action = args.action || 'list';

async function run() {
  switch (action) {
    case 'list': {
      const hasCredentials = fs.existsSync(CREDENTIALS_PATH);
      const accounts = listAccounts();

      console.log(JSON.stringify({
        credentialsConfigured: hasCredentials,
        accountCount: accounts.length,
        accounts: accounts.map(label => {
          try {
            const token = loadToken(label);
            return {
              label,
              hasAccessToken: !!token.access_token,
              hasRefreshToken: !!token.refresh_token,
              expiryDate: token.expiry_date
                ? new Date(token.expiry_date).toISOString()
                : null,
              scopes: token.scope ? token.scope.split(' ') : [],
            };
          } catch {
            return { label, error: 'Failed to load token' };
          }
        }),
      }, null, 2));
      break;
    }

    case 'status': {
      if (!args.account) {
        console.error('--account is required for status');
        process.exit(1);
      }

      try {
        const auth = getAuthClient(args.account);
        const oauth2 = google.oauth2({ version: 'v2', auth });
        const userInfo = await oauth2.userinfo.get();

        const token = loadToken(args.account);

        console.log(JSON.stringify({
          account: args.account,
          status: 'active',
          email: userInfo.data.email,
          name: userInfo.data.name,
          picture: userInfo.data.picture,
          scopes: token.scope ? token.scope.split(' ') : [],
          expiryDate: token.expiry_date
            ? new Date(token.expiry_date).toISOString()
            : null,
        }, null, 2));
      } catch (err) {
        console.log(JSON.stringify({
          account: args.account,
          status: 'error',
          error: err.message,
        }, null, 2));
      }
      break;
    }

    default:
      console.error(`Unknown action: ${action}`);
      console.error('Available: list, status');
      process.exit(1);
  }
}

run().catch((err) => {
  console.error(`Accounts error: ${err.message}`);
  process.exit(1);
});
