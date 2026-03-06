#!/usr/bin/env node
const apiClient = require('./api_client');

const VALID_DAYS = ['1', '7', '14', '30', '90', '180', '365'];

async function getCoinOhlcChart(coinId, vsCurrency = 'usd', days = '7', precision = null) {
  if (!VALID_DAYS.includes(days)) {
    return { error: `days must be one of: ${VALID_DAYS.join(', ')}` };
  }

  const params = { vs_currency: vsCurrency, days };
  if (precision) params.precision = precision;

  return apiClient.get(`/crypto/coins/${coinId}/ohlc`, params);
}

async function main() {
  const args = process.argv.slice(2);
  if (args.length === 0) {
    console.log(JSON.stringify({
      usage: 'node scripts/get_coin_ohlc_chart.js <coin_id> [--currency=usd] [--days=7] [--precision=2]',
      example: 'node scripts/get_coin_ohlc_chart.js bitcoin --currency=usd --days=30',
      valid_days: VALID_DAYS,
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

  const result = await getCoinOhlcChart(coinId, vsCurrency, days, precision);
  console.log(JSON.stringify(result, null, 2));
}

main();
