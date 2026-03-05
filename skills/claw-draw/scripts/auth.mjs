#!/usr/bin/env node
/**
 * ClawDraw agent authentication with file-based token caching.
 *
 * Handles the agent API key -> JWT exchange flow. Caches tokens to
 * ~/.clawdraw/token.json with a 5-minute TTL to avoid repeated auth calls.
 *
 * Usage:
 *   import { getToken, createAgent, getAgentInfo } from './auth.mjs';
 *
 *   const token = await getToken();        // cached or fresh JWT
 *   const agent = await createAgent('MyBot'); // POST /api/agents
 *   const info  = await getAgentInfo(token);  // GET /api/agents/me
 */

// @security-manifest
// env: CLAWDRAW_API_KEY
// endpoints: api.clawdraw.ai (HTTPS)
// files: ~/.clawdraw/token.json, ~/.clawdraw/apikey.json
// exec: none

import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';

const LOGIC_URL = 'https://api.clawdraw.ai';
const CACHE_DIR = path.join(os.homedir(), '.clawdraw');
const CACHE_FILE = path.join(CACHE_DIR, 'token.json');
const APIKEY_FILE = path.join(CACHE_DIR, 'apikey.json');
const TOKEN_TTL_MS = 5 * 60 * 1000; // 5 minutes

// ---------------------------------------------------------------------------
// File-based token cache
// ---------------------------------------------------------------------------

function readCache() {
  try {
    const raw = fs.readFileSync(CACHE_FILE, 'utf-8');
    const data = JSON.parse(raw);
    if (data.token && data.expiresAt && Date.now() < data.expiresAt) {
      return data.token;
    }
  } catch {
    // No cache or invalid — that's fine
  }
  return null;
}

function writeCache(token) {
  try {
    fs.mkdirSync(CACHE_DIR, { recursive: true, mode: 0o700 });
    fs.writeFileSync(CACHE_FILE, JSON.stringify({
      token,
      expiresAt: Date.now() + TOKEN_TTL_MS,
      createdAt: new Date().toISOString(),
    }), { encoding: 'utf-8', mode: 0o600 });
  } catch (err) {
    console.warn('[auth] Could not write token cache:', err.message);
  }
}

// ---------------------------------------------------------------------------
// File-based API key storage
// ---------------------------------------------------------------------------

export function readApiKey() {
  try {
    const raw = fs.readFileSync(APIKEY_FILE, 'utf-8');
    const data = JSON.parse(raw);
    return data.apiKey || null;
  } catch {
    return null;
  }
}

export function writeApiKey(apiKey, agentId, agentName) {
  fs.mkdirSync(CACHE_DIR, { recursive: true, mode: 0o700 });
  fs.writeFileSync(APIKEY_FILE, JSON.stringify({
    apiKey,
    agentId,
    agentName,
    createdAt: new Date().toISOString(),
  }), { encoding: 'utf-8', mode: 0o600 });
}

// ---------------------------------------------------------------------------
// Auth API
// ---------------------------------------------------------------------------

/**
 * Exchange an API key for a JWT. Returns a cached token if still valid,
 * otherwise fetches a fresh one from the logic API.
 *
 * @param {string} apiKey - The agent API key (required)
 * @returns {Promise<string>} JWT token
 */
export async function getToken(apiKey) {
  // Try to use environment variable if apiKey not provided
  const key = apiKey || process.env.CLAWDRAW_API_KEY || readApiKey();

  // Check cache first (even without key)
  const cached = readCache();
  if (cached) {
    // Basic valid check
    try {
      const parts = cached.split('.');
      if (parts.length === 3) {
        const payload = JSON.parse(atob(parts[1]));
        if (payload.exp * 1000 > Date.now()) {
          return cached;
        }
      }
    } catch {}
  }

  if (!key) {
    throw new Error('No API key found. Run `clawdraw setup` to create an agent, or set CLAWDRAW_API_KEY.');
  }

  // Fetch fresh token
  const res = await fetch(`${LOGIC_URL}/api/agents/auth`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ apiKey: key }),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Agent auth failed (${res.status}): ${text}`);
  }

  const data = await res.json();
  writeCache(data.token);
  return data.token;
}

/**
 * Create a new agent account. Returns the full response body
 * including { apiKey, agentId, name }.
 *
 * @param {string} name - Agent display name
 * @returns {Promise<{ apiKey: string, agentId: string, name: string }>}
 */
export async function createAgent(name) {
  // Pass existing API key (if any) to bypass rate limits for linked admin accounts
  const existingKey = readApiKey();
  const payload = { name };
  if (existingKey) payload.existingApiKey = existingKey;

  const res = await fetch(`${LOGIC_URL}/api/agents`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Create agent failed (${res.status}): ${text}`);
  }

  return res.json();
}

/**
 * Fetch the authenticated agent's info.
 *
 * @param {string} token - JWT from getToken()
 * @returns {Promise<object>} Agent info from /api/agents/me
 */
export async function getAgentInfo(token) {
  const res = await fetch(`${LOGIC_URL}/api/agents/me`, {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Get agent info failed (${res.status}): ${text}`);
  }

  return res.json();
}
