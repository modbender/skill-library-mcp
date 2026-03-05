'use strict';
/**
 * agent-context-loader.js
 *
 * Pre-loads relevant context for subagent spawns.
 * Queries INTENT.md, episodic memory, and recent routing decisions.
 * Prepends a compact context block to spawn task descriptions.
 * Also injects correction preamble (if correction-tracker is installed).
 *
 * Installation: copy to $OPENCLAW_WORKSPACE/lib/agent-context-loader.js
 *
 * Usage:
 *   const { prepareAgentContext } = require('./lib/agent-context-loader');
 *   const { context } = prepareAgentContext('code_review', workspaceRoot);
 *   const fullTask = context ? context + '\n\n---\n\n' + originalTask : originalTask;
 *
 * @module lib/agent-context-loader
 */

const fs   = require('fs');
const path = require('path');

// ── Correction preamble ────────────────────────────────────────────────────────

/**
 * Detect agent type from a task type string.
 * Extend this map to add custom agent types.
 *
 * @param {string} taskType
 * @returns {string} Agent type label (used to load corrections file)
 */
function detectAgentType(taskType) {
  const lower = taskType.toLowerCase();
  if (/code|coder|impl|debug/.test(lower))  return 'CoderAgent';
  if (/writ|author|novel|chapter/.test(lower)) return 'AuthorAgent';
  if (/world|build/.test(lower))            return 'WorldbuilderAgent';
  return 'general';
}

/**
 * Load correction preamble from correction-tracker (if installed).
 * Returns empty string if correction-tracker is not installed. Never throws.
 *
 * @param {string} taskType
 * @param {string} workspaceRoot
 * @returns {string}
 */
function loadCorrectionPreamble(taskType, workspaceRoot) {
  try {
    const trackerPath = path.join(workspaceRoot, 'lib', 'correction-tracker.js');
    let tracker;
    try { tracker = require(trackerPath); } catch (_) { return ''; }
    if (typeof tracker.buildCorrectionPreamble !== 'function') return '';
    const agentType = detectAgentType(taskType);
    return tracker.buildCorrectionPreamble(agentType, workspaceRoot) || '';
  } catch (_) {
    return '';
  }
}

// ── Intent summary ─────────────────────────────────────────────────────────────

/** Fallback if INTENT.md is missing. */
const INTENT_FALLBACK =
  '## Intent\n' +
  'Optimize for: user_value > honesty > cost. Never sacrifice: honesty, safety, user_autonomy.\n' +
  'Delegate when blocking chat. Prefer depth for architecture/writing. Quality over speed.';

/**
 * Read INTENT.md and return a compact (≤200 char) summary for injection.
 * Falls back to a safe default if missing. Never throws.
 *
 * @param {string} workspaceRoot
 * @returns {string}
 */
function getIntentSummary(workspaceRoot) {
  try {
    const intentPath = path.join(workspaceRoot, 'INTENT.md');
    const raw = fs.readFileSync(intentPath, 'utf8');

    const primary       = (raw.match(/primary:\s*(\S+)/)             || [])[1] || 'user_value_delivery';
    const secondary     = (raw.match(/secondary:\s*(\S+)/)           || [])[1] || 'honesty_and_accuracy';
    const tertiary      = (raw.match(/tertiary:\s*(\S+)/)            || [])[1] || 'cost_efficiency';
    const neverSacrifice = (raw.match(/never_sacrifice:\s*\[(.+?)\]/) || [])[1] || 'honesty, safety, user_autonomy';
    const delegate      = (raw.match(/delegate_vs_inline:\s*(\S+)/)  || [])[1] || 'delegate_when_blocking_chat';
    const depth         = (raw.match(/speed_vs_depth:\s*(\S+)/)      || [])[1] || 'prefer_depth_for_architecture';

    const summary =
      '## Intent\n' +
      `Optimize for: ${primary} > ${secondary} > ${tertiary}. ` +
      `Never sacrifice: ${neverSacrifice}.\n` +
      `${delegate.includes('delegate') ? 'Delegate when blocking chat.' : delegate} ` +
      `${depth.includes('depth') ? 'Prefer depth for architecture/writing.' : depth} Quality over speed.`;

    const lines = summary.split('\n');
    const body  = lines.slice(1).join('\n');
    const trimmedBody = body.length > 170 ? body.slice(0, 167) + '...' : body;
    return lines[0] + '\n' + trimmedBody;
  } catch (_) {
    return INTENT_FALLBACK;
  }
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function safeReadLines(filePath) {
  try { return fs.readFileSync(filePath, 'utf8').split('\n'); } catch (_) { return []; }
}

function keywordsFrom(taskType) {
  return taskType.toLowerCase().split(/[\s_\-]+/).filter(w => w.length > 2);
}

function matchesKeywords(text, keywords) {
  const lower = text.toLowerCase();
  return keywords.some(kw => lower.includes(kw));
}

// ── Schema normalization ───────────────────────────────────────────────────────

/**
 * Normalize a routing-decisions.log entry to { task_type, target, timestamp }.
 * Handles both nested (current) and flat (legacy) log schemas.
 *
 * @param {Object} entry
 * @returns {{ task_type: string, target: string, timestamp: string }}
 */
function normalizeEntry(entry) {
  const task_type =
    (entry.decision && entry.decision.classification && entry.decision.classification.type) ||
    entry.task_type || entry.type || 'unknown';
  const target =
    (entry.decision && entry.decision.target) ||
    entry.target || entry.route || entry.decision_target || 'unknown';
  const timestamp = entry.timestamp || entry.ts || '';
  return { task_type, target, timestamp };
}

// ── Context queries ────────────────────────────────────────────────────────────

/**
 * Find recent episodic memory entries matching taskType keywords.
 *
 * @param {string} taskType
 * @param {string} workspaceRoot
 * @param {number} [limit=3]
 * @returns {{ file: string, snippet: string }[]}
 */
function getRecentEpisodicEntries(taskType, workspaceRoot, limit = 3) {
  const episodicDir = path.join(workspaceRoot, 'memory', 'episodic');
  const keywords    = keywordsFrom(taskType);
  const results     = [];

  let files = [];
  try {
    files = fs.readdirSync(episodicDir)
      .filter(f => f.endsWith('.md'))
      .map(f => ({
        name: f,
        fullPath: path.join(episodicDir, f),
        mtime: (() => { try { return fs.statSync(path.join(episodicDir, f)).mtimeMs; } catch (_) { return 0; } })()
      }))
      .sort((a, b) => b.mtime - a.mtime);
  } catch (_) { return []; }

  for (const file of files) {
    if (results.length >= limit) break;
    const lines   = safeReadLines(file.fullPath);
    const content = lines.join('\n');
    if (matchesKeywords(content, keywords)) {
      const snippet = lines.find(l => l.trim().length > 0) || '';
      results.push({ file: file.name, snippet: snippet.trim().slice(0, 100) });
    }
  }
  return results;
}

/**
 * Find recent routing decisions matching taskType keywords.
 *
 * @param {string} taskType
 * @param {string} workspaceRoot
 * @param {number} [limit=3]
 * @returns {{ task_type: string, target: string, timestamp: string }[]}
 */
function getRecentRoutingDecisions(taskType, workspaceRoot, limit = 3) {
  const logPath = path.join(workspaceRoot, 'memory', 'routing-decisions.log');
  const keywords = keywordsFrom(taskType);
  const lines    = safeReadLines(logPath);
  const recent   = lines.filter(l => l.trim().length > 0).slice(-20).reverse();

  const results = [];
  for (const line of recent) {
    if (results.length >= limit) break;
    try {
      const raw   = JSON.parse(line);
      const entry = normalizeEntry(raw);
      const searchText = [entry.task_type, raw.task, raw.label].filter(Boolean).join(' ');
      if (matchesKeywords(searchText, keywords)) results.push(entry);
    } catch (_) {}
  }
  return results;
}

// ── Primary export ─────────────────────────────────────────────────────────────

/**
 * Prepare a context block to prepend to subagent spawn task descriptions.
 *
 * Always includes: INTENT.md summary + correction preamble (if available).
 * Optionally includes: relevant episodic memory, recent routing decisions,
 * active phase summary.
 *
 * @param {string} taskType - Task type string (e.g. "code_review", "research")
 * @param {string} workspaceRoot - Absolute path to workspace root
 * @returns {{ context: string, intent_propagated: boolean }}
 *
 * @example
 * const { context } = prepareAgentContext('code_review', '/path/to/workspace');
 * const fullTask = context + '\n\n' + originalTaskDescription;
 */
function prepareAgentContext(taskType, workspaceRoot) {
  try {
    const parts = [];

    // Always inject intent summary
    parts.push(getIntentSummary(workspaceRoot));

    // Inject correction preamble if correction-tracker is installed
    const correctionBlock = loadCorrectionPreamble(taskType, workspaceRoot);
    if (correctionBlock) parts.push(correctionBlock);

    const episodic = getRecentEpisodicEntries(taskType, workspaceRoot, 3);
    const routing  = getRecentRoutingDecisions(taskType, workspaceRoot, 3);

    if (episodic.length > 0 || routing.length > 0) {
      parts.push('\n## Relevant Context');
      parts.push('> Refer to INTENT.md for optimization priorities.\n');

      if (episodic.length > 0) {
        parts.push('**Recent episodic memory:**');
        for (const e of episodic) parts.push(`- ${e.file}: ${e.snippet}`);
      }

      if (routing.length > 0) {
        parts.push('**Recent routing decisions:**');
        for (const r of routing) parts.push(`- ${r.task_type} → ${r.target} (${r.timestamp})`);
      }
    }

    const block   = parts.join('\n');
    const context = block.length <= 700 ? block : block.slice(0, 697) + '...';
    return { context, intent_propagated: true };
  } catch (_) {
    return { context: '', intent_propagated: true };
  }
}

module.exports = {
  prepareAgentContext,
  getRecentEpisodicEntries,
  getRecentRoutingDecisions,
  getIntentSummary,
  normalizeEntry,
  detectAgentType,
  loadCorrectionPreamble
};

// ── Smoke test ────────────────────────────────────────────────────────────────
if (require.main === module) {
  const WS = process.argv[2] || process.env.OPENCLAW_WORKSPACE || process.cwd();
  console.log('=== agent-context-loader smoke test ===');
  console.log('workspace:', WS);

  const intent = getIntentSummary(WS);
  console.log('\nIntent summary:');
  console.log(intent);
  console.assert(typeof intent === 'string' && intent.length > 0, 'intent must be non-empty string');

  const result = prepareAgentContext('code_review', WS);
  console.log('\nprepareAgentContext:');
  console.log('  intent_propagated:', result.intent_propagated);
  console.log('  context length:', result.context.length);
  console.assert(result.intent_propagated === true, 'intent_propagated must be true');
  console.assert(typeof result.context === 'string', 'context must be string');

  console.log('\n✓ Smoke test passed');
}
