#!/usr/bin/env node

/**
 * Portfolio Tracker CLI
 * Quick portfolio valuation from the command line
 */

const { PortfolioTracker, getPrice } = require('./src/index');

const args = process.argv.slice(2);

async function main() {
  if (args.length === 0 || args[0] === '--help' || args[0] === '-h') {
    console.log(`
Portfolio Tracker CLI - Powered by Strykr Prism API

Usage:
  portfolio price <symbol>              Get current price
  portfolio track <sym:amt> [sym:amt]   Track portfolio value

Examples:
  portfolio price BTC
  portfolio price ETH
  portfolio track BTC:1.5 ETH:10 SOL:100

Environment:
  PRISM_API_KEY    Optional API key for higher rate limits
`);
    return;
  }

  const command = args[0];

  if (command === 'price') {
    const symbol = args[1];
    if (!symbol) {
      console.error('Error: Please specify a symbol');
      process.exit(1);
    }
    
    try {
      const data = await getPrice(symbol);
      console.log(`${symbol.toUpperCase()}: $${data.price_usd?.toLocaleString() || 'N/A'}`);
      if (data.change_24h_pct !== undefined) {
        const change = data.change_24h_pct;
        console.log(`24h: ${change > 0 ? '+' : ''}${change.toFixed(2)}%`);
      }
    } catch (err) {
      console.error(`Error: ${err.message}`);
      process.exit(1);
    }
  }

  else if (command === 'track') {
    const holdings = args.slice(1);
    if (holdings.length === 0) {
      console.error('Error: Please specify holdings as SYMBOL:AMOUNT');
      process.exit(1);
    }

    const tracker = new PortfolioTracker();

    for (const holding of holdings) {
      const [symbol, amount] = holding.split(':');
      if (!symbol || !amount) {
        console.error(`Invalid format: ${holding}. Use SYMBOL:AMOUNT`);
        process.exit(1);
      }
      tracker.addHolding(symbol, parseFloat(amount));
    }

    try {
      const valuation = await tracker.getValuation();
      
      console.log('\n📊 Portfolio Valuation');
      console.log('─'.repeat(50));
      
      for (const item of valuation.holdings) {
        const change = item.change24h ? ` (${item.change24h > 0 ? '+' : ''}${item.change24h.toFixed(2)}%)` : '';
        console.log(`${item.symbol.padEnd(6)} ${item.amount.toString().padStart(12)} @ $${item.price.toLocaleString().padStart(10)} = $${item.value.toLocaleString().padStart(12)}${change}`);
        console.log(`       Allocation: ${item.allocation.toFixed(1)}%`);
      }
      
      console.log('─'.repeat(50));
      console.log(`Total Value: $${valuation.totalValue.toLocaleString()}`);
      console.log(`\nPowered by Strykr Prism API - https://prismapi.ai`);
    } catch (err) {
      console.error(`Error: ${err.message}`);
      process.exit(1);
    }
  }

  else {
    console.error(`Unknown command: ${command}`);
    process.exit(1);
  }
}

main();
