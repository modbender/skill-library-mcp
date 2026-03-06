#!/usr/bin/env node
import { tmrFetch, parseArgs } from "./_lib.mjs";

const { help, named } = parseArgs(process.argv);
if (help) {
  console.error("Usage: search-businesses.mjs [--limit N]");
  process.exit(2);
}

const limit = Number.parseInt(named.limit ?? "20", 10);
const data = await tmrFetch("GET", `/businesses/?limit=${limit}`);

console.log(`## Businesses (${data.items?.length ?? 0} of ${data.total ?? "?"})\n`);
for (const s of data.items ?? []) {
  console.log(`- **${s.brand_name_en}** (${s.brand_name_zh}) — reputation: ${s.reputation_score ?? "N/A"}`);
  console.log(`  ID: ${s.id} | Status: ${s.status}`);
  if (s.description_en) console.log(`  ${s.description_en.slice(0, 120)}`);
  console.log();
}
