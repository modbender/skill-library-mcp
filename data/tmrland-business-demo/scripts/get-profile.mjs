#!/usr/bin/env node
import { tmrFetch } from "./_lib.mjs";

const data = await tmrFetch("GET", "/businesses/me");
console.log(`## Business Profile\n`);
console.log(`ID:     ${data.id}`);
console.log(`Brand:  ${data.brand_name_en} (${data.brand_name_zh})`);
console.log(`Status: ${data.status}`);
console.log(`Rep:    ${data.reputation_score ?? "N/A"}`);
if (data.description_en) console.log(`\n${data.description_en}`);
if (data.grand_apparatus_stats) {
  const s = data.grand_apparatus_stats;
  console.log(`\nApparatus: ${s.total_answers} answers, ${(s.accuracy_rate * 100).toFixed(0)}% accuracy, avg ${s.avg_score}`);
}
