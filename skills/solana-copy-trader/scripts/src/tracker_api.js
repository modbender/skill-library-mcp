/**
 * IRONMAN — Solana Tracker API
 * Free tier: 100 req/min
 * Better data than raw RPC for wallet tracking
 */

const axios = require('axios');

const BASE = 'https://data.solanatracker.io';
// Free API - no key needed for basic endpoints
const HEADERS = { 'x-api-key': 'free' };

const WHALE = 'AgmLJBMDCqWynYnQiPCuj9ewsNNsBJXyzoUhD9LJzN51';

async function getWalletTrades(wallet, limit = 20) {
  try {
    const r = await axios.get(`${BASE}/wallet/${wallet}/trades`, {
      params: { limit },
      timeout: 10000,
    });
    return r.data;
  } catch (e) {
    return null;
  }
}

async function getWalletTokens(wallet) {
  try {
    const r = await axios.get(`${BASE}/wallet/${wallet}`, {
      timeout: 10000,
    });
    return r.data;
  } catch (e) {
    return null;
  }
}

async function getTokenInfo(mint) {
  try {
    const r = await axios.get(`${BASE}/tokens/${mint}`, {
      timeout: 8000,
    });
    return r.data;
  } catch (e) {
    return null;
  }
}

async function analyzeWhaleNow() {
  console.log('\n=== LIVE WHALE ANALYSIS ===');
  console.log(`Wallet: ${WHALE}\n`);

  // Get recent trades
  const trades = await getWalletTrades(WHALE, 10);
  if (trades) {
    console.log(`Recent trades: ${JSON.stringify(trades).slice(0, 500)}`);
  }

  // Get holdings
  const holdings = await getWalletTokens(WHALE);
  if (holdings) {
    console.log(`Holdings: ${JSON.stringify(holdings).slice(0, 500)}`);
  }
}

module.exports = { getWalletTrades, getWalletTokens, getTokenInfo, analyzeWhaleNow, WHALE };
