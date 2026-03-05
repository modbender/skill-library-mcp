---
name: strawpoll-cli
description: >
  Create and manage StrawPoll polls, meeting polls, and ranking polls from the terminal
  using the strawpoll CLI. Use when the user wants to create polls, view poll results,
  schedule meetings with availability, run ranked-choice votes, delete or update polls,
  or automate StrawPoll workflows in scripts.
license: MIT
homepage: https://github.com/dedene/strawpoll-cli
metadata:
  author: dedene
  version: "1.1.0"
  openclaw:
    primaryEnv: STRAWPOLL_API_KEY
    requires:
      bins:
        - strawpoll
    install:
      - kind: brew
        tap: dedene/tap
        formula: strawpoll
        bins: [strawpoll]
      - kind: go
        package: github.com/dedene/strawpoll-cli/cmd/strawpoll
        bins: [strawpoll]
---

# strawpoll-cli

Command-line interface for the [StrawPoll API v3](https://strawpoll.com/). Supports three poll types: multiple-choice, meeting (availability), and ranking.

## Installation

```bash
# Homebrew (macOS/Linux)
brew install dedene/tap/strawpoll

# Or via Go
go install github.com/dedene/strawpoll-cli/cmd/strawpoll@latest
```

## Authentication

An API key is required. Get one at [strawpoll.com/account/settings](https://strawpoll.com/account/settings).

```bash
# Store in system keyring (interactive prompt)
strawpoll auth set-key

# Or use environment variable (for scripts/CI)
export STRAWPOLL_API_KEY="your-key-here"

# Verify setup
strawpoll auth status
```

## Quick Start

```bash
# Create a poll
strawpoll poll create "Favorite language?" Go Rust Python TypeScript

# View poll details (accepts ID or full URL)
strawpoll poll get NPgxkzPqrn2
strawpoll poll get https://strawpoll.com/NPgxkzPqrn2

# View results with vote counts
strawpoll poll results NPgxkzPqrn2

# Delete (with confirmation)
strawpoll poll delete NPgxkzPqrn2
```

## Poll Types

### Multiple-Choice Polls

```bash
# Basic poll
strawpoll poll create "Best editor?" Vim Emacs "VS Code" Neovim

# With voting rules
strawpoll poll create "Pick up to 3" A B C D E \
  --is-multiple-choice --multiple-choice-max 3 \
  --dupcheck session --deadline 24h

# Private poll, copy URL to clipboard
strawpoll poll create "Team vote" Opt1 Opt2 --is-private --copy

# Open in browser after creation
strawpoll poll create "Quick poll" Yes No --open

# List your polls
strawpoll poll list --limit 10

# Update a poll
strawpoll poll update NPgxkzPqrn2 --title "New title" --add-option "New option"

# Reset votes (with confirmation)
strawpoll poll reset NPgxkzPqrn2
```

### Meeting Polls (Availability)

```bash
# With all-day dates
strawpoll meeting create "Team standup" \
  -d 2025-03-10 -d 2025-03-11 -d 2025-03-12

# With time ranges
strawpoll meeting create "1:1 meeting" \
  -r "2025-03-10 09:00-10:00" \
  -r "2025-03-10 14:00-15:00" \
  --tz "America/New_York" --location "Room 4B"

# Interactive wizard (no dates = launches wizard)
strawpoll meeting create "Sprint planning"

# View availability grid
strawpoll meeting results xYz123abc

# List meeting polls
strawpoll meeting list
```

### Ranking Polls

```bash
# Create ranking poll
strawpoll ranking create "Rank these frameworks" React Vue Svelte Angular Solid

# View Borda count results
strawpoll ranking results rAnK456

# Verbose: per-position breakdown
strawpoll ranking results rAnK456 --verbose

# List ranking polls
strawpoll ranking list
```

## Output Formats

All commands support three output modes:

```bash
# Default: colored table (human-readable)
strawpoll poll results NPgxkzPqrn2

# JSON: structured output for scripting
strawpoll poll results NPgxkzPqrn2 --json

# Plain: tab-separated values
strawpoll poll results NPgxkzPqrn2 --plain

# Disable colors (also respects NO_COLOR env var)
strawpoll poll results NPgxkzPqrn2 --no-color
```

### Scripting Examples

```bash
# Get poll ID from creation
POLL_ID=$(strawpoll poll create "Vote" A B --json | jq -r '.id')

# Pipe results
strawpoll poll results "$POLL_ID" --plain | cut -f1,3

# Delete without confirmation
strawpoll poll delete "$POLL_ID" --force

# Results with participant breakdown
strawpoll poll results "$POLL_ID" --participants --json
```

## Configuration Defaults

Save preferred settings to avoid repetitive flags:

```bash
# Set defaults
strawpoll config set dupcheck session
strawpoll config set results_visibility after_vote
strawpoll config set is_private true

# View config
strawpoll config show

# Config file location
strawpoll config path
```

Config stored at `~/.config/strawpoll/config.yaml`.

## Interactive Mode

Create commands launch an interactive wizard when run in a terminal without arguments:

```bash
# Launches wizard (poll title, options, settings)
strawpoll poll create

# Launches meeting wizard (dates, times, location)
strawpoll meeting create "Team sync"
```

Wizards render on stderr; data output goes to stdout. In non-TTY (pipes), provide all arguments via flags.

## Important Notes

- Poll options: minimum 2, maximum 30
- Poll IDs: accepts bare IDs or full URLs (with/without `https://`, `www.`, `/polls/`)
- Deadlines: RFC3339 (`2025-03-15T18:00:00Z`) or duration (`24h`, `1h30m`)
- Meeting dates: `YYYY-MM-DD` for all-day, `YYYY-MM-DD HH:MM-HH:MM` for time ranges
- Timezones: IANA format (e.g., `Europe/Berlin`, `America/New_York`)
- No voting endpoint — voting is browser-only via the poll URL

## Shell Completions

```bash
strawpoll completion bash > /etc/bash_completion.d/strawpoll
strawpoll completion zsh > "${fpath[1]}/_strawpoll"
strawpoll completion fish > ~/.config/fish/completions/strawpoll.fish
```

See [reference.md](reference.md) for complete flag reference for all commands.


## Installation

```bash
brew install dedene/tap/strawpoll
```
