# OpenClaw Deck Tracker

[![OpenClaw](https://img.shields.io/badge/OpenClaw-Skill-blue?style=flat-square)](https://github.com/openclaw/openclaw)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Track OpenClaw agent tasks on a [NextCloud Deck](https://apps.nextcloud.com/apps/deck) board.

This skill provides a robust CLI (`deck`) for AI agents to manage their own task lifecycle—from queue to completion—with support for persistent heartbeat monitoring, progress logging, and daily archiving.

## Features

- **Task Lifecycle Management:** Create, move, update, and archive cards.
- **Heartbeat Monitoring:** `deck monitor` spawns a background process to log "Still working..." updates every 60s and notify the user via chat every 120s (preventing "is it stuck?" anxiety).
- **Rich Logging:** Append timestamped progress updates to card descriptions.
- **Automated Hygiene:** Utilities to dump completed tasks for memory synthesis (`deck dump-done`) and archive them (`deck archive-done`).
- **AI-Native Protocols:** Includes specific guidance for LLMs on avoiding shell expansion issues with complex markdown.

## Installation

1. **Install via ClawHub (Recommended):**
   ```bash
   clawhub install deck-tracker
   ```

2. **Manual Installation:**
   Clone this repo into your OpenClaw skills directory:
   ```bash
   cd ~/.openclaw/workspace/skills
   git clone https://github.com/SkanderHelali/openclaw-deck-tracker deck-tracker
   ```

## Configuration

This skill requires connection details for your NextCloud instance.

**⚠️ SECURITY WARNING:** Never hardcode your password in scripts or command arguments. Use environment variables.

Add the following to your `~/.bashrc` or OpenClaw environment config:

```bash
# Connection Details
export DECK_URL="https://your-nextcloud.com/index.php/apps/deck/api/v1.0"
export DECK_USER="your_username"
export DECK_PASS="your_app_password"  # Create an App Password in NextCloud Security settings!
export BOARD_ID=1                     # The ID of the board to track

# Stack IDs (Optional - Defaults provided)
# Inspect your board via API or browser network tab to find these IDs
export STACK_QUEUE=1
export STACK_PROGRESS=2
export STACK_WAITING=3
export STACK_DONE=4
```

### Finding Stack IDs
You can list stacks on your board to find their IDs:
```bash
curl -u user:pass "https://cloud.example.com/index.php/apps/deck/api/v1.0/boards/1/stacks" | jq '.[] | {id, title}'
```

## Usage

### Basic Commands

```bash
# List all tasks
deck list

# Add a task (and optionally move to progress immediately)
deck add "Fix Backup Script" "Debug cron failure" --progress

# Move a task
deck move <id> done

# Update details
deck update <id> --title "New Title" --description "New Description"
```

### Advanced Workflows

**Background Monitoring:**
For long-running tasks, the agent should start a monitor. This updates the card every minute and pings the user every 2 minutes.
```bash
deck monitor <card_id>
```

**Rich Logging:**
Append a status update to the card description without overwriting it.
```bash
deck log <id> progress "Compiling binaries..."
```

**Daily Cleanup:**
Archive all cards in the "Done" stack (useful for nightly maintenance crons).
```bash
deck archive-done
```

## AI Agent Protocol

If you are an AI assistant using this tool, follow these rules:

1. **Check First:** Always run `deck list` before starting work to see if a task is already tracked.
2. **Track Everything:** `deck add ... --progress` is your first action for any user request.
3. **Safe Updates:** When writing complex markdown descriptions (with quotes, backticks, etc.), **ALWAYS** write to a temporary file first to avoid shell syntax errors:
   ```bash
   cat > /tmp/desc.txt << 'EOF'
   My complex *markdown* here.
   EOF
   deck update <id> --description "$(cat /tmp/desc.txt)"
   ```

## License

MIT
