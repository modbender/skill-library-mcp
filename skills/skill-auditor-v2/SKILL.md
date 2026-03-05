---
name: skill-auditor
version: 2.0.0
description: >
  Security scanner for OpenClaw skills. Detects malicious code, obfuscated payloads,
  prompt injection, social engineering, typosquatting, and data exfiltration before
  installation. Features 0-100 numeric risk scoring, MITRE ATT&CK mappings, base64/hex
  deobfuscation, IoC database, whitelist system, and SHA256 file inventory. Use before
  installing any third-party skill. Triggers: audit skill, check security, scan skill,
  is this skill safe, security review, quarantine.
license: MIT
compatibility:
  openclaw: ">=0.10"
metadata:
  openclaw:
    requires:
      bins: ["python3"]
---

# Skill Auditor v2.0 🔍🛡️

Comprehensive security scanner for OpenClaw/ClawHub skills. Merges static analysis, deobfuscation, and threat intelligence into a single Python tool.

## When to Use

- Before installing **any** third-party skill from ClawHub
- When reviewing skill updates for security regressions
- To audit your own skills before publishing
- When someone asks: "is this skill safe?", "audit this", "check security"

## Quick Start

### Audit a local skill directory
```bash
python3 {baseDir}/scripts/audit_skill.py /path/to/skill --human
```

### Audit a ClawHub skill by slug
```bash
python3 {baseDir}/scripts/audit_skill.py --slug skill-name --human
```

### Quarantine workflow (audit + prompt to install)
```bash
bash {baseDir}/scripts/quarantine.sh /path/to/skill
bash {baseDir}/scripts/quarantine.sh --slug skill-name
```

### JSON output for programmatic use
```bash
python3 {baseDir}/scripts/audit_skill.py /path/to/skill --json
```

## Scoring System

| Score | Level | Action |
|-------|-------|--------|
| 0–20 | ✅ SAFE | Auto-install OK |
| 21–40 | 🟢 LOW RISK | Proceed with caution |
| 41–60 | 🟡 MEDIUM RISK | Manual review required |
| 61–80 | 🟠 HIGH RISK | Expert review needed |
| 81–100 | 🔴 CRITICAL | Do NOT install |

Exit codes: `0` = safe (≤20), `1` = review (21–60), `2` = dangerous (>60)

## Detection Layers

### Layer 1: Static Pattern Analysis
- 10+ scan categories with regex patterns
- Shell execution, network calls, env access, filesystem escape
- Prompt injection, data exfiltration, crypto wallet access
- Dynamic imports, browser credential theft, fake prerequisites

### Layer 2: Deobfuscation
- Base64 string extraction and decode → re-scan decoded content
- Hex escape sequence decode → re-scan
- Detects hidden commands, C2 IPs in encoded payloads

### Layer 3: Threat Intelligence
- IoC database: known malicious IPs, domains
- Social engineering detection: urgency, false authority, fear tactics
- MITRE ATT&CK ID mapping on every finding
- Whitelist system reduces score for safe binaries/domains

### Additional Checks
- SHA256 file inventory for integrity verification
- Typosquat detection (Levenshtein distance on package names)
- Zero-width character detection in SKILL.md
- Comment-context severity reduction (findings in comments scored lower)
- Permission scope analysis (what tools does the skill request?)

## IoC Database

Structured threat data in `references/ioc-database.json`. Update when new threats emerge. The scanner auto-loads this file at runtime.

## References

- `references/ioc-database.json` — Structured IoC data (IPs, domains, patterns)
- `references/known-patterns.md` — Human-readable threat documentation
- `references/prompt-injection-patterns.md` — Prompt injection pattern reference

## Credits

Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)

Fork of [skill-auditor-pro](https://clawhub.ai/skills/skill-auditor-pro) by sypsyp97, merged with [skill-security-auditor](https://clawhub.ai/skills/skill-security-auditor) by akm626.
