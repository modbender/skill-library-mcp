#!/usr/bin/env node
/**
 * test-skill.js
 *
 * End-to-end integration test for the rule-creation skill.
 * Tests both a high-stakes rule (needs Lobster) and a simple rule (no Lobster).
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');

const baseDir = path.join(os.homedir(), 'clawd/skills/rule-creation');
const tmpDir = os.tmpdir();

let passed = 0;
let failed = 0;

function runScript(script, env) {
  try {
    const result = execSync(`node ${path.join(baseDir, 'scripts', script)}`, {
      env: { ...process.env, ...env, BASE_DIR: baseDir },
      encoding: 'utf8'
    });
    return JSON.parse(result);
  } catch (e) {
    throw new Error(`Script ${script} failed: ${e.message}\nOutput: ${e.stdout}\nStderr: ${e.stderr}`);
  }
}

function assert(condition, message) {
  if (condition) {
    console.log(`  ✅ ${message}`);
    passed++;
  } else {
    console.error(`  ❌ ${message}`);
    failed++;
  }
}

console.log('\n══════════════════════════════════════════════');
console.log('  rule-creation skill — Integration Tests');
console.log('══════════════════════════════════════════════\n');

// ────────────────────────────────────────────────
// PRE-CHECK: Lobster availability (used to gate Tests 4 & 8)
// ────────────────────────────────────────────────
let lobsterAvailable = false;
try {
  const lc = runScript('check-lobster-available.js', {});
  lobsterAvailable = lc.available;
  console.log(`ℹ️  Lobster preflight: ${lobsterAvailable ? '✅ available' : '⚠️  unavailable'} — ${lc.reason}\n`);
} catch (e) {
  console.log(`ℹ️  Lobster preflight: check failed — ${e.message}\n`);
}

// ────────────────────────────────────────────────
// TEST 1: High-stakes rule → should need Lobster
// ────────────────────────────────────────────────
console.log('TEST 1: High-stakes rule (external message gate)');
const eval1 = runScript('evaluate-enforcement-need.js', {
  RULE_NAME: 'external-message-gate',
  RULE_DESCRIPTION: 'Before sending any external email or message, always get user approval first'
});
assert(eval1.needsEnforcement === true, 'needsEnforcement = true');
assert(eval1.criteria.includes('high-stakes'), 'criterion: high-stakes matched');
assert(typeof eval1.reason === 'string' && eval1.reason.length > 0, 'reason is non-empty');

// ────────────────────────────────────────────────
// TEST 2: Simple internal rule → should NOT need Lobster
// ────────────────────────────────────────────────
console.log('\nTEST 2: Simple internal rule (naming convention)');
const eval2 = runScript('evaluate-enforcement-need.js', {
  RULE_NAME: 'kebab-case-filenames',
  RULE_DESCRIPTION: 'All new files should use kebab-case naming'
});
assert(eval2.needsEnforcement === false, 'needsEnforcement = false');
assert(eval2.criteria.length === 0, 'no criteria matched');

// ────────────────────────────────────────────────
// TEST 3: Multi-step rule → should need Lobster
// ────────────────────────────────────────────────
console.log('\nTEST 3: Multi-step sequence rule');
const eval3 = runScript('evaluate-enforcement-need.js', {
  RULE_NAME: 'pr-review-flow',
  RULE_DESCRIPTION: 'First run tests, then request review, after approval then merge, finally notify team'
});
assert(eval3.needsEnforcement === true, 'needsEnforcement = true');
assert(eval3.criteria.includes('multi-step-sequence'), 'criterion: multi-step-sequence matched');

// ────────────────────────────────────────────────
// TEST 4: Lobster workflow creation
// ────────────────────────────────────────────────
console.log('\nTEST 4: Create Lobster workflow');
const tmpWorkflowsDir = path.join(baseDir, 'workflows');
const expectedSlug = 'test-lobster-rule';
const expectedPath = path.join(tmpWorkflowsDir, `${expectedSlug}.lobster`);

// Clean up any prior test artifact
if (fs.existsSync(expectedPath)) fs.unlinkSync(expectedPath);

const lobster = runScript('create-lobster-workflow.js', {
  RULE_NAME: 'test-lobster-rule',
  RULE_DESCRIPTION: 'A test rule for workflow generation',
  BASE_DIR: baseDir
});

if (lobsterAvailable) {
  assert(lobster.created === true, 'workflow created = true');
  assert(fs.existsSync(lobster.path), `workflow file exists at ${lobster.path}`);
  const content = fs.readFileSync(lobster.path, 'utf8');
  assert(content.includes('test-lobster-rule'), 'workflow contains rule name');
} else {
  // Lobster is disabled — verify graceful fallback
  assert(lobster.created === false, 'workflow created = false (Lobster unavailable)');
  assert(lobster.available === false, 'available = false (Lobster unavailable)');
  assert(lobster.path === null, 'path = null (no workflow written)');
  console.log(`  ℹ️  Graceful fallback confirmed: ${lobster.reason}`);
}

// ────────────────────────────────────────────────
// TEST 5: Wire to docs
// ────────────────────────────────────────────────
console.log('\nTEST 5: Wire rule to docs');
const testTargetFile = path.join(tmpDir, `rule-creation-test-${Date.now()}.md`);
const wire = runScript('wire-rule-to-docs.js', {
  RULE_NAME: 'test-wire-rule',
  RULE_DESCRIPTION: 'This is a test rule for wiring verification',
  RULE_TYPE: 'HARD',
  HAS_LOBSTER: 'true',
  LOBSTER_PATH: '/path/to/test.lobster',
  TARGET_FILE: testTargetFile,
  BASE_DIR: baseDir
});
assert(wire.location === testTargetFile, 'wired to correct location');
assert(wire.skipped === false, 'not skipped (new rule)');
const wiredContent = fs.readFileSync(testTargetFile, 'utf8');
assert(wiredContent.includes('test-wire-rule'), 'rule name in wired file');
assert(wiredContent.includes('HARD'), 'rule type in wired file');
assert(wiredContent.includes('/path/to/test.lobster'), 'lobster path in wired file');

// ────────────────────────────────────────────────
// TEST 6: Idempotency — wiring same rule twice
// ────────────────────────────────────────────────
console.log('\nTEST 6: Idempotency (wire same rule twice)');
const wire2 = runScript('wire-rule-to-docs.js', {
  RULE_NAME: 'test-wire-rule',
  RULE_DESCRIPTION: 'This is a test rule for wiring verification',
  RULE_TYPE: 'HARD',
  HAS_LOBSTER: 'false',
  TARGET_FILE: testTargetFile,
  BASE_DIR: baseDir
});
assert(wire2.skipped === true, 'second wire skipped (idempotent)');
const wiredContent2 = fs.readFileSync(testTargetFile, 'utf8');
const occurrences = (wiredContent2.match(/test-wire-rule/g) || []).length;
// Rule name appears exactly once (in the section header only — not duplicated by second wire call)
assert(occurrences === 1, `rule not duplicated (appears exactly 1 time: ${occurrences})`);

// ────────────────────────────────────────────────
// TEST 7: Lobster availability preflight (check-lobster-available.js)
// ────────────────────────────────────────────────
console.log('\nTEST 7: check-lobster-available.js preflight');
const lobsterCheck = runScript('check-lobster-available.js', {});
assert(typeof lobsterCheck.available === 'boolean', 'available is boolean');
assert(typeof lobsterCheck.reason === 'string' && lobsterCheck.reason.length > 0, 'reason is non-empty string');
// available value must be consistent with the pre-check we ran above
assert(lobsterCheck.available === lobsterAvailable, 'available consistent with pre-check');
console.log(`  ℹ️  Lobster status: ${lobsterCheck.available ? '✅ available' : '⚠️  unavailable'} — ${lobsterCheck.reason}`);

// ────────────────────────────────────────────────
// TEST 8: create-lobster-workflow graceful fallback when Lobster unavailable
// ────────────────────────────────────────────────
console.log('\nTEST 8: create-lobster-workflow graceful fallback when Lobster unavailable');
if (!lobsterAvailable) {
  // Real environment: Lobster is disabled — Test 4 already validated graceful result
  assert(lobster.created === false, 'created = false (already validated in TEST 4)');
  assert(typeof lobster.reason === 'string', 'reason is string (already validated in TEST 4)');
  console.log('  ℹ️  Fallback confirmed (validated in TEST 4, no re-run needed)');
} else {
  // Lobster available in this env — just verify the script returns available=true
  assert(lobster.available !== false, 'available not false when Lobster enabled');
  console.log('  ℹ️  Lobster available — fallback path N/A; workflow creation tested in TEST 4');
}

// ────────────────────────────────────────────────
// CLEANUP
// ────────────────────────────────────────────────
try {
  if (fs.existsSync(testTargetFile)) fs.unlinkSync(testTargetFile);
  if (fs.existsSync(expectedPath)) fs.unlinkSync(expectedPath);
  // Clean up test-external-gate from prior manual tests
  const testGatePath = path.join(baseDir, 'workflows', 'test-external-gate.lobster');
  if (fs.existsSync(testGatePath)) fs.unlinkSync(testGatePath);
} catch (e) { /* non-fatal */ }

// ────────────────────────────────────────────────
// SUMMARY
// ────────────────────────────────────────────────
console.log('\n══════════════════════════════════════════════');
console.log(`  Results: ${passed} passed, ${failed} failed`);
console.log('══════════════════════════════════════════════\n');

process.exit(failed > 0 ? 1 : 0);
