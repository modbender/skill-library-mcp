# Skill Cortex

**A self-evolving capability manager for [OpenClaw](https://github.com/openclaw) agents.**

Skill Cortex gives your agent the ability to autonomously find, install, use, and discard Skills from [ClawHub](https://clawhub.ai) — and learn from every interaction. The more you use it, the faster it gets.

## The Problem

OpenClaw loads every installed Skill into the system prompt. More Skills = more tokens burned per conversation, even when most are irrelevant to the current task. But uninstalling them means losing capability.

## The Solution

Skill Cortex introduces a **cached Skill layer** — a dynamic, temporary workspace that sits on top of your permanent Skills:

```
┌─────────────────────────────────────────────┐
│  User Task                                  │
├─────────────────────────────────────────────┤
│  Skill Cortex (this Skill)                  │
│  ┌────────────────────────────────────────┐ │
│  │ Sensory   → recognize task type        │ │
│  │ Motor     → route to best Skill        │ │
│  │ Prefrontal→ apply past experience      │ │
│  └────────────────────────────────────────┘ │
├─────────────────────────────────────────────┤
│  Cached Skills  (on-demand, auto-cleanup)   │
├─────────────────────────────────────────────┤
│  Long-term Skills  (user-installed, native) │
└─────────────────────────────────────────────┘
```

## How It Works

**Phase 1 — Perception:** Check local memory first. If the cortex has seen this type of task before, it routes directly to the best known Skill. Otherwise, search ClawHub.

**Phase 2 — Validation:** Present candidates to the user with safety info (stars, downloads, VirusTotal scan, source). Nothing installs without explicit approval.

**Phase 3 — Execution:** Install the Skill, generate an execution plan with side-effect warnings, execute the task. On failure, auto-recover or switch to the next candidate (max 2 switches).

**Phase 4 — Learning:** Update the cortex memory. Successful Skills gain weight; failed ones decay based on failure type. High-frequency read-only Skills can be promoted to **reflex mode** (near-instant invocation). Skills used often enough get recommended for permanent installation.

## Key Features

- **Use-and-release**: cached Skills are uninstalled after each task by default
- **Cortical learning**: every invocation strengthens or weakens routing pathways
- **Reflex arcs**: frequently successful read-only Skills skip the confirmation flow
- **Entity filtering**: signal words are stripped of personal data before storage
- **Synaptic pruning**: stale routes and low-confidence lessons are automatically cleaned up
- **Failure recovery**: auto-retry, candidate switching, and structured error reporting
- **Safety-first**: write operations never enter reflex; all installs require user consent

## Installation

```bash
# Copy into your OpenClaw skills directory
cp -r skill-cortex ~/.openclaw/skills/skill-cortex

# Or install from ClawHub (once published)
clawhub install skill-cortex
```

Requires `clawhub` CLI to be installed and available on PATH.

## File Structure

```
skill-cortex/
├── SKILL.md          # Core instructions (read by Agent every trigger, ~1700 tokens)
├── docs/
│   └── DESIGN.md     # Full schema, algorithms, design decisions (reference only)
└── README.md         # You are here
```

Runtime data is stored at `~/.openclaw/skill-cortex/cortex.json` (auto-created on first use).

## Cortex Architecture

The cortex file mirrors the structure of the biological cerebral cortex:

| Region | Role | Analogy |
|---|---|---|
| **Sensory** | Maps signal words to task regions | Pattern recognition |
| **Motor** | Routes task regions to ranked Skill candidates | Muscle memory |
| **Prefrontal** | Stores structured cross-task lessons | Strategic reasoning |

Weight updates use **frequency-sensitive reinforcement** (diminishing returns within 7-day windows) and **typed decay** (failure penalty scales with cause — a missing dependency barely hurts; a task mismatch is devastating).

## Safety

- All installations require user confirmation, even in reflex mode
- System dependency installs require separate explicit approval
- Write operations are **permanently excluded** from reflex promotion
- Reflex locks the Skill version — any version change triggers automatic demotion
- Entity filtering strips personal data from stored signal words
- Cortex file uses read-merge-write to prevent data loss

## Contributing

This is an early-stage project. Feedback, issues, and PRs are welcome.

## License

MIT
