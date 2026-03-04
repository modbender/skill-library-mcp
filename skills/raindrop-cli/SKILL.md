---
name: raindrop-cli
description: Manage Raindrop.io bookmarks from the command line (search, exists, add, update, remove) using the Raindrop REST API. Use when automating bookmark capture and organization with a personal RAINDROP_TOKEN.
---

# Raindrop CLI

This skill provides `scripts/raindrop`.

## Auth

Set `RAINDROP_TOKEN` in a local env file (recommended: `~/.config/openclaw/gateway.env`, chmod 600).

## Safety defaults

- If a URL already exists, the tool reports it and does **not** create duplicates.
- If no collection is provided, it defaults to **Unsorted**.

## Usage

- `raindrop collections`
- `raindrop search "query" --collection all`
- `raindrop exists <url>`
- `raindrop add <url> --tags tag1,tag2 --collection unsorted`
- `raindrop update <id> --title "New title"`
- `raindrop remove <id>`
