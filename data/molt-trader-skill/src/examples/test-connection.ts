/**
 * Test Connection Example
 * 
 * Quick test to verify API connection and authentication
 */

import { MoltTraderClient } from '../client';
import { AuthenticationError } from '../errors';

async function testConnection() {
  console.log('🧪 Molt Trader SDK - Connection Test\n');

  const apiKey = process.env.MOLT_TRADER_API_KEY;
  if (!apiKey) {
    console.error('❌ Error: MOLT_TRADER_API_KEY environment variable not set');
    console.log('   Set it with: export MOLT_TRADER_API_KEY=your-api-key');
    process.exit(1);
  }

  const client = new MoltTraderClient({
    apiKey,
    baseUrl: process.env.MOLT_TRADER_BASE_URL || 'http://localhost:3000',
    logLevel: 'info',
  });

  try {
    // Test 1: Fetch portfolio
    console.log('📊 Fetching portfolio...');
    const portfolio = await client.getPortfolioMetrics();
    console.log(`   ✓ Balance: $${portfolio.balance.toFixed(0)}`);
    console.log(`   ✓ ROI: ${portfolio.roi.toFixed(2)}%`);
    console.log(`   ✓ Total Trades: ${portfolio.totalTrades}`);
    console.log(`   ✓ Win Rate: ${portfolio.winRate.toFixed(2)}%\n`);

    // Test 2: Fetch positions
    console.log('📈 Fetching open positions...');
    const positions = await client.getPositions();
    console.log(`   ✓ Open positions: ${positions.length}`);
    positions.slice(0, 3).forEach((p) => {
      console.log(`     - ${p.symbol}: ${p.type} ${p.shares}sh @ $${p.entryPrice}`);
    });
    if (positions.length > 3) {
      console.log(`     ... and ${positions.length - 3} more`);
    }
    console.log();

    // Test 3: Fetch leaderboard
    console.log('🏆 Fetching leaderboard...');
    const leaderboard = await client.getLeaderboard('weekly');
    console.log(`   ✓ Period: ${leaderboard.period}`);
    console.log(`   ✓ Top 5 traders:`);
    leaderboard.rankings.slice(0, 5).forEach((r) => {
      console.log(
        `     ${r.rank}. ${r.displayName}: ${r.roi.toFixed(2)}% ROI ($${r.totalProfit.toFixed(0)})`
      );
    });
    console.log();

    console.log('✅ All tests passed! Your SDK is configured correctly.\n');
    console.log('📚 Next steps:');
    console.log('   1. See examples/ for trading strategy templates');
    console.log('   2. Read SKILL.md for full API documentation');
    console.log('   3. Start building your trading bot!\n');
  } catch (error) {
    if (error instanceof AuthenticationError) {
      console.error('❌ Authentication failed. Check your API key.');
    } else {
      console.error(`❌ Test failed: ${error}`);
    }
    process.exit(1);
  }
}

testConnection();
