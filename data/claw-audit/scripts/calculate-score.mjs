#!/usr/bin/env node

/**
 * ClawAudit Security Score Calculator
 * Combines findings from skill scan, config audit, and system audit into a 0-100 score.
 *
 * Usage:
 *   node calculate-score.mjs          # Interactive output
 *   node calculate-score.mjs --json   # JSON output
 */

import { execSync } from "child_process";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";
import { COLORS, parseFlag } from "./lib/utils.mjs";

const __dirname = dirname(fileURLToPath(import.meta.url));
const JSON_OUTPUT = parseFlag("--json");
const { BOLD, GREEN, YELLOW, RED, GRAY, RESET } = COLORS;

// --- Score weights ---
const SCORE_IMPACT = {
  // Critical findings from skill scanner
  "CRIT-001": -20,  // Shell execution
  "CRIT-002": -15,  // Credential access
  "CRIT-003": -25,  // Reverse shell
  "CRIT-004": -20,  // Prompt injection
  "CRIT-005": -25,  // External binary exec

  // Warnings from skill scanner
  "WARN-005": -8,   // Obfuscated content
  "WARN-007": -10,  // Exfiltration indicators
  "WARN-008": -8,   // Suspicious prerequisites
  "WARN-009": -10,  // Typosquat indicators
  "WARN-010": -10,  // Hidden file operations

  // Config audit findings
  "WARN-001": -15,  // Gateway exposed
  "WARN-002": -15,  // Open DM policy
  "WARN-003": -8,   // No sandbox
  "WARN-004": -10,  // Browser exposed
  "WARN-006": -8,   // Loose file permissions
  "WARN-011": -3,   // Invalid config JSON
  "WARN-012": -20,  // No auth on exposed gateway
  "WARN-013": -8,   // Unrestricted exec
  "WARN-014": -8,   // Unrestricted fs

  // Info items
  "INFO-001": -2,   // Unverified source
  "INFO-002": -1,   // No VT scan
  "INFO-003": -3,   // Excessive permissions
  "INFO-004": -3,   // No allowlist

  // System audit findings
  "SYS-001": -20,   // SSH PermitRootLogin enabled
  "SYS-002": -8,    // SSH PasswordAuthentication enabled
  "SYS-003": -5,    // SSH MaxAuthTries too high
  "SYS-004": -3,    // SSH X11Forwarding enabled
  "SYS-005": -5,    // No SSH user allowlist
  "SYS-006": -25,   // SSH Protocol 1
  "SYS-010": -20,   // UFW not available
  "SYS-011": -25,   // UFW inactive
  "SYS-012": -15,   // UFW default not deny
  "SYS-013": -10,   // SSH publicly accessible
  "SYS-014": -20,   // Dangerous port open (DB etc.)
  "SYS-020": -10,   // fail2ban not installed
  "SYS-021": -15,   // fail2ban not running
  "SYS-022": -8,    // fail2ban SSH jail inactive
  "SYS-030": -5,    // WireGuard not running, SSH public
  "SYS-031": -8,    // WireGuard running but SSH still public
  "SYS-032": -3,    // WireGuard full-tunnel (info)
  "SYS-040": -8,    // Auto-updates not installed
  "SYS-041": -5,    // Auto-update timer inactive
  "SYS-050": -5,    // Unexpected open port

  // New system checks
  "SYS-060": -8,    // sysctl hardening (warning), -15 if critical handled by severity
  "SYS-061": -5,    // AppArmor inactive (warning), -2 (info)
  "SYS-062": -8,    // authorized_keys (warning), -2 (info)
  "SYS-063": -5,    // NTP not synced
  "SYS-064": -2,    // Swap not encrypted (info)
  "SYS-065": -8,    // World-writable missing sticky bit
  "SYS-066": -10,   // Unexpected SUID/SGID binaries

  // Docker & Container Security (Phase 1)
  "SYS-070": -25,   // Docker daemon exposed on TCP
  "SYS-071": -25,   // Privileged containers
  "SYS-072": -25,   // Docker socket mounted in container

  // Process Isolation (Phase 1)
  "SYS-080": -25,   // OpenClaw running as root
  "SYS-081": -10,   // Container sharing host PID namespace
  "SYS-082": -5,    // No resource limits

  // Network Segmentation (Phase 1)
  "SYS-100": -10,   // Cloud metadata service accessible
  "SYS-101": -2,    // No egress filtering (info)
  "SYS-102": -1,    // Using public DNS (info)

  // CRITICAL: System Access & Authentication
  "SYS-163": -25,   // Empty passwords
  "SYS-164": -20,   // Root PATH integrity
  "SYS-190": -25,   // rsyslog not running
  "SYS-191": -20,   // auditd not running
  "SYS-204": -20,   // /etc/shadow weak permissions

  // HIGH: Filesystem & Policies
  "SYS-150": -10,   // Partition issues
  "SYS-160": -10,   // Weak password policy
  "SYS-161": -15,   // No account lockout
  "SYS-180": -8,    // Unnecessary services running
  "SYS-181": -5,    // Cron access not restricted

  // MEDIUM: System Hardening
  "SYS-151": -5,    // Core dumps not disabled
  "SYS-170": -2,    // IPv6 enabled but unused (info)
  "SYS-182": -2,    // No SSH banner (info)
  "SYS-183": -8,    // SSH idle timeout
  "SYS-192": -8,    // Log file permissions

  // New config checks
  "WARN-020": -15,  // Dangerous cron job pattern (critical)
  "WARN-021": -5,   // Concurrent LLM cron job schedule conflicts (warning)
  "WARN-022": -8,   // agentTurn jobs without bestEffortDeliver (warning)
  "INFO-010": -1,   // Paired devices (info), -5 (warning if >5)
  "INFO-011": -2,   // No sub-agent limits

  // System info / skipped checks
  "SYS-000": -1,    // SSH config not found (info)

  // Docker security (SYS-07x)
  "SYS-070": -25,   // Docker daemon exposed on TCP without TLS (critical)
  "SYS-071": -20,   // Privileged containers running (critical)
  "SYS-072": -20,   // Docker socket mounted into containers (critical)

  // Process isolation (SYS-08x)
  "SYS-080": -20,   // OpenClaw running as root (critical)
  "SYS-081": -10,   // Containers sharing host PID namespace (warning)
  "SYS-082": -5,    // OpenClaw unlimited resource limits (warning)

  // Network segmentation (SYS-10x)
  "SYS-100": -10,   // Cloud metadata service accessible (warning)
  "SYS-101": -2,    // No egress filtering (info)
  "SYS-102": -1,    // Using public DNS servers (info)

  // Filesystem & kernel hardening (SYS-15x)
  "SYS-150": -5,    // Filesystem partitioning issues (warning)
  "SYS-151": -5,    // Core dumps not disabled (warning)

  // Account & password policy (SYS-16x)
  "SYS-160": -8,    // Weak password policy (warning)
  "SYS-161": -8,    // No account lockout policy (warning)
  "SYS-163": -25,   // Accounts with empty passwords (critical)
  "SYS-164": -20,   // Root PATH contains unsafe directories (critical)

  // Misc system (SYS-17x)
  "SYS-170": -1,    // IPv6 enabled but not used (info)

  // Access control & SSH hardening (SYS-18x)
  "SYS-180": -5,    // Unnecessary services running (warning)
  "SYS-181": -3,    // /etc/cron.allow not configured (warning/info)
  "SYS-182": -2,    // SSH login banner not configured (info)
  "SYS-183": -5,    // SSH idle timeout not configured (warning)

  // Logging & audit (SYS-19x)
  "SYS-190": -15,   // System logging daemon not running (critical)
  "SYS-191": -10,   // auditd not running (critical)
  "SYS-192": -8,    // Log files with weak permissions (warning)

  // File permissions (SYS-20x)
  "SYS-204": -15,   // /etc/shadow weak permissions (critical)

  // File integrity checks
  "INTEG-001": -3,  // No baseline established (info)
  "INTEG-002": -15, // Cognitive file changed/deleted since baseline (warning)
  "INTEG-003": -2,  // New cognitive file since baseline (info)
};

// --- Collect findings ---
function runScanAndAudit() {
  let scanFindings = [];
  let auditFindings = [];
  let systemFindings = [];
  let integrityFindings = [];

  try {
    const scanOut = execSync(`bash "${resolve(__dirname, "scan-skills.sh")}" --json 2>/dev/null`, {
      encoding: "utf-8",
      timeout: 30000,
    });
    const scanData = JSON.parse(scanOut);
    scanFindings = scanData.findings || [];
  } catch {
    // No skills found or scan failed — that's OK
  }

  let auditMeta = { totalChecks: 0, passed: 0 };
  let systemMeta = { totalChecks: 0, passed: 0 };
  let integrityMeta = { totalChecks: 0, passed: 0 };
  let scanMeta = { totalChecks: 0, passed: 0 };

  try {
    const auditOut = execSync(`node "${resolve(__dirname, "audit-config.mjs")}" --json 2>/dev/null`, {
      encoding: "utf-8",
      timeout: 15000,
    });
    const auditData = JSON.parse(auditOut);
    auditFindings = auditData.findings || [];
    auditMeta = { totalChecks: auditData.totalChecks ?? 0, passed: auditData.passed ?? 0 };
  } catch {
    // Config not found or audit failed
  }

  try {
    const systemOut = execSync(`node "${resolve(__dirname, "audit-system.mjs")}" --json 2>/dev/null`, {
      encoding: "utf-8",
      timeout: 15000,
    });
    const systemData = JSON.parse(systemOut);
    systemFindings = systemData.findings || [];
    systemMeta = { totalChecks: systemData.totalChecks ?? 0, passed: systemData.passed ?? 0 };
  } catch {
    // System audit failed — skip
  }

  try {
    const integrityOut = execSync(`node "${resolve(__dirname, "check-integrity.mjs")}" --json 2>/dev/null`, {
      encoding: "utf-8",
      timeout: 10000,
    });
    const integrityData = JSON.parse(integrityOut);
    integrityFindings = integrityData.findings || [];
    integrityMeta = { totalChecks: integrityData.totalChecks ?? 0, passed: integrityData.passed ?? 0 };
  } catch {
    // Integrity check failed — skip
  }

  return { scanFindings, auditFindings, systemFindings, integrityFindings, auditMeta, systemMeta, integrityMeta, scanMeta };
}

// --- Calculate Score ---
function calculateScore(scanFindings, auditFindings, systemFindings, integrityFindings = []) {
  let score = 100;
  const deductions = [];

  // Apply mitigated reduction: 25% of original impact (min -1) when compensating control exists
  const applyImpact = (base, mitigated) =>
    mitigated ? Math.max(-1, Math.round(base * 0.25)) : base;

  // Process scan findings
  for (const f of scanFindings) {
    const base = SCORE_IMPACT[f.code] || -5;
    const impact = applyImpact(base, f.mitigated);
    score += impact;
    deductions.push({
      code: f.code,
      label: f.label || f.title,
      impact,
      source: "skill-scan",
      skill: f.skill,
      ...(f.mitigated && { mitigated: true }),
    });
  }

  // Process config audit findings
  for (const f of auditFindings) {
    const base = SCORE_IMPACT[f.code] || -3;
    const impact = applyImpact(base, f.mitigated);
    score += impact;
    deductions.push({
      code: f.code,
      label: f.title,
      impact,
      source: "config-audit",
      ...(f.mitigated && { mitigated: true }),
    });
  }

  // Process system audit findings
  for (const f of systemFindings) {
    const base = SCORE_IMPACT[f.code] || -3;
    const impact = applyImpact(base, f.mitigated);
    score += impact;
    deductions.push({
      code: f.code,
      label: f.title,
      impact,
      source: "system-audit",
      ...(f.mitigated && { mitigated: true }),
    });
  }

  // Process file integrity findings
  for (const f of integrityFindings) {
    const base = SCORE_IMPACT[f.code] || -3;
    const impact = applyImpact(base, f.mitigated);
    score += impact;
    deductions.push({
      code: f.code,
      label: f.title,
      impact,
      source: "integrity",
      ...(f.mitigated && { mitigated: true }),
    });
  }

  // Clamp to 0-100
  score = Math.max(0, Math.min(100, score));

  return { score, deductions };
}

// --- Grade ---
function getGrade(score) {
  if (score >= 90) return { grade: "A", color: GREEN, emoji: "🟢", label: "Excellent" };
  if (score >= 70) return { grade: "B", color: GREEN, emoji: "🟢", label: "Good" };
  if (score >= 50) return { grade: "C", color: YELLOW, emoji: "🟡", label: "Fair" };
  if (score >= 30) return { grade: "D", color: RED, emoji: "🟠", label: "Poor" };
  return { grade: "F", color: RED, emoji: "🔴", label: "Critical" };
}

// --- Main ---
function main() {
  const { scanFindings, auditFindings, systemFindings, integrityFindings, auditMeta, systemMeta, integrityMeta, scanMeta } = runScanAndAudit();
  const { score, deductions } = calculateScore(scanFindings, auditFindings, systemFindings, integrityFindings);
  const { grade, color, emoji, label } = getGrade(score);

  if (JSON_OUTPUT) {
    console.log(JSON.stringify({
      score,
      grade,
      label,
      deductions,
      scan_findings: scanFindings.length,
      audit_findings: auditFindings.length,
      system_findings: systemFindings.length,
      integrity_findings: integrityFindings.length,
    }, null, 2));
    return;
  }

  // --- Pretty Output ---
  console.log();
  console.log(`${BOLD}🛡️  ClawAudit Security Score${RESET}`);
  console.log();

  // Score bar
  const barWidth = 40;
  const filled = Math.round((score / 100) * barWidth);
  const empty = barWidth - filled;
  const bar = `${color}${"█".repeat(filled)}${GRAY}${"░".repeat(empty)}${RESET}`;

  console.log(`   ${bar}  ${color}${BOLD}${score}/100${RESET}  ${emoji} ${label} (${grade})`);
  console.log();

  // Top deductions
  if (deductions.length > 0) {
    const sorted = [...deductions].sort((a, b) => a.impact - b.impact);
    const top = sorted.slice(0, 5);

    console.log(`${BOLD}📉 Biggest Score Impacts:${RESET}`);
    for (const d of top) {
      const skillInfo = d.skill ? ` (${d.skill})` : "";
      const mitigatedTag = d.mitigated ? ` ${GRAY}[mitigated]${RESET}` : "";
      const icon = d.mitigated ? "⚪" : d.impact >= -5 ? "🔵" : d.impact >= -10 ? "🟡" : "🔴";
      console.log(`   ${icon} ${d.impact} pts — ${d.code}: ${d.label}${skillInfo}${mitigatedTag}`);
    }
    console.log();

    // Quick wins
    const quickWinCodes = [
      "WARN-001", "WARN-002", "WARN-003", "WARN-006", "WARN-012",
      "SYS-011", "SYS-012", "SYS-013", "SYS-001", "SYS-021",
      "SYS-060", "SYS-061", "SYS-063", "SYS-065", "SYS-066", "WARN-020", "INTEG-002",
    ];
    const quickWins = sorted.filter((d) => quickWinCodes.includes(d.code) && !d.mitigated).slice(0, 3);

    if (quickWins.length > 0) {
      console.log(`${BOLD}⚡ Quick Wins to Improve Your Score:${RESET}`);
      for (const qw of quickWins) {
        const potential = Math.abs(qw.impact);
        const fixCmd = qw.source === "system-audit"
          ? "node scripts/audit-system.mjs --fix"
          : "node scripts/audit-config.mjs --fix";
        console.log(`   💡 Fix ${qw.code} → +${potential} points  ${GRAY}(${fixCmd})${RESET}`);
      }
      console.log();
    }
  } else {
    console.log(`   ${color}✅ No issues found. Your setup is looking great!${RESET}`);
    console.log();
  }

  // --- Check Summary ---
  // Only critical/warning non-mitigated findings count as real failures.
  // Info findings and mitigated findings are not failures — shown separately.
  function classify(findings) {
    // Mitigated findings are stored as severity "info" + mitigated:true (compensating control present)
    // Info findings are severity "info" without mitigated flag (genuinely informational)
    return {
      failed:    findings.filter(f => (f.severity === "critical" || f.severity === "warning") && !f.mitigated),
      mitigated: findings.filter(f => f.mitigated),
      info:      findings.filter(f => f.severity === "info" && !f.mitigated),
    };
  }

  const cats = [
    { label: "Config",    total: auditMeta.totalChecks,     ...classify(auditFindings) },
    { label: "System",    total: systemMeta.totalChecks,    ...classify(systemFindings) },
    { label: "Integrity", total: integrityMeta.totalChecks, ...classify(integrityFindings) },
    { label: "Skills",    total: scanMeta.totalChecks,      ...classify(scanFindings) },
  ].filter(c => c.total > 0);

  const totalChecksAll = cats.reduce((s, c) => s + c.total, 0);
  const totalFailed    = cats.reduce((s, c) => s + c.failed.length, 0);

  console.log(`${GRAY}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}`);
  const headerStatus = totalFailed > 0
    ? `${RED}${totalFailed} failed${RESET}`
    : `${GREEN}all checks passed${RESET}`;
  console.log(`${BOLD}📋 Check Summary (${totalChecksAll} checks): ${headerStatus}${RESET}`);

  for (const c of cats) {
    const failStr  = c.failed.length    > 0 ? ` ${RED}✗ ${c.failed.length} failed${RESET}`       : ` ${GREEN}✓ passed${RESET}`;
    const mitigStr = c.mitigated.length > 0 ? `  ${GRAY}${c.mitigated.length} warn${RESET}`      : "";
    const infoStr  = c.info.length      > 0 ? `  ${GRAY}${c.info.length} info${RESET}`           : "";
    console.log(`   ${GRAY}${c.label.padEnd(10)}${RESET} ${String(c.total).padStart(2)} checks${failStr}${mitigStr}${infoStr}`);

    // List rule codes + short titles for non-passed findings
    for (const f of c.failed) {
      console.log(`      ${RED}✗${RESET} ${BOLD}${f.code}${RESET} ${GRAY}${f.title}${RESET}`);
    }
    for (const f of c.mitigated) {
      console.log(`      ${GRAY}warn ${f.code} ${f.title}${RESET}`);
    }
    for (const f of c.info) {
      console.log(`      ${GRAY}ℹ ${f.code} ${f.title}${RESET}`);
    }
  }
  console.log();
}

main();
