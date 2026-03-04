# CLI Command Reference

The `filewave` CLI provides a powerful interface for querying and managing your FileWave UEM environment.

## General Options

| Option | Description |
| :--- | :--- |
| `--profile` | Profile name (uses default if not specified) |
| `-h, --help` | Show help message and exit |

---

## Device Discovery & Search

### `filewave device-search`

Search for devices by name or serial number across the global API.

**Note:** Returns ALL matching results (partial matches allowed).

```bash
filewave device-search "iPad"
```

### `filewave find-devices`

Find all devices of a specific hardware product type. This uses a recursive search and type-identification logic (not just name matching).

**Supported Types:** `iPad`, `iPhone`, `iOS`, `Mac`, `Windows`, `Android`, `Chromebook`.

```bash
filewave find-devices iPad
filewave find-devices --format json iPhone
```

### `filewave device-details`

Show full device info including groups, clone status, and hardware summaries.

```bash
filewave device-details 34486
```

---

## Inventory Queries

### `filewave query`

Execute an Inventory Query and parse results into manageable objects.

```bash
# Basic query
filewave query --query-id 1

# Filter by last check-in (supports relative time)
filewave query --query-id 1 --filter "last_seen > 30 days"

# Export to JSON
filewave query --query-id 1 --format json --reference lab_data
```

---

## Fleet Management

### `filewave update-model`

Manually trigger a Model Update on the FileWave server to push pending changes to clients.

```bash
filewave update-model
```

### `filewave bulk-update`

Perform mass updates of device names and enrollment users (Auth Username) via CSV.

```bash
filewave bulk-update --csv ~/school_students.csv
```

### `filewave hierarchy`

Analyze a device's relationships, identifying its original record and all clone memberships across the group tree.

```bash
filewave hierarchy 213
```

---

## Setup & Maintenance

### `filewave setup`

Interactive onboarding for configuring server profiles and API tokens.

### `filewave insights`

Fleet-wide analytics including platform breakdown, stale device reports, and arbitrary field summaries. All operations are **read-only** and **non-destructive**.

```bash
# Basic platform breakdown
filewave insights

# Include stale device report (>30 days)
filewave insights --stale-days 30

# Group by any field
filewave insights --group-by OperatingSystem_edition

# Summary only (no version details)
filewave insights --summary-only

# JSON output
filewave insights --format json

# Use specific query and profile
filewave insights --query-id 2 --profile production
```

| Flag | Description | Default |
|------|-------------|---------|
| `--query-id` | Inventory Query ID | 1 |
| `--profile` | Server profile name | default |
| `--stale-days` | Include stale report (N days threshold) | disabled |
| `--group-by` | Count devices by any field | disabled |
| `--summary-only` | Platform totals only, skip versions | false |
| `--format` | `text` or `json` | text |

**Example Output:**

```
============================================================
Fleet Insights — [lab]
Server: support2.filewave.net
Query ID: 1
============================================================

Fleet Summary: 5 device(s)

  macOS: 5 (100%)
    • 26.3.0 (Tahoe): 2
    • 12.7.6 (Monterey): 1
    • 14.5 (Sonoma): 1
    • 15.1.0 (Sequoia): 1

────────────────────────────────────────────────────────────

Stale Device Report (>30 days)

  Active:  1
  Stale:   2
  Unknown: 2
  Total:   5

  Stale Devices:
    • C02PN3G1FVH8 - JoshL (last seen: 2025-12-27T05:12:02Z)
    • Josh Mac Studio 2022 (last seen: 2025-07-25T18:17:28Z)
```

**Supported Platforms:** macOS, iOS, iPadOS, Windows, Android, ChromeOS, tvOS, watchOS, Linux.

### `filewave cache-status`

View the status of the local device cache (used to speed up ID-to-serial lookups).

### `filewave warm-cache`

Pre-fetch all devices from the server into the local cache. This makes subsequent searches and lookups instant.

```bash
filewave warm-cache
# (Optional) fetch sequentially instead of parallel
filewave warm-cache --serial
```
