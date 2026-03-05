#!/usr/bin/env node
/**
 * Trading Analysis API client for Consortium AI skill.
 * Usage:
 *   node trading-analysis.js           → latest analysis (any pair)
 *   node trading-analysis.js SOL       → latest analysis for token SOL
 * Requires: TRADING_ANALYSIS_API_KEY
 */

const baseUrl = 'https://api.consortiumai.org';
const apiKey = process.env.TRADING_ANALYSIS_API_KEY;

if (!apiKey) {
  console.error(JSON.stringify({ success: false, message: 'TRADING_ANALYSIS_API_KEY is not set' }));
  process.exit(1);
}

const token = process.argv[2] ? String(process.argv[2]).trim().toUpperCase() : null;
const url = token
  ? `${baseUrl}/api/trading-analysis?token=${encodeURIComponent(token)}`
  : `${baseUrl}/api/trading-analysis`;

let res;
try {
  res = await fetch(url, {
    method: 'GET',
    headers: {
      'x-api-key': apiKey,
      'Accept': 'application/json',
    },
  });
} catch (err) {
  console.error(JSON.stringify({ success: false, message: 'Request failed', error: err.message }));
  process.exit(1);
}

const text = await res.text();
let body;
try {
  body = text ? JSON.parse(text) : {};
} catch {
  console.error(JSON.stringify({ success: false, message: 'Invalid JSON response', status: res.status }));
  process.exit(1);
}

if (res.status === 401) {
  console.error(JSON.stringify(body));
  process.exit(1);
}
if (res.status === 404) {
  console.error(JSON.stringify(body.data || body));
  process.exit(1);
}
if (res.status >= 500) {
  console.error(JSON.stringify(body.data || body));
  process.exit(1);
}
if (!res.ok) {
  console.error(JSON.stringify(body.data || body || { success: false, message: 'Unknown error' }));
  process.exit(1);
}

// Success: output full response for the agent to use
console.log(JSON.stringify(body));
