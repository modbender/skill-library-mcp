#!/usr/bin/env node
const apiClient = require('./api_client');

async function getCoinDetails(coinId) {
  return apiClient.get(`/crypto/coins/${coinId}`);
}

async function main() {
  const args = process.argv.slice(2);
  if (args.length === 0) {
    console.log(JSON.stringify({
      usage: 'node scripts/get_coin_details.js <coin_id>',
      example: 'node scripts/get_coin_details.js bitcoin',
    }, null, 2));
    process.exit(1);
  }

  const result = await getCoinDetails(args[0]);
  console.log(JSON.stringify(result, null, 2));
}

main();
