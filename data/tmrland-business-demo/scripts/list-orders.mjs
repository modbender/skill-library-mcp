#!/usr/bin/env node
import { tmrFetch, parseArgs } from "./_lib.mjs";

const { help, named } = parseArgs(process.argv);
if (help) {
  console.error("Usage: list-orders.mjs [--limit N]");
  process.exit(2);
}

const limit = Number.parseInt(named.limit ?? "20", 10);
const data = await tmrFetch("GET", `/orders/?role=business&limit=${limit}`);

console.log(`## Orders (${data.items?.length ?? 0})\n`);
for (const o of data.items ?? []) {
  console.log(`- ${o.id} | ${o.status} | $${o.amount} | ${o.created_at}`);
}
