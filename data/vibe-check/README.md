# 🎭 Vibe Check

> Audit code for "vibe coding sins" — patterns that indicate AI-generated code was accepted without proper human review.

![Vibe Score](https://img.shields.io/badge/vibe--score-73%2F100-yellow)

**Vibe Check** scans your Python, TypeScript, and JavaScript code for 8 categories of "vibe coding" sins — the telltale patterns of AI-generated code that was accepted without proper review. It produces a scored report card with specific line-level findings and optional fix suggestions.

## Features

- 🔍 **8 sin categories** — error handling, duplication, dead code, input validation, magic values, test coverage, naming, security
- 📊 **Scored report card** — 0-100 score with letter grades (A-F)
- 📁 **Flexible input** — single file, directory (recursive), or git diff
- 🔧 **Fix mode** — generates unified diff patches for each finding
- 🏷️ **README badge** — copy-pasteable shields.io badge for your repo
- 🤖 **LLM-powered** — uses Claude or GPT for deep analysis, with heuristic fallback
- 💬 **Discord v2-ready delivery** — compact first response + quick follow-up actions for OpenClaw Discord channels

## Quick Start

```bash
# Install from ClawHub
clawhub install vibe-check

# Analyze a directory
./scripts/vibe-check.sh src/

# Analyze a single file
./scripts/vibe-check.sh app.py

# Check your last 3 commits
./scripts/vibe-check.sh --diff HEAD~3

# With fix suggestions
./scripts/vibe-check.sh --fix src/

# Save report to file
./scripts/vibe-check.sh --fix --output report.md src/
```

## OpenClaw Discord v2 Ready

Tested against OpenClaw Discord channel capabilities documented for v2026.2.14+:
- Sends a compact first response (score + top findings), then expands on demand
- Avoids dumping full wide tables into the first Discord message
- Supports component-style follow-ups when available (`Show Top Findings`, `Show Fix Suggestions`, `Run Diff Mode`)

## Requirements

- **bash** (4.0+)
- **python3** (stdlib only — no pip installs)
- **curl** (for LLM API calls)
- **ANTHROPIC_API_KEY** or **OPENAI_API_KEY** environment variable (recommended; falls back to heuristic analysis)

## Security

- **Read-only by default.** The skill reads source files and generates a report. It never auto-applies code changes.
- **Fixes are suggestions only.** `--fix` outputs unified diffs for human review.
- **LLM usage is explicit.** If an API key is configured, file content may be sent to that provider for analysis.
- See **[SECURITY.md](SECURITY.md)** for the full security model and abuse-case mitigations.

## Testing

- Run syntax checks and smoke tests before publishing.
- Full test plan: **[TESTING.md](TESTING.md)**.

## Sin Categories

| # | Category | Weight | Description |
|:-:|----------|:------:|-------------|
| 1 | 🛡️ Error Handling | 20% | Missing try/catch, bare exceptions, no edge cases |
| 2 | 📋 Duplication | 15% | Copy-pasted logic, DRY violations |
| 3 | 💀 Dead Code | 10% | Unused imports, commented-out blocks, unreachable code |
| 4 | 🔍 Input Validation | 15% | No type checks, no bounds checks, trusting all input |
| 5 | 🔮 Magic Values | 10% | Hardcoded numbers/strings/URLs without named constants |
| 6 | 🧪 Test Coverage | 10% | No test files, no assertions, no test patterns |
| 7 | 📛 Naming Quality | 10% | Vague names (data, result, temp, x), misleading names |
| 8 | 🔒 Security | 10% | eval(), exec(), hardcoded secrets, SQL injection |

## Scoring

| Grade | Range | Meaning |
|:-----:|:-----:|---------|
| A | 90-100 | Pristine code. Ship it! 🚀 |
| B | 80-89 | Clean code with minor issues |
| C | 70-79 | Decent but some lazy patterns |
| D | 60-69 | Needs human attention |
| F | <60 | Heavy vibe coding detected 🚨 |

## Example Output

```
# 🎭 Vibe Check Report

**Project:** `src/`
**Score:** 42/100 (Grade: F)
**Files analyzed:** 5
**Total lines:** 847
**Verdict:** Heavy vibe coding detected. This codebase needs serious human review. 🚨

![Vibe Score](https://img.shields.io/badge/vibe--score-42%2F100-red)

## 📊 Score Breakdown

| Category | Score | Weight | Issues |
|----------|:-----:|:------:|:------:|
| 🛡️ Error Handling | 25 | 20% | 8 |
| 📋 Duplication | 50 | 15% | 4 |
| 💀 Dead Code | 65 | 10% | 3 |
| 🔍 Input Validation | 20 | 15% | 7 |
| 🔮 Magic Values | 45 | 10% | 5 |
| 🧪 Test Coverage | 0 | 10% | 0 test files |
| 📛 Naming Quality | 55 | 10% | 3 |
| 🔒 Security | 30 | 10% | 4 |

## 📈 Category Bars

\`\`\`
Error Handling       █████░░░░░░░░░░░░░░░  25/100
Duplication          ██████████░░░░░░░░░░  50/100
Dead Code            █████████████░░░░░░░  65/100
Input Validation     ████░░░░░░░░░░░░░░░░  20/100
Magic Values         █████████░░░░░░░░░░░  45/100
Test Coverage        ░░░░░░░░░░░░░░░░░░░░   0/100
Naming Quality       ███████████░░░░░░░░░  55/100
Security             ██████░░░░░░░░░░░░░░  30/100
\`\`\`

## 🔍 Top Findings

### 🔴 Critical
1. **api/handler.py:42** — `eval(user_input)` — Remote code execution vulnerability
2. **utils/db.py:88** — `f"SELECT * FROM users WHERE id={user_id}"` — SQL injection via f-string
3. **auth/login.py:15** — `password = "admin123"` — Hardcoded credential

### 🟡 Warning
4. **api/handler.py:15-67** — Entire function has no error handling (53 lines)
5. **utils/helpers.py:23** — `data = process(x)` — Vague variable names throughout
6. **api/handler.py:90** — `# result = old_function(data)` — Commented-out code block

### 🔵 Info
7. **utils/helpers.py:1** — `import os, sys, json, re` — Unused imports: os, re
8. **api/handler.py:30** — `timeout = 30` — Magic number without named constant

## 📁 Per-File Breakdown

| File | Score | Grade | Lines | Top Issue |
|------|:-----:|:-----:|------:|-----------|
| `api/handler.py` | 22 | F | 203 | eval() with user input — RCE vuln... |
| `utils/db.py` | 35 | F | 156 | SQL string concatenation with f-stri... |
| `auth/login.py` | 45 | F | 89 | Hardcoded credentials found... |
| `utils/helpers.py` | 62 | D | 234 | Vague variable names throughout... |
| `models/user.py` | 78 | C | 165 | Missing input validation on email... |

## 🔧 Suggested Fixes

### Fix #1: api/handler.py:42
> Use of eval() — potential code injection vulnerability

\`\`\`diff
--- a/api/handler.py
+++ b/api/handler.py
@@ -41,2 +41,3 @@
-    result = eval(user_input)
+    import ast
+    result = ast.literal_eval(user_input)
\`\`\`

### Fix #2: utils/db.py:88
> SQL injection via f-string concatenation

\`\`\`diff
--- a/utils/db.py
+++ b/utils/db.py
@@ -87,2 +87,2 @@
-    query = f"SELECT * FROM users WHERE id={user_id}"
+    query = "SELECT * FROM users WHERE id=%s"
-    cursor.execute(query)
+    cursor.execute(query, (user_id,))
\`\`\`

---

*🎭 Vibe Check v0.1.1 — 34 findings across 5 files*
*Badge for your README:* `![Vibe Score](https://img.shields.io/badge/vibe--score-42%2F100-red)`
```

## Badge for Your README

After running a vibe check, copy the badge Markdown into your README:

```markdown
![Vibe Score](https://img.shields.io/badge/vibe--score-73%2F100-yellow)
```

Color mapping:
- 🟢 **brightgreen** — A (90-100)
- 🟢 **green** — B (80-89)
- 🟡 **yellow** — C (70-79)
- 🟠 **orange** — D (60-69)
- 🔴 **red** — F (<60)

## How It Works

1. **File Discovery** — Finds all `.py`, `.ts`, `.tsx`, `.js`, `.jsx` files (skips `node_modules`, `dist`, `__pycache__`, etc.)
2. **LLM Analysis** — Sends each file to an LLM with a structured audit prompt targeting the 8 sin categories
3. **Scoring** — Each file gets a 0-100 score per category; overall score is a weighted average across files (weighted by line count)
4. **Report** — Generates a Markdown scorecard with tables, bar charts, findings, and optional fix patches

### Without an LLM API Key

The tool falls back to heuristic analysis using regex patterns and code structure checks. It's less accurate but still catches common issues like:
- Missing try/catch blocks
- `eval()` / `exec()` usage
- Magic numbers
- Vague variable names
- Commented-out code blocks
- Missing test patterns

## Supported Languages (v1)

- **Python** (`.py`)
- **TypeScript** (`.ts`, `.tsx`)
- **JavaScript** (`.js`, `.jsx`, `.mjs`, `.cjs`)

## Environment Variables

| Variable | Description |
|----------|-------------|
| `ANTHROPIC_API_KEY` | Anthropic API key for Claude (recommended) |
| `OPENAI_API_KEY` | OpenAI API key for GPT-4o |
| `VIBE_CHECK_BATCH_SIZE` | Files per LLM batch (default: 3) |

## More from Anvil AI

This skill is part of the **Anvil AI** open-source skill suite.

| Skill | What it does |
|-------|-------------|
| **[vibe-check](https://clawhub.com/skills/vibe-check)** | This skill — AI code quality + security review scorecard. |
| **[rug-checker](https://clawhub.com/skills/rug-checker)** | Solana token rug-pull risk analysis. |
| **[dep-audit](https://clawhub.com/skills/dep-audit)** | Dependency vulnerability auditing across npm/pip/cargo/go. |
| **[prom-query](https://clawhub.com/skills/prom-query)** | Prometheus metrics + alert triage from natural language. |


## License

MIT

---

Built by **[Anvil AI](https://anvil-ai.io)**.

