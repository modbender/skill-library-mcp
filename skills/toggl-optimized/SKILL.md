---
name: Toggl-Optimized
description: A high-performance Toggl Track agent skill optimized for token
  efficiency and reporting.
---

# Toggl-Optimized

A high-performance Toggl Track agent skill optimized for token efficiency and reporting.

## Overview

This skill provides a streamlined way to interact with Toggl Track, focusing on minimizing context usage and providing fast reporting capabilities via direct API v3 calls.

## Features

- **Token Efficient:** Uses optimized API calls to reduce LLM context consumption.
- **Fast Reporting:** Includes a shell script for quick JSON and PDF reports.
- **Direct API Access:** Examples for direct `curl` interaction with Toggl v3 Reports.

## Setup

1. Get your API Token from [Toggl Profile Settings](https://track.toggl.com/profile).
2. Set the environment variable:
   ```bash
   export TOGGL_API_TOKEN="your-api-token"
   ```
3. (Optional) Set your Workspace ID:
   ```bash
   export TOGGL_WORKSPACE_ID="your-workspace-id"
   ```

## Usage

### Optimized Reporting Script

Use the provided script for fast summaries:
```bash
# Usage: bash scripts/toggl_report.sh <client_name> <start_date> <end_date> <format: json|pdf>
bash scripts/toggl_report.sh myclient 2026-02-01 2026-02-28 json
```

### CLI Commands (Toggl-CLI)

If you have `toggl-cli` installed:
- `toggl te list --compact`: List time entries with minimal token usage.
- `toggl proj list --compact`: List projects efficiently.

## Configuration

The reporting script uses environment variables for authentication. Ensure `TOGGL_API_TOKEN` and `TOGGL_WORKSPACE_ID` are set.
