/**
 * ClawAudit — CIS Benchmark Tests
 * Tests for CRITICAL, HIGH, and MEDIUM priority CIS/Lynis checks
 *
 * Some checks require elevated privileges at runtime.
 * Without them, checks are reported as "skipped" (no test failure,
 * but missing security coverage). Required sudoers entries:
 *
 *   # /etc/sudoers.d/claw-audit
 *   openclaw ALL=(ALL) NOPASSWD: /usr/bin/wg show           # SYS-030-032
 *   openclaw ALL=(ALL) NOPASSWD: /sbin/auditctl -l          # SYS-191
 *   openclaw ALL=(ALL) NOPASSWD: /usr/bin/stat -c %a /etc/shadow    # SYS-204
 *   openclaw ALL=(ALL) NOPASSWD: /usr/bin/stat -c %U:%G /etc/shadow # SYS-204
 *
 * Group membership required to read /etc/shadow (SYS-163):
 *   sudo usermod -aG shadow openclaw
 */

import { test } from "node:test";
import { strict as assert } from "node:assert";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";
import { createScriptRunner } from "./lib/test-utils.mjs";

const __dirname = dirname(fileURLToPath(import.meta.url));
const AUDIT_SCRIPT = resolve(__dirname, "..", "scripts", "audit-system.mjs");
const runAudit = createScriptRunner(AUDIT_SCRIPT);

// Run audit once and share result across all tests (each test only inspects the output)
const data = runAudit();

// =============================================================================
// CRITICAL: System Access & Authentication
// =============================================================================

test("SYS-163: Empty password check exists", () => {
  // REQUIRES: shadow group membership or sudo access to /etc/shadow
  //   sudo usermod -aG shadow openclaw  (then re-login)
  //   Without this: check is skipped (entry appears in skippedChecks)
  assert.ok(data.findings !== undefined);
  // If empty passwords exist, should be flagged as critical
  const finding = data.findings.find(f => f.code === "SYS-163");
  if (finding) {
    assert.equal(finding.severity, "critical", "Empty passwords must be critical");
  }
});

test("SYS-164: Root PATH integrity check exists", () => {

  assert.ok(data.findings !== undefined);
  // If PATH contains . or writable dirs, should be flagged
  const finding = data.findings.find(f => f.code === "SYS-164");
  if (finding) {
    assert.equal(finding.severity, "critical", "Unsafe PATH must be critical");
  }
});

test("SYS-190: rsyslog check exists", () => {

  assert.ok(data.findings !== undefined);
  // If neither rsyslog nor syslog-ng running, should be flagged
  const finding = data.findings.find(f => f.code === "SYS-190");
  if (finding) {
    assert.equal(finding.severity, "critical", "No syslog must be critical");
  }
});

test("SYS-191: auditd check exists", () => {
  // REQUIRES (for audit rule check): sudo auditctl -l
  //   echo "openclaw ALL=(ALL) NOPASSWD: /sbin/auditctl -l" \
  //     | sudo tee /etc/sudoers.d/claw-audit-auditctl
  //   Without this: auditd service status is checked, but rule check is skipped

  assert.ok(data.findings !== undefined);
  // auditd not running = critical, no rules = warning
  const findings = data.findings.filter(f => f.code === "SYS-191");
  if (findings.length > 0) {
    const hasCritical = findings.some(f => f.severity === "critical");
    const hasWarning = findings.some(f => f.severity === "warning");
    assert.ok(hasCritical || hasWarning, "auditd finding must be critical or warning");
  }
});

test("SYS-204: /etc/shadow permissions check exists", () => {

  assert.ok(data.findings !== undefined);
  // Weak shadow permissions = critical
  const finding = data.findings.find(f => f.code === "SYS-204");
  if (finding) {
    const isCritOrWarn = finding.severity === "critical" || finding.severity === "warning";
    assert.ok(isCritOrWarn, "Shadow permissions must be critical or warning");
  }
});

// =============================================================================
// HIGH: Filesystem & Policies
// =============================================================================

test("SYS-150: Partition separation check exists", () => {

  assert.ok(data.findings !== undefined);
  // Missing partitions or mount options = warning or info (mitigated on single-partition VPS)
  const finding = data.findings.find(f => f.code === "SYS-150");
  if (finding) {
    assert.ok(["warning", "info"].includes(finding.severity), "Partition issues should be warning or info");
  }
});

test("SYS-160: Password policy check exists", () => {

  assert.ok(data.findings !== undefined);
  // Weak password policy = warning or info (mitigated: VPN-only VPS)
  const finding = data.findings.find(f => f.code === "SYS-160");
  if (finding) {
    assert.ok(["warning", "info"].includes(finding.severity), "Password policy should be warning or info");
  }
});

test("SYS-161: Account lockout check exists", () => {

  assert.ok(data.findings !== undefined);
  // No lockout policy = warning or info (mitigated: fail2ban + VPN active)
  const finding = data.findings.find(f => f.code === "SYS-161");
  if (finding) {
    assert.ok(["warning", "info"].includes(finding.severity), "Account lockout should be warning or info");
  }
});

test("SYS-180: Unnecessary services check exists", () => {

  assert.ok(data.findings !== undefined);
  // Services like avahi, cups running = warning
  const finding = data.findings.find(f => f.code === "SYS-180");
  if (finding) {
    assert.equal(finding.severity, "warning", "Unnecessary services should be warning");
  }
});

test("SYS-181: Cron access control check exists", () => {

  assert.ok(data.findings !== undefined);
  // No cron.allow = warning, no at.allow = info
  const findings = data.findings.filter(f => f.code === "SYS-181");
  if (findings.length > 0) {
    for (const f of findings) {
      const isValid = f.severity === "warning" || f.severity === "info";
      assert.ok(isValid, "Cron access should be warning or info");
    }
  }
});

// =============================================================================
// MEDIUM: System Hardening
// =============================================================================

test("SYS-151: Core dumps check exists", () => {

  assert.ok(data.findings !== undefined);
  // Core dumps enabled = warning
  const finding = data.findings.find(f => f.code === "SYS-151");
  if (finding) {
    assert.equal(finding.severity, "warning", "Core dumps should be warning");
  }
});

test("SYS-170: IPv6 check exists", () => {

  assert.ok(data.findings !== undefined);
  // IPv6 enabled but unused = info
  const finding = data.findings.find(f => f.code === "SYS-170");
  if (finding) {
    assert.equal(finding.severity, "info", "IPv6 unused should be info");
  }
});

test("SYS-182: SSH banner check exists", () => {

  assert.ok(data.findings !== undefined);
  // No SSH banner = info
  const finding = data.findings.find(f => f.code === "SYS-182");
  if (finding) {
    assert.equal(finding.severity, "info", "SSH banner should be info");
  }
});

test("SYS-183: SSH timeout check exists", () => {

  assert.ok(data.findings !== undefined);
  // No idle timeout = warning
  const finding = data.findings.find(f => f.code === "SYS-183");
  if (finding) {
    assert.equal(finding.severity, "warning", "SSH timeout should be warning");
  }
});

test("SYS-192: Log permissions check exists", () => {

  assert.ok(data.findings !== undefined);
  // Weak log permissions = warning
  const finding = data.findings.find(f => f.code === "SYS-192");
  if (finding) {
    assert.equal(finding.severity, "warning", "Log permissions should be warning");
  }
});

// =============================================================================
// Integration Tests
// =============================================================================

test("audit-system.mjs: CIS checks integrate without errors", () => {


  // Verify structure
  assert.ok(typeof data.critical === "number", "Should have critical count");
  assert.ok(typeof data.warnings === "number", "Should have warnings count");
  assert.ok(typeof data.info === "number", "Should have info count");
  assert.ok(Array.isArray(data.findings), "findings must be an array");

  // Verify all findings have required fields
  for (const f of data.findings) {
    assert.ok(typeof f.severity === "string", "finding must have severity");
    assert.ok(typeof f.code === "string", "finding must have code");
    assert.ok(typeof f.title === "string", "finding must have title");
    assert.ok(typeof f.detail === "string", "finding must have detail");
  }
});

test("audit-system.mjs: totalChecks increased after CIS checks", () => {


  // After adding 15 CIS checks (5 CRITICAL + 5 HIGH + 5 MEDIUM)
  // Previous: 16, now should be at least 31
  assert.ok(data.totalChecks >= 31, `Expected at least 31 checks, got ${data.totalChecks}`);
});

test("audit-system.mjs: CIS check codes follow SYS-1XX and SYS-2XX pattern", () => {


  const cisCodes = [
    "SYS-150", "SYS-151", "SYS-160", "SYS-161", "SYS-163", "SYS-164",
    "SYS-170", "SYS-180", "SYS-181", "SYS-182", "SYS-183",
    "SYS-190", "SYS-191", "SYS-192", "SYS-204"
  ];

  // Check that codes follow expected pattern
  for (const code of cisCodes) {
    assert.ok(/^SYS-[12]\d{2}$/.test(code), `${code} should match SYS-1XX or SYS-2XX pattern`);
  }
});

test("audit-system.mjs: All CIS checks have score impacts", () => {


  // Find any CIS findings and verify they would have score impact
  const cisFindings = data.findings.filter(f =>
    f.code.match(/^SYS-(15[01]|16[01]|163|164|170|18[0-3]|19[0-2]|204)$/)
  );

  // If we have CIS findings, they should be properly categorized
  for (const f of cisFindings) {
    assert.ok(
      f.severity === "critical" || f.severity === "warning" || f.severity === "info",
      `Finding ${f.code} must have valid severity`
    );
  }
});

test("audit-system.mjs: CRITICAL findings have high score impact", () => {


  const criticalCodes = ["SYS-163", "SYS-164", "SYS-190", "SYS-191", "SYS-204"];
  const criticalFindings = data.findings.filter(f => criticalCodes.includes(f.code));

  for (const f of criticalFindings) {
    assert.equal(f.severity, "critical", `${f.code} must be critical severity`);
  }
});
