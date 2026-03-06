---
name: openclaw-skill-lazy-loader
description: Dramatically reduce per-session token usage by loading skills and context files only when needed — not at session start. Includes the SKILLS catalog pattern, AGENTS.md lazy loading strategy, and a Python helper that recommends exactly which files to load for any given task. Compatible with all OpenClaw agents. Works alongside Token Optimizer.
version: 1.0.0
homepage: https://github.com/Asif2BD/openclaw-skill-lazy-loader
source: https://github.com/Asif2BD/openclaw-skill-lazy-loader
author: Asif2BD
license: Apache 2.0
security:
  verified: true
  auditor: Oracle (Matrix Zion)
  audit_date: 2026-02-28
  scripts_no_network: true
  scripts_no_code_execution: true
  scripts_no_subprocess: true
  scripts_data_local_only: true
---

# OpenClaw Skill Lazy Loader

Stop loading every skill file at session start. Load what you need, when you need it — and cut your token usage by 40–70%.

## The Problem

Most OpenClaw agents load their entire skill library at startup:

```markdown
# AGENTS.md (naive approach)
Read ALL of these before starting:
- skills/python/SKILL.md
- skills/git/SKILL.md
- skills/docker/SKILL.md
- skills/aws/SKILL.md
- skills/browser/SKILL.md
... (20 more)
```

Each session burns **3,000–15,000 tokens** just loading context that may never be used. At scale, this is your biggest cost.

## The Solution: Lazy Loading

Instead of loading skills upfront, agents check a **SKILLS catalog** (a lightweight index) and load individual skill files only when a task requires them.

**Before:** Load 20 skill files = ~12,000 tokens/session
**After:** Load catalog (300 tokens) + 1–2 relevant skills (~800 tokens) = **~1,100 tokens/session**

That's an **89% reduction** on context loading alone.

---

## Implementation Guide

### Step 1: Create Your SKILLS Catalog

Create `SKILLS.md` in your agent workspace — a lightweight index of all available skills:

```markdown
# Available Skills

| Skill | File | Use When |
|-------|------|----------|
| Python | skills/python/SKILL.md | Writing/debugging Python code |
| Git | skills/git/SKILL.md | Git operations, PRs, branches |
| Docker | skills/docker/SKILL.md | Containers, images, compose |
| Browser | skills/browser/SKILL.md | Web scraping, UI automation |
| AWS | skills/aws/SKILL.md | Cloud deployments, S3, Lambda |
```

This catalog is the ONLY file loaded at session start. ~200–400 tokens instead of 10,000+.

See `SKILLS.md.template` for a complete starter template.

### Step 2: Update Your AGENTS.md

Replace bulk loading with the catalog pattern:

```markdown
## Skills

At session start: Read SKILLS.md (the index only).
When a task needs a skill: Read the specific SKILL.md for that skill.
Never load all skills upfront.

### Loading Decision
Before loading any skill file:
1. Does the current task need it? (yes → load it, no → skip)
2. Has it already been loaded this session? (yes → skip, no → load once)
```

See `AGENTS.md.template` for the full recommended AGENTS.md skills section.

### Step 3: Use the Context Optimizer (Optional)

The included `context_optimizer.py` analyzes your task description and recommends which skills to load:

```bash
python3 context_optimizer.py recommend "Write a Python script to push to S3"
# Output:
# Recommended skills to load:
#   - skills/python/SKILL.md  (confidence: high — Python task)
#   - skills/aws/SKILL.md     (confidence: high — S3 mentioned)
#   - skills/git/SKILL.md     (confidence: low  — skip unless pushing to GitHub)
```

### Step 4: Apply to Memory Files Too

The same pattern works for memory and context files:

```markdown
## Memory Loading (AGENTS.md)

At session start: Read MEMORY.md (summary only).
Load daily files (memory/YYYY-MM-DD.md) only when:
- User asks about past work
- Task references a specific date or project
- Debugging requires historical context
```

---

## Token Savings Calculator

| Scenario | Before | After | Savings |
|----------|--------|-------|---------|
| 5 skills loaded | ~3,000 tokens | ~600 tokens | 80% |
| 10 skills loaded | ~6,500 tokens | ~750 tokens | 88% |
| 20 skills loaded | ~13,000 tokens | ~900 tokens | 93% |
| +Memory files (5) | +4,000 tokens | +400 tokens | 90% |

*Estimates based on average SKILL.md size of ~600 tokens. Catalog averages ~150 tokens.*

---

## Integration with Token Optimizer

This skill pairs directly with [OpenClaw Token Optimizer](https://clawhub.ai/Asif2BD/openclaw-token-optimizer). Lazy loading handles **context loading costs**; Token Optimizer handles **model routing, heartbeat budgeting, and runtime costs**. Together they cover the full token lifecycle.

Install both:
```bash
clawhub install openclaw-skill-lazy-loader
clawhub install openclaw-token-optimizer
```

---

## Files in This Skill

| File | Purpose |
|------|---------|
| `SKILL.md` | This guide |
| `SKILLS.md.template` | Starter SKILLS catalog template |
| `AGENTS.md.template` | Lazy loading AGENTS.md section |
| `context_optimizer.py` | CLI helper — recommends skills to load per task |
| `README.md` | ClawHub listing description |
| `SECURITY.md` | Security audit and script disclosure |
| `.clawhubsafe` | File integrity manifest |

---

## Quick Start (5 minutes)

```bash
# 1. Install
clawhub install openclaw-skill-lazy-loader

# 2. Copy templates to your agent workspace
cp ~/.openclaw/skills/openclaw-skill-lazy-loader/SKILLS.md.template ~/my-agent/SKILLS.md
cp ~/.openclaw/skills/openclaw-skill-lazy-loader/AGENTS.md.template ~/my-agent/AGENTS.lazy.md

# 3. Edit SKILLS.md — fill in your actual skills
# 4. Merge AGENTS.lazy.md into your AGENTS.md
# 5. Test with context_optimizer.py
python3 ~/.openclaw/skills/openclaw-skill-lazy-loader/context_optimizer.py recommend "your next task"
```

---

*By M Asif Rahman (@Asif2BD) · Apache 2.0 · https://clawhub.ai/Asif2BD/openclaw-skill-lazy-loader*
