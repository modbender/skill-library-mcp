#!/usr/bin/env node
/**
 * x402 Fetch Proxy — Makes x402-paid API calls using a Solana wallet
 * 
 * Usage:
 *   node x402-fetch.js <endpoint> [payload_json]
 * 
 * Examples:
 *   node x402-fetch.js /image/creative-director '{"idea":"trending Solana design"}'
 *   node x402-fetch.js /token/pumpfun-trending
 *   node x402-fetch.js /image/grok-imagine '{"prompt":"a glowing Solana logo"}'
 * 
 * Env vars required:
 *   XONA_WALLET_SECRET  — Solana private key (base58)
 *   XONA_API_BASE       — API base URL (default: https://api.xona-agent.com)
 */

const { wrapFetch } = require('@dexterai/x402/client');

const API_BASE = process.env.XONA_API_BASE || 'https://api.xona-agent.com';

async function main() {
  const endpoint = process.argv[2];
  const payloadArg = process.argv[3];

  if (!endpoint) {
    console.error(JSON.stringify({
      success: false,
      error: 'Usage: node x402-fetch.js <endpoint> [payload_json]'
    }));
    process.exit(1);
  }

  const walletSecret = process.env.XONA_WALLET_SECRET;
  if (!walletSecret) {
    console.error(JSON.stringify({
      success: false,
      error: 'XONA_WALLET_SECRET env var is required'
    }));
    process.exit(1);
  }

  const x402Fetch = wrapFetch(fetch, { walletPrivateKey: walletSecret });

  const url = endpoint.startsWith('http') ? endpoint : `${API_BASE}${endpoint}`;
  const hasPayload = payloadArg && payloadArg.trim().length > 0;
  const method = hasPayload ? 'POST' : 'GET';

  const fetchOptions = {
    method,
    headers: { 'Content-Type': 'application/json' }
  };

  if (hasPayload) {
    fetchOptions.body = payloadArg;
  }

  try {
    const response = await x402Fetch(url, fetchOptions);
    const data = await response.json();

    if (!response.ok) {
      console.log(JSON.stringify({
        success: false,
        status: response.status,
        error: data.error || data.message || `Request failed with status ${response.status}`,
        data
      }));
      process.exit(1);
    }

    console.log(JSON.stringify(data, null, 2));
  } catch (error) {
    console.error(JSON.stringify({
      success: false,
      error: error.message
    }));
    process.exit(1);
  }
}

main();
