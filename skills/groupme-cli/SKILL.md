---
name: groupme-cli
description: Send and read GroupMe messages via the groupme CLI. Use when asked to list groups, read messages, send messages to groups, or manage GroupMe direct messages from the command line.
metadata:
  {
    "openclaw":
      {
        "requires":
          {
            "bins": ["groupme"],
            "env": ["GROUPME_TOKEN"],
          },
        "primaryEnv": "GROUPME_TOKEN",
        "install":
          [
            {
              "id": "source",
              "kind": "source",
              "repo": "https://github.com/cuuush/groupme-cli",
              "bins": ["groupme"],
              "label": "Install groupme-cli (from source)",
              "notes": "Bundles to a single JS file via esbuild (git clone + npm install + npm run bundle + npm link). No separate build step needed — esbuild produces a self-contained dist/groupme-cli.js. Review package.json scripts before running on sensitive systems.",
            },
          ],
      },
  }
---

# GroupMe CLI

Send and read GroupMe messages from the command line using the `groupme` CLI.

## Setup

### Installation

```bash
git clone https://github.com/cuuush/groupme-cli
cd groupme-cli
npm install
npm run bundle
npm link
```

> **Note:** `npm run bundle` uses [esbuild](https://esbuild.github.io/) to produce a single self-contained file at `dist/groupme-cli.js`. No separate TypeScript compilation step needed — just install, bundle, and link.

### Authentication

Get your GroupMe API token from [dev.groupme.com](https://dev.groupme.com/) → Access Token, then configure:

```bash
groupme config --token YOUR_ACCESS_TOKEN
```

Or use the `GROUPME_TOKEN` environment variable, or pass `--token` to any command.

## Core Commands

### List Groups

```bash
groupme groups
groupme groups --json
```

### Read Messages

```bash
# Latest messages from a group
groupme read --group GROUP_ID

# More messages
groupme read --group GROUP_ID --limit 50

# Paginate older messages
groupme read --group GROUP_ID --before MESSAGE_ID

# JSON output
groupme read --group GROUP_ID --json
```

### Send a Message

```bash
groupme send --group GROUP_ID --message "Hello!"
```

### Direct Messages

```bash
# Read DMs
groupme dm-read --user USER_ID

# Send a DM
groupme dm --user USER_ID --message "Hey!"
```

### List DM Conversations

```bash
groupme chats
groupme chats --page 2 --per-page 10
```

### Current User Info

```bash
groupme me
```

## Fuzzy Group Search

Groups support fuzzy name matching — you can use partial names when referencing groups in commands.

## Global Options

- `--token <token>` — Override configured token
- `--json` — Machine-readable JSON output
- `--help` — Show help

## Tips

- Run `groupme groups --json` to get GROUP_IDs for use in other commands
- Use `--json` output to pipe into other tools or for scripting
- Config is stored at `~/.config/groupme/config.json`
