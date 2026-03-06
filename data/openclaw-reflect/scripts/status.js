#!/usr/bin/env node
/**
 * status.js — Human-readable status report for openclaw-reflect.
 *
 * Usage:
 *   node status.js              (full report)
 *   node status.js --brief      (one-line summary)
 *   node status.js --pending    (show proposals awaiting operator approval)
 *   node status.js --history    (show applied changes)
 */
'use strict';

const fs = require('fs');
const path = require('path');

const REFLECT_DIR = path.join(process.cwd(), '.reflect');
const OUTCOMES_FILE = path.join(REFLECT_DIR, 'outcomes.jsonl');
const PATTERNS_FILE = path.join(REFLECT_DIR, 'patterns.json');
const PROPOSALS_FILE = path.join(REFLECT_DIR, 'proposals.json');
const PENDING_FILE = path.join(REFLECT_DIR, 'pending.json');
const APPLIED_FILE = path.join(REFLECT_DIR, 'applied.jsonl');

function load(file, parse = true) {
  if (!fs.existsSync(file)) return parse ? [] : '';
  try {
    const content = fs.readFileSync(file, 'utf8');
    return parse ? JSON.parse(content) : content;
  } catch { return parse ? [] : ''; }
}

function loadJsonl(file) {
  if (!fs.existsSync(file)) return [];
  return fs.readFileSync(file, 'utf8')
    .trim().split('\n').filter(Boolean)
    .map(l => { try { return JSON.parse(l); } catch { return null; } })
    .filter(Boolean);
}

function parseArgs() {
  const args = process.argv.slice(2);
  return {
    brief: args.includes('--brief'),
    pending: args.includes('--pending'),
    history: args.includes('--history'),
  };
}

function main() {
  const args = parseArgs();

  const outcomes = loadJsonl(OUTCOMES_FILE);
  const patterns = load(PATTERNS_FILE);
  const proposals = load(PROPOSALS_FILE);
  const pending = load(PENDING_FILE);
  const applied = loadJsonl(APPLIED_FILE);

  const errors = outcomes.filter(e => e.outcome === 'error').length;
  const successes = outcomes.filter(e => e.outcome === 'success').length;
  const activeProposals = proposals.filter(p => !['applied', 'rejected', 'reverted', 'rejected_by_operator'].includes(p.status));
  const appliedNonReverted = applied.filter(e => !e.reverted_at);

  if (args.brief) {
    const parts = [];
    if (patterns.length > 0) parts.push(`${patterns.length} pattern(s)`);
    if (pending.length > 0) parts.push(`${pending.length} pending approval`);
    if (appliedNonReverted.length > 0) parts.push(`${appliedNonReverted.length} applied`);
    process.stdout.write(parts.join(', ') || 'no active improvements');
    return;
  }

  if (args.pending) {
    if (pending.length === 0) {
      console.log('No proposals awaiting approval.');
      return;
    }
    console.log(`\n=== Pending Operator Approval (${pending.length}) ===\n`);
    for (const p of pending) {
      console.log(`ID: ${p.id}`);
      console.log(`Tool: ${p.tool} | Target: ${p.blast_target} | Confidence: ${p.evaluation?.confidence ?? p.confidence}`);
      console.log(`Pattern: ${p.error_pattern}`);
      console.log(`Proposed: ${p.hypothesis.proposed_change}`);
      console.log(`Evaluator: ${p.evaluation?.reasoning?.slice(0, 200) || 'not evaluated'}`);
      console.log(`\nApprove: node .reflect/scripts/apply.js --id ${p.id} --approve`);
      console.log(`Reject:  node .reflect/scripts/apply.js --id ${p.id} --reject\n`);
      console.log('---');
    }
    return;
  }

  if (args.history) {
    if (applied.length === 0) {
      console.log('No changes applied yet.');
      return;
    }
    console.log(`\n=== Applied Changes (${applied.length}) ===\n`);
    for (const e of applied) {
      const status = e.reverted_at ? '↩ REVERTED' : '✓ ACTIVE';
      console.log(`[${status}] ${e.change_id} — ${e.target} — ${e.ts}`);
    }
    console.log(`\nTo rollback last: node .reflect/scripts/rollback.js`);
    return;
  }

  // Full report
  console.log('\n=== openclaw-reflect status ===\n');
  console.log(`Outcomes recorded: ${outcomes.length} (${successes} success, ${errors} error)`);
  console.log(`Patterns detected: ${patterns.length}`);
  console.log(`Active proposals:  ${activeProposals.length}`);
  console.log(`Pending approval:  ${pending.length}`);
  console.log(`Applied (active):  ${appliedNonReverted.length}`);

  if (patterns.length > 0) {
    console.log('\nTop patterns:');
    patterns.slice(0, 5).forEach(p =>
      console.log(`  ${p.tool} — "${p.error_pattern.slice(0, 60)}" (${p.recurrence}x, ${p.session_count} sessions)`)
    );
  }

  if (pending.length > 0) {
    console.log(`\n⚠ ${pending.length} proposal(s) need your approval.`);
    console.log('  Run: node .reflect/scripts/status.js --pending');
  }

  console.log('');
}

main();
