# Sentry CLI Command Reference

## Authentication

```bash
sentry auth login --token <TOKEN>     # authenticate with auth token
sentry auth status                     # check current auth
```

## issue

Track and manage Sentry issues.

### issue list

```bash
sentry issue list <org>/<project>      # explicit org/project
sentry issue list <org>/               # all projects in org
sentry issue list <project>            # search project across orgs
sentry issue list                      # auto-detect from DSN/config
```

**Options:**
| Option | Description |
|--------|-------------|
| `--query <query>` | Sentry search syntax (e.g., `"is:unresolved TypeError"`) |
| `--sort <sort>` | Sort by: `date` (default), `new`, `freq`, `user` |
| `--limit <n>` | Max results (default: 10) |
| `--json` | JSON output |

**Search query examples:**
- `--query "is:unresolved"` — only unresolved
- `--query "is:resolved"` — only resolved
- `--query "is:unresolved TypeError"` — unresolved + keyword
- `--query "assigned:me"` — assigned to current user

### issue view

```bash
sentry issue view <issue-id>           # by numeric ID
sentry issue view <short-id>           # by short ID (e.g., PROJ-ABC)
sentry issue view <short-id> -w        # open in browser
sentry issue view <id> --json          # JSON output
```

### issue explain

AI-powered root cause analysis using Seer.

```bash
sentry issue explain <issue-id>
sentry issue explain <short-id>
sentry issue explain my-org/MYPROJECT-ABC
sentry issue explain <issue-id> --force   # force fresh analysis
sentry issue explain <issue-id> --json
```

**Requirements:** Seer AI enabled, GitHub integration configured, code mappings set up.

**Output includes:** identified root causes, reproduction steps, relevant code locations.

### issue plan

Generate a fix plan (requires `explain` to have run first).

```bash
sentry issue plan <issue-id>
sentry issue plan <issue-id> --cause 0       # specific root cause
sentry issue plan my-org/MYPROJECT-ABC --cause 1
sentry issue plan <issue-id> --json
```

## event

Inspect Sentry events.

### event view

```bash
sentry event view <event-id>
sentry event view <event-id> -w        # open in browser
sentry event view <event-id> --json
```

**Output includes:** exception type/message, full stack trace, tags (browser, OS, environment, release), context (URL, user_id).

**Finding event IDs:** from `sentry issue view` output, from Sentry UI, or from error reports (`event_id` field).

## project

Manage Sentry projects.

### project list

```bash
sentry project list                    # all accessible projects
sentry project list <org-slug>         # projects in specific org
sentry project list --platform javascript  # filter by platform
sentry project list --json
```

### project view

```bash
sentry project view                    # auto-detect
sentry project view <org>/<project>    # explicit
sentry project view <project>          # search across orgs
sentry project view <target> -w        # open in browser
sentry project view <target> --json
```

**Output includes:** project name, org, platform, team, DSN.

## api

Make direct REST API calls to Sentry.

```bash
sentry api <endpoint> [options]
```

**Options:**
| Option | Description |
|--------|-------------|
| `--method <method>` | HTTP method: GET (default), POST, PUT, DELETE |
| `--field <key=value>` | Request body field (repeatable) |
| `--header <key:value>` | Custom header (repeatable) |
| `--include` | Include response headers |
| `--paginate` | Auto-paginate through all results |

### Common API endpoints

```bash
# Organizations
sentry api /organizations/
sentry api /organizations/my-org/

# Projects
sentry api /projects/my-org/my-project/

# Issues
sentry api /projects/my-org/my-project/issues/ --paginate

# Resolve an issue
sentry api /issues/<id>/ --method PUT --field status=resolved

# Assign an issue
sentry api /issues/<id>/ --method PUT --field assignedTo="user@example.com"

# Create a project
sentry api /teams/my-org/my-team/projects/ \
  --method POST \
  --field name="New Project" \
  --field platform=javascript

# Delete a project
sentry api /projects/my-org/my-project/ --method DELETE
```

Full API docs: https://docs.sentry.io/api/
