#!/usr/bin/env node
const apiClient = require('./api_client');

async function getTrendingCoins() {
  return apiClient.get('/crypto/search/trending');
}

async function main() {
  const result = await getTrendingCoins();
  console.log(JSON.stringify(result, null, 2));
}

main();
