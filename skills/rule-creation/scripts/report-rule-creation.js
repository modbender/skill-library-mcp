#!/usr/bin/env node
/**
 * report-rule-creation.js
 *
 * Generates a user-facing summary of rule creation results.
 *
 * Input (via env):
 *   RULE_NAME          - Rule name/slug
 *   RULE_TYPE          - HARD or soft
 *   WIRED_TO           - File path where rule was wired
 *   WIRE_SECTION       - Section header in that file
 *   HAS_ENFORCEMENT    - "true"/"false"
 *   ENFORCEMENT_REASON - Why enforcement was or wasn't applied
 *   LOBSTER_PATH       - Path to Lobster workflow (if created)
 *   CRITERIA           - JSON array of matched CR-012 criteria
 *
 * Output (stdout): Human-readable summary + JSON block for structured parsing
 */

const ruleName = process.env.RULE_NAME || '(unknown)';
const ruleType = process.env.RULE_TYPE || 'HARD';
const wiredTo = process.env.WIRED_TO || '(unknown)';
const wireSection = process.env.WIRE_SECTION || '';
const hasEnforcement = process.env.HAS_ENFORCEMENT === 'true';
const enforcementReason = process.env.ENFORCEMENT_REASON || '';
const lobsterPath = process.env.LOBSTER_PATH || '';
// LOBSTER_AVAILABLE defaults to true for backwards-compat; explicitly 'false' = unavailable
const lobsterAvailable = process.env.LOBSTER_AVAILABLE !== 'false';

let criteria = [];
try {
  const raw = process.env.CRITERIA || '[]';
  criteria = JSON.parse(raw);
} catch (e) {
  // ignore parse errors
}

// Build human-readable summary
const lines = [
  '─────────────────────────────────────────',
  '  Rule Creation Complete',
  '─────────────────────────────────────────',
  `  ✅ Rule wired:    ${ruleName}`,
  `  📋 Type:          ${ruleType}`,
  `  📄 Location:      ${wiredTo}`,
];

if (wireSection) {
  lines.push(`  📌 Section:       ${wireSection}`);
}

if (hasEnforcement && lobsterPath && lobsterAvailable) {
  lines.push(`  🔒 Enforcement:   ${lobsterPath}`);
  if (criteria.length > 0) {
    lines.push(`  📊 CR-012 match:  ${criteria.join(', ')}`);
  }
} else if (hasEnforcement && !lobsterAvailable) {
  lines.push(`  ⚠️  Enforcement:   unavailable (Lobster not enabled)`);
  lines.push(`  💡 To enable:     openclaw plugins enable lobster`);
  lines.push(`  📄 Fallback:      TOOLS.md entry wired; no .lobster workflow created`);
} else {
  lines.push(`  🔓 Enforcement:   None (TOOLS.md entry sufficient)`);
}

if (enforcementReason) {
  lines.push(`  💬 Reason:        ${enforcementReason}`);
}

lines.push('─────────────────────────────────────────');

// Structured result for downstream parsing
const structured = {
  ruleName,
  ruleType,
  wiredTo,
  wireSection,
  hasEnforcement,
  lobsterAvailable,
  lobsterPath: (hasEnforcement && lobsterAvailable) ? lobsterPath : null,
  criteria,
  enforcementReason
};

lines.push('');
lines.push('JSON:');
lines.push(JSON.stringify(structured, null, 2));

process.stdout.write(lines.join('\n') + '\n');
process.exit(0);
