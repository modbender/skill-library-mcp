---
name: agent-wake
version: 1.0.1
description: Wake an OpenClaw agent session from an external script or process. Use when a background task (Claude Code CLI, cron job, webhook, price alert, or any script) finishes and you want the agent to automatically receive a notification and respond in the correct Discord channel without manual prompting. Solves the problem of agents not knowing when async work completes.
credentials:
  - name: GATEWAY_TOKEN
    description: OpenClaw gateway auth token. Read from GATEWAY_TOKEN env var, a local .env file next to the script, or auto-detected from ~/.openclaw/gateway.cmd.
    required: true
---

# agent-wake

Wake your OpenClaw agent from any external process using the gateway HTTP API.

## How it works

`scripts/agent-wake.py` calls `POST /tools/invoke` with the `cron` tool, firing a `wake` event into the agent's session. The agent receives the event text as a system message and responds immediately in the correct channel.

## Quick start

```bash
python agent-wake.py "Task finished -- brief summary" "YOUR_DISCORD_CHANNEL_ID"
```

## Setup (one-time)

See `references/setup.md` for:
- Enabling the `cron` tool over HTTP (required -- blocked by default)
- Setting `GATEWAY_TOKEN`
- Finding your Discord channel ID

## Usage patterns

### End of a Claude Code CLI task
Add to the task prompt:
```
When done, run: python "/path/to/agent-wake.py" "Task done -- summary here" "CHANNEL_ID"
```

### From any Python script
```python
import subprocess
subprocess.run([
    "python", "/path/to/agent-wake.py",
    "Price alert triggered -- AAPL crossed $200",
    "1475232925724315740"
])
```

### Standalone (wake main session)
```bash
python agent-wake.py "Backup completed successfully"
```
Omit channel ID to wake the main session (response goes to default channel).

## What the agent receives

The event text is injected as a system message. Be specific -- the agent acts on what you write:

```
Build finished -- 3 errors fixed, tests passing. Send your response to Discord channel 1475232925724315740...
```

## Script location

`scripts/agent-wake.py` -- copy this wherever your tasks run. No dependencies beyond Python stdlib.
