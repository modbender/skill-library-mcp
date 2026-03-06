#!/usr/bin/env node
import { tmrFetch, parseArgs } from "./_lib.mjs";

const { help, positional } = parseArgs(process.argv);
if (help || positional.length === 0) {
  console.error("Usage: trigger-match.mjs <intention-id>");
  process.exit(2);
}

const intentionId = positional[0];
const data = await tmrFetch("POST", `/intentions/${intentionId}/match`);
console.log(`Matching triggered for intention ${intentionId}`);

const candidates = data.candidates ?? data.items ?? [];
console.log(`\n## Match Candidates (${candidates.length})\n`);
for (const c of candidates) {
  console.log(`- **${c.business_name_en ?? c.business_id}** — score: ${c.score ?? "N/A"}`);
  if (c.recall_sources) console.log(`  Sources: ${c.recall_sources.join(", ")}`);
  if (c.explanation) console.log(`  ${c.explanation.slice(0, 150)}`);
  console.log();
}
