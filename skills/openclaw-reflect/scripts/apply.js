#!/usr/bin/env node
/**
 * apply.js — Applies approved proposals with warden snapshot + ledger logging.
 *
 * Tiers:
 *   1 (MEMORY.md) — auto-apply if confidence >= 0.7 and --auto flag
 *   2 (CLAUDE.md) — auto-apply if confidence >= 0.85 and --auto flag
 *   3 (SOUL.md)   — always queue to pending.json for operator approval
 *
 * Usage:
 *   node apply.js --auto              (session-end: apply eligible, queue rest)
 *   node apply.js --id <id> --approve (operator: approve a specific proposal)
 *   node apply.js --id <id> --reject  (operator: reject a specific proposal)
 */
'use strict';

const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');
const crypto = require('crypto');

const REFLECT_DIR = path.join(process.cwd(), '.reflect');
const PROPOSALS_FILE = path.join(REFLECT_DIR, 'proposals.json');
const PENDING_FILE = path.join(REFLECT_DIR, 'pending.json');
const APPLIED_FILE = path.join(REFLECT_DIR, 'applied.jsonl');
const SNAPSHOTS_DIR = path.join(REFLECT_DIR, 'snapshots');

const AUTO_APPLY_THRESHOLDS = { 1: 0.7, 2: 0.85 };

function loadProposals() {
  if (!fs.existsSync(PROPOSALS_FILE)) return [];
  try { return JSON.parse(fs.readFileSync(PROPOSALS_FILE, 'utf8')); }
  catch { return []; }
}

function loadPending() {
  if (!fs.existsSync(PENDING_FILE)) return [];
  try { return JSON.parse(fs.readFileSync(PENDING_FILE, 'utf8')); }
  catch { return []; }
}

function saveProposals(proposals) {
  fs.writeFileSync(PROPOSALS_FILE, JSON.stringify(proposals, null, 2), 'utf8');
}

function savePending(pending) {
  fs.writeFileSync(PENDING_FILE, JSON.stringify(pending, null, 2), 'utf8');
}

function snapshotFile(filePath) {
  if (!fs.existsSync(filePath)) return null;
  if (!fs.existsSync(SNAPSHOTS_DIR)) fs.mkdirSync(SNAPSHOTS_DIR, { recursive: true });

  const ts = new Date().toISOString().replace(/[:.]/g, '-');
  const name = path.basename(filePath);
  const snapshotPath = path.join(SNAPSHOTS_DIR, `${name}.${ts}.bak`);
  fs.copyFileSync(filePath, snapshotPath);

  // Try warden snapshot too (best-effort)
  try {
    execFileSync(process.execPath,
      [path.join(process.cwd(), 'skills', 'openclaw-warden', 'warden.js'), 'snapshot'],
      { cwd: process.cwd(), timeout: 10000 }
    );
  } catch {}

  return snapshotPath;
}

function appendToFile(filePath, content) {
  const existing = fs.existsSync(filePath) ? fs.readFileSync(filePath, 'utf8') : '';
  const separator = existing.endsWith('\n') ? '' : '\n';
  fs.writeFileSync(filePath, existing + separator + content + '\n', 'utf8');
}

function applyProposal(proposal) {
  const targetFile = path.join(process.cwd(), proposal.blast_target);
  const snapshotPath = snapshotFile(targetFile);

  // Build the learning entry to append
  const entry = [
    `\n## Reflect: ${proposal.id}`,
    `<!-- Applied: ${new Date().toISOString()} | Tier: ${proposal.blast_tier} | Confidence: ${proposal.evaluation?.confidence || proposal.confidence} -->`,
    `**Pattern:** \`${proposal.tool}\` → ${proposal.error_pattern}`,
    `**Learning:** ${proposal.evaluation?.modification || proposal.hypothesis.proposed_change}`,
    `**Success criteria:** ${proposal.hypothesis.success_criteria}`,
  ].join('\n');

  appendToFile(targetFile, entry);

  // Log to applied.jsonl
  const record = {
    ts: new Date().toISOString(),
    change_id: crypto.randomBytes(6).toString('hex'),
    proposal_id: proposal.id,
    pattern_key: proposal.pattern_key,
    target: proposal.blast_target,
    snapshot: snapshotPath,
    content: entry,
  };
  fs.appendFileSync(APPLIED_FILE, JSON.stringify(record) + '\n', 'utf8');

  return record.change_id;
}

function parseArgs() {
  const args = process.argv.slice(2);
  const result = { auto: false, id: null, approve: false, reject: false };
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--auto') result.auto = true;
    if (args[i] === '--id') result.id = args[++i];
    if (args[i] === '--approve') result.approve = true;
    if (args[i] === '--reject') result.reject = true;
  }
  return result;
}

function main() {
  const args = parseArgs();
  const proposals = loadProposals();
  const pending = loadPending();
  const messages = [];

  if (args.id) {
    // Operator manual approve/reject
    const allProposals = [...proposals, ...pending];
    const target = allProposals.find(p => p.id === args.id);
    if (!target) {
      process.stdout.write(`proposal ${args.id} not found`);
      return;
    }
    if (args.approve) {
      const changeId = applyProposal(target);
      target.status = 'applied';
      target.applied_at = new Date().toISOString();
      target.change_id = changeId;
      messages.push(`applied ${target.id} → ${target.blast_target} (change: ${changeId})`);
    } else if (args.reject) {
      target.status = 'rejected_by_operator';
      target.rejected_at = new Date().toISOString();
      messages.push(`rejected ${target.id}`);
    }
    // Update both files
    const updatedProposals = proposals.map(p => p.id === target.id ? target : p);
    const updatedPending = pending.filter(p => p.id !== target.id);
    saveProposals(updatedProposals);
    savePending(updatedPending);

  } else if (args.auto) {
    // Auto-apply eligible proposals, queue the rest
    const approved = proposals.filter(p => p.status === 'approved');
    const newPending = loadPending();

    for (const proposal of approved) {
      const threshold = AUTO_APPLY_THRESHOLDS[proposal.blast_tier];

      if (!threshold) {
        // Tier 3 (SOUL.md) — always queue
        if (!newPending.find(p => p.id === proposal.id)) {
          newPending.push(proposal);
          messages.push(`queued ${proposal.id} for operator approval (SOUL.md)`);
        }
        continue;
      }

      const confidence = proposal.evaluation?.confidence ?? proposal.confidence;
      if (confidence >= threshold) {
        const changeId = applyProposal(proposal);
        proposal.status = 'applied';
        proposal.applied_at = new Date().toISOString();
        proposal.change_id = changeId;
        messages.push(`auto-applied ${proposal.id} → ${proposal.blast_target} (${changeId})`);
      } else {
        // Below threshold — queue for operator
        if (!newPending.find(p => p.id === proposal.id)) {
          newPending.push(proposal);
          messages.push(`queued ${proposal.id} (confidence ${confidence} < ${threshold})`);
        }
      }
    }

    saveProposals(proposals);
    savePending(newPending);
  }

  process.stdout.write(messages.join('; ') || 'nothing to apply');
}

main();
