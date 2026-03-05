#!/usr/bin/env node
/**
 * OpenClaw hook tests (consolidated). Learnings from benchmark:
 * - Assert reminder is token-efficient (shorter than legacy).
 * - One script for all edge cases for maintainability.
 */
const fs = require('fs');
const path = require('path');

const SKILL_ROOT = process.env.SKILL_ROOT || path.join(__dirname, '..');
const handler = require(path.join(SKILL_ROOT, 'hooks/openclaw/handler.js'));

function run(name, fn) {
  return Promise.resolve()
    .then(fn)
    .then(() => ({ name, ok: true }))
    .catch((e) => ({ name, ok: false, error: e.message || e }));
}

async function main() {
  const results = [];

  // --- Reminder token-efficiency (learning from benchmark) ---
  const legacyPath = path.join(SKILL_ROOT, 'scripts/benchmark/legacy-reminder.txt');
  let legacyChars = 632; // fallback if file missing
  if (fs.existsSync(legacyPath)) {
    legacyChars = fs.readFileSync(legacyPath, 'utf8').length;
  }
  results.push(await run('reminder token-efficient (shorter than legacy)', async () => {
    const event = { type: 'agent', action: 'bootstrap', sessionKey: 'main', context: { bootstrapFiles: [] } };
    await handler(event);
    const content = event.context?.bootstrapFiles?.[0]?.content || '';
    if (!content.includes('mulch prime') || !content.includes('mulch record')) throw new Error('reminder missing mulch prime/record');
    if (content.length > legacyChars) throw new Error(`reminder ${content.length} chars > legacy ${legacyChars} (should be shorter)`);
  }));

  // --- Bootstrap main → injects ---
  results.push(await run('bootstrap main injects SELF_IMPROVEMENT_REMINDER.md', async () => {
    const event = { type: 'agent', action: 'bootstrap', sessionKey: 'main', context: { bootstrapFiles: [] } };
    await handler(event);
    const f = event.context.bootstrapFiles;
    if (!Array.isArray(f) || f.length !== 1 || f[0].path !== 'SELF_IMPROVEMENT_REMINDER.md' || !f[0].virtual) {
      throw new Error('expected one virtual SELF_IMPROVEMENT_REMINDER.md');
    }
  }));

  // --- Sub-agent skip ---
  results.push(await run('sub-agent skipped', async () => {
    const event = { type: 'agent', action: 'bootstrap', sessionKey: 'agent:main:subagent:x', context: { bootstrapFiles: [] } };
    await handler(event);
    if (event.context.bootstrapFiles.length !== 0) throw new Error('sub-agent should skip');
  }));

  // --- Null / missing context → no throw ---
  results.push(await run('null event no throw', async () => { await handler(null); }));
  results.push(await run('missing context no throw', async () => { await handler({ type: 'agent', action: 'bootstrap' }); }));

  // --- Wrong type/action → no injection ---
  results.push(await run('wrong type skipped', async () => {
    const event = { type: 'other', action: 'bootstrap', context: { bootstrapFiles: [] } };
    await handler(event);
    if (event.context.bootstrapFiles.length !== 0) throw new Error('wrong type should skip');
  }));
  results.push(await run('wrong action skipped', async () => {
    const event = { type: 'agent', action: 'other', context: { bootstrapFiles: [] } };
    await handler(event);
    if (event.context.bootstrapFiles.length !== 0) throw new Error('wrong action should skip');
  }));

  // --- bootstrapFiles not array → no crash ---
  results.push(await run('bootstrapFiles missing no crash', async () => {
    await handler({ type: 'agent', action: 'bootstrap', sessionKey: 'main', context: {} });
  }));
  results.push(await run('bootstrapFiles null no crash', async () => {
    await handler({ type: 'agent', action: 'bootstrap', sessionKey: 'main', context: { bootstrapFiles: null } });
  }));

  // --- sessionKey missing → inject (treated as main) ---
  results.push(await run('missing sessionKey injects', async () => {
    const event = { type: 'agent', action: 'bootstrap', context: { bootstrapFiles: [] } };
    await handler(event);
    if (event.context.bootstrapFiles.length !== 1) throw new Error('missing sessionKey should inject');
  }));

  // Report
  const failed = results.filter((r) => !r.ok);
  results.forEach((r) => {
    console.log(r.ok ? `OK: ${r.name}` : `FAIL: ${r.name}${r.error ? ' - ' + r.error : ''}`);
  });
  if (failed.length) {
    process.exitCode = 1;
    process.exit(1);
  }
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
