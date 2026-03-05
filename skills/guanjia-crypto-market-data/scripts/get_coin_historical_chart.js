#!/usr/bin/env node
const apiClient = require('./api_client');

async function getCoinHistoricalChart(coinId, vsCurrency = 'usd', days = '7', precision = null) {
  const params = { vs_currency: vsCurrency, days, interval: 'daily' };
  if (precision) params.precision = precision;

  return apiClient.get(`/crypto/coins/${coinId}/market_chart`, params);
}

async function main() {
  const args = process.argv.slice(2);
  if (args.length === 0) {
    console.log(JSON.stringify({
      usage: 'node scripts/get_coin_historical_chart.js <coin_id> [--currency=usd] [--days=7] [--precision=2]',
      example: 'node scripts/get_coin_historical_chart.js bitcoin --currency=usd --days=30',
    }, null, 2));
    process.exit(1);
  }

  const coinId = args[0];
  let vsCurrency = 'usd';
  let days = '7';
  let precision = null;

  for (const arg of args.slice(1)) {
    if (arg.startsWith('--currency=')) vsCurrency = arg.split('=')[1];
    else if (arg.startsWith('--days=')) days = arg.split('=')[1];
    else if (arg.startsWith('--precision=')) precision = arg.split('=')[1];
  }

  const result = await getCoinHistoricalChart(coinId, vsCurrency, days, precision);
  console.log(JSON.stringify(result, null, 2));
}

main();
