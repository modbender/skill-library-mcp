# OpenClaw flomo Skill (Read + Write)

[English](README.md) | [中文](README.zh-CN.md)

This folder is a shareable OpenClaw skill that can **read and write flomo memos on macOS**.

## What's New (2026-02-11)

- Improved read reliability for sparse tags/keywords:
  - `read --remote` now auto-expands the query window (`1d -> 7d -> 30d -> 180d -> 365d -> 5y`) until enough results are found.
- Added first-class tag filter:
  - `read --tag "xxx"` for exact tag intent.
  - `read --query "#xxx"` is also treated as tag query for backward compatibility.
- Added tag diagnostics:
  - `read --dump-tags --limit N` returns top tags with counts, to quickly verify how many memos are available per tag.
- Sorting and truncation behavior is stabilized:
  - Results are sorted by `updated_at` (then `created_at`) descending before applying `--limit`.
- `FLOMO_SINCE_SECONDS` behavior changed:
  - `0` (default) means auto-expand window.
  - `>0` forces a fixed query window.

## What It Does

- **Read**: fetch recent memos via flomo's API (`/api/v1/memo/updated/`) using your local flomo desktop login state.
- **Write**: create memos via flomo **incoming webhook** (`https://flomoapp.com/iwh...`).
- **Verify**: end-to-end check (remote read + webhook write + readback hit).

## Requirements

- macOS
- flomo desktop app installed and **logged in**
- `curl` available
- OpenClaw (optional, but recommended)

## Security Model (Important)

- This skill **does not include** your `access_token` or your `incoming webhook` URL.
- The script reads your local flomo app config on *your machine* (default path):
  - `~/Library/Containers/com.flomoapp.m/Data/Library/Application Support/flomo/config.json`
- The script fetches your incoming webhook path from flomo API on-demand.
- Do **not** share your local flomo `config.json` with anyone.

## Install (OpenClaw)

1. Copy this folder to the OpenClaw workspace skills directory:

```bash
mkdir -p ~/.openclaw/workspace/skills/flomo
rsync -a --delete ./openclaw-flomo-skill/ ~/.openclaw/workspace/skills/flomo/
```

2. Confirm OpenClaw sees the skill:

```bash
openclaw skills info flomo
```

## Usage (Standalone)

From the skill folder:

- Read (remote API, auto-expands time window by default):

```bash
python3 scripts/flomo_tool.py read --remote --limit 20
```

- Search recent memos:

```bash
python3 scripts/flomo_tool.py read --remote --limit 100 --query "keyword"
```

- Read by tag:

```bash
python3 scripts/flomo_tool.py read --remote --limit 10 --tag "diary"
```

- Dump top tags:

```bash
python3 scripts/flomo_tool.py read --dump-tags --limit 20
```

- Write a memo (auto-resolve webhook):

```bash
python3 scripts/flomo_tool.py write --content "hello from script"
```

- End-to-end verify:

```bash
python3 scripts/flomo_tool.py verify --try-webhook
```

## Configuration (Optional)

Environment variables you can set:

- `FLOMO_CONFIG_PATH`: override local flomo config path
- `FLOMO_ACCESS_TOKEN`: override access token (not recommended; prefer local flomo login)
- `FLOMO_APP_VERSION`: override app version
- `FLOMO_SIGN_SECRET`: override sign secret (only if flomo changes)
- `FLOMO_API_BASE`: override API base (default `https://flomoapp.com/api/v1`)
- `FLOMO_TZ`: timezone offset (default `8:0`)
- `FLOMO_SINCE_SECONDS`: force fixed remote cursor window (when unset/0, script auto-expands window)

## Troubleshooting

- If read returns too few results, force a larger fixed cursor window:

```bash
FLOMO_SINCE_SECONDS=604800 python3 scripts/flomo_tool.py read --remote --limit 100
```

- If write fails, check you are logged into flomo desktop app and can open flomo normally.
