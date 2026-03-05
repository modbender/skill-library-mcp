# toggl-cli

Interact with your Toggl Track workspace via the toggl-cli.

## Install

Clone and install the CLI:
```bash
git clone https://github.com/FroeMic/toggl-cli
cd toggl-cli
npm install
npm run build
npm link
```

Set `TOGGL_API_TOKEN` environment variable (get it from [Toggl Profile Settings](https://track.toggl.com/profile)):
- **Recommended:** Add to `~/.claude/.env` for Claude Code
- **Alternative:** Add to `~/.bashrc` or `~/.zshrc`: `export TOGGL_API_TOKEN="your-api-token"`

Optionally set default workspace:
```bash
export TOGGL_WORKSPACE_ID="your-workspace-id"
```

**Repository:** https://github.com/FroeMic/toggl-cli

## Commands

### Time Entries (alias: `te`)
```bash
toggl te start --description "Working on feature"  # Start a timer
toggl te stop                                       # Stop the running timer
toggl te current                                    # Get current running entry
toggl te list                                       # List recent entries
toggl te list --start-date 2024-01-01              # List from date to now
toggl te list --start-date 2024-01-01 --end-date 2024-01-31  # Date range
toggl te get <id>                                   # Get entry by ID
toggl te create --start "2024-01-15T09:00:00Z" --duration 3600 --description "Meeting"
toggl te update <id> --description "Updated"        # Update entry
toggl te delete <id>                                # Delete entry
```

### Projects (alias: `proj`)
```bash
toggl proj list                        # List all projects
toggl proj list --active true          # List active projects only
toggl proj get <id>                    # Get project details
toggl proj create --name "New Project" --color "#FF5733"
toggl proj update <id> --name "Renamed"
toggl proj delete <id>
```

### Clients
```bash
toggl client list                      # List clients
toggl client list --status archived    # List archived clients
toggl client create --name "Acme Corp" --notes "Important client"
toggl client archive <id>              # Archive a client
toggl client restore <id>              # Restore archived client
toggl client delete <id>
```

### Tags
```bash
toggl tag list                         # List tags
toggl tag create --name "urgent"
toggl tag update <id> --name "high-priority"
toggl tag delete <id>
```

### Tasks
```bash
toggl task list --project <project_id>
toggl task create --name "Implement feature" --project <project_id>
toggl task update <id> --project <project_id> --name "Updated task"
toggl task delete <id> --project <project_id>
```

### Workspaces (alias: `ws`)
```bash
toggl ws list                          # List workspaces
toggl ws get <id>                      # Get workspace details
toggl ws users list --workspace <id>   # List workspace users
```

### Organizations (alias: `org`)
```bash
toggl org get <id>                     # Get organization details
toggl org users list --organization <id>  # List org users
```

### Groups
```bash
toggl group list --organization <id>
toggl group create --organization <id> --name "Development Team"
toggl group update <id> --organization <org_id> --name "Engineering Team"
toggl group delete <id> --organization <org_id>
```

### User Profile
```bash
toggl me get                           # Get your profile
toggl me get --with-related-data       # Include workspaces, etc.
toggl me preferences                   # Get user preferences
toggl me quota                         # Get API rate limit info
```

## Output Formats

All list/get commands support `--format` option:
```bash
toggl te list --format json            # JSON output (default)
toggl te list --format table           # Human-readable table
toggl te list --format csv             # CSV for spreadsheets
```

## Key Concepts

| Concept | Purpose | Example |
|---------|---------|---------|
| Time Entries | Track time spent on tasks | "2 hours on Project X" |
| Projects | Group related time entries | "Website Redesign" |
| Clients | Group projects by customer | "Acme Corp" |
| Workspaces | Separate environments | "Personal", "Work" |
| Tags | Categorize entries | "billable", "meeting" |
| Tasks | Sub-items within projects | "Design mockups" |

## API Reference

- **Base URL:** `https://api.track.toggl.com/api/v9`
- **Auth:** HTTP Basic with API token as both username and password
- **Rate Limits:** 1 request/second (leaky bucket), 30-600 requests/hour (quota)

### Common API Operations

Get current user:
```bash
curl -u $TOGGL_API_TOKEN:api_token https://api.track.toggl.com/api/v9/me
```

List time entries:
```bash
curl -u $TOGGL_API_TOKEN:api_token \
  "https://api.track.toggl.com/api/v9/me/time_entries?start_date=2024-01-01&end_date=2024-01-31"
```

Start a timer:
```bash
curl -X POST -u $TOGGL_API_TOKEN:api_token \
  -H "Content-Type: application/json" \
  -d '{"workspace_id": 123, "start": "2024-01-15T09:00:00Z", "duration": -1, "created_with": "curl"}' \
  https://api.track.toggl.com/api/v9/workspaces/123/time_entries
```

Stop a timer:
```bash
curl -X PATCH -u $TOGGL_API_TOKEN:api_token \
  https://api.track.toggl.com/api/v9/workspaces/{workspace_id}/time_entries/{entry_id}/stop
```

## Notes

- The CLI handles rate limiting automatically with retry and exponential backoff.
- Negative duration on a time entry indicates a running timer.
- When using `--start-date` alone, `--end-date` defaults to now.
- Using `--end-date` without `--start-date` will error (API requires both).
- All timestamps are in ISO 8601 format.
