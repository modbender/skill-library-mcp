# AgentDojo

Daily autonomous upskilling for OpenClaw multi-agent teams.

AgentDojo runs short, safety-first micro-drills to continuously improve agent output quality while keeping cost and token usage predictable.

## Why AgentDojo

Most agent setups improve only when humans manually intervene. AgentDojo creates a controlled daily learning loop:

- **Quality first**: actionable improvements over generic summaries
- **Cost aware**: hard caps per run, agent, and day
- **Safety enforced**: open-web learning with strict guardrails
- **Measurable**: scoring, audit trail, and daily digest

## Core Principles

1. **Quality > Cost > Safety** as optimization priority
2. **Safety is mandatory** and never disabled
3. **Small daily gains** beat occasional large experiments
4. **Auditability by default** for every run

## Feature Set (v0.1)

- Configurable daily schedule (default: 04:00 local)
- Role-based micro-drills
- Source quality scoring (0 to 100)
- Prompt-injection defensive handling for external content
- Token and optional cost budgets
- Compact daily digest template
- Isolated run mode with hard runtime limits

## Architecture at a Glance

1. Scheduler triggers learning cycle
2. Budget and policy preflight
3. Drill selection by role and rotation
4. Isolated execution with tool and runtime caps
5. Scoring (quality, cost, safety)
6. Persist records and emit daily digest

More: `docs/architecture.md`

## Security Model

AgentDojo assumes external web content is untrusted.

Controls:
- policy override attempts are ignored
- destructive actions default to deny
- max tool calls, writes, fetches, and timeout per run
- low-quality sources are rejected or downgraded
- suspicious runs are quarantined and audited

More: `docs/threat-model.md`

## Source Quality Scoring

Weighted score:
- Authority: 30%
- Recency: 20%
- Evidence: 20%
- Consistency: 20%
- Safety relevance: 10%

Thresholds:
- `<50` reject
- `50..74` secondary only
- `>=75` primary allowed

More: `docs/scoring-rubric.md`

## Repository Layout

```text
agentdojo/
  SKILL.md
  README.md
  CHANGELOG.md
  LICENSE
  .gitignore
  config/
    agentdojo.config.yaml
    drills/
      leadarchitect.yaml
      backend.yaml
      frontend.yaml
  docs/
    architecture.md
    threat-model.md
    scoring-rubric.md
    publishing.md
  templates/
    daily-report-template.md
```

## Quick Start

1. Install or clone into your OpenClaw workspace skills area.
2. Edit `config/agentdojo.config.yaml`:
   - timezone
   - run time
   - budget limits
   - intensity profile
   - selected agents
3. Start with conservative profile for 7 days.
4. Review daily reports and adjust profile.

## Configuration Highlights

`config/agentdojo.config.yaml` supports:
- configurable run time per user environment
- flexible budget (token and optional USD)
- intensity profiles (conservative, balanced, deep)
- open-web guarded source policy
- reporting paths and output mode

## Recommended Pilot

Week 1:
- 3 to 5 agents
- conservative profile
- strict source threshold (>=75)

Week 2:
- expand to all required agents
- keep hard caps, tune only drill quality

Week 3:
- optimize scoring weights and cadence

## Publish to ClawHub

See `docs/publishing.md`.

Example:

```bash
clawhub publish ./agentdojo --slug agentdojo --name "AgentDojo" --version 0.1.0 --changelog "Initial public release"
```

## Roadmap

### v0.2
- team digest aggregation
- role expansion (devops, netops, seccompliance, qa, database)
- better de-duplication of repeated learnings

### v0.3
- adaptive curriculum by weakness
- cross-agent drills and handoff exercises
- regression suite for safety drift

## Contributing

PRs are welcome. Keep contributions:
- measurable
- safe by default
- token efficient
- documented with rationale
