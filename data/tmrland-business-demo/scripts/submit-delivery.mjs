#!/usr/bin/env node
import { tmrFetch, parseArgs } from "./_lib.mjs";

const { help, positional, named } = parseArgs(process.argv);
if (help || positional.length === 0 || (!named.notes && !named.url)) {
  console.error('Usage: submit-delivery.mjs <order-id> --notes "delivery notes..." [--url "https://..."]');
  process.exit(2);
}

const body = {};
if (named.notes) body.delivery_notes = named.notes;
if (named.url) body.deliverable_url = named.url;

const data = await tmrFetch("POST", `/orders/${positional[0]}/deliver`, body);
console.log(`Delivery submitted for order ${positional[0]}`);
console.log(JSON.stringify(data, null, 2));
