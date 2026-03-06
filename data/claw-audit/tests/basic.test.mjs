#!/usr/bin/env node

/**
 * ClawAudit Basic Tests
 * Run with: npm test
 */

import { test } from "node:test";
import { strict as assert } from "node:assert";
import { execSync } from "child_process";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const scriptsDir = resolve(__dirname, "..", "scripts");

test("scan-skills.sh should run without errors", () => {
  try {
    const result = execSync(`bash "${scriptsDir}/scan-skills.sh" --json`, {
      encoding: "utf-8",
      timeout: 10000,
    });
    const data = JSON.parse(result);
    assert.ok(typeof data.skills_scanned === "number");
    assert.ok(typeof data.critical === "number");
    assert.ok(typeof data.warnings === "number");
    assert.ok(Array.isArray(data.findings));
  } catch (err) {
    // It's OK if no skills directory exists - this is expected in test environment
    assert.ok(
      err.status === 1,
      "Script should exit with code 1 when no skills directory is found"
    );
  }
});

test("audit-config.mjs should run without errors", () => {
  try {
    const result = execSync(`node "${scriptsDir}/audit-config.mjs" --json`, {
      encoding: "utf-8",
      timeout: 10000,
    });
    const data = JSON.parse(result);
    assert.ok(typeof data.critical === "number");
    assert.ok(typeof data.warnings === "number");
    assert.ok(typeof data.info === "number");
    assert.ok(Array.isArray(data.findings));
  } catch (err) {
    throw err;
  }
});

test("calculate-score.mjs should run without errors", () => {
  try {
    const result = execSync(`node "${scriptsDir}/calculate-score.mjs" --json`, {
      encoding: "utf-8",
      timeout: 15000,
    });
    const data = JSON.parse(result);
    assert.ok(typeof data.score === "number");
    assert.ok(data.score >= 0 && data.score <= 100);
    assert.ok(typeof data.grade === "string");
    assert.ok(Array.isArray(data.deductions));
  } catch (err) {
    throw err;
  }
});
