#!/usr/bin/env node
/**
 * Basic test suite for review.js — no external deps
 */
'use strict';

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');

const SCRIPT = path.join(__dirname, '..', 'scripts', 'review.js');
let passed = 0;
let failed = 0;
let tmpDir;

function run(args, opts = {}) {
  const { expectFail = false, allowExit1 = false } = typeof opts === 'boolean' ? { expectFail: opts } : opts;
  try {
    const out = execSync(`node ${SCRIPT} ${args}`, {
      encoding: 'utf8',
      timeout: 10000,
      env: { ...process.env, NODE_ENV: 'test' },
    });
    if (expectFail) throw new Error(`Expected failure but got success: ${out}`);
    return { ok: true, stdout: out.trim(), code: 0 };
  } catch (e) {
    // Exit code 1 = REVISE (expected for non-approved rounds)
    if (allowExit1 && e.status === 1) {
      return { ok: true, stdout: (e.stdout || '').trim(), code: 1 };
    }
    if (!expectFail) throw e;
    return { ok: false, stderr: (e.stderr || '').trim(), stdout: (e.stdout || '').trim(), code: e.status || 1 };
  }
}

function assert(condition, msg) {
  if (!condition) {
    failed++;
    console.error(`  ✗ FAIL: ${msg}`);
  } else {
    passed++;
    console.log(`  ✓ ${msg}`);
  }
}

function setup() {
  tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'review-test-'));
  const planPath = path.join(tmpDir, 'test-plan.md');
  fs.writeFileSync(planPath, '# Test Plan\n\nThis is a test implementation plan.\n\n## Architecture\nSimple REST API with auth.\n');
  return planPath;
}

function cleanup() {
  if (tmpDir) fs.rmSync(tmpDir, { recursive: true, force: true });
}

// ---- Tests ----

console.log('\n=== review.js test suite ===\n');

// Test: help
console.log('--- help ---');
{
  const r = run('--help');
  assert(r.stdout.includes('review.js'), 'help output contains script name');
  assert(r.stdout.includes('init'), 'help mentions init command');
  assert(r.stdout.includes('parse-round'), 'help mentions parse-round command');
  assert(r.stdout.includes('finalize'), 'help mentions finalize command');
  assert(r.stdout.includes('status'), 'help mentions status command');
  assert(r.stdout.includes('--max-rounds'), 'help mentions --max-rounds');
  assert(r.stdout.includes('--token-budget'), 'help mentions --token-budget');
}

// Test: init — success
console.log('\n--- init ---');
const planPath = setup();
{
  const outDir = path.join(tmpDir, 'reviews');
  const r = run(`init --plan ${planPath} --reviewer-model openai/codex --planner-model anthropic/sonnet --out ${outDir}`);
  assert(r.ok, 'init exits 0');
  assert(fs.existsSync(r.stdout), 'workspace directory created');

  const wsDir = r.stdout;
  assert(fs.existsSync(path.join(wsDir, 'meta.json')), 'meta.json created');
  assert(fs.existsSync(path.join(wsDir, 'issues.json')), 'issues.json created');
  assert(fs.existsSync(path.join(wsDir, 'changelog.md')), 'changelog.md created');
  assert(fs.existsSync(path.join(wsDir, 'plan-v1.md')), 'plan-v1.md created');

  const meta = JSON.parse(fs.readFileSync(path.join(wsDir, 'meta.json'), 'utf8'));
  assert(meta.reviewerModel === 'openai/codex', 'reviewer model stored');
  assert(meta.plannerModel === 'anthropic/sonnet', 'planner model stored');
  assert(meta.verdict === 'PENDING', 'initial verdict is PENDING');
  assert(meta.maxRounds === 5, 'default maxRounds is 5');
  assert(meta.tokenBudget === 8000, 'default tokenBudget is 8000');

  // Test: same-provider rejection
  console.log('\n--- init: same-provider rejection ---');
  const r2 = run(`init --plan ${planPath} --reviewer-model anthropic/opus --planner-model anthropic/sonnet --out ${outDir}`, { expectFail: true });
  assert(!r2.ok, 'same-provider init fails');
  assert(r2.code === 2, 'exits with code 2');

  // Test: --max-rounds stored in meta
  console.log('\n--- init: --max-rounds and --token-budget stored in meta ---');
  const outDirMR = path.join(tmpDir, 'reviews-maxrounds');
  const rMR = run(`init --plan ${planPath} --reviewer-model openai/codex --planner-model anthropic/sonnet --out ${outDirMR} --max-rounds 3 --token-budget 4000`);
  assert(rMR.ok, 'init with --max-rounds and --token-budget exits 0');
  const wsDirMR = rMR.stdout;
  const metaMR = JSON.parse(fs.readFileSync(path.join(wsDirMR, 'meta.json'), 'utf8'));
  assert(metaMR.maxRounds === 3, '--max-rounds 3 stored in meta.json');
  assert(metaMR.tokenBudget === 4000, '--token-budget 4000 stored in meta.json');

  // Test: parse-round
  console.log('\n--- parse-round ---');
  const respPath = path.join(tmpDir, 'response.json');
  fs.writeFileSync(respPath, JSON.stringify({
    verdict: 'REVISE',
    prior_issues: [],
    new_issues: [
      { severity: 'CRITICAL', location: 'Auth', problem: 'No rate limiting on login', fix: 'Add rate limiter' },
      { severity: 'HIGH', location: 'DB', problem: 'No input validation on queries', fix: 'Add parameterized queries' },
      { severity: 'LOW', location: 'Logging', problem: 'Verbose debug logs in prod', fix: 'Set log level via env var' },
    ],
    summary: '3 issues found, 1 critical',
  }));

  const r3 = run(`parse-round --workspace ${wsDir} --round 1 --response ${respPath}`, { allowExit1: true });
  const output = JSON.parse(r3.stdout);
  assert(output.verdict === 'REVISE', 'verdict is REVISE');
  assert(output.newIssues === 3, '3 new issues parsed');
  assert(output.blockers === 2, '2 blockers (CRITICAL + HIGH)');

  const issues = JSON.parse(fs.readFileSync(path.join(wsDir, 'issues.json'), 'utf8'));
  assert(issues.length === 3, '3 issues in tracker');
  assert(issues[0].id === 'ISS-001', 'first issue is ISS-001');
  assert(issues[0].severity === 'CRITICAL', 'first issue is CRITICAL');
  assert(issues[1].id === 'ISS-002', 'second issue is ISS-002');

  // Test: parse-round with resolution
  console.log('\n--- parse-round: round 2 with resolutions ---');
  const resp2Path = path.join(tmpDir, 'response2.json');
  fs.writeFileSync(resp2Path, JSON.stringify({
    verdict: 'APPROVED',
    prior_issues: [
      { id: 'ISS-001', status: 'resolved', evidence: 'Rate limiter added' },
      { id: 'ISS-002', status: 'resolved', evidence: 'Parameterized queries implemented' },
      { id: 'ISS-003', status: 'resolved', evidence: 'Log level configurable' },
    ],
    new_issues: [],
    summary: 'All issues resolved',
  }));

  const r4 = run(`parse-round --workspace ${wsDir} --round 2 --response ${resp2Path}`);
  const output2 = JSON.parse(r4.stdout);
  assert(output2.verdict === 'APPROVED', 'verdict is APPROVED after all resolved');
  assert(output2.blockers === 0, '0 blockers');

  // Test: finalize
  console.log('\n--- finalize ---');
  const r5 = run(`finalize --workspace ${wsDir}`);
  const finalOutput = JSON.parse(r5.stdout);
  assert(finalOutput.verdict === 'APPROVED', 'final verdict is APPROVED');
  assert(finalOutput.issuesFound === 3, '3 total issues found');
  assert(finalOutput.issuesResolved === 3, '3 issues resolved');
  assert(fs.existsSync(path.join(wsDir, 'plan-final.md')), 'plan-final.md generated');
  assert(fs.existsSync(path.join(wsDir, 'summary.json')), 'summary.json generated');

  // Test: verdict lives in meta.json (not issues.json)
  const metaAfterFinalize = JSON.parse(fs.readFileSync(path.join(wsDir, 'meta.json'), 'utf8'));
  assert(metaAfterFinalize.verdict === 'APPROVED', 'verdict stored in meta.json after finalize');

  // Test: status
  console.log('\n--- status ---');
  const r6 = run(`status --workspace ${wsDir}`);
  const status = JSON.parse(r6.stdout);
  assert(status.verdict === 'APPROVED', 'status shows APPROVED');
  assert(status.totalIssues === 3, 'status shows 3 total issues');

  // Test: dedup detection (cross-round, existing open issue)
  console.log('\n--- dedup detection (cross-round) ---');
  const outDir2 = path.join(tmpDir, 'reviews2');
  const r7 = run(`init --plan ${planPath} --reviewer-model openai/codex --planner-model anthropic/sonnet --out ${outDir2}`);
  const wsDir2 = r7.stdout;

  const dedupResp1 = path.join(tmpDir, 'dedup-resp1.json');
  fs.writeFileSync(dedupResp1, JSON.stringify({
    verdict: 'REVISE',
    prior_issues: [],
    new_issues: [
      { severity: 'HIGH', location: 'Auth', problem: 'No rate limiting on login endpoint allows brute force attacks', fix: 'Add rate limiter' },
    ],
    summary: '1 issue',
  }));
  run(`parse-round --workspace ${wsDir2} --round 1 --response ${dedupResp1}`, { allowExit1: true });

  const dedupResp2 = path.join(tmpDir, 'dedup-resp2.json');
  fs.writeFileSync(dedupResp2, JSON.stringify({
    verdict: 'REVISE',
    prior_issues: [{ id: 'ISS-001', status: 'still-open', evidence: 'not fixed' }],
    new_issues: [
      { severity: 'HIGH', location: 'Authentication', problem: 'No rate limiting on login endpoint allows brute force attacks to succeed', fix: 'Implement rate limiting' },
    ],
    summary: '1 new issue (likely dup)',
  }));
  const r8 = run(`parse-round --workspace ${wsDir2} --round 2 --response ${dedupResp2}`, { allowExit1: true });
  const dedupOutput = JSON.parse(r8.stdout);
  assert(dedupOutput.dedupWarnings > 0, 'dedup warning detected for similar issue (cross-round)');

  // Test: intra-batch dedup (two nearly-identical issues in the same round's new_issues)
  console.log('\n--- dedup detection (intra-batch) ---');
  const outDirIB = path.join(tmpDir, 'reviews-intrabatch');
  const rIB = run(`init --plan ${planPath} --reviewer-model openai/codex --planner-model anthropic/sonnet --out ${outDirIB}`);
  const wsDirIB = rIB.stdout;

  const intraBatchResp = path.join(tmpDir, 'intra-batch-resp.json');
  fs.writeFileSync(intraBatchResp, JSON.stringify({
    verdict: 'REVISE',
    prior_issues: [],
    new_issues: [
      { severity: 'HIGH', location: 'Auth', problem: 'No rate limiting on login endpoint allows brute force', fix: 'Add rate limiter' },
      { severity: 'HIGH', location: 'Login', problem: 'No rate limiting on login endpoint allows brute force attacks', fix: 'Implement rate limiting middleware' },
    ],
    summary: '2 issues (probably duplicates)',
  }));
  const rIBResult = run(`parse-round --workspace ${wsDirIB} --round 1 --response ${intraBatchResp}`, { allowExit1: true });
  const intraBatchOutput = JSON.parse(rIBResult.stdout);
  assert(intraBatchOutput.dedupWarnings > 0, 'intra-batch dedup warning detected for two similar new issues in same round');

  // Test: blocked approval (reviewer says APPROVED but blockers remain)
  console.log('\n--- blocked approval ---');
  const outDir3 = path.join(tmpDir, 'reviews3');
  const r9 = run(`init --plan ${planPath} --reviewer-model openai/codex --planner-model anthropic/sonnet --out ${outDir3}`);
  const wsDir3 = r9.stdout;

  const blockResp = path.join(tmpDir, 'block-resp.json');
  fs.writeFileSync(blockResp, JSON.stringify({
    verdict: 'REVISE',
    prior_issues: [],
    new_issues: [{ severity: 'CRITICAL', location: 'Core', problem: 'Fatal flaw', fix: 'Fix it' }],
    summary: '1 critical issue',
  }));
  run(`parse-round --workspace ${wsDir3} --round 1 --response ${blockResp}`, { allowExit1: true });

  const fakeApprove = path.join(tmpDir, 'fake-approve.json');
  fs.writeFileSync(fakeApprove, JSON.stringify({
    verdict: 'APPROVED',
    prior_issues: [{ id: 'ISS-001', status: 'still-open', evidence: 'nope' }],
    new_issues: [],
    summary: 'Approving anyway',
  }));
  const r10 = run(`parse-round --workspace ${wsDir3} --round 2 --response ${fakeApprove}`, { allowExit1: true });
  const blockOutput = JSON.parse(r10.stdout);
  assert(blockOutput.verdict === 'REVISE', 'approval blocked when CRITICAL still open');

  // Test: schema validation failure
  console.log('\n--- schema validation ---');
  const badResp = path.join(tmpDir, 'bad-resp.json');
  fs.writeFileSync(badResp, JSON.stringify({ verdict: 'MAYBE', prior_issues: 'nope', new_issues: [], summary: 123 }));
  const r11 = run(`parse-round --workspace ${wsDir3} --round 3 --response ${badResp}`, { expectFail: true });
  assert(!r11.ok, 'invalid schema rejected');

  // Test: force-approve with --ci-force in non-TTY mode (no blockers → clean finalize first)
  console.log('\n--- force-approve: --ci-force non-TTY ---');
  const outDir4 = path.join(tmpDir, 'reviews4');
  const r12 = run(`init --plan ${planPath} --reviewer-model openai/codex --planner-model anthropic/sonnet --out ${outDir4}`);
  const wsDir4 = r12.stdout;

  const blockResp4 = path.join(tmpDir, 'block-resp4.json');
  fs.writeFileSync(blockResp4, JSON.stringify({
    verdict: 'REVISE',
    prior_issues: [],
    new_issues: [{ severity: 'CRITICAL', location: 'Core', problem: 'Unresolved fatal issue in architecture', fix: 'Redesign component' }],
    summary: '1 critical',
  }));
  run(`parse-round --workspace ${wsDir4} --round 1 --response ${blockResp4}`, { allowExit1: true });

  // Now force-approve with --ci-force (simulates non-TTY CI environment)
  const r13 = run(
    `finalize --workspace ${wsDir4} --override-reason "Emergency deadline approved by team" --ci-force`
  );
  const ciForceOutput = JSON.parse(r13.stdout);
  assert(ciForceOutput.verdict === 'FORCE_APPROVED', '--ci-force produces FORCE_APPROVED verdict');
  assert(ciForceOutput.forceApproved === true, 'forceApproved flag is true');

  const summary4 = JSON.parse(fs.readFileSync(path.join(wsDir4, 'summary.json'), 'utf8'));
  assert(summary4.force_approve_log !== null, 'force_approve_log written to summary.json');
  assert(summary4.force_approve_log.ci_force === true, 'ci_force flag recorded in audit log');
  assert(summary4.force_approve_log.reason === 'Emergency deadline approved by team', 'override reason recorded');

  // Test: --ci-force without --override-reason should fail
  console.log('\n--- force-approve: --ci-force requires --override-reason ---');
  const outDir5 = path.join(tmpDir, 'reviews5');
  const r14 = run(`init --plan ${planPath} --reviewer-model openai/codex --planner-model anthropic/sonnet --out ${outDir5}`);
  const wsDir5 = r14.stdout;

  const blockResp5 = path.join(tmpDir, 'block-resp5.json');
  fs.writeFileSync(blockResp5, JSON.stringify({
    verdict: 'REVISE',
    prior_issues: [],
    new_issues: [{ severity: 'HIGH', location: 'DB', problem: 'Missing index on foreign key', fix: 'Add index' }],
    summary: '1 high',
  }));
  run(`parse-round --workspace ${wsDir5} --round 1 --response ${blockResp5}`, { allowExit1: true });

  // --ci-force without --override-reason — should fail because no override-reason means die() with no blockers check
  // Actually the check is: if blockers > 0 and no overrideReason, die. So this should fail.
  const r15 = run(`finalize --workspace ${wsDir5} --ci-force`, { expectFail: true });
  assert(!r15.ok, '--ci-force without --override-reason fails when blockers exist');
  assert(r15.code === 2, 'exits with code 2 for missing override-reason');

  // Test: rubric scoring
  console.log('\n--- rubric scoring ---');

  // Create a fresh workspace for rubric tests
  const outDirRubric = path.join(tmpDir, 'reviews-rubric');
  const rRubricInit = run(`init --plan ${planPath} --reviewer-model openai/gpt-4 --planner-model anthropic/sonnet --out ${outDirRubric}`);
  const wsRubric = rRubricInit.stdout;

  // Round 1: response with full rubric
  const rubricResponse = JSON.stringify({
    verdict: 'APPROVED',
    rubric: {
      security:        { score: 4, rationale: 'Auth properly implemented' },
      data_integrity:  { score: 5, rationale: 'Schema is consistent' },
      concurrency:     { score: null, rationale: 'Not applicable to this plan' },
      error_handling:  { score: 3, rationale: 'Some timeout handling missing' },
      scalability:     { score: 4, rationale: 'No unbounded operations' },
      completeness:    { score: 4, rationale: 'Edge cases covered' },
      maintainability: { score: 5, rationale: 'Clean code organization' },
    },
    prior_issues: [],
    new_issues: [],
    summary: 'Plan looks solid with minor error handling gaps.',
  });
  const rubricRespPath = path.join(tmpDir, 'rubric-response.json');
  fs.writeFileSync(rubricRespPath, rubricResponse);

  const rRubric1 = run(`parse-round --workspace "${wsRubric}" --round 1 --response "${rubricRespPath}"`);
  assert(rRubric1.ok, 'rubric response parsed successfully');

  const rubricOutput = JSON.parse(rRubric1.stdout);
  assert(rubricOutput.rubric !== null, 'rubric present in output');
  assert(rubricOutput.rubric.average !== undefined, 'rubric average calculated');
  assert(rubricOutput.rubric.scored === 6, 'rubric scored 6 non-null dimensions');
  assert(rubricOutput.rubric.average > 4.0, 'rubric average > 4.0 for good scores');
  assert(rubricOutput.rubric.dimensions.security.score === 4, 'security score preserved');
  assert(rubricOutput.rubric.dimensions.concurrency.score === null, 'null dimension preserved');

  // Test rubric in round output file
  const roundOutFile = path.join(wsRubric, 'round-1-output.json');
  const roundOutData = JSON.parse(fs.readFileSync(roundOutFile, 'utf8'));
  assert(roundOutData.rubric !== null, 'rubric saved to round output file');
  assert(roundOutData.rubric._average > 4.0, 'rubric average in round output');
  assert(roundOutData.rubricWarnings.length === 0, 'no rubric warnings for good scores');

  // Finalize and check rubric in summary
  const rRubricFin = run(`finalize --workspace "${wsRubric}"`);
  assert(rRubricFin.ok, 'finalize with rubric succeeds');
  const summaryRubric = JSON.parse(fs.readFileSync(path.join(wsRubric, 'summary.json'), 'utf8'));
  assert(summaryRubric.rubric !== null, 'rubric in summary.json');
  assert(summaryRubric.rubric.average > 4.0, 'rubric average in summary');

  // Test: rubric with low scores triggers warnings
  console.log('\n--- rubric low score warnings ---');
  const outDirRubricLow = path.join(tmpDir, 'reviews-rubric-low');
  const rRubricLowInit = run(`init --plan ${planPath} --reviewer-model openai/gpt-4 --planner-model anthropic/sonnet --out ${outDirRubricLow}`);
  const wsRubricLow = rRubricLowInit.stdout;

  const lowRubricResponse = JSON.stringify({
    verdict: 'REVISE',
    rubric: {
      security:        { score: 1, rationale: 'Major auth vulnerability' },
      data_integrity:  { score: 2, rationale: 'Schema inconsistencies' },
      concurrency:     { score: null, rationale: 'N/A' },
      error_handling:  { score: 1, rationale: 'No error handling at all' },
      scalability:     { score: 3, rationale: 'OK for now' },
      completeness:    { score: 2, rationale: 'Missing edge cases' },
      maintainability: { score: 3, rationale: 'Acceptable' },
    },
    prior_issues: [],
    new_issues: [
      { severity: 'CRITICAL', location: 'Auth', problem: 'No auth check', fix: 'Add auth middleware' },
    ],
    summary: 'Significant security and error handling issues.',
  });
  const lowRubricRespPath = path.join(tmpDir, 'low-rubric-response.json');
  fs.writeFileSync(lowRubricRespPath, lowRubricResponse);

  const rRubricLow1 = run(`parse-round --workspace "${wsRubricLow}" --round 1 --response "${lowRubricRespPath}"`, { allowExit1: true });
  assert(rRubricLow1.ok, 'low rubric response parsed');

  const lowRubricOutput = JSON.parse(rRubricLow1.stdout);
  assert(lowRubricOutput.rubric.warnings.length > 0, 'low scores generate rubric warnings');
  assert(lowRubricOutput.rubric.warnings.some(w => w.includes('security')), 'security warning present');
  assert(lowRubricOutput.rubric.warnings.some(w => w.includes('error_handling')), 'error_handling warning present');
  assert(lowRubricOutput.rubric.average < 3.0, 'low average detected');

  // Test: response without rubric (backward compat)
  console.log('\n--- rubric backward compatibility ---');
  const outDirNoRubric = path.join(tmpDir, 'reviews-norubric');
  const rNoRubricInit = run(`init --plan ${planPath} --reviewer-model openai/gpt-4 --planner-model anthropic/sonnet --out ${outDirNoRubric}`);
  const wsNoRubric = rNoRubricInit.stdout;

  const noRubricResponse = JSON.stringify({
    verdict: 'APPROVED',
    prior_issues: [],
    new_issues: [],
    summary: 'Looks good.',
  });
  const noRubricRespPath = path.join(tmpDir, 'no-rubric-response.json');
  fs.writeFileSync(noRubricRespPath, noRubricResponse);

  const rNoRubric1 = run(`parse-round --workspace "${wsNoRubric}" --round 1 --response "${noRubricRespPath}"`);
  assert(rNoRubric1.ok, 'response without rubric still parses (backward compat)');
  const noRubricOutput = JSON.parse(rNoRubric1.stdout);
  assert(noRubricOutput.rubric === null, 'rubric is null when not provided');

  // Test: rubric in status
  console.log('\n--- rubric in status ---');
  const rRubricStatus = run(`status --workspace "${wsRubric}"`);
  const statusOutput = JSON.parse(rRubricStatus.stdout);
  assert(statusOutput.rubric !== null, 'rubric present in status output');
  assert(statusOutput.rubric.average > 4.0, 'rubric average in status');

  // Test: unknown model family warnings
  console.log('\n--- unknown model family handling ---');
  // Both unknown: should warn but allow
  const outDirUK = path.join(tmpDir, 'reviews-unknown');
  const rUK = run(`init --plan ${planPath} --reviewer-model custom/unknown-model-xyz --planner-model custom2/another-unknown --out ${outDirUK}`);
  assert(rUK.ok, 'both-unknown init exits 0 (warn but allow)');
  // The workspace should still be created
  assert(fs.existsSync(rUK.stdout), 'workspace created for both-unknown models');

  // One unknown, one known: should warn but allow
  const outDirUK2 = path.join(tmpDir, 'reviews-unknown2');
  const rUK2 = run(`init --plan ${planPath} --reviewer-model custom/unknown-model-xyz --planner-model anthropic/sonnet --out ${outDirUK2}`);
  assert(rUK2.ok, 'one-unknown one-known init exits 0 (warn but allow)');
  assert(fs.existsSync(rUK2.stdout), 'workspace created for one-unknown model');
}

cleanup();

// ---- Summary ----
console.log(`\n=== Results: ${passed} passed, ${failed} failed ===\n`);
process.exit(failed > 0 ? 1 : 0);
