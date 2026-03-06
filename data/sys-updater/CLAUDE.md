# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

sys-updater is a system maintenance automation tool for Ubuntu hosts. It runs safe daily maintenance (security updates + upgrade simulations), tracks pending non-security updates for manual review, and generates Telegram reports in Russian.

**Design philosophy:** Conservative and safe. Security updates are applied automatically via `unattended-upgrade`, but non-security upgrades are never applied automatically—only tracked and reported.

## Commands

```bash
# Run 6am maintenance (apt update, security updates, simulation, track packages)
python3 scripts/apt_maint.py run_6am

# Generate 9am report (reads state from last run)
python3 scripts/apt_maint.py report_9am
```

No external dependencies—uses only Python stdlib. Requires sudo NOPASSWD for apt-get and unattended-upgrade.

## Architecture

Single-file implementation: `scripts/apt_maint.py` (~245 lines)

**Two-phase daily workflow:**
1. `run_6am` - Executes maintenance, saves state to JSON
2. `report_9am` - Renders human-readable Telegram report from saved state

**State files** (default: `state/apt/`):
- `last_run.json` - Results from latest run (RunResult dataclass)
- `tracked.json` - Package tracking metadata (firstSeenAt, reviewedAt, planned, blocked, note)

Override state directory via `SYS_UPDATER_STATE_DIR` environment variable.

**Key constraints:**
- No full-upgrade/dist-upgrade
- No autoremove
- Non-security upgrades are informational only (tracked but not applied)
