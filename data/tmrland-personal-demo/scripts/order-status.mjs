#!/usr/bin/env node
import { tmrFetch, parseArgs } from "./_lib.mjs";

const { help, positional } = parseArgs(process.argv);
if (help || positional.length === 0) {
  console.error("Usage: order-status.mjs <order-id>");
  process.exit(2);
}

const data = await tmrFetch("GET", `/orders/${positional[0]}`);
console.log(`## Order ${data.id}\n`);
console.log(`Status: ${data.status}`);
console.log(`Amount: ${data.amount}`);
console.log(`Business: ${data.business_id}`);
console.log(`Created: ${data.created_at}`);
if (data.delivered_at) console.log(`Delivered: ${data.delivered_at}`);
