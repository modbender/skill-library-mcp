#!/usr/bin/env node
import { tmrFetch, parseArgs } from "./_lib.mjs";

const { help, named } = parseArgs(process.argv);
if (help || !named.content) {
  console.error('Usage: create-intention.mjs --content "..." [--budget-min N] [--budget-max N] [--tags "a,b"] [--locale zh]');
  process.exit(2);
}

const body = {
  content: named.content,
};
if (named["budget-min"]) body.budget_min = Number.parseFloat(named["budget-min"]);
if (named["budget-max"]) body.budget_max = Number.parseFloat(named["budget-max"]);
if (named.tags) body.tags = named.tags.split(",").map((t) => t.trim());
if (named.locale) body.locale = named.locale;

const data = await tmrFetch("POST", "/intentions/", body);
console.log(`Intention created: ${data.id}`);
console.log(JSON.stringify(data, null, 2));
