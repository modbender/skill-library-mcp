---
name: black-box
description: Indestructible audit logs for agent actions, stored in TiDB Zero.
metadata:
  openclaw:
    emoji: 📦
    requires:
      bins: ["python3", "curl"]
      env: ["TIDB_HOST", "TIDB_PORT", "TIDB_USER", "TIDB_PASSWORD"]
---

# Black Box (Powered by TiDB Zero)

## Overview
**Black Box** is an indestructible audit log for AI Agents. It acts as a "Flight Data Recorder" that streams critical actions, errors, and reasoning chains to a persistent cloud database (TiDB Zero) in real-time.

## Security & Provisioning
1.  **Bring Your Own Database (Recommended):** Set `TIDB_*` environment variables.
2.  **Auto-Provisioning (Fallback):** If no credentials are found, this skill uses the TiDB Zero API to create a temporary database for logging. The connection string is cached in `~/.openclaw_black_box_dsn`.

## Why use this?
*   **Crash Survival:** Local logs vanish when containers crash. Cloud logs persist.
*   **Audit Trail:** Prove exactly what your agent did and why (compliance).
*   **Debugging:** Retrieve the last 100 actions leading up to a failure.

## Prerequisites
*   **TiDB Credentials:** Standard MySQL connection parameters (`TIDB_HOST`, `TIDB_USER`, etc.).
*   **Network:** Outbound access to TiDB Cloud (port 4000).

## Usage

### 1. Log an Event
Record a critical action or error:

```bash
python {baseDir}/run.py --action log --level ERROR --message "System crash imminent: Memory leak detected"
```

### 2. Read Logs
Retrieve the last N logs (default: 10):

```bash
python {baseDir}/run.py --action read --limit 20
```

## Schema
This skill creates a table `agent_logs` with columns: `timestamp`, `level`, `message`, `metadata` (JSON).
