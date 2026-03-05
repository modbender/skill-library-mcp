/**
 * 飞书 (Feishu) API Wrapper
 * Handles authentication and API calls with automatic token refresh
 * Auto-discovers credentials from Clawdbot's openclaw.json
 */

import { config } from 'dotenv';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { existsSync, readFileSync } from 'fs';

const __dirname = dirname(fileURLToPath(import.meta.url));

/**
 * Find and load credentials from Clawdbot's openclaw.json
 */
function loadCredentials() {
  // Check if already in environment
  if (process.env.FEISHU_APP_ID && process.env.FEISHU_APP_SECRET) {
    return {
      appId: process.env.FEISHU_APP_ID,
      appSecret: process.env.FEISHU_APP_SECRET,
      source: 'environment'
    };
  }

  // Try to read from openclaw.json
  const openclawPaths = [
    join(process.env.HOME || '', '.openclaw', 'openclaw.json'),
    join(process.env.HOME || '', 'openclaw', '.openclaw', 'openclaw.json'),
    join(__dirname, '../../../../.openclaw', 'openclaw.json'),
  ];

  for (const configPath of openclawPaths) {
    if (existsSync(configPath)) {
      try {
        const config = JSON.parse(readFileSync(configPath, 'utf-8'));

        // Check if feishu channel is configured
        if (config.channels?.feishu?.accounts) {
          const accounts = config.channels.feishu.accounts;
          const accountNames = Object.keys(accounts);

          if (accountNames.length === 0) {
            continue;
          }

          // Use the first enabled account, or first account
          let selectedAccount = null;

          // Prefer 'default' account
          if (accounts.default?.enabled) {
            selectedAccount = accounts.default;
          } else {
            // Find first enabled account
            const enabledName = accountNames.find(name => accounts[name]?.enabled);
            if (enabledName) {
              selectedAccount = accounts[enabledName];
            } else {
              // Fallback to first account
              selectedAccount = accounts[accountNames[0]];
            }
          }

          if (selectedAccount?.appId && selectedAccount?.appSecret) {
            if (process.env.DEBUG) {
              console.log(`[lark-api] Loaded credentials from: ${configPath}`);
              console.log(`[lark-api] Using account: ${accountNames.find(name => accounts[name] === selectedAccount) || 'unknown'}`);
            }
            return {
              appId: selectedAccount.appId,
              appSecret: selectedAccount.appSecret,
              source: configPath,
              account: 'feishu'
            };
          }
        }
      } catch (error) {
        if (process.env.DEBUG) {
          console.warn(`[lark-api] Failed to read ${configPath}:`, error.message);
        }
      }
    }
  }

  // Fallback: try .secrets.env files
  const secretPaths = [
    join(process.env.HOME || '', 'openclaw', '.secrets.env'),
    join(process.env.HOME || '', '.secrets.env'),
  ];

  for (const envPath of secretPaths) {
    if (existsSync(envPath)) {
      config({ path: envPath });
      if (process.env.FEISHU_APP_ID && process.env.FEISHU_APP_SECRET) {
        return {
          appId: process.env.FEISHU_APP_ID,
          appSecret: process.env.FEISHU_APP_SECRET,
          source: envPath
        };
      }
    }
  }

  return null;
}

// Load credentials
const creds = loadCredentials();

if (!creds) {
  throw new Error(
    'FEISHU_APP_ID and FEISHU_APP_SECRET not found!\n\n' +
    'Please configure your Feishu app in one of these ways:\n\n' +
    'Option 1: Add to ~/.openclaw/openclaw.json:\n' +
    '  {\n' +
    '    "channels": {\n' +
    '      "feishu": {\n' +
    '        "accounts": {\n' +
    '          "default": {\n' +
    '            "appId": "cli_xxxxxxxxxxxxx",\n' +
    '            "appSecret": "xxxxxxxxxxxxxxxxxxxx",\n' +
    '            "enabled": true\n' +
    '          }\n' +
    '        }\n' +
    '      }\n' +
    '    }\n' +
    '  }\n\n' +
    'Option 2: Add to ~/openclaw/.secrets.env:\n' +
    '  FEISHU_APP_ID=cli_xxxxxxxxxxxxx\n' +
    '  FEISHU_APP_SECRET=xxxxxxxxxxxxxxxxxxxx\n\n' +
    'Option 3: Set as environment variables'
  );
}

const APP_ID = creds.appId;
const APP_SECRET = creds.appSecret;

// 使用飞书开放平台 API
const BASE_URL = 'https://open.larksuite.com/open-apis';

let accessToken = null;
let tokenExpiry = 0;

/**
 * Get or refresh access token
 */
async function getAccessToken() {
  // Return cached token if still valid (with 5 min buffer)
  if (accessToken && Date.now() < tokenExpiry - 300000) {
    return accessToken;
  }

  const response = await fetch(`${BASE_URL}/auth/v3/tenant_access_token/internal`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      app_id: APP_ID,
      app_secret: APP_SECRET
    })
  });

  const data = await response.json();

  if (data.code !== 0) {
    throw new Error(`Failed to get access token: ${JSON.stringify(data)}`);
  }

  accessToken = `Bearer ${data.tenant_access_token}`;
  // Token expires in ~2 hours, we store expiry time
  tokenExpiry = Date.now() + (data.expire * 1000);

  return accessToken;
}

/**
 * Make authenticated API request
 * @param {string} method - HTTP method
 * @param {string} endpoint - API endpoint (without base URL)
 * @param {object} options - { params, data }
 * @returns {object} - Response data
 */
export async function larkApi(method, endpoint, { params = null, data = null } = {}) {
  const token = await getAccessToken();

  let url = `${BASE_URL}${endpoint}`;

  // Add query params
  if (params) {
    const searchParams = new URLSearchParams();
    for (const [key, value] of Object.entries(params)) {
      if (value !== undefined && value !== null) {
        searchParams.append(key, value);
      }
    }
    const queryString = searchParams.toString();
    if (queryString) {
      url += `?${queryString}`;
    }
  }

  const fetchOptions = {
    method,
    headers: {
      'Authorization': token,
      'Content-Type': 'application/json'
    }
  };

  if (data && ['POST', 'PUT', 'PATCH'].includes(method.toUpperCase())) {
    fetchOptions.body = JSON.stringify(data);
  }

  const response = await fetch(url, fetchOptions);
  const result = await response.json();

  // Check for token expiry error
  if (result.code === 99991663) {
    // Token expired, clear cache and retry once
    accessToken = null;
    tokenExpiry = 0;
    return larkApi(method, endpoint, { params, data });
  }

  if (result.code !== 0) {
    const error = new Error(`飞书 API error: ${JSON.stringify(result)}`);
    error.code = result.code;
    error.larkResponse = result;
    throw error;
  }

  return result.data;
}

/**
 * Reply to a message
 * @param {string} messageId - Message ID to reply to
 * @param {object} content - Message content
 */
export async function replyMessage(messageId, content) {
  return larkApi('POST', `/im/v1/messages/${messageId}/reply`, { data: content });
}

/**
 * Send message to a chat
 * @param {string} receiveId - Chat ID or user ID
 * @param {string} receiveIdType - 'chat_id' | 'user_id' | 'open_id'
 * @param {object} content - Message content
 */
export async function sendMessage(receiveId, receiveIdType, content) {
  return larkApi('POST', '/im/v1/messages', {
    params: { receive_id_type: receiveIdType },
    data: {
      receive_id: receiveId,
      ...content
    }
  });
}

/**
 * Export credentials for debugging
 */
export function getCredentials() {
  return {
    appId: APP_ID,
    source: creds.source
  };
}
