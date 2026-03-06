#!/usr/bin/env node
import { tmrFetch, parseArgs } from "./_lib.mjs";

const { help, positional } = parseArgs(process.argv);
if (help || !positional[0]) {
  console.error("Usage: pay-order.mjs <order-id>");
  process.exit(2);
}

const data = await tmrFetch("POST", `/orders/${positional[0]}/pay`);
console.log(`Order ${data.id} paid — status: ${data.status}`);
console.log(JSON.stringify(data, null, 2));
