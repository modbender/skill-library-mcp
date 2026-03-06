'use strict';
/**
 * failure-tracer.js
 *
 * Captures failure traces when subagent quality scores are below threshold.
 * Writes structured JSON to memory/traces/ for post-mortem analysis.
 *
 * Installation: copy to $OPENCLAW_WORKSPACE/lib/failure-tracer.js
 *
 * Usage:
 *   const { captureFailureTrace } = require('./lib/failure-tracer');
 *   if (qualityScore < 7) {
 *     captureFailureTrace('AgentLabel', qualityScore, agentOutput, workspaceRoot);
 *   }
 *
 * @module lib/failure-tracer
 */

const fs   = require('fs');
const path = require('path');

const TRACES_DIR        = 'memory/traces';
const FAILURE_THRESHOLD = 7;

/**
 * Extract tool call sequence hints from output text.
 * Looks for common tool invocation patterns.
 *
 * @param {string} text
 * @returns {string[]}
 */
function extractToolSequenceHints(text) {
  const hints    = [];
  const patterns = [
    { re: /<tool_use[^>]*>/gi,           label: 'xml-tool-use' },
    { re: /function_call["\s:]+/gi,      label: 'function-call' },
    { re: /"type"\s*:\s*"tool_use"/gi,   label: 'json-tool-use' },
    { re: /\btool\s*:\s*["']?\w+["']?/gi, label: 'tool-field' },
    { re: /actions?\s*:\s*\[/gi,         label: 'actions-array' },
    { re: /exec\s*\(/gi,                 label: 'exec-call' },
    { re: /browser\s*\(/gi,              label: 'browser-call' },
    { re: /web_search\s*\(/gi,           label: 'web-search-call' }
  ];

  for (const { re, label } of patterns) {
    const matches = text.match(re);
    if (matches && matches.length > 0) hints.push(`${label}(${matches.length}x)`);
  }

  const fnNames = text.match(/(?:function_name|tool_name)["\s:]+["']?(\w+)["']?/gi);
  if (fnNames) {
    fnNames.slice(0, 5).forEach(m => {
      const name = m.replace(/.*["'\s:]/, '').trim();
      if (name) hints.push(`fn:${name}`);
    });
  }
  return hints;
}

function dateStamp(date) {
  const d   = date || new Date();
  const pad = n => String(n).padStart(2, '0');
  return `${d.getFullYear()}${pad(d.getMonth() + 1)}${pad(d.getDate())}-${pad(d.getHours())}${pad(d.getMinutes())}`;
}

function inferFailureReason(text, score) {
  if (score < 3)                                              return 'critical_quality_failure';
  if (text.length < 100)                                     return 'output_too_short';
  if (/error|exception|failed|crash/i.test(text.slice(0, 200))) return 'error_in_output';
  if (!/\S/.test(text))                                      return 'empty_output';
  return 'below_quality_threshold';
}

/**
 * Capture a failure trace when a subagent output scores below threshold.
 * Creates memory/traces/ if needed. Atomic write. Never throws.
 *
 * @param {string} label - Subagent label or task identifier
 * @param {number} score - Quality score (0–10)
 * @param {string|Object} output - Subagent output
 * @param {string} workspaceRoot - Workspace root path
 * @returns {{ captured: boolean, tracePath?: string, skipped?: boolean, error?: string }}
 */
function captureFailureTrace(label, score, output, workspaceRoot) {
  try {
    if (score >= FAILURE_THRESHOLD) return { captured: false, skipped: true, reason: 'score_above_threshold' };

    const root        = workspaceRoot || process.env.OPENCLAW_WORKSPACE || process.cwd();
    const text        = typeof output === 'string' ? output : JSON.stringify(output);
    const ts          = new Date();
    const safePart    = (label || 'unknown').replace(/[^a-zA-Z0-9_-]/g, '_').slice(0, 40);
    const filename    = `${safePart}-${dateStamp(ts)}.json`;
    const tracesDir   = path.join(root, TRACES_DIR);
    const tracePath   = path.join(tracesDir, filename);

    const trace = {
      ts:                  ts.toISOString(),
      label,
      score,
      failure_threshold:   FAILURE_THRESHOLD,
      tool_sequence_hints: extractToolSequenceHints(text),
      output_snippet:      text.slice(0, 500),
      failure_reason:      inferFailureReason(text, score)
    };

    const tmpPath = tracePath + '.tmp.' + process.pid;
    try {
      fs.mkdirSync(tracesDir, { recursive: true });
      fs.writeFileSync(tmpPath, JSON.stringify(trace, null, 2), 'utf8');
      fs.renameSync(tmpPath, tracePath);
    } catch (writeErr) {
      try { fs.unlinkSync(tmpPath); } catch (_) {}
      return { captured: false, error: writeErr.message };
    }

    return { captured: true, tracePath };
  } catch (err) {
    return { captured: false, error: err.message };
  }
}

/**
 * List all existing failure traces, newest first.
 *
 * @param {string} workspaceRoot
 * @returns {{ file: string, ts: string, label: string, score: number }[]}
 */
function listFailureTraces(workspaceRoot) {
  const root      = workspaceRoot || process.env.OPENCLAW_WORKSPACE || process.cwd();
  const tracesDir = path.join(root, TRACES_DIR);
  try {
    return fs.readdirSync(tracesDir)
      .filter(f => f.endsWith('.json'))
      .map(f => {
        const fullPath = path.join(tracesDir, f);
        try {
          const data = JSON.parse(fs.readFileSync(fullPath, 'utf8'));
          return { file: f, ts: data.ts, label: data.label, score: data.score };
        } catch (_) {
          return { file: f, ts: null, label: null, score: null };
        }
      })
      .sort((a, b) => (b.ts || '').localeCompare(a.ts || ''));
  } catch (_) { return []; }
}

module.exports = { captureFailureTrace, listFailureTraces, FAILURE_THRESHOLD };

// ── Smoke test ────────────────────────────────────────────────────────────────
if (require.main === module) {
  const os    = require('os');
  const tmpWs = fs.mkdtempSync(path.join(os.tmpdir(), 'failure-tracer-test-'));
  console.log('=== failure-tracer smoke test ===');

  const skipped = captureFailureTrace('GoodAgent', 8.5, 'Great output', tmpWs);
  console.assert(skipped.skipped === true, 'should skip when score >= 7');
  console.log('score 8.5: skipped ✓');

  const badOutput = 'function_call: {"type":"tool_use"} ERROR: timeout after 30s';
  const captured  = captureFailureTrace('ResearchAgent', 4.2, badOutput, tmpWs);
  console.assert(captured.captured === true, 'should capture when score < 7');
  console.assert(captured.tracePath,         'should have tracePath');
  console.log('score 4.2: captured at', captured.tracePath, '✓');

  const traceData = JSON.parse(fs.readFileSync(captured.tracePath, 'utf8'));
  console.assert(traceData.score === 4.2,              'score preserved');
  console.assert(traceData.tool_sequence_hints.length > 0, 'hints extracted');

  const traces = listFailureTraces(tmpWs);
  console.assert(traces.length === 1, 'should have 1 trace');
  console.log('listFailureTraces:', traces.length, 'trace(s) ✓');

  fs.rmSync(tmpWs, { recursive: true });
  console.log('\n✓ Smoke test passed');
}
