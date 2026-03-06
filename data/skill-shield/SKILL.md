---
name: skill-shield
version: 0.6.1
description: "Security audit tool for ClawHub skills. Scans a skill directory with 65 detection patterns, anti-obfuscation analysis, and dual rating system (Security + Compliance). v0.6.1 fixes batch scan performance by skipping venv/node_modules directories. Use when: installing a new skill, reviewing skill safety, or auditing permissions."
---

# Skill Shield v0.6.1 — Security Auditor

Scan any skill directory for permissions and dangerous patterns. Get a safety rating before you install.

## Usage

Run the scanner on a skill directory:

```bash
python3 scripts/scan.py /path/to/skill-directory
```

### SARIF Output (GitHub Code Scanning)

```bash
python3 scripts/scan.py /path/to/skill-directory --sarif
```

### Output

The script prints two blocks to stdout:

1. A JSON report (between `--- JSON START ---` and `--- JSON END ---` markers)
2. A Markdown report (between `--- MD START ---` and `--- MD END ---` markers)

### Save reports to files

```bash
python3 scripts/scan.py /path/to/skill-directory --output-dir /path/to/output
```

This creates `report.json` and `report.md` in the output directory.

## Safety Ratings

| Grade | Meaning | Action |
|-------|---------|--------|
| A | Safe | Install freely |
| B | Low risk | Minor concerns, generally safe |
| C | Needs review | Review flagged patterns before installing |
| D | High risk | Significant dangerous patterns detected |
| F | Dangerous | Do not install without thorough manual review |

## Detection Capabilities (65 patterns, 11 categories)

- File deletion: rm -rf, shred, unlink, rmtree, rimraf, del /f (7 patterns)
- Network exfiltration: curl POST, wget --post, requests.post, fetch POST, netcat reverse shell, DNS exfil, pipe to curl, socat (9 patterns)
- Environment variable access: process.env, os.environ, .env files, printenv (5 patterns)
- Secret/key access: .ssh/, .gnupg/, private keys, wallets, tokens, passwords, keychain, cloud credentials (8 patterns)
- Privilege escalation: sudo, su, chmod 777, chown, setuid/setgid, doas (6 patterns)
- Code execution: eval, exec(), Function(), child_process, subprocess, os.system, os.popen, compile (8 patterns)
- Data collection: /etc/passwd, /etc/shadow, whoami, hostname, ifconfig, /proc/self (6 patterns)
- Persistence: crontab, systemd, rc.local, shell profile modification, autostart (5 patterns)
- Obfuscation: long base64 strings, hex escapes, charCode, base64 decode, string reversal (5 patterns)
- Cryptocurrency/mining: xmrig/minerd, mining pool URLs, wallet addresses (3 patterns)
- Shell injection: backtick execution, pipe to shell, download-and-execute (3 patterns)

## Key Features

### Permission Declaration Audit (unique to skill-shield)
Compares tools declared in SKILL.md against tools actually used in code. Reports:
- Undeclared permissions with sensitivity scoring (1-5)
- Unused declared permissions
- Declaration coverage ratio
- Per-tool risk recommendations

### Anti-Obfuscation Analysis
Automatically decodes base64 and hex-encoded content, then re-scans decoded output for dangerous patterns. Obfuscated findings receive elevated severity.

### Context-Aware False Positive Reduction
- Comments and docstrings: severity reduced by 2
- Markdown code blocks in SKILL.md: severity reduced by 2 (examples, not real code)
- Pattern definition lines in scanner source: skipped entirely
- Original vs adjusted severity shown in reports (e.g., "Low (2←4)")

### CWE References
Every detection pattern includes a CWE (Common Weakness Enumeration) reference for professional vulnerability classification.

## v0.6.0 — Batch Scan Mode

### Batch Scanning
Scan all skills in a directory at once with `--batch`:

```bash
python3 scripts/scan.py /path/to/skills/ --batch
python3 scripts/scan.py /path/to/skills/ --batch --json-summary
python3 scripts/scan.py /path/to/skills/ --batch --json-summary -o /path/to/output
```

### Performance
- Skips venv/node_modules/dist/.git directories automatically
- Caps at 200 script files per skill for safety
- 164 skills scanned in ~8 seconds

### Output
- Markdown table with summary stats and per-skill ratings (default)
- JSON summary with `--json-summary` flag for machine consumption
- Writes `batch-summary.json` when using `-o`

## v0.5.0 — SARIF Output Format

### GitHub Code Scanning Integration
Use `--sarif` flag to output SARIF 2.1.0 format, compatible with:
- GitHub Code Scanning (upload-sarif action)
- VS Code SARIF Viewer extension
- SARIF Web Viewer

```bash
python3 scripts/scan.py /path/to/skill --sarif > report.sarif
python3 scripts/scan.py /path/to/skill --sarif -o /path/to/output
```

### SARIF Features
- Full rule definitions for all 65 detection patterns
- CWE taxonomy references (MITRE CWE 4.14)
- Partial fingerprints for deduplication across runs
- Security severity scores (2.0-10.0 scale)
- Skill-shield metadata in run properties (ratings, recommendation)

## v0.4.0 — Security Tool False Positive Fix

### String Literal Context Detection
Regex patterns and string constants inside security tools (scanners, auditors) are no longer flagged as dangerous code. The scanner now recognizes when a pattern like `rm -rf` or `curl POST` appears inside a string literal (quotes, regex, array) and reduces severity accordingly.

### Ignore-Next-Line Support
Add `# skill-shield: ignore-next-line` above any line to suppress the next finding. Useful for known-safe patterns in security tools.

### Results
- 5 security audit tools reclassified from F to A/C/D (agents-skill-security-audit, ai-skill-scanner, skulk-skill-scanner, aoi-prompt-injection-sentinel, aoi-sandbox-shield-lite)
- 0 regressions on known-safe skills

## v0.3.0 — Dual Rating System

### Security Rating (code safety)
Based purely on dangerous code patterns found in executable files. Not affected by permission declarations.

### Compliance Rating (documentation quality)
Based on permission declaration completeness: does SKILL.md declare the tools actually used in code?

### Recommendation
Combines both ratings into an actionable recommendation:
- **install** — Security A/B + Compliance A/B
- **install_with_review** — Code is safe but permissions undeclared (likely poor docs, not malicious)
- **review_required** — Security patterns flagged
- **do_not_install** — Significant security concerns
- **documentation_only** — No executable code (pure SKILL.md guidance)

### False Positive Fixes (v0.3.0)
- JS template literals (backticks) no longer flagged as shell execution
- Variable names (hostname, whoami) no longer flagged as commands
- Shell script normal $VAR usage no longer floods findings
- `os.environ.get("KEY")` / `process.env.KEY` reduced severity (standard practice)
- `--disable-setuid-sandbox` (browser flag) reduced severity
- Documentation-only skills marked as N/A instead of getting A rating

## Exit Codes

| Code | Ratings | Meaning |
|------|---------|---------|
| 0 | A, B | Safe to install |
| 1 | C, D | Review recommended |
| 2 | F | Do not install |

## Support

Tips welcome: `0x6c730bDcfC762e23cE53aD991B75ab9852e87806` (Base)
Moltbook: https://www.moltbook.com/u/Yuqian
Twitter: @Yuqian0202
