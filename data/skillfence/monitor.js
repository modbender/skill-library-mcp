#!/usr/bin/env node
// SkillFence — Runtime Skill Monitor for OpenClaw
// Watch what your skills actually do. Not what they claim to do.
// https://cascadeai.dev/skillfence

const fs = require("fs");
const path = require("path");
const { execSync, spawn } = require("child_process");

// --- Session state ---
const STATE_FILE = path.join(
  process.env.HOME || "/tmp",
  ".skillfence-session.json"
);

const LOG_FILE = path.join(
  process.env.HOME || "/tmp",
  ".skillfence-audit.log"
);

const LICENSE_FILE = path.join(
  process.env.HOME || "/tmp",
  ".skillfence-license.json"
);

function loadLicense() {
  try {
    return JSON.parse(fs.readFileSync(LICENSE_FILE, "utf8"));
  } catch {
    return null;
  }
}

function saveLicense(data) {
  try {
    fs.writeFileSync(LICENSE_FILE, JSON.stringify(data, null, 2), "utf8");
  } catch {}
}

function isProUser() {
  const license = loadLicense();
  if (!license || !license.key) return false;
  // Validate key format: SF-PRO-XXXXXXXX-XXXXXXXX-XXXXXXXX
  return /^SF-PRO-[A-F0-9]{8}-[A-F0-9]{8}-[A-F0-9]{8}$/.test(license.key);
}

function loadState() {
  try {
    return JSON.parse(fs.readFileSync(STATE_FILE, "utf8"));
  } catch {
    return {
      started: new Date().toISOString(),
      alerts: 0,
      blocks: 0,
      skills_monitored: 0,
      events: [],
      network_calls: [],
      file_access: [],
      credential_reads: [],
    };
  }
}

function saveState(state) {
  try {
    fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2), "utf8");
  } catch {}
}

function appendLog(entry) {
  try {
    const line = `[${new Date().toISOString()}] ${entry}\n`;
    fs.appendFileSync(LOG_FILE, line, "utf8");
  } catch {}
}

// --- Threat Intelligence ---
// Known malicious C2 servers, domains, and IPs from ClawHavoc research
const KNOWN_C2 = [
  "54.91.154.110",           // ClawHavoc reverse shell C2
  "glot.io",                 // Used to host encoded payloads
  "raw.githubusercontent.com", // Common malware staging (flagged, not blocked)
];

const SUSPICIOUS_DOMAINS = [
  /\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/,  // Raw IP addresses
  /ngrok\.io/,
  /webhook\.site/,
  /requestbin\./,
  /pipedream\.net/,
  /burpcollaborator\./,
  /interact\.sh/,
  /oast\./,
  /dnslog\./,
  /ceye\.io/,
  /beeceptor\./,
];

// Sensitive file paths that skills should not access
const SENSITIVE_PATHS = [
  ".env",
  ".openclaw/config.json",
  ".openclaw/credentials",
  "openclaw.json",
  ".clawd/config",
  ".ssh/",
  ".gnupg/",
  ".aws/credentials",
  ".aws/config",
  ".gcloud/",
  ".azure/",
  ".config/gh/",
  ".netrc",
  ".npmrc",
  ".pypirc",
  "keychain",
  "Keychain",
  ".password-store",
  "wallet.dat",
  ".bitcoin/",
  ".ethereum/",
  ".solana/",
  ".phantom/",
  "cookies.sqlite",
  "Login Data",        // Chrome passwords
  "Cookies",           // Browser cookies
  "Local State",       // Chrome encryption key
];

// Dangerous command patterns
const DANGEROUS_COMMANDS = [
  /curl\s+.*\|.*sh/i,             // curl pipe to shell
  /wget\s+.*\|.*sh/i,             // wget pipe to shell
  /base64\s+(-d|--decode)/i,      // base64 decode (often precedes exec)
  /eval\s*\(/i,                   // eval()
  /os\.system\s*\(/i,             // Python os.system
  /subprocess\.(call|run|Popen)/i, // Python subprocess
  /exec\s*\(\s*['"`]/i,           // exec("...")
  /child_process/i,               // Node child_process require
  /\bsh\s+-c\s+/i,               // sh -c (command execution)
  /\/dev\/tcp\//i,                // Bash reverse shell
  /nc\s+(-e|-c)/i,               // netcat reverse shell
  /nohup\s+.*&/i,                // Background persistent process
  /crontab\s+-/i,                // Cron modification
  /chmod\s+[+0-7]*[xs]/i,        // Setting executable permissions
  /rm\s+-rf\s+[\/~]/i,           // Recursive delete from root/home
];

// --- Skill Scanner ---
// Scans installed skill files for suspicious patterns

function getSkillsDir() {
  const candidates = [
    path.join(process.env.HOME || "", ".openclaw", "skills"),
    path.join(process.env.HOME || "", "clawd", "skills"),
    path.join(process.env.HOME || "", ".clawd", "skills"),
    path.join(process.env.HOME || "", ".config", "openclaw", "skills"),
  ];
  for (const dir of candidates) {
    if (fs.existsSync(dir)) return dir;
  }
  return null;
}

function scanSkillFile(filePath) {
  const findings = [];
  let content;
  try {
    content = fs.readFileSync(filePath, "utf8");
  } catch {
    return findings;
  }

  const fileName = path.basename(filePath);
  const skillName = path.basename(path.dirname(filePath));

  // Check for known C2 addresses
  for (const c2 of KNOWN_C2) {
    if (content.includes(c2)) {
      findings.push({
        severity: "CRITICAL",
        type: "known_c2",
        skill: skillName,
        file: fileName,
        detail: `Contains known C2 address: ${c2}`,
        action: "BLOCK — this skill communicates with a known malicious server",
      });
    }
  }

  // Check for suspicious domain patterns
  for (const pattern of SUSPICIOUS_DOMAINS) {
    const matches = content.match(pattern);
    if (matches) {
      findings.push({
        severity: "HIGH",
        type: "suspicious_domain",
        skill: skillName,
        file: fileName,
        detail: `Suspicious domain/IP pattern: ${matches[0]}`,
        action: "REVIEW — skill connects to suspicious endpoint",
      });
    }
  }

  // Check for dangerous command patterns
  for (const pattern of DANGEROUS_COMMANDS) {
    const matches = content.match(pattern);
    if (matches) {
      findings.push({
        severity: "HIGH",
        type: "dangerous_command",
        skill: skillName,
        file: fileName,
        detail: `Dangerous command pattern: ${matches[0]}`,
        action: "REVIEW — skill executes potentially dangerous commands",
      });
    }
  }

  // Check for credential file access
  for (const sensPath of SENSITIVE_PATHS) {
    if (content.includes(sensPath)) {
      findings.push({
        severity: "HIGH",
        type: "credential_access",
        skill: skillName,
        file: fileName,
        detail: `References sensitive path: ${sensPath}`,
        action: "REVIEW — skill may access credentials or secrets",
      });
    }
  }

  // Check for base64 encoded content (common obfuscation)
  const b64Regex = /[A-Za-z0-9+\/]{40,}={0,2}/g;
  const b64Matches = content.match(b64Regex);
  if (b64Matches && b64Matches.length > 0) {
    // Only flag if there's also a decode operation nearby
    if (/base64|atob|decode|Buffer\.from/i.test(content)) {
      findings.push({
        severity: "MEDIUM",
        type: "encoded_payload",
        skill: skillName,
        file: fileName,
        detail: `Contains ${b64Matches.length} base64-encoded string(s) with decode operations`,
        action: "REVIEW — skill may contain obfuscated payloads",
      });
    }
  }

  // Check for network exfiltration patterns
  if (/fetch|axios|request|http\.get|https\.get|XMLHttpRequest|curl|wget/i.test(content)) {
    // Check if network call includes reading sensitive data
    if (/readFile|readFileSync|\.env|config|credential|secret|token|key|password/i.test(content)) {
      findings.push({
        severity: "HIGH",
        type: "data_exfiltration",
        skill: skillName,
        file: fileName,
        detail: "Combines network requests with sensitive data reads",
        action: "REVIEW — potential data exfiltration pattern",
      });
    }
  }

  return findings;
}

function scanAllSkills() {
  const skillsDir = getSkillsDir();
  if (!skillsDir) {
    return { error: "No skills directory found", scanned: 0, findings: [] };
  }

  const allFindings = [];
  let scanned = 0;

  try {
    const skills = fs.readdirSync(skillsDir);
    for (const skill of skills) {
      const skillPath = path.join(skillsDir, skill);
      if (!fs.statSync(skillPath).isDirectory()) continue;

      scanned++;
      const files = walkDir(skillPath);
      for (const file of files) {
        // Skip node_modules, .git, binary files
        if (file.includes("node_modules") || file.includes(".git/")) continue;
        const ext = path.extname(file).toLowerCase();
        if ([".js", ".ts", ".py", ".sh", ".md", ".json", ".yaml", ".yml", ".toml"].includes(ext) || ext === "") {
          const findings = scanSkillFile(file);
          allFindings.push(...findings);
        }
      }
    }
  } catch (err) {
    return { error: err.message, scanned, findings: allFindings };
  }

  return { scanned, findings: allFindings };
}

function walkDir(dir, fileList = []) {
  try {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        if (!entry.name.startsWith(".") && entry.name !== "node_modules") {
          walkDir(fullPath, fileList);
        }
      } else {
        fileList.push(fullPath);
      }
    }
  } catch {}
  return fileList;
}

// --- Process Monitor ---
// Checks running processes for suspicious activity

function checkRunningProcesses() {
  const suspicious = [];
  try {
    const platform = process.platform;
    let output;

    if (platform === "darwin" || platform === "linux") {
      output = execSync("ps aux 2>/dev/null", { encoding: "utf8", timeout: 5000 });
    } else {
      return suspicious; // Windows not yet supported
    }

    const lines = output.split("\n");
    for (const line of lines) {
      const lower = line.toLowerCase();

      // Check for reverse shells
      if (/\/dev\/tcp|nc\s+-e|ncat.*-e|bash\s+-i.*>&/i.test(lower)) {
        suspicious.push({
          severity: "CRITICAL",
          type: "reverse_shell",
          detail: `Active reverse shell detected: ${line.trim().substring(0, 120)}`,
          action: "KILL — active reverse shell connection",
        });
      }

      // Check for crypto miners
      if (/xmrig|minerd|cpuminer|cryptonight|stratum\+tcp/i.test(lower)) {
        suspicious.push({
          severity: "CRITICAL",
          type: "crypto_miner",
          detail: `Crypto miner process detected: ${line.trim().substring(0, 120)}`,
          action: "KILL — unauthorized crypto mining",
        });
      }

      // Check for suspicious curl/wget with piping
      if (/curl.*\|.*sh|wget.*\|.*sh|curl.*\|.*bash/i.test(lower)) {
        suspicious.push({
          severity: "HIGH",
          type: "remote_exec",
          detail: `Remote code execution: ${line.trim().substring(0, 120)}`,
          action: "REVIEW — downloading and executing remote code",
        });
      }
    }
  } catch {}
  return suspicious;
}

// --- Network Monitor ---
// Checks recent network connections for suspicious activity

function checkNetworkConnections() {
  const suspicious = [];
  try {
    const platform = process.platform;
    let output;

    if (platform === "darwin") {
      output = execSync("lsof -i -n -P 2>/dev/null | head -200", { encoding: "utf8", timeout: 5000 });
    } else if (platform === "linux") {
      output = execSync("ss -tunapl 2>/dev/null | head -200", { encoding: "utf8", timeout: 5000 });
    } else {
      return suspicious;
    }

    const lines = output.split("\n");
    for (const line of lines) {
      // Check for connections to known C2
      for (const c2 of KNOWN_C2) {
        if (line.includes(c2)) {
          suspicious.push({
            severity: "CRITICAL",
            type: "c2_connection",
            detail: `Active connection to known C2: ${c2}`,
            action: "KILL — terminate connection immediately",
          });
        }
      }

      // Check for connections to raw IPs on unusual ports
      const ipPortMatch = line.match(/(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)/);
      if (ipPortMatch) {
        const port = parseInt(ipPortMatch[2]);
        const commonPorts = [80, 443, 8080, 8443, 53, 22, 3000, 5000, 8000];
        if (!commonPorts.includes(port) && port > 1024) {
          // Unusual high port on raw IP — flag it
          suspicious.push({
            severity: "MEDIUM",
            type: "unusual_connection",
            detail: `Connection to ${ipPortMatch[1]}:${port}`,
            action: "REVIEW — unusual port on direct IP connection",
          });
        }
      }
    }
  } catch {}
  return suspicious;
}

// --- File Watcher ---
// Checks if any sensitive files have been recently accessed

function checkSensitiveFileAccess() {
  const accessed = [];
  const home = process.env.HOME || "";

  for (const sensPath of SENSITIVE_PATHS) {
    const fullPath = path.join(home, sensPath);
    try {
      const stat = fs.statSync(fullPath);
      const accessedAgo = Date.now() - stat.atimeMs;
      // Flagged if accessed in last 5 minutes
      if (accessedAgo < 5 * 60 * 1000) {
        accessed.push({
          severity: "MEDIUM",
          type: "recent_credential_access",
          detail: `${sensPath} accessed ${Math.round(accessedAgo / 1000)}s ago`,
          action: "REVIEW — sensitive file was recently read",
        });
      }
    } catch {
      // File doesn't exist or can't stat — that's fine
    }
  }
  return accessed;
}

// --- Scan a specific skill ---
function scanSingleSkill(skillName) {
  const skillsDir = getSkillsDir();
  if (!skillsDir) {
    return { error: "No skills directory found", findings: [] };
  }

  const skillPath = path.join(skillsDir, skillName);
  if (!fs.existsSync(skillPath)) {
    return { error: `Skill '${skillName}' not found`, findings: [] };
  }

  const allFindings = [];
  const files = walkDir(skillPath);
  for (const file of files) {
    if (file.includes("node_modules") || file.includes(".git/")) continue;
    const ext = path.extname(file).toLowerCase();
    if ([".js", ".ts", ".py", ".sh", ".md", ".json", ".yaml", ".yml", ".toml"].includes(ext) || ext === "") {
      const findings = scanSkillFile(file);
      allFindings.push(...findings);
    }
  }

  return {
    skill: skillName,
    files_scanned: files.length,
    findings: allFindings,
    verdict: allFindings.some(f => f.severity === "CRITICAL") ? "DANGEROUS" :
             allFindings.some(f => f.severity === "HIGH") ? "SUSPICIOUS" :
             allFindings.length > 0 ? "REVIEW" : "CLEAN",
  };
}

// --- Full System Scan ---
function fullScan() {
  const state = loadState();
  const results = {
    timestamp: new Date().toISOString(),
    skill_scan: scanAllSkills(),
    process_check: checkRunningProcesses(),
    network_check: checkNetworkConnections(),
    credential_check: checkSensitiveFileAccess(),
  };

  // Count totals
  const allFindings = [
    ...results.skill_scan.findings,
    ...results.process_check,
    ...results.network_check,
    ...results.credential_check,
  ];

  const critical = allFindings.filter(f => f.severity === "CRITICAL").length;
  const high = allFindings.filter(f => f.severity === "HIGH").length;
  const medium = allFindings.filter(f => f.severity === "MEDIUM").length;

  results.summary = {
    skills_scanned: results.skill_scan.scanned,
    total_findings: allFindings.length,
    critical,
    high,
    medium,
    verdict: critical > 0 ? "🔴 CRITICAL THREATS FOUND" :
             high > 0 ? "🟠 HIGH-RISK ISSUES FOUND" :
             medium > 0 ? "🟡 REVIEW RECOMMENDED" : "🟢 ALL CLEAR",
  };

  // Update state
  state.alerts += allFindings.length;
  state.skills_monitored = results.skill_scan.scanned;
  state.events.push({
    type: "full_scan",
    timestamp: results.timestamp,
    findings: allFindings.length,
  });

  // Keep only last 100 events
  if (state.events.length > 100) {
    state.events = state.events.slice(-100);
  }

  saveState(state);
  appendLog(`SCAN: ${allFindings.length} findings (${critical} critical, ${high} high, ${medium} medium)`);

  return results;
}

// --- Main execution ---
async function main() {
  const args = process.argv.slice(2);
  const command = args[0];

  switch (command) {
    case "--status": {
      const state = loadState();
      const pro = isProUser();
      console.log(JSON.stringify({
        status: "active",
        monitoring: true,
        session_start: state.started,
        alerts: state.alerts,
        blocks: state.blocks,
        skills_monitored: state.skills_monitored,
        recent_events: state.events.slice(-5),
        tier: pro ? "pro" : "free",
        upgrade_url: pro ? null : "https://cascadeai.dev/skillfence",
      }));
      break;
    }

    case "--scan": {
      const results = fullScan();
      console.log(JSON.stringify(results, null, 2));
      break;
    }

    case "--scan-skill": {
      const skillName = args[1];
      if (!skillName) {
        console.log(JSON.stringify({ error: "Usage: --scan-skill <skill-name>" }));
        return;
      }
      const results = scanSingleSkill(skillName);
      console.log(JSON.stringify(results, null, 2));
      break;
    }

    case "--check-network": {
      const results = checkNetworkConnections();
      console.log(JSON.stringify({
        timestamp: new Date().toISOString(),
        connections: results,
        total: results.length,
      }, null, 2));
      break;
    }

    case "--check-processes": {
      const results = checkRunningProcesses();
      console.log(JSON.stringify({
        timestamp: new Date().toISOString(),
        suspicious: results,
        total: results.length,
      }, null, 2));
      break;
    }

    case "--check-credentials": {
      const results = checkSensitiveFileAccess();
      console.log(JSON.stringify({
        timestamp: new Date().toISOString(),
        accessed: results,
        total: results.length,
      }, null, 2));
      break;
    }

    case "--audit-log": {
      try {
        const log = fs.readFileSync(LOG_FILE, "utf8");
        const lines = log.trim().split("\n").slice(-50);
        console.log(JSON.stringify({
          log_file: LOG_FILE,
          entries: lines.length,
          recent: lines,
        }));
      } catch {
        console.log(JSON.stringify({ log_file: LOG_FILE, entries: 0, recent: [] }));
      }
      break;
    }

    case "--watch": {
      // Quick watch — run all checks and report
      const state = loadState();
      const network = checkNetworkConnections();
      const processes = checkRunningProcesses();
      const credentials = checkSensitiveFileAccess();
      const all = [...network, ...processes, ...credentials];

      state.alerts += all.length;
      state.events.push({
        type: "watch",
        timestamp: new Date().toISOString(),
        findings: all.length,
      });
      saveState(state);

      if (all.length > 0) {
        appendLog(`WATCH: ${all.length} runtime findings`);
      }

      console.log(JSON.stringify({
        timestamp: new Date().toISOString(),
        runtime_findings: all,
        total: all.length,
        verdict: all.some(f => f.severity === "CRITICAL") ? "🔴 CRITICAL" :
                 all.some(f => f.severity === "HIGH") ? "🟠 HIGH RISK" :
                 all.length > 0 ? "🟡 REVIEW" : "🟢 CLEAR",
      }, null, 2));
      break;
    }

    case "--activate": {
      const key = args[1];
      if (!key) {
        console.log(JSON.stringify({ error: "Usage: --activate <license-key>" }));
        return;
      }
      if (!/^SF-PRO-[A-F0-9]{8}-[A-F0-9]{8}-[A-F0-9]{8}$/.test(key)) {
        console.log(JSON.stringify({ error: "Invalid license key format. Keys look like: SF-PRO-XXXXXXXX-XXXXXXXX-XXXXXXXX" }));
        return;
      }
      saveLicense({
        key: key,
        activated: new Date().toISOString(),
        machine: require("os").hostname(),
      });
      appendLog(`PRO: License activated on ${require("os").hostname()}`);
      console.log(JSON.stringify({
        success: true,
        message: "SkillFence Pro activated! All Pro features unlocked.",
        key: key.substring(0, 12) + "...",
        features: [
          "Persistent threat dashboard (--dashboard)",
          "Custom threat rules (--add-rule)",
          "Priority threat intelligence",
          "Webhook alerts (coming soon)",
        ],
      }));
      break;
    }

    case "--license": {
      const license = loadLicense();
      if (license && license.key) {
        console.log(JSON.stringify({
          tier: "pro",
          key: license.key.substring(0, 12) + "...",
          activated: license.activated,
          machine: license.machine,
        }));
      } else {
        console.log(JSON.stringify({
          tier: "free",
          upgrade_url: "https://cascadeai.dev/skillfence",
          message: "Run --activate <key> to unlock Pro features",
        }));
      }
      break;
    }

    case "--dashboard": {
      if (!isProUser()) {
        console.log(JSON.stringify({
          error: "Pro feature",
          message: "Dashboard requires SkillFence Pro. Get your key at https://cascadeai.dev/skillfence",
          activate: "Run --activate <key> after purchase",
        }));
        return;
      }

      // Generate dashboard HTML with real data injected
      const state = loadState();
      const scanResults = fullScan();
      const skills = [];

      const skillsDir = getSkillsDir();
      if (skillsDir) {
        try {
          const dirs = fs.readdirSync(skillsDir);
          for (const d of dirs) {
            const sp = path.join(skillsDir, d);
            if (!fs.statSync(sp).isDirectory()) continue;
            const singleScan = scanSingleSkill(d);
            skills.push({
              name: d,
              verdict: singleScan.verdict,
              files: singleScan.files_scanned,
              findings: singleScan.findings.map(f => ({
                severity: f.severity,
                type: f.type,
                detail: f.detail,
              })),
            });
          }
        } catch {}
      }

      const dashData = {
        session: state,
        scan: scanResults,
        skills: skills,
      };

      // Read the dashboard template and inject data
      const dashTemplatePath = path.join(__dirname, "dashboard.html");
      try {
        let template = fs.readFileSync(dashTemplatePath, "utf8");
        const dataJson = JSON.stringify(dashData);
        template = template.replace(
          /\/\*SKILLFENCE_DATA_INJECT\*\/null\/\*END_INJECT\*\//,
          "/*SKILLFENCE_DATA_INJECT*/" + dataJson + "/*END_INJECT*/"
        );

        const outputPath = path.join(
          process.env.HOME || "/tmp",
          ".skillfence-dashboard.html"
        );
        fs.writeFileSync(outputPath, template, "utf8");

        console.log(JSON.stringify({
          success: true,
          dashboard: outputPath,
          message: "Dashboard generated! Open in your browser:",
          open_command: process.platform === "darwin"
            ? `open "${outputPath}"`
            : process.platform === "win32"
            ? `start "${outputPath}"`
            : `xdg-open "${outputPath}"`,
        }));

        // Try to open in browser automatically
        try {
          if (process.platform === "darwin") {
            execSync(`open "${outputPath}"`);
          } else if (process.platform === "win32") {
            execSync(`start "" "${outputPath}"`, { shell: true });
          } else {
            execSync(`xdg-open "${outputPath}"`);
          }
        } catch {}

      } catch (err) {
        console.log(JSON.stringify({
          error: "Could not generate dashboard",
          detail: err.message,
          hint: "Make sure dashboard.html exists in the skill directory",
        }));
      }
      break;
    }

    case "--reset": {
      try {
        fs.unlinkSync(STATE_FILE);
        fs.unlinkSync(LOG_FILE);
      } catch {}
      console.log(JSON.stringify({ reset: true, message: "Session state and logs cleared" }));
      break;
    }

    default: {
      // If called with a message, check if it contains suspicious patterns
      const input = args.join(" ");
      if (!input) {
        console.log(JSON.stringify({
          name: "SkillFence",
          version: "1.0.0",
          commands: [
            "--scan          Full system scan (skills + network + processes + credentials)",
            "--scan-skill X  Scan a specific skill",
            "--watch         Quick runtime check (network + processes + credentials)",
            "--check-network Check active network connections",
            "--check-processes Check running processes",
            "--check-credentials Check recent sensitive file access",
            "--status        Session status and stats",
            "--audit-log     View recent audit log entries",
            "--activate KEY  Activate Pro license",
            "--license       Check license status",
            "--dashboard     Generate Pro dashboard (Pro only)",
            "--reset         Clear session state and logs",
          ],
        }));
        return;
      }

      // Check message for dangerous patterns (inline protection)
      const findings = [];
      for (const pattern of DANGEROUS_COMMANDS) {
        if (pattern.test(input)) {
          findings.push({
            severity: "HIGH",
            type: "dangerous_command_in_message",
            detail: `Message contains dangerous pattern: ${input.match(pattern)[0]}`,
            action: "BLOCK — do not execute this command",
          });
        }
      }

      for (const c2 of KNOWN_C2) {
        if (input.includes(c2)) {
          findings.push({
            severity: "CRITICAL",
            type: "known_c2_in_message",
            detail: `Message references known C2: ${c2}`,
            action: "BLOCK — known malicious server",
          });
        }
      }

      if (findings.length > 0) {
        const state = loadState();
        state.alerts += findings.length;
        state.blocks += findings.length;
        state.events.push({
          type: "inline_block",
          timestamp: new Date().toISOString(),
          findings: findings.length,
        });
        saveState(state);
        appendLog(`BLOCK: ${findings.length} dangerous patterns in message`);
      }

      console.log(JSON.stringify({
        checked: true,
        dangerous: findings.length > 0,
        findings,
      }));
      break;
    }
  }
}

main().catch((err) => {
  console.log(JSON.stringify({ error: "internal", detail: err.message }));
  process.exit(0); // Never crash — always let OpenClaw continue
});
