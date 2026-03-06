---
name: wallabag
description: Manage Wallabag bookmarks through the Wallabag Developer API with OAuth2 authentication, including creating, reading, updating, deleting, searching, and tag management. Use when a user wants to talk to Wallabag, store links, retrieve entries, filter by search or tags, or modify bookmark metadata.
---

# Wallabag

## Overview

Use this skill to operate a Wallabag instance through its API with deterministic shell commands. Keep credentials in environment variables and never hardcode secrets.

## Runtime Requirements

- Required binaries: `bash`, `curl`
- Required for `tag add` and `tag remove`: `jq`

## Required Environment

Set these variables before running commands:

- `WALLABAG_BASE_URL`
- `WALLABAG_CLIENT_ID`
- `WALLABAG_CLIENT_SECRET`
- `WALLABAG_USERNAME`
- `WALLABAG_PASSWORD`

Example:

```bash
export WALLABAG_BASE_URL="https://wallabag.example.com"
export WALLABAG_CLIENT_ID="..."
export WALLABAG_CLIENT_SECRET="..."
export WALLABAG_USERNAME="..."
export WALLABAG_PASSWORD="..."
```

## Command Interface

Main command:

```bash
scripts/wallabag.sh <subcommand> [options]
```

Subcommands:

- `auth [--show-token]`
- `list [--search <text>] [--tag <name>] [--archive 0|1] [--starred 0|1] [--page <n>] [--per-page <n>]`
- `get --id <entry_id>`
- `create --url <url> [--title <title>] [--tags "tag1,tag2"]`
- `update --id <entry_id> [--title <title>] [--tags "tag1,tag2"] [--archive 0|1] [--starred 0|1]`
- `delete --id <entry_id>`
- `tag add --id <entry_id> --tags "tag1,tag2"`
- `tag remove --id <entry_id> --tag "tag"`

## Workflow

1. Run `auth` to verify OAuth credentials.
2. Use `create` to add bookmarks.
3. Use `list` and `get` to retrieve bookmarks.
4. Use `update` or `tag` commands to adjust metadata.
5. Use `delete` only when removal is required.

## Operational Rules

- Keep tokens in process memory only. Do not persist token state to disk.
- `auth` does not print access tokens unless `--show-token` is explicitly passed.
- Return JSON output unchanged where possible.
- Emit actionable error messages on stderr and non-zero exit codes.
- Prefer `tag add` and `tag remove` when only tag mutation is needed.

## Example Prompts

- "Use $wallabag to save https://example.com with tags ai,read-later"
- "Use $wallabag to list starred entries tagged tech"
- "Use $wallabag to remove tag inbox from entry 123"

## References

Read API specifics from `references/wallabag-api.md` when endpoint details are needed.
