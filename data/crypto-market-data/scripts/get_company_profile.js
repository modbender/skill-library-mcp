#!/usr/bin/env node
const apiClient = require('./api_client');

async function getCompanyProfile(symbol) {
  return apiClient.get('/stock/profile', { symbol: symbol.toUpperCase() });
}

async function main() {
  const args = process.argv.slice(2);
  if (args.length === 0) {
    console.log(JSON.stringify({
      usage: 'node scripts/get_company_profile.js <SYMBOL>',
      example: 'node scripts/get_company_profile.js AAPL',
    }, null, 2));
    process.exit(1);
  }

  const result = await getCompanyProfile(args[0]);
  console.log(JSON.stringify(result, null, 2));
}

main();
