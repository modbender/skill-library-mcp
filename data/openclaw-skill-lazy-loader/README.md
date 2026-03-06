# OpenClaw Skill Lazy Loader

> Stop loading every skill file at session start. Cut context loading costs by 40–93%.

[![ClawHub](https://img.shields.io/badge/ClawHub-Asif2BD%2Fopenclaw--skill--lazy--loader-green)](https://clawhub.ai/Asif2BD/openclaw-skill-lazy-loader)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0-brightgreen)](CHANGELOG.md)

## What It Does

Most OpenClaw agents eagerly load all their skill files at session start — burning thousands of tokens on context that may never be used. This skill teaches you (and your agents) how to fix that.

**The pattern:** Use a lightweight SKILLS catalog (~300 tokens) at startup. Load individual skill files only when a task actually needs them.

**Result:** 40–93% reduction in context loading costs, depending on your skill library size.

## Install

```bash
clawhub install openclaw-skill-lazy-loader
```

## Quick Start

```bash
# 1. Copy the SKILLS catalog template to your agent workspace
cp ~/.openclaw/skills/openclaw-skill-lazy-loader/SKILLS.md.template ~/my-agent/SKILLS.md

# 2. Edit it — fill in your actual skills
nano ~/my-agent/SKILLS.md

# 3. Update your AGENTS.md to use the lazy loading pattern
# (copy the relevant section from AGENTS.md.template)

# 4. Test the optimizer
python3 ~/.openclaw/skills/openclaw-skill-lazy-loader/context_optimizer.py recommend "your task"
```

## Token Savings

| Skills in library | Before | After | Savings |
|-------------------|--------|-------|---------|
| 5 skills | ~3,000 tok | ~600 tok | **80%** |
| 10 skills | ~6,500 tok | ~750 tok | **88%** |
| 20 skills | ~13,000 tok | ~900 tok | **93%** |

## What's Included

- **`SKILL.md`** — Full implementation guide
- **`SKILLS.md.template`** — Ready-to-use skill catalog starter
- **`AGENTS.md.template`** — AGENTS.md lazy loading section to paste in
- **`context_optimizer.py`** — CLI tool: recommends which skills to load per task

## Pairs With

→ [OpenClaw Token Optimizer](https://clawhub.ai/Asif2BD/openclaw-token-optimizer) — handles model routing and runtime costs. Together they cover the entire token lifecycle.

## Author

**M Asif Rahman** ([@Asif2BD](https://github.com/Asif2BD)) — Matrix Zion AI team  
Apache 2.0 · [GitHub](https://github.com/Asif2BD/openclaw-skill-lazy-loader) · [ClawHub](https://clawhub.ai/Asif2BD/openclaw-skill-lazy-loader)
