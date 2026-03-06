# How sys-updater Works

## Overview

sys-updater is a two-phase daily workflow for safe system maintenance:

1. **06:00 MSK** - `run_6am`: Execute maintenance, save state
2. **09:00 MSK** - `report_9am`: Generate human-readable report from saved state

## Architecture

Single-file implementation: `scripts/apt_maint.py` (~300 lines, Python stdlib only)

```
┌─────────────────────────────────────────────────────────────────┐
│                        run_6am (06:00 MSK)                      │
├─────────────────────────────────────────────────────────────────┤
│  1. apt-get update          → refresh package lists            │
│  2. unattended-upgrade -d   → apply security updates           │
│  3. apt-get -s upgrade      → simulate (dry-run) full upgrade  │
│  4. apt list --upgradable   → list pending non-security pkgs   │
│  5. save state              → last_run.json, tracked.json      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    state/apt/last_run.json
                    state/apt/tracked.json
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                       report_9am (09:00)                        │
├─────────────────────────────────────────────────────────────────┤
│  1. load state files                                            │
│  2. render Telegram report (Russian)                            │
│  3. print to stdout (caller sends to Telegram)                  │
└─────────────────────────────────────────────────────────────────┘
```

## Key Constraints

| Constraint | Rationale |
|------------|-----------|
| No `dist-upgrade` / `full-upgrade` | Could break system with major version changes |
| No `autoremove` | Could remove packages needed by other software |
| Non-security upgrades NOT applied | Require manual review before applying |
| Security updates via `unattended-upgrade` | Official Ubuntu mechanism, well-tested |

## RunResult Dataclass

The core data structure saved after each run:

```python
@dataclass
class RunResult:
    ranAt: str              # ISO timestamp
    aptUpdateOk: bool       # apt-get update succeeded
    unattendedOk: bool      # unattended-upgrade succeeded
    simulatedOk: bool       # apt-get -s upgrade succeeded
    updatedPackages: list   # packages updated (from apt history)
    plannedApplied: list    # reserved for future (manual apply)
    securityNote: str|None  # last line from unattended-upgrade
    upgradable: list        # pending non-security packages
    simulateSummary: str    # e.g. "5 upgraded, 0 newly installed..."
```

## Package Tracking

`tracked.json` maintains metadata for each non-security package.

**Automatic cleanup:** Packages that are no longer upgradable (already upgraded or removed from repos) are automatically removed from tracking, unless they are marked as `blocked` or `planned` (indicating admin made a decision about them).

```json
{
  "createdAt": "2024-01-15T06:00:00Z",
  "items": {
    "package-name": {
      "firstSeenAt": "2024-01-15T06:00:00Z",
      "reviewedAt": null,
      "planned": false,
      "blocked": false,
      "note": null
    }
  }
}
```

- **firstSeenAt**: When package first appeared as upgradable
- **reviewedAt**: When admin reviewed (null = not reviewed)
- **planned**: Mark for future upgrade (informational only)
- **blocked**: Block from planned upgrades (known issues)
- **note**: Admin notes (e.g., "wait for v2.1 bug fix")
