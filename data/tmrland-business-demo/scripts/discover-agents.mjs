#!/usr/bin/env node
import { tmrFetch, parseArgs } from "./_lib.mjs";

const { help, named } = parseArgs(process.argv);
if (help || !named.capabilities) {
  console.error('Usage: discover-agents.mjs --capabilities "a,b,c"');
  process.exit(2);
}

const body = { capabilities: named.capabilities.split(",").map(s => s.trim()) };

const data = await tmrFetch("POST", "/a2a/discover", body);

const agents = data.agents ?? data.items ?? data;
console.log(`## Discovered Agents (${Array.isArray(agents) ? agents.length : "?"})\n`);
for (const a of Array.isArray(agents) ? agents : []) {
  console.log(`- **${a.brand_name_en ?? a.business_id ?? a.id}**`);
  if (a.capabilities) console.log(`  Capabilities: ${a.capabilities.join(", ")}`);
  if (a.a2a_endpoint) console.log(`  Endpoint: ${a.a2a_endpoint}`);
  console.log();
}
