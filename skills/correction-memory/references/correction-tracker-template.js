'use strict';
/**
 * correction-tracker.js
 *
 * Captures corrections to agent output and makes them reusable across sessions.
 * When an agent is overridden, rejected, or corrected, that gets logged and
 * injected into future spawns of the same agent type.
 *
 * Storage: memory/corrections/[agentType].jsonl
 * Schema:  { ts, issue, correction, session_channel, applied_count }
 *
 * Installation: copy to $OPENCLAW_WORKSPACE/lib/correction-tracker.js
 *
 * Usage:
 *   const { logCorrection, buildCorrectionPreamble } = require('./lib/correction-tracker');
 *   logCorrection('CoderAgent', 'what was wrong', 'correct behavior', workspaceRoot);
 *   const preamble = buildCorrectionPreamble('CoderAgent', workspaceRoot);
 *   // prepend preamble to agent spawn task description
 *
 * @module lib/correction-tracker
 */

const fs   = require('fs');
const path = require('path');

const CORRECTIONS_DIR  = 'memory/corrections';
const THIRTY_DAYS_MS   = 30 * 24 * 60 * 60 * 1000;

// Max lengths for input validation
const MAX_AGENT_TYPE_LEN = 64;
const MAX_CONTENT_LEN    = 2000;

// ── Input sanitization ────────────────────────────────────────────────────────

/**
 * Sanitize agentType: allow only alphanumeric, hyphens, underscores.
 * Prevents path traversal via filename injection.
 */
function _sanitizeAgentType(agentType) {
  if (typeof agentType !== 'string' || agentType.length === 0) {
    throw new Error('agentType must be a non-empty string');
  }
  if (agentType.length > MAX_AGENT_TYPE_LEN) {
    throw new Error(`agentType exceeds max length of ${MAX_AGENT_TYPE_LEN}`);
  }
  const sanitized = agentType.replace(/[^a-zA-Z0-9_-]/g, '');
  if (sanitized.length === 0) {
    throw new Error('agentType contains no valid characters after sanitization');
  }
  return sanitized;
}

/**
 * Sanitize free-text content (issue/correction).
 * Strips null bytes and control characters. Enforces max length.
 * Does NOT strip legitimate punctuation — just removes injection-risky chars.
 */
function _sanitizeContent(text, fieldName) {
  if (typeof text !== 'string' || text.trim().length === 0) {
    throw new Error(`${fieldName} must be a non-empty string`);
  }
  // Remove null bytes and ASCII control chars (except tab/newline which are benign)
  // eslint-disable-next-line no-control-regex
  const sanitized = text.replace(/\x00/g, '').replace(/[\x01-\x08\x0B\x0C\x0E-\x1F\x7F]/g, '').trim();
  if (sanitized.length === 0) {
    throw new Error(`${fieldName} is empty after sanitization`);
  }
  if (sanitized.length > MAX_CONTENT_LEN) {
    throw new Error(`${fieldName} exceeds max length of ${MAX_CONTENT_LEN}`);
  }
  return sanitized;
}

// ── Internal helpers ───────────────────────────────────────────────────────────

function _correctionFilePath(agentType, workspaceRoot) {
  const safe = _sanitizeAgentType(agentType);
  const dir  = path.resolve(workspaceRoot, CORRECTIONS_DIR);
  const file = path.resolve(dir, `${safe}.jsonl`);
  // Confirm resolved path is still inside corrections dir (defense in depth)
  if (!file.startsWith(dir + path.sep) && file !== dir) {
    throw new Error(`Path traversal detected for agentType: ${agentType}`);
  }
  return file;
}

function _ensureDir(workspaceRoot) {
  const dir = path.join(workspaceRoot, CORRECTIONS_DIR);
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
}

function _readAll(agentType, workspaceRoot) {
  const filePath = _correctionFilePath(agentType, workspaceRoot);
  if (!fs.existsSync(filePath)) return [];
  let raw;
  try { raw = fs.readFileSync(filePath, 'utf8'); }
  catch (err) { console.error(`correction-tracker: read error: ${err.message}`); return []; }

  const entries = [];
  for (const line of raw.split('\n')) {
    const trimmed = line.trim();
    if (!trimmed) continue;
    try { entries.push(JSON.parse(trimmed)); } catch (_) {}
  }
  return entries;
}

function _writeAll(agentType, workspaceRoot, entries) {
  _ensureDir(workspaceRoot);
  const filePath = _correctionFilePath(agentType, workspaceRoot);
  const tmpPath  = filePath + '.tmp';
  const data = entries.map(e => JSON.stringify(e)).join('\n') + (entries.length > 0 ? '\n' : '');
  fs.writeFileSync(tmpPath, data, 'utf8');
  fs.renameSync(tmpPath, filePath);
}

// ── Public API ─────────────────────────────────────────────────────────────────

/**
 * Log a correction for an agent type.
 *
 * @param {string} agentType - e.g. 'CoderAgent', 'AuthorAgent', 'general'
 * @param {string} issue - Brief description of what was wrong
 * @param {string} correction - What the correct behavior should be
 * @param {string} workspaceRoot - Absolute path to workspace root
 * @param {{ session_channel?: string }} [opts]
 * @returns {{ ts: string, issue: string, correction: string, session_channel: string, applied_count: number }}
 *
 * @example
 * logCorrection('CoderAgent', 'Used ESM imports', 'Always use require() for stdlib', workspaceRoot);
 */
function logCorrection(agentType, issue, correction, workspaceRoot, opts = {}) {
  if (!workspaceRoot) throw new Error('logCorrection: workspaceRoot is required');

  const entry = {
    ts:              new Date().toISOString(),
    issue:           _sanitizeContent(issue, 'issue'),
    correction:      _sanitizeContent(correction, 'correction'),
    session_channel: _sanitizeContent(opts.session_channel || 'unknown', 'session_channel'),
    applied_count:   0
  };

  const existing = _readAll(agentType, workspaceRoot);
  existing.push(entry);
  _writeAll(agentType, workspaceRoot, existing);

  return entry;
}

/**
 * Return the most recent N corrections for an agent type.
 *
 * @param {string} agentType
 * @param {string} workspaceRoot
 * @param {number} [limit=5] - Max entries to return (most recent first)
 * @returns {Array<{ ts: string, issue: string, correction: string, session_channel: string, applied_count: number }>}
 */
function getCorrections(agentType, workspaceRoot, limit = 5) {
  if (!workspaceRoot) throw new Error('getCorrections: workspaceRoot is required');
  agentType = _sanitizeAgentType(agentType);

  const all = _readAll(agentType, workspaceRoot);
  if (all.length === 0) return [];

  return all.slice().sort((a, b) => new Date(b.ts) - new Date(a.ts)).slice(0, limit);
}

/**
 * Build a correction preamble string for prepending to agent spawn prompts.
 * Only includes corrections from the last 30 days. Returns '' if none.
 *
 * @param {string} agentType
 * @param {string} workspaceRoot
 * @returns {string} Formatted markdown block, or empty string
 *
 * @example
 * const preamble = buildCorrectionPreamble('CoderAgent', workspaceRoot);
 * const fullTask = preamble ? preamble + '\n\n---\n\n' + task : task;
 */
function buildCorrectionPreamble(agentType, workspaceRoot) {
  if (!workspaceRoot) throw new Error('buildCorrectionPreamble: workspaceRoot is required');
  agentType = _sanitizeAgentType(agentType);

  const cutoff = new Date(Date.now() - THIRTY_DAYS_MS);
  const recent = _readAll(agentType, workspaceRoot)
    .filter(e => new Date(e.ts) >= cutoff)
    .sort((a, b) => new Date(b.ts) - new Date(a.ts));

  if (recent.length === 0) return '';

  const lines = recent.map((e, i) => {
    const date = new Date(e.ts).toISOString().slice(0, 10);
    return `${i + 1}. **[${date}] Issue:** ${e.issue}\n   **Correction:** ${e.correction}`;
  });

  return `## Corrections from Previous Sessions\n\nThe following corrections were logged for ${agentType}. Apply these behaviors:\n\n${lines.join('\n\n')}\n`;
}

/**
 * Increment applied_count for a specific correction entry by timestamp.
 * Use to track how often corrections are actually applied.
 *
 * @param {string} agentType
 * @param {string} ts - ISO timestamp of the entry
 * @param {string} workspaceRoot
 * @returns {boolean} true if found and updated, false otherwise
 */
function markApplied(agentType, ts, workspaceRoot) {
  if (!ts)           throw new Error('markApplied: ts is required');
  if (!workspaceRoot) throw new Error('markApplied: workspaceRoot is required');
  agentType = _sanitizeAgentType(agentType);

  const entries = _readAll(agentType, workspaceRoot);
  const idx     = entries.findIndex(e => e.ts === ts);
  if (idx === -1) return false;

  entries[idx] = { ...entries[idx], applied_count: (entries[idx].applied_count || 0) + 1 };
  _writeAll(agentType, workspaceRoot, entries);
  return true;
}

module.exports = { logCorrection, getCorrections, buildCorrectionPreamble, markApplied };

// ── Smoke test ────────────────────────────────────────────────────────────────
if (require.main === module) {
  const os    = require('os');
  const tmpWs = fs.mkdtempSync(path.join(os.tmpdir(), 'correction-tracker-test-'));
  console.log('=== correction-tracker smoke test ===');
  console.log('tmp workspace:', tmpWs);

  try {
    // 1. Log corrections
    const e1 = logCorrection('CoderAgent', 'Used ESM imports', 'Always use require() for stdlib', tmpWs, { session_channel: 'discord' });
    console.log('✓ logCorrection e1:', e1.ts);

    const e2 = logCorrection('CoderAgent', 'Missing smoke test', 'Every module must include smoke test block', tmpWs);
    console.log('✓ logCorrection e2:', e2.ts);

    logCorrection('AuthorAgent', 'Chapter ended mid-scene', 'Always close a scene before ending a chapter', tmpWs);
    console.log('✓ logCorrection AuthorAgent');

    // 2. getCorrections
    const corrections = getCorrections('CoderAgent', tmpWs, 5);
    console.assert(corrections.length === 2, 'should have 2 CoderAgent corrections');
    console.log(`✓ getCorrections: ${corrections.length} entries`);

    // 3. Unknown agent returns []
    const none = getCorrections('UnknownAgent', tmpWs);
    console.assert(none.length === 0, 'unknown agent should return []');
    console.log('✓ unknown agent returns []');

    // 4. buildCorrectionPreamble
    const preamble = buildCorrectionPreamble('CoderAgent', tmpWs);
    console.assert(preamble.includes('Corrections from Previous Sessions'), 'preamble header');
    console.assert(preamble.includes('ESM imports'), 'correction content present');
    console.log('✓ buildCorrectionPreamble:', preamble.length, 'chars');

    // 5. Empty preamble for unknown agent
    const empty = buildCorrectionPreamble('UnknownAgent', tmpWs);
    console.assert(empty === '', 'unknown agent preamble should be empty');
    console.log('✓ empty preamble for unknown agent');

    // 6. markApplied
    const marked = markApplied('CoderAgent', e1.ts, tmpWs);
    console.assert(marked === true, 'markApplied should return true');
    const updated = getCorrections('CoderAgent', tmpWs, 5).find(c => c.ts === e1.ts);
    console.assert(updated?.applied_count === 1, 'applied_count should be 1');
    console.log('✓ markApplied:', updated?.applied_count);

    // 7. markApplied on nonexistent ts returns false
    const notFound = markApplied('CoderAgent', '1970-01-01T00:00:00.000Z', tmpWs);
    console.assert(notFound === false, 'should return false for unknown ts');
    console.log('✓ markApplied false for unknown ts');

    // 8. Error on missing agentType
    try { logCorrection('', 'x', 'y', tmpWs); console.error('✗ Should throw'); }
    catch (e) { console.log('✓ throws on empty agentType:', e.message); }

    console.log('\n✓ All tests passed');
  } finally {
    fs.rmSync(tmpWs, { recursive: true, force: true });
  }
}
