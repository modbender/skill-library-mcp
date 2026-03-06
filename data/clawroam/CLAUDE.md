# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

ClawRoam is an OpenClaw skill that syncs an agent's knowledge, memory, and system packages across machines — like iCloud, but for AI agents. The core is pure Bash (no build step); the cloud backend is TypeScript.

The skill is published on ClawHub as `clawroam`. The managed backend runs on Cloudflare Workers at `clawroam-api.ovisoftblue.workers.dev`.

## Commands

### Bash skill (core)
There is no build step. Scripts run directly.

```bash
# Run the main CLI
bash clawroam.sh <command>

# Test a specific provider
bash providers/cloud.sh info
bash providers/git.sh info

# Test the sync engine
bash src/sync-engine.sh status
```

### Cloud API (Node.js — `cloud-api/`)
```bash
cd cloud-api
npm install
npm run dev        # tsx watch — hot reload
npm run build      # tsc
npm run migrate    # run DB migrations
```

### Cloud API Worker (Cloudflare — `cloud-api-worker/`)
```bash
cd cloud-api-worker
npm install
wrangler dev       # local dev
wrangler deploy    # deploy to Cloudflare Workers
```

### Publishing to ClawHub
```bash
clawhub publish . --slug clawroam --name "ClawRoam" --version "X.Y.Z"
```

## Architecture

### Bash layer (skill runtime)
- **`clawroam.sh`** — main CLI entry point; routes subcommands to modules
- **`src/sync-engine.sh`** — iCloud-like daemon: watches vault with `fswatch`/polling, auto-commits to a local git repo at `~/.clawroam/.git-local/`, then calls the active provider's `push`/`pull`
- **`src/keypair.sh`** — Ed25519 key generation (`ssh-keygen`), signing (via `openssl dgst`), and rotation
- **`src/provider.sh`** — provider registry: lists, selects, and delegates to `providers/*.sh`
- **`providers/*.sh`** — one file per storage backend, each implementing `{setup,push,pull,info,list-profiles}`
- **`track-packages.sh`** — scans Homebrew, apt, npm global, pip global into `requirements.yaml`
- **`migrate.sh`** — interactive wizard for restoring vault to a new machine

### Provider model
Each provider script is standalone and must implement: `setup`, `push`, `pull`, `info`, `list-profiles`. The `cloud.sh` provider encrypts the archive with AES-256-CBC (key derived from the Ed25519 private key) before upload.

### Cloud backend
Two separate implementations exist and should be kept in sync:
- **`cloud-api/`** — Node.js/Hono server for traditional hosting, uses PostgreSQL + S3
- **`cloud-api-worker/`** — Cloudflare Workers version (deployed), uses D1 + R2; the live one

Auth is Ed25519 signature-based: the client signs a request hash with `~/.clawroam/keys/clawroam_ed25519` and sends `X-ClawRoam-Signature`. The server verifies against registered public keys. The Workers version also supports JWT for the web dashboard.

### Vault structure
The vault lives at `~/.clawroam/`. `local/` (SOUL.md, IDENTITY.md) is never synced. `keys/` never leaves the machine. Everything else syncs per-profile — each machine uses its hostname as a profile name by default, so machines don't overwrite each other.

### Web assets
`web/index.html` is a standalone landing page (no build step). `web/dashboard.html` is the ClawRoam Cloud user dashboard.

## Key conventions

- All Bash scripts use `set -euo pipefail` and are macOS/Linux compatible
- macOS/Linux `sed -i` syntax differs — always branch on `uname -s` for in-place edits
- `python3` is used for JSON parsing in shell scripts (assumed available)
- The Cloud Worker is the live deployment; `cloud-api/` is a reference/fallback
- Versions in `SKILL.md` must be semver strings (quote them in YAML: `version: "2.0.0"`)
