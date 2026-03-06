/**
 * IRONMAN — Pump.fun Direct API
 * 
 * New pump tokens directly trade via bonding curve
 * Jupiter doesn't route them until they graduate (~$69K mcap)
 * 
 * This module:
 * 1. Checks if token exists on pump.fun
 * 2. Gets token metadata + price
 * 3. Simulates buy via bonding curve math
 */

const axios = require('axios');
require('dotenv').config();

const HELIUS_URL = `https://mainnet.helius-rpc.com/?api-key=${process.env.HELIUS_API_KEY}`;

/**
 * Get pump.fun token info via Helius DAS API
 */
async function getPumpToken(mint) {
  try {
    const res = await axios.post(HELIUS_URL, {
      jsonrpc: '2.0', id: 1, method: 'getAsset', params: { id: mint }
    }, { timeout: 8000 });

    const d = res.data?.result;
    if (!d) return null;

    const meta = d.content?.metadata || {};
    const isPump = mint.endsWith('pump');

    return {
      mint,
      name: meta.name || 'Unknown',
      symbol: meta.symbol || '???',
      description: meta.description || '',
      marketCap: null,          // not in DAS
      virtualSolReserves: null, // not in DAS
      virtualTokenReserves: null,
      totalSupply: d.token_info?.supply,
      complete: !isPump,        // non-pump suffix = likely graduated
      createdAt: Date.now(),    // unknown from DAS
      twitter: null,
      website: null,
      creatorWallet: d.authorities?.[0]?.address,
      replies: 0,
      decimals: d.token_info?.decimals || 6,
      isPump,
    };
  } catch (e) {
    return null;
  }
}

/**
 * Bonding curve price calc
 * Returns tokens you get for X SOL
 */
function calcBuy(virtualSolReserves, virtualTokenReserves, solAmountLamports) {
  // Pump.fun uses constant product: x * y = k
  const sol = BigInt(Math.floor(virtualSolReserves));
  const tokens = BigInt(Math.floor(virtualTokenReserves));
  const solIn = BigInt(Math.floor(solAmountLamports));
  
  // tokens_out = tokens * sol_in / (sol + sol_in)
  const tokensOut = (tokens * solIn) / (sol + solIn);
  return Number(tokensOut);
}

/**
 * Get recent pump.fun launches
 * Sorted by creation time — freshest first
 */
async function getRecentLaunches(limit = 20) {
  try {
    const res = await axios.get(`${PUMP_API}/coins/latest`, {
      params: { offset: 0, limit, sort: 'creation_time', order: 'DESC', includeNsfw: false },
      timeout: 8000,
    });
    return res.data.map(d => ({
      mint: d.mint,
      name: d.name,
      symbol: d.symbol,
      marketCap: d.usd_market_cap,
      createdAt: d.created_timestamp,
      ageSeconds: Math.floor((Date.now() - d.created_timestamp) / 1000),
      replies: d.reply_count,
      complete: d.complete,
    }));
  } catch (e) {
    return [];
  }
}

/**
 * Get top trending pump tokens (by volume)
 */
async function getTrending(limit = 10) {
  try {
    const res = await axios.get(`${PUMP_API}/coins`, {
      params: { offset: 0, limit, sort: 'last_trade_timestamp', order: 'DESC', includeNsfw: false },
      timeout: 8000,
    });
    return res.data.map(d => ({
      mint: d.mint,
      name: d.name,
      symbol: d.symbol,
      marketCap: d.usd_market_cap,
      lastTrade: d.last_trade_timestamp,
      replies: d.reply_count,
      complete: d.complete,
    }));
  } catch (e) {
    return [];
  }
}

/**
 * Safety check for pump token
 * Returns score 0-100 (higher = safer)
 */
async function pumpSafetyCheck(mint) {
  const token = await getPumpToken(mint);
  if (!token) return { score: 0, pass: false, reasons: ['Token metadata not found'] };
  
  const reasons = [];
  let score = 50; // base score — token exists

  // Is it a pump.fun token? (ends in 'pump')
  if (token.isPump) {
    score += 10;
    reasons.push('Pump.fun token ✅');
  }

  // Has name/symbol?
  if (token.name && token.name !== 'Unknown') score += 10;
  if (token.symbol && token.symbol !== '???') score += 10;

  // Already graduated to Raydium?
  if (token.complete) {
    score += 20;
    reasons.push('Graduated to Raydium ✅');
  }

  return {
    score: Math.min(100, Math.max(0, score)),
    pass: score >= 40,
    token,
    reasons,
  };
}

module.exports = { getPumpToken, calcBuy, getRecentLaunches, getTrending, pumpSafetyCheck };
