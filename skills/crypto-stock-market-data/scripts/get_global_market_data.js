#!/usr/bin/env node
const apiClient = require('./api_client');

async function getGlobalMarketData() {
  return apiClient.get('/crypto/global');
}

async function main() {
  const result = await getGlobalMarketData();
  console.log(JSON.stringify(result, null, 2));
}

main();
