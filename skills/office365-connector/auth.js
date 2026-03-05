#!/usr/bin/env node
/**
 * Microsoft Graph OAuth 2.0 Device Code Flow Authentication
 * Handles token acquisition, refresh, and storage
 * Supports multiple accounts
 */

const https = require('https');
const fs = require('fs');
const path = require('path');
const { getAccount } = require('./accounts.js');

const SCOPES = [
  'User.Read',
  'Mail.Read',
  'Mail.ReadWrite',
  'Mail.Send',
  'Calendars.Read',
  'Calendars.ReadWrite',
  'Contacts.Read',
  'Contacts.ReadWrite',
  'offline_access'
].join(' ');

/**
 * Get account configuration
 */
function getAccountConfig(accountName) {
  try {
    return getAccount(accountName);
  } catch (error) {
    // Fallback to environment variables for backward compatibility
    const tenantId = process.env.AZURE_TENANT_ID;
    const clientId = process.env.AZURE_CLIENT_ID;
    const clientSecret = process.env.AZURE_CLIENT_SECRET;
    
    if (!tenantId || !clientId || !clientSecret) {
      throw new Error('No account configured and no credentials in environment. Run: node accounts.js add <name> ...');
    }
    
    // Return legacy format
    return {
      name: 'legacy',
      tenantId,
      clientId,
      clientSecret,
      tokenPath: path.join(process.env.HOME, '.openclaw', 'auth', 'microsoft-graph.json')
    };
  }
}

/**
 * Make HTTPS request
 */
function httpsRequest(url, options = {}) {
  return new Promise((resolve, reject) => {
    const urlObj = new URL(url);
    const reqOptions = {
      hostname: urlObj.hostname,
      path: urlObj.pathname + urlObj.search,
      method: options.method || 'GET',
      headers: options.headers || {}
    };

    const req = https.request(reqOptions, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        try {
          const parsed = JSON.parse(data);
          if (res.statusCode >= 400) {
            reject(new Error(`HTTP ${res.statusCode}: ${parsed.error_description || parsed.error || data}`));
          } else {
            resolve(parsed);
          }
        } catch (e) {
          reject(new Error(`Failed to parse response: ${data}`));
        }
      });
    });

    req.on('error', reject);
    
    if (options.body) {
      req.write(options.body);
    }
    
    req.end();
  });
}

/**
 * Request device code
 */
async function requestDeviceCode(accountConfig) {
  const authority = `https://login.microsoftonline.com/${accountConfig.tenantId}`;
  const url = `${authority}/oauth2/v2.0/devicecode`;
  const body = new URLSearchParams({
    client_id: accountConfig.clientId,
    scope: SCOPES
  }).toString();

  return httpsRequest(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'Content-Length': Buffer.byteLength(body)
    },
    body
  });
}

/**
 * Poll for token
 */
async function pollForToken(deviceCode, accountConfig) {
  const authority = `https://login.microsoftonline.com/${accountConfig.tenantId}`;
  const url = `${authority}/oauth2/v2.0/token`;
  const body = new URLSearchParams({
    grant_type: 'urn:ietf:params:oauth:grant-type:device_code',
    client_id: accountConfig.clientId,
    device_code: deviceCode
  }).toString();

  return httpsRequest(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'Content-Length': Buffer.byteLength(body)
    },
    body
  });
}

/**
 * Refresh access token
 */
async function refreshAccessToken(refreshToken, accountConfig) {
  const authority = `https://login.microsoftonline.com/${accountConfig.tenantId}`;
  const url = `${authority}/oauth2/v2.0/token`;
  
  // Build request params - only include client_secret for confidential clients
  const params = {
    grant_type: 'refresh_token',
    client_id: accountConfig.clientId,
    refresh_token: refreshToken,
    scope: SCOPES
  };
  
  // Only include client_secret if it exists (for confidential client apps)
  // Public clients (device code flow) should NOT include it
  if (accountConfig.clientSecret && accountConfig.clientSecret !== '') {
    // Don't include it - public clients fail with client_secret
  }
  
  const body = new URLSearchParams(params).toString();

  return httpsRequest(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'Content-Length': Buffer.byteLength(body)
    },
    body
  });
}

/**
 * Save tokens to file
 */
function saveTokens(tokens, accountConfig) {
  const data = {
    access_token: tokens.access_token,
    refresh_token: tokens.refresh_token,
    expires_at: Date.now() + (tokens.expires_in * 1000),
    scope: tokens.scope
  };
  
  const tokenDir = path.dirname(accountConfig.tokenPath);
  if (!fs.existsSync(tokenDir)) {
    fs.mkdirSync(tokenDir, { recursive: true, mode: 0o700 });
  }
  
  fs.writeFileSync(accountConfig.tokenPath, JSON.stringify(data, null, 2), { mode: 0o600 });
  return data;
}

/**
 * Load tokens from file
 */
function loadTokens(accountConfig) {
  if (!fs.existsSync(accountConfig.tokenPath)) {
    return null;
  }
  
  try {
    const data = fs.readFileSync(accountConfig.tokenPath, 'utf8');
    return JSON.parse(data);
  } catch (e) {
    console.error('Failed to load tokens:', e.message);
    return null;
  }
}

/**
 * Get valid access token (with auto-refresh)
 */
async function getAccessToken(accountName = null) {
  const accountConfig = getAccountConfig(accountName);
  const tokens = loadTokens(accountConfig);
  
  if (!tokens) {
    throw new Error(`Not authenticated for account "${accountConfig.name}". Run authentication first.`);
  }
  
  // Check if token is expired (with 5 minute buffer)
  if (tokens.expires_at < Date.now() + (5 * 60 * 1000)) {
    console.error('Token expired, refreshing...');
    const refreshed = await refreshAccessToken(tokens.refresh_token, accountConfig);
    return saveTokens(refreshed, accountConfig).access_token;
  }
  
  return tokens.access_token;
}

/**
 * Main authentication flow
 */
async function authenticate(accountName = null) {
  const accountConfig = getAccountConfig(accountName);
  
  console.log(`Starting Microsoft Graph authentication for account "${accountConfig.name}"...\n`);
  
  // Check for existing valid tokens
  const existingTokens = loadTokens(accountConfig);
  if (existingTokens && existingTokens.expires_at > Date.now()) {
    console.log('✅ Already authenticated! Token is valid.');
    return existingTokens;
  }
  
  // Request device code
  console.log('Requesting device code...');
  const deviceCodeResponse = await requestDeviceCode(accountConfig);
  
  console.log('\n' + '='.repeat(60));
  console.log('📱 AUTHENTICATION REQUIRED');
  console.log('='.repeat(60));
  console.log(`\n1. Open this URL: ${deviceCodeResponse.verification_uri}`);
  console.log(`\n2. Enter this code: ${deviceCodeResponse.user_code}`);
  console.log(`\n3. Sign in with your Microsoft account`);
  console.log(`\n4. Approve the requested permissions`);
  console.log('\n' + '='.repeat(60) + '\n');
  console.log('Waiting for authentication...');
  
  // Poll for token
  const interval = deviceCodeResponse.interval * 1000;
  const expiresAt = Date.now() + (deviceCodeResponse.expires_in * 1000);
  
  while (Date.now() < expiresAt) {
    await new Promise(resolve => setTimeout(resolve, interval));
    
    try {
      const tokenResponse = await pollForToken(deviceCodeResponse.device_code, accountConfig);
      const saved = saveTokens(tokenResponse, accountConfig);
      
      console.log('\n✅ Authentication successful!');
      console.log(`Token expires: ${new Date(saved.expires_at).toLocaleString()}`);
      console.log(`Tokens saved to: ${accountConfig.tokenPath}\n`);
      
      return saved;
    } catch (error) {
      if (error.message.includes('authorization_pending') || error.message.includes('AADSTS70016')) {
        // Still waiting...
        process.stderr.write('.');
      } else if (error.message.includes('authorization_declined')) {
        throw new Error('User declined authorization');
      } else if (error.message.includes('expired_token') || error.message.includes('AADSTS70019')) {
        throw new Error('Device code expired - please try again');
      } else {
        throw error;
      }
    }
  }
  
  throw new Error('Authentication timed out');
}

// CLI usage
if (require.main === module) {
  const command = process.argv[2];
  const accountArg = process.argv.find(arg => arg.startsWith('--account='));
  const accountName = accountArg ? accountArg.split('=')[1] : null;
  
  if (command === 'login') {
    authenticate(accountName).catch(err => {
      console.error('\n❌ Authentication failed:', err.message);
      process.exit(1);
    });
  } else if (command === 'status') {
    try {
      const accountConfig = getAccountConfig(accountName);
      const tokens = loadTokens(accountConfig);
      
      console.log(`Account: ${accountConfig.name}`);
      
      if (!tokens) {
        console.log('Status: ❌ Not authenticated');
        process.exit(1);
      }
      
      const expired = tokens.expires_at < Date.now();
      console.log(`Status: ${expired ? '⚠️  Expired' : '✅ Valid'}`);
      console.log(`Expires: ${new Date(tokens.expires_at).toLocaleString()}`);
      console.log(`Scopes: ${tokens.scope}`);
      process.exit(expired ? 1 : 0);
    } catch (err) {
      console.error('❌ Error:', err.message);
      process.exit(1);
    }
  } else if (command === 'token') {
    getAccessToken(accountName)
      .then(token => {
        console.log(token);
        process.exit(0);
      })
      .catch(err => {
        console.error('❌ Failed to get token:', err.message);
        process.exit(1);
      });
  } else {
    console.log('Usage:');
    console.log('  node auth.js login [--account=name]   - Authenticate with Microsoft');
    console.log('  node auth.js status [--account=name]  - Check authentication status');
    console.log('  node auth.js token [--account=name]   - Get current access token');
    console.log('\nIf --account is not specified, the default account is used.');
    process.exit(1);
  }
}

module.exports = {
  authenticate,
  getAccessToken,
  loadTokens,
  saveTokens,
  refreshAccessToken
};
