# issue

> Manage Linear issues

## Usage

```text
linear issue [subcommand]
```

The current issue is determined by:
- **git**: the issue ID in the current branch name (e.g. `eng-123-my-feature`)
- **jj**: the `Linear-issue` trailer in the current or ancestor commits

## Subcommands

### list

List your issues in a table view.

```bash
linear issue list [options]
```

| Flag | Description | Default |
|---|---|---|
| `-s, --state <state>` | Filter by state (triage, backlog, unstarted, started, completed, canceled). Repeatable. | `unstarted` |
| `--all-states` | Show issues from all states | |
| `--assignee <username>` | Filter by assignee username | |
| `-A, --all-assignees` | Show issues for all assignees | |
| `-U, --unassigned` | Show only unassigned issues | |
| `--sort <sort>` | Sort order: `manual` or `priority` | |
| `--team <team>` | Team to list issues for | |
| `--project <project>` | Filter by project name | |
| `--limit <n>` | Max issues to fetch (0 = unlimited) | `50` |
| `-w, --web` | Open in web browser | |
| `-a, --app` | Open in Linear.app | |
| `--no-pager` | Disable automatic paging | |

**Examples:**

```bash
# List your unstarted issues
linear issue list

# List started issues for all assignees
linear issue list -s started -A

# List issues in a specific project
linear issue list --project "Q1 Launch"

# List all issues with no limit
linear issue list --all-states --limit 0
```

### create

Create a new Linear issue.

```bash
linear issue create [options]
```

| Flag | Description |
|---|---|
| `-t, --title <title>` | Title of the issue |
| `-d, --description <desc>` | Description of the issue |
| `-a, --assignee <assignee>` | Assign to `self` or someone (by username or name) |
| `-s, --state <state>` | Workflow state (by name or type) |
| `-l, --label <label>` | Issue label (repeatable) |
| `-p, --parent <parent>` | Parent issue as team_number code |
| `--priority <1-4>` | Priority (1=urgent, 4=low) |
| `--estimate <points>` | Points estimate |
| `--due-date <date>` | Due date |
| `--team <team>` | Team (if not default) |
| `--project <project>` | Project name |
| `--start` | Start the issue after creation |
| `--no-use-default-template` | Skip default template |
| `--no-interactive` | Disable interactive prompts |
| `--no-color` | Disable colored output |

**Examples:**

```bash
# Interactive creation
linear issue create

# Non-interactive with all details
linear issue create -t "Fix auth bug" -d "SSO login broken" -a self --priority 1 -s "In Progress" -l "bug"

# Create and immediately start
linear issue create -t "New feature" --start

# Create a sub-issue
linear issue create -t "Subtask" -p ENG-123
```

### update

Update a Linear issue.

```bash
linear issue update [issueId] [options]
```

| Flag | Description |
|---|---|
| `-t, --title <title>` | New title |
| `-d, --description <desc>` | New description |
| `-a, --assignee <assignee>` | New assignee |
| `-s, --state <state>` | New workflow state |
| `-l, --label <label>` | New label (repeatable) |
| `-p, --parent <parent>` | New parent issue |
| `--priority <1-4>` | New priority |
| `--estimate <points>` | New estimate |
| `--due-date <date>` | New due date |
| `--team <team>` | Move to different team |
| `--project <project>` | Move to different project |
| `--no-color` | Disable colored output |

**Examples:**

```bash
# Update current branch's issue state
linear issue update -s "Done"

# Update a specific issue
linear issue update ENG-123 -t "Updated title" --priority 2

# Assign to someone
linear issue update ENG-123 -a "jane"
```

### view

View issue details or open in browser/app.

```bash
linear issue view [issueId] [options]
```

| Flag | Description |
|---|---|
| `-w, --web` | Open in web browser |
| `-a, --app` | Open in Linear.app |
| `--no-comments` | Exclude comments |
| `--no-pager` | Disable paging |
| `-j, --json` | Output as JSON |
| `--no-download` | Keep remote URLs |

**Examples:**

```bash
# View current branch's issue
linear issue view

# View specific issue
linear issue view ENG-123

# Get JSON output
linear issue view ENG-123 --json

# Open in browser
linear issue view -w
```

### start

Start working on an issue. Creates/switches to a git branch and marks the issue as started.

```bash
linear issue start [issueId] [options]
```

| Flag | Description |
|---|---|
| `-A, --all-assignees` | Show issues for all assignees |
| `-U, --unassigned` | Show only unassigned issues |
| `-f, --from-ref <ref>` | Git ref to create branch from |
| `-b, --branch <name>` | Custom branch name |

**Examples:**

```bash
# Interactive: pick from your issues
linear issue start

# Start a specific issue
linear issue start ENG-123

# Start from a specific branch
linear issue start ENG-123 -f main
```

### pull-request (pr)

Create a GitHub pull request with issue details pre-filled (uses `gh` CLI).

```bash
linear issue pr [issueId] [options]
```

| Flag | Description |
|---|---|
| `--base <branch>` | Target branch for merge |
| `--draft` | Create as draft PR |
| `-t, --title <title>` | Custom PR title (issue ID auto-prefixed) |
| `--web` | Open PR in browser after creating |
| `--head <branch>` | Branch with commits |

### delete

Delete an issue.

```bash
linear issue delete [issueId] [options]
```

| Flag | Description |
|---|---|
| `-y, --confirm` | Skip confirmation |
| `--bulk <ids...>` | Delete multiple issues |
| `--bulk-file <file>` | Read IDs from file |
| `--bulk-stdin` | Read IDs from stdin |

### comment

Manage issue comments.

#### comment add

```bash
linear issue comment add [issueId] [options]
```

| Flag | Description |
|---|---|
| `-b, --body <text>` | Comment body |
| `-p, --parent <id>` | Parent comment ID (for replies) |
| `-a, --attach <file>` | Attach a file (repeatable) |

#### comment update

```bash
linear issue comment update <commentId> -b <text>
```

#### comment list

```bash
linear issue comment list [issueId] [--json]
```

### Other subcommands

| Command | Description |
|---|---|
| `linear issue id` | Print the issue ID from current branch |
| `linear issue title [issueId]` | Print the issue title |
| `linear issue url [issueId]` | Print the Linear URL |
| `linear issue describe [issueId]` | Print title + Linear-issue trailer |
| `linear issue commits [issueId]` | Show commits for an issue (jj only) |
| `linear issue attach <issueId> <file>` | Attach a file to an issue |
