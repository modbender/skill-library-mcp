---
name: are.na-claw
description: Simple CLI wrapper for the are.na API. Lists channels, adds blocks, watches feeds. No AI, no automation, no external integrations. Just API calls.
read_when:
  - Managing are.na channels and blocks via API
  - Listing channel contents
  - Adding images/links to channels
  - Watching channels for changes
metadata: {"clawdbot":{"emoji":"🪬","requires":{"bins":["curl","python3"]}}}
allowed-tools: Bash(arena:*) - No file writes, no exec beyond curl
---

# are.na-claw

Simple, transparent CLI for are.na API. No AI. No automation. No hidden features.

## What This Does

- Makes API calls to are.na
- Lists channels and blocks
- Adds images/links to channels  
- Watches channels for changes
- Switches between multiple accounts

## What This Does NOT Do

- ✗ AI-powered curation
- ✗ Automatic content discovery
- ✗ Cross-platform sync
- ✗ External integrations
- ✗ Image analysis or color extraction
- ✗ Scheduled automation

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/arena-claw ~/arena-claw

# Or copy just the arena script
cp arena-claw/arena ~/bin/arena
chmod +x ~/bin/arena

# Add to PATH (add to ~/.zshrc or ~/.bashrc)
export PATH="$HOME/bin:$PATH"
```

## Source Code

The CLI is a single Python script: `arena`

It uses only:
- `curl` for API calls
- `python3` for parsing
- Local files for token storage

No dependencies, no external imports.

## Authentication

**Your API token stays on your machine.**

Tokens are stored locally:
- Single account: `~/.arena_token`
- Multi-account: `~/.openclaw/.arena_tokens`

The skill never sends your tokens anywhere except to are.na API.

```bash
# Add your account
arena auth YOUR_API_TOKEN

# Or add named account
arena auth YOUR_API_TOKEN myaccount

# Switch accounts
arena switch myaccount

# List accounts
arena accounts
```

## Usage

```bash
# Check your account
arena me

# List your channels
arena channels

# Get channel contents
arena channel channel-name

# Add image to channel
arena add image https://example.com/image.jpg --channel my-channel

# Add link to channel  
arena add link https://example.com --channel my-channel --title "Example"

# Watch for new items
arena watch channel-name --interval 60

# Search channels
arena search glitch

# Create channel
arena create "my-channel"
```

## Multi-Account

```bash
# Add multiple accounts
arena auth TOKEN1 account1
arena auth TOKEN2 account2

# Use specific account
arena -a account1 me
arena -a account2 channel shared-channel

# Switch default account
arena switch account1
```

## Commands

| Command | Description |
|---------|-------------|
| `arena auth <token> [name]` | Add API token |
| `arena accounts` | List configured accounts |
| `arena switch <name>` | Switch default account |
| `arena me` | Show current user |
| `arena channels [user]` | List channels |
| `arena channel <slug>` | Get channel contents |
| `arena add <type> <url> --channel <name>` | Add block to channel |
| `arena watch <slug>` | Watch for changes |
| `arena search <query>` | Search channels |
| `arena create <title>` | Create new channel |
| `arena trending` | Search trending |
| `arena explore <keywords>` | Search by keywords |
| `arena analyze <slug>` | Count block types |
| `arena doctor` | Debug connection |

## Security

- **No credential harvesting** - Tokens stored only in your home directory
- **No external calls** - Only talks to api.are.na
- **No data exfiltration** - All data stays local
- **No automatic execution** - Every command is explicit
- **No dependencies** - Only curl and shell built-ins

## Uninstall

```bash
rm -rf ~/arena-claw
rm ~/.arena_token ~/.openclaw/.arena_tokens
```

## No Warranty

This is a simple wrapper. Use at your own risk. Always verify what commands do before running them.
