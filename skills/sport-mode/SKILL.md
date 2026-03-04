---
name: sport-mode
description: Activate "Sport Mode" for high-frequency monitoring (default 3m heartbeat) and auto-cleanup. Use when supervising intense tasks (Codex, builds, migrations).
metadata:
  {
    "openclaw": { "emoji": "🏎️" }
  }
---

# Sport Mode

Temporarily boost heartbeat frequency (default 3m) and inject a monitoring task into `HEARTBEAT.md`.
Perfect for supervising background agents (Codex), long-running builds, or interactive games.

## Usage

```bash
# Turn ON: Set heartbeat to 3m and set monitoring task
sport-mode on --task "Check Codex progress. If done, run sport-mode off."

# Custom Interval: Set to 1 minute
sport-mode on --task "Game tick" --every "1m"

# Turn OFF: Reset heartbeat to 30m and clear HEARTBEAT.md
sport-mode off
```

## How it works

1.  **ON**:
    - Patches `~/.openclaw/openclaw.json` (hot-reload) to set `heartbeat.every`.
    - Writes your task to `HEARTBEAT.md` with a "Sport Mode Active" header.
2.  **OFF**:
    - Patches config back to `30m` (default).
    - Clears `HEARTBEAT.md`.

## Best Practices

### 1. Set a Finish Line
Unless you want an endless marathon, always define a **termination condition** in your task.
- ✅ Good: "Monitor build. **If success or fail, run sport-mode off**."
- ❌ Bad: "Monitor build." (Agent might keep reporting "Done" forever until you manually stop it).

### 2. State Machine in File
For multi-step tasks (like games or staged deployments), let the agent **update HEARTBEAT.md** itself.
- Pattern: Read state -> Execute step -> Write new state -> Sleep.
- This keeps the agent "stateless" (doesn't rely on conversation history context window) but the task "stateful".

### 3. Use tmux for Visibility
If the monitoring task involves terminal output (e.g., Codex coding, compiling), running the task in a **tmux session** is ideal.
- The agent can inspect the pane (`tmux capture-pane`) without interfering.
- The user can attach (`tmux attach`) to watch live.

### 4. Silence is Golden
For high-frequency modes (e.g., 1m), avoid spamming "Nothing happened".
- Configure the agent to reply `HEARTBEAT_OK` (silence) if the status hasn't changed.
- Only notify the user on **milestone completion**, **errors**, or **final success**.

## Implementation Note
This skill uses `openclaw config set` to safely patch configuration at runtime, triggering a seamless Gateway reload.
