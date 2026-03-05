#!/usr/bin/env node
const apiClient = require('./api_client');

async function getCryptoPrice(coinIds, currency = 'usd') {
  const params = {
    ids: coinIds.join(','),
    vs_currencies: currency,
    include_market_cap: 'true',
    include_24hr_vol: 'true',
    include_24hr_change: 'true',
    include_last_updated_at: 'true',
  };
  return apiClient.get('/crypto/prices', params);
}

async function main() {
  const args = process.argv.slice(2);
  if (args.length === 0) {
    console.log(JSON.stringify({
      usage: 'node scripts/get_crypto_price.js <coin_id_1> [coin_id_2] ... [--currency=usd]',
      example: 'node scripts/get_crypto_price.js bitcoin ethereum --currency=usd',
    }, null, 2));
    process.exit(1);
  }

  let currency = 'usd';
  const coinIds = [];
  for (const arg of args) {
    if (arg.startsWith('--currency=')) {
      currency = arg.split('=')[1];
    } else {
      coinIds.push(arg);
    }
  }
  if (coinIds.length === 0) coinIds.push('bitcoin');

  const result = await getCryptoPrice(coinIds, currency);
  console.log(JSON.stringify(result, null, 2));
}

main();
