---
name: prediction-market-bot
description: Runs the full Dawn CLI strategy lifecycle from authentication and funding through strategy creation, launch, monitoring, and termination. Use when the user asks to create, launch, monitor, debug, or operate a strategy/agent using dawn-cli commands.
tags: [trading, strategy, operations, prediction-market]
metadata:
  openclaw:
    emoji: "🌅"
    homepage: https://dawn.ai
    requires:
      bins: [dawn]
    install:
      - kind: node
        package: "@dawnai/cli"
        bins: [dawn]
---

# Run a Dawn strategy lifecycle

## Goal

Execute a complete `dawn` strategy workflow: install/check CLI, authenticate, prepare funding, create and iterate strategy code, launch paper/live runs, monitor status, and stop safely when requested.

## When to use

Use this skill when the user asks to:
- create a strategy from plain-English intent,
- revise or upload strategy code,
- launch paper or live strategy runs,
- monitor run health/positions/logs,
- stop or debug an active run.

## Install and preflight

Install `dawn` if needed:

```bash
npm install -g @dawnai/cli
```

Verify:

```bash
# Print current Dawn CLI version
dawn version
dawn --help
```

Local source workflow only:

```bash
cd dawn-cli
npm install
npm run build
./install.sh
```

## Command map

Auth:
- `dawn auth login`
- `dawn auth status`
- `dawn auth logout`

Account:
- `dawn account overview`
- `dawn account fund`
- `dawn account wallet`

Strategy authoring:
- `dawn strategy list`
- `dawn strategy create "<text>"`
- `dawn strategy status <conversationId>`
- `dawn strategy revise <conversationId> "<text>"`
- `dawn strategy rules <conversationId> list`
- `dawn strategy rules <conversationId> approve <rule-index>`
- `dawn strategy rules <conversationId> approve-all`
- `dawn strategy code <conversationId> status`
- `dawn strategy code <conversationId> generate`
- `dawn strategy code <conversationId> export [--out <path>] [--json]`
- `dawn strategy code <conversationId> upload <path-to-file>`

Launch and operations:
- `dawn strategy launch <conversationId> --budget <usd> [--live] [--hours N]`
- `dawn strategy positions <conversationId> [--strategy-id <strategyId>]`
- `dawn run list`
- `dawn run status <conversationId>`
- `dawn run logs <conversationId> [--limit N]`
- `dawn run stop <conversationId>`

## Standard flow

1. Authenticate: `dawn auth login`.
2. Confirm funding path: `dawn account fund` (required for live runs).
3. Create strategy: `dawn strategy create "<request>"` and capture `conversationId`.
4. Iterate strategy:
   - revise prompt (`strategy revise`) and/or upload files (`strategy code ... upload`),
   - review/approve rules,
   - generate code,
   - export code when needed (`--json` for multi-file map).
5. Launch:
   - paper: `dawn strategy launch <conversationId> --budget 50`
   - live: `dawn strategy launch <conversationId> --budget 50 --live`
   - custom duration: add `--hours N`
6. Monitor:
   - `dawn run status <conversationId>`
   - `dawn strategy positions <conversationId>`
   - `dawn run logs <conversationId> --limit N`
7. Stop when requested: `dawn run stop <conversationId>`, then verify status again.

## Monitoring loop

For active monitoring sessions:
1. Query `dawn run status <conversationId>`.
2. Record timestamp, `isRunning`, status, and active strategy IDs.
3. Query `dawn strategy positions <conversationId>` for holdings/PnL.
4. Query `dawn run logs <conversationId> --limit N` for execution details.
5. If records look stale or missing, wait briefly and retry once.

## Troubleshooting

- `"Not authenticated. Run: dawn auth login"`: run `dawn auth login` and retry.
- Auth callback completes but CLI appears stuck: interrupt once and retry login.
- `"No strategy version found..."`: create/revise/upload strategy code, then relaunch.
- `"No strategies found for this agent"` on stop: verify `conversationId`, then check `dawn run status`.
- Live launch fails: re-check funding path with `dawn account fund`.

## Run checklist

```text
Dawn Strategy Runbook
- [ ] Preflight complete
- [ ] Auth complete
- [ ] Funding path checked (or user confirmed paper-only)
- [ ] conversationId captured
- [ ] Strategy code generated/uploaded
- [ ] Launch run completed (paper/live)
- [ ] strategyId captured (if launched)
- [ ] Monitoring snapshots collected
- [ ] Stop executed (if requested)
- [ ] Final status verified
```

## Skills

Individual skills for each command:

| Skill | Purpose |
|-------|---------|
| **dawn-auth** | Install, authenticate, check status, logout |
| **dawn-account** | Account overview, funding, wallet balances |
| **dawn-strategy-create** | Create a strategy from plain-English prompt |
| **dawn-strategy-list** | List all strategies |
| **dawn-strategy-status** | Full strategy status and health |
| **dawn-strategy-revise** | Iterate on a strategy with revisions |
| **dawn-strategy-rules** | List, approve, and manage rules |
| **dawn-strategy-code** | Code generation, status, export, upload |
| **dawn-strategy-launch** | Launch paper or live runs |
| **dawn-strategy-positions** | View positions and PnL |
| **dawn-run-monitor** | List runs, check status, view logs |
| **dawn-run-stop** | Stop a running strategy |

## Required output

When using this skill, always return:
- `conversationId`,
- `strategyId` (if launched),
- run mode (paper/live),
- latest monitoring summary,
- exact next command to run (or the last command run).
