---
name: hefestoai-auditor
version: "2.2.0"
description: "Static code analysis tool. Detects security vulnerabilities, code smells, and complexity issues across 17 languages. All analysis runs locally — no code leaves your machine."
metadata:
  {
    "openclaw":
      {
        "emoji": "🔨",
        "requires": { "bins": ["hefesto"] },
        "install":
          [
            {
              "id": "pip",
              "kind": "pip",
              "package": "hefesto-ai",
              "bins": ["hefesto"],
              "label": "Install HefestoAI (pip)"
            }
          ]
      }
  }
---

# HefestoAI Auditor

Static code analysis for security, quality, and complexity. Supports 17 languages.

**Privacy:** All analysis runs locally. No code is transmitted to external services. No network calls are made during analysis.

**Permissions:** This tool reads source files in the specified directory (read-only). It does not modify your code.

---

## Install

```bash
pip install hefesto-ai
```

## Quick Start

```bash
hefesto analyze /path/to/project --severity HIGH
```

### Severity Levels

```bash
hefesto analyze /path/to/project --severity CRITICAL   # Critical only
hefesto analyze /path/to/project --severity HIGH        # High + Critical
hefesto analyze /path/to/project --severity MEDIUM      # Medium + High + Critical
hefesto analyze /path/to/project --severity LOW         # Everything
```

### Output Formats

```bash
hefesto analyze /path/to/project --output text                          # Terminal (default)
hefesto analyze /path/to/project --output json                          # Structured JSON
hefesto analyze /path/to/project --output html --save-html report.html  # HTML report
hefesto analyze /path/to/project --quiet                                # Summary only
```

### Status and Version

```bash
hefesto status
hefesto --version
```

---

## What It Detects

### Security Vulnerabilities
- SQL injection and command injection
- Hardcoded secrets (API keys, passwords, tokens)
- Insecure configurations (Dockerfiles, Terraform, YAML)
- Path traversal and XSS risks

### Semantic Drift (AI Code Integrity)
- Logic alterations that preserve syntax but change intent
- Architectural degradation from AI-generated code
- Hidden duplicates and inconsistencies in monorepos

### Code Quality
- Cyclomatic complexity >10 (HIGH) or >20 (CRITICAL)
- Deep nesting (>4 levels)
- Long functions (>50 lines)
- Code smells and anti-patterns

### DevOps Issues
- Dockerfile: missing USER, no HEALTHCHECK, running as root
- Shell: missing `set -euo pipefail`, unquoted variables
- Terraform: missing tags, hardcoded values

### What It Does NOT Detect
- Runtime network attacks (DDoS, port scanning)
- Active intrusions (rootkits, privilege escalation)
- Network traffic monitoring
- For these, use SIEM/IDS/IPS or GCP Security Command Center

---

## Supported Languages (17)

**Code:** Python, TypeScript, JavaScript, Java, Go, Rust, C#

**DevOps/Config:** Dockerfile, Jenkins/Groovy, JSON, Makefile, PowerShell, Shell, SQL, Terraform, TOML, YAML

---

## Interpreting Results

```
file.py:42:10
  Issue: Hardcoded database password detected
  Function: connect_db
  Type: HARDCODED_SECRET
  Severity: CRITICAL
  Suggestion: Move credentials to environment variables or a secrets manager
```

### Issue Types

| Type | Severity | Action |
|------|----------|--------|
| `VERY_HIGH_COMPLEXITY` | CRITICAL | Fix immediately |
| `HIGH_COMPLEXITY` | HIGH | Fix in current sprint |
| `DEEP_NESTING` | HIGH | Refactor nesting levels |
| `SQL_INJECTION_RISK` | HIGH | Parameterize queries |
| `HARDCODED_SECRET` | CRITICAL | Remove and rotate |
| `LONG_FUNCTION` | MEDIUM | Split function |

---

## CI/CD Integration

```bash
# Fail build on HIGH or CRITICAL issues
hefesto analyze /path/to/project --fail-on HIGH

# Pre-push git hook
hefesto install-hook

# Limit output
hefesto analyze /path/to/project --max-issues 10

# Exclude specific issue types
hefesto analyze /path/to/project --exclude-types VERY_HIGH_COMPLEXITY,LONG_FUNCTION
```

---

## Licensing

| Tier | Price | Key Features |
|------|-------|-------------|
| **FREE** | $0/mo | Static analysis, 17 languages, pre-push hooks |
| **PRO** | $8/mo | ML semantic analysis, REST API, BigQuery integration, custom rules |
| **OMEGA** | $19/mo | IRIS monitoring, auto-correlation, real-time alerts, team dashboard |

All paid tiers include a **14-day free trial**.

See pricing and subscribe at [hefestoai.narapallc.com](https://hefestoai.narapallc.com).

To activate a license, see the setup guide at [hefestoai.narapallc.com/setup](https://hefestoai.narapallc.com/setup).

---

## About

Created by **Narapa LLC** (Miami, FL) — Arturo Velasquez (@artvepa)

- GitHub: [github.com/artvepa80/Agents-Hefesto](https://github.com/artvepa80/Agents-Hefesto)
- Support: support@narapallc.com
