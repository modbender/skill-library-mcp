#!/usr/bin/env node
// scripts/proposals.js – List proposals by status
const { initSchema } = require('../lib/db');

function main() {
  const db = initSchema();
  const filter = process.argv[2] || 'proposed';

  let sql = 'SELECT * FROM proposals';
  const params = [];
  if (filter !== 'all') {
    sql += ' WHERE status = ?';
    params.push(filter);
  }
  sql += ' ORDER BY proposed_at DESC LIMIT 20';

  const rows = db.prepare(sql).all(...params);
  if (!rows.length) { console.log(`No proposals (${filter}).`); return; }

  const eff = { quick: '⚡', medium: '🔧', large: '🏗️' };
  console.log(`💡 Proposals (${filter}):\n`);
  for (const p of rows) {
    console.log(`#${p.id} [${p.status}] ${eff[p.effort_estimate] || ''} ${p.title}`);
    console.log(`   ${p.description}`);
    if (p.reasoning) console.log(`   Why: ${p.reasoning}`);
    if (p.user_feedback) console.log(`   Feedback: ${p.user_feedback}`);
    console.log(`   ${p.proposed_at}\n`);
  }
}
main();
