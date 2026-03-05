#!/usr/bin/env node
/**
 * Create Account script for Consortium AI skill.
 * Usage:
 *   node create-account.js <WALLET_ADDRESS>
 * Requires: TRADING_ANALYSIS_API_KEY
 */

const baseUrl = 'https://api.consortiumai.org';
const apiKey = process.env.TRADING_ANALYSIS_API_KEY;

if (!apiKey) {
  console.error(JSON.stringify({ success: false, message: 'TRADING_ANALYSIS_API_KEY is not set' }));
  process.exit(1);
}

const walletAddress = process.argv[2] ? String(process.argv[2]).trim() : null;

if (!walletAddress) {
  console.error(JSON.stringify({ error: 'Missing walletAddress' }));
  process.exit(1);
}

const url = `${baseUrl}/api/custodial-wallet/create-with-api-key`;

let res;
try {
  res = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': apiKey,
    },
    body: JSON.stringify({ walletAddress }),
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

if (!res.ok) {
  // Pass through the error response from API
  console.error(JSON.stringify(body));
  process.exit(1);
}

// Success (201)
console.log(JSON.stringify(body));
