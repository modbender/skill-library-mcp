# project

> Manage Linear projects

## Usage

```text
linear project [subcommand]
```

## Subcommands

### list

List projects.

```bash
linear project list [options]
```

| Flag | Description |
|---|---|
| `--team <team>` | Filter by team key |
| `--all-teams` | Show projects from all teams |
| `--status <status>` | Filter by status name |
| `-w, --web` | Open in web browser |
| `-a, --app` | Open in Linear.app |

**Examples:**

```bash
# List all projects
linear project list

# Filter by team
linear project list --team ENG

# Filter by status
linear project list --status started
```

### view

View project details.

```bash
linear project view <projectId> [options]
```

| Flag | Description |
|---|---|
| `-w, --web` | Open in web browser |
| `-a, --app` | Open in Linear.app |

### create

Create a new Linear project.

```bash
linear project create [options]
```

| Flag | Description |
|---|---|
| `-n, --name <name>` | Project name (required) |
| `-d, --description <desc>` | Project description |
| `-t, --team <team>` | Team key (required, repeatable for multiple teams) |
| `-l, --lead <lead>` | Project lead (username, email, or @me) |
| `-s, --status <status>` | Status: planned, started, paused, completed, canceled, backlog |
| `--start-date <YYYY-MM-DD>` | Start date |
| `--target-date <YYYY-MM-DD>` | Target completion date |
| `--initiative <initiative>` | Add to initiative (ID, slug, or name) |
| `-i, --interactive` | Interactive mode (default if no flags) |
| `--no-color` | Disable colored output |

**Examples:**

```bash
# Interactive creation
linear project create

# Non-interactive
linear project create -n "Q1 Launch" -t ENG -s started --target-date 2026-03-31

# Multiple teams
linear project create -n "Cross-team effort" -t ENG -t DESIGN -l @me

# Add to initiative
linear project create -n "New Feature" -t ENG --initiative "2026 Roadmap"
```

## Related Commands

### project-update

Manage project status updates (timeline posts).

```bash
linear project-update list <projectId>
linear project-update create <projectId>
linear project-update view <updateId>
```

### milestone

Manage project milestones.

```bash
linear milestone list --project <projectId>
linear milestone view <milestoneId>
linear milestone create --project <projectId> --name "Q1 Goals" --target-date 2026-03-31
linear milestone update <milestoneId> --name "New Name"
linear milestone delete <milestoneId> [--force]
```

Alias: `linear m` can be used instead of `linear milestone`.

### initiative

Manage Linear initiatives.

```bash
linear initiative list
linear initiative view <initiativeId>
linear initiative create
```
