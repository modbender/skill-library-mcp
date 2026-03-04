#!/usr/bin/env node
/**
 * observe.js — Manual observation recorder.
 * Use this when you want to record a significant event that the PostToolUse
 * hook may not capture (e.g., a reasoning error, a wrong assumption).
 *
 * Usage:
 *   node observe.js --manual \
 *     --type error|correction|preference \
 *     --tool "ToolName" \
 *     --pattern "brief description" \
 *     --context "what you were doing"
 */
'use strict';

const fs = require('fs');
const path = require('path');

const REFLECT_DIR = path.join(process.cwd(), '.reflect');
const OUTCOMES_FILE = path.join(REFLECT_DIR, 'outcomes.jsonl');

function parseArgs() {
  const args = process.argv.slice(2);
  const result = { manual: false, type: 'error', tool: 'manual', pattern: null, context: null };
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--manual') result.manual = true;
    if (args[i] === '--type') result.type = args[++i];
    if (args[i] === '--tool') result.tool = args[++i];
    if (args[i] === '--pattern') result.pattern = args[++i];
    if (args[i] === '--context') result.context = args[++i];
  }
  return result;
}

function main() {
  const args = parseArgs();

  if (!args.pattern) {
    process.stderr.write('--pattern is required\n');
    process.exit(1);
  }

  if (!fs.existsSync(REFLECT_DIR)) fs.mkdirSync(REFLECT_DIR, { recursive: true });

  const event = {
    ts: new Date().toISOString(),
    session: process.env.CLAUDE_SESSION_ID || 'manual',
    tool: args.tool,
    outcome: args.type,
    exit_code: args.type === 'error' ? 1 : 0,
    error_pattern: args.pattern,
    input_summary: args.context || null,
    source: 'manual',
  };

  fs.appendFileSync(OUTCOMES_FILE, JSON.stringify(event) + '\n', 'utf8');
  process.stdout.write(`recorded: ${args.type} on ${args.tool} — "${args.pattern}"`);
}

main();
