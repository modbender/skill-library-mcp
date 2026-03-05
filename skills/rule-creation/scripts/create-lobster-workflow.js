#!/usr/bin/env node
/**
 * create-lobster-workflow.js
 *
 * Creates a Lobster enforcement workflow for a rule from the template.
 *
 * Performs a Lobster availability preflight (via check-lobster-available.js)
 * before writing any files. If Lobster is unavailable the script exits cleanly
 * with { created: false, available: false } so callers can fall back to a
 * TOOLS.md-only wiring path.
 *
 * Input (via env):
 *   RULE_NAME        - Short slug for the rule (used as filename)
 *   RULE_DESCRIPTION - Plain-language rule description
 *   BASE_DIR         - Base directory of the skill (for template path)
 *
 * Output (stdout JSON):
 *   {
 *     path:      string|null, // path to created workflow file, or null
 *     created:   boolean,
 *     available: boolean,     // false when Lobster preflight fails
 *     reason:    string       // human-readable explanation when available=false
 *   }
 */

'use strict';

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');

const ruleName = process.env.RULE_NAME || '';
const ruleDescription = process.env.RULE_DESCRIPTION || '';
const baseDir = process.env.BASE_DIR || path.join(os.homedir(), 'clawd/skills/rule-creation');

if (!ruleName) {
  console.error('RULE_NAME is required');
  process.exit(1);
}

// ── Lobster availability preflight ──────────────────────────────────────────
const checkScript = path.join(baseDir, 'scripts', 'check-lobster-available.js');
let lobsterAvailable = true;
let lobsterUnavailableReason = '';

try {
  const checkResult = JSON.parse(
    execSync(`node "${checkScript}"`, { encoding: 'utf8', timeout: 15_000 })
  );
  lobsterAvailable = checkResult.available;
  lobsterUnavailableReason = checkResult.reason;
} catch (e) {
  lobsterAvailable = false;
  lobsterUnavailableReason = `check-lobster-available.js error: ${e.message}`;
}

if (!lobsterAvailable) {
  const result = {
    path: null,
    created: false,
    available: false,
    reason: lobsterUnavailableReason
  };
  process.stdout.write(JSON.stringify(result, null, 2) + '\n');
  process.exit(0);
}
// ─────────────────────────────────────────────────────────────────────────────

// Normalize rule name to kebab-case slug
const slug = ruleName.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');

const templatePath = path.join(baseDir, 'templates', 'lobster-workflow.template.lobster');
const outputPath = path.join(baseDir, 'workflows', `${slug}.lobster`);

// Read template
let template;
try {
  template = fs.readFileSync(templatePath, 'utf8');
} catch (e) {
  // Fallback inline template if file doesn't exist yet
  template = `name: {{RULE_SLUG}}
description: >
  Enforcement workflow for: {{RULE_DESCRIPTION}}

args:
  context:
    required: false
    description: "Optional context about the current action being checked"

steps:
  - id: check
    description: "Verify compliance with {{RULE_NAME}}"
    command: |
      echo "Checking compliance for rule: {{RULE_NAME}}"
      echo "Rule: {{RULE_DESCRIPTION}}"

  - id: gate
    description: "Gate — block non-compliant actions"
    command: |
      echo "GATE: If the action violates '{{RULE_NAME}}', halt and report."
      echo "Required: {{RULE_DESCRIPTION}}"

  - id: report
    description: "Report compliance status"
    command: |
      echo "Rule check complete: {{RULE_NAME}}"
`;
}

// Fill template
const filled = template
  .replace(/\{\{RULE_SLUG\}\}/g, slug)
  .replace(/\{\{RULE_NAME\}\}/g, ruleName)
  .replace(/\{\{RULE_DESCRIPTION\}\}/g, ruleDescription);

// Ensure workflows dir exists
const workflowsDir = path.dirname(outputPath);
if (!fs.existsSync(workflowsDir)) {
  fs.mkdirSync(workflowsDir, { recursive: true });
}

// Write workflow
fs.writeFileSync(outputPath, filled, 'utf8');

const result = {
  path: outputPath,
  created: true,
  available: true,
  slug
};

process.stdout.write(JSON.stringify(result, null, 2) + '\n');
process.exit(0);
