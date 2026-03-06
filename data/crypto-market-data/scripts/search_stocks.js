#!/usr/bin/env node
const apiClient = require('./api_client');

async function searchStocks(query, limit = 10) {
  return apiClient.get('/stock/search', { query, limit: String(limit) });
}

async function main() {
  const args = process.argv.slice(2);
  if (args.length === 0) {
    console.log(JSON.stringify({
      usage: 'node scripts/search_stocks.js <query> [--limit=10]',
      example: 'node scripts/search_stocks.js apple --limit=5',
    }, null, 2));
    process.exit(1);
  }

  let limit = 10;
  const queryParts = [];

  for (const arg of args) {
    if (arg.startsWith('--limit=')) {
      const val = parseInt(arg.split('=')[1], 10);
      if (!isNaN(val)) limit = val;
    } else {
      queryParts.push(arg);
    }
  }

  const result = await searchStocks(queryParts.join(' '), limit);
  console.log(JSON.stringify(result, null, 2));
}

main();
