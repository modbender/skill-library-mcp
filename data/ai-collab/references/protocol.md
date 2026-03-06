# ai-collab Message Protocol Reference

## Message Tags

| Tag | Usage | Example |
|-----|-------|---------|
| `[TASK:name]` | Assign a named task | `[TASK:price-check] Get BTC from CoinGecko` |
| `[ACK:name]` | Acknowledge receipt | `[ACK:price-check] On it.` |
| `[DONE:name]` | Task complete + result | `[DONE:price-check] BTC $94,230 as of 03:15 UTC` |
| `[BLOCKED:name]` | Can't complete + why | `[BLOCKED:price-check] CoinGecko 429 rate limit` |
| `[HANDOFF:name]` | Full ownership transfer | `[HANDOFF:report] Write summary to report.md. Reply [DONE:report] when done.` |
| `[STATUS:name]` | Mid-task progress update | `[STATUS:report] 50% done, on section 3` |
| `[QUESTION:topic]` | Need info to proceed | `[QUESTION:auth] Which API key should I use for Kraken?` |
| `[DEPIN-HEALTH]` | Cron health check | `[DEPIN-HEALTH] grass=native:up nodepay=ext:up` |

## Protocol Rules

1. **Answer before asking.** If you receive a `[QUESTION:]`, answer it before sending a new task.
2. **One task at a time.** Close current task before opening a new one (exceptions: parallel tasks where both agents know they're running concurrently).
3. **No hanging threads.** Every `[TASK:]` gets either `[DONE:]` or `[BLOCKED:]`. No silent drops.
4. **Result on close.** `[DONE:name]` always includes the result in one line. Not just "Done."
5. **Reason on block.** `[BLOCKED:name]` always includes why. Include retry suggestion if obvious.

## Bad vs Good Examples

**Bad:**
```
A → B: Check on the trading bot
B → A: I'll look into that and let you know when I find something.
```

**Good:**
```
A → B: [TASK:bot-check] Get trading bot PID and last 5 log lines from bot.log
B → A: [ACK:bot-check] Checking.
B → A: [DONE:bot-check] PID 130815 running. Last entry: "SL hit at -0.82% — cooling down 60s"
```

## chat.log Line Format

```
YYYY-MM-DD HH:MM:SS SENDER -> RECEIVER: message
```

Examples:
```
2026-02-22 03:15:44 JIM -> CLAWDY: [TASK:price-check] BTC price
2026-02-22 03:15:46 CLAWDY -> JIM: [DONE:price-check] BTC $94,230
2026-02-22 03:30:00 SYSTEM: Cron fired depin_health.sh
2026-02-22 03:30:01 CLAWDY -> JIM: [DEPIN-HEALTH] grass=native:up nodepay=ext:up
2026-02-22 04:00:00 JEREMY -> TEAM: pause the bot overnight
```

## Sender Prefixes

| Prefix | Source |
|--------|--------|
| `A -> B:` | Primary agent to daemon |
| `B -> A:` | Daemon to primary agent |
| `SYSTEM:` | Daemon startup/shutdown, cron events |
| `JEREMY ->` | User message (via Telegram bridge or direct) |

## Inbox File Naming

Files in `collab/inbox/` must use atomic write pattern:
```bash
# Correct:
TMPFILE=$(mktemp "$INBOX/.msg.XXXXXX")
echo "$MSG" > "$TMPFILE"
mv "$TMPFILE" "$INBOX/msg_$(date +%s%N).txt"

# Wrong (partial reads possible):
echo "$MSG" > "$INBOX/message.txt"
```

inotifywait fires on `moved_to` event, not `close_write` — the `mv` is the trigger.
