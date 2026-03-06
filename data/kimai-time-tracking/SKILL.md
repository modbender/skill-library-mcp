---
name: kimai-time-tracking
description: Complete Kimai time-tracking API integration. Manage timesheets, customers, projects, activities, teams, invoices and exports via REST API. Supports time tracking workflows, reporting, and administrative operations. Keywords - kimai, zeiterfassung, timesheet, tracking, project, customer, activity, invoice, export, timer, stunden
---

# Kimai Time Tracking Skill

Complete API integration for [Kimai](https://www.kimai.org/) time-tracking software. Enables full control over timesheets, projects, customers, activities, teams, invoices, and system configuration.

## When to use

**Activate this skill when the user requests:**
- Start/stop/restart time tracking (timers)
- List, filter, or export timesheets
- Manage customers, projects, or activities
- Create invoices or export data
- Administrative tasks (users, teams, rates)
- Query system status (version, plugins, config)

**Activation triggers:**
- Keywords: "kimai", "zeiterfassung", "timesheet", "timer", "stunden", "erfasse Zeit", "starte Tracking", "Projekt anlegen", "Rechnung erstellen"
- "Start tracking for project X"
- "Show my timesheets from last week"
- "Create new customer in Kimai"
- "Export timesheets to CSV"
- "List all active timers"
- "Stop current time tracking"

**Do NOT activate for:**
- General time questions ("What time is it?")
- Other time-tracking tools (Toggl, Clockify, etc.)
- Calendar/scheduling without Kimai context

## Environment Setup

**Required Environment Variables:**
- `KIMAI_BASE_URL` - Full URL to Kimai instance (e.g., `https://kimai.example.com`)
- `KIMAI_API_TOKEN` - Bearer token for authentication

**Optional:**
- `KIMAI_WORKSPACE` - Path for exports/temp files (defaults to `~/.openclaw/workspace/kimai`)

**API Permissions required depend on operation:**
- `view_own_timesheet`, `create_own_timesheet`, `edit_own_timesheet`, `delete_own_timesheet`
- `view_other_timesheet` (for viewing other users' entries)
- `view_customer`, `edit_customer`, `delete_customer`
- `view_project`, `edit_project`, `delete_project`
- `view_activity`, `edit_activity`, `delete_activity`
- `view_team`, `edit_team`, `create_team`, `delete_team`
- `view_invoice` (for invoice operations)
- `view_user` (for user management)

**Compatibility:** Requires Kimai 2.x with REST API enabled. Internet access required. Linux/macOS supported.

## Workflow

### 1. Quick Time Tracking

```bash
# List recent activities (to find project/activity IDs)
./scripts/kimai_cli.py timesheets recent

# Start tracking
./scripts/kimai_cli.py timesheets start --project 1 --activity 5 --description "Implementing API"

# Check active timers
./scripts/kimai_cli.py timesheets active

# Stop tracking
./scripts/kimai_cli.py timesheets stop --id 123
```

### 2. Data Management Workflow

```bash
# Create customer → Project → Activity hierarchy
./scripts/kimai_cli.py customers create --name "Acme Corp" --country DE --currency EUR --timezone Europe/Berlin
./scripts/kimai_cli.py projects create --name "Website Redesign" --customer 1
./scripts/kimai_cli.py activities create --name "Development" --project 1

# List with filters
./scripts/kimai_cli.py timesheets list --customer 1 --begin "2024-01-01T00:00:00" --exported 0
```

### 3. Export/Invoice Workflow

```bash
# Mark timesheets as exported (locks them)
./scripts/kimai_cli.py timesheets export --id 123

# List invoices
./scripts/kimai_cli.py invoices list --status pending --begin 2024-01-01T00:00:00
```

## CLI Tool Reference

Use `scripts/kimai_cli.py` for all operations. Structure follows API endpoints:

### Timesheets (`timesheets`)
- `list` - List entries (supports pagination, filters: user, customer, project, activity, tags, date range, exported status)
- `get <id>` - Fetch single entry
- `create` - Create manual entry or start timer (omit --end for active tracking)
- `update <id>` - Patch existing entry
- `delete <id>` - **Requires confirmation** (destructive)
- `stop <id>` - Stop active timer
- `restart <id>` - Restart finished entry (creates new)
- `duplicate <id>` - Copy entry (resets export status)
- `active` - List currently running timers
- `recent` - Recent unique working sets (last activity per project/activity combination)
- `export <id>` - Toggle export/lock status

### Customers (`customers`)
- `list` - List customers (filter: visible, term)
- `get <id>` - Fetch customer details
- `create` - Create new customer
- `update <id>` - Update customer
- `delete <id>` - **Requires confirmation** (cascades to projects/activities/timesheets)
- `meta <id>` - Update custom fields
- `rates <id>` - Manage customer-specific rates

### Projects (`projects`)
- `list` - List projects (filter: customer, visible, date range)
- `get <id>` - Fetch project
- `create` - Create project (requires customer ID)
- `update <id>` - Update project
- `delete <id>` - **Requires confirmation** (cascades to activities/timesheets)
- `rates <id>` - Manage project rates

### Activities (`activities`)
- `list` - List activities (filter: project, visible, global only)
- `get <id>` - Fetch activity
- `create` - Create activity (can be global or project-specific)
- `update <id>` - Update activity
- `delete <id>` - **Requires confirmation** (cascades to timesheets)
- `rates <id>` - Manage activity rates

### Teams (`teams`)
- `list`, `get`, `create`, `update`, `delete`
- `member-add <team-id> <user-id>` - Add team member
- `member-remove <team-id> <user-id>` - Remove member
- `grant-customer <team-id> <customer-id>` - Grant customer access
- `grant-project <team-id> <project-id>` - Grant project access
- `grant-activity <team-id> <activity-id>` - Grant activity access

### Users (`users`)
- `list` - List users (requires view_user permission)
- `me` - Current user info
- `get <id>` - User details
- `create` - Create user (admin)
- `update <id>` - Update user

### Invoices (`invoices`)
- `list` - List invoices (filter: date range, customer, status)
- `get <id>` - Invoice details

### System (`system`)
- `ping` - Test connectivity
- `version` - Kimai version info
- `plugins` - Installed plugins
- `config` - Timesheet configuration
- `colors` - Color codes

## Safety & Boundaries

**⚠️ DESTRUCTIVE OPERATIONS**
- `delete` operations on customers, projects, activities, timesheets, teams, or tags **require explicit user confirmation**.
- Deleting customers cascades to all linked projects, activities, and timesheets [1].
- Deleting projects cascades to activities and timesheets [1].
- The CLI will show a preview of affected data and require "yes" confirmation.

**API Security:**
- API token is passed via `Authorization: Bearer` header [1].
- Token is never logged or stored in CLI output.
- Use `--dry-run` flag for testing (simulates API calls without executing).

**Rate Limiting & Pagination:**
- API returns paginated results (default 50 items) [1].
- CLI auto-handles pagination for `list` commands (fetches all pages or respects `--limit`).
- Use `--page` and `--size` for manual pagination control.

**Data Privacy:**
- Timesheet data may contain sensitive information.
- Export files are saved to workspace with restricted permissions (600).
- Redact personal data (emails, names) when sharing debug output.

**Workspace Safety:**
- All file exports (CSV, JSON) default to `KIMAI_WORKSPACE` or `~/.openclaw/workspace/kimai`.
- Never write to system directories outside workspace without explicit confirmation.

## Input/Output Specifications

**Inputs:**
- Entity IDs (integers)
- ISO 8601 datetime strings (YYYY-MM-DDTHH:mm:ss)
- JSON data for create/update operations (via --json file or CLI args)
- Filter parameters (customer, project, activity IDs, date ranges, visibility)

**Outputs:**
- JSON (default, pipe-friendly)
- Table format (`--format table` for human readability)
- CSV (`--format csv` for exports)
- Exit codes: 0 (success), 1 (API error), 2 (validation error), 3 (cancelled by user)

**Success Criteria:**
- HTTP 200/201 for successful operations
- Valid JSON response structure matching API schemas [1]
- For exports: File created in workspace with expected record count

## Examples

### Start tracking with description

```bash
./scripts/kimai_cli.py timesheets create \
  --project 5 \
  --activity 12 \
  --description "Client meeting - requirements analysis" \
  --tags "meeting,urgent"
```

### List and export non-exported hours

```bash
# Find billable hours not yet exported
./scripts/kimai_cli.py timesheets list \
  --exported 0 \
  --billable 1 \
  --begin "2024-01-01T00:00:00" \
  --end "2024-01-31T23:59:59" \
  --format csv > january_hours.csv
```

### Update custom fields (meta)

```bash
./scripts/kimai_cli.py customers meta 42 \
  --name "order_number" \
  --value "PO-2024-001"
```

### Create team and assign resources

```bash
./scripts/kimai_cli.py teams create --name "Development Team" --members '[{"user": 1, "teamlead": true}]'
./scripts/kimai_cli.py teams grant-project 1 5
```

## Error Handling

**Common HTTP codes:**
- `200` - Success
- `201` - Created
- `204` - No content (successful delete)
- `400` - Bad request (validation error, missing fields)
- `401` - Unauthorized (invalid/expired token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not found (invalid ID)
- `409` - Conflict (overlapping timesheet if not allowed by config)

**CLI behavior:**
- Validates required fields before API call (e.g., project+activity for timesheets [1])
- Pretty-prints validation errors from API
- Suggests fixes (e.g., "Did you mean to use 'PATCH' instead of DELETE? Try setting visible=false to hide instead of delete")

## Validation

Validate this skill using the Openclaw skills validator:

```bash
skills-ref validate ./kimai-time-tracking
```

Test API connectivity:

```bash
export KIMAI_BASE_URL="https://your-kimai.example.com"
export KIMAI_API_TOKEN="your-api-token"
./kimai-time-tracking/scripts/kimai_cli.py system ping
```

## References

- Kimai REST API Docs: https://www.kimai.org/documentation/rest-api.html
- Pagination Guide: https://www.kimai.org/documentation/api-pagination.html
- API Spec: `references/api-reference.json` (complete OpenAPI schema)
