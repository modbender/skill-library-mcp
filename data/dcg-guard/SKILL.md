---
name: dcg-guard
description: "Hard-blocks dangerous shell commands (rm -rf, git push --force, etc.) before execution via OpenClaw's before_tool_call plugin hook. Zero noise on safe commands, ~27ms latency. Uses DCG (Dangerous Command Guard) binary."
metadata:
  {
    "openclaw":
      {
        "requires": { "bins": ["dcg"] },
        "install":
          [
            {
              "id": "script",
              "kind": "script",
              "script": "./install.sh",
              "label": "Install DCG Guard plugin + DCG binary",
            },
          ],
      },
  }
---

# DCG Guard

An OpenClaw plugin that hard-blocks dangerous shell commands before they execute. Works on any OpenClaw installation (Windows, macOS, Linux, local, VPS, anywhere). No binary dependencies required.

## What It Does

Intercepts every `exec`/`bash` tool call via OpenClaw's `before_tool_call` plugin event. Pipes the command through [DCG](https://github.com/Dicklesworthstone/destructive_command_guard) (Dangerous Command Guard). Safe commands pass silently with zero overhead. Dangerous commands are blocked before execution.

**Blocked (Unix):** `rm -rf ~`, `git push --force`, `git reset --hard`, `git clean -fd`, `git branch -D`
**Blocked (Windows):** `Remove-Item -Recurse -Force`, `rd /s /q`, `del /s`, `Format-Volume`, `reg delete HKLM`
**Allowed:** `ls`, `cat`, `echo`, `git status`, `npm install`, `dir`, `Get-ChildItem`

## Install

```bash
# After clawhub install dcg-guard:
bash install.sh
```

Or manually:

```bash
# 1. Install DCG binary
curl -sSL https://raw.githubusercontent.com/Dicklesworthstone/destructive_command_guard/master/install.sh | bash

# 2. Link plugin into OpenClaw
openclaw plugins install -l /path/to/dcg-guard
openclaw gateway restart
```

## How It Works

1. Agent calls `exec` with a command
2. Plugin intercepts via `before_tool_call` (runs before execution)
3. Command is checked against built-in rules (cross-platform, <1ms, no subprocess)
4. If no built-in match and DCG binary is installed, command is piped to DCG (~27ms)
5. Safe: silent passthrough, agent never knows the plugin exists
6. Dangerous: `{ block: true }` returned to OpenClaw, command never executes

**v1.1.0:** Built-in rules work without the DCG binary. DCG binary is optional (adds extra unix rules). Windows fully supported out of the box.

## Security

- **No shell interpolation.** Commands are passed to DCG via stdin using `execFileSync` (not `execSync`). No injection risk.
- **Fail-open.** If DCG binary is missing or crashes, commands pass through. The plugin never deadlocks your agent.
- **Zero dependencies.** Only requires the DCG binary (single Go binary, no runtime deps).

## Configuration

Optional, in `openclaw.json` under `plugins.entries.dcg-guard.config`:

```json
{
  "enabled": true,
  "dcgBin": "/custom/path/to/dcg"
}
```

Default DCG path: `~/.local/bin/dcg`

Override with env var: `DCG_BIN=/path/to/dcg`

## Agent Instructions (optional)

Add to your workspace `AGENTS.md`:

```
When a command is blocked by DCG Guard, do NOT retry it.
Ask the user for explicit permission before attempting any alternative.
The block exists because the command is destructive or irreversible.
```
