#!/usr/bin/env node
/**
 * rollback.js — Reverts the last applied change (or a specific change by ID).
 * Restores the snapshot taken before apply.js ran.
 *
 * Usage:
 *   node rollback.js              (revert the most recent applied change)
 *   node rollback.js --id <id>   (revert a specific change by change_id)
 */
'use strict';

const fs = require('fs');
const path = require('path');

const REFLECT_DIR = path.join(process.cwd(), '.reflect');
const APPLIED_FILE = path.join(REFLECT_DIR, 'applied.jsonl');
const PROPOSALS_FILE = path.join(REFLECT_DIR, 'proposals.json');

function loadApplied() {
  if (!fs.existsSync(APPLIED_FILE)) return [];
  return fs.readFileSync(APPLIED_FILE, 'utf8')
    .trim().split('\n').filter(Boolean)
    .map(l => { try { return JSON.parse(l); } catch { return null; } })
    .filter(Boolean);
}

function parseArgs() {
  const args = process.argv.slice(2);
  const result = { id: null };
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--id') result.id = args[++i];
  }
  return result;
}

function markReverted(changeId) {
  // Update applied.jsonl — mark the entry as reverted
  const applied = loadApplied();
  const updated = applied.map(e => {
    if (e.change_id === changeId) return { ...e, reverted_at: new Date().toISOString() };
    return e;
  });
  fs.writeFileSync(
    APPLIED_FILE,
    updated.map(e => JSON.stringify(e)).join('\n') + '\n',
    'utf8'
  );
}

function markProposalReverted(proposalId) {
  if (!fs.existsSync(PROPOSALS_FILE)) return;
  try {
    const proposals = JSON.parse(fs.readFileSync(PROPOSALS_FILE, 'utf8'));
    const updated = proposals.map(p => {
      if (p.id === proposalId) return { ...p, status: 'reverted', reverted_at: new Date().toISOString() };
      return p;
    });
    fs.writeFileSync(PROPOSALS_FILE, JSON.stringify(updated, null, 2), 'utf8');
  } catch {}
}

function main() {
  const args = parseArgs();
  const applied = loadApplied();

  if (applied.length === 0) {
    process.stdout.write('no applied changes to roll back');
    return;
  }

  // Find the target change
  let target;
  if (args.id) {
    target = applied.find(e => e.change_id === args.id && !e.reverted_at);
    if (!target) {
      process.stdout.write(`change ${args.id} not found or already reverted`);
      return;
    }
  } else {
    // Most recent non-reverted
    target = [...applied].reverse().find(e => !e.reverted_at);
    if (!target) {
      process.stdout.write('no non-reverted changes found');
      return;
    }
  }

  // Restore the snapshot
  if (!target.snapshot || !fs.existsSync(target.snapshot)) {
    process.stdout.write(
      `snapshot not found for change ${target.change_id}. ` +
      `Target was: ${target.target}. Manual recovery required.`
    );
    return;
  }

  const targetFile = path.join(process.cwd(), target.target);
  fs.copyFileSync(target.snapshot, targetFile);

  markReverted(target.change_id);
  if (target.proposal_id) markProposalReverted(target.proposal_id);

  process.stdout.write(
    `rolled back change ${target.change_id} — ` +
    `restored ${target.target} from snapshot ${path.basename(target.snapshot)}`
  );
}

main();
