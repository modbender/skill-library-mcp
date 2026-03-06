#!/usr/bin/env node

/**
 * Polymarket User Analyzer
 * Analyzes trading strategies and patterns from Polymarket users
 */

const args = process.argv.slice(2);

if (args.length === 0 || args.includes('--help')) {
  console.log(`
Polymarket User Analyzer

Usage:
  node analyze_user.js <username|address> [options]

Arguments:
  username|address    Polymarket username (@username) or wallet address (0x...)

Options:
  --limit <n>        Number of trades to fetch (default: 100)
  --output <file>    Save detailed JSON report to file
  --quiet            Only show summary, no detailed breakdown
  --help             Show this help message

Examples:
  node analyze_user.js @vague-sourdough
  node analyze_user.js 0x8c74b4eef9a894433B8126aA11d1345efb2B0488
  node analyze_user.js @username --limit 200 --output report.json
`);
  process.exit(0);
}

const input = args[0];
const limit = args.includes('--limit') ? parseInt(args[args.indexOf('--limit') + 1]) : 100;
const outputFile = args.includes('--output') ? args[args.indexOf('--output') + 1] : null;
const quiet = args.includes('--quiet');

// Extract wallet address from username
async function getWalletAddress(username) {
  const cleanUsername = username.replace('@', '');
  
  try {
    const response = await fetch(`https://polymarket.com/@${cleanUsername}`);
    const html = await response.text();
    
    const addressMatch = html.match(/0x[a-fA-F0-9]{40}/);
    if (addressMatch) {
      return addressMatch[0];
    }
    
    throw new Error('Wallet address not found in profile page');
  } catch (error) {
    throw new Error(`Failed to fetch wallet address: ${error.message}`);
  }
}

// Fetch trading history
async function fetchTradingHistory(address, limit) {
  try {
    const response = await fetch(
      `https://data-api.polymarket.com/activity?user=${address}&limit=${limit}`
    );
    
    if (!response.ok) {
      throw new Error(`API returned ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    throw new Error(`Failed to fetch trading history: ${error.message}`);
  }
}

// Analyze trading patterns
function analyzeTrades(trades) {
  const realTrades = trades.filter(t => t.type === 'TRADE');
  const redeems = trades.filter(t => t.type === 'REDEEM');
  
  if (realTrades.length === 0) {
    return { error: 'No trades found for this user' };
  }
  
  // Basic stats
  const totalTrades = realTrades.length;
  const totalInvested = realTrades.reduce((sum, t) => sum + t.usdcSize, 0);
  const avgPosition = totalInvested / totalTrades;
  
  // Market type analysis
  const markets = {};
  const assets = {};
  realTrades.forEach(t => {
    // Extract asset from title (BTC, ETH, SOL, etc.)
    const words = t.title.split(' ');
    const asset = words[0];
    assets[asset] = (assets[asset] || 0) + 1;
    
    // Market type
    if (t.title.includes('Up or Down')) {
      markets['Short-term Crypto'] = (markets['Short-term Crypto'] || 0) + 1;
    } else if (t.title.toLowerCase().includes('election') || t.title.toLowerCase().includes('president')) {
      markets['Politics'] = (markets['Politics'] || 0) + 1;
    } else if (t.title.toLowerCase().includes('nfl') || t.title.toLowerCase().includes('nba')) {
      markets['Sports'] = (markets['Sports'] || 0) + 1;
    } else {
      markets['Other'] = (markets['Other'] || 0) + 1;
    }
  });
  
  // Direction analysis
  const directions = {};
  realTrades.forEach(t => {
    if (t.outcome) {
      directions[t.outcome] = (directions[t.outcome] || 0) + 1;
    }
  });
  
  // Entry price analysis
  const prices = realTrades.map(t => t.price);
  const avgPrice = prices.reduce((a, b) => a + b, 0) / prices.length;
  const priceRanges = {
    'Very Low (0-0.2)': prices.filter(p => p < 0.2).length,
    'Low (0.2-0.4)': prices.filter(p => p >= 0.2 && p < 0.4).length,
    'Medium (0.4-0.6)': prices.filter(p => p >= 0.4 && p < 0.6).length,
    'High (0.6-0.8)': prices.filter(p => p >= 0.6 && p < 0.8).length,
    'Very High (0.8-1.0)': prices.filter(p => p >= 0.8).length
  };
  
  // Position sizing analysis
  const positions = realTrades.map(t => t.usdcSize);
  const minPosition = Math.min(...positions);
  const maxPosition = Math.max(...positions);
  const positionVariance = positions.reduce((sum, p) => sum + Math.pow(p - avgPosition, 2), 0) / positions.length;
  const isFixedSize = positionVariance < 0.1; // Low variance = fixed sizing
  
  // Time analysis
  const timestamps = realTrades.map(t => new Date(t.timestamp * 1000));
  const hours = timestamps.map(t => t.getHours());
  const hourDist = {};
  hours.forEach(h => hourDist[h] = (hourDist[h] || 0) + 1);
  const topHours = Object.entries(hourDist)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 3)
    .map(([h, c]) => ({ hour: parseInt(h), count: c }));
  
  // P&L analysis
  const totalRedeemed = redeems.reduce((sum, t) => sum + t.usdcSize, 0);
  const netPnL = totalRedeemed - totalInvested;
  const roi = totalInvested > 0 ? (netPnL / totalInvested) * 100 : 0;
  
  // Strategy classification
  let strategyType = 'Unknown';
  if (avgPrice < 0.4) {
    strategyType = 'Value Investor (buys underpriced outcomes)';
  } else if (avgPrice > 0.6) {
    strategyType = 'Momentum Trader (follows market trends)';
  } else if (isFixedSize && totalTrades > 20) {
    strategyType = 'Systematic Scalper (fixed size, high frequency)';
  } else if (maxPosition > avgPosition * 3) {
    strategyType = 'Conviction Trader (variable sizing)';
  } else {
    strategyType = 'Balanced Trader (neutral approach)';
  }
  
  return {
    summary: {
      totalTrades,
      totalInvested,
      avgPosition,
      minPosition,
      maxPosition,
      isFixedSize,
      strategyType
    },
    markets,
    assets,
    directions,
    priceAnalysis: {
      avgPrice,
      ranges: priceRanges
    },
    timePatterns: {
      topHours
    },
    performance: {
      totalRedeemed,
      netPnL,
      roi
    },
    rawTrades: realTrades
  };
}

// Format report
function formatReport(username, address, analysis) {
  const { summary, markets, assets, directions, priceAnalysis, timePatterns, performance } = analysis;
  
  console.log('\n' + '='.repeat(70));
  console.log(`📊 Polymarket Strategy Analysis: ${username}`);
  console.log('='.repeat(70));
  
  console.log('\n【Overview】');
  console.log(`Wallet: ${address}`);
  console.log(`Total Trades: ${summary.totalTrades}`);
  console.log(`Capital Deployed: $${summary.totalInvested.toFixed(2)}`);
  console.log(`Average Position: $${summary.avgPosition.toFixed(2)}`);
  console.log(`Position Range: $${summary.minPosition.toFixed(2)} - $${summary.maxPosition.toFixed(2)}`);
  console.log(`Position Sizing: ${summary.isFixedSize ? 'Fixed' : 'Dynamic'}`);
  
  console.log('\n【Strategy Classification】');
  console.log(`Type: ${summary.strategyType}`);
  
  console.log('\n【Market Focus】');
  Object.entries(markets)
    .sort((a, b) => b[1] - a[1])
    .forEach(([market, count]) => {
      const pct = (count / summary.totalTrades * 100).toFixed(1);
      console.log(`  ${market}: ${count} trades (${pct}%)`);
    });
  
  console.log('\n【Asset Distribution】');
  Object.entries(assets)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)
    .forEach(([asset, count]) => {
      const pct = (count / summary.totalTrades * 100).toFixed(1);
      console.log(`  ${asset}: ${count} trades (${pct}%)`);
    });
  
  if (Object.keys(directions).length > 0) {
    console.log('\n【Direction Bias】');
    Object.entries(directions)
      .sort((a, b) => b[1] - a[1])
      .forEach(([dir, count]) => {
        const pct = (count / summary.totalTrades * 100).toFixed(1);
        console.log(`  ${dir}: ${count} trades (${pct}%)`);
      });
  }
  
  console.log('\n【Entry Price Analysis】');
  console.log(`Average Entry: ${priceAnalysis.avgPrice.toFixed(3)}`);
  console.log('Price Distribution:');
  Object.entries(priceAnalysis.ranges).forEach(([range, count]) => {
    if (count > 0) {
      const pct = (count / summary.totalTrades * 100).toFixed(1);
      console.log(`  ${range}: ${count} trades (${pct}%)`);
    }
  });
  
  console.log('\n【Trading Hours (UTC)】');
  timePatterns.topHours.forEach(({ hour, count }) => {
    console.log(`  ${hour}:00 - ${count} trades`);
  });
  
  console.log('\n【Performance】');
  console.log(`Total Invested: $${performance.totalRedeemed > 0 ? summary.totalInvested.toFixed(2) : 'N/A'}`);
  console.log(`Total Redeemed: $${performance.totalRedeemed.toFixed(2)}`);
  console.log(`Net P&L: $${performance.netPnL.toFixed(2)}`);
  console.log(`ROI: ${performance.roi.toFixed(2)}%`);
  
  console.log('\n' + '='.repeat(70));
  console.log('Note: Analysis based on publicly available on-chain data');
  console.log('='.repeat(70) + '\n');
}

// Main execution
(async () => {
  try {
    console.log('🔍 Analyzing Polymarket user...\n');
    
    // Determine if input is username or address
    let address;
    let username;
    
    if (input.startsWith('0x')) {
      address = input;
      username = address.slice(0, 10) + '...';
      console.log(`Using wallet address: ${address}`);
    } else {
      username = input;
      console.log(`Fetching wallet address for ${username}...`);
      address = await getWalletAddress(username);
      console.log(`Found address: ${address}`);
    }
    
    // Fetch trading history
    console.log(`\nFetching trading history (limit: ${limit})...`);
    const trades = await fetchTradingHistory(address, limit);
    console.log(`Retrieved ${trades.length} activities`);
    
    // Analyze
    console.log('\nAnalyzing trading patterns...');
    const analysis = analyzeTrades(trades);
    
    if (analysis.error) {
      console.error(`\n❌ ${analysis.error}`);
      process.exit(1);
    }
    
    // Output
    if (!quiet) {
      formatReport(username, address, analysis);
    }
    
    // Save to file if requested
    if (outputFile) {
      const fs = await import('fs');
      const output = {
        username,
        address,
        analyzedAt: new Date().toISOString(),
        analysis
      };
      fs.writeFileSync(outputFile, JSON.stringify(output, null, 2));
      console.log(`\n💾 Detailed report saved to: ${outputFile}`);
    }
    
  } catch (error) {
    console.error(`\n❌ Error: ${error.message}`);
    process.exit(1);
  }
})();
