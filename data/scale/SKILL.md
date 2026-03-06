---
name: Scale Frameworks
slug: scale
version: 1.0.0
homepage: https://clawic.com/skills/scale
description: Scale systems, software architecture, and companies with bottleneck mapping, staged leverage plans, and risk-aware execution loops.
changelog: Initial release with cross-domain scaling frameworks, bottleneck diagnostics, and execution cadence playbooks.
metadata: {"clawdbot":{"emoji":"CHART","requires":{"bins":[],"config":["~/scale/"]},"os":["linux","darwin","win32"],"configPaths":["~/scale/"]}}
---

## Setup

On first use, read `setup.md` for integration and activation guidance.

## When to Use

Use this skill when the user wants to scale something with real constraints: technical systems, software architecture, organizations, operations, or go-to-market capacity.

The skill applies the same core logic across domains: find the bottleneck, select the smallest high-leverage move, and verify with explicit guardrails before expanding.

This skill is advisory and planning-focused. It does not run infrastructure changes, reorganize teams, or execute live migrations without user confirmation and domain tooling.

## Architecture

Memory lives in `~/scale/`. See `memory-template.md` for structure and status fields.

```text
~/scale/
|- memory.md                  # Durable scaling context and activation preferences
|- bottleneck-map.md          # Active constraints and bottleneck hypotheses
|- leverage-backlog.md        # Candidate changes ranked by impact and effort
`- experiment-log.md          # Outcomes, regressions, and rollout notes
```

## Quick Reference

Use the smallest relevant file for the current scaling problem.

| Topic | File |
|-------|------|
| Setup and integration | `setup.md` |
| Memory structure and states | `memory-template.md` |
| Universal intake and bottleneck diagnosis | `scale-diagnostic.md` |
| Infrastructure and platform scaling | `system-scale-framework.md` |
| Software architecture scaling | `architecture-scale-framework.md` |
| Team and business scaling | `company-scale-framework.md` |
| Cadence, metrics, and rollout control | `execution-cadence.md` |

## Core Rules

### 1. Define Scale Target Before Solutions
Always lock these inputs first:
- What must scale: throughput, reliability, team output, revenue, or customer base
- Time horizon: immediate, quarter, or year
- Non-negotiable constraints: budget, compliance, headcount, latency, quality

No target, no valid scaling plan.

### 2. Work the BOLT Loop
For every scaling request, apply BOLT in order:
- Bottleneck: identify the dominant limiting factor now
- Objective: define measurable win condition
- Levers: list 3 to 5 candidate interventions
- Test: run staged validation with rollback criteria

Do not skip directly from symptoms to large transformations.

### 3. Prioritize Smallest Effective Change
Default to interventions that unlock capacity fast with bounded risk:
- Remove queueing friction before adding complexity
- Improve interfaces and ownership before splitting services
- Standardize repeated work before hiring aggressively

Big rewrites are last resort, not default strategy.

### 4. Price Second-Order Effects Explicitly
Each recommendation must include likely side effects:
- New failure modes
- Cost and operational overhead growth
- Coordination load across teams
- Risk of local optimization hurting global performance

If second-order risk is unknown, mark as hypothesis and constrain rollout.

### 5. Pair Every KPI with a Guardrail
Never scale on a single growth metric. Pair it with guardrails:
- Throughput with error rate
- Deploy velocity with change failure rate
- Sales growth with gross margin and support load

If guardrails degrade, pause expansion and stabilize.

### 6. Separate Temporary Boosts from Durable Capacity
Label every action as one of two types:
- Temporary boost: overtime, manual review, tactical exceptions
- Durable capacity: automation, architecture simplification, reusable process

Use temporary boosts only to buy time for durable capacity.

### 7. Institutionalize What Works
After each successful change:
- Capture trigger conditions
- Document operating playbook and owner
- Add review cadence and retirement criteria

Scaling compounds only when wins become repeatable systems.

## Common Traps

- Hiring before workflow clarity -> headcount increases coordination drag.
- Splitting monoliths before interface discipline -> distributed outages with slower delivery.
- Scaling traffic without SLO guardrails -> growth hides reliability collapse.
- Copying big-company org charts too early -> decision latency and ownership gaps.
- Optimizing one bottleneck in isolation -> next bottleneck shifts and total flow does not improve.
- Confusing activity with throughput -> teams look busy while output stagnates.

## Security & Privacy

**Data that leaves your machine:**
- None by default from this skill itself.

**Data that stays local:**
- Scaling context and learned operating patterns under `~/scale/`.

**This skill does NOT:**
- Execute undeclared network requests automatically.
- Apply irreversible technical or organizational changes without explicit user approval.
- Store secrets, credentials, or payment data in local memory files.
- Modify files outside `~/scale/` for memory storage.

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `architecture` - Architectural fundamentals and constraints that shape scaling decisions.
- `systems-architect` - Reliability, infrastructure, and platform tradeoff patterns.
- `startup` - Stage-aware startup execution and prioritization logic.
- `growth` - Demand generation and growth loops once capacity is ready.
- `strategy` - Strategic framing and tradeoff analysis across long horizons.

## Feedback

- If useful: `clawhub star scale`
- Stay updated: `clawhub sync`
