#!/usr/bin/env node
import { tmrFetch, parseArgs } from "./_lib.mjs";

const { help, named } = parseArgs(process.argv);
if (help || !named.business || !named.amount) {
  console.error("Usage: create-order.mjs --business <id> --amount <N> [--intention <id>]");
  process.exit(2);
}

const body = {
  business_id: named.business,
  amount: Number.parseFloat(named.amount),
};
if (named.intention) body.intention_id = named.intention;

const data = await tmrFetch("POST", "/orders/", body);
console.log(`Order created: ${data.id}`);
console.log(JSON.stringify(data, null, 2));
