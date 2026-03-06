# strawpoll-cli Flag Reference

## Global Flags

Available on all commands:

| Flag | Short | Description |
|------|-------|-------------|
| `--json` | `-j` | Output JSON to stdout |
| `--plain` | | Output plain TSV (for scripting) |
| `--no-color` | | Disable colors |
| `--copy` | | Copy poll URL to clipboard |
| `--open` | | Open poll URL in browser |
| `--version` | | Print version and exit |

## Poll Commands

### `strawpoll poll create [TITLE] [OPTIONS...]`

Both args optional — launches interactive wizard if missing in TTY.

**Voting Rules:**

| Flag | Default | Values |
|------|---------|--------|
| `--dupcheck` | `ip` | `ip`, `session`, `none` |
| `--is-multiple-choice` | `false` | Allow multiple selections |
| `--multiple-choice-min` | | Min selections (requires `--is-multiple-choice`) |
| `--multiple-choice-max` | | Max selections (requires `--is-multiple-choice`) |
| `--allow-other` | `false` | Allow voters to add options |
| `--require-names` | `false` | Require voter names |

**Privacy & Access:**

| Flag | Default | Values |
|------|---------|--------|
| `--is-private` | `false` | Hide from public listings |
| `--results-vis` | `always` | `always`, `after_deadline`, `after_vote`, `hidden` |
| `--hide-participants` | `false` | Hide participant names |
| `--allow-vpn` | `true` | Allow VPN users |
| `--edit-vote-perms` | `admin_voter` | `admin`, `admin_voter`, `voter`, `nobody` |

**Display & Scheduling:**

| Flag | Default | Description |
|------|---------|-------------|
| `--deadline` | | RFC3339 or duration (e.g., `24h`) |
| `--randomize` | `false` | Randomize option order |
| `--allow-comments` | `false` | Allow comments |

### `strawpoll poll get <POLL_ID>`

Accepts poll ID or full URL.

### `strawpoll poll list`

| Flag | Default | Description |
|------|---------|-------------|
| `--limit` | `20` | Polls per page |
| `--page` | `1` | Page number |
| `--type` | `created` | `created`, `participated` |

### `strawpoll poll update <POLL_ID>`

| Flag | Short | Description |
|------|-------|-------------|
| `--title` | `-t` | New poll title |
| `--add-option` | `-a` | Add option (repeatable) |
| `--remove-option` | `-r` | Remove option by position index (repeatable) |

### `strawpoll poll delete <POLL_ID>`

| Flag | Short | Description |
|------|-------|-------------|
| `--force` | `-f` | Skip confirmation prompt |

### `strawpoll poll results <POLL_ID>`

| Flag | Short | Description |
|------|-------|-------------|
| `--participants` | `-p` | Show per-participant breakdown |

### `strawpoll poll reset <POLL_ID>`

| Flag | Short | Description |
|------|-------|-------------|
| `--force` | `-f` | Skip confirmation prompt |

## Meeting Commands

### `strawpoll meeting create <TITLE>`

Title required. Launches wizard if no dates/ranges provided.

| Flag | Short | Description |
|------|-------|-------------|
| `--date` | `-d` | All-day date `YYYY-MM-DD` (repeatable) |
| `--range` | `-r` | Time range `YYYY-MM-DD HH:MM-HH:MM` (repeatable) |
| `--tz` | | IANA timezone (default: local) |
| `--location` | | Meeting location |
| `--description` | | Poll description |
| `--allow-maybe` | | Allow "if need be" responses (default: `true`) |
| `--no-allow-maybe` | | Disable "if need be" responses |
| `--dupcheck` | | Duplication checking (default: `none`) |
| `--deadline` | | Deadline (RFC3339 or duration) |

### `strawpoll meeting get <MEETING_ID>`

Accepts meeting poll ID or URL.

### `strawpoll meeting list`

| Flag | Default | Description |
|------|---------|-------------|
| `--limit` | `20` | Results per page |
| `--page` | `1` | Page number |

### `strawpoll meeting update <MEETING_ID>`

| Flag | Short | Description |
|------|-------|-------------|
| `--title` | `-t` | New poll title |
| `--location` | | Meeting location |
| `--add-date` | `-d` | Add all-day date `YYYY-MM-DD` (repeatable) |
| `--add-range` | `-r` | Add time range `YYYY-MM-DD HH:MM-HH:MM` (repeatable) |
| `--tz` | | IANA timezone |

### `strawpoll meeting delete <MEETING_ID>`

| Flag | Short | Description |
|------|-------|-------------|
| `--force` | `-f` | Skip confirmation prompt |

### `strawpoll meeting results <MEETING_ID>`

Displays participant-by-timeslot availability grid with Yes/No/Maybe and summary totals.

## Ranking Commands

### `strawpoll ranking create <TITLE> <OPTIONS...>`

Both title and options required (no wizard).

| Flag | Default | Description |
|------|---------|-------------|
| `--dupcheck` | `ip` | `ip`, `session`, `none` |
| `--is-private` | `false` | Hide from public listings |
| `--results-vis` | `always` | Results visibility |
| `--deadline` | | Deadline (RFC3339 or duration) |
| `--allow-comments` | `false` | Allow comments |
| `--description` | | Poll description |

### `strawpoll ranking get <RANKING_ID>`

Accepts ranking poll ID or URL.

### `strawpoll ranking list`

| Flag | Short | Default | Description |
|------|-------|---------|-------------|
| `--limit` | `-l` | `20` | Max results per page |
| `--page` | `-p` | `1` | Page number |

### `strawpoll ranking update <RANKING_ID>`

| Flag | Short | Description |
|------|-------|-------------|
| `--title` | `-t` | New poll title |
| `--add-option` | `-a` | Add option (repeatable) |
| `--remove-option` | `-r` | Remove option by position index (repeatable) |

### `strawpoll ranking delete <RANKING_ID>`

| Flag | Short | Description |
|------|-------|-------------|
| `--force` | `-f` | Skip confirmation prompt |

### `strawpoll ranking results <RANKING_ID>`

| Flag | Short | Description |
|------|-------|-------------|
| `--verbose` | `-v` | Show per-option position breakdown (Borda count) |

## Auth Commands

### `strawpoll auth set-key`

| Flag | Description |
|------|-------------|
| `--stdin` | Read API key from stdin (for scripts) |

### `strawpoll auth status`

Shows API key status, keyring backend, and config path.

### `strawpoll auth remove`

Deletes stored API key from keyring.

## Config Commands

### `strawpoll config show`

Displays current configuration.

### `strawpoll config set <KEY> <VALUE>`

Valid keys:

| Key | Values |
|-----|--------|
| `keyring_backend` | `auto`, `keychain`, `file` |
| `dupcheck` | `ip`, `session`, `none` |
| `results_visibility` | `always`, `after_deadline`, `after_vote`, `hidden` |
| `is_private` | `true`, `false` |
| `allow_comments` | `true`, `false` |
| `allow_vpn_users` | `true`, `false` |
| `hide_participants` | `true`, `false` |
| `edit_vote_permissions` | `admin`, `admin_voter`, `voter`, `nobody` |

### `strawpoll config path`

Prints config file location (`~/.config/strawpoll/config.yaml`).

## Environment Variables

| Variable | Description |
|----------|-------------|
| `STRAWPOLL_API_KEY` | API key (overrides keyring) |
| `STRAWPOLL_KEYRING_BACKEND` | Keyring backend: `keychain`, `file`, `auto` |
| `STRAWPOLL_KEYRING_PASSWORD` | Password for file-based keyring |
| `NO_COLOR` | Disable colored output |

## Completion Commands

```bash
strawpoll completion bash    # Bash completions
strawpoll completion zsh     # Zsh completions
strawpoll completion fish    # Fish completions
```
