#!/usr/bin/env node
/**
 * Crypto Daily Dashboard
 * All-in-one crypto financial dashboard
 * 
 * Features:
 * - Binance account balances (spot, futures, unrealized PnL)
 * - Major crypto prices (BTC, ETH, SOL) with 24h change
 * - Fear & Greed Index (market sentiment)
 * - Top funding rates (negative rates = earn by going long)
 * - Economic tracking (balance, runway, income/expenses)
 * 
 * Configuration:
 * - BINANCE_API_KEY: Your Binance API key (optional, for balance)
 * - BINANCE_API_SECRET: Your Binance API secret (optional, for balance)
 * - ECONOMIC_TRACKER_PATH: Path to economic_tracker.py (optional)
 * 
 * Usage:
 *   node dashboard.js
 */

const https = require('https');
const crypto = require('crypto');

// ============================================================================
// Configuration
// ============================================================================

const CONFIG = {
  binance: {
    apiKey: process.env.BINANCE_API_KEY || '',
    apiSecret: process.env.BINANCE_API_SECRET || '',
    spotEndpoint: 'https://api.binance.com',
    futuresEndpoint: 'https://fapi.binance.com'
  },
  economicTracker: {
    enabled: process.env.ECONOMIC_TRACKER_PATH ? true : false,
    path: process.env.ECONOMIC_TRACKER_PATH || ''
  },
  timezone: process.env.TZ || 'Australia/Melbourne',
  locale: process.env.LANG || 'zh-CN'
};

// ============================================================================
// Utilities
// ============================================================================

function httpsGet(url, headers = {}) {
  return new Promise((resolve) => {
    https.get(url, { headers }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try { 
          resolve(JSON.parse(data)); 
        } catch(e) { 
          resolve(null); 
        }
      });
    }).on('error', (err) => {
      console.error(`HTTP GET error: ${err.message}`);
      resolve(null);
    });
  });
}

function binanceSignature(queryString, secret) {
  return crypto
    .createHmac('sha256', secret)
    .update(queryString)
    .digest('hex');
}

// ============================================================================
// Data Fetchers
// ============================================================================

async function getBinanceBalance() {
  if (!CONFIG.binance.apiKey || !CONFIG.binance.apiSecret) {
    return null;
  }

  try {
    const timestamp = Date.now();
    
    // Spot balance
    const spotQuery = `timestamp=${timestamp}`;
    const spotSig = binanceSignature(spotQuery, CONFIG.binance.apiSecret);
    const spotUrl = `${CONFIG.binance.spotEndpoint}/api/v3/account?${spotQuery}&signature=${spotSig}`;
    const spotData = await httpsGet(spotUrl, {
      'X-MBX-APIKEY': CONFIG.binance.apiKey
    });
    
    let spotTotal = 0;
    if (spotData && spotData.balances) {
      for (const bal of spotData.balances) {
        const free = parseFloat(bal.free);
        const locked = parseFloat(bal.locked);
        if (bal.asset === 'USDT') {
          spotTotal += free + locked;
        }
      }
    }
    
    // Futures balance
    const futuresQuery = `timestamp=${timestamp}`;
    const futuresSig = binanceSignature(futuresQuery, CONFIG.binance.apiSecret);
    const futuresUrl = `${CONFIG.binance.futuresEndpoint}/fapi/v2/account?${futuresQuery}&signature=${futuresSig}`;
    const futuresData = await httpsGet(futuresUrl, {
      'X-MBX-APIKEY': CONFIG.binance.apiKey
    });
    
    let futuresTotal = 0;
    let unrealizedPnl = 0;
    if (futuresData) {
      futuresTotal = parseFloat(futuresData.totalWalletBalance || 0);
      unrealizedPnl = parseFloat(futuresData.totalUnrealizedProfit || 0);
    }
    
    return {
      spot: spotTotal,
      futures: futuresTotal,
      total: spotTotal + futuresTotal,
      unrealizedPnl: unrealizedPnl
    };
  } catch(e) {
    console.error(`Binance balance error: ${e.message}`);
    return null;
  }
}

async function getCryptoPrices() {
  // Try CoinGecko first (free, no API key)
  const coins = ['bitcoin', 'ethereum', 'solana'];
  const cgUrl = `https://api.coingecko.com/api/v3/simple/price?ids=${coins.join(',')}&vs_currencies=usd&include_24hr_change=true`;
  const cg = await httpsGet(cgUrl);
  
  if (cg && cg.bitcoin && cg.bitcoin.usd) {
    return cg;
  }
  
  // Fallback: Binance public tickers
  const map = { 
    BTCUSDT: 'bitcoin', 
    ETHUSDT: 'ethereum', 
    SOLUSDT: 'solana' 
  };
  const result = {};
  
  for (const [symbol, name] of Object.entries(map)) {
    const url = `https://fapi.binance.com/fapi/v1/ticker/24hr?symbol=${symbol}`;
    const ticker = await httpsGet(url);
    if (ticker && ticker.lastPrice) {
      result[name] = {
        usd: parseFloat(ticker.lastPrice),
        usd_24h_change: parseFloat(ticker.priceChangePercent)
      };
    }
  }
  
  return Object.keys(result).length > 0 ? result : null;
}

async function getFearGreedIndex() {
  const url = 'https://api.alternative.me/fng/?limit=1';
  return await httpsGet(url);
}

async function getTopFundingRates() {
  const coins = ['BTC', 'ETH', 'SOL', 'DOGE', 'AXS', 'DENT', 'HOLO', 'INJ', 'PENDLE', 'ARB'];
  const results = [];
  
  for (const coin of coins) {
    const url = `https://fapi.binance.com/fapi/v1/premiumIndex?symbol=${coin}USDT`;
    const data = await httpsGet(url);
    if (data && data.lastFundingRate) {
      results.push({
        coin,
        rate: parseFloat(data.lastFundingRate)
      });
    }
  }
  
  // Sort by rate (lowest first) and return top 5
  return results.sort((a, b) => a.rate - b.rate).slice(0, 5);
}

async function getEconomicStatus() {
  if (!CONFIG.economicTracker.enabled) {
    return null;
  }
  
  try {
    const { execSync } = require('child_process');
    const output = execSync(`python3 ${CONFIG.economicTracker.path} status`, {
      timeout: 5000,
      encoding: 'utf8'
    });
    return JSON.parse(output);
  } catch(e) {
    console.error(`Economic tracker error: ${e.message}`);
    return null;
  }
}

// ============================================================================
// Display
// ============================================================================

function formatTimestamp() {
  return new Date().toLocaleString(CONFIG.locale, { 
    timeZone: CONFIG.timezone 
  });
}

async function displayDashboard() {
  const ts = formatTimestamp();
  
  console.log('');
  console.log('╔══════════════════════════════════════════════╗');
  console.log(`║       💰 Crypto Daily Dashboard | ${ts.padEnd(12)} ║`);
  console.log('╚══════════════════════════════════════════════╝');
  
  // 1. Binance Balance
  console.log('\n📊 Binance Account');
  console.log('─'.repeat(46));
  const balance = await getBinanceBalance();
  if (balance) {
    console.log(`  Spot:     $${balance.spot.toFixed(2)}`);
    console.log(`  Futures:  $${balance.futures.toFixed(2)}`);
    console.log(`  Total:    $${balance.total.toFixed(2)} USDT`);
    if (balance.unrealizedPnl !== 0) {
      const sign = balance.unrealizedPnl > 0 ? '+' : '';
      console.log(`  Unrealized PnL: ${sign}$${balance.unrealizedPnl.toFixed(2)}`);
    }
  } else {
    console.log('  ⚠️  Not configured (set BINANCE_API_KEY & BINANCE_API_SECRET)');
  }
  
  // 2. Crypto Prices
  console.log('\n📈 Major Cryptocurrencies');
  console.log('─'.repeat(46));
  const prices = await getCryptoPrices();
  if (prices) {
    for (const [coin, data] of Object.entries(prices)) {
      if (!data || !data.usd) continue;
      const change = data.usd_24h_change 
        ? `${data.usd_24h_change > 0 ? '+' : ''}${data.usd_24h_change.toFixed(1)}%` 
        : '';
      const price = data.usd.toLocaleString('en-US', { 
        minimumFractionDigits: 2, 
        maximumFractionDigits: 2 
      });
      console.log(`  ${coin.padEnd(10)} $${price.padStart(12)}  ${change}`);
    }
  } else {
    console.log('  ⚠️  Unable to fetch price data');
  }
  
  // 3. Fear & Greed Index
  console.log('\n🎭 Market Sentiment');
  console.log('─'.repeat(46));
  const fng = await getFearGreedIndex();
  if (fng && fng.data && fng.data[0]) {
    const val = parseInt(fng.data[0].value);
    const cls = fng.data[0].value_classification;
    const emoji = val < 25 ? '😱' : val < 45 ? '😰' : val < 55 ? '😐' : val < 75 ? '😊' : '🤑';
    console.log(`  ${emoji} ${cls}: ${val}/100`);
    if (val < 20) {
      console.log('  ⚠️  Extreme fear! Consider waiting before opening positions');
    }
  } else {
    console.log('  ⚠️  Unable to fetch sentiment data');
  }
  
  // 4. Funding Rates
  console.log('\n💸 Funding Rates (negative = earn by going long)');
  console.log('─'.repeat(46));
  const rates = await getTopFundingRates();
  const negativeRates = rates.filter(r => r.rate < 0);
  if (negativeRates.length > 0) {
    for (const r of negativeRates) {
      const annualized3x = (Math.abs(r.rate) * 3 * 365 * 3 * 100).toFixed(0);
      console.log(`  ${r.coin.padEnd(8)} ${(r.rate * 100).toFixed(4)}%  Annualized (3x): ${annualized3x}%`);
    }
  } else {
    console.log('  ⚪ No significant negative funding rates currently');
  }
  
  // 5. Economic Status
  console.log('\n🏦 Economic Status');
  console.log('─'.repeat(46));
  const econ = await getEconomicStatus();
  if (econ) {
    const emojiMap = { 
      thriving: '🟢', 
      stable: '🔵', 
      struggling: '🟡', 
      critical: '🔴', 
      bankrupt: '💀' 
    };
    console.log(`  ${emojiMap[econ.status] || '❓'} Status: ${econ.status.toUpperCase()}`);
    console.log(`  💰 Balance: $${econ.balance.toFixed(2)}`);
    console.log(`  📈 Total Income: $${econ.total_income.toFixed(2)}`);
    console.log(`  📉 Total Expenses: $${econ.total_cost.toFixed(2)}`);
    console.log(`  ⏳ Runway: ${econ.runway_days} days`);
  } else {
    console.log('  ⚠️  Not configured (set ECONOMIC_TRACKER_PATH)');
  }
  
  console.log('\n' + '═'.repeat(46));
  console.log('💡 Remember: Safety First | Compound Growth | Cut Losses');
  console.log('═'.repeat(46));
  console.log('');
}

// ============================================================================
// Main
// ============================================================================

if (require.main === module) {
  displayDashboard().catch(err => {
    console.error('Dashboard error:', err);
    process.exit(1);
  });
}

module.exports = { displayDashboard };
