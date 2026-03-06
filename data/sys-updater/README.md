# sys-updater

System maintenance automation for Ubuntu/OpenClaw hosts.

It runs safe daily maintenance, separates security patching from non-security upgrades, tracks package decisions (candidate/planned/blocked), performs risk-aware auto-review for npm/pnpm/brew, and generates clear 09:00 MSK Telegram reports with **what was actually installed**.

## Philosophy

**Conservative and safe.** Security updates are applied automatically via `unattended-upgrade`, but non-security upgrades are never applied automatically—only tracked and reported.

## Quick Start

```bash
# Run 6am maintenance (apt update, security updates, simulation, track packages)
python3 scripts/apt_maint.py run_6am

# Generate 9am report (reads state from last run)
python3 scripts/apt_maint.py report_9am

# Dry-run mode (test without executing sudo commands)
python3 scripts/apt_maint.py run_6am --dry-run

# Verbose mode (also log to console)
python3 scripts/apt_maint.py run_6am --verbose
```

## Requirements

- Python 3.10+ (stdlib only, no dependencies)
- Ubuntu with `unattended-upgrades` installed
- Sudo NOPASSWD for apt-get and unattended-upgrade (see [docs/sudoers.md](docs/sudoers.md))

## Directory Structure

```
sys-updater/
├── scripts/
│   └── apt_maint.py      # Main script (~300 lines)
├── state/
│   ├── apt/
│   │   ├── last_run.json # Results from latest run
│   │   └── tracked.json  # Package tracking metadata
│   └── logs/
│       ├── apt_maint.log          # Current log file
│       ├── apt_maint.log.YYYY-MM-DD # Rotated daily (UTC midnight), kept 10 days
│       └── cron.log              # Optional: stdout/stderr redirection
├── docs/                  # Documentation
├── CLAUDE.md             # Instructions for Claude Code
└── README.md
```

## Schedule

Default intended schedule (Europe/Moscow):
- **06:00 MSK** — `run_6am` (apt update + unattended-upgrade + simulation + tracking)
- **09:00 MSK** — `report_9am` (renders Telegram report from saved state)

In this setup, scheduling is typically done via **OpenClaw cron jobs** (see `openclaw cron list`).

## Documentation

- [How it Works](docs/how-it-works.md) - Architecture and workflow
- [Scheduling](docs/scheduling.md) - Cron setup
- [Sudoers Setup](docs/sudoers.md) - Required permissions
- [State Files](docs/state-files.md) - JSON schema reference
- [Logging](docs/logging.md) - Log format and location
- [Operations](docs/operations.md) - Disable, rollback, troubleshooting
- [Extending](docs/extending.md) - Adding providers (brew/npm/etc)

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SYS_UPDATER_BASE_DIR` | `/home/moltuser/clawd/sys-updater` | Base directory |
| `SYS_UPDATER_STATE_DIR` | `$BASE_DIR/state/apt` | State files location |
| `SYS_UPDATER_LOG_DIR` | `$BASE_DIR/state/logs` | Log files location |

## License

Internal tool, not for distribution.
