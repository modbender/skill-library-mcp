---
name: deck-tracker
version: 0.1.1
description: Track OpenClaw tasks on NextCloud Deck board. Auto-add tasks to Queue, move through states.
metadata:
  openclaw:
    emoji: "📋"
---

# Deck Tracker v1.0.0

Track tasks on a NextCloud Deck board.

## Board Structure

This skill assumes a board with 4 stacks (columns):

| Stack | Default ID | Purpose |
|-------|------------|---------|
| Queue | 1 | New incoming tasks |
| In Progress | 2 | Currently working on |
| Waiting | 3 | Blocked/waiting for user |
| Done Today | 4 | Completed tasks |

## Configuration

Set the following environment variables (e.g. in your `.bashrc` or OpenClaw config):

```bash
export DECK_URL="https://your-nextcloud.com/index.php/apps/deck/api/v1.0"
export DECK_USER="your_username"
export DECK_PASS="your_app_password" # Use an App Password!
export BOARD_ID=1
```

If your stack IDs differ from the defaults (1, 2, 3, 4), override them:

```bash
export STACK_QUEUE=10
export STACK_PROGRESS=11
export STACK_WAITING=12
export STACK_DONE=13
```

## Commands

### List all cards on the board

```bash
deck list
```

### Add a new task to Queue

```bash
deck add "Task title" "Optional description"
```
**Options:**
- `--progress`: Automatically move the new card to "In Progress" immediately.
- `--stack <id>`: Create in a specific stack ID (default: Queue).

Example with auto-start:
```bash
deck add "Urgent Fix" "Fixing production bug" --progress
```

### Move a card to a different stack

```bash
deck move <card_id> <queue|progress|waiting|done>
```

### Get card details

```bash
deck get <card_id>
```

### Update card title/description

```bash
deck update <card_id> [--title "New title"] [--description "New desc"]
```

### Log a status update to a card

```bash
deck log <card_id> <status> "Message"
```
**Statuses:** `progress`, `success`, `error`, `warning`, `info`.

### Start automated heartbeat monitoring

```bash
deck monitor <card_id> [target_id]
```
Spawns a background process that appends a "Still working..." log entry every 60 seconds. Additionally, it sends a chat notification to the specified `target_id` (defaults to Skander) every 120 seconds. The process terminates automatically when the card is moved out of the "In Progress" stack (to Done or Waiting). Use for tasks expected to take >2 minutes.

### Dump all completed tasks as JSON

```bash
deck dump-done
```
Outputs the JSON payload for all cards in "Done Today". Useful for memory synthesis.

### Archive all completed cards

```bash
deck archive-done
```

Moves all cards in "Done Today" to the archived state. Useful for daily cleanup via cron.

### Delete a card

```bash
deck delete <card_id>
```

## Workflow & Memory Protocol

1. **New task arrives** → `deck add "Title" "Rich Initial Description"` (Use `--progress` to start immediately).
2. **Detailed Descriptions:** Start descriptions with **Objective**, **Plan**, and **Constraints**.
3. **Log updates** → `deck log <id> progress "Finished step 1"`.
4. **Closing Task:** Use `deck update <id> --description "Rich Summary"` to include **Technical Summary**, **Operations Performed**, and **Outcome**.
5. **Memory Synthesis:** Before archiving, use `deck dump-done` to parse the day's work and reinforce long-term memory.
6. **Daily cleanup** → `deck archive-done`.

### 🚨 AI Protocol: Complex Descriptions

When updating cards with multi-line markdown descriptions, ALWAYS use the **temp file method** to prevent shell expansion errors:

```bash
# 1. Write rich description to temp file
cat > /tmp/deck_desc_<id>.txt << 'EOF'
[Rich Markdown]
EOF

# 2. Update deck using the temp file
deck update <id> --description "$(cat /tmp/deck_desc_<id>.txt)"
```
