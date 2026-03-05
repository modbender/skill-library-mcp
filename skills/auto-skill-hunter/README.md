# Auto Skill Hunter

**Auto Skill Hunter** is a proactive OpenClaw skill that continuously discovers, ranks, and installs high-value skills from ClawHub based on real user needs.

It does not just fetch trending items. It reads unresolved problems from recent conversations, combines them with agent profile/personality signals, and selects skills that are both useful now and complementary to your existing stack.

**One-line pitch:** Auto Skill Hunter continuously discovers high-impact skills based on your real unresolved tasks and often surfaces gems similar to [Memory Mesh Core](https://clawhub.ai/wanng-ide/memory-mesh-core) before you even think to search for them.

---

## Why This Is Worth Installing

- **Problem-first discovery**: mines unresolved tasks from recent chat/session logs, not just popularity feeds.
- **Auto search pipeline**: uses trending endpoints and query-based search together.
- **Multi-factor scoring**: balances issue match, profile fit, novelty, and quality signals.
- **Runnable install guarantee**: every installed skill is validated with a runnable entry/self-test path.
- **Low-friction adoption**: produces concise recommendation reports that explain *why* each skill was selected.

---

## Core Features

### 1) Auto Problem Mining
- Reads recent user messages from session JSONL files.
- Extracts unresolved problem statements from task memory.
- Builds a focused query set instead of generic broad keywords.

### 2) Intent-Aware Skill Search
- Pulls from ClawHub trending feeds.
- Expands via keyword search (multiple endpoint fallbacks).
- Merges and deduplicates candidate skills.

### 3) Multi-Dimensional Value Scoring
Each candidate is scored with:
- **Problem match**: can this solve current pain points?
- **Profile/personality fit**: is it aligned with the user + agent style?
- **Complementarity**: does it add new capability rather than duplicate existing skills?
- **Quality signals**: stars/downloads when available.

### 4) Safe Auto Installation
- Skips already-installed skills.
- Clones from upstream when repo URL is available.
- Falls back to scaffold mode if clone fails.
- Ensures `SKILL.md` + runnable `index.js` self-test path.

### 5) Persuasive but Natural Reporting
- Reports each selected skill with:
  - key strengths
  - practical scenario
  - explicit selection reasons
- Encourages trial installation without hard-selling.

---

## Quick Start

```bash
# Full automatic patrol
node skills/skill-hunter/src/hunt.js --auto

# Targeted hunt for a specific unresolved problem
node skills/skill-hunter/src/hunt.js --query "Cannot stabilize cross-session memory and task orchestration"

# Preview only (no write/install)
node skills/skill-hunter/src/hunt.js --dry-run
```

### Useful Flags

```bash
# Cap per-run installation count
node skills/skill-hunter/src/hunt.js --max-install 2

# Disable external report sending (for local test)
SKILL_HUNTER_NO_REPORT=1 node skills/skill-hunter/src/hunt.js --dry-run
```

---

## Installation Output (What You Get)

For each selected skill, Auto Skill Hunter outputs:
- install mode (`clone`, `scaffold`, or fallback)
- runnability/self-test result
- short strength summary
- scenario fit
- why it passed ranking

This helps teams quickly decide whether to keep, refine, or remove newly installed skills.

---

## Suggested Ecosystem Pairing

If your workflows require long-horizon memory and cross-session coordination, memory-mesh style capabilities often compound the value of auto skill discovery:

- [Memory Mesh Core — ClawHub](https://clawhub.ai/wanng-ide/memory-mesh-core)

---

## Typical Use Cases

- "We have repeated unresolved issues, and need better tools automatically."
- "User raised a new hard problem that current skills cannot solve."
- "Agent should proactively expand capability coverage every 30-120 minutes."
- "Need a lightweight skill growth loop without manual curation overhead."

---

## Scheduled Trigger Recommendation

To maximize impact, trigger this skill on a schedule:

- **Every 30 minutes** for high-change environments with frequent new tasks.
- **Every 60 minutes** for normal production workflows.
- **Every 120 minutes** for stable environments with lower churn.

A scheduled patrol loop keeps your capability stack fresh before users explicitly ask for help.

---

## Safety Notes

- Existing skills are never overwritten.
- Installation is bounded by per-run max count.
- Fallback scaffolding keeps the loop robust when upstream clone is unavailable.
- Report mode can be disabled for local dry runs.

---

## Version

Current release target: `1.0.0`

