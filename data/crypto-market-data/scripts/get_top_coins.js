#!/usr/bin/env node
const apiClient = require('./api_client');

async function getTopCoins(vsCurrency = 'usd', perPage = 10, page = 1, order = 'market_cap_desc') {
  const params = {
    vs_currency: vsCurrency,
    per_page: String(perPage),
    page: String(page),
    order,
  };
  return apiClient.get('/crypto/coins/markets', params);
}

async function main() {
  let vsCurrency = 'usd';
  let perPage = 10;
  let page = 1;
  let order = 'market_cap_desc';

  for (const arg of process.argv.slice(2)) {
    if (arg.startsWith('--currency=')) vsCurrency = arg.split('=')[1];
    else if (arg.startsWith('--per_page=')) perPage = parseInt(arg.split('=')[1], 10);
    else if (arg.startsWith('--page=')) page = parseInt(arg.split('=')[1], 10);
    else if (arg.startsWith('--order=')) order = arg.split('=')[1];
  }

  const result = await getTopCoins(vsCurrency, perPage, page, order);
  console.log(JSON.stringify(result, null, 2));
}

main();
