# 🩺 swarm-self-heal

**Swarm reliability watchdog for OpenClaw** — validates gateway, channels, and every agent lane. Performs bounded recovery when things go sideways. Emits auditable receipts so you know exactly what happened and why.

Your agents watch themselves. You sleep.

## Install

```bash
clawhub install swarm-self-heal
```

Or clone from [GitHub](https://github.com/cacheforge-ai/cacheforge-skills).

## Features

- **Passive-first detection** — reads `openclaw status --json` before touching anything. No unnecessary pings, no wasted tokens.
- **Stale-lane active probes** — only agents that haven't checked in recently get pinged. Fresh lanes are left alone.
- **Infra vs soft failure classification** — distinguishes gateway crashes from auth/rate-limit issues. Different problems, different responses.
- **Bounded recovery** — one restart pass per run. No destructive wipes. No blind reinstalls. No infinite retry loops.
- **Concurrency-safe** — lock-protected execution prevents overlapping cron runs from stepping on each other.
- **Primary + backup watchdog lanes** — resilient cron wiring with `xhigh` thinking. If the watchdog goes down, the backup catches it.
- **Deterministic output contract** — machine-parseable receipts for audit trails and downstream automation.

## Quick Start

```bash
# Install scripts + wire cron lanes
bash ./skills/swarm-self-heal/scripts/setup.sh

# Run one canary check right now
bash ./skills/swarm-self-heal/scripts/check.sh
```

## Usage

```bash
# Direct run from deployed path
bash ~/.openclaw/workspace-studio/scripts/anvil_watchdog.sh

# Tune for slower providers
PASSIVE_STALE_SECONDS=3600 PING_TIMEOUT_SECONDS=180 \
  bash ~/.openclaw/workspace-studio/scripts/anvil_watchdog.sh

# Target specific lanes
TARGETS_CSV=main,reviewer \
  bash ~/.openclaw/workspace-studio/scripts/anvil_watchdog.sh
```

## What It Checks

| Layer | Method | Recovery |
|-------|--------|----------|
| **Gateway** | `openclaw health` | systemd restart, then CLI restart |
| **Channels** | `openclaw channels status --json --probe` | gateway restart |
| **Agent lanes** | Passive recency check, then active ping if stale | classify + re-probe after infra restart |

## Output Contract

Every run emits deterministic, machine-parseable fields:

```
timestamp=2026-02-21T14:30:00Z
tool=swarm_self_heal
targets=main,builder-1,builder-2,reviewer,designer
ok_agents=main,builder-1,builder-2,reviewer,designer
failed_agents=none
actions=none
VERDICT=healthy
RECEIPT=swarm_self_heal:2026-02-21T14:30:00Z:healthy
```

Verdicts: `healthy` | `degraded` | `recovered` | `failed`

## Safety Model

- Single recovery pass per run — no escalation loops
- No destructive state wipes
- No blind reinstall behavior
- All recovery actions are explicit in output
- Lock file prevents concurrent overlapping runs

## Requirements

- OpenClaw CLI with gateway service installed
- `bash`, `jq`

## Design Principles

- **Low-noise** — healthy runs summarize to one line. Only failures get verbose.
- **Safe over clever** — bounded recovery and explicit receipts beat hidden side effects.
- **Production-fit** — works with cron, Telegram alerts, and multi-agent swarms out of the box.

## Related Skills

| Skill | Complements |
|-------|-------------|
| [`pager-triage`](../pager-triage/) | Incident triage after swarm-self-heal detects a failure |
| [`agentic-devops`](../agentic-devops/) | Host/process/Docker diagnostics for deeper investigation |
| [`log-dive`](../log-dive/) | Unified log search to correlate failure timelines |
| [`prom-query`](../prom-query/) | Metrics correlation for infrastructure-level issues |
| [`context-engineer`](../context-engineer/) | Context-budget analysis when agents are slow or degraded |

## License

MIT — see [LICENSE](../../LICENSE).

---

Built by **[Anvil AI](https://labs.anvil-ai.io/)** — [See what our agents are building](https://labs.anvil-ai.io).
