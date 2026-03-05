/**
 * Basic usage examples for realtime-crypto-price-api
 */

const { CryptoPrice } = require('../src/index.js');

async function main() {
  const client = new CryptoPrice();

  console.log('=== Single Price ===');
  const btc = await client.getPrice('BTC');
  console.log(`Bitcoin: $${btc.price.toLocaleString()}`);
  
  console.log('\n=== Multiple Prices ===');
  const prices = await client.getPrices(['BTC', 'ETH', 'SOL', 'DOGE']);
  Object.entries(prices).forEach(([symbol, data]) => {
    console.log(`${symbol}: $${data.price.toLocaleString()}`);
  });

  console.log('\n=== Top 5 Coins ===');
  const top5 = await client.getTopCoins(5);
  top5.forEach((coin, i) => {
    console.log(`${i + 1}. ${coin.symbol}: $${coin.price.toLocaleString()}`);
  });

  console.log('\n=== Top Gainers ===');
  const gainers = await client.getTrending('gainers', 5);
  gainers.forEach(coin => {
    console.log(`${coin.symbol}: +${coin.change24h.toFixed(2)}%`);
  });
}

main().catch(console.error);
