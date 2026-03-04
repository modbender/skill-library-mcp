#!/usr/bin/env node
/**
 * guard-scanner CLI
 *
 * @security-manifest
 *   env-read: []
 *   env-write: []
 *   network: none
 *   fs-read: [scan target directory, plugin files, custom rules files]
 *   fs-write: [JSON/SARIF/HTML reports to scan directory]
 *   exec: none
 *   purpose: CLI entry point for guard-scanner static analysis
 *
 * Usage: guard-scanner [scan-dir] [options]
 *
 * Options:
 *   --verbose, -v       Detailed findings
 *   --json              JSON report
 *   --sarif             SARIF report (CI/CD)
 *   --html              HTML report
 *   --self-exclude      Skip scanning self
 *   --strict            Lower thresholds
 *   --summary-only      Summary only
 *   --check-deps        Scan dependencies
 *   --rules <file>      Custom rules JSON
 *   --plugin <file>     Load plugin module
 *   --fail-on-findings  Exit 1 on findings (CI/CD)
 *   --help, -h          Help
 */

const fs = require('fs');
const path = require('path');
const { GuardScanner, VERSION } = require('./scanner.js');

const args = process.argv.slice(2);

if (args.includes('--help') || args.includes('-h')) {
  console.log(`
🛡️  guard-scanner v${VERSION} — Agent Skill Security Scanner

Usage: guard-scanner [scan-dir] [options]

Options:
  --verbose, -v       Detailed findings with categories and samples
  --json              Write JSON report to file
  --sarif             Write SARIF report to file (GitHub Code Scanning / CI/CD)
  --html              Write HTML report (visual dashboard)
  --format json|sarif Print JSON or SARIF to stdout (pipeable, v3.2.0)
  --quiet             Suppress all text output (use with --format for clean pipes)
  --self-exclude      Skip scanning the guard-scanner skill itself
  --strict            Lower detection thresholds (more sensitive)
  --summary-only      Only print the summary table
  --check-deps        Scan package.json for dependency chain risks
  --soul-lock         Enable Soul Lock patterns (agent identity protection)
  --rules <file>      Load custom rules from JSON file
  --plugin <file>     Load plugin module (JS file exporting { name, patterns })
  --fail-on-findings  Exit code 1 if any findings (CI/CD)
  --help, -h          Show this help

Custom Rules JSON Format:
  [
    {
      "id": "CUSTOM_001",
      "pattern": "dangerous_function\\\\(",
      "flags": "gi",
      "severity": "HIGH",
      "cat": "malicious-code",
      "desc": "Custom: dangerous function call",
      "codeOnly": true
    }
  ]

Plugin API:
  // my-plugin.js
  module.exports = {
    name: 'my-plugin',
    patterns: [
      { id: 'MY_01', cat: 'custom', regex: /pattern/g, severity: 'HIGH', desc: 'Description', all: true }
    ]
  };

Examples:
  guard-scanner ./skills/ --verbose --self-exclude
  guard-scanner ./skills/ --strict --json --sarif --check-deps
  guard-scanner ./skills/ --html --verbose --check-deps
  guard-scanner ./skills/ --rules my-rules.json --fail-on-findings
  guard-scanner ./skills/ --plugin ./my-plugin.js
`);
  process.exit(0);
}

const verbose = args.includes('--verbose') || args.includes('-v');
const jsonOutput = args.includes('--json');
const sarifOutput = args.includes('--sarif');
const htmlOutput = args.includes('--html');
const selfExclude = args.includes('--self-exclude');
const strict = args.includes('--strict');
const summaryOnly = args.includes('--summary-only');
const checkDeps = args.includes('--check-deps');
const soulLock = args.includes('--soul-lock');
const failOnFindings = args.includes('--fail-on-findings');
const quietMode = args.includes('--quiet');

// --format json|sarif → stdout output (v3.2.0)
const formatIdx = args.indexOf('--format');
const formatValue = formatIdx >= 0 ? args[formatIdx + 1] : null;

const rulesIdx = args.indexOf('--rules');
const rulesFile = rulesIdx >= 0 ? args[rulesIdx + 1] : null;

// Collect plugins
const plugins = [];
let idx = 0;
while (idx < args.length) {
  if (args[idx] === '--plugin' && args[idx + 1]) {
    plugins.push(args[idx + 1]);
    idx += 2;
  } else {
    idx++;
  }
}

const scanDir = args.find(a =>
  !a.startsWith('-') &&
  a !== rulesFile &&
  a !== formatValue &&
  !plugins.includes(a)
) || process.cwd();

const scanner = new GuardScanner({
  verbose, selfExclude, strict, summaryOnly, checkDeps, soulLock, rulesFile, plugins,
  quiet: quietMode || !!formatValue,
});

scanner.scanDirectory(scanDir);

// Output reports (file-based, backward compatible)
if (jsonOutput) {
  const report = scanner.toJSON();
  const outPath = path.join(scanDir, 'guard-scanner-report.json');
  fs.writeFileSync(outPath, JSON.stringify(report, null, 2));
  if (!quietMode && !formatValue) console.log(`\n📄 JSON report: ${outPath}`);
}

if (sarifOutput) {
  const outPath = path.join(scanDir, 'guard-scanner.sarif');
  fs.writeFileSync(outPath, JSON.stringify(scanner.toSARIF(scanDir), null, 2));
  if (!quietMode && !formatValue) console.log(`\n📄 SARIF report: ${outPath}`);
}

if (htmlOutput) {
  const outPath = path.join(scanDir, 'guard-scanner-report.html');
  fs.writeFileSync(outPath, scanner.toHTML());
  if (!quietMode && !formatValue) console.log(`\n📄 HTML report: ${outPath}`);
}

// --format stdout output (v3.2.0)
if (formatValue === 'json') {
  process.stdout.write(JSON.stringify(scanner.toJSON(), null, 2) + '\n');
} else if (formatValue === 'sarif') {
  process.stdout.write(JSON.stringify(scanner.toSARIF(scanDir), null, 2) + '\n');
} else if (formatValue) {
  console.error(`❌ Unknown format: ${formatValue}. Use 'json' or 'sarif'.`);
  process.exit(2);
}

// Exit codes
if (scanner.stats.malicious > 0) process.exit(1);
if (failOnFindings && scanner.findings.length > 0) process.exit(1);
process.exit(0);
