#!/usr/bin/env node
/**
 * propose.js — Generates structured improvement proposals from qualifying patterns.
 * Reads patterns.json, produces proposals.json.
 * Each proposal has a blast_radius tier (1=MEMORY.md, 2=CLAUDE.md, 3=SOUL.md)
 * and a preliminary confidence score based on recurrence and session count.
 */
'use strict';

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const REFLECT_DIR = path.join(process.cwd(), '.reflect');
const PATTERNS_FILE = path.join(REFLECT_DIR, 'patterns.json');
const PROPOSALS_FILE = path.join(REFLECT_DIR, 'proposals.json');
const APPLIED_FILE = path.join(REFLECT_DIR, 'applied.jsonl');

function loadPatterns() {
  if (!fs.existsSync(PATTERNS_FILE)) return [];
  try { return JSON.parse(fs.readFileSync(PATTERNS_FILE, 'utf8')); }
  catch { return []; }
}

function loadApplied() {
  if (!fs.existsSync(APPLIED_FILE)) return new Set();
  const lines = fs.readFileSync(APPLIED_FILE, 'utf8').trim().split('\n').filter(Boolean);
  const applied = new Set();
  for (const l of lines) {
    try {
      const e = JSON.parse(l);
      if (e.pattern_key) applied.add(e.pattern_key);
    } catch {}
  }
  return applied;
}

function inferBlastRadius(pattern) {
  // Tier 1: factual/preference corrections → MEMORY.md
  // Tier 2: behavioral patterns → CLAUDE.md
  // Tier 3: identity/value conflicts → SOUL.md (always operator-gated)
  const p = pattern.error_pattern.toLowerCase();

  if (/permission|denied|access|auth|credential|secret|key/i.test(p)) {
    return { tier: 1, target: 'MEMORY.md', label: 'credential/access pattern' };
  }
  if (/not found|no such|missing file|path/i.test(p)) {
    return { tier: 1, target: 'MEMORY.md', label: 'file path assumption' };
  }
  if (/timeout|connection|network|ssl|certificate/i.test(p)) {
    return { tier: 1, target: 'MEMORY.md', label: 'network/connectivity pattern' };
  }
  if (/syntax|parse|json|yaml|invalid/i.test(p)) {
    return { tier: 2, target: 'CLAUDE.md', label: 'formatting/syntax behavior' };
  }
  if (/loop|recursion|infinite|repeat|retry/i.test(p)) {
    return { tier: 2, target: 'CLAUDE.md', label: 'control flow behavior' };
  }
  // Default: factual memory update
  return { tier: 1, target: 'MEMORY.md', label: 'recurring error pattern' };
}

function confidenceScore(pattern) {
  // Base: recurrence weight
  const recurrenceScore = Math.min(pattern.recurrence / 10, 0.5);
  // Session diversity: more sessions = more confident
  const sessionScore = Math.min(pattern.session_count / 5, 0.3);
  // Recency: if last seen recently, higher confidence
  const daysSince = (Date.now() - new Date(pattern.last_seen).getTime()) / 86400000;
  const recencyScore = daysSince < 1 ? 0.2 : daysSince < 7 ? 0.1 : 0.0;

  return Math.round((recurrenceScore + sessionScore + recencyScore) * 100) / 100;
}

function buildProposal(pattern, applied) {
  if (applied.has(pattern.key)) return null; // Already addressed

  const blast = inferBlastRadius(pattern);
  const confidence = confidenceScore(pattern);

  const id = crypto.createHash('sha256')
    .update(pattern.key + pattern.first_seen)
    .digest('hex')
    .slice(0, 12);

  return {
    id,
    pattern_key: pattern.key,
    tool: pattern.tool,
    error_pattern: pattern.error_pattern,
    blast_tier: blast.tier,
    blast_target: blast.target,
    blast_label: blast.label,
    confidence,
    recurrence: pattern.recurrence,
    session_count: pattern.session_count,
    first_seen: pattern.first_seen,
    last_seen: pattern.last_seen,
    sample_inputs: pattern.sample_inputs,
    proposed_at: new Date().toISOString(),
    status: 'pending_evaluation',
    hypothesis: buildHypothesis(pattern, blast),
  };
}

function buildHypothesis(pattern, blast) {
  return {
    problem: `The tool "${pattern.tool}" has failed ${pattern.recurrence} times across ` +
             `${pattern.session_count} sessions with the pattern: "${pattern.error_pattern}".`,
    likely_cause: `Recurring error suggests a consistent assumption or behavior that is ` +
                  `incorrect for this environment or context.`,
    proposed_change: `Add a note to ${blast.target} documenting this failure pattern and ` +
                     `the correct approach or prerequisite for "${pattern.tool}" calls ` +
                     `matching this error signature.`,
    success_criteria: `The pattern "${pattern.error_pattern}" does not recur in the next ` +
                      `5 sessions after the change is applied.`,
  };
}

function main() {
  const patterns = loadPatterns();
  if (patterns.length === 0) {
    process.stdout.write('no patterns to propose for');
    return;
  }

  const applied = loadApplied();
  const proposals = patterns
    .map(p => buildProposal(p, applied))
    .filter(Boolean);

  // Merge with existing proposals (preserve evaluator decisions)
  let existing = [];
  if (fs.existsSync(PROPOSALS_FILE)) {
    try { existing = JSON.parse(fs.readFileSync(PROPOSALS_FILE, 'utf8')); }
    catch {}
  }
  const existingIds = new Set(existing.map(e => e.id));
  const newProposals = proposals.filter(p => !existingIds.has(p.id));
  const merged = [...existing, ...newProposals];

  fs.writeFileSync(PROPOSALS_FILE, JSON.stringify(merged, null, 2), 'utf8');

  if (newProposals.length === 0) {
    process.stdout.write('no new proposals (all patterns already proposed or applied)');
  } else {
    process.stdout.write(
      `generated ${newProposals.length} new proposal(s): ` +
      newProposals.map(p => `${p.id} (tier ${p.blast_tier}, confidence ${p.confidence})`).join(', ')
    );
  }
}

main();
