/**
 * ClawAudit — Score Calculator Tests
 * Tests score calculation logic, clamping, grading, and JSON output.
 */

import { test } from "node:test";
import { strict as assert } from "node:assert";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";
import { createScriptRunner } from "./lib/test-utils.mjs";

const __dirname = dirname(fileURLToPath(import.meta.url));
const SCORE_SCRIPT = resolve(__dirname, "..", "scripts", "calculate-score.mjs");
const runScore = createScriptRunner(SCORE_SCRIPT);

// Run score calculation once and share result across integration tests
const scoreData = runScore();

// --- Pure score logic (mirrors calculate-score.mjs) ---

const SCORE_IMPACT = {
  "CRIT-001": -20, "CRIT-002": -15, "CRIT-003": -25, "CRIT-004": -20, "CRIT-005": -25,
  "WARN-003": -8,  "WARN-001": -15, "WARN-002": -15, "WARN-012": -20,
  "SYS-001": -20,  "SYS-011": -25, "SYS-021": -15,
};

function calcScore(findings) {
  let score = 100;
  for (const f of findings) {
    score += SCORE_IMPACT[f.code] || -3;
  }
  return Math.max(0, Math.min(100, score));
}

function getGrade(score) {
  if (score >= 90) return "A";
  if (score >= 70) return "B";
  if (score >= 50) return "C";
  if (score >= 30) return "D";
  return "F";
}

// =============================================================================
// Score Calculation Logic
// =============================================================================

test("Score: starts at 100 with no findings", () => {
  assert.equal(calcScore([]), 100);
});

test("Score: deducts correctly for single finding", () => {
  assert.equal(calcScore([{ code: "WARN-003" }]), 92); // 100 - 8
});

test("Score: deducts correctly for multiple findings", () => {
  assert.equal(calcScore([{ code: "WARN-003" }, { code: "SYS-001" }]), 72); // 100 - 8 - 20
});

test("Score: unknown code uses default -3 deduction", () => {
  assert.equal(calcScore([{ code: "UNKNOWN-999" }]), 97); // 100 - 3
});

// =============================================================================
// Score Clamping
// =============================================================================

test("Score: clamps at 0 (never negative)", () => {
  // Many critical findings should clamp to 0
  const findings = Array(10).fill({ code: "CRIT-003" }); // 10 × -25 = -250
  assert.equal(calcScore(findings), 0);
});

test("Score: clamps at 100 (never exceeds max)", () => {
  // No findings = 100, already at max
  assert.equal(calcScore([]), 100);
});

// =============================================================================
// Grade Thresholds
// =============================================================================

test("Grade: 100 → A (Excellent)", () => { assert.equal(getGrade(100), "A"); });
test("Grade: 90 → A (Excellent)", () => { assert.equal(getGrade(90), "A"); });
test("Grade: 89 → B (Good)", () => { assert.equal(getGrade(89), "B"); });
test("Grade: 70 → B (Good)", () => { assert.equal(getGrade(70), "B"); });
test("Grade: 69 → C (Fair)", () => { assert.equal(getGrade(69), "C"); });
test("Grade: 50 → C (Fair)", () => { assert.equal(getGrade(50), "C"); });
test("Grade: 49 → D (Poor)", () => { assert.equal(getGrade(49), "D"); });
test("Grade: 30 → D (Poor)", () => { assert.equal(getGrade(30), "D"); });
test("Grade: 29 → F (Critical)", () => { assert.equal(getGrade(29), "F"); });
test("Grade: 0 → F (Critical)", () => { assert.equal(getGrade(0), "F"); });

// =============================================================================
// Integration: JSON Output Structure
// =============================================================================

test("Score JSON output has correct structure", () => {
  const data = scoreData;
  assert.ok(typeof data.score === "number", "Missing score");
  assert.ok(data.score >= 0 && data.score <= 100, `Score ${data.score} out of 0-100 range`);
  assert.ok(typeof data.grade === "string", "Missing grade");
  assert.ok(["A", "B", "C", "D", "F"].includes(data.grade), `Invalid grade: ${data.grade}`);
  assert.ok(typeof data.label === "string", "Missing label");
  assert.ok(Array.isArray(data.deductions), "deductions must be an array");
  assert.ok(typeof data.scan_findings === "number", "Missing scan_findings count");
  assert.ok(typeof data.audit_findings === "number", "Missing audit_findings count");
  assert.ok(typeof data.system_findings === "number", "Missing system_findings count");
});

test("Score deductions have correct structure", () => {
  const data = scoreData;
  for (const d of data.deductions) {
    assert.ok(typeof d.code === "string", "deduction.code must be string");
    assert.ok(typeof d.impact === "number", "deduction.impact must be number");
    assert.ok(d.impact < 0, `deduction.impact should be negative, got ${d.impact}`);
    assert.ok(typeof d.source === "string", "deduction.source must be string");
    assert.ok(
      ["skill-scan", "config-audit", "system-audit", "integrity"].includes(d.source),
      `Unknown source: ${d.source}`
    );
  }
});

test("Score grade matches score value", () => {
  const data = scoreData;
  const expectedGrade = getGrade(data.score);
  assert.equal(data.grade, expectedGrade, `Grade ${data.grade} doesn't match score ${data.score}`);
});

test("Score is consistent with deductions sum", () => {
  const data = scoreData;
  const deducted = data.deductions.reduce((sum, d) => sum + d.impact, 0);
  const expected = Math.max(0, Math.min(100, 100 + deducted));
  assert.equal(data.score, expected, "Score doesn't match sum of deductions");
});
