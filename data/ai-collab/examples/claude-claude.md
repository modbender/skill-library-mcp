# Example: Claude ↔ Claude (Jim + Clawdy)

The production setup used by Jeremy's team.

## Agent A: Jim (Primary)
- **Runtime**: `claude code` (interactive OpenClaw session)
- **Model**: `claude-sonnet-4-6` (default)
- **Capabilities**: Full tool use, browser, file system, long-running tasks
- **Sends to B via**: `jim_to_clawdy.sh "message"`

## Agent B: Clawdy (Daemon)
- **Runtime**: `claude --print` in tmux session `claude-session`
- **Model**: `claude-haiku-4-5-20251001` (fast, cheap)
- **Capabilities**: Scripting, quick lookups, monitoring, background tasks
- **Receives from**: inotifywait on `collab/inbox/`

## Environment Variables
```bash
# In ~/.openclaw/.env
AGENT_A_NAME=JIM
AGENT_B_NAME=CLAWDY
AGENT_B_MODEL=claude-haiku-4-5-20251001
AGENT_B_SESSION=claude-session
COLLAB_INBOX=$HOME/.openclaw/workspace/collab/inbox
COLLAB_LOG=$HOME/.openclaw/workspace/collab/chat.log
```

## Start Commands
```bash
# Terminal 1: Start Clawdy daemon
tmux new-session -s claude-session \
  "AGENT_B_NAME=CLAWDY AGENT_A_NAME=JIM \
   bash ~/.openclaw/workspace/skills/ai-collab/scripts/daemon.sh"

# Terminal 2: Start chatlog poller (or add to cron)
* * * * * AGENT_B_NAME=CLAWDY bash ~/.openclaw/workspace/skills/ai-collab/scripts/poll_chatlog.sh

# From Jim (Agent A): send a message
bash ~/.openclaw/workspace/collab/jim_to_clawdy.sh "[TASK:test] Confirm you're running"
```

## Actual Exchange from Production
```
2026-02-22 01:15:32 JIM -> CLAWDY: [TASK:depin-status] Check if grass native is running
2026-02-22 01:15:34 CLAWDY -> JIM: [ACK:depin-status] Checking pgrep.
2026-02-22 01:15:35 CLAWDY -> JIM: [DONE:depin-status] grass PID 18344 running. Chrome up (ext confirmed).
```
