# Telegram Bridge — Full Setup

Route user Telegram messages into Agent B's inbox so the daemon can respond autonomously.

## Prerequisites

1. **Create a Telegram bot** via [@BotFather](https://t.me/BotFather):
   - `/newbot` → follow prompts → get `BOT_TOKEN`
   - `/mybots` → select bot → **Bot Settings → Group Privacy → Turn Off** (required to read group messages)

2. **Add bot to your group** → send a message → get the `GROUP_ID`:
   ```bash
   curl -s "https://api.telegram.org/bot<BOT_TOKEN>/getUpdates" | python3 -m json.tool | grep '"id"' | head -5
   # Group IDs are negative numbers: -1001234567890
   ```

3. **Get your Telegram USER_ID** from [@userinfobot](https://t.me/userinfobot):
   - Send it a message → it replies with your ID

4. **Store credentials** in `~/.openclaw/.env` (chmod 600):
   ```bash
   TELEGRAM_BOT_TOKEN=your-bot-token
   TELEGRAM_GROUP_ID=-your-group-id
   TELEGRAM_USER_ID=your-user-id
   ```

## The Bridge Script

Save to `scripts/telegram-bridge.sh` and run in tmux:

```bash
#!/bin/bash
# telegram-bridge.sh — Route Telegram group messages to Agent B inbox
# Run: tmux new-session -d -s tg-bridge "bash scripts/telegram-bridge.sh"

source ~/.openclaw/.env

BOT_TOKEN="${TELEGRAM_BOT_TOKEN:?TELEGRAM_BOT_TOKEN not set}"
GROUP_ID="${TELEGRAM_GROUP_ID:?TELEGRAM_GROUP_ID not set}"
WHITELIST_ID="${TELEGRAM_USER_ID:?TELEGRAM_USER_ID not set}"  # Only route this user's messages
INBOX="${COLLAB_INBOX:-$HOME/.openclaw/workspace/collab/inbox}"
LOG="${COLLAB_LOG:-$HOME/.openclaw/workspace/collab/chat.log}"
OFFSET_FILE="/tmp/tg_bridge_offset"

mkdir -p "$INBOX"
OFFSET=$(cat "$OFFSET_FILE" 2>/dev/null || echo "0")

log_system() {
  printf "%s SYSTEM: %s\n" "$(date '+%Y-%m-%d %H:%M:%S')" "$1" >> "$LOG"
}

log_system "Telegram bridge started"

while true; do
  RESPONSE=$(curl -s \
    "https://api.telegram.org/bot${BOT_TOKEN}/getUpdates?offset=$((OFFSET+1))&limit=10&timeout=20&allowed_updates=[\"message\"]")

  UPDATES=$(echo "$RESPONSE" | python3 -c "
import json, sys
d = json.load(sys.stdin)
if not d.get('ok'):
    sys.exit(0)
for u in d.get('result', []):
    uid = u['update_id']
    msg = u.get('message', {})
    chat_id = str(msg.get('chat', {}).get('id', ''))
    sender = msg.get('from', {})
    sender_id = str(sender.get('id', ''))
    is_bot = sender.get('is_bot', False)
    text = msg.get('text', '').replace('\n', '\\\\n')
    username = sender.get('username', '') or sender.get('first_name', 'unknown')
    print(f'{uid}|{chat_id}|{sender_id}|{is_bot}|{username}|{text}')
" 2>/dev/null)

  while IFS='|' read -r uid chat_id sender_id is_bot username text; do
    [ -z "$uid" ] && continue

    # Only process messages from the configured group
    if [ "$chat_id" != "$GROUP_ID" ]; then
      OFFSET="$uid"
      continue
    fi

    # Skip bot messages
    if [ "$is_bot" = "True" ]; then
      OFFSET="$uid"
      continue
    fi

    # Restore newlines
    text=$(echo "$text" | sed 's/\\n/\n/g')

    if [ "$sender_id" = "$WHITELIST_ID" ]; then
      # Whitelisted user → route to Agent B inbox with USER: prefix
      TMPFILE=$(mktemp "$INBOX/.msg.XXXXXX")
      echo "USER: $text" > "$TMPFILE"
      mv "$TMPFILE" "$INBOX/msg_$(date +%s%N).txt"
      log_system "Telegram → inbox: ${text:0:60}"
    else
      # Other group members → log as context only, don't route to daemon
      log_system "[TG] $username: ${text:0:80}"
    fi

    OFFSET="$uid"
    echo "$OFFSET" > "$OFFSET_FILE"
  done <<< "$UPDATES"

  sleep 2
done
```

## Running It

```bash
# Start bridge in background tmux session
tmux new-session -d -s tg-bridge \
  "bash ~/.openclaw/workspace/skills/ai-collab/scripts/telegram-bridge.sh"

# Watch the log to confirm messages are routing
tail -f ~/.openclaw/workspace/collab/chat.log | grep -E "Telegram|TG"
```

## How the Daemon Handles USER: Messages

The daemon treats messages prefixed `USER:` differently from `A -> B:` messages:

```bash
# In daemon.sh, add this check before the claude --print call:
if echo "$MSG" | grep -q "^USER:"; then
  CLEAN="${MSG#USER: }"
  PROMPT="The user says: $CLEAN
You are $AGENT_B_NAME. Respond directly to the user.
Use [DONE:task] or [BLOCKED:task] if applicable. Under 100 words."
else
  PROMPT="$AGENT_A_NAME says: $MSG
..."
fi
```

## Multi-User Groups

To allow multiple users to message the daemon, change `WHITELIST_ID` to a comma-separated list:

```bash
WHITELIST="user_id_1,user_id_2"
# Then in the check:
if echo ",$WHITELIST," | grep -q ",$sender_id,"; then
  # Route to inbox
fi
```
