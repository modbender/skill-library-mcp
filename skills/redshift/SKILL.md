---
name: redshift
description: Manage application secrets with the Redshift CLI (https://redshiftapp.com) — decentralized, encrypted secret management built on Nostr. Use when setting, getting, deleting, listing, uploading, or downloading secrets, injecting secrets into commands, configuring projects/environments, or authenticating with Nostr keys. Covers redshift secrets, redshift run, redshift setup, redshift login, and related commands.
homepage: https://redshiftapp.com
metadata:
  {
    "openclaw":
      {
        "emoji": "🔐",
        "requires":
          {
            "bins": ["redshift"],
            "envOptional": ["REDSHIFT_NSEC", "REDSHIFT_BUNKER", "REDSHIFT_CONFIG_DIR"],
          },
        "installHint": "Install from https://redshiftapp.com or build from source: https://github.com/accolver/redshift",
      },
  }
---

# Redshift

Decentralized secret management via the `redshift` CLI. Secrets are client-side encrypted (NIP-59 Gift Wrap) and stored on Nostr relays — no central server.

Project homepage: https://redshiftapp.com

## Key concepts

- **Project** (`-p`): a project slug (e.g. `backend`, `myapp`)
- **Config/Environment** (`-c`): an environment slug (e.g. `dev`, `staging`, `production`)
- **redshift.yaml**: per-directory project config created by `redshift setup`
- When `-p`/`-c` are omitted, Redshift reads from `redshift.yaml` in the current directory

## Security considerations

- Never pass secret values directly on the command line in shared/logged environments — prefer `redshift secrets set` interactively or pipe from stdin
- Use `REDSHIFT_NSEC` / `REDSHIFT_BUNKER` env vars for CI/CD rather than CLI flags
- Avoid `redshift serve --host 0.0.0.0` unless you intend to expose the web UI to the network — default `127.0.0.1` is localhost-only
- All encryption is client-side; secrets never leave the device unencrypted
- Private keys are stored in the system keychain, not in plaintext config files

## Authentication

```bash
redshift login                    # Interactive (recommended)
redshift login --nsec nsec1...    # Direct private key (use env var in CI instead)
redshift login --bunker "bunker://pubkey?relay=wss://relay.example&secret=xxx"  # NIP-46 (ALWAYS quote the URL)
redshift login --connect          # Generate NostrConnect URI for bunker app
redshift me                       # Check current identity
redshift logout                   # Clear credentials
```

CI/CD: set `REDSHIFT_NSEC` or `REDSHIFT_BUNKER` env vars instead of `redshift login`. These should be stored in your CI platform's secret management (e.g. GitHub Actions secrets), never hardcoded.

## Project setup

```bash
redshift setup                                  # Interactive
redshift setup -p myapp -c production           # Non-interactive
redshift setup --no-interactive -p app -c dev   # Strict non-interactive
```

Creates `redshift.yaml` with project, environment, and relay list.

## Secrets

```bash
# List all
redshift secrets                          # Redacted values
redshift secrets --raw                    # Show plaintext values
redshift secrets --json                   # JSON output
redshift secrets --only-names             # Names only

# Get
redshift secrets get API_KEY
redshift secrets get API_KEY --plain      # Raw value, no formatting
redshift secrets get API_KEY --copy       # Copy to clipboard
redshift secrets get KEY1 KEY2            # Multiple keys

# Set
redshift secrets set API_KEY sk_live_xxx
redshift secrets set API_KEY '123' DB_URL 'postgres://...'    # Multiple at once

# Delete
redshift secrets delete OLD_KEY
redshift secrets delete KEY1 KEY2 -y      # Skip confirmation

# Download
redshift secrets download ./secrets.json                     # JSON (default)
redshift secrets download --format=env --no-file             # Print .env to stdout
redshift secrets download --format=env ./secrets.env         # Save as .env file
# Formats: json, env, yaml, docker, env-no-quotes

# Upload
redshift secrets upload secrets.env
```

Override project/environment on any secrets command with `-p` / `-c`:

```bash
redshift secrets -p backend -c production --raw
redshift secrets set -p myapp -c staging FEATURE_FLAG true
```

## Run with secrets injected

**Important:** Only run commands the user has explicitly requested. Never construct arbitrary commands to pass to `redshift run`. Always confirm the command with the user before executing.

```bash
redshift run -- npm start
redshift run -- python app.py
redshift run --command "npm start && npm test"
redshift run -p myapp -c prod -- docker-compose up

# Mount secrets to a file instead of env vars
redshift run --mount secrets.json -- cat secrets.json
redshift run --mount secrets.env --mount-format env -- cat secrets.env

# Fallback for offline mode
redshift run --fallback ./fallback.json -- npm start
redshift run --fallback-only -- npm start          # Read only from fallback

# Preserve existing env values for specific keys
redshift run --preserve-env PORT,HOST -- npm start
```

## Configuration

```bash
redshift configure                    # Show config
redshift configure --all              # Show all saved options
redshift configure get project        # Get specific option
redshift configure set project=myapp  # Set option
redshift configure unset project      # Remove option
redshift configure reset --yes        # Reset to initial state
```

## Web UI

```bash
redshift serve                        # http://127.0.0.1:3000 (localhost only)
redshift serve --port 8080 --open     # Custom port, auto-open browser
redshift serve --host 0.0.0.0         # ⚠️ Exposes to network — use with caution
```

## Global flags

| Flag             | Short | Description                   |
|------------------|-------|-------------------------------|
| `--help`         | `-h`  | Show help                     |
| `--version`      | `-v`  | Show version                  |
| `--json`         |       | JSON output                   |
| `--silent`       |       | Suppress info messages        |
| `--debug`        |       | Verbose debug output          |
| `--config-dir`   |       | Override config dir (~/.redshift) |

## Environment variables

| Variable               | Description                                      |
|------------------------|--------------------------------------------------|
| `REDSHIFT_NSEC`        | Private key for CI/CD (bypasses interactive login)|
| `REDSHIFT_BUNKER`      | NIP-46 bunker URL for CI/CD (alternative to nsec) |
| `REDSHIFT_CONFIG_DIR`  | Override config directory (default: ~/.redshift)  |

## Important notes

- Always quote bunker URLs (`--bunker "bunker://..."`) — shell interprets `&` otherwise
- Secret values with spaces or special chars should be quoted
- Complex values (objects/arrays) are auto-JSON-stringified when injected by `redshift run`
