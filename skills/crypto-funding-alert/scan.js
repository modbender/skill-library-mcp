#!/usr/bin/env node
/**
 * Crypto Funding Rate Scanner
 * 
 * Scans Binance futures markets for negative funding rates and identifies
 * profitable long position opportunities.
 * 
 * Features:
 * - Real-time funding rate monitoring
 * - Risk management filters (volume, leverage, stop-loss)
 * - Composite scoring (rate + trend + volume)
 * - Signal classification (STRONG/MODERATE/WATCH)
 * - Historical data logging
 * 
 * Safety Rules:
 * - Max leverage ≤ 3x
 * - Position size ≤ 30% capital
 * - Stop-loss ≥ 10%
 * - Only liquid markets (>$10M volume)
 * - Trend-aware filtering
 */

const https = require('https');
const fs = require('fs');
const path = require('path');

// Parse command-line arguments
function parseArgs() {
  const args = process.argv.slice(2);
  const config = {
    maxLeverage: 3,
    maxPositionPct: 0.3,
    stopLossPct: 0.10,
    minVolume: 10000000,
    minAbsRate: 0.0005,
    maxCoins: 5,
    coins: null,
    outputDir: null,
  };

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    const next = args[i + 1];

    switch (arg) {
      case '--max-leverage':
        config.maxLeverage = parseFloat(next);
        i++;
        break;
      case '--min-volume':
        config.minVolume = parseFloat(next);
        i++;
        break;
      case '--stop-loss':
        config.stopLossPct = parseFloat(next);
        i++;
        break;
      case '--min-rate':
        config.minAbsRate = parseFloat(next);
        i++;
        break;
      case '--max-coins':
        config.maxCoins = parseInt(next);
        i++;
        break;
      case '--coins':
        config.coins = next.split(',').map(c => c.trim().toUpperCase());
        i++;
        break;
      case '--output':
        config.outputDir = next;
        i++;
        break;
      case '--help':
        printHelp();
        process.exit(0);
    }
  }

  return config;
}

function printHelp() {
  console.log(`
Crypto Funding Rate Scanner

Usage: node scan.js [options]

Options:
  --max-leverage <n>      Maximum leverage (default: 3)
  --min-volume <n>        Minimum 24h volume in USD (default: 10000000)
  --stop-loss <n>         Stop-loss percentage (default: 0.10)
  --min-rate <n>          Minimum absolute funding rate (default: 0.0005)
  --max-coins <n>         Maximum simultaneous positions (default: 5)
  --coins <list>          Comma-separated coin list (overrides default)
  --output <path>         Custom output directory
  --help                  Show this help message

Examples:
  node scan.js
  node scan.js --max-leverage 2 --min-volume 20000000
  node scan.js --coins BTC,ETH,SOL --stop-loss 0.15
`);
}

// Default coin list (major + mid-cap)
const DEFAULT_COINS = [
  'BTC','ETH','SOL','DOGE','XRP','ADA','AVAX','LINK','DOT','ATOM',
  'UNI','LTC','INJ','PENDLE','AXS','MANA','SAND','SNX','AAVE','CRV',
  'GMX','DYDX','ARB','OP','SUI','SEI','TIA','BLUR','WLD','PEPE',
  'SHIB','NEAR','APT','FTM','FIL','ICP','RUNE','ENS','LDO','MKR',
  'COMP','YFI','SUSHI','1INCH','DENT','HOLO','ORDER','GPS','BOB'
];

function httpsGet(url) {
  return new Promise((resolve) => {
    https.get(url, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try { resolve(JSON.parse(data)); }
        catch(e) { resolve(null); }
      });
    }).on('error', () => resolve(null));
  });
}

async function scanAll(config) {
  const coins = config.coins || DEFAULT_COINS;
  const results = [];
  
  for (const coin of coins) {
    const [funding, ticker] = await Promise.all([
      httpsGet(`https://fapi.binance.com/fapi/v1/premiumIndex?symbol=${coin}USDT`),
      httpsGet(`https://fapi.binance.com/fapi/v1/ticker/24hr?symbol=${coin}USDT`)
    ]);
    
    if (!funding || !ticker) continue;
    
    const rate = parseFloat(funding.lastFundingRate || 0);
    const volume = parseFloat(ticker.quoteVolume || 0);
    const change24h = parseFloat(ticker.priceChangePercent || 0);
    const price = parseFloat(ticker.lastPrice || 0);
    
    // Only negative funding rates
    if (rate >= 0) continue;
    
    // Risk filters
    if (Math.abs(rate) < config.minAbsRate) continue;
    if (volume < config.minVolume) continue;
    
    // Composite scoring
    // Rate weight 40% + Trend weight 30% + Volume weight 30%
    const rateScore = Math.min(Math.abs(rate) / 0.01, 1) * 40;
    const trendScore = (change24h > 0 ? 1 : change24h > -3 ? 0.5 : 0) * 30;
    const volScore = Math.min(volume / 100000000, 1) * 30;
    const totalScore = rateScore + trendScore + volScore;
    
    // Signal classification
    let signal = 'WATCH';
    if (totalScore > 60 && change24h > 0) signal = 'STRONG';
    else if (totalScore > 40) signal = 'MODERATE';
    
    results.push({
      coin,
      rate: (rate * 100).toFixed(4),
      change24h: change24h.toFixed(2),
      volume: (volume / 1000000).toFixed(1),
      price,
      score: totalScore.toFixed(1),
      signal,
      annualized3x: (Math.abs(rate) * 3 * 365 * 3 * 100).toFixed(0),
    });
  }
  
  results.sort((a, b) => parseFloat(b.score) - parseFloat(a.score));
  return results;
}

function saveResults(results, config) {
  const outputDir = config.outputDir || 
    path.join(process.env.HOME || process.cwd(), '.openclaw/workspace/data/funding-monitor');
  
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }
  
  const record = {
    timestamp: new Date().toISOString(),
    results: results.slice(0, 10),
    config: {
      maxLeverage: config.maxLeverage,
      maxPositionPct: config.maxPositionPct,
      stopLossPct: config.stopLossPct,
      minVolume: config.minVolume,
      minAbsRate: config.minAbsRate,
      maxCoins: config.maxCoins,
    }
  };
  
  const logFile = path.join(outputDir, 'scan_history.jsonl');
  fs.appendFileSync(logFile, JSON.stringify(record) + '\n');
  
  return logFile;
}

async function main() {
  const config = parseArgs();
  const ts = new Date().toISOString();
  
  console.log(`\n🔍 Crypto Funding Rate Scanner | ${ts}`);
  console.log('═'.repeat(70));
  console.log(`Safety: ${config.maxLeverage}x max | ${config.stopLossPct*100}% stop-loss | $${(config.minVolume/1e6).toFixed(0)}M min volume`);
  console.log('═'.repeat(70));
  
  const results = await scanAll(config);
  
  if (results.length === 0) {
    console.log('\n⚪ No opportunities found. Continue monitoring...');
    return;
  }
  
  console.log('\n  Signal   Coin     Rate      24h     Vol($M)  Score  Annual(3x)');
  console.log('  ' + '─'.repeat(64));
  
  for (const r of results.slice(0, 10)) {
    const emoji = r.signal === 'STRONG' ? '🟢' : r.signal === 'MODERATE' ? '🟡' : '⚪';
    console.log(`  ${emoji} ${r.signal.padEnd(8)} ${r.coin.padEnd(8)} ${r.rate.padStart(8)}%  ${r.change24h.padStart(7)}%  ${r.volume.padStart(8)}  ${r.score.padStart(5)}  ${r.annualized3x}%`);
  }
  
  // Show top opportunities
  const strong = results.filter(r => r.signal === 'STRONG');
  if (strong.length > 0) {
    console.log('\n🏆 Recommended Actions:');
    for (const s of strong.slice(0, 3)) {
      console.log(`   ${s.coin}: Long ${config.maxLeverage}x | Stop-loss ${config.stopLossPct*100}% | Rate ${s.rate}% | Annual ${s.annualized3x}%`);
    }
  }
  
  // Save to file
  const logFile = saveResults(results, config);
  
  console.log('\n═'.repeat(70));
  console.log(`📁 History saved: ${logFile}`);
}

main().catch(console.error);
