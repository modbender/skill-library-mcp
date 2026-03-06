---
name: skulk-skill-scanner
description: "Scan OpenClaw skill folders for security red flags before installing or publishing. Detects data exfiltration, credential theft, prompt injection, destructive commands, obfuscation, privilege escalation, and supply chain risks. Use when: evaluating a skill from ClawHub before install, auditing your own skills before publishing, or reviewing any SKILL.md for safety. NOT for: general code review or vulnerability scanning of non-skill codebases."
---

# Skill Scanner

Security scanner for OpenClaw agent skills. Static analysis for red flags.

## Usage

```bash
node scripts/scanner.js <path-to-skill> [--verbose] [--json] [--summary] [--ignore <path>] [--include-self]
```

## Examples

```bash
# Scan a downloaded skill folder before enabling it
clawhub inspect some-skill
node scripts/scanner.js ./skills/some-skill --verbose

# Scan your own skill before publishing
node scripts/scanner.js ./skills/my-skill

# JSON output for automation
node scripts/scanner.js ./skills/my-skill --json

# One-line summary output for heartbeat checks
node scripts/scanner.js ./skills/my-skill --summary

# Include scanner internals (off by default to reduce self-scan noise)
node scripts/scanner.js ./skills/skulk-skill-scanner --include-self
```

## What It Catches

| Severity | Flags |
|----------|-------|
| 🔴 Critical | Data exfiltration, credential access, safety overrides, destructive commands |
| 🟠 High | Obfuscation (base64/eval), unknown network access, env scanning, privilege escalation, hidden instructions |
| 🟡 Medium | Writes outside workspace, package installs (supply chain), messaging on user's behalf, persistent timers/automation |
| 🔵 Info | API key references, broad tool access requests |

## Scoring

- Each unique rule deducts points: critical=30, high=15, medium=5, info=0
- Score 75-100: ✅ PASS
- Score 50-74: ⚠️ WARN
- Score 0-49 or any critical: ❌ FAIL
- Exit code 1 on FAIL (CI-friendly)

## Safe Domain Allowlist

Known legitimate API domains are allowlisted to reduce false positives on network-related rules. Edit the `SAFE_DOMAINS` array in `scripts/scanner.js` to customize.

## Limitations

This is static pattern matching — it catches obvious and moderately obfuscated attacks but cannot detect:
- Sophisticated multi-step social engineering
- Runtime-generated URLs or dynamic exfiltration
- Attacks that look identical to legitimate skill behavior

It's a first line of defense, not a guarantee. Always review skills manually before granting sensitive access.
