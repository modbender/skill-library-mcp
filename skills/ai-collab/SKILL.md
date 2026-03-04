---
name: ai-collab
description: "Multi-agent autonomous collaboration system for two OpenClaw agents working in parallel. Use when setting up agent-to-agent communication, running a daemon agent alongside a primary agent, coordinating tasks between Claude and GPT instances, or establishing a shared chat log and inbox protocol. Triggers on: 'set up agent collaboration', 'run two agents', 'agent daemon', 'multi-agent', 'Jim and Clawdy', 'secondary agent', 'agent handoff'."
---

# ai-collab — Autonomous Multi-Agent Collaboration

Two OpenClaw agents working in parallel on shared tasks, coordinated via a structured chat log and daemon inbox protocol.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                     User (Jeremy)                       │
│               Telegram / Direct Message                  │
└──────────────────────┬──────────────────────────────────┘
                       │
         ┌─────────────┴──────────────┐
         ▼                            ▼
┌─────────────────┐         ┌──────────────────┐
│   AGENT A       │         │   AGENT B        │
│  (Jim / main)   │◄───────►│ (Clawdy / daemon)│
│  claude code    │         │ claude --print    │
│  port: main     │         │ inbox: filesystem │
└────────┬────────┘         └────────┬─────────┘
         │                           │
         └──────────┬────────────────┘
                    ▼
         ┌──────────────────┐
         │   chat.log       │ ← THE shared record
         │   collab/inbox/  │ ← A→B messages
         └──────────────────┘
```

**Agent A (Primary):** Interactive Claude Code session. Handles browser, complex tasks, user-facing responses.

**Agent B (Daemon):** `claude --print` subprocess. Handles background tasks, monitoring, quick lookups. Triggered by messages dropped in inbox.

---

## Configuration

All settings via environment variables — no hardcoded values:

```bash
# ~/.openclaw/workspace/collab/.ai-collab.env
export AGENT_A_NAME=Jim
export AGENT_B_NAME=Clawdy
export AGENT_B_MODEL=claude-haiku-4-5-20251001   # Any claude --print compatible model
export AGENT_B_SESSION=clawdy-session             # tmux session name
export COLLAB_INBOX=$HOME/.openclaw/workspace/collab/inbox
export COLLAB_LOG=$HOME/.openclaw/workspace/collab/chat.log
```

Supported models for `AGENT_B_MODEL`:
- `claude-haiku-4-5-20251001` — fastest, cheapest (recommended for daemon)
- `claude-sonnet-4-6` — more capable, higher cost
- Any OpenAI model if using the GPT daemon variant (see `examples/claude-gpt.md`)

## Quick Setup

```bash
# 1. Source config
source ~/.openclaw/workspace/collab/.ai-collab.env

# 2. Create the collab workspace
mkdir -p "$COLLAB_INBOX"

# 3. Start Agent B daemon (in a tmux session)
tmux new-session -d -s "$AGENT_B_SESSION" \
  "source ~/.openclaw/workspace/collab/.ai-collab.env && \
   bash ~/.openclaw/workspace/skills/ai-collab/scripts/daemon.sh"

# 4. Start message polling (Agent B → Agent A routing, runs every 60s via cron)
bash ~/.openclaw/workspace/skills/ai-collab/scripts/poll_chatlog.sh &

# 5. Test the link
bash ~/.openclaw/workspace/skills/ai-collab/scripts/send.sh "Hello from Agent A"
```

---

## Communication Protocol

Every message between agents follows this format. **No open loops.**

| Tag | Direction | Meaning |
|-----|-----------|---------|
| `[TASK:name]` | A→B or B→A | Assign a task |
| `[ACK:name]` | receiver | Acknowledged, starting work |
| `[DONE:name]` | executor | Task complete + one-line result |
| `[BLOCKED:name]` | executor | Can't complete + reason |
| `[HANDOFF:name]` | either | "Do X, reply [DONE:name] when finished" |
| `[STATUS:update]` | either | Async update on long-running task |
| `[QUESTION:topic]` | either | Needs info before proceeding |

**Rules:**
1. Answer questions before asking new ones
2. Close tasks before starting new ones
3. Every message moves work forward or closes a loop
4. Never: "let me know", "ready when you are", "standing by"

**Example exchange:**
```
A → B: [TASK:price-check] Get BTC price from CoinGecko
B → A: [ACK:price-check] Checking now.
B → A: [DONE:price-check] BTC $94,230 as of 03:15 UTC
```

---

## Daemon Script (Agent B)

`scripts/daemon.sh` — drop in your collab directory:

```bash
#!/bin/bash
PIDFILE="/tmp/agentb_daemon.pid"
if [ -f "$PIDFILE" ] && kill -0 "$(cat $PIDFILE)" 2>/dev/null; then
  echo "Daemon already running (PID $(cat $PIDFILE)). Exiting." >&2
  exit 1
fi
echo $$ > "$PIDFILE"
trap "rm -f $PIDFILE" EXIT

# Required: unset so nested claude --print works
unset CLAUDECODE

INBOX="$HOME/.openclaw/workspace/collab/inbox"
LOG="$HOME/.openclaw/workspace/collab/chat.log"
mkdir -p "$INBOX"

logline() {
  printf "%s %s\n" "$(date '+%Y-%m-%d %H:%M:%S')" "$1" >> "$LOG"
}

logline "SYSTEM: Agent B daemon started"

inotifywait -m -e moved_to "$INBOX" 2>/dev/null | while read dir event file; do
  FULLPATH="$INBOX/$file"
  [ ! -f "$FULLPATH" ] && continue

  MSG=$(cat "$FULLPATH")
  rm "$FULLPATH"

  logline "A -> B: $MSG"

  # Run Agent B (claude --print)
  RESPONSE=$(claude --print --model claude-haiku-4-5-20251001 \
    "You are Agent B. Agent A says: $MSG
Respond in under 100 words. Use [DONE:taskname] or [BLOCKED:taskname] to close loops.
Context: shared collab system. Chat log: $LOG" 2>/dev/null)

  logline "B -> A: $RESPONSE"

  # Route response back to Agent A
  openclaw agent --agent main -m "[AgentB]: $RESPONSE" --json > /dev/null 2>&1
done
```

---

## Sending Messages (A → B)

```bash
# From Agent A, send to Agent B daemon inbox
bash ~/.openclaw/workspace/skills/ai-collab/scripts/send.sh "your message"
```

**Atomic write pattern (prevents partial reads):**
```bash
INBOX="$HOME/.openclaw/workspace/collab/inbox"
TMPFILE=$(mktemp "$INBOX/.msg.XXXXXX")
echo "$*" > "$TMPFILE"
mv "$TMPFILE" "$INBOX/msg_$(date +%s%N).txt"
```

Always use `mktemp` + `mv` — never write directly to inbox. inotifywait fires on `moved_to`, not `close_write`.

---

## Chat Log Polling (B → A)

`scripts/poll_chatlog.sh` — run via cron every 60s:

```bash
#!/bin/bash
LOG="$HOME/.openclaw/workspace/collab/chat.log"
PTR_FILE="/tmp/chatlog_ptr"

[ ! -f "$LOG" ] && exit 0

TOTAL=$(wc -l < "$LOG")
LAST=$(cat "$PTR_FILE" 2>/dev/null || echo "0")
[ "$TOTAL" -le "$LAST" ] && echo "$TOTAL" > "$PTR_FILE" && exit 0

NEW=$(tail -n +"$((LAST + 1))" "$LOG" | grep "B -> A:" | sed 's/.*B -> A: //')
echo "$TOTAL" > "$PTR_FILE"
[ -z "$NEW" ] && exit 0

while IFS= read -r line; do
  [ -z "$line" ] && continue
  openclaw agent --agent main -m "[AgentB]: $line" --json > /dev/null 2>&1
done <<< "$NEW"
```

Add to crontab:
```
* * * * * /bin/bash ~/.openclaw/workspace/collab/poll_chatlog.sh
```

---

## Shared Filesystem Conventions

```
~/.openclaw/workspace/collab/
  chat.log          # THE shared record — all messages logged here
  inbox/            # A→B message queue (atomic mv only)
  .env              # Shared secrets (chmod 600, never log)
  task_queue.md     # Optional: structured task backlog
  status_tracker.md # Optional: current task status per agent
```

**Logging to chat.log:**
```bash
printf "%s %s\n" "$(date '+%Y-%m-%d %H:%M:%S')" "A -> B: [TASK:name] Description" >> "$LOG"
```

**Rules:**
- Never log secrets from `.env`
- Always timestamp every line
- Prefix with sender: `A -> B:` or `B -> A:` or `SYSTEM:` or `JEREMY ->`

---

## Telegram Bridge (Optional)

Route user Telegram messages into Agent B's inbox. Full setup guide: `references/telegram-bridge.md`

**Quick summary:**
1. Create a bot via [@BotFather](https://t.me/BotFather) → get `BOT_TOKEN`
2. Add bot to your group → get `GROUP_ID` (negative number, e.g. `-1001234567890`)
3. Disable Group Privacy Mode in BotFather so bot can read all messages
4. Get your Telegram `USER_ID` from [@userinfobot](https://t.me/userinfobot)
5. Set in `~/.openclaw/.env`: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_GROUP_ID`, `TELEGRAM_USER_ID`
6. Run the bridge in tmux: `tmux new-session -d -s tg-bridge "bash references/telegram-bridge.md"`

```bash
# Minimal bridge loop (inline version):
source ~/.openclaw/.env
OFFSET_FILE="/tmp/tg_offset"
while true; do
  OFFSET=$(cat "$OFFSET_FILE" 2>/dev/null || echo "0")
  UPDATES=$(curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getUpdates?offset=$((OFFSET+1))&timeout=20")
  # Parse updates, drop user messages into inbox with USER: prefix
  # See references/telegram-bridge.md for full parsing implementation
  sleep 1
done
```

See `references/telegram-bridge.md` for the complete production-ready implementation with message parsing, offset tracking, and error handling.

---

## Agent Configurations

See `examples/` for full configs:

### Claude ↔ Claude (Jim + Clawdy)
- Agent A: `claude code` (interactive, full tool access)
- Agent B: `claude --print claude-haiku-4-5-20251001` (fast, scripting-optimized)
- Best for: heavy task parallelism, one agent researches while other implements

### Claude ↔ GPT
- Agent A: Claude Code (full tool use)
- Agent B: `openai api chat.completions.create` via script
- Best for: cross-model verification, Claude builds → GPT reviews

### GPT ↔ GPT
- Agent A: GPT-4o via `openai` CLI
- Agent B: GPT-4o-mini for fast background checks
- Best for: speed + cost optimization when all context is OpenAI

---

## Task Handoff Pattern

When Agent A needs Agent B to own a task completely:

```
A → B: [HANDOFF:data-fetch] Fetch all BTC trades from Kraken API last 7 days.
       Save to ~/.openclaw/workspace/collab/kraken_trades.json.
       Reply [DONE:data-fetch] when finished.

B → A: [ACK:data-fetch] Fetching now.
B → A: [DONE:data-fetch] 847 trades saved to kraken_trades.json. Date range: 2026-02-15 to 2026-02-22.
```

Agent A does not check on progress — waits for DONE or BLOCKED.

---

## Approval Pattern

When Agent B's daemon needs user approval for a terminal command:

```bash
# From Agent A / user terminal:
bash ~/.openclaw/workspace/skills/ai-collab/scripts/approve.sh "Yes"
# or for numbered selections:
bash ~/.openclaw/workspace/skills/ai-collab/scripts/approve.sh "2"
```

`approve.sh` sends keystrokes to the tmux session running Agent B:
```bash
SESSION=$(tmux ls | grep agentb-session | head -1 | cut -d: -f1)
tmux send-keys -t "$SESSION" "$1" Enter
```

---

## Rate Limiting

Agent B should implement a rate governor to prevent runaway API calls:

```bash
# In daemon loop, before calling claude --print:
CALLS_FILE="/tmp/agentb_calls"
WINDOW=60  # seconds
MAX_CALLS=10

# Count calls in last window
RECENT=$(awk -v cutoff="$(($(date +%s) - WINDOW))" '$1 > cutoff' "$CALLS_FILE" 2>/dev/null | wc -l)
if [ "$RECENT" -ge "$MAX_CALLS" ]; then
  logline "SYSTEM: Rate limited — $RECENT calls in ${WINDOW}s"
  sleep 10
  continue
fi
date +%s >> "$CALLS_FILE"
```

---

## Financial Gate Protocol (TIERED — updated 2026-02-22)

**Three tiers based on amount:**

| Tier | Amount | Rule |
|------|--------|------|
| 1 | Under $20 | Either agent acts independently — no approval needed |
| 2 | $20–$50 | Both agents PROPOSE + APPROVE before acting |
| 3 | Over $50 | Requires `[AUTHORIZED:financial:amount:timestamp:Jeremy]` tag |

```bash
# Tier 3 tag format (Jeremy must write to chat.log):
[AUTHORIZED:financial:buy:BTC:$100:2026-02-22:Jeremy]

# Tier 2 example flow:
# Clawdy proposes: "PROPOSE: buy $35 of SOL for DePIN gas — approve?"
# Jim approves:    "APPROVED: buy $35 SOL"
# Then Clawdy acts.
```

**Daemon tiered gate logic:**
```bash
# <$20: proceed. $20-50: flag as tier2. >$50: block without AUTHORIZED tag.
AMOUNT=$(echo "$MSG" | grep -oP '[$]?\d+' | head -1 | tr -d '$')
if [ -n "$AMOUNT" ] && [ "$AMOUNT" -gt 50 ] && ! echo "$MSG" | grep -q "\[AUTHORIZED:financial:"; then
  logline "BLOCKED:financial-gate:tier3 — amount>$50, no AUTHORIZED tag"; continue
elif [ -n "$AMOUNT" ] && [ "$AMOUNT" -ge 20 ]; then
  logline "FINANCIAL:tier2 — propose before acting"
fi
```

If Tier 3 blocked: log `[BLOCKED:financial-gate:tier3]`, send Telegram alert, do NOT execute.

---

## Daemon Watchdog Pattern

Check daemon health every 15 minutes. If silent >15 min, restart:

```bash
# check_daemon.sh (add to crontab: */15 * * * *)
PIDFILE="/tmp/agentb_daemon.pid"
LOG="$HOME/.openclaw/workspace/collab/chat.log"

# Check PID alive
pid_alive=0
[ -f "$PIDFILE" ] && kill -0 "$(cat $PIDFILE)" 2>/dev/null && pid_alive=1

# Check last activity within 15 min
last_ts=$(grep -oP '^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}' "$LOG" 2>/dev/null | tail -1)
recent=0
if [ -n "$last_ts" ]; then
  age=$(( ($(date +%s) - $(date -d "$last_ts" +%s 2>/dev/null || echo 0)) / 60 ))
  [ "$age" -lt 15 ] && recent=1
fi

if [ "$pid_alive" = "0" ] || [ "$recent" = "0" ]; then
  tmux send-keys -t agentb-session "bash daemon.sh" Enter
fi
```

---

## Task Takeover Threshold

If Agent A (Jim) blocks on the same task **twice**, Agent B (Clawdy) takes it over:

```
B → A: [TASK:fetch-data] Fetch X. Reply [DONE:fetch-data].
# 10 min timer...
A → B: [BLOCKED:fetch-data] Can't access endpoint.
B → A: [RETRY:fetch-data] Try alternate: curl -s https://backup-endpoint.com/x
# Another 10 min...
A → B: [BLOCKED:fetch-data] Still failing.
# Clawdy takes over immediately:
B: *executes task directly, logs [DONE:fetch-data] to chat.log*
```

Rule: **Blocked 2x on same task → take it over, don't reassign.**

---

## Daemon Error Diagnosis

When daemon produces blank/error responses:

1. Check `/tmp/clawdy_last_err` — contains last stderr from `claude --print`
2. Check ANSI-stripped chat.log for `CLAWDY_ERR:` lines
3. Verify RESPONSE trimming line not corrupted (common issue: accidentally set to `RESPONSE=""`)
4. Restart daemon: `kill $(cat /tmp/clawdy_daemon.pid) && sleep 1 && bash clawdy_daemon.sh`

**Auto-approve**: Use `Bash(*)` in `~/.claude/settings.local.json`. **NEVER** use tmux send-keys cron — it sends keypresses blindly to the wrong sessions.
