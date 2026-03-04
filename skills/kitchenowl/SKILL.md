---
name: kitchenowl-cli
description: Use kitchenowl-cli from terminal with pipx install, auth, and core read/write commands for KitchenOwl.
metadata: {"author":"KitchenOwl","homepage":"https://github.com/kitchenowl/kitchenowl-cli","openclaw":{"requires":{"anyBins":["kitchenowl"]},"install":["pipx install kitchenowl-cli"]}}
---

# KitchenOwl CLI Skill

Use this skill when the user wants to install and operate KitchenOwl via the `kitchenowl` CLI.

## Install and verify

Prefer `pipx` for isolated CLI installs.

```bash
pipx install kitchenowl-cli
kitchenowl --help
kitchenowl --version
```

Upgrade:

```bash
pipx upgrade kitchenowl-cli
```

## Authentication

```bash
kitchenowl auth login --server https://kitchenowl.example.com
kitchenowl auth status
kitchenowl auth logout
```

`auth login` accepts `--username` and `--password` flags (or prompts interactively) and always asks for the server when `--server` is omitted, defaulting to the last saved host. The CLI stores `server_url`, `access_token`, `refresh_token`, `user`, and any saved defaults in `~/.config/kitchenowl/config.json` (or `$XDG_CONFIG_HOME/kitchenowl/config.json`). `auth logout` removes the tokens from that file but leaves the configured server URL.

## Command usage rules

1. Start with read-only commands before mutating data.
2. Ask for confirmation before destructive commands (`delete`, `remove-item`, bulk edits).
3. Prefer explicit IDs and `--household-id` for all scoped commands.
4. Use `--json` whenever output is consumed programmatically.

## Core command groups

Use `references/commands.md` as the canonical command set for:
- auth
- config/server settings
- households and members
- shopping lists
- recipes
- users
