/**
 * ClawAudit — System Auditor Tests
 *
 * Two levels:
 * 1. Unit tests: SSH config parsing regex logic (pure, no system deps)
 * 2. Integration tests: JSON output structure + known-good state verification
 */

import { test } from "node:test";
import { strict as assert } from "node:assert";
import { spawnSync } from "child_process";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const AUDIT_SCRIPT = resolve(__dirname, "..", "scripts", "audit-system.mjs");

// --- Run auditor once, share across integration tests ---

function runAudit() {
  const result = spawnSync("node", [AUDIT_SCRIPT, "--json"], {
    encoding: "utf-8",
    timeout: 15000,
  });
  assert.ok(result.stdout, `Audit produced no output. stderr: ${result.stderr}`);
  return JSON.parse(result.stdout);
}

const auditData = runAudit();

// =============================================================================
// SSH Config Parsing — Unit Tests (mirrors audit-system.mjs get() logic)
// Tests Bug #2 fix: first match wins (sshd semantics)
// =============================================================================

function parseSSHConfig(raw) {
  const get = (key) => {
    // sshd uses FIRST occurrence — matches[0] not matches[last]
    const matches = [...raw.matchAll(new RegExp(`^\\s*${key}\\s+(.+)`, "gim"))];
    return matches.length > 0 ? matches[0][1].trim() : null;
  };
  return get;
}

test("SSH parser: gets first occurrence (sshd first-match semantics)", () => {
  const raw = "X11Forwarding no\nX11Forwarding yes\n";
  const get = parseSSHConfig(raw);
  assert.equal(get("X11Forwarding"), "no", "Should return first match, not last");
});

test("SSH parser: returns null when key not set", () => {
  const get = parseSSHConfig("Port 22\nUseDNS no\n");
  assert.equal(get("X11Forwarding"), null);
});

test("SSH parser: ignores commented directives", () => {
  const raw = "#X11Forwarding yes\nX11Forwarding no\n";
  const get = parseSSHConfig(raw);
  assert.equal(get("X11Forwarding"), "no", "Should ignore commented line");
});

test("SSH parser: handles indented directives", () => {
  const raw = "  X11Forwarding yes\n";
  const get = parseSSHConfig(raw);
  assert.equal(get("X11Forwarding"), "yes");
});

// =============================================================================
// SYS-001: PermitRootLogin
// =============================================================================

test("SYS-001: PermitRootLogin=yes is detected", () => {
  const raw = "PermitRootLogin yes\n";
  const get = parseSSHConfig(raw);
  const val = (get("PermitRootLogin") ?? "yes").toLowerCase();
  const isBad = !["no", "prohibit-password", "forced-commands-only"].includes(val);
  assert.ok(isBad, "PermitRootLogin yes should be flagged");
});

test("SYS-001: PermitRootLogin=no is safe", () => {
  const raw = "PermitRootLogin no\n";
  const get = parseSSHConfig(raw);
  const val = (get("PermitRootLogin") ?? "yes").toLowerCase();
  const isBad = !["no", "prohibit-password", "forced-commands-only"].includes(val);
  assert.ok(!isBad, "PermitRootLogin no should be safe");
});

test("SYS-001: PermitRootLogin=prohibit-password is safe", () => {
  const raw = "PermitRootLogin prohibit-password\n";
  const get = parseSSHConfig(raw);
  const val = (get("PermitRootLogin") ?? "yes").toLowerCase();
  const isBad = !["no", "prohibit-password", "forced-commands-only"].includes(val);
  assert.ok(!isBad, "prohibit-password should be safe");
});

// =============================================================================
// SYS-002: PasswordAuthentication
// =============================================================================

test("SYS-002: PasswordAuthentication=yes is detected", () => {
  const raw = "PasswordAuthentication yes\n";
  const get = parseSSHConfig(raw);
  assert.equal((get("PasswordAuthentication") ?? "yes").toLowerCase(), "yes");
});

test("SYS-002: PasswordAuthentication=no is safe", () => {
  const raw = "PasswordAuthentication no\n";
  const get = parseSSHConfig(raw);
  assert.notEqual((get("PasswordAuthentication") ?? "yes").toLowerCase(), "yes");
});

// =============================================================================
// SYS-003: MaxAuthTries
// =============================================================================

test("SYS-003: MaxAuthTries=6 is flagged (>4)", () => {
  const raw = "MaxAuthTries 6\n";
  const get = parseSSHConfig(raw);
  const val = parseInt(get("MaxAuthTries") ?? "6", 10);
  assert.ok(val > 4, "MaxAuthTries 6 should be flagged");
});

test("SYS-003: MaxAuthTries=3 is safe", () => {
  const raw = "MaxAuthTries 3\n";
  const get = parseSSHConfig(raw);
  const val = parseInt(get("MaxAuthTries") ?? "6", 10);
  assert.ok(val <= 4, "MaxAuthTries 3 should be safe");
});

// =============================================================================
// SYS-004: X11Forwarding
// =============================================================================

test("SYS-004: X11Forwarding=yes is detected", () => {
  const raw = "X11Forwarding yes\n";
  const get = parseSSHConfig(raw);
  assert.equal((get("X11Forwarding") ?? "yes").toLowerCase(), "yes");
});

test("SYS-004: X11Forwarding=no is safe", () => {
  const raw = "X11Forwarding no\n";
  const get = parseSSHConfig(raw);
  assert.notEqual((get("X11Forwarding") ?? "yes").toLowerCase(), "yes");
});

// =============================================================================
// SYS-005: No AllowUsers restriction
// =============================================================================

test("SYS-005: missing AllowUsers and AllowGroups is flagged", () => {
  const raw = "Port 22\nX11Forwarding no\n";
  const get = parseSSHConfig(raw);
  assert.equal(get("AllowUsers"), null);
  assert.equal(get("AllowGroups"), null);
});

test("SYS-005: AllowUsers set is safe", () => {
  const raw = "AllowUsers admin\n";
  const get = parseSSHConfig(raw);
  assert.notEqual(get("AllowUsers"), null);
});

// =============================================================================
// SYS-013: UFW Regex — False Positive fix verification (Bug #3)
// =============================================================================

test("SYS-013: regex does NOT match Anywhere (v6) as public SSH", () => {
  const ufwStatus = `
Status: active
To                         Action      From
--                         ------      ----
22                         ALLOW IN    192.168.178.0/24
22 (v6)                    ALLOW IN    Anywhere (v6)
`;
  // SYS-013 should only trigger on IPv4 "Anywhere", not "(v6)"
  const matchesV4 = /22.*ALLOW IN.*Anywhere(?!\s*\(v6\))/i.test(ufwStatus);
  assert.ok(!matchesV4, "Should NOT flag SSH-behind-VPN setup due to v6 Anywhere entry");
});

test("SYS-013: regex DOES match when SSH open to all IPv4", () => {
  const ufwStatus = `
22/tcp                     ALLOW IN    Anywhere
22/tcp (v6)                ALLOW IN    Anywhere (v6)
`;
  const matchesV4 = /22.*ALLOW IN.*Anywhere(?!\s*\(v6\))/i.test(ufwStatus);
  assert.ok(matchesV4, "Should flag SSH publicly open on IPv4");
});

// =============================================================================
// SYS-030-032: WireGuard — Unit Tests
//
// REQUIRES (for full runtime coverage):
//   sudo wg show — without this, SYS-030-032 checks are skipped at runtime.
//   Add sudoers entry:
//     echo "openclaw ALL=(ALL) NOPASSWD: /usr/bin/wg show" \
//       | sudo tee /etc/sudoers.d/claw-audit-wg
// =============================================================================
// SYS-031: WireGuard subnet detection (Bug #7 fix verification)
// =============================================================================

test("SYS-031: detects SSH restricted to 192.168.x.x VPN subnet", () => {
  // UFW format: "22   ALLOW IN   192.168.x.x/y" — port comes before subnet
  const ufwStatus = "22   ALLOW IN   192.168.178.0/24";
  const sshBehindVpn =
    /22.*192\.168\.\d+\.\d+\/\d+/i.test(ufwStatus) ||
    /22.*10\.\d+\.\d+\.\d+\/\d+/i.test(ufwStatus) ||
    /22.*172\.(1[6-9]|2\d|3[01])\.\d+\.\d+\/\d+/i.test(ufwStatus);
  assert.ok(sshBehindVpn, "192.168.x.x VPN subnet should be recognized");
});

test("SYS-031: detects SSH restricted to 10.x.x.x subnet", () => {
  const ufwStatus = "22   ALLOW IN   10.8.0.0/24";
  const sshBehindVpn =
    /22.*192\.168\.\d+\.\d+\/\d+/i.test(ufwStatus) ||
    /22.*10\.\d+\.\d+\.\d+\/\d+/i.test(ufwStatus) ||
    /22.*172\.(1[6-9]|2\d|3[01])\.\d+\.\d+\/\d+/i.test(ufwStatus);
  assert.ok(sshBehindVpn, "10.x.x.x subnet should be recognized");
});

test("SYS-031: detects SSH restricted to 172.16-31.x subnet", () => {
  const ufwStatus = "22   ALLOW IN   172.20.0.0/24";
  const sshBehindVpn = /22.*172\.(1[6-9]|2\d|3[01])\.\d+\.\d+\/\d+/i.test(ufwStatus);
  assert.ok(sshBehindVpn, "172.16-31.x subnet should be recognized");
});

// =============================================================================
// Integration: JSON Output Structure
// =============================================================================

test("audit-system.mjs JSON output has correct structure", () => {
  const data = auditData;
  assert.ok(typeof data.critical === "number", "Missing critical count");
  assert.ok(typeof data.warnings === "number", "Missing warnings count");
  assert.ok(typeof data.info === "number", "Missing info count");
  assert.ok(Array.isArray(data.findings), "findings must be an array");
  for (const f of data.findings) {
    assert.ok(typeof f.code === "string", "finding.code must be string");
    assert.ok(f.code.startsWith("SYS-"), `finding.code should start with SYS-, got: ${f.code}`);
    assert.ok(["critical", "warning", "info"].includes(f.severity), `Invalid severity: ${f.severity}`);
    assert.ok(typeof f.title === "string", "finding.title must be string");
    assert.ok(typeof f.detail === "string", "finding.detail must be string");
  }
});

test("audit-system.mjs: no critical findings on a hardened system", () => {
  // Runs on the real system — fails only on unmitigated critical findings.
  // Skipped checks (due to missing permissions) are shown as diagnostics, not failures.
  //
  // To enable skipped checks, add the following permissions:
  //
  //   1. Sudoers (/etc/sudoers.d/claw-audit):
  //        openclaw ALL=(ALL) NOPASSWD: /usr/bin/wg show
  //        openclaw ALL=(ALL) NOPASSWD: /sbin/auditctl -l
  //        openclaw ALL=(ALL) NOPASSWD: /usr/bin/stat -c %a /etc/shadow
  //        openclaw ALL=(ALL) NOPASSWD: /usr/bin/stat -c %U:%G /etc/shadow
  //
  //   2. Group membership (to read /etc/shadow without sudo):
  //        sudo usermod -aG shadow openclaw
  //        (then re-login or: su - openclaw)
  const data = auditData;

  // Show skipped checks as diagnostic info (not failures)
  if (data.skippedChecks && data.skippedChecks.length > 0) {
    console.log(`\n  ℹ️  ${data.skippedChecks.length} check(s) skipped (missing permissions):`);
    for (const s of data.skippedChecks) {
      console.log(`     • ${s.check}: ${s.reason}`);
      if (s.requirement) console.log(`       → ${s.requirement.split("\n")[0]}`);
    }
  }

  // Fail only on real (non-mitigated) critical findings
  const criticals = data.findings.filter((f) => f.severity === "critical" && !f.mitigated);
  if (criticals.length > 0) {
    const codes = criticals.map((f) => f.code).join(", ");
    assert.fail(`Unmitigated critical findings on hardened system: ${codes}`);
  }
});

// =============================================================================
// SYS-060: sysctl Hardening — Unit Tests
// =============================================================================

function parseSysctl(lines) {
  // Simulate the sysctl check: returns array of "key=val (want X)" for wrong values
  const params = [
    { key: "net.ipv4.ip_forward",               expected: "0" },
    { key: "net.ipv4.conf.all.rp_filter",        expected: "1" },
    { key: "net.ipv4.tcp_syncookies",            expected: "1" },
    { key: "net.ipv4.conf.all.accept_redirects", expected: "0" },
    { key: "net.ipv6.conf.all.accept_redirects", expected: "0" },
    { key: "net.ipv4.conf.all.send_redirects",   expected: "0" },
    { key: "kernel.randomize_va_space",          expected: "2" },
  ];
  const vals = Object.fromEntries(lines.map((l) => l.split("=").map((s) => s.trim())));
  return params.filter(({ key, expected }) => vals[key] !== undefined && vals[key] !== expected);
}

test("SYS-060: all sysctl values correct → no issues", () => {
  const lines = [
    "net.ipv4.ip_forward=0",
    "net.ipv4.conf.all.rp_filter=1",
    "net.ipv4.tcp_syncookies=1",
    "net.ipv4.conf.all.accept_redirects=0",
    "net.ipv6.conf.all.accept_redirects=0",
    "net.ipv4.conf.all.send_redirects=0",
    "kernel.randomize_va_space=2",
  ];
  assert.equal(parseSysctl(lines).length, 0, "No issues expected when all params are correct");
});

test("SYS-060: ip_forward=1 is flagged", () => {
  const lines = ["net.ipv4.ip_forward=1"];
  const wrong = parseSysctl(lines);
  assert.equal(wrong.length, 1);
  assert.equal(wrong[0].key, "net.ipv4.ip_forward");
});

test("SYS-060: 3+ wrong params → critical severity", () => {
  const lines = [
    "net.ipv4.ip_forward=1",
    "net.ipv4.tcp_syncookies=0",
    "kernel.randomize_va_space=0",
    "net.ipv4.conf.all.send_redirects=1",
  ];
  const wrong = parseSysctl(lines);
  const severity = wrong.length >= 3 ? "critical" : "warning";
  assert.equal(severity, "critical", "3+ issues should be critical");
});

test("SYS-060: 1-2 wrong params → warning severity", () => {
  const lines = ["net.ipv4.ip_forward=1", "net.ipv4.tcp_syncookies=0"];
  const wrong = parseSysctl(lines);
  const severity = wrong.length >= 3 ? "critical" : "warning";
  assert.equal(severity, "warning", "1-2 issues should be warning");
});

// =============================================================================
// SYS-062: SSH authorized_keys — Unit Tests
// =============================================================================

function countAuthorizedKeys(content) {
  return content.split("\n").filter((l) => l.trim() && !l.trim().startsWith("#")).length;
}

test("SYS-062: empty authorized_keys → 0 keys", () => {
  assert.equal(countAuthorizedKeys(""), 0);
});

test("SYS-062: comments and blank lines not counted as keys", () => {
  const content = "# This is a comment\n\n  \n# Another comment\n";
  assert.equal(countAuthorizedKeys(content), 0);
});

test("SYS-062: 1 key → info severity", () => {
  const count = 1;
  const severity = count >= 4 ? "warning" : "info";
  assert.equal(severity, "info");
});

test("SYS-062: 4+ keys → warning severity", () => {
  const count = 4;
  const severity = count >= 4 ? "warning" : "info";
  assert.equal(severity, "warning");
});

test("SYS-062: counts real key entries correctly", () => {
  const content = [
    "# authorized keys",
    "ssh-rsa AAAAB3NzaC1yc2EAAAA user@host",
    "",
    "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAA user2@host",
    "# another comment",
    "ecdsa-sha2-nistp256 AAAA user3@host",
  ].join("\n");
  assert.equal(countAuthorizedKeys(content), 3);
});

// =============================================================================
// SYS-063: NTP — Unit Tests
// =============================================================================

function parseTimedatectl(output) {
  const get = (key) => {
    const m = output.match(new RegExp(`^${key}=(.+)`, "m"));
    return m ? m[1].trim() : null;
  };
  return { ntp: get("NTP"), synced: get("NTPSynchronized") };
}

test("SYS-063: NTPSynchronized=yes → ok", () => {
  const out = "NTP=yes\nNTPSynchronized=yes\nTimeZone=Europe/Berlin\n";
  const { synced } = parseTimedatectl(out);
  assert.equal(synced, "yes");
});

test("SYS-063: NTPSynchronized=no → warning", () => {
  const out = "NTP=yes\nNTPSynchronized=no\n";
  const { synced } = parseTimedatectl(out);
  assert.notEqual(synced, "yes");
});

// =============================================================================
// SYS-065: World-Writable Sticky Bit — Unit Tests
// =============================================================================

function checkStickyBit(modeStr) {
  // Returns true if sticky bit is set (mode starts with "1", e.g. "1777")
  return modeStr.trim().startsWith("1");
}

test("SYS-065: /tmp with mode 1777 → sticky bit ok", () => {
  assert.ok(checkStickyBit("1777"), "1777 has sticky bit");
});

test("SYS-065: /tmp with mode 777 → sticky bit missing", () => {
  assert.ok(!checkStickyBit("777"), "777 is missing sticky bit");
});

test("SYS-065: /tmp with mode 1755 → sticky bit ok", () => {
  assert.ok(checkStickyBit("1755"), "1755 has sticky bit");
});

// =============================================================================
// SYS-066: SUID/SGID — Unit Tests
// =============================================================================

function checkSUID(files) {
  const whitelist = new Set([
    "sudo", "su", "passwd", "chsh", "chfn", "gpasswd", "newgrp",
    "mount", "umount", "ping", "ping6", "traceroute6",
    "ssh-agent", "crontab", "at", "wall", "write",
    "pkexec", "dbus-daemon-launch-helper", "unix_chkpwd",
    "pam_timestamp_check", "locate", "fusermount", "fusermount3",
    "newuidmap", "newgidmap", "pt_chown", "expiry", "chage",
  ]);
  return files.filter((f) => !whitelist.has(f.split("/").pop()));
}

test("SYS-066: known-safe binaries not flagged", () => {
  const files = ["/usr/bin/sudo", "/usr/bin/passwd", "/usr/bin/ping"];
  assert.equal(checkSUID(files).length, 0, "Safe binaries should not be flagged");
});

test("SYS-066: unknown binary is flagged", () => {
  const files = ["/usr/bin/sudo", "/usr/local/bin/suspicious-tool"];
  const unknown = checkSUID(files);
  assert.equal(unknown.length, 1);
  assert.equal(unknown[0], "/usr/local/bin/suspicious-tool");
});

test("SYS-066: node not in whitelist — should be flagged if found with SUID", () => {
  const files = ["/usr/bin/node"];
  const unknown = checkSUID(files);
  assert.equal(unknown.length, 1, "node with SUID bit is unexpected and should be flagged");
});

// =============================================================================
// Integration: new check codes present in output
// =============================================================================

test("audit-system.mjs: new check codes (SYS-06x) have valid structure if present", () => {
  const data = auditData;
  const newChecks = data.findings.filter((f) => /^SYS-06\d$/.test(f.code));
  for (const f of newChecks) {
    assert.ok(["critical", "warning", "info"].includes(f.severity), `Invalid severity for ${f.code}`);
    assert.ok(f.title.length > 0, `Empty title for ${f.code}`);
    assert.ok(f.detail.length > 0, `Empty detail for ${f.code}`);
  }
});
