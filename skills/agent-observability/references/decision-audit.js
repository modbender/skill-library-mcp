'use strict';
/**
 * decision-audit.js
 *
 * Lightweight append-only audit log of significant agent decisions.
 * Schema: { id, ts, task_type, decision, reasoning_summary, outcome, session_channel }
 *
 * Installation: copy to $OPENCLAW_WORKSPACE/lib/decision-audit.js
 *
 * Usage:
 *   const { logDecision } = require('./lib/decision-audit');
 *   logDecision({ task_type, decision, reasoning_summary }, workspaceRoot);
 *
 * @module lib/decision-audit
 */

const fs     = require('fs');
const path   = require('path');
const crypto = require('crypto');

const AUDIT_FILE = 'memory/decisions-audit.jsonl';

function ensureDir(filePath) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
}

function auditPath(workspaceRoot) {
  const root = workspaceRoot || process.env.OPENCLAW_WORKSPACE || process.cwd();
  return path.join(root, AUDIT_FILE);
}

/**
 * Log a significant agent decision to the append-only audit log.
 *
 * @param {{ task_type: string, decision: string, reasoning_summary: string, outcome?: string, session_channel?: string }} entry
 * @param {string} workspaceRoot - Absolute path to workspace root
 * @returns {{ id: string, ts: string, error?: string }}
 *
 * @example
 * logDecision({
 *   task_type: 'code_review',
 *   decision: 'spawn CoderAgent',
 *   reasoning_summary: 'Multi-file edit blocks chat >5s',
 * }, workspaceRoot);
 */
function logDecision(entry, workspaceRoot) {
  const ts = new Date().toISOString();
  const id = crypto.randomBytes(6).toString('hex');

  const record = {
    id,
    ts,
    task_type:         entry.task_type         || 'unknown',
    decision:          entry.decision          || '',
    reasoning_summary: entry.reasoning_summary || '',
    outcome:           entry.outcome           || null,
    session_channel:   entry.session_channel   || null
  };

  const filePath = auditPath(workspaceRoot);
  try {
    ensureDir(filePath);
    fs.appendFileSync(filePath, JSON.stringify(record) + '\n', 'utf8');
  } catch (err) {
    return { id, ts, error: err.message };
  }

  return { id, ts };
}

/**
 * Return the last N decisions from the audit log.
 * Returns [] if the file doesn't exist or is unreadable.
 *
 * @param {number} [limit=20]
 * @param {string} workspaceRoot
 * @returns {Object[]}
 */
function getRecentDecisions(limit = 20, workspaceRoot) {
  const filePath = auditPath(workspaceRoot);
  let lines;
  try {
    lines = fs.readFileSync(filePath, 'utf8').split('\n').filter(l => l.trim());
  } catch (_) { return []; }

  return lines
    .slice(-limit)
    .map(l => { try { return JSON.parse(l); } catch (_) { return null; } })
    .filter(Boolean);
}

/**
 * Update the outcome field of a specific decision entry by id.
 *
 * @param {string} id - Decision id to update
 * @param {string} outcome - e.g. "success", "failed", "cancelled"
 * @param {string} workspaceRoot
 * @returns {{ updated: boolean, id: string, error?: string }}
 */
function updateOutcome(id, outcome, workspaceRoot) {
  const filePath = auditPath(workspaceRoot);
  let lines;
  try {
    lines = fs.readFileSync(filePath, 'utf8').split('\n');
  } catch (_) { return { updated: false, id }; }

  let updated = false;
  const newLines = lines.map(line => {
    if (!line.trim()) return line;
    try {
      const record = JSON.parse(line);
      if (record.id === id) {
        record.outcome    = outcome;
        record.outcome_ts = new Date().toISOString();
        updated = true;
        return JSON.stringify(record);
      }
    } catch (_) {}
    return line;
  });

  if (!updated) return { updated: false, id };

  const tmpPath = filePath + '.tmp.' + process.pid;
  try {
    ensureDir(filePath);
    fs.writeFileSync(tmpPath, newLines.join('\n'), 'utf8');
    fs.renameSync(tmpPath, filePath);
  } catch (err) {
    try { fs.unlinkSync(tmpPath); } catch (_) {}
    return { updated: false, id, error: err.message };
  }

  return { updated: true, id };
}

module.exports = { logDecision, getRecentDecisions, updateOutcome };

// ── Smoke test ────────────────────────────────────────────────────────────────
if (require.main === module) {
  const os    = require('os');
  const tmpWs = fs.mkdtempSync(path.join(os.tmpdir(), 'decision-audit-test-'));
  console.log('=== decision-audit smoke test ===');

  const r1 = logDecision({
    task_type: 'code_review',
    decision: 'spawn CoderAgent',
    reasoning_summary: 'Multi-file edit; blocks chat',
    session_channel: 'discord'
  }, tmpWs);
  console.assert(r1.id && r1.ts, 'logDecision must return id + ts');
  console.log('logged:', r1);

  const recent = getRecentDecisions(10, tmpWs);
  console.assert(recent.length === 1, 'should have 1 entry');
  console.log('getRecentDecisions:', recent.length, 'entries');

  const upd = updateOutcome(r1.id, 'success', tmpWs);
  console.assert(upd.updated, 'updateOutcome should return updated=true');
  const after = getRecentDecisions(10, tmpWs);
  console.assert(after.find(d => d.id === r1.id)?.outcome === 'success', 'outcome should be success');
  console.log('updateOutcome: ok');

  fs.rmSync(tmpWs, { recursive: true });
  console.log('\n✓ Smoke test passed');
}
