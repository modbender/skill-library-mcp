#!/usr/bin/env node
/**
 * hook-observe.js — Claude Code PostToolUse hook for openclaw-reflect.
 *
 * Reads tool result JSON from stdin, extracts error patterns, and
 * appends to outcomes.jsonl for later classification.
 *
 * Claude Code PostToolUse stdin format:
 * {
 *   "session_id": "...",
 *   "tool_name": "Bash" | "Edit" | etc,
 *   "tool_input": { ... },
 *   "tool_response": {
 *     "type": "tool_result",
 *     "content": [{ "type": "text", "text": "..." }],
 *     "is_error": true | false
 *   }
 * }
 */
'use strict';

const fs = require('fs');
const path = require('path');

// Derive workspace from script location: scripts/ → openclaw-reflect/ → skills/ → workspace/
const WORKSPACE_DIR = path.join(__dirname, '..', '..', '..');
const REFLECT_DIR = path.join(WORKSPACE_DIR, '.reflect');
const OUTCOMES_FILE = path.join(REFLECT_DIR, 'outcomes.jsonl');

function extractText(response) {
  if (!response) return '';
  if (typeof response === 'string') return response;
  if (Array.isArray(response.content)) {
    return response.content.map(c => c.text || '').join('\n');
  }
  return JSON.stringify(response).slice(0, 500);
}

function extractErrorPattern(text) {
  if (!text) return null;

  // Match common failure signatures
  const patterns = [
    /error:\s*(.{10,100})/i,
    /exception:\s*(.{10,100})/i,
    /failed[:\s]+(.{10,100})/i,
    /not found[:\s]+(.{10,100})/i,
    /permission denied[:\s]*(.{0,80})/i,
    /cannot\s+(.{10,80})/i,
    /exit code\s+\d+[:\s]*(.{0,80})/i,
    /traceback.*?(\w+error[:\s].{10,80})/is,
  ];

  for (const re of patterns) {
    const m = text.match(re);
    if (m) return m[0].slice(0, 100).replace(/\s+/g, ' ').trim();
  }

  // If output is very short and tool errored, use the whole thing
  if (text.trim().length < 200) return text.trim().replace(/\s+/g, ' ').slice(0, 100);

  return 'generic_error';
}

function main() {
  let raw = '';
  process.stdin.on('data', chunk => raw += chunk);
  process.stdin.on('end', () => {
    let event;
    try { event = JSON.parse(raw); } catch { process.exit(0); }

    const response = event.tool_response || {};
    const isError = response.is_error === true ||
                    (typeof response.exit_code === 'number' && response.exit_code !== 0);

    if (!isError) process.exit(0); // Only record failures

    const text = extractText(response);
    const errorPattern = extractErrorPattern(text);

    if (!errorPattern) process.exit(0);

    if (!fs.existsSync(REFLECT_DIR)) fs.mkdirSync(REFLECT_DIR, { recursive: true });

    const record = {
      ts: new Date().toISOString(),
      session: event.session_id || 'unknown',
      tool: event.tool_name || 'unknown',
      outcome: 'error',
      exit_code: response.exit_code ?? 1,
      error_pattern: errorPattern,
      input_summary: JSON.stringify(event.tool_input || {}).slice(0, 200),
      source: 'hook',
    };

    fs.appendFileSync(OUTCOMES_FILE, JSON.stringify(record) + '\n', 'utf8');
    // Exit 0 — hooks must not block Claude Code
    process.exit(0);
  });
}

main();
