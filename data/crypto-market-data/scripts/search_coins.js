#!/usr/bin/env node
const apiClient = require('./api_client');

async function searchCoins(query) {
  return apiClient.get('/crypto/search', { query });
}

async function main() {
  const args = process.argv.slice(2);
  if (args.length === 0) {
    console.log(JSON.stringify({
      usage: 'node scripts/search_coins.js <query>',
      example: 'node scripts/search_coins.js bitcoin',
    }, null, 2));
    process.exit(1);
  }

  const query = args.join(' ');
  const result = await searchCoins(query);
  console.log(JSON.stringify(result, null, 2));
}

main();
