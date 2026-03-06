# Agent Budget Governance Framework

## Philosophy

Trust-based autonomy with accountability. Agents start with mesh privileges
(can spawn each other directly), keep them by being responsible with budget,
and lose them through waste.

## Daily Token Budget

Each agent has a daily output token budget. Resets at midnight in the configured timezone.

Default: 50,000 output tokens/day per agent. Orchestrator (main) is unlimited.

## Budget File Schema

Location: `agents/<agent_dir>/BUDGET.json`

```json
{
  "daily_limit_output_tokens": 50000,
  "today": "YYYY-MM-DD",
  "used_output_tokens": 0,
  "spawns": [
    {"target": "agent_id", "task": "brief description", "tokens": 5000, "ts": "ISO8601"}
  ],
  "status": "active|red|demoted",
  "warnings": [],
  "consecutive_overbudget_days": 0
}
```

## Enforcement Levels

| Level | Threshold | Effect |
|-------|-----------|--------|
| Green | < 80% | Normal operation |
| Yellow | 80-100% | Warning logged. Finish current work, avoid new spawns |
| Red | > 100% | Over budget. MUST NOT spawn. Route through orchestrator |
| Emergency | > 200% | Immediate demotion |
| Demoted | 3 consecutive days over | Mesh privileges revoked |

## Demotion Process

1. Set `allowAgents: []` in openclaw.json for the agent
2. Set `status: "demoted"` in BUDGET.json
3. Log event to `agents/governance/log.jsonl`
4. Restart gateway
5. Alert the human operator

## Rehabilitation

1. Agent demonstrates responsible behaviour for 5 days via orchestrator-mediated calls
2. Orchestrator recommends reinstatement
3. Human approves
4. Restore `allowAgents` and set `status: "active"`

## Governance Log

Append-only JSONL at `agents/governance/log.jsonl`:

```json
{"ts": "ISO8601", "agent": "name", "event": "daily_reset|warning|red|demotion|reinstatement", "details": {}}
```

## Agent AGENTS.md Budget Rules Section

Every agent's AGENTS.md must include:

```markdown
## Budget Rules
- Read `agents/<your_dir>/BUDGET.json` at session start to check your status
- If status is "red" or "demoted": do NOT spawn other agents. Write to OUTBOX.md instead.
- After completing spawned tasks, update BUDGET.json: increment `used_output_tokens` and add to `spawns[]`
- If approaching 80% of daily limit, finish current work and avoid new spawns
- Budget resets daily at midnight. Orchestrator audits on heartbeat.
- See `agents/governance/GOVERNANCE.md` for full rules
```
