---
name: "Help Center"
slug: help-center
version: "1.0.0"
homepage: https://clawic.com/skills/help-center
description: "Build and run help centers with provider selection, migration playbooks, workflow mapping, content taxonomy, and support deflection metrics."
changelog: "Initial release with provider selection matrix, custom stack blueprint, migration playbook, and help center operations guidance."
metadata: {"clawdbot":{"emoji":"🛟","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## Setup

If `~/help-center/` does not exist or is empty, explain that local planning files can be created for this skill and follow `setup.md`.

## When to Use

User needs to create, migrate, or improve a help center. Handles provider selection, custom architecture, knowledge base structure, support workflow design, and ongoing optimization.

## Architecture

Memory lives in `~/help-center/`. See `memory-template.md` for structure.

```
~/help-center/
├── memory.md           # Status, decisions, and constraints
├── provider-score.md   # Provider scoring snapshots
├── content-inventory.md # Existing articles and gaps
└── rollout-log.md      # Launch and post-launch notes
```

## Quick Reference

| Topic | File |
|-------|------|
| Setup and integration | `setup.md` |
| Memory template | `memory-template.md` |
| Provider comparison | `provider-matrix.md` |
| Build your own stack | `build-own-stack.md` |
| Migration plan | `migration-playbook.md` |
| Content operations | `content-ops.md` |
| Launch checklist | `launch-checklist.md` |

## Core Rules

### 1. Frame the Support Model Before Picking Tools
Capture support channels, monthly ticket volume, languages, compliance constraints, and team size first. Do not recommend a provider or architecture without these inputs.

### 2. Compare Provider and Build-Your-Own Paths Explicitly
Use `provider-matrix.md` to score at least two vendor options and one custom-stack option against the same criteria: total cost, speed, customization, lock-in risk, and maintenance burden.

### 3. Design Information Architecture Early
Define categories, article templates, ownership, and review cadence before content migration. A help center without taxonomy rules becomes unsearchable within weeks.

### 4. Tie the Help Center to Ticketing Workflows
Map every article category to triage tags, escalation routes, and SLA targets. A help center is operational infrastructure, not only documentation.

### 5. Treat Migration as a Controlled Release
Use `migration-playbook.md` for inventory, redirects, URL mapping, and fallback plans. Never migrate content without rollback steps and QA checks.

### 6. Operate with Leading and Lagging Metrics
Track deflection rate, first response time, article freshness, unresolved search queries, and escalation frequency. Review weekly and update content priorities.

### 7. Save Decisions and Constraints for Future Sessions
After each strategic choice, update `~/help-center/memory.md` with decision rationale, rejected options, and open risks so future work stays consistent.

## Common Traps

- Choosing a provider by brand familiarity alone -> hidden costs and painful migration later.
- Migrating old articles without rewrite standards -> users keep opening tickets for already documented issues.
- Ignoring search analytics -> dead articles stay published while top unanswered intents grow.
- Launching without ownership model -> stale content accumulates and trust drops.
- Tracking only page views -> no visibility into support impact or deflection quality.

## Security & Privacy

**Data that leaves your machine:**
- None by default. This skill focuses on local planning and decision support.

**Data that stays local:**
- Planning notes, scoring decisions, and rollout logs in `~/help-center/`.

**This skill does NOT:**
- Send local files to third-party APIs.
- Execute provider-side changes automatically.
- Access files outside `~/help-center/` for memory storage.

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `customer-support` — run frontline support workflows and escalation handling.
- `documentation` — write clear internal and external product documentation.
- `workflow` — design repeatable operational workflows with clear handoffs.
- `crm` — connect support insights with customer lifecycle systems.

## Feedback

- If useful: `clawhub star help-center`
- Stay updated: `clawhub sync`
