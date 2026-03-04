#!/usr/bin/env node
const apiClient = require('./api_client');

async function getStockQuote(symbols) {
  const symbolsStr = symbols.map((s) => s.toUpperCase()).join(',');
  return apiClient.get('/stock/quote', { symbols: symbolsStr });
}

async function main() {
  const args = process.argv.slice(2);
  if (args.length === 0) {
    console.log(JSON.stringify({
      usage: 'node scripts/get_stock_quote.js <SYMBOL_1> [SYMBOL_2] ...',
      example: 'node scripts/get_stock_quote.js AAPL MSFT GOOG',
    }, null, 2));
    process.exit(1);
  }

  const result = await getStockQuote(args);
  console.log(JSON.stringify(result, null, 2));
}

main();
