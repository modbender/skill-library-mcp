# State Files

All state is stored in JSON files under `state/apt/` (configurable via `SYS_UPDATER_STATE_DIR`).

## last_run.json

Results from the most recent `run_6am` execution.

```json
{
  "ranAt": "2024-01-15T06:00:05Z",
  "aptUpdateOk": true,
  "unattendedOk": true,
  "simulatedOk": true,
  "updatedPackages": ["openssl", "libssl3"],
  "plannedApplied": [],
  "securityNote": "All upgrades installed",
  "upgradable": ["nodejs", "npm", "docker-ce"],
  "simulateSummary": "3 upgraded, 0 newly installed, 0 to remove and 0 not upgraded."
}
```

| Field | Type | Description |
|-------|------|-------------|
| `ranAt` | string | ISO 8601 timestamp (UTC) |
| `aptUpdateOk` | bool | `apt-get update` succeeded |
| `unattendedOk` | bool | `unattended-upgrade` succeeded |
| `simulatedOk` | bool | `apt-get -s upgrade` succeeded |
| `updatedPackages` | string[] | Packages updated (from apt history) |
| `plannedApplied` | string[] | Reserved for future manual apply feature |
| `securityNote` | string? | Last line from unattended-upgrade output |
| `upgradable` | string[] | Pending non-security packages |
| `simulateSummary` | string | Summary line from simulation |

## tracked.json

Long-term tracking metadata for non-security packages.

```json
{
  "createdAt": "2024-01-10T06:00:00Z",
  "items": {
    "nodejs": {
      "firstSeenAt": "2024-01-10T06:00:00Z",
      "reviewedAt": "2024-01-12T10:30:00Z",
      "planned": true,
      "blocked": false,
      "note": "Reviewed changelog, safe to upgrade"
    },
    "docker-ce": {
      "firstSeenAt": "2024-01-14T06:00:00Z",
      "reviewedAt": null,
      "planned": false,
      "blocked": false,
      "note": null
    },
    "php8.1": {
      "firstSeenAt": "2024-01-08T06:00:00Z",
      "reviewedAt": "2024-01-09T11:00:00Z",
      "planned": false,
      "blocked": true,
      "note": "Known regression in 8.1.27, wait for 8.1.28"
    }
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `createdAt` | string | When tracking file was created |
| `items` | object | Map of package name → metadata |
| `items.*.firstSeenAt` | string | When package first appeared as upgradable |
| `items.*.reviewedAt` | string? | When admin reviewed (null = not reviewed) |
| `items.*.planned` | bool | Marked for future upgrade |
| `items.*.blocked` | bool | Blocked due to known issues |
| `items.*.note` | string? | Admin notes |

## Manual Editing

You can edit `tracked.json` manually to:

- Mark packages as reviewed: set `reviewedAt` to current timestamp
- Plan upgrades: set `planned: true`
- Block risky packages: set `blocked: true`, add `note`

Example workflow:

```bash
# Edit tracked.json
vim state/apt/tracked.json

# Re-run report to see changes
python3 scripts/apt_maint.py report_9am
```
