#!/usr/bin/env node
const https = require('https');
const http = require('http');
const fs = require('fs');
const path = require('path');
const url = require('url');

const BASE_URL = process.env.API_BASE_URL || 'https://api.igent.net/api';
const TOKEN_FILE = path.join(__dirname, '.token');
const USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36';

function _loadToken() {
  if (!fs.existsSync(TOKEN_FILE)) return null;

  try {
    const data = JSON.parse(fs.readFileSync(TOKEN_FILE, 'utf-8'));
    const expiresAtStr = data.expires_at;
    if (!expiresAtStr) return null;

    const expiresAt = new Date(expiresAtStr);
    if (Date.now() >= expiresAt.getTime()) return null;

    return data.token || null;
  } catch (e) {
    console.error(`Warning: Failed to load token file: ${e.message}`);
    return null;
  }
}

function _httpRequest(reqUrl, headers = {}) {
  return new Promise((resolve, reject) => {
    const parsed = new URL(reqUrl);
    const mod = parsed.protocol === 'https:' ? https : http;
    const options = {
      hostname: parsed.hostname,
      port: parsed.port,
      path: parsed.pathname + parsed.search,
      method: 'GET',
      headers: { 'User-Agent': USER_AGENT, ...headers },
    };

    const req = mod.request(options, (res) => {
      let body = '';
      res.on('data', (chunk) => (body += chunk));
      res.on('end', () => resolve({ status: res.statusCode, body }));
    });
    req.on('error', reject);
    req.end();
  });
}

async function _fetchNewToken() {
  const reqUrl = `${BASE_URL}/token`;
  const { status, body } = await _httpRequest(reqUrl);

  if (status === 200) {
    const data = JSON.parse(body);
    fs.writeFileSync(TOKEN_FILE, JSON.stringify(data));
    return data.token;
  }
  throw new Error(`Failed to fetch token. Status: ${status}`);
}

async function getToken() {
  const token = _loadToken();
  if (token) return token;
  return _fetchNewToken();
}

async function get(endpoint, params) {
  let token;
  try {
    token = await getToken();
  } catch (e) {
    return { error: e.message };
  }

  const parsed = new URL(`${BASE_URL}${endpoint}`);
  if (params) {
    for (const [key, value] of Object.entries(params)) {
      parsed.searchParams.set(key, value);
    }
  }

  const headers = {
    accept: 'application/json',
    'X-API-Token': token,
  };

  try {
    const { status, body } = await _httpRequest(parsed.toString(), headers);
    if (status === 200) {
      return JSON.parse(body);
    }
    try {
      const errorJson = JSON.parse(body);
      return { error: `HTTP Error ${status}: ${errorJson.error || 'Unknown'}` };
    } catch {
      return { error: `HTTP Error ${status}` };
    }
  } catch (e) {
    return { error: `Request error: ${e.message}` };
  }
}

module.exports = { get, getToken };
