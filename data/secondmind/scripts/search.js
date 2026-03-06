#!/usr/bin/env node
// scripts/search.js – CLI knowledge search (FTS5 + optional LLM rerank)
const { initSchema } = require('../lib/db');
const { search } = require('../lib/search');

async function main() {
  const args = process.argv.slice(2);
  if (!args.length) {
    console.log('Usage: node search.js "<query>" [--limit <n>] [--no-rerank]');
    return;
  }

  initSchema();
  const query = args[0];
  const li = args.indexOf('--limit');
  const limit = li >= 0 ? parseInt(args[li + 1]) : 10;
  const rerank = !args.includes('--no-rerank');

  console.log(`🔍 "${query}" (rerank: ${rerank ? 'on' : 'off'})\n`);

  const results = await search(query, { limit, rerank });

  if (!results.length) { console.log('No results.'); return; }

  for (const r of results) {
    const tier = r.tier ? ` [${r.tier}]` : '';
    const tags = r.tags ? ` {${JSON.parse(r.tags).join(', ')}}` : '';
    console.log(`[${r.category}]${tier} ${r.title}${tags}`);
    console.log(`  ${r.summary}\n`);
  }
  console.log(`${results.length} result(s).`);
}
main().catch(e => { console.error(e.message); process.exit(1); });
