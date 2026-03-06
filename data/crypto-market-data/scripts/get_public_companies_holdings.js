#!/usr/bin/env node
const apiClient = require('./api_client');

async function getPublicCompaniesHoldings(coinId) {
  if (!['bitcoin', 'ethereum'].includes(coinId)) {
    return { error: "coin_id must be either 'bitcoin' or 'ethereum'" };
  }
  return apiClient.get('/crypto/companies/holdings', { coin_id: coinId });
}

async function main() {
  const args = process.argv.slice(2);
  if (args.length === 0) {
    console.log(JSON.stringify({
      usage: 'node scripts/get_public_companies_holdings.js <coin_id>',
      example: 'node scripts/get_public_companies_holdings.js bitcoin',
      note: "coin_id must be either 'bitcoin' or 'ethereum'",
    }, null, 2));
    process.exit(1);
  }

  const result = await getPublicCompaniesHoldings(args[0].toLowerCase());
  console.log(JSON.stringify(result, null, 2));
}

main();
