# FileWave UEM API Skill

Connect to FileWave UEM servers and query device inventory across all supported platforms (macOS, Windows, iOS, iPadOS, Android, ChromeOS, tvOS).

## Purpose

FileWave is a unified endpoint management platform supporting:
- **Computers:** macOS, Windows, ChromeOS
- **Mobile:** iOS, iPadOS, Android
- **Other:** tvOS, and more

This skill enables programmatic access to device inventory, allowing you to:

- Query device status and details across all platforms
- Generate inventory reports
- Identify devices with specific characteristics (e.g., not seen in 30+ days)
- Answer complex inventory questions with intelligent filtering
- Track device health, compliance, and fleet demographics

### Licensing

Works with:
- **Community Edition** — Free (15 computers + 15 mobile devices)
- **Commercial License** — Unlimited devices

## Installation

### Via clawhub (Recommended)
```bash
clawhub install filewave
```

**What happens automatically:**
1. FileWave skill is downloaded
2. **Onboarding wizard runs in the same terminal**
3. You're prompted to add your first server (name, URL, token)
4. Config file is created at `~/.filewave/config`
5. Skill is ready to use immediately

You'll see:
```
Profile name (e.g., 'lab'): lab
Server hostname: filewave.company.com
API Token: (paste)
✓ Profile created
```

Then you can immediately use:
```bash
filewave query --query-id 1
```

**No additional steps needed — setup is part of installation.**

See [ONBOARDING.md](./ONBOARDING.md) for detailed setup guide.

## Features

✅ **Multi-Server Support** — Manage lab, production, and test servers  
✅ **Device Lookup** — Search devices, view groups, identify original vs. clones  
✅ **Inventory Queries** — Query pre-configured Inventory Queries  
✅ **Intelligent Caching** — 7-day device cache for fast lookups  
✅ **Natural Language Filters** — "last_seen > 30 days", "platform = iOS"  
✅ **Session Tracking** — Compare servers with named query references  
✅ **Secure Credentials** — Config file, chmod 600, no hardcoded tokens  
✅ **JSON Export** — Export results for scripting  
✅ **Bulk Device Updates** — Rename devices and update enrollment users in batches (school district workflow)  

## Quick Start

### Prerequisites

Before using the skill, you must create an **Inventory Query** in FileWave:
1. FileWave Admin Console → **Inventory → Queries**
2. Create a new query (select device type, choose fields)
3. Save and note the **Query ID** (numeric)

The skill uses existing Inventory Queries to fetch device data.

### Setup Profiles

The skill uses a configuration file (~/.filewave/config) with server profiles.

**First time:**
```bash
filewave setup
# Interactive wizard → adds first server
```

**Add more servers:**
```bash
filewave setup
# Adds to existing config
```

### Try It

```bash
# List your configured servers
filewave profiles

# === Query Inventory ===

# Query from default server
filewave query --query-id 1

# Query specific server
filewave query --query-id 1 --profile production

# With reference name (for comparison)
filewave query --query-id 1 --reference lab_devices

# With filter
filewave query --query-id 1 --filter "last_seen > 30 days"

# JSON output
filewave query --query-id 1 --format json

# === Device Details & Groups ===

# Search for a device
filewave device-search "device-name"

# Show device info + all groups (identify original vs. clones)
filewave device-details "device-name"

# View device lookup cache status
filewave cache-status

# === Compare Servers ===

filewave query --query-id 1 --profile lab --reference lab_devices
filewave query --query-id 1 --profile production --reference prod_devices
filewave compare lab_devices prod_devices

# === Bulk Device Updates (School District Workflow) ===

# Generate CSV template
filewave bulk-template --output ~/devices.csv

# Edit the CSV file with device data...

# Execute bulk update
filewave bulk-update --csv ~/devices.csv
```

## Core Concepts

### Platforms

FileWave manages these device types:
- **macOS** — Apple computers
- **Windows** — Microsoft PCs
- **iOS** — iPhones
- **iPadOS** — iPads
- **Android** — Android devices
- **ChromeOS** — Chromebooks
- **tvOS** — Apple TVs

### Device Properties

Every device has:
- **Identity**: name, serial, UDID/IMEI
- **OS**: platform, version, build
- **Hardware**: model, processor, RAM, storage
- **Status**: active/inactive, last seen, enrollment date
- **Management**: group, user, compliance, pending updates

See [API_CAPABILITIES.md](./API_CAPABILITIES.md) for complete field reference.

## Usage Examples

### List All Devices

```bash
filewave query --query-id 1
filewave query --query-id 1 --format json
```

### Filter by Platform

```bash
filewave query --query-id 1 --filter "platform = iOS"
filewave query --query-id 1 --filter "platform = macOS"
```

### Find Stale Devices

```bash
filewave query --query-id 1 --filter "last_seen > 30 days"
```

### Fleet Analytics

```bash
filewave insights --query-id 1
filewave insights --query-id 1 --stale-days 30
filewave insights --query-id 1 --group-by OperatingSystem_name
```

### Search for Device

```bash
filewave device-search "MacBook"
filewave device-search "ABC123"  # Serial number
```

### Device Details & Groups

```bash
filewave device-details "device-name"
filewave hierarchy 213
```

## Bulk Device Updates

The skill supports **batch rename and enrollment user assignment** — commonly needed in school districts when deploying new device shipments.

**Workflow:**
1. Generate CSV template: `filewave bulk-template --output ~/devices.csv`
2. Fill in device serial numbers, new names, and enrollment users
3. Execute: `filewave bulk-update --csv ~/devices.csv`
4. Tool automatically:
   - Validates CSV structure
   - Looks up each device by serial number
   - Updates device name and auth user
   - Handles server busy/timeout with backoff retry
   - Refreshes FileWave model

**Typical use case:**
- Summer: New iPad shipment arrives with 500 devices
- Have student roster with email addresses
- Rename iPads to match roster (`Grade5-Alice-001`, etc.)
- Set auth_username to student email for auto-enrollment

See [BULK_UPDATE.md](./BULK_UPDATE.md) for complete guide including backoff strategy, performance tips, and examples.

## Intelligent Inventory Questions (Future)

The skill is designed to eventually answer questions like:

- "How many iPads have not been seen online in more than 30 days?"
- "Show me all Windows machines needing security updates"
- "How many macOS machines are on Sonoma?"
- "List iOS devices not compliant with policy"
- "Summarize device inventory by platform and status"

See [API_CAPABILITIES.md](./API_CAPABILITIES.md) for details on how these queries work.

## Configuration

### Environment Variables

- `FILEWAVE_SERVER` — Server hostname (e.g., `filewave.company.com`)
- `FILEWAVE_TOKEN` — API token from Admin Console

### Command-Line Options

```
--profile NAME      Select server profile
--format [text|json] Output format (default: text)
```

## API Reference

The skill wraps the FileWave REST API.

**Swagger/OpenAPI docs:** `https://your-server/filewave/api/doc/`

### Endpoints Used

- `GET /api/inv/api/v1/query_result/{query_id}` — Inventory Query results
- `GET /api/devices/v1/devices/{id}` — Device details
- `GET /api/devices/internal/devices/{id}/groups` — Device group memberships
- `GET /api/search/v1/global?query={term}&limit={n}` — Global device search
- `PATCH /api/devices/v1/devices/{id}` — Update device (name, auth_username)
- `POST /filewave/api/fwserver/update_model` — Refresh model after changes

## Current Scope

**v1.1 features (complete):**
- ✅ Device listing with natural language filters
- ✅ Device search and detail lookup
- ✅ Device hierarchy and clone analysis
- ✅ Fleet analytics (platform breakdown, stale devices)
- ✅ Bulk device updates (school district workflow)
- ✅ Multi-server comparison
- ✅ Session tracking with named references

**Future (v2+):** Management operations, deployments, policies, MDM commands.

## Troubleshooting

### 404 Not Found on API Calls

→ Verify Inventory Query ID exists in FileWave Admin Console

### 401/403 Authorization

```
ERROR: 401 Unauthorized
```

→ Check API token validity and ensure account has API permissions.

### No Data Returned

→ Verify Inventory Query is configured and contains devices

## Files

- `filewave` — Main CLI script (Python 3)
- `SKILL.md` — Skill description (OpenClaw requirement)
- `manifest.json` — Clawhub manifest
- `lib/` — Python modules (api_utils, config_manager, query_parser, device_cache, bulk_update_handler, device_hierarchy, device_analytics, session_data_manager, onboarding)
- `docs/` — Documentation (README, CLI_REFERENCE, BULK_UPDATE, API_CAPABILITIES, CREDENTIAL_ARCHITECTURE, SESSION_DATA_MANAGER, ONBOARDING)
- `development/` — Internal development notes and phase history
