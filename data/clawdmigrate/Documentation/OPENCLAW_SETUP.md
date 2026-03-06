# Openclaw setup after migration

## Overview

Migration **only copies your files** into the openclaw layout (`memory/`, `.config/openclaw/`, `.config/clawdbook/`, `projects/`). It does **not** install the openclaw app. To install openclaw and register the migrated directory as an openclaw workspace, use the post-migration setup.

## Flow

1. **Migrate** – clawd-migrate copies your moltbot/clawdbot assets into the openclaw layout in the target directory.
2. **Install openclaw** – `npm i -g openclaw` (global install).
3. **Onboard** – `openclaw onboard` run in the migrated directory so openclaw sets up that folder with your existing files in place and adds any new structure.

Your files are already in the right places; openclaw onboard makes the directory a proper openclaw workspace and merges seamlessly with what migration put there.

## How to run setup

### Interactive (TUI)

After a successful migration, you’ll be prompted:

**Install openclaw and run openclaw onboard in this directory? [Y/n]:**

Answer **Y** (or press Enter) to run `npm i -g openclaw` and then `openclaw onboard` in the migrated directory.

### CLI

```bash
clawd-migrate migrate --root ~/my-bot --setup-openclaw
```

Same as above: after migration, the tool runs `npm i -g openclaw` and `openclaw onboard` in the output directory (default: same as `--root`).

### Manual

You can also do it yourself after migration:

```bash
npm i -g openclaw
cd /path/to/migrated/directory
openclaw onboard
```

## Requirements

- **Node.js** and **npm** on PATH (for `npm i -g openclaw`).
- **openclaw** will be on PATH after global install (for `openclaw onboard`).

## Files

- `openclaw_setup.py` – `install_openclaw_global()`, `run_openclaw_onboard()`, `install_openclaw_and_onboard()`.
- Wired from `tui.py` (post-migration prompt) and `__main__.py` (`--setup-openclaw`).
