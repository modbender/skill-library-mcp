/**
 * Trifle API client
 */

import { readFileSync, existsSync } from 'fs';
import { PATHS, getBackendUrl } from './config.mjs';

let cachedToken = null;
let tokenLoadedAt = 0;
const TOKEN_CACHE_MS = 60000; // Reload token every minute

/**
 * Load auth token — resolution order:
 *   1. TRIFLE_AUTH_TOKEN env var (highest priority, explicit)
 *   2. ~/.config/snake-rodeo/auth.json  { "token": "..." }
 *      (populated by `snake auth login` or copied manually from trifle-auth)
 *
 * Never reads from host agent internals (~/.openclaw/...).
 */
function loadToken() {
  // 1. Environment variable — always authoritative
  if (process.env.TRIFLE_AUTH_TOKEN) {
    return process.env.TRIFLE_AUTH_TOKEN;
  }

  const now = Date.now();
  if (cachedToken && (now - tokenLoadedAt) < TOKEN_CACHE_MS) {
    return cachedToken;
  }

  try {
    if (existsSync(PATHS.authFile)) {
      const state = JSON.parse(readFileSync(PATHS.authFile, 'utf8'));
      cachedToken = state?.token || null;
      tokenLoadedAt = now;
      return cachedToken;
    }
  } catch {}
  return null;
}

/**
 * Clear cached token (force reload on next request)
 */
export function clearTokenCache() {
  cachedToken = null;
  tokenLoadedAt = 0;
}

/**
 * Make an API request to Trifle backend
 */
export async function apiRequest(path, options = {}) {
  const url = `${getBackendUrl()}${path}`;
  const res = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Origin': 'https://trifle.life',
      'Referer': 'https://trifle.life/',
      ...options.headers,
    },
  });

  if (!res.ok) {
    const text = await res.text();
    const error = new Error(`API ${res.status}: ${text}`);
    error.status = res.status;
    error.body = text;
    throw error;
  }

  return res.json();
}

/**
 * Make an authenticated API request
 * Returns null if not authenticated (instead of throwing)
 */
export async function authRequest(path, options = {}) {
  const token = loadToken();
  if (!token) {
    return { error: 'AUTH_MISSING', message: 'Not authenticated' };
  }

  try {
    return await apiRequest(path, {
      ...options,
      headers: {
        'Authorization': `Bearer ${token}`,
        ...options.headers,
      },
    });
  } catch (e) {
    if (e.status === 401 || e.status === 403) {
      clearTokenCache();
      return { error: 'AUTH_EXPIRED', message: 'Token expired' };
    }
    throw e;
  }
}

/**
 * Get current game state
 */
export async function getGameState() {
  const result = await authRequest('/snake/state');
  if (result.error) return result;
  return result.gameState || result;
}

/**
 * Get ball balance
 */
export async function getBalance() {
  try {
    const result = await authRequest('/balls');
    if (result.error) return 0;
    return result.balls ?? result.totalBalls ?? 0;
  } catch {
    return 0;
  }
}

/**
 * Submit a vote
 */
export async function submitVote(direction, team, amount) {
  return authRequest('/snake/vote', {
    method: 'POST',
    body: JSON.stringify({ direction, team, amount }),
  });
}

/**
 * Get rodeo configurations
 */
export async function getRodeos() {
  const result = await apiRequest('/snake/rodeos');
  return Array.isArray(result) ? result : result.rodeos || [];
}

/**
 * Check if authenticated
 */
export function isAuthenticated() {
  return !!loadToken();
}
