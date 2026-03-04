#!/usr/bin/env node
const apiClient = require('./api_client');

async function getSupportedCurrencies() {
  return apiClient.get('/crypto/supported-currencies');
}

async function main() {
  const result = await getSupportedCurrencies();
  console.log(JSON.stringify(result, null, 2));
}

main();
