#!/usr/bin/env node
/**
 * wire-rule-to-docs.js
 *
 * Appends a rule entry to the appropriate governance file (default: TOOLS.md).
 * Uses the template for consistent formatting.
 *
 * Input (via env):
 *   RULE_NAME        - Short slug / display name for the rule
 *   RULE_DESCRIPTION - Plain-language rule description
 *   RULE_TYPE        - "HARD" or "soft" (default: HARD)
 *   HAS_LOBSTER      - "true"/"false" — whether a Lobster workflow was created
 *   LOBSTER_PATH     - Path to the Lobster workflow (if HAS_LOBSTER=true)
 *   TARGET_FILE      - Override destination file (optional)
 *   BASE_DIR         - Base directory of the skill
 *
 * Output (stdout JSON):
 *   {
 *     location: string,  // file path where rule was appended
 *     section: string,   // section header used
 *     entry: string      // the text that was appended
 *   }
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

const ruleName = process.env.RULE_NAME || '';
const ruleDescription = process.env.RULE_DESCRIPTION || '';
const ruleType = (process.env.RULE_TYPE || 'HARD').toUpperCase() === 'HARD' ? 'HARD' : 'soft';
const hasLobster = process.env.HAS_LOBSTER === 'true';
const lobsterPath = process.env.LOBSTER_PATH || '';
const targetFileOverride = process.env.TARGET_FILE || '';
const baseDir = process.env.BASE_DIR || path.join(os.homedir(), 'clawd/skills/rule-creation');

if (!ruleName || !ruleDescription) {
  console.error('RULE_NAME and RULE_DESCRIPTION are required');
  process.exit(1);
}

const clawd = path.join(os.homedir(), 'clawd');

// Auto-detect target file from rule content if not overridden
function detectTargetFile(name, description) {
  const text = `${name} ${description}`.toLowerCase();

  if (text.includes('identity') || text.includes('persona') || text.includes('voice') || text.includes('tone')) {
    return path.join(clawd, 'SOUL.md');
  }
  if (text.includes('customer') || text.includes('external message') || text.includes('outbound')) {
    const agentsCustomers = path.join(clawd, 'agents', 'customers.md');
    if (fs.existsSync(agentsCustomers)) return agentsCustomers;
  }
  if (text.includes('project') || text.includes('okr') || text.includes('task board')) {
    const agentsProjects = path.join(clawd, 'agents', 'projects.md');
    if (fs.existsSync(agentsProjects)) return agentsProjects;
  }
  // Default: TOOLS.md
  return path.join(clawd, 'TOOLS.md');
}

const targetFile = targetFileOverride || detectTargetFile(ruleName, ruleDescription);

// Read template
const templatePath = path.join(baseDir, 'templates', 'tools-md-entry.template.md');
let template;
try {
  template = fs.readFileSync(templatePath, 'utf8');
} catch (e) {
  // Fallback inline template
  template = `\n## {{RULE_NAME}} ({{RULE_TYPE}})\n\n{{RULE_DESCRIPTION}}\n{{LOBSTER_LINE}}\n`;
}

// Build lobster pointer line
const lobsterLine = hasLobster && lobsterPath
  ? `\n**Enforced by:** \`${lobsterPath}\``
  : '';

// Fill template
const now = new Date().toISOString().split('T')[0];
const entry = template
  .replace(/\{\{RULE_NAME\}\}/g, ruleName)
  .replace(/\{\{RULE_TYPE\}\}/g, ruleType)
  .replace(/\{\{RULE_DESCRIPTION\}\}/g, ruleDescription)
  .replace(/\{\{LOBSTER_LINE\}\}/g, lobsterLine)
  .replace(/\{\{DATE\}\}/g, now);

// Read existing file content
let existing = '';
try {
  existing = fs.readFileSync(targetFile, 'utf8');
} catch (e) {
  // File doesn't exist yet — will create it
  existing = `# ${path.basename(targetFile, '.md')}\n`;
}

// Check if rule already exists (idempotent)
const ruleHeader = `## ${ruleName}`;
if (existing.includes(ruleHeader)) {
  const result = {
    location: targetFile,
    section: ruleHeader,
    entry: entry.trim(),
    skipped: true,
    reason: `Rule "${ruleName}" already exists in ${targetFile} — skipped to avoid duplicate`
  };
  process.stdout.write(JSON.stringify(result, null, 2) + '\n');
  process.exit(0);
}

// Append entry
const newContent = existing.trimEnd() + '\n\n' + entry.trim() + '\n';
fs.writeFileSync(targetFile, newContent, 'utf8');

const result = {
  location: targetFile,
  section: ruleHeader,
  entry: entry.trim(),
  skipped: false
};

process.stdout.write(JSON.stringify(result, null, 2) + '\n');
process.exit(0);
