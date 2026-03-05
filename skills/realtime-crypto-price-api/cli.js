#!/usr/bin/env node
/**
 * realtime-crypto-price-api CLI
 * Quick price lookups from the command line
 */

const { CryptoPrice } = require('./src/index.js');

const args = process.argv.slice(2);
const command = args[0];

async function main() {
  const client = new CryptoPrice();

  if (!command || command === 'help' || command === '--help') {
    console.log(`
realtime-crypto-price-api - Real-time cryptocurrency prices

Usage:
  crypto-price <symbol>              Get price for a single token
  crypto-price batch <sym1,sym2,...> Get multiple prices
  crypto-price top [limit]           Get top coins by market cap
  crypto-price trending [gainers|losers]  Get trending coins
  crypto-price search <query>        Search for tokens

Examples:
  crypto-price BTC
  crypto-price batch BTC,ETH,SOL
  crypto-price top 20
  crypto-price trending gainers
  crypto-price search pepe

Environment:
  PRISM_API_KEY - Your API key (optional for basic usage)
`);
    return;
  }

  try {
    if (command === 'batch') {
      const symbols = args[1]?.split(',') || ['BTC', 'ETH'];
      const prices = await client.getPrices(symbols);
      console.log(JSON.stringify(prices, null, 2));
    } 
    else if (command === 'top') {
      const limit = parseInt(args[1]) || 10;
      const top = await client.getTopCoins(limit);
      console.log(JSON.stringify(top, null, 2));
    }
    else if (command === 'trending') {
      const direction = args[1] || 'gainers';
      const trending = await client.getTrending(direction);
      console.log(JSON.stringify(trending, null, 2));
    }
    else if (command === 'search') {
      const query = args[1];
      if (!query) {
        console.error('Usage: crypto-price search <query>');
        process.exit(1);
      }
      const results = await client.search(query);
      console.log(JSON.stringify(results, null, 2));
    }
    else {
      // Single symbol lookup
      const price = await client.getPrice(command);
      console.log(`${price.symbol}: $${price.price.toLocaleString()}`);
      if (price.changePercent24h !== undefined) {
        const sign = price.changePercent24h >= 0 ? '+' : '';
        console.log(`24h: ${sign}${price.changePercent24h.toFixed(2)}%`);
      }
    }
  } catch (err) {
    console.error('Error:', err.message);
    process.exit(1);
  }
}

main();
