---
name: skill-factory
description: "Multi-Agent Pipeline Orchestrator that builds new skills from scratch. Use when: (1) You have a skill idea and want to take it from concept to market-ready package, (2) You need a structured 7-stage process: market research → planning → architecture → building → auditing → documentation → pricing, (3) You want each stage run as an isolated, sequential agent call with no nested sessions. Trigger on: 'create a new skill', 'build a skill', 'skill factory', 'new skill pipeline'."
---

# Skill Factory

A 7-stage multi-agent pipeline that takes a raw skill idea and produces a complete, market-ready skill package. Each stage is an isolated CLI agent call — no nested sessions, no parallelism.

## Overview

```
idea → market → planner → arch → builder → auditor → docs → pricer → done
```

All state is written to disk between stages. Any stage can be re-run independently.

## Workflow

### Step 1: Initialize a skill idea

```bash
python3 {baseDir}/scripts/init_pipeline.py "My Skill Idea" --workspace /tmp/sf-my-skill
```

This creates a workspace directory with `idea.md` pre-filled. Review and edit `idea.md` before running the pipeline.

### Step 2: Run the full pipeline

```bash
bash {baseDir}/scripts/pipeline.sh --workspace /tmp/sf-my-skill
```

The pipeline runs all 7 agents sequentially. Each agent reads previous outputs and writes its own report into the workspace.

### Step 3: Collect outputs

After the pipeline completes, the workspace contains:

```
workspace/
├── idea.md          # Your original idea (input)
├── market.md        # Market research report
├── plan.md          # Product plan with requirements
├── arch.md          # Architecture and file structure
├── skill/           # The built skill (SKILL.md + scripts/ + references/)
├── audit.md         # Quality audit report
├── docs_review.md   # Documentation review
└── pricing.md       # Pricing and positioning
```

### Step 4: Review gates

Each stage has a gate. If a gate fails, the pipeline stops with a non-zero exit code and reports which stage failed. Fix the issue and re-run from that stage:

```bash
bash {baseDir}/scripts/pipeline.sh --workspace /tmp/sf-my-skill --from auditor
```

## Stages at a glance

| Stage    | Agent ID   | Input              | Output         |
|----------|------------|--------------------|----------------|
| market   | market     | idea.md            | market.md      |
| planner  | planner    | idea.md, market.md | plan.md        |
| arch     | arch       | plan.md            | arch.md        |
| builder  | builder    | arch.md, plan.md   | skill/         |
| auditor  | auditor    | skill/             | audit.md       |
| docs     | docs       | skill/, audit.md   | docs_review.md |
| pricer   | pricer     | all outputs        | pricing.md     |

Read [references/agents.md](references/agents.md) for full agent descriptions, models, and prompt guidance.

Read [references/pipeline.md](references/pipeline.md) for detailed gate definitions, failure modes, and re-run strategies.

## Key Constraints

- **No nested sessions** — every agent runs as a top-level isolated CLI call
- **No parallelism** — stages run strictly sequentially; each depends on the previous
- **File-based state** — all inter-stage communication goes through the workspace filesystem
- **Idempotent stages** — re-running a stage overwrites its output without affecting others

## When NOT to Use This Skill

- You only need a quick, simple skill with no research phase — use `init_skill.py` directly
- You are iterating on an existing skill — edit files directly
- You want parallel research across multiple skill ideas — run multiple pipeline instances in separate workspaces
