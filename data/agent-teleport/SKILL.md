---
name: agent-teleport
description: Seamlessly migrate your agent's configuration and memory to a new machine using TiDB Zero.
metadata:
  openclaw:
    emoji: 🛸
    requires:
      bins: ["python3", "curl"]
      env: ["TIDB_HOST", "TIDB_PORT", "TIDB_USER", "TIDB_PASSWORD"]
---

# Agent Teleport (Powered by TiDB Zero)

## Overview
**Agent Teleport** is a migration utility that allows your AI Agent to transfer its entire state (memory, configuration, and workspace files) from one machine to another instantly.

## Security & Provisioning
1.  **Bring Your Own Database (Recommended):** Set `TIDB_*` environment variables.
2.  **Auto-Provisioning (Fallback):** If no credentials are found, this skill uses the TiDB Zero API to create a temporary database for the transfer. The connection string is returned as the "Restore Code".

## Prerequisites
*   **Move freely:** Switch from your office desktop to your laptop without losing context.
*   **Backup:** Create an instant snapshot of your agent's brain before trying risky operations.
*   **Clone:** Duplicate your agent's configuration to a new instance.

## Prerequisites
This skill requires a TiDB Cloud account. The agent will automatically provision a free serverless cluster using the provided credentials.

*   **Environment Variables:**
    *   `TIDB_HOST`
    *   `TIDB_PORT`
    *   `TIDB_USER`
    *   `TIDB_PASSWORD`

## Usage

### 1. Pack (Source Machine)
To save your current state and generate a restore code:

```bash
python {baseDir}/run.py --action pack
```
**Output:** A connection string (DSN) or a short code.

### 2. Restore (Destination Machine)
To load the state on a new machine:

```bash
python {baseDir}/run.py --action restore --dsn "mysql+pymysql://..."
```

## Security Note
The temporary database created by this skill is **ephemeral**. It is recommended to delete the cluster after restoration if it contains sensitive data.
