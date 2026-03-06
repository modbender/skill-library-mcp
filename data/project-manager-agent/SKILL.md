---
name: project-manager-agent
displayName: Project Manager Agent
description: Monitors active sub-agents, detects stalls, provides status updates, and steers stuck agents via sessions_send.
---

# Project Manager Agent

## Description

Monitors active sub-agents, detects stalls, provides status updates, and steers stuck agents via sessions_send.

# Project Manager Agent

This skill provides oversight for your OpenClaw sub-agents. It proactively checks the status of running sub-agents, identifies potential stalls or failures, and can steer stalled sub-agents by sending a continue message via the **sessions_send** tool.


## Usage

### Running the monitor

```bash
python3 <skill-dir>/scripts/project_manager.py
```

### Options

- `--staleness_threshold_minutes <int>`: Minutes after which a sub-agent is considered stalled (default from config or 10).
- `--check_all_sessions`: Check all sessions, not just subagents of the current main session.
- `--json`: Print human summary then a JSON line with `stalledSessionKeys`, `steerMessage`, and `summary` for agent steering.
- `--no_cooldown`: Output all stalled keys (ignore 15-minute cooldown).
- `--record-steered KEY [KEY ...]`: Record these session keys as just steered (for cooldown). Run after calling sessions_send.

### Example (Status check, human-only)

```bash
python3 /Users/ghost/.openclaw/workspace/skills/project-manager-agent/scripts/project_manager.py --staleness_threshold_minutes 15
```

### Example (Agent run with steering)

```bash
python3 /Users/ghost/.openclaw/workspace/skills/project-manager-agent/scripts/project_manager.py --json --staleness_threshold_minutes 10
```

Then parse the last line (JSON), call sessions_send for each key in `stalledSessionKeys`, and optionally run `--record-steered <keys>`.


## Features

- **Sub-agent Monitoring**: Lists all active sub-agents (file-based; no gateway API in the script).
- **Stall Detection**: Flags sub-agents that haven't updated their status within a configurable time period.
- **Failure Identification**: Reports on sub-agents that have aborted their last run.
- **Status Reports**: Human-readable summaries and optional JSON with `stalledSessionKeys` for steering.
- **Automated Steering**: When you run the skill with `--json`, parse the output and call **sessions_send** for each stalled session (see Agent instructions below).


## Agent instructions (mandatory when running this skill)

When the user or a cron asks you to run the project-manager-agent skill:

1. **Run the script with `--json`** (and existing args as needed):
   ```bash
   python3 /Users/ghost/.openclaw/workspace/skills/project-manager-agent/scripts/project_manager.py --json --staleness_threshold_minutes 10
   ```
2. **Parse the script stdout**: The last line is a single JSON object with `stalledSessionKeys`, `steerMessage`, and `summary`. Parse it (e.g. take the last line that starts with `{` and ends with `}`).
3. **If `stalledSessionKeys` is non-empty**:
   - For each session key in `stalledSessionKeys` (cap at 5 per run to avoid spam), call **sessions_send**(`sessionKey`, `steerMessage` from JSON or `"Please continue working on your task."`, `0`) (fire-and-forget; `timeoutSeconds=0`).
   - Optionally run the script again to record cooldown so the same session is not steered again for 15 minutes:
     ```bash
     python3 /Users/ghost/.openclaw/workspace/skills/project-manager-agent/scripts/project_manager.py --record-steered <key1> <key2> ...
     ```
4. **Reply** to the user/cron with the status summary (the human-readable part of the script output) and, if you steered any, add: "Steered N stalled subagent(s)."

You have access to **sessions_list** and **sessions_send**; the script only produces the list of session keys to steer. Steering is done by you in the same turn via the sessions_send tool.


## Config (optional)

See `config.json` for: `staleness_threshold_minutes`, `steer_cooldown_minutes`, `steer_message`, `max_steer_per_run`.


## Integration as a Cron Job

This skill is ideal for a cron job, running periodically (e.g., every 5 minutes). The agent runs the script with `--json`, steers stalled subagents via sessions_send, and announces the status.

**Example Cron Job Payload:**

```json
{
  "payload": {
    "kind": "agentTurn",
    "message": "Run project-manager-agent skill and report status of all sub-agents.",
    "model": "openrouter/google/gemini-2.5-flash",
    "thinking": "low",
    "timeoutSeconds": 60
  },
  "schedule": {
    "kind": "every",
    "everyMs": 300000
  },
  "delivery": {
    "mode": "announce"
  },
  "sessionTarget": "isolated",
  "name": "Project Manager (Sub-agent Monitor)"
}
```

---
version: 0.2.0
