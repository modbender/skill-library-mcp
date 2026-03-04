# skill-auto-attach

## Description
This skill monitors the OpenClaw workspace for file changes and automatically attaches new or updated documentation files to Telegram messages instead of displaying code snippets.

## Features
- Detects file creation and modification events in workspace
- Copies files to /tmp for Telegram compatibility
- Sends files via message tool with filePath parameter
- Works with .html, .md, .txt files
- Silent operation unless file is updated

## Usage
1. Install the skill files in ~/.openclaw/skills/skill-auto-attach
2. Enable with `openclaw skills enable skill-auto-attach`
3. The skill will automatically attach files to Telegram messages when they are created/updated

## Requirements
- OpenClaw v2026.2+
- Telegram channel access
- `message` tool available

## Implementation
- Watches workspace directory
- Copies files to /tmp
- Sends via message tool
- Uses unique filenames to avoid conflicts

## Known Issues
- Only works with Telegram (other channels require config changes)
- May need adjust /tmp path on low-storage devices