---
name: gmail-inbox-zero
description: Gmail Inbox Zero Triage - Interactive inbox management using gog CLI with Telegram buttons. Use when the user wants to achieve inbox zero, triage their Gmail inbox interactively, process ALL inbox messages (read and unread) with AI summaries and batch actions (archive, filter, unsubscribe). OAuth-based, no passwords needed.
---

# Gmail Inbox Zero Triage

Achieve inbox zero with AI-powered email triage! Process ALL Gmail inbox messages interactively with summaries and batch actions using OAuth (no passwords needed).

## Features

✅ **OAuth-based** - No passwords, secure authentication via gog  
✅ **AI summaries** - Quick 1-line summary of each email  
✅ **Batch processing** - Queue actions instantly, execute at the end  
✅ **Telegram buttons** - Archive, Filter, Unsubscribe, View  
✅ **Inbox zero focus** - Process ALL inbox messages (read + unread)  
✅ **Fast workflow** - No waiting between actions

## Workflow

1. **User triggers:** "Triage my emails" or "Process my inbox"
2. **Fetch ALL inbox messages** from Gmail (up to 20 at a time)
3. **Display all emails at once** with:
   - Subject and sender
   - AI-generated summary (1 line)
   - Telegram inline buttons for actions
4. **User clicks actions** for each email (queued instantly, no API calls yet)
5. **User clicks "Done"** button to execute all queued actions in batch
6. **Repeat until inbox zero!** 🎯

## Prerequisites

**Requires:** `gog` CLI with authenticated Gmail account.

Check if already set up:
```bash
gog auth list
```

If not set up, user needs to run `gog auth add` (see gog skill for OAuth setup).

Set environment variable for keyring password:
```bash
export GOG_KEYRING_PASSWORD="your-password"
```

## Telegram Button Layout

Each email displays with 4 action buttons:

```
[📥 Archive] [🔍 Filter]
[🚫 Unsub]   [📧 View]
```

- **📥 Archive** - Remove from inbox, mark as read
- **🔍 Filter** - Create filter to auto-archive future emails from sender
- **🚫 Unsubscribe** - Find and open unsubscribe link
- **📧 View** - Show full email content
- **No click** = Skip (leave in inbox)

At the end:
```
[✅ Done - Execute All Actions]
```

## Action Queue System

Actions are queued using short callback codes to avoid Telegram's 64-char limit:

- `q:a:0` = queue archive, message index 0
- `q:f:0` = queue filter, message index 0  
- `q:u:0` = queue unsubscribe, message index 0
- `q:v:0` = view full email, message index 0 (executes immediately)
- `q:done` = execute all queued actions

Queue is managed via `scripts/queue_manager.py` and stored in `action_queue.json`.

## Scripts

### gog_processor.py

Main processor for Gmail operations via gog CLI.

**List inbox messages:**
```bash
python3 scripts/gog_processor.py list <account> [limit]
```

**Archive a message:**
```bash
python3 scripts/gog_processor.py archive <account> <msg_id>
```

**Find unsubscribe link:**
```bash
python3 scripts/gog_processor.py unsubscribe <account> <msg_id>
```

**Create filter:**
```bash
python3 scripts/gog_processor.py filter <account> "<from_header>"
```

**Get message body:**
```bash
python3 scripts/gog_processor.py body <account> <msg_id>
```

### queue_manager.py

Manages action queue for batch execution.

**Add action to queue:**
```bash
python3 scripts/queue_manager.py add <action> <msg_id> [from_header]
```

**Get queue:**
```bash
python3 scripts/queue_manager.py get
```

**Clear queue:**
```bash
python3 scripts/queue_manager.py clear
```

### execute_queue.py

Executes all queued actions in batch.

```bash
python3 scripts/execute_queue.py <account>
```

Returns JSON with results of all executed actions.

## Implementation Steps

1. **Load current batch:** Fetch inbox messages and save to `current_batch.json`
2. **Display all emails:** Show each with summary and buttons
3. **Handle button callbacks:**
   - Archive/Filter/Unsub: Add to queue via `queue_manager.py`
   - View: Fetch and display full email immediately
   - Done: Execute queue via `execute_queue.py`
4. **Show results:** Report archived count and remaining inbox count
5. **Repeat if needed:** Fetch next batch or celebrate inbox zero

## AI Summary Guidelines

Generate concise 1-line summaries:

- **Receipts/Invoices:** "Payment receipt for $X. Financial record."
- **Security alerts:** "Security notification about [action]. [Important/Standard] alert."
- **Newsletters:** "Newsletter about [topic]. No action required."
- **Calendar:** "Calendar [event type] for [date/time]."
- **Legal:** "Legal [document type]. [Brief context]."

Keep it simple, factual, and action-oriented.

## Security Notes

- **OAuth-based authentication** - No passwords needed, uses gog's OAuth tokens
- **Tokens stored securely** by gog CLI in system keychain
- **Read/modify permissions** - gog only gets access to what user grants
- **Queue stored locally** - Action queue is temporary, cleared after execution

## Error Handling

Common issues:
- **gog not authenticated:** Run `gog auth add <account>`
- **Account not found:** Check `gog auth list` for available accounts
- **No inbox messages:** Success state - inbox zero achieved!
- **Permission denied:** User may need to re-authenticate with gog
- **Keyring password:** Set `GOG_KEYRING_PASSWORD` environment variable

## Dependencies

- **gog CLI** - Must be installed and authenticated (see gog skill)
- **Python 3** - Standard library only (subprocess, json, re, pathlib)

No additional pip packages needed.

## Tips for Best Experience

- **Process regularly:** Triage inbox daily to maintain inbox zero
- **Use filters liberally:** Auto-archive recurring newsletters and notifications
- **Archive aggressively:** If you don't need it now, archive it (searchable in All Mail)
- **Batch mode is fast:** Process 10-20 emails in under a minute
- **Trust the summaries:** AI summaries are accurate for quick decisions
