#!/usr/bin/env node
// cc-file-guard/guard.mjs
// PreToolUse hook for Claude Code.
// Blocks destructive edits to protected files.
// - Blocks Write tool on protected files entirely
// - Blocks Edit when net line removal > 2 lines

import { basename } from 'node:path';
import { existsSync } from 'node:fs';

// Exact basename matches
export const PROTECTED = new Set([
  'CLAUDE.md',
  'SHARED-CONTEXT.md',
  'SOUL.md',
  'IDENTITY.md',
  'CONTEXT.md',
  'TOOLS.md',
  'MEMORY.md',
]);

// Pattern matches (case-insensitive, checked against full path and basename)
export const PROTECTED_PATTERNS = [
  /memory/i,
  /memories/i,
  /journal/i,
  /diary/i,
  /daily.*log/i,
];

function isProtected(filePath) {
  const name = basename(filePath);
  if (PROTECTED.has(name)) return name;
  for (const pattern of PROTECTED_PATTERNS) {
    if (pattern.test(filePath)) return name + ` (matched pattern: ${pattern})`;
  }
  return null;
}

function deny(reason) {
  const output = {
    hookSpecificOutput: {
      hookEventName: 'PreToolUse',
      permissionDecision: 'deny',
      permissionDecisionReason: reason,
    },
  };
  process.stdout.write(JSON.stringify(output));
}

function countLines(str) {
  if (!str) return 0;
  return str.split('\n').length;
}

// CLI mode: node guard.mjs --list
if (process.argv.includes('--list')) {
  console.log('Protected files (exact):');
  for (const f of PROTECTED) console.log(`  ${f}`);
  console.log('Protected patterns:');
  for (const p of PROTECTED_PATTERNS) console.log(`  ${p}`);
  process.exit(0);
}

async function main() {
  let raw = '';
  for await (const chunk of process.stdin) {
    raw += chunk;
  }

  let input;
  try {
    input = JSON.parse(raw);
  } catch {
    // Can't parse input, allow by default
    process.exit(0);
  }

  const toolName = input.tool_name || '';
  const toolInput = input.tool_input || {};
  const filePath = toolInput.file_path || toolInput.filePath || '';
  const fileName = basename(filePath);

  // Only check protected files
  const match = isProtected(filePath);
  if (!match) {
    process.exit(0);
  }

  // Block Write on protected files
  // Exact matches: always block Write (use Edit instead)
  // Pattern matches: only block if file already exists (allow creating new files)
  if (toolName === 'Write') {
    const isExactMatch = PROTECTED.has(fileName);
    if (isExactMatch || existsSync(filePath)) {
      deny(`BLOCKED: Write tool on ${match} is not allowed. Use Edit to make specific changes. Never overwrite protected files.`);
      process.exit(0);
    }
    // Pattern match but file doesn't exist yet — allow creation
    process.exit(0);
  }

  // For Edit, check line removal AND large replacements
  if (toolName === 'Edit') {
    const oldString = toolInput.old_string || '';
    const newString = toolInput.new_string || '';
    const oldLines = countLines(oldString);
    const newLines = countLines(newString);
    const removed = oldLines - newLines;

    // Block net removal of more than 2 lines
    if (removed > 2) {
      deny(`BLOCKED: You are removing ${removed} lines from ${match} (old: ${oldLines} lines, new: ${newLines} lines). Re-read the file and add content instead of replacing it.`);
      process.exit(0);
    }

    // Block large replacements (swapping big chunks even if line count is similar)
    if (oldLines > 4 && oldString !== newString) {
      deny(`BLOCKED: You are replacing ${oldLines} lines in ${match}. Edit smaller sections or append new content instead of replacing existing content.`);
      process.exit(0);
    }
  }

  // Allow
  process.exit(0);
}

main().catch(() => process.exit(0));
