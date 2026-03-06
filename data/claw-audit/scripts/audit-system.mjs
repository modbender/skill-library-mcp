#!/usr/bin/env node

/**
 * ClawAudit System Auditor
 * Audits the underlying server/OS for security hardening issues.
 *
 * Checks: SSH config, UFW firewall, fail2ban, WireGuard, auto-updates, open ports.
 *
 * Usage:
 *   node audit-system.mjs            # Run full system audit
 *   node audit-system.mjs --json     # Output as JSON
 *   node audit-system.mjs --fix      # Show fix commands
 */

import { execFileSync, execSync } from "child_process";
import { existsSync, readFileSync } from "fs";
import { join } from "path";
import { parseFlag, createFindingCollector } from "./lib/utils.mjs";

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

/**
 * Apply user-defined mitigations from claw-audit-config.json.
 * Matched findings are downgraded to "info" + flagged as mitigated.
 */
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

// --- Helpers ---

/**
 * Safe command execution using execFileSync (no shell).
 * Prevents shell injection by passing arguments as an array.
 */
function run(cmd, args = [], { sudo = false, timeout = 5000 } = {}) {
  try {
    const fullCmd = sudo ? "sudo" : cmd;
    const fullArgs = sudo ? ["-n", cmd, ...args] : args;
    return execFileSync(fullCmd, fullArgs, {
      encoding: "utf-8",
      stdio: ["pipe", "pipe", "pipe"],
      timeout,
    }).trim();
  } catch {
    return null;
  }
}

/** Shell execution for hardcoded pipelines only. NEVER pass dynamic input. */
function runShell(shellCmd, { timeout = 5000 } = {}) {
  try {
    return execSync(shellCmd, {
      encoding: "utf-8",
      stdio: ["pipe", "pipe", "pipe"],
      timeout,
    }).trim();
  } catch {
    return null;
  }
}

/** Run docker command with automatic sudo fallback. */
function runDocker(args, { timeout = 5000 } = {}) {
  return run("docker", args, { timeout }) || run("docker", args, { sudo: true, timeout });
}

function readFile(path) {
  try {
    return readFileSync(path, "utf-8");
  } catch {
    return null;
  }
}

// --- Finding collector ---
const collector = createFindingCollector();
const addFinding = collector.add.bind(collector);
const addCheck = collector.check.bind(collector);

// --- Skip tracker for privilege-required checks ---
const skippedChecks = [];

function trackSkip(checkName, reason, requirement) {
  skippedChecks.push({ check: checkName, reason, requirement });
}

// --- SSH Audit ---

function auditSSH() {
  addCheck();
  const SSH_CONFIG = "/etc/ssh/sshd_config";

  if (!existsSync(SSH_CONFIG)) {
    addFinding("info", "SYS-000", "SSH config not found", `${SSH_CONFIG} does not exist. SSH may not be installed.`);
    return;
  }

  const raw = readFile(SSH_CONFIG) || "";
  if (!raw) {
    trackSkip("SSH Configuration (SYS-001-006)",
              "Cannot read /etc/ssh/sshd_config",
              "Add user to shadow group OR: sudo chmod 644 /etc/ssh/sshd_config");
    return;
  }

  // Helper: get effective value — sshd uses the FIRST occurrence of a directive
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

  // SYS-002: PasswordAuthentication
  const passwordAuth = get("PasswordAuthentication") ?? "yes";
  if (passwordAuth.toLowerCase() === "yes") {
    // Mitigating check: is SSH port 22 restricted to a private/VPN subnet only?
    const ufwStatus = run("ufw", ["status", "verbose"], { sudo: true }) || "";
    const sshPublicAnywhere = /22.*ALLOW.*Anywhere(?!\s*\(v6\))/i.test(ufwStatus);
    const sshBehindVpn =
      /22.*192\.168\.\d+\.\d+\/\d+/i.test(ufwStatus) ||
      /22.*10\.\d+\.\d+\.\d+\/\d+/i.test(ufwStatus) ||
      /22.*172\.(1[6-9]|2\d|3[01])\.\d+\.\d+\/\d+/i.test(ufwStatus) ||
      /22.*fd[0-9a-f]{2}:/i.test(ufwStatus);

    if (sshBehindVpn && !sshPublicAnywhere) {
      addFinding(
        "info",
        "SYS-002",
        "SSH PasswordAuthentication enabled (VPN-only access)",
        "Password-based SSH login is allowed, but port 22 is restricted to a VPN/private subnet — not publicly accessible. Real-world risk is low.",
        `Set "PasswordAuthentication no" in ${SSH_CONFIG} if SSH keys are configured.`,
        true // mitigated
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

  // SYS-005: AllowUsers / AllowGroups restriction
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

  // SYS-006: Protocol (legacy)
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

function auditUFW() {
  addCheck();
  const status = run("ufw", ["status", "verbose"], { sudo: true });

  if (!status) {
    trackSkip("Firewall Status (SYS-010-014)",
              "Cannot run 'sudo ufw status'",
              "Add to /etc/sudoers.d/claw-audit:\n    <user> ALL=(ALL) NOPASSWD: /usr/sbin/ufw status verbose, /usr/sbin/ufw status");

    // Check if another firewall (iptables/nftables) is active before flagging as critical
    const hasIptables = runShell("iptables -L INPUT -n 2>/dev/null | grep -c 'Chain INPUT'");
    const hasNftables = runShell("nft list ruleset 2>/dev/null | grep -c 'chain'");
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

  // SYS-013: SSH exposed to the world (exclude IPv6-only entries)
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

  // SYS-014: Common dangerous ports open
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

function auditFail2ban() {
  addCheck();
  // Check if installed
  const which = run("which", ["fail2ban-client"]);
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

  // Check if running
  const active = run("systemctl", ["is-active", "fail2ban"]);
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

  // Check SSH jail
  const sshdStatus = run("fail2ban-client", ["status", "sshd"], { sudo: true });
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

function auditWireGuard() {
  addCheck();
  const wgShow = run("wg", ["show"], { sudo: true });

  if (!wgShow) {
    // Check if it's a permission issue or WireGuard not installed/running
    const wgInstalled = run("which", ["wg"]);
    if (wgInstalled && !run("wg", ["show"])) {
      trackSkip("WireGuard Status (SYS-030-032)",
                "Cannot run 'sudo wg show'",
                "Add to /etc/sudoers.d/claw-audit:\n    <user> ALL=(ALL) NOPASSWD: /usr/bin/wg show");
    }

    // WireGuard not running — only an issue if SSH is publicly exposed
    // Check SSH UFW rule
    const ufwStatus = run("ufw", ["status"], { sudo: true }) || "";
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

  // WireGuard is running
  const interfaces = wgShow.match(/^interface:\s+(\S+)/gm) || [];
  if (interfaces.length === 0) return;

  // Check if SSH is restricted to WireGuard subnet
  const ufwStatus = run("ufw", ["status", "verbose"], { sudo: true }) || "";
  const sshPublic =
    /22.*ALLOW IN.*Anywhere(?! \()/i.test(ufwStatus);
  // Detect SSH restricted to any private/VPN subnet (RFC1918 + custom ranges)
  // UFW status format: "22   ALLOW IN   <from-subnet>" — port comes before subnet
  const sshBehindVpn =
    /22.*192\.168\.\d+\.\d+\/\d+/i.test(ufwStatus) ||
    /22.*10\.\d+\.\d+\.\d+\/\d+/i.test(ufwStatus) ||
    /22.*172\.(1[6-9]|2\d|3[01])\.\d+\.\d+\/\d+/i.test(ufwStatus) ||
    /22.*fd[0-9a-f]{2}:/i.test(ufwStatus);

  if (sshPublic && !sshBehindVpn) {
    addFinding(
      "warning",
      "SYS-031",
      "WireGuard running but SSH still publicly accessible",
      "WireGuard is active but SSH port 22 is still open to the internet. Restrict SSH to the WireGuard subnet for full protection.",
      "sudo ufw delete allow 22 && sudo ufw allow from <wg-subnet> to any port 22"
    );
  }

  // Check for full-tunnel (AllowedIPs 0.0.0.0/0) on server role
  if (wgShow.includes("0.0.0.0/0")) {
    addFinding(
      "info",
      "SYS-032",
      "WireGuard full-tunnel detected",
      "A WireGuard peer has AllowedIPs = 0.0.0.0/0. This routes all traffic through the tunnel (full-tunnel). Verify this is intentional.",
      "Change AllowedIPs to a specific subnet (e.g. 10.0.0.0/24 or 192.168.x.x/24) for split-tunnel if full-tunnel is not desired."
    );
  }
}

// --- Auto-Updates Audit ---

function auditAutoUpdates() {
  addCheck();
  const unattended = runShell("dpkg -l unattended-upgrades 2>/dev/null | grep '^ii'");
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

  // Check if enabled
  const timerActive = run("systemctl", ["is-active", "apt-daily-upgrade.timer"]);
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

function auditOpenPorts() {
  addCheck();
  const ss = run("ss", ["-tlnup"]);
  if (!ss) return;

  // Find services listening on 0.0.0.0 or :: (all interfaces, not just loopback)
  const lines = ss.split("\n").slice(1); // skip header
  const publicListeners = [];

  for (const line of lines) {
    if (!line.trim()) continue;
    // Match lines with 0.0.0.0:PORT or *:PORT (not 127.x or ::1)
    if (/\s(0\.0\.0\.0|\*|\[::\]):(\d+)\s/.test(line)) {
      const portMatch = line.match(/(?:0\.0\.0\.0|\*|\[::\]):(\d+)/);
      if (portMatch) {
        const port = parseInt(portMatch[1], 10);
        // Exclude well-known managed ports and ephemeral range
        if (port > 1024 && port < 32768) {
          const processMatch = line.match(/users:\(\("([^"]+)"/);
          const processName = processMatch ? processMatch[1] : "unknown";
          publicListeners.push({ port, processName, line: line.trim() });
        }
      }
    }
  }

  for (const { port, processName } of publicListeners) {
    // Skip known-good services by process name
    // Note: "node" is intentionally NOT whitelisted — any unexpected Node process should be reviewed
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

function auditSysctl() {
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

  const wrong = [];
  for (const { key, expected } of params) {
    const val = run("sysctl", ["-n", key]);
    if (val !== null && val.trim() !== expected) {
      wrong.push(`${key}=${val.trim()} (want ${expected})`);
    }
  }

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

// --- AppArmor ---

function auditAppArmor() {
  addCheck();
  // Check if AppArmor module is loaded
  const enabled = readFile("/sys/module/apparmor/parameters/enabled");
  if (!enabled || enabled.trim() !== "Y") {
    addFinding(
      "warning",
      "SYS-061",
      "AppArmor is not active",
      "AppArmor kernel module is not loaded. AppArmor provides mandatory access control to limit damage from exploits.",
      "sudo apt install apparmor apparmor-utils && sudo systemctl enable --now apparmor"
    );
    return;
  }

  // Check profiles loaded via filesystem (readable without sudo)
  const profilesFile = readFile("/sys/kernel/security/apparmor/profiles");
  const profileCount = profilesFile
    ? profilesFile.split("\n").filter((l) => l.trim()).length
    : -1;

  if (profileCount === 0) {
    addFinding(
      "info",
      "SYS-061",
      "AppArmor active but no profiles loaded",
      "AppArmor module is running but no profiles are loaded. Consider adding profiles for critical services.",
      "sudo apt install apparmor-profiles apparmor-profiles-extra && sudo aa-enforce /etc/apparmor.d/*"
    );
  }
  // profileCount > 0: AppArmor running with profiles — all good, no finding
}

// --- SSH authorized_keys ---

function auditAuthorizedKeys() {
  addCheck();
  const paths = [
    `${process.env.HOME || "/root"}/.ssh/authorized_keys`,
    "/root/.ssh/authorized_keys",
  ];

  for (const keyPath of [...new Set(paths)]) {
    const content = readFile(keyPath);
    if (!content) continue;

    // Count non-empty, non-comment lines
    const keys = content.split("\n").filter((l) => l.trim() && !l.trim().startsWith("#"));
    const count = keys.length;

    if (count === 0) continue;

    const severity = count >= 4 ? "warning" : "info";
    addFinding(
      severity,
      "SYS-062",
      `${count} SSH authorized key${count > 1 ? "s" : ""} found in ${keyPath}`,
      `${count} public key${count > 1 ? "s are" : " is"} authorized for SSH login. Verify all are known and current.`,
      `Review: cat ${keyPath} — remove any unknown or outdated keys`
    );
  }
}

// --- NTP / Zeitsync ---

function auditNTP() {
  addCheck();
  const out = run("timedatectl", ["show", "--no-pager"]);
  if (!out) {
    addFinding(
      "info",
      "SYS-063",
      "Time sync status unknown",
      "timedatectl not available. Cannot verify NTP sync — required for valid TLS certificate checks.",
      "sudo apt install systemd (or check ntpd/chrony directly)"
    );
    return;
  }

  const get = (key) => {
    const m = out.match(new RegExp(`^${key}=(.+)`, "m"));
    return m ? m[1].trim() : null;
  };

  const ntp = get("NTP");
  const synced = get("NTPSynchronized");

  if (synced !== "yes") {
    addFinding(
      "warning",
      "SYS-063",
      "System clock is not NTP-synchronized",
      `NTPSynchronized=${synced ?? "unknown"}, NTP=${ntp ?? "unknown"}. An unsynchronized clock can cause TLS errors and audit log gaps.`,
      "sudo timedatectl set-ntp true"
    );
  }
}

// --- Swap Encryption ---

function auditSwap() {
  addCheck();
  const out = run("swapon", ["--show=NAME,TYPE", "--noheadings"]);
  if (!out || !out.trim()) return; // No swap — fine

  const lines = out.trim().split("\n").filter(Boolean);
  const unencrypted = lines.filter((l) => {
    // Encrypted swap usually appears as /dev/mapper/... or dm-
    const name = l.trim().split(/\s+/)[0];
    return name && !name.includes("/mapper/") && !name.includes("dm-") && !name.includes("zram");
  });

  if (unencrypted.length > 0) {
    addFinding(
      "info",
      "SYS-064",
      "Swap partition is not encrypted",
      `Unencrypted swap: ${unencrypted.join(", ")}. Sensitive data in memory may persist on disk.`,
      "Consider enabling encrypted swap: https://wiki.debian.org/EncryptedSwap"
    );
  }
}

// --- World-Writable /tmp Sticky Bit ---

function auditWorldWritable() {
  addCheck();
  const dirs = ["/tmp", "/var/tmp"];
  const issues = [];

  for (const dir of dirs) {
    if (!existsSync(dir)) continue;
    const modeStr = run("stat", ["-c", "%a", dir]);
    if (!modeStr) continue;
    const mode = modeStr.trim();
    // Sticky bit = mode starts with "1" (e.g. 1777)
    if (!mode.startsWith("1")) {
      issues.push(`${dir} (mode: ${mode})`);
    }
  }

  if (issues.length > 0) {
    addFinding(
      "warning",
      "SYS-065",
      "World-writable directory missing sticky bit",
      `Missing sticky bit on: ${issues.join(", ")}. Without it, users can delete each other's files.`,
      `sudo chmod +t /tmp /var/tmp`
    );
  }
}

// --- SUID/SGID Binaries ---

function auditSUID() {
  addCheck();
  const whitelist = new Set([
    "sudo", "su", "passwd", "chsh", "chfn", "gpasswd", "newgrp",
    "mount", "umount", "ping", "ping6", "traceroute6",
    "ssh-agent", "crontab", "at", "wall", "write",
    "pkexec", "dbus-daemon-launch-helper", "unix_chkpwd",
    "pam_timestamp_check", "pam_extrausers_chkpwd", // Ubuntu PAM extra-users helper
    "locate", "fusermount", "fusermount3",
    "newuidmap", "newgidmap", "pt_chown", "expiry", "chage",
  ]);

  const result = run(
    "find", ["/usr/bin", "/usr/sbin", "/bin", "/sbin", "-perm", "/6000", "-type", "f"],
    { timeout: 15000 }
  );
  if (!result) return;

  const unknown = [];
  for (const line of result.split("\n")) {
    const file = line.trim();
    if (!file) continue;
    const name = file.split("/").pop();
    if (!whitelist.has(name)) {
      unknown.push(file);
    }
  }

  if (unknown.length > 0) {
    addFinding(
      "warning",
      "SYS-066",
      `${unknown.length} unexpected SUID/SGID ${unknown.length === 1 ? "binary" : "binaries"} found`,
      `Files with elevated privileges not in whitelist: ${unknown.join(", ")}`,
      `Review each file. Remove SUID bit if not needed: sudo chmod -s <file>`
    );
  }
}

// --- Docker Security ---

function auditDockerSecurity() {
  addCheck();

  // Check if Docker is installed
  const dockerInstalled = run("which", ["docker"]);
  if (!dockerInstalled) return; // Docker not installed - skip checks

  // SYS-070: Docker daemon exposed on TCP
  const dockerInfo = runDocker(["info"]);
  if (!dockerInfo) {
    trackSkip("Docker Security (SYS-070-072)",
              "Cannot run 'docker info' (permission denied)",
              "Add to /etc/sudoers.d/claw-audit:\n    <user> ALL=(ALL) NOPASSWD: /usr/bin/docker info, /usr/bin/docker ps *, /usr/bin/docker inspect *\n  OR add user to docker group: sudo usermod -aG docker <user>");
    return;
  }

  if (dockerInfo) {
    // Check if daemon is listening on TCP
    const netstat = runShell("ss -tlnp | grep dockerd || netstat -tlnp 2>/dev/null | grep dockerd");
    if (netstat && /0\.0\.0\.0:2375/.test(netstat)) {
      addFinding(
        "critical",
        "SYS-070",
        "Docker daemon exposed on TCP without TLS",
        "Docker daemon is listening on 0.0.0.0:2375 without TLS authentication. This allows anyone on the network to control Docker.",
        "Edit /etc/docker/daemon.json: remove tcp://0.0.0.0:2375 or enable TLS with --tlsverify"
      );
    }
  }

  // SYS-071: Privileged containers
  const containers = runDocker(["ps", "--format", "{{.ID}}:{{.Names}}"]);
  if (containers) {
    const lines = containers.split("\n").filter(Boolean);
    const privileged = [];

    for (const line of lines) {
      const [id, name] = line.split(":");
      if (!id) continue;
      const inspect = runDocker(["inspect", id, "--format", "{{.HostConfig.Privileged}}"]);
      if (inspect && inspect.trim() === "true") {
        privileged.push(name || id);
      }
    }

    if (privileged.length > 0) {
      addFinding(
        "critical",
        "SYS-071",
        `${privileged.length} privileged container${privileged.length > 1 ? "s" : ""} running`,
        `Containers with --privileged flag can escape to host: ${privileged.join(", ")}. This bypasses all container isolation.`,
        "Remove --privileged flag. Use --cap-add for specific capabilities instead."
      );
    }
  }

  // SYS-072: Docker socket mounted into containers
  if (containers) {
    const lines = containers.split("\n").filter(Boolean);
    const socketMounted = [];

    for (const line of lines) {
      const [id, name] = line.split(":");
      if (!id) continue;
      const mounts = runDocker(["inspect", id, "--format", "{{range .Mounts}}{{.Source}}{{end}}"]);
      if (mounts && mounts.includes("/var/run/docker.sock")) {
        socketMounted.push(name || id);
      }
    }

    if (socketMounted.length > 0) {
      addFinding(
        "critical",
        "SYS-072",
        `${socketMounted.length} container${socketMounted.length > 1 ? "s" : ""} with Docker socket mounted`,
        `Docker socket mounted in: ${socketMounted.join(", ")}. This allows container escape and full host control.`,
        "Remove -v /var/run/docker.sock:/var/run/docker.sock from container launch"
      );
    }
  }
}

// --- Process Isolation ---

function auditProcessIsolation() {
  addCheck();

  // SYS-080: OpenClaw running as root
  const openclawProcs = runShell("ps aux | grep -E '(openclaw|clawdbot|moltbot)' | grep -v grep");
  if (openclawProcs) {
    const lines = openclawProcs.split("\n").filter(Boolean);
    const rootProcs = lines.filter(line => line.trim().startsWith("root"));

    if (rootProcs.length > 0) {
      addFinding(
        "critical",
        "SYS-080",
        "OpenClaw process running as root",
        `${rootProcs.length} OpenClaw process${rootProcs.length > 1 ? "es" : ""} running as UID 0. AI agents should never run with root privileges.`,
        "Create dedicated user: sudo useradd -r -s /bin/false openclaw && chown -R openclaw:openclaw ~/.openclaw"
      );
    }
  }

  // SYS-081: Containers sharing host PID namespace
  const containers = runDocker(["ps", "-q"]);
  if (containers) {
    const ids = containers.split("\n").filter(Boolean);
    const sharedPID = [];

    for (const id of ids) {
      const pidMode = runDocker(["inspect", id, "--format", "{{.HostConfig.PidMode}}"]);
      if (pidMode && pidMode.trim() === "host") {
        const name = runDocker(["inspect", id, "--format", "{{.Name}}"]);
        sharedPID.push((name || id).replace(/^\//, ""));
      }
    }

    if (sharedPID.length > 0) {
      addFinding(
        "warning",
        "SYS-081",
        `${sharedPID.length} container${sharedPID.length > 1 ? "s" : ""} sharing host PID namespace`,
        `Containers with --pid=host can see all host processes: ${sharedPID.join(", ")}`,
        "Remove --pid=host flag from container configuration"
      );
    }
  }

  // SYS-082: No resource limits (check for OpenClaw processes)
  if (openclawProcs) {
    const lines = openclawProcs.split("\n").filter(Boolean);
    if (lines.length > 0) {
      // Get first OpenClaw PID
      const firstLine = lines[0].trim().split(/\s+/);
      const pid = firstLine[1];

      if (pid) {
        const limitsRaw = readFile(`/proc/${pid}/limits`);
        const limits = limitsRaw ? limitsRaw.split("\n").filter(l => /(Max processes|Max open files|Max locked memory)/.test(l)).join("\n") || null : null;
        if (limits && /unlimited/.test(limits)) {
          const unlimitedCount = (limits.match(/unlimited/g) || []).length;
          addFinding(
            "warning",
            "SYS-082",
            "OpenClaw process has unlimited resource limits",
            `Process ${pid} has ${unlimitedCount} unlimited resource limit${unlimitedCount > 1 ? "s" : ""}. This could lead to resource exhaustion attacks.`,
            "Set limits in /etc/security/limits.conf:\nopenclaw hard nproc 1000\nopenclaw hard nofile 65536"
          );
        }
      }
    }
  }
}

// --- Network Segmentation ---

function auditNetworkSegmentation() {
  addCheck();

  // SYS-100: Check if running in cloud/VM with metadata service exposed
  const metadataReachable = run("timeout", ["2", "curl", "-s", "http://169.254.169.254/latest/meta-data/"]);
  if (metadataReachable) {
    // Check if iptables blocks it
    const blocked = runShell("iptables -L OUTPUT -n | grep 169.254.169.254 || sudo -n iptables -L OUTPUT -n | grep 169.254.169.254");
    if (!blocked) {
      addFinding(
        "warning",
        "SYS-100",
        "Cloud metadata service accessible without firewall rules",
        "Instance metadata API (169.254.169.254) is reachable. Compromised OpenClaw agent could steal IAM credentials.",
        "Block metadata API: sudo iptables -A OUTPUT -d 169.254.169.254 -j REJECT"
      );
    }
  }

  // SYS-101: Egress filtering check
  const ufwStatus = run("ufw", ["status", "verbose"], { sudo: true }) || "";
  const hasEgressRules = /DENY OUT/.test(ufwStatus) || /REJECT OUT/.test(ufwStatus);

  if (!hasEgressRules) {
    addFinding(
      "info",
      "SYS-101",
      "No egress filtering configured",
      "OpenClaw can reach any internet destination. Egress filtering limits data exfiltration risk.",
      "Consider default-deny egress with whitelist: sudo ufw default deny outgoing && sudo ufw allow out to claude.ai"
    );
  }

  // SYS-102: DNS configuration check
  const resolvConf = readFile("/etc/resolv.conf");
  if (resolvConf) {
    const publicDNS = ["8.8.8.8", "8.8.4.4", "1.1.1.1", "1.0.0.1"];
    const usesPublicDNS = publicDNS.some(dns => resolvConf.includes(dns));

    if (usesPublicDNS) {
      const dnsServers = resolvConf.match(/nameserver\s+([\d.]+)/g) || [];
      addFinding(
        "info",
        "SYS-102",
        "Using public DNS servers",
        `DNS queries visible to third parties: ${dnsServers.join(", ")}. Consider privacy implications.`,
        "Use encrypted DNS (DoT/DoH) or internal DNS server"
      );
    }
  }
}

// --- CRITICAL: System Access & Authentication ---

function auditEmptyPasswords() {
  addCheck();
  // SYS-163: Check for accounts with empty passwords
  const shadow = readFile("/etc/shadow");
  if (!shadow) {
    trackSkip("Empty Passwords (SYS-163)",
              "Cannot read /etc/shadow",
              "Add user to shadow group: sudo usermod -aG shadow <user>\n  OR: sudo chmod 640 /etc/shadow && sudo chgrp shadow /etc/shadow");
    return;
  }

  const emptyPasswords = [];
  for (const line of shadow.split("\n")) {
    if (!line || line.startsWith("#")) continue;
    const parts = line.split(":");
    const username = parts[0];
    const password = parts[1];

    // Empty password field or single ! or * means no password
    if (!password || password === "" || password === "!!" || password === "*") {
      // Skip system accounts (UID < 1000) that should be locked
      const uid = run("id", ["-u", username]);
      if (uid && parseInt(uid) >= 1000) {
        emptyPasswords.push(username);
      }
    }
  }

  if (emptyPasswords.length > 0) {
    addFinding(
      "critical",
      "SYS-163",
      `${emptyPasswords.length} account${emptyPasswords.length > 1 ? "s" : ""} with empty password`,
      `Accounts without password: ${emptyPasswords.join(", ")}. These can be accessed without authentication.`,
      `Lock accounts: sudo passwd -l ${emptyPasswords[0]} (repeat for each)`
    );
  }
}

function auditRootPATH() {
  addCheck();
  // SYS-164: Root PATH integrity
  const rootPath = process.env.PATH;
  if (!rootPath) return;

  const issues = [];
  const pathDirs = rootPath.split(":");

  // Check for current directory (.)
  if (pathDirs.includes(".") || pathDirs.includes("")) {
    issues.push("Contains current directory (.)");
  }

  // Check for writable directories
  for (const dir of pathDirs) {
    if (!dir || dir === ".") continue;
    // Use -L to follow symlinks (/bin → /usr/bin is always 777 as symlink)
    const mode = run("stat", ["-Lc", "%a", dir]);
    if (mode) {
      const perms = parseInt(mode.trim(), 8);
      // Check if world-writable (group-writable is acceptable for user-owned dirs)
      if (perms & 0o002) {
        issues.push(`${dir} is group/world-writable (${mode.trim()})`);
      }
    }
  }

  if (issues.length > 0) {
    addFinding(
      "critical",
      "SYS-164",
      "Root PATH contains unsafe directories",
      `PATH integrity issues: ${issues.join("; ")}. Attacker could place malicious binaries.`,
      "Fix PATH in /root/.bashrc and /root/.profile - remove '.' and fix permissions"
    );
  }
}

function auditSyslog() {
  addCheck();
  // SYS-190: rsyslog/syslog-ng running
  const rsyslog = run("systemctl", ["is-active", "rsyslog"]);
  const syslogng = run("systemctl", ["is-active", "syslog-ng"]);

  if (rsyslog !== "active" && syslogng !== "active") {
    addFinding(
      "critical",
      "SYS-190",
      "System logging daemon not running",
      "Neither rsyslog nor syslog-ng is active. System events are not being logged.",
      "Start logging: sudo systemctl enable --now rsyslog"
    );
  }
}

function auditAuditd() {
  addCheck();
  // SYS-191: auditd running and configured
  const auditdActive = run("systemctl", ["is-active", "auditd"]);

  if (auditdActive !== "active") {
    addFinding(
      "critical",
      "SYS-191",
      "auditd not running",
      "Audit daemon is not active. Security events (file access, privilege escalation) are not tracked.",
      "Install and enable: sudo apt install auditd && sudo systemctl enable --now auditd"
    );
  } else {
    // Check if audit rules are configured
    const rules = run("auditctl", ["-l"]);
    if (!rules) {
      trackSkip("Auditd Rules (SYS-191)",
                "Cannot run 'auditctl -l' (requires root)",
                "Add to /etc/sudoers.d/claw-audit:\n    <user> ALL=(ALL) NOPASSWD: /sbin/auditctl -l");
    } else if (rules.includes("No rules")) {
      addFinding(
        "warning",
        "SYS-191",
        "auditd running but no rules configured",
        "Audit daemon is active but has no monitoring rules. Critical paths (/etc, /var/log) are not monitored.",
        "Add rules: sudo auditctl -w /etc -p wa -k config_changes"
      );
    }
  }
}

function auditShadowPermissions() {
  addCheck();
  // SYS-204: /etc/shadow permissions
  const mode = run("stat", ["-c", "%a", "/etc/shadow"]);
  if (!mode) {
    trackSkip("Shadow File Permissions (SYS-204)",
              "Cannot stat /etc/shadow",
              "Add to /etc/sudoers.d/claw-audit:\n    <user> ALL=(ALL) NOPASSWD: /usr/bin/stat -c \\%a /etc/shadow, /usr/bin/stat -c \\%U\\:\\%G /etc/shadow");
    return;
  }

  // Normalize: stat may return "0" instead of "000"
  const perms = mode.trim().padStart(3, "0");
  if (perms !== "000" && perms !== "400") {
    addFinding(
      "critical",
      "SYS-204",
      "/etc/shadow has weak permissions",
      `/etc/shadow has mode ${perms}. Should be 000 or 400 to protect password hashes.`,
      "Fix permissions: sudo chmod 000 /etc/shadow"
    );
  }

  // Also check owner
  const owner = run("stat", ["-c", "%U:%G", "/etc/shadow"]);
  if (owner && owner.trim() !== "root:root" && owner.trim() !== "root:shadow") {
    addFinding(
      "warning",
      "SYS-204",
      "/etc/shadow has incorrect owner",
      `/etc/shadow owned by ${owner.trim()}. Should be root:root or root:shadow.`,
      "Fix ownership: sudo chown root:root /etc/shadow"
    );
  }
}

// --- HIGH: Filesystem & Partitions ---

function auditPartitions() {
  addCheck();
  // SYS-150: Separate partitions for critical directories
  const mount = run("mount", []);
  if (!mount) return;

  const criticalDirs = {
    "/tmp": { required: true, options: ["noexec", "nosuid", "nodev"] },
    "/var": { required: false, options: [] },
    "/var/log": { required: false, options: [] },
    "/var/tmp": { required: true, options: ["noexec", "nosuid", "nodev"] },
    "/home": { required: false, options: ["nodev"] },
  };

  const issues = [];

  for (const [dir, config] of Object.entries(criticalDirs)) {
    const mountLine = mount.split("\n").find(line => {
      const parts = line.split(" on ");
      return parts[1] && parts[1].startsWith(dir + " ");
    });

    if (!mountLine) {
      if (config.required) {
        issues.push(`${dir} not on separate partition`);
      }
    } else {
      // Check mount options
      const optMatch = mountLine.match(/\(([^)]+)\)/);
      if (optMatch && config.options.length > 0) {
        const opts = optMatch[1].split(",");
        const missing = config.options.filter(o => !opts.includes(o));
        if (missing.length > 0) {
          issues.push(`${dir} missing options: ${missing.join(",")}`);
        }
      }
    }
  }

  if (issues.length > 0) {
    addFinding(
      "warning",
      "SYS-150",
      "Filesystem partitioning issues",
      `${issues.join("; ")}. Separate partitions improve security and prevent DoS via disk fill.`,
      "Consider repartitioning or add bind-mount with noexec/nosuid/nodev in /etc/fstab"
    );
  }
}

function auditPasswordPolicy() {
  addCheck();
  // SYS-160: Password policy
  const loginDefs = readFile("/etc/login.defs");
  if (!loginDefs) return;

  const issues = [];

  // Check PASS_MAX_DAYS
  const maxDays = loginDefs.match(/^PASS_MAX_DAYS\s+(\d+)/m);
  if (!maxDays || parseInt(maxDays[1]) > 90) {
    issues.push("PASS_MAX_DAYS > 90 or not set");
  }

  // Check PASS_MIN_DAYS
  const minDays = loginDefs.match(/^PASS_MIN_DAYS\s+(\d+)/m);
  if (!minDays || parseInt(minDays[1]) < 1) {
    issues.push("PASS_MIN_DAYS < 1");
  }

  // Check PASS_MIN_LEN
  const minLen = loginDefs.match(/^PASS_MIN_LEN\s+(\d+)/m);
  if (!minLen || parseInt(minLen[1]) < 14) {
    issues.push("PASS_MIN_LEN < 14");
  }

  if (issues.length > 0) {
    addFinding(
      "warning",
      "SYS-160",
      "Weak password policy",
      `${issues.join("; ")}. Weak policies allow easily guessable passwords and unlimited credential lifetime.`,
      "Edit /etc/login.defs: PASS_MAX_DAYS 90, PASS_MIN_DAYS 1, PASS_MIN_LEN 14"
    );
  }
}

function auditAccountLockout() {
  addCheck();
  // SYS-161: Account lockout configuration
  const commonAuth = readFile("/etc/pam.d/common-auth");
  if (!commonAuth) return;

  const hasFaillock = /pam_faillock/.test(commonAuth);
  const hasTally = /pam_tally2/.test(commonAuth);

  if (!hasFaillock && !hasTally) {
    addFinding(
      "warning",
      "SYS-161",
      "No account lockout policy configured",
      "Neither pam_faillock nor pam_tally2 configured. Accounts will not lock after repeated failed login attempts.",
      "Configure faillock in /etc/pam.d/common-auth: auth required pam_faillock.so deny=5 unlock_time=900"
    );
  }
}

function auditUnnecessaryServices() {
  addCheck();
  // SYS-180: Unnecessary services disabled
  const unnecessaryServices = [
    "avahi-daemon",
    "cups",
    "rpcbind",
    "rsync",
    "snmpd",
    "telnet",
    "tftp",
  ];

  const running = [];
  for (const svc of unnecessaryServices) {
    const status = run("systemctl", ["is-active", svc]);
    if (status === "active") {
      running.push(svc);
    }
  }

  if (running.length > 0) {
    addFinding(
      "warning",
      "SYS-180",
      `${running.length} unnecessary service${running.length > 1 ? "s" : ""} running`,
      `Services that are rarely needed on servers: ${running.join(", ")}. Reduce attack surface by disabling.`,
      `Disable: sudo systemctl disable --now ${running[0]} (repeat for each)`
    );
  }
}

function auditCronAccess() {
  addCheck();
  // SYS-181: Cron/at access restricted
  const cronAllow = existsSync("/etc/cron.allow");
  const atAllow = existsSync("/etc/at.allow");

  if (!cronAllow) {
    addFinding(
      "warning",
      "SYS-181",
      "/etc/cron.allow not configured",
      "No cron.allow file. All users can create cron jobs, increasing risk of persistence mechanisms.",
      "Create /etc/cron.allow with authorized users: echo 'root' | sudo tee /etc/cron.allow"
    );
  }

  if (!atAllow) {
    addFinding(
      "info",
      "SYS-181",
      "/etc/at.allow not configured",
      "No at.allow file. All users can schedule at jobs.",
      "Create /etc/at.allow with authorized users: echo 'root' | sudo tee /etc/at.allow"
    );
  }
}

// --- MEDIUM: System Hardening ---

function auditCoreDumps() {
  addCheck();
  // SYS-151: Core dumps disabled
  const limitsConf = readFile("/etc/security/limits.conf");
  // Use full path — /usr/sbin/sysctl may not be in PATH for non-root users
  // Fallback: read from sysctl.d config files directly
  const sysctl = run("/usr/sbin/sysctl", ["fs.suid_dumpable"])
    || run("sysctl", ["fs.suid_dumpable"]);
  const sysctlConf = [
    "/etc/sysctl.conf",
    "/etc/sysctl.d/99-hardening.conf",
    "/etc/sysctl.d/10-kernel-hardening.conf",
  ].map(readFile).filter(Boolean).join("\n");
  const sysctlOk = (sysctl && sysctl.includes("fs.suid_dumpable = 0"))
    || sysctlConf.includes("fs.suid_dumpable=0")
    || sysctlConf.includes("fs.suid_dumpable = 0");

  const issues = [];

  if (!limitsConf || !limitsConf.includes("* hard core 0")) {
    issues.push("limits.conf: hard core limit not 0");
  }

  if (!sysctlOk) {
    issues.push("sysctl: fs.suid_dumpable not 0");
  }

  if (issues.length > 0) {
    addFinding(
      "warning",
      "SYS-151",
      "Core dumps not disabled",
      `${issues.join("; ")}. Core dumps may contain sensitive data (passwords, keys).`,
      "Add to /etc/security/limits.conf: * hard core 0; sysctl -w fs.suid_dumpable=0"
    );
  }
}

function auditIPv6() {
  addCheck();
  // SYS-170: IPv6 disabled if not used
  const ipv6 = run("/usr/sbin/sysctl", ["net.ipv6.conf.all.disable_ipv6"])
    || run("sysctl", ["net.ipv6.conf.all.disable_ipv6"]);

  if (ipv6 && ipv6.includes("= 0")) {
    // IPv6 is enabled - check if it's actually used
    const ipv6Addr = runShell("ip -6 addr show scope global 2>/dev/null | grep -c inet6");
    const hasIPv6 = ipv6Addr && parseInt(ipv6Addr) > 0;

    if (!hasIPv6) {
      addFinding(
        "info",
        "SYS-170",
        "IPv6 enabled but not used",
        "IPv6 is enabled in kernel but no IPv6 addresses configured. Unused protocols increase attack surface.",
        "Disable IPv6: echo 'net.ipv6.conf.all.disable_ipv6=1' | sudo tee -a /etc/sysctl.d/99-ipv6.conf && sudo sysctl -p"
      );
    }
  }
}

function auditSSHBanner() {
  addCheck();
  // SYS-182: SSH banner configured
  const sshConfig = readFile("/etc/ssh/sshd_config");
  if (!sshConfig) {
    trackSkip("SSH Banner (SYS-182)",
              "Cannot read /etc/ssh/sshd_config",
              "Add user to shadow group OR: sudo chmod 644 /etc/ssh/sshd_config");
    return;
  }

  const bannerMatch = sshConfig.match(/^\s*Banner\s+(.+)/m);
  if (!bannerMatch) {
    addFinding(
      "info",
      "SYS-182",
      "SSH login banner not configured",
      "No Banner directive in sshd_config. Legal warning banners deter unauthorized access and establish expectations.",
      "Add to /etc/ssh/sshd_config: Banner /etc/issue.net && sudo systemctl reload sshd"
    );
  }
}

function auditSSHTimeout() {
  addCheck();
  // SYS-183: SSH idle timeout
  const sshConfig = readFile("/etc/ssh/sshd_config");
  if (!sshConfig) {
    trackSkip("SSH Idle Timeout (SYS-183)",
              "Cannot read /etc/ssh/sshd_config",
              "Add user to shadow group OR: sudo chmod 644 /etc/ssh/sshd_config");
    return;
  }

  const clientAlive = sshConfig.match(/^\s*ClientAliveInterval\s+(\d+)/m);
  const clientMax = sshConfig.match(/^\s*ClientAliveCountMax\s+(\d+)/m);

  if (!clientAlive || parseInt(clientAlive[1]) === 0 || parseInt(clientAlive[1]) > 300) {
    addFinding(
      "warning",
      "SYS-183",
      "SSH idle timeout not configured",
      "ClientAliveInterval not set or too high. Idle sessions remain open indefinitely, increasing hijack risk.",
      "Add to /etc/ssh/sshd_config: ClientAliveInterval 300, ClientAliveCountMax 2"
    );
  }
}

function auditLogPermissions() {
  addCheck();
  // SYS-192: Log file permissions
  const logFiles = runShell("find /var/log -type f 2>/dev/null | head -20");
  if (!logFiles) {
    trackSkip("Log File Permissions (SYS-192)",
              "Cannot access /var/log directory",
              "Add user to adm group: sudo usermod -aG adm <user>\n  This grants read access to most log files");
    return;
  }

  const weakPerms = [];
  for (const logFile of logFiles.split("\n")) {
    if (!logFile) continue;
    const mode = run("stat", ["-c", "%a", logFile]);
    if (mode) {
      const perms = parseInt(mode.trim(), 8);
      // Check if world-readable or world-writable
      if (perms & 0o004 || perms & 0o002) {
        weakPerms.push(`${logFile} (${mode.trim()})`);
      }
    }
  }

  if (weakPerms.length > 0) {
    addFinding(
      "warning",
      "SYS-192",
      `${weakPerms.length} log file${weakPerms.length > 1 ? "s" : ""} with weak permissions`,
      `Log files readable/writable by non-root: ${weakPerms.slice(0, 3).join(", ")}${weakPerms.length > 3 ? ` (+${weakPerms.length - 3} more)` : ""}`,
      "Fix permissions: sudo chmod -R 640 /var/log/*.log"
    );
  }
}

// --- Run All Checks ---

function runAudit() {
  if (!JSON_OUTPUT) {
    console.log("\n🛡️  ClawAudit System Auditor\n");
    console.log("Checking SSH, firewall, fail2ban, Docker, process isolation, network segmentation...\n");
  }

  auditSSH();
  auditUFW();
  auditFail2ban();
  auditWireGuard();
  auditAutoUpdates();
  auditOpenPorts();
  auditSysctl();
  auditAppArmor();
  auditAuthorizedKeys();
  auditNTP();
  auditSwap();
  auditWorldWritable();
  auditSUID();
  auditDockerSecurity();
  auditProcessIsolation();
  auditNetworkSegmentation();

  // CRITICAL checks
  auditEmptyPasswords();
  auditRootPATH();
  auditSyslog();
  auditAuditd();
  auditShadowPermissions();

  // HIGH priority checks
  auditPartitions();
  auditPasswordPolicy();
  auditAccountLockout();
  auditUnnecessaryServices();
  auditCronAccess();

  // MEDIUM priority checks
  auditCoreDumps();
  auditIPv6();
  auditSSHBanner();
  auditSSHTimeout();
  auditLogPermissions();

  // --- Apply user-defined mitigations from config ---
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
      findings,
      skippedChecks,
    };
    console.log(JSON.stringify(summary, null, 2));
    return;
  }

  if (findings.length === 0) {
    console.log("✅ System looks well-hardened! No issues found.\n");
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

  // --- Show Skipped Checks ---
  if (skippedChecks.length > 0) {
    console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
    console.log(`⚠️  ${skippedChecks.length} Check${skippedChecks.length > 1 ? "s" : ""} Skipped (Missing Privileges)\n`);

    // Group by requirement type
    const sudoersNeeded = [];
    const filePermNeeded = [];
    const groupNeeded = [];
    const packageNeeded = [];

    for (const skip of skippedChecks) {
      if (skip.requirement.includes("sudoers")) {
        sudoersNeeded.push(skip);
      } else if (skip.requirement.includes("chmod") || skip.requirement.includes("chgrp")) {
        filePermNeeded.push(skip);
      } else if (skip.requirement.includes("usermod -aG")) {
        groupNeeded.push(skip);
      } else if (skip.requirement.includes("apt install") || skip.requirement.includes("Install:")) {
        packageNeeded.push(skip);
      } else {
        // Generic/other
        console.log(`⊘ ${skip.check}`);
        console.log(`  Reason: ${skip.reason}`);
        console.log(`  Fix: ${skip.requirement}\n`);
      }
    }

    if (groupNeeded.length > 0) {
      console.log("📋 Group Membership Required:");
      for (const skip of groupNeeded) {
        console.log(`  • ${skip.check}: ${skip.reason}`);
      }
      console.log("\n  Commands:");
      const groups = new Set();
      for (const skip of groupNeeded) {
        const match = skip.requirement.match(/usermod -aG (\w+)/);
        if (match) groups.add(match[1]);
      }
      for (const group of groups) {
        console.log(`    sudo usermod -aG ${group} $USER`);
      }
      console.log("    # Then logout and login again for group changes to take effect\n");
    }

    if (filePermNeeded.length > 0) {
      console.log("📂 File Permission Changes Required:");
      for (const skip of filePermNeeded) {
        console.log(`  • ${skip.check}: ${skip.reason}`);
        const lines = skip.requirement.split('\n');
        for (const line of lines) {
          if (line.trim()) console.log(`    ${line.trim()}`);
        }
      }
      console.log();
    }

    if (sudoersNeeded.length > 0) {
      console.log("🔐 Sudoers Configuration Required:");
      console.log("  Create file: /etc/sudoers.d/claw-audit\n");

      const sudoersEntries = new Set();
      for (const skip of sudoersNeeded) {
        console.log(`  # ${skip.check}`);
        // Extract sudoers line from requirement
        const lines = skip.requirement.split('\n');
        for (const line of lines) {
          if (line.includes('ALL=(ALL) NOPASSWD:')) {
            const entry = line.trim().replace(/<user>/g, '$USER');
            sudoersEntries.add(entry);
          }
        }
      }
      console.log();
      for (const entry of sudoersEntries) {
        console.log(`  ${entry}`);
      }
      console.log("\n  Replace $USER with your actual username\n");
    }

    if (packageNeeded.length > 0) {
      console.log("📦 Missing Packages:");
      for (const skip of packageNeeded) {
        console.log(`  • ${skip.check}: ${skip.reason}`);
        console.log(`    ${skip.requirement}`);
      }
      console.log();
    }

    console.log();
  }

  console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
  console.log(`📊 System Audit: ${crit} critical, ${warn} warnings, ${info} info`);
  if (skippedChecks.length > 0) {
    console.log(`⊘ ${skippedChecks.length} check${skippedChecks.length > 1 ? "s" : ""} skipped due to missing privileges`);
  }
  if (!SHOW_FIX && findings.length > 0) {
    console.log("   Run with --fix to see remediation steps.");
  }
  console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n");
}

runAudit();
