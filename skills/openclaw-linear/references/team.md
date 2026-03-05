# team

> Manage Linear teams

## Usage

```text
linear team [subcommand]
```

## Subcommands

### list

List teams.

```bash
linear team list [options]
```

| Flag | Description |
|---|---|
| `-w, --web` | Open in web browser |
| `-a, --app` | Open in Linear.app |

### id

Print the configured team ID.

```bash
linear team id
```

### members

List team members.

```bash
linear team members [teamKey] [options]
```

| Flag | Description |
|---|---|
| `-a, --all` | Include inactive members |

**Examples:**

```bash
# List members of default team
linear team members

# List members of a specific team
linear team members ENG

# Include inactive
linear team members --all
```

### create

Create a new Linear team.

```bash
linear team create [options]
```

| Flag | Description |
|---|---|
| `-n, --name <name>` | Name of the team |
| `-d, --description <desc>` | Description |
| `-k, --key <key>` | Team key (auto-generated from name if omitted) |
| `--private` | Make the team private |
| `--no-color` | Disable colored output |
| `--no-interactive` | Disable interactive prompts |

**Examples:**

```bash
# Interactive creation
linear team create

# Non-interactive
linear team create -n "Platform" -k "PLT" -d "Platform engineering team"

# Private team
linear team create -n "Security" --private
```

### delete

Delete a Linear team.

```bash
linear team delete <teamKey> [options]
```

| Flag | Description |
|---|---|
| `--move-issues <targetTeam>` | Move all issues to another team before deletion |
| `-y, --force` | Skip confirmation prompt |

**Examples:**

```bash
# Delete with confirmation
linear team delete OLD

# Move issues and force delete
linear team delete OLD --move-issues ENG -y
```

### autolinks

Configure GitHub repository autolinks for Linear issues with this team prefix.

```bash
linear team autolinks
```

This sets up GitHub autolinks so that references like `ENG-123` in commits and PRs automatically link to the corresponding Linear issue.
