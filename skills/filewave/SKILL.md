# FileWave UEM API Skill

Query and manage FileWave UEM device inventory via REST API.

> **⚠️ Disclaimer:** This skill is a **technology demonstration** of Agentic Endpoint Management (AEM) — the concept of AI agents interacting directly with UEM platforms to assist IT administrators. It is provided as-is for educational purposes to explore what's possible when AI meets endpoint management. Neither the author nor FileWave accepts any liability for the use, misuse, or consequences of running this skill against production or any other environment. **Use at your own risk.** Always test in a lab environment first and review any actions before applying them to production systems.

## Overview

FileWave is a unified endpoint management platform for macOS, Windows, ChromeOS, Android, tvOS, iPadOS, and iOS. This skill provides programmatic access to device inventory and status information.

### Licensing

FileWave ( https://www.filewave.com ) offers flexible deployment options:

- **Community Edition** — Free, manages up to **15 computers + 15 mobile devices**
  - Good for testing and small deployments
  - All API capabilities available
  - No advanced features (deployments, policies, MDM commands)

- **Commercial License** — More than 15 devices with advanced features
  - TeamViewer Remote Control
  - Deployment management, policy enforcement, MDM commands
  - Technical support

This skill works with both licensing models.

## Setup

### Prerequisites

- FileWave server hostname/DNS
- FileWave API token (from FileWave Central → Manage Administrators → API Token)

### Configuration

Setup is interactive via `filewave setup`:

```bash
filewave setup
```

This creates `~/.filewave/config` with your server profiles. Credentials are stored securely (chmod 600, never hardcoded in scripts).

For **CI/CD environments**, use environment variables:

```bash
export FILEWAVE_SERVER="filewave.company.com"
export FILEWAVE_TOKEN="your_api_token_here"
```

Never hardcode tokens in scripts or documentation.

## Usage

### Basic Commands

```bash
# Setup profiles (first time)
filewave setup

# List configured servers
filewave profiles

# Query inventory
filewave query --query-id 1

# Query with filter
filewave query --query-id 1 --filter "last_seen > 30 days"

# Search for devices (now returns multiple matches)
filewave device-search "iPad"

# Find all devices by product type (authoritative hardware lookup)
filewave find-devices iPad
filewave find-devices iPhone

# View device hierarchy and groups
filewave hierarchy 123

# Trigger a Model Update
filewave update-model

# Fleet analytics
filewave insights --type platform
filewave insights --type stale --days 30

# Cache management
filewave warm-cache
filewave cache-status

# Bulk device updates (school workflow)
filewave bulk-template --output ~/devices.csv
filewave bulk-update --csv ~/devices.csv

# Session comparison
filewave query --query-id 1 --reference lab
filewave query --query-id 1 --profile production --reference prod
filewave compare lab prod
```

## API Architecture

**Multi-Server Support:** Configure multiple FileWave servers (lab, production, test) with named profiles.

### Key Endpoints Used

- `GET /api/inv/api/v1/query_result/{query_id}` — Query device inventory
- `GET /filewave/api/devices/v1/devices/{id}` — Device details
- `GET /filewave/api/devices/internal/devices/{id}/groups` — Device group memberships
- `PATCH /filewave/api/devices/v1/devices/{id}` — Update device (name, auth user)
- `POST /filewave/api/fwserver/update_model` — Refresh model after bulk updates

### Available Device Fields (per Inventory Query)

You configure which fields to include in your Inventory Query:
- Device name, model, serial number, UDID/IMEI
- OS name, version, build
- Last checkin timestamp
- Enrollment date, user assignment
- Device group, management status, compliance state
- And 50+ more fields (configurable)

### Platforms Supported
- macOS
- Windows
- ChromeOS
- Android
- iOS
- iPadOS
- tvOS

## Example Queries

```bash
# Query from Inventory Query (returns all devices)
filewave query --query-id 1

# Filter devices not seen in 30+ days
filewave query --query-id 1 --filter "last_seen > 30 days"

# Get JSON format for scripting
filewave query --query-id 1 --format json

# Multiple filters (AND logic)
filewave query --query-id 1 \
  --filter "last_seen > 30 days" \
  --filter "platform = iOS"

# Compare lab vs production
filewave query --query-id 1 --profile lab --reference lab_inventory
filewave query --query-id 1 --profile prod --reference prod_inventory
filewave compare lab_inventory prod_inventory
```

## Authentication

FileWave API uses Bearer token authentication:

```
Authorization: Bearer <token>
```

## Response Format

FileWave Inventory Queries return column-oriented data:

```json
{
  "offset": 0,
  "fields": [
    "Client_device_name",
    "OperatingSystem_name",
    "OperatingSystem_version",
    "Client_last_connected_to_fwxserver"
  ],
  "values": [
    ["MacBook-Pro-John", "macOS 15 Sequoia", "15.1.0", "2026-02-12T14:30:00Z"],
    ["iPad-Student-001", "iPadOS", "17.3", "2026-02-10T10:22:00Z"]
  ],
  "filter_results": 2,
  "total_results": 2,
  "version": 7
}
```

The CLI converts this to device objects automatically.

## Current Features

- ✅ Multi-server profile support
- ✅ Inventory Query integration
- ✅ Natural language filtering (last_seen > 30 days)
- ✅ Device hierarchy analysis (original vs. clones)
- ✅ Bulk device updates (school deployment workflow)
- ✅ Fleet analytics: platform breakdown, stale device reports, field summaries
- ✅ Session tracking and server comparison
- ✅ JSON export for scripting
- ✅ 7-day device cache for performance

## Documentation

- **README.md** — Overview and quick start
- **CLI_REFERENCE.md** — Complete command reference (includes fleet analytics, cache commands)
- **BULK_UPDATE.md** — School district workflow
- **API_CAPABILITIES.md** — API reference and analytics module
- **CREDENTIAL_ARCHITECTURE.md** — Security design
- **SESSION_DATA_MANAGER.md** — Session tracking internals
- **ONBOARDING.md** — Setup wizard details
