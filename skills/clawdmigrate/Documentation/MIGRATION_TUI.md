# Migration TUI – Feature Tracking

## Overview

Interactive terminal UI for **clawd_migrate** that shows a lobster ASCII art on load and guides users through the migration process (discover -> backup -> migrate). Supports **moltbot or clawdbot** as source; works on any user's system (no machine-specific paths).

## Status

- **Added:** 2025-02-01
- **Entry points:** `python -m clawd_migrate` (no args) or `python -m clawd_migrate run`

## Features

| Feature | Status |
|--------|--------|
| Lobster ASCII art on load (red lobster + cyan “CLAWD MIGRATE” text) | Done |
| Welcome banner and tagline | Done |
| Choose working directory (default: cwd) | Done |
| Menu: Discover assets | Done |
| Menu: Create backup only | Done |
| Menu: Run full migration (backup first) | Done |
| Menu: Migrate without backup (with warning) | Done |
| Menu: Change working directory | Done |
| Menu: Quit | Done |
| ANSI colors (Windows Terminal / PowerShell 7+ / Unix) | Done |
| Feature doc in Documentation/ | Done |

## Usage

```bash
# Interactive mode (default)
python -m clawd_migrate

# Explicit interactive mode
python -m clawd_migrate run

# Existing CLI still works
python -m clawd_migrate discover [--root PATH]
python -m clawd_migrate backup [--root PATH] [--backup-dir PATH]
python -m clawd_migrate migrate [--root PATH] [--no-backup] [--output PATH]
```

## Files

- `tui.py` – TUI logic, lobster art, menu, discover/backup/migrate flows
- `__main__.py` – Wires no-args and `run` to TUI; keeps existing subcommands

## Notes

- Colors use ANSI escape codes; supported in Windows Terminal and modern PowerShell.
- Lobster art is ASCII-only for broad terminal compatibility.
