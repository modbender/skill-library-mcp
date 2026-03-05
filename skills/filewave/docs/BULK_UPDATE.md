# Phase 4.1: Bulk Device Update (School District Workflow)

## Overview

Bulk Device Update is an automated action for school districts that need to rename devices and assign enrollment users (auth users) in batches. This is a common summer workflow for K-12 and higher ed institutions that are distributing new devices (iPads, Chromebooks, etc.) to students and teachers.

**Use Case:**
- Receive new shipment of 500 iPads with serial numbers
- Have a roster file with student names and email addresses
- Need to assign each iPad to a student with naming convention: `Grade-Name-Device`
- Update the "Enrollment User" (auth_username) field in FileWave to match the roster

## Discovery: Finding Your Device Queries

**Important:** Every FileWave server has different Inventory Queries (reports) with different IDs. You must discover YOUR server's queries first.

Before running bulk updates, list all available queries on your server:

```bash
# List all queries/reports on YOUR server
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "https://your-filewave-server/filewave/api/reports/v1/reports?limit=50"

# Response includes query IDs and names unique to your server
# Example (your server will be different):
# - Query 1: "All macOS"
# - Query 19: "All iOS"
# - Query 34: "All Mobile"
# - Query 50: "iPad Devices" (or similar)
```

**Find your iPad/device query ID**, then verify it before creating your CSV:

```bash
# Use YOUR query ID to list devices
filewave query --query-id <YOUR_ID> --profile <YOUR_PROFILE>

# Example (yours will be different):
filewave query --query-id 19 --profile lab
```

Once you see the devices match what you expect, you're ready to create your bulk update CSV.

## Quick Start

### 1. Generate CSV Template

```bash
filewave bulk-template --output ~/Desktop/devices.csv
```

This creates a CSV template with three required columns:
- `SerialNumber` — Device serial number (primary lookup key)
- `DeviceName` — New device name to set
- `EnrollmentUser` — Enrollment user email/username

**Example template:**
```csv
SerialNumber,DeviceName,EnrollmentUser
DMPPT57WHP50,Student-iPad-001,student@district.edu
F9FYD15YLMX0,Teacher-iPad-001,teacher@district.edu
```

### 2. Fill in Your Data

Edit the CSV file with your device information. Each row must have all three fields.

**Naming conventions** (examples):
- `HS-Grade10-Alice-001` (high school, grade, name, instance)
- `ES-K-Bob-iPad` (elementary school, kindergarten, name, device type)
- `Faculty-Charlie-MacBook` (faculty, name, device type)

### 3. Run Bulk Update

```bash
filewave bulk-update --csv ~/Desktop/devices.csv
```

The CLI will:
1. ✓ Validate CSV structure and content
2. ✓ Show a summary and ask for confirmation
3. → Look up each device by serial number
4. → PATCH device name
5. → PATCH enrollment user
6. → Refresh FileWave model
7. ✓ Report results (successes/failures)

## Command Reference

### `filewave bulk-template`

Generate a CSV template for bulk updates.

```bash
filewave bulk-template [--output PATH]
```

**Options:**
- `--output PATH` — Output file path (default: `~/Desktop/bulk_update_template.csv`)

**Example:**
```bash
filewave bulk-template --output ~/Documents/summer_ipads.csv
```

### `filewave bulk-update`

Execute bulk device updates from a CSV file.

```bash
filewave bulk-update --csv FILE [--profile PROFILE] [--confirm] [--format FORMAT]
```

**Options:**
- `--csv FILE` — Path to CSV file (required)
- `--profile PROFILE` — Profile name (uses default if not specified)
- `--confirm` — Skip confirmation prompt
- `--format {text|json}` — Output format (default: text)

**Example:**
```bash
# Interactive confirmation
filewave bulk-update --csv ~/Desktop/devices.csv

# Auto-confirm (use with caution)
filewave bulk-update --csv ~/Desktop/devices.csv --confirm

# JSON output for scripting
filewave bulk-update --csv ~/Desktop/devices.csv --format json
```

## Workflow Details

### 1. CSV Validation

Before any updates run, the CSV is validated:
- File exists
- Contains required columns: `SerialNumber`, `DeviceName`, `EnrollmentUser`
- All rows have values in all three columns
- No empty/missing fields

**Example validation errors:**
```
✗ CSV file not found: /tmp/devices.csv
✗ Missing required columns: DeviceName
✗ Row 3: SerialNumber is empty
```

### 2. Device Lookup

Each device is looked up by serial number using `/api/search/v1/global`:

```
Serial: DMPPT57WHP50
  → Looking up device... Found (ID: 11341, name: C02PN3G1FVH8 - JoshL)
```

**If device not found:**
- Device marked as failed
- Processing continues for next device
- Details included in final report

### 3. Device Updates

Each device receives two separate PATCH requests:

1. **PATCH name:**
   ```
   PATCH /filewave/api/devices/v1/devices/{id}
   {"name": "Student-iPad-001"}
   ```

2. **PATCH auth_username:**
   ```
   PATCH /filewave/api/devices/v1/devices/{id}
   {"auth_username": "student@district.edu"}
   ```

### 4. Backoff & Retry

If the FileWave server is busy, the tool implements **exponential backoff**:
- Initial delay: 100ms
- Double on each retry: 200ms, 400ms, 800ms, 1600ms
- Max delay: 2000ms (2 seconds)
- Overall timeout: 2 minutes per device

**Example backoff:**
```
  → Updating name to: Student-iPad-001
    Server busy (HTTP 429), backing off 0.10s...
    Server busy (HTTP 429), backing off 0.20s...
    Server busy (HTTP 429), backing off 0.40s...
    Server busy (HTTP 429), backing off 0.80s...
    [success]
```

### 5. Model Refresh

After all devices are updated, FileWave's internal model is refreshed:

```
POST /filewave/api/fwserver/update_model
```

This ensures the web console and mobile apps see the updated device names and auth users immediately.

## Results & Output

### Text Output (default)

```
============================================================
Results Summary
============================================================

Successful: 500/500
Failed: 0
Model Refresh: success

(no failures)
```

### JSON Output

```bash
filewave bulk-update --csv ~/Desktop/devices.csv --format json
```

Returns:
```json
{
  "total": 500,
  "successful": 500,
  "failed": 0,
  "timestamp": "2026-02-12T16:30:00.000000",
  "model_refresh": "success",
  "details": [
    {
      "serial": "DMPPT57WHP50",
      "name": "Student-iPad-001",
      "user": "student@district.edu",
      "success": true,
      "messages": [
        "Name update: Name updated",
        "Auth user update: Auth user updated"
      ]
    },
    ...
  ]
}
```

## Troubleshooting

### CSV Column Order Doesn't Matter

FileWave uses DictReader, so columns can be in any order. These are equivalent:

```csv
SerialNumber,DeviceName,EnrollmentUser
DMPPT57WHP50,Student-001,student@edu

DeviceName,EnrollmentUser,SerialNumber
Student-001,student@edu,DMPPT57WHP50
```

### Device Not Found by Serial

**Causes:**
- Serial number typo or incorrect format
- Device not yet imported into FileWave
- Serial number is for a different asset type (computer vs. mobile)

**Fix:**
1. Verify serial number in FileWave directly
2. Use `filewave device-search --query <serial>` to test lookup
3. Check if device is in a special group or archived state

### Server Rejected Updates (HTTP 429, 503)

**Cause:** FileWave server is overloaded

**The tool automatically retries with exponential backoff** — no action needed. If timeout occurs after 2 minutes:
1. Check FileWave server status
2. Reduce batch size (split CSV into smaller files)
3. Try again later during off-peak hours

### Auth User Not Updating

**Possible causes:**
- Email format invalid for your LDAP/SSO system
- User doesn't exist in directory
- FileWave has different auth_username field requirements

**Check:** View device details to confirm auth_username was set:
```bash
filewave device-details "Student-iPad-001"
```

## Session Tracking

Bulk updates are recorded in your FileWave session:

```bash
filewave summary
```

Shows:
```
Bulk Updates:
  2026-02-12T16:30:00: production (500/500)
```

Export full session:
```bash
filewave session-log --server <server>
```

## CSV Template Examples

### School District Example

```csv
SerialNumber,DeviceName,EnrollmentUser
DMPPT57WHP50,Grade5-Alice-001,alice.smith@district.edu
F9FYD15YLMX0,Grade5-Bob-001,bob.jones@district.edu
ABC123DEF456,Grade6-Charlie-001,charlie.brown@district.edu
XYZ789UVW012,Faculty-Diana-MacBook,diana.miller@district.edu
```

### Corporate Example

```csv
SerialNumber,DeviceName,EnrollmentUser
ABC001,SALES-Alice-MacBook,alice@company.com
ABC002,SALES-Bob-iPad,bob@company.com
ABC003,ENG-Charlie-MacBook,charlie@company.com
ABC004,IT-Diana-DevMachine,diana@company.com
```

### Higher Ed Example

```csv
SerialNumber,DeviceName,EnrollmentUser
XYZ001,CS101-Student-001,jsmith123@university.edu
XYZ002,CS101-Student-002,bjones456@university.edu
XYZ003,Library-Laptop-01,library.kiosk@university.edu
```

## Performance Notes

- **Typical speed:** 10–20 devices per minute (depending on network and server load)
- **For 500 devices:** Expect 25–50 minutes
- **For 1000+ devices:** Consider splitting into multiple CSVs and batching overnight

Each device update includes:
1. Serial lookup (API call)
2. Device name PATCH (API call)
3. Auth username PATCH (API call)
4. Potential retries on server busy

Plus one final model refresh POST.

## Security Notes

- CSV file is processed in memory (not cached on disk after processing)
- Auth credentials come from `~/.filewave/config` (chmod 600)
- API token is from your FileWave profile configuration
- No data is logged or stored beyond the session

## Next Steps

- [Phase 4.2] Device hierarchy analysis (clone detection, group relationships)
- [Phase 4.3] CSV export with hierarchy structure for device relationships
- [Phase 4.4] Bulk group operations (add/remove devices from groups)
