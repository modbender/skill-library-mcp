---
name: openclaw-architect
description: "Design, configure, debug, and optimize OpenClaw AI agent deployments. Master guide for gateway configuration, openclaw.json settings, model routing and fallback chains, skills development and publishing, cron job scheduling, memory systems (Qdrant, Neo4j, SQLite), Docker infrastructure, and Tailscale VPN networking. Includes config analyzer that audits your openclaw.json and suggests improvements, plus health checker that validates all OpenClaw subsystems. Built for AI agents — Python stdlib only, no dependencies. Use for OpenClaw setup, gateway debugging, skill building, cron management, model optimization, cost reduction, and infrastructure troubleshooting."
homepage: https://www.agxntsix.ai
license: MIT
compatibility: Python 3.10+ (stdlib only — no dependencies)
metadata: {"openclaw": {"emoji": "🏗️", "requires": {"env": ["OPENCLAW_WORKSPACE"]}, "primaryEnv": "OPENCLAW_WORKSPACE", "homepage": "https://www.agxntsix.ai"}}
---

# 🏗️ OpenClaw Architect

The definitive skill for understanding, configuring, debugging, and optimizing OpenClaw deployments. Built from real production experience.

## Features

- **Analyze configurations** — audit openclaw.json and suggest improvements
- **Health check systems** — validate all OpenClaw subsystems in one command
- **Configure model routing** — set up primary models, fallback chains, cost tiers
- **Build skills** — SKILL.md format, CLI design, publishing to ClawHub
- **Debug gateway issues** — troubleshoot errors, cron failures, session crashes
- **Optimize performance** — model selection, cost reduction, context management
- **Manage cron jobs** — scheduling, error handling, retry patterns
- **Configure memory systems** — Qdrant, Neo4j, SQLite integration
- **Deploy infrastructure** — Docker, Tailscale VPN, networking
- **Post-update verification** — checklist for safe OpenClaw upgrades

## Requirements

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENCLAW_WORKSPACE` | ✅ | Path to OpenClaw workspace directory |

## Quick Start

```bash
PY=~/.openclaw/workspace/.venv/bin/python3

# Analyze your openclaw.json configuration
$PY skills/openclaw-architect/scripts/config_analyzer.py

# Health check all OpenClaw systems
$PY skills/openclaw-architect/scripts/health_check.py
```

## Commands

### Config Analyzer
```bash
# Audit current configuration
$PY skills/openclaw-architect/scripts/config_analyzer.py

# Analyze a specific config file
$PY skills/openclaw-architect/scripts/config_analyzer.py --config /path/to/openclaw.json
```

### Health Check
```bash
# Check all subsystems
$PY skills/openclaw-architect/scripts/health_check.py

# Check specific subsystem
$PY skills/openclaw-architect/scripts/health_check.py --check gateway
$PY skills/openclaw-architect/scripts/health_check.py --check cron
$PY skills/openclaw-architect/scripts/health_check.py --check memory
```

## References

| File | Description |
|------|-------------|
| `references/architecture-overview.md` | How OpenClaw works end-to-end |
| `references/config-reference.md` | All openclaw.json options documented |
| `references/skills-guide.md` | Building and publishing skills |
| `references/cron-guide.md` | Cron job scheduling and patterns |
| `references/memory-guide.md` | Memory system configuration |
| `references/troubleshooting.md` | Common fixes and debugging |
| `references/optimization-tips.md` | Performance tuning guide |

## Architecture Principles

1. **Brain-First** — Strategic content → Mem0/Qdrant/Neo4j/SQLite. Markdown = operational logs only.
2. **Fault-Tolerant** — Always configure 2+ fallback models. Test each one works.
3. **Credit-Aware** — Monitor usage, auto-switch tiers, alert before exhaustion.
4. **Skills = Publishing** — Every reusable pattern becomes a ClawHub skill.
5. **Self-Monitoring** — System watches its own health, uptime, costs via cron.
6. **Automate Repetition** — If it happens twice → cron job or script.

## Script Reference

| Script | Description |
|--------|-------------|
| `{baseDir}/scripts/config_analyzer.py` | Audits openclaw.json configuration |
| `{baseDir}/scripts/health_check.py` | Validates all OpenClaw subsystems |

## Output Format

All commands output structured text with clear pass/fail indicators and actionable recommendations.

## Data Policy

This skill reads local configuration files only. No data is sent to external services.

---

Built by [M. Abidi](https://www.agxntsix.ai)

[LinkedIn](https://www.linkedin.com/in/mohammad-ali-abidi) · [YouTube](https://youtube.com/@aiwithabidi) · [GitHub](https://github.com/aiwithabidi) · [Book a Call](https://cal.com/agxntsix/abidi-openclaw)
