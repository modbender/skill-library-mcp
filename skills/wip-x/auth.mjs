/**
 * wip-x/auth.mjs
 * OAuth and token management for X Platform API.
 * Resolves credentials from 1Password or environment variables.
 */

import { execSync } from 'node:child_process';

const OP_VAULT = process.env.X_OP_VAULT || 'Agent Secrets';
const OP_ITEM = process.env.X_OP_ITEM || 'X API Key - wip-01';

/**
 * Read a field from 1Password.
 * Returns null if op CLI is not available or field not found.
 */
function opRead(field) {
  try {
    const ref = `op://${OP_VAULT}/${OP_ITEM}/${field}`;
    return execSync(`op read "${ref}" 2>/dev/null`, { encoding: 'utf8' }).trim() || null;
  } catch {
    return null;
  }
}

/**
 * Resolve all available credentials.
 * Priority: environment variables first, then 1Password.
 *
 * Environment variables:
 *   X_BEARER_TOKEN       ... app-only bearer token (read operations)
 *   X_API_KEY            ... OAuth 1.0a consumer key
 *   X_API_SECRET         ... OAuth 1.0a consumer secret
 *   X_ACCESS_TOKEN       ... OAuth 1.0a access token
 *   X_ACCESS_TOKEN_SECRET ... OAuth 1.0a access token secret
 *
 * 1Password (configurable via env):
 *   X_OP_VAULT  ... vault name (default: "Agent Secrets")
 *   X_OP_ITEM   ... item name (default: "X API Key - wip-01")
 *   Fields: bearer token, api key, api secret, access token, access token secret
 */
export function resolveAuth() {
  const auth = {
    bearerToken: process.env.X_BEARER_TOKEN || opRead('bearer token'),
    apiKey: process.env.X_API_KEY || opRead('api key'),
    apiSecret: process.env.X_API_SECRET || opRead('api secret'),
    accessToken: process.env.X_ACCESS_TOKEN || opRead('access token'),
    accessTokenSecret: process.env.X_ACCESS_TOKEN_SECRET || opRead('access token secret'),
  };

  if (!auth.bearerToken && !auth.apiKey) {
    throw new Error(
      'X Platform API credentials not found.\n' +
      'Set X_BEARER_TOKEN (for read-only) or X_API_KEY + X_API_SECRET + X_ACCESS_TOKEN + X_ACCESS_TOKEN_SECRET (for read/write).\n' +
      `Or add them to 1Password: vault "${OP_VAULT}", item "${OP_ITEM}".`
    );
  }

  return auth;
}

/**
 * Build the config object for the @xdevplatform/xdk Client constructor.
 * Uses OAuth 1.0a if all four tokens are available (needed for write operations).
 * Falls back to bearer token for read-only access.
 */
export async function getClientConfig(auth) {
  if (!auth) auth = resolveAuth();

  // If we have OAuth 1.0a credentials, use them (supports read + write)
  if (auth.apiKey && auth.apiSecret && auth.accessToken && auth.accessTokenSecret) {
    const { OAuth1 } = await import('@xdevplatform/xdk');
    const oauth1 = new OAuth1({
      apiKey: auth.apiKey,
      apiSecret: auth.apiSecret,
      accessToken: auth.accessToken,
      accessTokenSecret: auth.accessTokenSecret,
    });
    return { oauth1 };
  }

  // Bearer token only (read operations)
  if (auth.bearerToken) {
    return { bearerToken: auth.bearerToken };
  }

  throw new Error('No valid auth configuration. Need bearer token or full OAuth 1.0a credentials.');
}
