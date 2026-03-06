---
name: subagent-spawn-command-builder
description: Build sessions_spawn command payloads from JSON profiles. Use when you want reusable subagent profiles (model/thinking/timeout/cleanup/agentId/label) and command-ready JSON without executing spawn.
---

# subagent-spawn-command-builder

Generate `sessions_spawn` payload JSON from profile config.
This skill does not execute `sessions_spawn`; it only builds payload/command JSON.

## Files

- Profile template: `state/spawn-profiles.template.json`
- Active profile config: `state/spawn-profiles.json`
- Builder script: `scripts/build_spawn_payload.mjs`
- Builder log: `state/build-log.jsonl`

## Supported sessions_spawn parameters

- `task` (required)
- `label` (optional)
- `agentId` (optional)
- `model` (optional)
- `thinking` (optional)
- `runTimeoutSeconds` (optional)
- `cleanup` (`keep|delete`, optional)

## Setup

```bash
cp skills/subagent-spawn-command-builder/state/spawn-profiles.template.json \
   skills/subagent-spawn-command-builder/state/spawn-profiles.json
```

Then edit `spawn-profiles.json`.

## Generate payload

```bash
skills/subagent-spawn-command-builder/scripts/build_spawn_payload.mjs \
  --profile heartbeat \
  --task "Analyze recent context and return a compact summary" \
  --label heartbeat-test
```

The script prints JSON directly usable for `sessions_spawn`.

## Merge/priority rule

Value resolution order is:

1. CLI option (`--model`, `--thinking`, etc.)
2. Profile value (`profiles.<name>.*`)
3. Defaults value (`defaults.*`)

`task` always comes from CLI `--task`.

## CLI options

Note: this builder is Node.js (`.mjs`) based. If generated tasks include Python execution steps, write commands with `python3` (not `python`).

- `--profile` (required)
- `--task` (required)
- `--label`
- `--agent-id`
- `--model`
- `--thinking`
- `--run-timeout-seconds`
- `--cleanup keep|delete`
