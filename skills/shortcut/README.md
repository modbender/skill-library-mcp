# Shortcut Skill for OpenClaw

Manage stories on Shortcut.com kanban boards directly from your OpenClaw agent.

## Features

- **List stories** - View active, completed, or all stories on your board
- **Create stories** - Add new tasks with descriptions and types (feature/bug/chore)
- **Update stories** - Change story status and descriptions

## Installation

```bash
# Install via OpenClaw skills system
openclaw skills install shortcut
```

Or manually:
1. Download `shortcut.skill` from releases
2. Place in your OpenClaw skills directory
3. Restart OpenClaw gateway

## Prerequisites

- Shortcut.com account with API access
- API token from Shortcut.com (Settings → API Tokens)
- Token must have permissions for the workspace(s) you want to manage

## Usage

Once installed, your OpenClaw agent can handle requests like:

- "Add a story to the board: Fix login bug"
- "Show me active stories on Shortcut"
- "Mark story #38 as started"

## Scripts

The skill includes three bash scripts:

- `shortcut-list-stories.sh` - List stories with filters
- `shortcut-create-story.sh` - Create new stories
- `shortcut-update-story.sh` - Update existing stories

All scripts use the Shortcut API v3.

## Configuration

1. Store your Shortcut API token:
   ```bash
   echo "your-token" > ~/.config/shortcut/api-token
   chmod 600 ~/.config/shortcut/api-token
   ```

2. Initialize workflow states for your workspace:
   ```bash
   scripts/shortcut-init-workflow.sh
   ```

This will auto-detect your workspace's workflow state IDs and save them to `~/.config/shortcut/workflow-states`.

## License

MIT

## Author

@catwalksophie
