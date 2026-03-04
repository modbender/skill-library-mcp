/**
 * Basic usage example for @strykr/portfolio-tracker
 */

const { PortfolioTracker, getPrice, getPrices } = require('../src/index');

async function main() {
  console.log('=== Portfolio Tracker Demo ===\n');

  // 1. Single price lookup
  console.log('1. Single Price Lookup');
  console.log('-'.repeat(30));
  try {
    const btc = await getPrice('BTC');
    console.log('BTC:', btc);
  } catch (err) {
    console.log('BTC price lookup:', err.message);
  }

  // 2. Batch price lookup
  console.log('\n2. Batch Price Lookup');
  console.log('-'.repeat(30));
  try {
    const prices = await getPrices(['BTC', 'ETH', 'SOL']);
    console.log('Prices:', JSON.stringify(prices, null, 2));
  } catch (err) {
    console.log('Batch lookup:', err.message);
  }

  // 3. Portfolio tracking
  console.log('\n3. Portfolio Tracking');
  console.log('-'.repeat(30));
  
  const portfolio = new PortfolioTracker();
  portfolio
    .addHolding('BTC', 1.5, 45000)
    .addHolding('ETH', 10, 2500)
    .addHolding('SOL', 100, 80);

  console.log('Holdings:', portfolio.toJSON());

  try {
    const valuation = await portfolio.getValuation();
    console.log('\nValuation:');
    console.log(`  Total Value: $${valuation.totalValue.toLocaleString()}`);
    console.log(`  Total Cost:  $${valuation.totalCost?.toLocaleString() || 'N/A'}`);
    console.log(`  Total P&L:   $${valuation.totalPnl?.toLocaleString() || 'N/A'}`);
    console.log(`  P&L %:       ${valuation.totalPnlPercent?.toFixed(2) || 'N/A'}%`);
    
    console.log('\nBreakdown:');
    for (const h of valuation.holdings) {
      console.log(`  ${h.symbol}: ${h.amount} @ $${h.price} = $${h.value.toLocaleString()} (${h.allocation.toFixed(1)}%)`);
    }
  } catch (err) {
    console.log('Valuation error:', err.message);
  }

  console.log('\n✅ Demo complete');
}

main().catch(console.error);
