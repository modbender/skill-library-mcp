---
name: linear
description: Manage Linear issues, projects, teams, and documents from the command line using the linear CLI. Create, update, list, and track issues; manage projects and milestones; interact with the Linear GraphQL API.
homepage: https://github.com/cipher-shad0w/openclaw-linear
metadata: {"openclaw": {"emoji": "🖇️", "os": ["darwin", "linux", "win32"], "requires": {"bins": ["linear"]}, "install": [{"id": "brew", "kind": "brew", "formula": "schpet/tap/linear", "bins": ["linear"], "label": "Install linear CLI (brew)", "os": ["darwin", "linux"]}]}}
---

# Linear

A CLI to manage Linear issues from the command line, with git and jj integration.

## Prerequisites

The `linear` command must be available on PATH. To check:

```bash
linear --version
```

If not installed:
- **Homebrew**: `brew install schpet/tap/linear`
- **Deno**: `deno install -A --reload -f -g -n linear jsr:@schpet/linear-cli`
- **Binaries**: https://github.com/schpet/linear-cli/releases/latest

## Setup

1. Create an API key at https://linear.app/settings/account/security
2. Authenticate: `linear auth login`
3. Configure your project: `cd my-project-repo && linear config`

## Available Commands

```text
linear auth               # Manage Linear authentication
linear issue              # Manage Linear issues
linear team               # Manage Linear teams
linear project            # Manage Linear projects
linear project-update     # Manage project status updates
linear milestone          # Manage Linear project milestones
linear initiative         # Manage Linear initiatives
linear initiative-update  # Manage initiative status updates
linear label              # Manage Linear issue labels
linear document           # Manage Linear documents
linear config             # Interactively generate .linear.toml configuration
linear schema             # Print the GraphQL schema to stdout
linear api                # Make a raw GraphQL API request
```

## Common Workflows

### List and view issues

```bash
# List your unstarted issues
linear issue list

# List issues in a specific state
linear issue list -s started
linear issue list -s completed

# List all assignees' issues
linear issue list -A

# View the current branch's issue
linear issue view

# View a specific issue
linear issue view ABC-123
```

### Create and manage issues

```bash
# Create an issue interactively
linear issue create

# Create non-interactively
linear issue create -t "Fix login bug" -d "Users can't log in with SSO" -s "In Progress" -a self --priority 1

# Update an issue
linear issue update ABC-123 -s "Done" -t "Updated title"

# Add a comment
linear issue comment add ABC-123 -b "This is fixed in the latest build"

# Delete an issue
linear issue delete ABC-123 -y
```

### Start working on an issue

```bash
# Pick an issue interactively, creates a git branch and marks it as started
linear issue start

# Start a specific issue
linear issue start ABC-123

# Create a PR with issue details pre-filled
linear issue pr
```

### Projects and milestones

```bash
# List projects
linear project list

# Create a project
linear project create -n "Q1 Launch" -t ENG -s started --target-date 2026-03-31

# List milestones for a project
linear milestone list --project <projectId>
```

### Documents

```bash
# List documents
linear document list

# Create a document from a file
linear document create --title "Design Spec" --content-file ./spec.md --project <projectId>

# View a document
linear document view <slug>
```

### Teams

```bash
# List teams
linear team list

# List team members
linear team members
```

## Discovering Options

Run `--help` on any command for flags and options:

```bash
linear --help
linear issue --help
linear issue list --help
linear issue create --help
```

## Using the Linear GraphQL API Directly

**Prefer the CLI for all supported operations.** The `api` command is a fallback for queries not covered by the CLI.

### Check the schema

```bash
linear schema -o "${TMPDIR:-/tmp}/linear-schema.graphql"
grep -i "cycle" "${TMPDIR:-/tmp}/linear-schema.graphql"
grep -A 30 "^type Issue " "${TMPDIR:-/tmp}/linear-schema.graphql"
```

### Make a GraphQL request

```bash
# Simple query
linear api '{ viewer { id name email } }'

# With variables
linear api 'query($teamId: String!) { team(id: $teamId) { name } }' --variable teamId=abc123

# Complex filter via JSON
linear api 'query($filter: IssueFilter!) { issues(filter: $filter) { nodes { title } } }' \
  --variables-json '{"filter": {"state": {"name": {"eq": "In Progress"}}}}'

# Pipe to jq
linear api '{ issues(first: 5) { nodes { identifier title } } }' | jq '.data.issues.nodes[].title'
```

### Using curl directly

```bash
curl -s -X POST https://api.linear.app/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: $(linear auth token)" \
  -d '{"query": "{ viewer { id } }"}'
```

## Reference Documentation

For detailed subcommand documentation with all flags and options:

- [issue](references/issue.md) - Manage Linear issues (list, create, update, start, view, comment, PR, delete)
- [team](references/team.md) - Manage Linear teams (list, create, delete, members, autolinks)
- [project](references/project.md) - Manage Linear projects (list, view, create)
- [document](references/document.md) - Manage Linear documents (list, view, create, update, delete)
- [api](references/api.md) - Make raw GraphQL API requests

## Configuration

The CLI supports environment variables or a `.linear.toml` config file:

| Option | Env Var | TOML Key | Example |
|---|---|---|---|
| Team ID | `LINEAR_TEAM_ID` | `team_id` | `"ENG"` |
| Workspace | `LINEAR_WORKSPACE` | `workspace` | `"mycompany"` |
| Issue sort | `LINEAR_ISSUE_SORT` | `issue_sort` | `"priority"` or `"manual"` |
| VCS | `LINEAR_VCS` | `vcs` | `"git"` or `"jj"` |

Config file locations (checked in order):
1. `./linear.toml` or `./.linear.toml` (current directory)
2. `<repo-root>/linear.toml` or `<repo-root>/.linear.toml`
3. `<repo-root>/.config/linear.toml`
4. `~/.config/linear/linear.toml`
