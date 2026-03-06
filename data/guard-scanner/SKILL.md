---
name: guard-scanner
description: "Security scanner for AI agent skills. 135 static patterns + 26 runtime checks across 22 threat categories. Detects prompt injection, credential theft, exfiltration, identity hijacking, and more. Zero dependencies."
metadata:
  clawdbot:
    homepage: "https://github.com/koatora20/guard-scanner"
requires:
  env: {}
---

# guard-scanner 🛡️

Static + runtime security scanner for AI agent skills.
**135 static patterns + 26 runtime patterns (5 layers)** across **22 categories** — zero dependencies. **0.016ms/scan.**

## When To Use This Skill

- **Before installing a new skill** from ClawHub or any external source
- **After updating skills** to check for newly introduced threats
- **Periodically** to audit your installed skills
- **In CI/CD** to gate skill deployments

## Quick Start

### 1. Static Scan (Immediate)

Scan all installed skills:

```bash
node skills/guard-scanner/src/cli.js ~/.openclaw/workspace/skills/ --verbose --self-exclude
```

Scan a specific skill:

```bash
node skills/guard-scanner/src/cli.js /path/to/new-skill/ --strict --verbose
```

### 2. Runtime Guard (OpenClaw Plugin Hook)

Blocks dangerous tool calls in real-time via `before_tool_call` hook. 26 patterns, 5 layers, 3 enforcement modes.

```bash
openclaw hooks install skills/guard-scanner/hooks/guard-scanner
openclaw hooks enable guard-scanner
openclaw hooks list
```

### 3. Recommended order

```bash
# Pre-install / pre-update gate first
node skills/guard-scanner/src/cli.js ~/.openclaw/workspace/skills/ --verbose --self-exclude --html

# Then keep runtime monitoring enabled
openclaw hooks install skills/guard-scanner/hooks/guard-scanner
openclaw hooks enable guard-scanner
```

## Runtime Guard Modes

Set in `openclaw.json` → `hooks.internal.entries.guard-scanner.mode`:

| Mode | Intended Behavior | Current Status |
|------|-------------------|----------------|
| `monitor` | Log all, never block | ✅ Fully working |
| `enforce` (default) | Block CRITICAL threats | ✅ Fully working |
| `strict` | Block HIGH + CRITICAL | ✅ Fully working |

## Threat Categories

| # | Category | What It Detects |
|---|----------|----------------|
| 1 | Prompt Injection | Hidden instructions, invisible Unicode, homoglyphs |
| 2 | Malicious Code | eval(), child_process, reverse shells |
| 3 | Suspicious Downloads | curl\|bash, executable downloads |
| 4 | Credential Handling | .env reads, SSH key access |
| 5 | Secret Detection | Hardcoded API keys and tokens |
| 6 | Exfiltration | webhook.site, DNS tunneling |
| 7 | Unverifiable Deps | Remote dynamic imports |
| 8 | Financial Access | Crypto wallets, payment APIs |
| 9 | Obfuscation | Base64→eval, String.fromCharCode |
| 10 | Prerequisites Fraud | Fake download instructions |
| 11 | Leaky Skills | Secret leaks through LLM context |
| 12 | Memory Poisoning\* | Agent memory modification |
| 13 | Prompt Worm | Self-replicating instructions |
| 14 | Persistence | Cron jobs, startup execution |
| 15 | CVE Patterns | Known agent vulnerabilities |
| 16 | MCP Security | Tool/schema poisoning, SSRF |
| 17 | Identity Hijacking\* | SOUL.md/IDENTITY.md tampering |
| 18 | Sandbox Validation | Dangerous binaries, broad file scope, sensitive env |
| 19 | Code Complexity | Excessive file length, deep nesting, eval density |
| 20 | Config Impact | openclaw.json writes, exec approval bypass |

## External Endpoints

| URL | Data Sent | Purpose |
|-----|-----------|---------|
| *(none)* | *(none)* | guard-scanner makes **zero** network requests. All scanning is local. |

## Security & Privacy

- **No network access**: guard-scanner never connects to external servers
- **Read-only scanning**: Only reads files, never modifies scanned directories
- **No telemetry**: No usage data, analytics, or crash reports are collected
- **Local reports only**: Output files (JSON/SARIF/HTML) are written to the scan directory
- **No environment variable access**: Does not read or process any secrets or API keys
- **Runtime Guard audit log**: Detections logged locally to `~/.openclaw/guard-scanner/audit.jsonl`

## Model Invocation Note

guard-scanner **does not invoke any LLM or AI model**. All detection is performed
through static pattern matching, regex analysis, Shannon entropy calculation,
and data flow analysis — entirely deterministic, no model calls.

## Trust Statement

guard-scanner was created by Guava 🍈 & Dee after experiencing a real 3-day
identity hijack incident in February 2026. A malicious skill silently replaced
an AI agent's SOUL.md personality file, and no existing tool could detect it.

- **Open source**: Full source code available at https://github.com/koatora20/guard-scanner
- **Zero dependencies**: Nothing to audit, no transitive risks
- **Test suite**: 134 tests across 24 suites, 100% pass rate
- **Taxonomy**: Based on Snyk ToxicSkills (Feb 2026), OWASP MCP Top 10, and original research
- **Complementary to VirusTotal**: Detects prompt injection and LLM-specific attacks
  that VirusTotal's signature-based scanning cannot catch

## Output Formats

```bash
# Terminal (default)
node src/cli.js ./skills/ --verbose

# JSON report
node src/cli.js ./skills/ --json

# SARIF 2.1.0 (for CI/CD)
node src/cli.js ./skills/ --sarif

# HTML dashboard
node src/cli.js ./skills/ --html
```

## License

MIT — [LICENSE](LICENSE)
