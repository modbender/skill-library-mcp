/**
 * ClawAudit — File Integrity Monitor Tests
 *
 * Tests for check-integrity.mjs:
 * - SHA256 hashing correctness
 * - Baseline comparison logic (drift, new files, deleted files)
 * - Finding severity logic
 * - JSON output structure (integration)
 */

import { test } from "node:test";
import { strict as assert } from "node:assert";
import { createHash } from "crypto";
import { spawnSync } from "child_process";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const INTEGRITY_SCRIPT = resolve(__dirname, "..", "scripts", "check-integrity.mjs");

// --- Helpers ---

function sha256(content) {
  return createHash("sha256").update(content, "utf-8").digest("hex");
}

// Simulate the baseline comparison logic from check-integrity.mjs
function compareToBaseline(baseFiles, currentFiles) {
  const findings = [];

  for (const [filename, info] of Object.entries(currentFiles)) {
    if (!baseFiles[filename]) {
      findings.push({ code: "INTEG-003", severity: "info", filename, reason: "new" });
    } else if (baseFiles[filename].hash !== info.hash) {
      findings.push({ code: "INTEG-002", severity: "warning", filename, reason: "changed" });
    }
  }

  for (const filename of Object.keys(baseFiles)) {
    if (!currentFiles[filename]) {
      findings.push({ code: "INTEG-002", severity: "warning", filename, reason: "deleted" });
    }
  }

  return findings;
}

// =============================================================================
// SHA256 Hashing — Unit Tests
// =============================================================================

test("sha256: empty string produces consistent hash", () => {
  const h1 = sha256("");
  const h2 = sha256("");
  assert.equal(h1, h2);
  assert.equal(h1.length, 64); // 256 bits = 64 hex chars
});

test("sha256: different content produces different hash", () => {
  const h1 = sha256("SOUL.md content v1");
  const h2 = sha256("SOUL.md content v2");
  assert.notEqual(h1, h2);
});

test("sha256: same content always produces same hash", () => {
  const content = "# SOUL.md\nYou are Karl.\n";
  assert.equal(sha256(content), sha256(content));
});

test("sha256: single character change produces different hash", () => {
  const h1 = sha256("You are Karl.");
  const h2 = sha256("You are Karl!");
  assert.notEqual(h1, h2, "Single character change must produce different hash");
});

test("sha256: hash is 64 hex characters (SHA256 output)", () => {
  const h = sha256("test content");
  assert.match(h, /^[0-9a-f]{64}$/, "Hash must be 64 lowercase hex characters");
});

// =============================================================================
// Baseline Comparison Logic — Unit Tests
// =============================================================================

test("INTEG: no changes → no findings", () => {
  const content = "# SOUL.md\nYou are Karl.\n";
  const hash = sha256(content);

  const baseFiles = { "SOUL.md": { hash, size: content.length } };
  const currentFiles = { "SOUL.md": { hash, size: content.length } };

  const findings = compareToBaseline(baseFiles, currentFiles);
  assert.equal(findings.length, 0);
});

test("INTEG-002: changed file is detected", () => {
  const baseFiles = { "SOUL.md": { hash: sha256("original content"), size: 16 } };
  const currentFiles = { "SOUL.md": { hash: sha256("modified content"), size: 16 } };

  const findings = compareToBaseline(baseFiles, currentFiles);
  assert.equal(findings.length, 1);
  assert.equal(findings[0].code, "INTEG-002");
  assert.equal(findings[0].severity, "warning");
  assert.equal(findings[0].reason, "changed");
  assert.equal(findings[0].filename, "SOUL.md");
});

test("INTEG-002: deleted file is detected", () => {
  const baseFiles = { "SOUL.md": { hash: sha256("content"), size: 7 } };
  const currentFiles = {}; // SOUL.md gone

  const findings = compareToBaseline(baseFiles, currentFiles);
  assert.equal(findings.length, 1);
  assert.equal(findings[0].code, "INTEG-002");
  assert.equal(findings[0].reason, "deleted");
});

test("INTEG-003: new file since baseline → info only", () => {
  const baseFiles = { "SOUL.md": { hash: sha256("soul"), size: 4 } };
  const currentFiles = {
    "SOUL.md": { hash: sha256("soul"), size: 4 },
    "AGENTS.md": { hash: sha256("agents"), size: 6 }, // new
  };

  const findings = compareToBaseline(baseFiles, currentFiles);
  assert.equal(findings.length, 1);
  assert.equal(findings[0].code, "INTEG-003");
  assert.equal(findings[0].severity, "info");
  assert.equal(findings[0].filename, "AGENTS.md");
});

test("INTEG: multiple changes detected independently", () => {
  const baseFiles = {
    "SOUL.md": { hash: sha256("soul v1"), size: 7 },
    "MEMORY.md": { hash: sha256("memory v1"), size: 9 },
    "IDENTITY.md": { hash: sha256("identity"), size: 8 },
  };
  const currentFiles = {
    "SOUL.md": { hash: sha256("soul v2"), size: 7 },  // changed
    "MEMORY.md": { hash: sha256("memory v1"), size: 9 }, // unchanged
    // IDENTITY.md: deleted
    "USER.md": { hash: sha256("user"), size: 4 },      // new
  };

  const findings = compareToBaseline(baseFiles, currentFiles);
  const codes = findings.map((f) => f.code);

  assert.ok(codes.includes("INTEG-002"), "Changed SOUL.md should trigger INTEG-002");
  assert.ok(findings.some((f) => f.filename === "IDENTITY.md" && f.reason === "deleted"), "Deleted IDENTITY.md should be detected");
  assert.ok(codes.includes("INTEG-003"), "New USER.md should trigger INTEG-003");
  assert.equal(findings.filter((f) => f.filename === "MEMORY.md").length, 0, "Unchanged MEMORY.md should not be flagged");
});

test("INTEG: unchanged file with same hash → no finding", () => {
  const hash = sha256("You are Karl, a helpful assistant.");
  const file = { hash, size: 34 };
  const findings = compareToBaseline({ "SOUL.md": file }, { "SOUL.md": file });
  assert.equal(findings.length, 0);
});

// =============================================================================
// Finding Severity — Unit Tests
// =============================================================================

test("INTEG-002 is warning severity (tamper/deletion = serious)", () => {
  const findings = compareToBaseline(
    { "SOUL.md": { hash: sha256("v1"), size: 2 } },
    { "SOUL.md": { hash: sha256("v2"), size: 2 } }
  );
  assert.equal(findings[0].severity, "warning");
});

test("INTEG-003 is info severity (new file = noteworthy but not alarming)", () => {
  const findings = compareToBaseline(
    {},
    { "SOUL.md": { hash: sha256("new"), size: 3 } }
  );
  assert.equal(findings[0].severity, "info");
});

// =============================================================================
// Integration: JSON Output Structure
// =============================================================================

test("check-integrity.mjs JSON output has correct structure", () => {
  const result = spawnSync("node", [INTEGRITY_SCRIPT, "--json"], {
    encoding: "utf-8",
    timeout: 10000,
  });
  assert.ok(result.stdout, `Script produced no output. stderr: ${result.stderr}`);
  const data = JSON.parse(result.stdout);

  assert.ok(typeof data.critical === "number", "Missing critical count");
  assert.ok(typeof data.warnings === "number", "Missing warnings count");
  assert.ok(typeof data.info === "number", "Missing info count");
  assert.ok(Array.isArray(data.findings), "findings must be an array");

  for (const f of data.findings) {
    assert.ok(typeof f.code === "string", "finding.code must be string");
    assert.ok(f.code.startsWith("INTEG-"), `finding.code should start with INTEG-, got: ${f.code}`);
    assert.ok(["critical", "warning", "info"].includes(f.severity), `Invalid severity: ${f.severity}`);
    assert.ok(typeof f.title === "string", "finding.title must be string");
    assert.ok(typeof f.detail === "string", "finding.detail must be string");
  }
});

test("check-integrity.mjs: exits 0 regardless of findings", () => {
  const result = spawnSync("node", [INTEGRITY_SCRIPT, "--json"], {
    encoding: "utf-8",
    timeout: 10000,
  });
  assert.equal(result.status, 0, "Script should always exit 0 (non-crashing)");
});
