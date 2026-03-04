#!/usr/bin/env node
/**
 * post-tool-use.js — PostToolUse hook for openclaw-reflect.
 * Records tool outcomes to .reflect/outcomes.jsonl.
 * Fires after every tool call. Fast, non-blocking, append-only.
 */
'use strict';

const fs = require('fs');
const path = require('path');
const os = require('os');

const REFLECT_DIR = path.join(process.cwd(), '.reflect');
const OUTCOMES_FILE = path.join(REFLECT_DIR, 'outcomes.jsonl');

function ensureDir() {
  if (!fs.existsSync(REFLECT_DIR)) fs.mkdirSync(REFLECT_DIR, { recursive: true });
}

function classifyOutcome(exitCode, output) {
  if (exitCode === undefined || exitCode === null) return 'unknown';
  const code = parseInt(exitCode, 10);
  if (isNaN(code)) return 'unknown';
  if (code === 0) return 'success';
  if (code === 1) return 'error';
  return 'error';
}

function extractErrorPattern(output) {
  if (!output) return null;
  const lines = output.split('\n').filter(l => l.trim());
  // Look for common error indicators
  const errorLine = lines.find(l =>
    /error|exception|failed|traceback|cannot|denied|not found|timeout/i.test(l)
  );
  if (!errorLine) return null;
  // Normalize: strip file paths and line numbers to get the pattern
  return errorLine
    .replace(/['"]?[A-Za-z]:[\\\/][^'"]+['"]?/g, '<path>')
    .replace(/line \d+/gi, 'line N')
    .replace(/\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/g, '<ts>')
    .trim()
    .slice(0, 200);
}

function main() {
  ensureDir();

  const toolName = process.env.CLAUDE_TOOL_NAME || process.env.TOOL_NAME || 'unknown';
  const exitCode = process.env.CLAUDE_TOOL_EXIT_CODE ?? process.env.TOOL_EXIT_CODE;
  const output = process.env.CLAUDE_TOOL_OUTPUT || process.env.TOOL_OUTPUT || '';
  const input = process.env.CLAUDE_TOOL_INPUT || process.env.TOOL_INPUT || '';
  const sessionId = process.env.CLAUDE_SESSION_ID || 'unknown';

  // Only record non-trivial tool calls
  const ignoredTools = ['TodoRead', 'TodoWrite'];
  if (ignoredTools.includes(toolName)) return;

  const outcome = classifyOutcome(exitCode, output);
  const errorPattern = outcome === 'error' ? extractErrorPattern(output) : null;

  const event = {
    ts: new Date().toISOString(),
    session: sessionId,
    tool: toolName,
    outcome,
    exit_code: exitCode !== undefined ? parseInt(exitCode, 10) : null,
    error_pattern: errorPattern,
    // Capture minimal input context (first 150 chars, no secrets)
    input_summary: typeof input === 'string' ? input.slice(0, 150).replace(/\n/g, ' ') : null,
  };

  try {
    fs.appendFileSync(OUTCOMES_FILE, JSON.stringify(event) + '\n', 'utf8');
  } catch (e) {
    // Silent — never block the tool call
  }
}

main();
