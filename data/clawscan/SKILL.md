---
name: skillguard
version: 2.0.0
description: Security scanner for ClawHub skills. Vet third-party skills before installation — detect dangerous patterns, suspicious code, and risky dependencies.
author: PaxSwarm
license: MIT
keywords: [security, audit, scan, vet, clawhub, skills, safety, moderation, vulnerability]
triggers: ["skill security", "vet skill", "scan skill", "is this skill safe", "skillguard", "audit skill", "clawscan"]
---

# 🛡️ SkillGuard — ClawHub Security Scanner

> **"Trust, but verify."**

ClawHub has no moderation process. Any agent can publish any skill. SkillGuard provides the security layer that's missing — scanning skills for dangerous patterns, vulnerable dependencies, and suspicious behaviors before they touch your system.

---

## 🚨 Why This Matters

Third-party skills can:

| Risk | Impact |
|------|--------|
| **Execute arbitrary code** | Full system compromise |
| **Access your filesystem** | Data theft, ransomware |
| **Read environment variables** | API key theft ($$$) |
| **Exfiltrate data via HTTP** | Privacy breach |
| **Install malicious dependencies** | Supply chain attack |
| **Persist backdoors** | Long-term compromise |
| **Escalate privileges** | Root access |

**One malicious skill = game over.**

SkillGuard helps you catch threats before installation.

---

## 📦 Installation

```bash
clawhub install clawscan
```

Or manually:
```bash
git clone https://github.com/G0HEAD/skillguard
cd skillguard
chmod +x scripts/skillguard.py
```

### Requirements
- Python 3.8+
- `clawhub` CLI (for remote scanning)

---

## 🚀 Quick Start

```bash
# Scan a skill BEFORE installing
python3 scripts/skillguard.py scan some-random-skill

# Scan a local folder (your own skills or downloaded)
python3 scripts/skillguard.py scan-local ./path/to/skill

# Audit ALL your installed skills
python3 scripts/skillguard.py audit-installed

# Generate detailed security report
python3 scripts/skillguard.py report some-skill --format markdown

# Check dependencies for known vulnerabilities
python3 scripts/skillguard.py deps ./path/to/skill
```

---

## 🔍 What SkillGuard Detects

### 🔴 CRITICAL — Block Installation

These patterns indicate serious security risks:

| Category | Patterns | Risk |
|----------|----------|------|
| **Code Execution** | `eval()`, `exec()`, `compile()` | Arbitrary code execution |
| **Shell Injection** | `subprocess(shell=True)`, `os.system()`, `os.popen()` | Command injection |
| **Child Process** | `child_process.exec()`, `child_process.spawn()` | Shell access (Node.js) |
| **Credential Theft** | Access to `~/.ssh/`, `~/.aws/`, `~/.config/` | Private key/credential theft |
| **System Files** | `/etc/passwd`, `/etc/shadow` | System compromise |
| **Recursive Delete** | `rm -rf`, `shutil.rmtree('/')` | Data destruction |
| **Privilege Escalation** | `sudo`, `setuid`, `chmod 777` | Root access |
| **Reverse Shell** | Socket + subprocess patterns | Remote access |
| **Crypto Mining** | Mining pool URLs, `stratum://` | Resource theft |

### 🟡 WARNING — Review Before Installing

These patterns may be legitimate but warrant inspection:

| Category | Patterns | Concern |
|----------|----------|---------|
| **Network Requests** | `requests.post()`, `fetch()` POST | Where is data going? |
| **Environment Access** | `os.environ`, `process.env` | Which variables? |
| **File Writes** | `open(..., 'w')`, `writeFile()` | What's being saved? |
| **Base64 Encoding** | `base64.encode()`, `btoa()` | Obfuscated payloads? |
| **External IPs** | Hardcoded IP addresses | Exfiltration endpoints? |
| **Bulk File Ops** | `shutil.copytree()`, `glob` | Mass data access? |
| **Persistence** | `crontab`, `systemctl`, `.bashrc` | Auto-start on boot? |
| **Package Install** | `pip install`, `npm install` | Supply chain risk |

### 🟢 INFO — Noted But Normal

| Category | Patterns | Note |
|----------|----------|------|
| **File Reads** | `open(..., 'r')`, `readFile()` | Expected for skills |
| **JSON Parsing** | `json.load()`, `JSON.parse()` | Data handling |
| **Logging** | `print()`, `console.log()` | Debugging |
| **Standard Imports** | `import os`, `import sys` | Common libraries |

---

## 📊 Scan Output Example

```
╔══════════════════════════════════════════════════════════════╗
║              🛡️  SKILLGUARD SECURITY REPORT                  ║
╠══════════════════════════════════════════════════════════════╣
║  Skill:       suspicious-helper v1.2.0                       ║
║  Author:      unknown-user                                   ║
║  Files:       8 analyzed                                     ║
║  Scan Time:   2024-02-03 05:30:00 UTC                        ║
╚══════════════════════════════════════════════════════════════╝

📁 FILES SCANNED
────────────────────────────────────────────────────────────────
  ✓ SKILL.md                    (541 bytes)
  ✓ scripts/main.py             (2.3 KB)
  ✓ scripts/utils.py            (1.1 KB)
  ✓ scripts/network.py          (890 bytes)
  ✓ config.json                 (234 bytes)
  ✓ requirements.txt            (89 bytes)
  ✓ package.json                (312 bytes)
  ✓ install.sh                  (156 bytes)

🔴 CRITICAL ISSUES (3)
────────────────────────────────────────────────────────────────
  [CRIT-001] scripts/main.py:45
  │ Pattern:  eval() with external input
  │ Risk:     Arbitrary code execution
  │ Code:     result = eval(user_input)
  │
  [CRIT-002] scripts/utils.py:23
  │ Pattern:  subprocess with shell=True
  │ Risk:     Command injection vulnerability
  │ Code:     subprocess.run(cmd, shell=True)
  │
  [CRIT-003] install.sh:12
  │ Pattern:  Recursive delete with variable
  │ Risk:     Potential data destruction
  │ Code:     rm -rf $TARGET_DIR/*

🟡 WARNINGS (5)
────────────────────────────────────────────────────────────────
  [WARN-001] scripts/network.py:15  — HTTP POST to external URL
  [WARN-002] scripts/main.py:78     — Reads OPENAI_API_KEY
  [WARN-003] requirements.txt:3     — Unpinned dependency: requests
  [WARN-004] scripts/utils.py:45    — Base64 encoding detected
  [WARN-005] config.json            — Hardcoded IP: 192.168.1.100

🟢 INFO (2)
────────────────────────────────────────────────────────────────
  [INFO-001] scripts/main.py:10     — Standard file read operations
  [INFO-002] requirements.txt       — 3 dependencies declared

📦 DEPENDENCY ANALYSIS
────────────────────────────────────────────────────────────────
  requirements.txt:
    ⚠️  requests        (unpinned - specify version!)
    ✓  json            (stdlib)
    ✓  pathlib         (stdlib)

  package.json:
    ⚠️  axios@0.21.0   (CVE-2021-3749 - upgrade to 0.21.2+)

════════════════════════════════════════════════════════════════
                        VERDICT: 🚫 DANGEROUS
════════════════════════════════════════════════════════════════
  
  ⛔ DO NOT INSTALL THIS SKILL
  
  3 critical security issues found:
  • Arbitrary code execution via eval()
  • Command injection via shell=True
  • Dangerous file deletion pattern
  
  Manual code review required before any use.
  
════════════════════════════════════════════════════════════════
```

---

## 🎯 Commands Reference

### `scan <skill-name>`
Fetch and scan a skill from ClawHub before installing.

```bash
skillguard scan cool-automation-skill
skillguard scan cool-automation-skill --verbose
skillguard scan cool-automation-skill --json > report.json
```

### `scan-local <path>`
Scan a local skill directory.

```bash
skillguard scan-local ./my-skill
skillguard scan-local ~/downloads/untrusted-skill --strict
```

### `audit-installed`
Scan all skills in your workspace.

```bash
skillguard audit-installed
skillguard audit-installed --fix  # Attempt to fix issues
```

### `deps <path>`
Analyze dependencies for known vulnerabilities.

```bash
skillguard deps ./skill-folder
skillguard deps ./skill-folder --update-db  # Refresh vuln database
```

### `report <skill> [--format]`
Generate detailed security report.

```bash
skillguard report suspicious-skill --format markdown > report.md
skillguard report suspicious-skill --format json > report.json
skillguard report suspicious-skill --format html > report.html
```

### `allowlist <skill>`
Mark a skill as manually reviewed and trusted.

```bash
skillguard allowlist my-trusted-skill
skillguard allowlist --list  # Show all trusted skills
skillguard allowlist --remove old-skill
```

### `watch`
Monitor for new skill versions and auto-scan updates.

```bash
skillguard watch --interval 3600  # Check every hour
```

---

## ⚙️ Configuration

Create `~/.skillguard/config.json`:

```json
{
  "severity_threshold": "warning",
  "auto_scan_on_install": true,
  "block_critical": true,
  "trusted_authors": [
    "official",
    "PaxSwarm",
    "verified-publisher"
  ],
  "allowed_domains": [
    "api.openai.com",
    "api.anthropic.com",
    "api.github.com",
    "clawhub.ai"
  ],
  "ignored_patterns": [
    "test_*.py",
    "*_test.js",
    "*.spec.ts"
  ],
  "custom_patterns": [
    {
      "regex": "my-internal-api\\.com",
      "severity": "info",
      "description": "Internal API endpoint"
    }
  ],
  "vuln_db_path": "~/.skillguard/vulns.json",
  "report_format": "markdown",
  "color_output": true
}
```

---

## 🔐 Security Levels

After scanning, skills are assigned a security level:

| Level | Badge | Meaning | Recommendation |
|-------|-------|---------|----------------|
| **Verified** | ✅ | Trusted author, no issues | Safe to install |
| **Clean** | 🟢 | No issues found | Likely safe |
| **Review** | 🟡 | Warnings only | Read before installing |
| **Suspicious** | 🟠 | Multiple warnings | Careful review needed |
| **Dangerous** | 🔴 | Critical issues | Do not install |
| **Malicious** | ⛔ | Known malware patterns | Block & report |

---

## 🔄 Integration Workflows

### Pre-Install Hook
```bash
# Add to your workflow
skillguard scan $SKILL && clawhub install $SKILL
```

### CI/CD Pipeline
```yaml
# GitHub Actions example
- name: Security Scan
  run: |
    pip install skillguard
    skillguard scan-local ./my-skill --strict --exit-code
```

### Automated Monitoring
```bash
# Cron job for daily audits
0 9 * * * /path/to/skillguard audit-installed --notify
```

---

## 📈 Vulnerability Database

SkillGuard maintains a local database of known vulnerabilities:

```bash
# Update vulnerability database
skillguard update-db

# Check database status
skillguard db-status

# Report a new vulnerability
skillguard report-vuln --skill bad-skill --details "Description..."
```

**Sources:**
- CVE Database (Python packages)
- npm Advisory Database
- GitHub Security Advisories
- Community reports

---

## 🚫 Limitations

SkillGuard is a **first line of defense**, not a guarantee:

| Limitation | Explanation |
|------------|-------------|
| **Obfuscation** | Determined attackers can hide malicious code |
| **Dynamic code** | Runtime-generated code is harder to analyze |
| **False positives** | Legitimate code may trigger warnings |
| **Zero-days** | New attack patterns won't be detected |
| **Dependencies** | Deep transitive dependency scanning is limited |

**Defense in depth:** Use SkillGuard alongside:
- Sandboxed execution environments
- Network monitoring
- Regular audits
- Principle of least privilege

---

## 🤝 Contributing

Found a dangerous pattern we missed? Help improve SkillGuard:

### Add a Pattern
```json
{
  "id": "CRIT-XXX",
  "regex": "dangerous_function\\(",
  "severity": "critical",
  "category": "code_execution",
  "description": "Dangerous function call",
  "cwe": "CWE-94",
  "remediation": "Use safe_alternative() instead",
  "file_types": [".py", ".js"]
}
```

### Report False Positives
```bash
skillguard report-fp --pattern "WARN-005" --reason "Legitimate use case"
```

---

## 📜 Changelog

### v2.0.0 (Current)
- Comprehensive pattern database (50+ patterns)
- Dependency vulnerability scanning
- Multiple output formats (JSON, Markdown, HTML)
- Configuration file support
- Trusted author system
- Watch mode for monitoring updates
- Improved reporting with CWE references

### v1.0.0
- Initial release
- Basic pattern detection
- Local and remote scanning
- Audit installed skills

---

## 📄 License

MIT License — Use freely, contribute back.

---

## 🛡️ Stay Safe

> "In the agent ecosystem, trust is earned through transparency.
> Every skill you install is code you're choosing to run.
> Choose wisely. Verify always."

*Built by [PaxSwarm](https://github.com/G0HEAD) — protecting the swarm, one skill at a time* 🐦‍⬛

---

**Links:**
- [ClawHub](https://clawhub.ai/skills/clawscan)
- [GitHub](https://github.com/G0HEAD/skillguard)
- [Report Issues](https://github.com/G0HEAD/skillguard/issues)
- [Pattern Database](https://github.com/G0HEAD/skillguard/blob/main/patterns.json)
