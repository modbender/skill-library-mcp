/**
 * Shared test utilities
 */

import { spawnSync } from "child_process";
import { strict as assert } from "node:assert";

export function createScriptRunner(scriptPath) {
  return function run(args = ["--json"], extraEnv = {}) {
    const result = spawnSync("node", [scriptPath, ...args], {
      encoding: "utf-8",
      env: { ...process.env, ...extraEnv },
      timeout: 15000,
    });
    assert.ok(result.stdout, `Script produced no output. stderr: ${result.stderr}`);
    return JSON.parse(result.stdout);
  };
}

export function createBashRunner(scriptPath) {
  return function run(args = ["--json"], extraEnv = {}) {
    const result = spawnSync("bash", [scriptPath, ...args], {
      encoding: "utf-8",
      env: { ...process.env, ...extraEnv },
      timeout: 15000,
    });
    assert.ok(result.stdout, `Script produced no output. stderr: ${result.stderr}`);
    return JSON.parse(result.stdout);
  };
}

export function hasCode(findings, code, skill) {
  return findings.some(f => f.code === code && (!skill || f.skill === skill));
}
