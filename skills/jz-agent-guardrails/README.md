# Agent Guardrails 🛡️

[🇨🇳 中文文档](./references/SKILL_CN.md)

[![Claude Code Skill](https://img.shields.io/badge/Claude_Code-Skill-8A2BE2)](https://github.com/topics/claude-code-skill)
[![Clawdbot Skill](https://img.shields.io/badge/Clawdbot-Skill-blue)](https://clawdhub.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Version](https://img.shields.io/badge/version-1.1.0-green.svg)](./VERSION)

📖 **Featured in:** [I audited my own AI agent system and found it full of holes](https://x.com/xxx111god/status/2019455237048709336) — the security audit that spawned this 5-tool security suite. ⭐ **`audit-skills.sh`** is the comprehensive audit script at the heart of the article.

## Your AI agent secretly bypasses your rules. This skill enforces them with code.

**Works with:** Claude Code | Clawdbot | Cursor | Any AI coding agent

> Rules in markdown are suggestions. Code hooks are laws.

🚨 **Stop production incidents before they happen** — Born from real crashes, token leaks, and silent bypasses

## The Problem

You spend hours building validation pipelines, scoring systems, and verification logic. Then your AI agent writes a "quick version" that bypasses all of it. Sound familiar?

### Real Production Incidents (February 2026)

**🔥 Server Crash:** Bad config edit → service crash loop → server down all night  
**🔑 Token Leak:** Notion token hardcoded in code, nearly pushed to public GitHub  
**🔄 Code Rewrite:** Agent rewrote validated scoring logic instead of importing it, sent unverified predictions  
**🚀 Deployment Gap:** Built new features but forgot to wire them into production, users got incomplete output  

This isn't a prompting problem — it's an enforcement problem. More markdown rules won't fix it. You need mechanical enforcement that **actually works**.

## Enforcement Hierarchy

| Level | Method | Reliability |
|-------|--------|-------------|
| 1 | **Code hooks** (pre-commit, creation guards) | 100% |
| 2 | **Architectural constraints** (import registries) | 95% |
| 3 | **Self-verification loops** | 80% |
| 4 | **Prompt rules** (AGENTS.md) | 60-70% |
| 5 | **Markdown documentation** | 40-50% ⚠️ |

This toolkit focuses on levels 1-2: the ones that actually work.

## What's Included

| Tool | Purpose |
|------|---------|
| `scripts/install.sh` | One-command project setup |
| `scripts/pre-create-check.sh` | Lists existing modules before you create new files |
| `scripts/post-create-validate.sh` | Detects duplicate functions and missing imports |
| `scripts/check-secrets.sh` | Scans for hardcoded tokens/keys/passwords |
| `assets/pre-commit-hook` | Git hook that blocks bypass patterns + secrets |
| `assets/registry-template.py` | Template `__init__.py` for import enforcement |
| `references/agents-md-template.md` | Battle-tested AGENTS.md template |
| `scripts/audit-skills.sh` | ⭐ Comprehensive security audit — scans all skills for gaps |
| `references/enforcement-research.md` | Full research on why code > prompts |

## Quick Start

**For Claude Code:**
```bash
git clone https://github.com/jzOcb/agent-guardrails ~/.claude/skills/agent-guardrails
cd your-project && bash ~/.claude/skills/agent-guardrails/scripts/install.sh .
```

**For Clawdbot:**
```bash
clawdhub install agent-guardrails
```

**Manual:**
```bash
bash /path/to/agent-guardrails/scripts/install.sh /path/to/your/project
```

📖 [Claude Code detailed guide](./CLAUDE_CODE_INSTALL.md)

This will:
- ✅ Install git pre-commit hook (blocks bypass patterns + hardcoded secrets)
- ✅ Create `__init__.py` registry template  
- ✅ Copy check scripts to your project
- ✅ Add enforcement rules to your AGENTS.md

## Usage

### Before creating any new file:
```bash
bash scripts/pre-create-check.sh /path/to/project
```
Shows existing modules and functions. If it already exists, **import it**.

### After creating/editing a file:
```bash
bash scripts/post-create-validate.sh /path/to/new_file.py
```
Catches duplicate functions, missing imports, and bypass patterns like "simplified version" or "temporary".

### Secret scanning:
```bash
bash scripts/check-secrets.sh /path/to/project
```

## How It Works

### Pre-commit Hook
Automatically blocks commits containing:
- Bypass patterns: `"simplified version"`, `"quick version"`, `"temporary"`, `"TODO: integrate"`
- Hardcoded secrets: API keys, tokens, passwords in source code

### Pre-create Check
Before writing new code, the script shows you:
- All existing Python modules in the project
- All public functions (`def` declarations)
- The project's `__init__.py` registry (if it exists)
- SKILL.md contents (if it exists)

This makes it **structurally difficult** to "not notice" existing code.

### Post-create Validation
After writing code, the script checks:
- Are there duplicate function names across files?
- Does the new file import from established modules?
- Does it contain bypass patterns?

### Import Registry
Each project gets an `__init__.py` that explicitly lists validated functions:

```python
# This is the ONLY approved interface for this project
from .core import validate_data, score_item, generate_report

# New scripts MUST import from here, not reimplement
```

## Origin Story

Born from a real incident (2026-02-02): We built a complete decision engine for prediction market analysis — scoring system, rules parser, news verification, data source validation. Then the AI agent created a "quick scan" script that bypassed ALL of it, sending unverified recommendations. Hours of careful work, completely ignored.

The fix wasn't writing more rules. It was writing code that **mechanically prevents** the bypass.

## Research

Based on research from:
- [Anthropic's Claude Code Best Practices](https://code.claude.com/docs/en/best-practices) — *"Unlike CLAUDE.md instructions which are advisory, hooks are deterministic"*
- [Cursor's Scaling Agents](https://cursor.com/blog/scaling-agents) — *"Opus 4.5 tends to stop earlier and take shortcuts"*
- [Guardrails AI Framework](https://www.guardrailsai.com/docs)
- [NVIDIA NeMo Guardrails](https://github.com/NVIDIA-NeMo/Guardrails)

Full research notes in `references/enforcement-research.md`.

## For Clawdbot Users

This is a [Clawdbot](https://clawd.bot) skill. Install via ClawdHub (coming soon):
```bash
clawdhub install agent-guardrails
```

Or clone directly:
```bash
git clone https://github.com/jzOcb/agent-guardrails.git
```

## 中文文档

完整中文文档见 [`references/SKILL_CN.md`](references/SKILL_CN.md)

## 🛡️ Part of the AI Agent Security Suite

| Tool | What It Prevents |
|------|-----------------|
| **[agent-guardrails](https://github.com/jzOcb/agent-guardrails)** | AI rewrites validated code, leaks secrets, bypasses standards |
| **[config-guard](https://github.com/jzOcb/config-guard)** | AI writes malformed config, crashes gateway |
| **[upgrade-guard](https://github.com/jzOcb/upgrade-guard)** | Version upgrades break dependencies, no rollback |
| **[token-guard](https://github.com/jzOcb/token-guard)** | Runaway token costs, budget overruns |
| **[process-guardian](https://github.com/jzOcb/process-guardian)** | Background processes die silently, no auto-recovery |

📖 **Read the full story:** [I audited my own AI agent system and found it full of holes](https://x.com/xxx111god/status/2019455237048709336)

## License

MIT — Use it, share it, make your agents behave.

## 🛡️ Part of the OpenClaw Security Suite

| Guard | Purpose | Protects Against |
|-------|---------|------------------|
| **[agent-guardrails](https://github.com/jzOcb/agent-guardrails)** | Pre-commit hooks + secret detection | Code leaks, unsafe commits |
| **[config-guard](https://github.com/jzOcb/config-guard)** | Config validation + auto-rollback | Gateway crashes from bad config |
| **[upgrade-guard](https://github.com/jzOcb/upgrade-guard)** | Safe upgrades + watchdog | Update failures, cascading breaks |
| **[token-guard](https://github.com/jzOcb/token-guard)** | Usage monitoring + cost alerts | Budget overruns, runaway costs |

📚 **Full writeup:** [4-Layer Defense System for AI Agents](https://x.com/xxx111god/status/2019096285853139083)
