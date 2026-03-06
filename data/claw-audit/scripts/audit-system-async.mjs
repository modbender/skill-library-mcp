#!/usr/bin/env node

/**
 * ClawAudit System Auditor (Async Optimized)
 * Performance improvements:
 * - Non-blocking subprocess execution with promisify
 * - Parallel check execution with Promise.all()
 * - File read caching to reduce I/O
 * 
 * Expected: 5-10x faster than sync version
 */

import { exec } from "child_process";
import { promisify } from "util";
import { existsSync, readFileSync } from "fs";
import { join } from "path";
import { parseFlag, createFindingCollector } from "./lib/utils.mjs";

const execAsync = promisify(exec);

const JSON_OUTPUT = parseFlag("--json");
const SHOW_FIX = parseFlag("--fix");

// --- Config ---

const HOME = process.env.HOME || "/root";
const CONFIG_PATHS = [
  join(HOME, ".openclaw", "claw-audit-config.json"),
  join(HOME, ".openclaw", "workspace", "skills", "claw-audit", "claw-audit-config.json"),
];

function loadConfig() {
  for (const p of CONFIG_PATHS) {
    if (existsSync(p)) {
      try { return JSON.parse(readFileSync(p, "utf-8")); } catch { /* ignore */ }
    }
  }
  return {};
}

const CONFIG = loadConfig();

function applyConfigMitigations(findings) {
  const mitigations = CONFIG.mitigations || {};
  for (const f of findings) {
    if (mitigations[f.code] && !f.mitigated) {
      const reason = mitigations[f.code];
      f.severity  = "info";
      f.mitigated = true;
      f.title     = `${f.title} (accepted risk)`;
      f.detail    = `${f.detail} Mitigation: ${reason}`;
    }
  }
}

// --- Async Helpers with Caching ---

const fileCache = new Map();
const commandCache = new Map();

/**
 * Async command execution with caching
 */
async function run(cmd, args = [], { sudo = false, timeout = 5000, cache = false } = {}) {
  const fullCmd = sudo ? `sudo -n ${cmd} ${args.join(' ')}` : `${cmd} ${args.join(' ')}`;
  
  if (cache && commandCache.has(fullCmd)) {
    return commandCache.get(fullCmd);
  }

  try {
    const { stdout } = await execAsync(fullCmd, { 
      timeout,
      encoding: "utf-8",
      maxBuffer: 1024 * 1024 // 1MB buffer
    });
    const result = stdout.trim();
    if (cache) commandCache.set(fullCmd, result);
    return result;
  } catch {
    if (cache) commandCache.set(fullCmd, null);
    return null;
  }
}

/**
 * Cached file reader
 */
function readFile(path) {
  if (fileCache.has(path)) {
    return fileCache.get(path);
  }
  
  try {
    const content = readFileSync(path, "utf-8");
    fileCache.set(path, content);
    return content;
  } catch {
    fileCache.set(path, null);
    return null;
  }
}

// --- Finding collector ---
const collector = createFindingCollector();
const addFinding = collector.add.bind(collector);
const addCheck = collector.check.bind(collector);

const skippedChecks = [];

function trackSkip(checkName, reason, requirement) {
  skippedChecks.push({ check: checkName, reason, requirement });
}

// --- SSH Audit ---

async function auditSSH() {
  addCheck();
  const SSH_CONFIG = "/etc/ssh/sshd_config";

  if (!existsSync(SSH_CONFIG)) {
    addFinding("info", "SYS-000", "SSH config not found", `${SSH_CONFIG} does not exist. SSH may not be installed.`);
    return;
  }

  const raw = readFile(SSH_CONFIG);
  if (!raw) {
    trackSkip("SSH Configuration (SYS-001-006)",
              "Cannot read /etc/ssh/sshd_config",
              "Add user to shadow group OR: sudo chmod 644 /etc/ssh/sshd_config");
    return;
  }

  const get = (key) => {
    const matches = [...raw.matchAll(new RegExp(`^\\s*${key}\\s+(.+)`, "gim"))];
    return matches.length > 0 ? matches[0][1].trim() : null;
  };

  // SYS-001: PermitRootLogin
  const permitRoot = get("PermitRootLogin") ?? "yes";
  if (!["no", "prohibit-password", "forced-commands-only"].includes(permitRoot.toLowerCase())) {
    addFinding(
      "critical",
      "SYS-001",
      "SSH PermitRootLogin is enabled",
      `PermitRootLogin is set to "${permitRoot}". Direct root login over SSH is a significant risk.`,
      `Set "PermitRootLogin no" in ${SSH_CONFIG} and run: sudo systemctl reload sshd`
    );
  }

  // SYS-002: PasswordAuthentication (with VPN mitigation check)
  const passwordAuth = get("PasswordAuthentication") ?? "yes";
  if (passwordAuth.toLowerCase() === "yes") {
    const ufwStatus = await run("ufw", ["status", "verbose"], { sudo: true, cache: true }) || "";
    const sshPublicAnywhere = /22.*ALLOW.*Anywhere(?!\s*\(v6\))/i.test(ufwStatus);
    const sshBehindVpn =
      /22.*192\.168\.\d+\.\d+\/\d+/i.test(ufwStatus) ||
      /22.*10\.\d+\.\d+\.\d+\/\d+/i.test(ufwStatus) ||
      /22.*172\.(1[6-9]|2\d|3[01])\.\d+\.\d+\/\d+/i.test(ufwStatus);

    if (sshBehindVpn && !sshPublicAnywhere) {
      addFinding(
        "info",
        "SYS-002",
        "SSH PasswordAuthentication enabled (VPN-only access)",
        "Password-based SSH login is allowed, but port 22 is restricted to a VPN/private subnet — not publicly accessible. Real-world risk is low.",
        `Set "PasswordAuthentication no" in ${SSH_CONFIG} if SSH keys are configured.`,
        true
      );
    } else {
      addFinding(
        "warning",
        "SYS-002",
        "SSH PasswordAuthentication enabled",
        "Password-based SSH login is allowed. Key-based authentication only is more secure.",
        `Set "PasswordAuthentication no" in ${SSH_CONFIG} — only if SSH keys are configured!`
      );
    }
  }

  // SYS-003: MaxAuthTries
  const maxAuth = parseInt(get("MaxAuthTries") ?? "6", 10);
  if (maxAuth > 4) {
    addFinding(
      "warning",
      "SYS-003",
      "SSH MaxAuthTries is high",
      `MaxAuthTries is ${maxAuth}. Values above 3-4 allow more brute-force attempts per connection.`,
      `Set "MaxAuthTries 3" in ${SSH_CONFIG}`
    );
  }

  // SYS-004: X11Forwarding
  const x11 = get("X11Forwarding") ?? "yes";
  if (x11.toLowerCase() === "yes") {
    addFinding(
      "warning",
      "SYS-004",
      "SSH X11Forwarding enabled",
      "X11Forwarding is on. Unnecessary on headless servers and increases attack surface.",
      `Set "X11Forwarding no" in ${SSH_CONFIG}`
    );
  }

  // SYS-005: AllowUsers / AllowGroups
  const allowUsers = get("AllowUsers");
  const allowGroups = get("AllowGroups");
  if (!allowUsers && !allowGroups) {
    addFinding(
      "warning",
      "SYS-005",
      "No SSH user allowlist configured",
      "Any system user can attempt SSH login. Restricting with AllowUsers limits the attack surface.",
      `Add "AllowUsers <your-user>" to ${SSH_CONFIG}`
    );
  }

  // SYS-006: Protocol
  const protocol = get("Protocol");
  if (protocol && protocol !== "2") {
    addFinding(
      "critical",
      "SYS-006",
      "SSH Protocol 1 enabled",
      "SSH Protocol 1 has known vulnerabilities. Only Protocol 2 should be used.",
      `Set "Protocol 2" in ${SSH_CONFIG}`
    );
  }
}

// --- UFW Audit ---

async function auditUFW() {
  addCheck();
  const status = await run("ufw", ["status", "verbose"], { sudo: true, cache: true });

  if (!status) {
    trackSkip("Firewall Status (SYS-010-014)",
              "Cannot run 'sudo ufw status'",
              "Add to /etc/sudoers.d/claw-audit:\n    <user> ALL=(ALL) NOPASSWD: /usr/sbin/ufw status verbose, /usr/sbin/ufw status");

    const hasIptables = await run("bash", ["-c", "iptables -L INPUT -n 2>/dev/null | grep -c 'Chain INPUT'"], { cache: true });
    const hasNftables = await run("bash", ["-c", "nft list ruleset 2>/dev/null | grep -c 'chain'"], { cache: true });
    const hasAlternative = (parseInt(hasIptables || "0", 10) > 0) || (parseInt(hasNftables || "0", 10) > 0);

    addFinding(
      hasAlternative ? "warning" : "critical",
      "SYS-010",
      hasAlternative ? "UFW not available (alternative firewall detected)" : "UFW firewall not available",
      hasAlternative
        ? "UFW is not installed, but another firewall (iptables/nftables) appears to be active. ClawAudit cannot verify its rules."
        : "No firewall detected. Install and configure UFW to protect this server.",
      "Install UFW: sudo apt install ufw && sudo ufw enable"
    );
    return;
  }

  // SYS-011: UFW active
  if (!status.includes("Status: active")) {
    addFinding(
      "critical",
      "SYS-011",
      "UFW firewall is inactive",
      "UFW is installed but not active. Server has no firewall protection.",
      "sudo ufw enable"
    );
    return;
  }

  // SYS-012: Default deny incoming
  if (!status.includes("deny (incoming)")) {
    addFinding(
      "critical",
      "SYS-012",
      "UFW default incoming policy is not deny",
      "UFW should deny all incoming connections by default and only allow explicitly needed ports.",
      "sudo ufw default deny incoming"
    );
  }

  // SYS-013: SSH exposed
  const sshFromAnywhere =
    /22.*ALLOW IN.*Anywhere(?!\s*\(v6\))/i.test(status) ||
    /22\/tcp.*ALLOW IN.*Anywhere(?!\s*\(v6\))/i.test(status);

  if (sshFromAnywhere) {
    addFinding(
      "warning",
      "SYS-013",
      "SSH port 22 is publicly accessible",
      "Port 22 is open to the internet. Consider restricting SSH to a VPN/WireGuard network only.",
      "sudo ufw delete allow 22 && sudo ufw allow from <vpn-subnet> to any port 22"
    );
  }

  // SYS-014: Dangerous ports
  const dangerousPorts = [
    { port: "3306", name: "MySQL" },
    { port: "5432", name: "PostgreSQL" },
    { port: "27017", name: "MongoDB" },
    { port: "6379", name: "Redis" },
    { port: "11211", name: "Memcached" },
    { port: "9200", name: "Elasticsearch" },
  ];

  for (const { port, name } of dangerousPorts) {
    if (new RegExp(`${port}.*ALLOW IN.*Anywhere`, "i").test(status)) {
      addFinding(
        "critical",
        "SYS-014",
        `${name} port ${port} is publicly exposed`,
        `${name} (port ${port}) is reachable from the internet. Database services should never be publicly accessible.`,
        `sudo ufw delete allow ${port} && restrict to specific IPs if remote access is needed`
      );
    }
  }
}

// --- fail2ban Audit ---

async function auditFail2ban() {
  addCheck();
  const which = await run("which", ["fail2ban-client"], { cache: true });
  if (!which) {
    trackSkip("Fail2ban Status (SYS-020-022)",
              "fail2ban not installed",
              "Install: sudo apt install fail2ban");
    addFinding(
      "warning",
      "SYS-020",
      "fail2ban not installed",
      "fail2ban is not installed. It protects against brute-force attacks by banning repeat offenders.",
      "sudo apt install fail2ban"
    );
    return;
  }

  const active = await run("systemctl", ["is-active", "fail2ban"], { cache: true });
  if (active !== "active") {
    addFinding(
      "critical",
      "SYS-021",
      "fail2ban is not running",
      `fail2ban service status: "${active}". Brute-force protection is disabled.`,
      "sudo systemctl enable --now fail2ban"
    );
    return;
  }

  const sshdStatus = await run("fail2ban-client", ["status", "sshd"], { sudo: true });
  if (!sshdStatus) {
    addFinding(
      "warning",
      "SYS-022",
      "fail2ban SSH jail (sshd) not active",
      "fail2ban is running but the sshd jail is not active. SSH brute-force attempts are not being blocked.",
      "Enable sshd jail in /etc/fail2ban/jail.local: [sshd]\\nenabled = true"
    );
  }
}

// --- WireGuard Audit ---

async function auditWireGuard() {
  addCheck();
  const wgShow = await run("wg", ["show"], { sudo: true, cache: true });

  if (!wgShow) {
    const wgInstalled = await run("which", ["wg"], { cache: true });
    if (wgInstalled && !await run("wg", ["show"], { cache: true })) {
      trackSkip("WireGuard Status (SYS-030-032)",
                "Cannot run 'sudo wg show'",
                "Add to /etc/sudoers.d/claw-audit:\n    <user> ALL=(ALL) NOPASSWD: /usr/bin/wg show");
    }

    const ufwStatus = await run("ufw", ["status"], { sudo: true, cache: true }) || "";
    const sshPublic = /22.*ALLOW.*Anywhere/i.test(ufwStatus);

    if (sshPublic) {
      addFinding(
        "info",
        "SYS-030",
        "WireGuard not running — SSH is publicly accessible",
        "No WireGuard tunnel detected. Placing SSH behind a VPN tunnel significantly reduces attack surface.",
        "Consider setting up WireGuard and restricting SSH to the VPN subnet only."
      );
    }
    return;
  }

  const interfaces = wgShow.match(/^interface:\s+(\S+)/gm) || [];
  if (interfaces.length === 0) return;

  const ufwStatus = await run("ufw", ["status", "verbose"], { sudo: true, cache: true }) || "";
  const sshPublic = /22.*ALLOW IN.*Anywhere(?! \()/i.test(ufwStatus);
  const sshBehindVpn =
    /22.*192\.168\.\d+\.\d+\/\d+/i.test(ufwStatus) ||
    /22.*10\.\d+\.\d+\.\d+\/\d+/i.test(ufwStatus) ||
    /22.*172\.(1[6-9]|2\d|3[01])\.\d+\.\d+\/\d+/i.test(ufwStatus);

  if (sshPublic && !sshBehindVpn) {
    addFinding(
      "warning",
      "SYS-031",
      "WireGuard running but SSH still publicly accessible",
      "WireGuard is active but SSH port 22 is still open to the internet. Restrict SSH to the WireGuard subnet for full protection.",
      "sudo ufw delete allow 22 && sudo ufw allow from <wg-subnet> to any port 22"
    );
  }

  if (wgShow.includes("0.0.0.0/0")) {
    addFinding(
      "info",
      "SYS-032",
      "WireGuard full-tunnel detected",
      "A WireGuard peer has AllowedIPs = 0.0.0.0/0. This routes all traffic through the tunnel (full-tunnel). Verify this is intentional.",
      "Change AllowedIPs to a specific subnet (e.g. 10.0.0.0/24) for split-tunnel if full-tunnel is not desired."
    );
  }
}

// --- Auto-Updates Audit ---

async function auditAutoUpdates() {
  addCheck();
  const unattended = await run("bash", ["-c", "dpkg -l unattended-upgrades 2>/dev/null | grep '^ii'"], { cache: true });
  if (!unattended) {
    addFinding(
      "warning",
      "SYS-040",
      "Automatic security updates not installed",
      "unattended-upgrades is not installed. Security patches won't be applied automatically.",
      "sudo apt install unattended-upgrades && sudo dpkg-reconfigure unattended-upgrades"
    );
    return;
  }

  const timerActive = await run("systemctl", ["is-active", "apt-daily-upgrade.timer"], { cache: true });
  if (timerActive !== "active") {
    addFinding(
      "warning",
      "SYS-041",
      "Automatic update timer is not active",
      "unattended-upgrades is installed but the apt-daily-upgrade timer is not running.",
      "sudo systemctl enable --now apt-daily-upgrade.timer"
    );
  }
}

// --- Open Ports Audit ---

async function auditOpenPorts() {
  addCheck();
  const ss = await run("ss", ["-tlnup"], { cache: true });
  if (!ss) return;

  const lines = ss.split("\n").slice(1);
  const publicListeners = [];

  for (const line of lines) {
    if (!line.trim()) continue;
    if (/\s(0\.0\.0\.0|\*|\[::\]):(\d+)\s/.test(line)) {
      const portMatch = line.match(/(?:0\.0\.0\.0|\*|\[::\]):(\d+)/);
      if (portMatch) {
        const port = parseInt(portMatch[1], 10);
        if (port > 1024 && port < 32768) {
          const processMatch = line.match(/users:\(\("([^"]+)"/);
          const processName = processMatch ? processMatch[1] : "unknown";
          publicListeners.push({ port, processName });
        }
      }
    }
  }

  for (const { port, processName } of publicListeners) {
    const knownSafe = ["openclaw-gatewa", "sshd"];
    if (!knownSafe.includes(processName)) {
      addFinding(
        "warning",
        "SYS-050",
        `Unexpected service on port ${port}`,
        `Process "${processName}" is listening on port ${port} (all interfaces). Verify this is intentional.`,
        `Check with: ss -tlnup | grep :${port} — then firewall or stop if not needed`
      );
    }
  }
}

// --- sysctl Hardening ---

async function auditSysctl() {
  addCheck();
  const params = [
    { key: "net.ipv4.ip_forward",                 expected: "0" },
    { key: "net.ipv4.conf.all.rp_filter",          expected: "1" },
    { key: "net.ipv4.tcp_syncookies",              expected: "1" },
    { key: "net.ipv4.conf.all.accept_redirects",   expected: "0" },
    { key: "net.ipv6.conf.all.accept_redirects",   expected: "0" },
    { key: "net.ipv4.conf.all.send_redirects",     expected: "0" },
    { key: "kernel.randomize_va_space",            expected: "2" },
  ];

  const checks = params.map(async ({ key, expected }) => {
    const val = await run("sysctl", ["-n", key], { cache: true });
    if (val !== null && val.trim() !== expected) {
      return `${key}=${val.trim()} (want ${expected})`;
    }
    return null;
  });

  const results = await Promise.all(checks);
  const wrong = results.filter(Boolean);

  if (wrong.length === 0) return;

  const severity = wrong.length >= 3 ? "critical" : "warning";
  addFinding(
    severity,
    "SYS-060",
    `Kernel hardening: ${wrong.length} insecure sysctl value${wrong.length > 1 ? "s" : ""}`,
    `Suboptimal parameters: ${wrong.join("; ")}`,
    `Add to /etc/sysctl.d/99-hardening.conf then run: sudo sysctl --system`
  );
}

// --- Run All Checks in Parallel ---

async function runAudit() {
  if (!JSON_OUTPUT) {
    console.log("\n🛡️  ClawAudit System Auditor (Async Optimized)\n");
    console.log("Running checks in parallel...\n");
  }

  const startTime = Date.now();

  // Group 1: Independent checks (can run in parallel)
  await Promise.all([
    auditSSH(),
    auditUFW(),
    auditFail2ban(),
    auditWireGuard(),
    auditAutoUpdates(),
    auditOpenPorts(),
    auditSysctl(),
  ]);

  const elapsed = Date.now() - startTime;

  // Apply mitigations
  applyConfigMitigations(collector.getAll());

  // --- Output ---
  const findings = collector.getAll();
  const counts = collector.countBySeverity();

  if (JSON_OUTPUT) {
    const summary = {
      critical: counts.critical,
      warnings: counts.warnings,
      info: counts.info,
      totalChecks: collector.getTotalChecks(),
      passed: collector.getPassed(),
      skipped: skippedChecks.length,
      executionTimeMs: elapsed,
      findings,
      skippedChecks,
    };
    console.log(JSON.stringify(summary, null, 2));
    return;
  }

  if (findings.length === 0) {
    console.log(`✅ System looks well-hardened! No issues found. (${elapsed}ms)\n`);
    return;
  }

  const severityIcon = { critical: "🔴", warning: "🟡", info: "🔵" };
  const severityLabel = { critical: "CRITICAL", warning: "WARNING", info: "INFO" };

  collector.sort();

  for (const f of findings) {
    console.log(`${severityIcon[f.severity]} ${severityLabel[f.severity]}: ${f.code} — ${f.title}`);
    console.log(`   ${f.detail}`);
    if (SHOW_FIX && f.fix) {
      console.log(`   💡 Fix: ${f.fix}`);
    }
    console.log();
  }

  const { critical: crit, warnings: warn, info } = counts;

  console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
  console.log(`📊 System Audit: ${crit} critical, ${warn} warnings, ${info} info (${elapsed}ms)`);
  if (skippedChecks.length > 0) {
    console.log(`⊘ ${skippedChecks.length} check${skippedChecks.length > 1 ? "s" : ""} skipped due to missing privileges`);
  }
  if (!SHOW_FIX && findings.length > 0) {
    console.log("   Run with --fix to see remediation steps.");
  }
  console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n");
}

runAudit().catch(err => {
  console.error("Fatal error:", err);
  process.exit(1);
});
