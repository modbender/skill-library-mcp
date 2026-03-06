# 🦦 Osori (오소리)

> Local project registry & context loader for AI agents.

Osori keeps track of all your local projects in a single JSON registry and lets AI agents (or you) find, switch, inspect, and manage them instantly — via Telegram slash commands or shell scripts.

## Features

- **📋 Project Registry** — Single-file JSON with auto-migration and atomic writes
- **🔀 Smart Switch** — Fuzzy match with multi-candidate scoring and `--index` selection
- **🌳 Multi-Root** — Organize projects into roots (e.g. `work`, `personal`) with discovery paths
- **🩺 Doctor** — Health check with safe auto-fix for registry issues
- **🧬 Fingerprints** — Git remote, last commit, open PR/issue counts at a glance
- **🏷️ Aliases** — Short names for quick access (`rh` → `RunnersHeart`)
- **⭐ Favorites** — Mark and list your go-to projects
- **📊 GitHub Cache** — TTL-based cache for PR/issue counts (no API spam)
- **🔗 Entire Integration** — Run [Entire](https://entire.io) CLI commands in project context

## Requirements

| Dependency | Required | Notes |
|---|---|---|
| `python3` | ✅ | JSON processing |
| `git` | ✅ | Project detection & status |
| `gh` | ✅ | GitHub PR/issue counts |
| `mdfind` | macOS only | Spotlight search (auto-fallback to `find` on Linux) |
| `entire` | Optional | Only for `/entire-*` commands |

## Installation

### Via [ClawHub](https://clawhub.com)

```bash
clawhub install osori
```

### Manual

Copy the skill folder into your OpenClaw workspace:

```bash
cp -r osori /path/to/.openclaw/workspace/skills/osori
```

## Quick Start

```bash
# Add a project
/add /path/to/my-project

# Scan a directory for all git repos
/scan /path/to/workspace

# List everything
/list

# Switch to a project (loads full context)
/switch my-project

# Check health
/doctor
```

## Commands

### Core

| Command | Description |
|---|---|
| `/list [root]` | Show registered projects |
| `/status [root]` | Check git status of projects |
| `/find <name> [--root <root>]` | Find a project by name |
| `/switch <name> [--root <root>] [--index <n>]` | Switch to project & load context |
| `/fingerprints [name] [--root <root>]` | Show repo fingerprint (remote, commit, PRs, issues) |
| `/add <path>` | Add project to registry |
| `/remove <name>` | Remove project from registry |
| `/scan <path> [root]` | Scan directory for git projects |
| `/doctor [--fix] [--json]` | Registry health check |

### Root Management

| Command | Description |
|---|---|
| `/list-roots` | List all roots with project counts |
| `/root-add <key> [label]` | Add or update a root |
| `/root-path-add <key> <path>` | Add discovery path to root |
| `/root-path-remove <key> <path>` | Remove discovery path |
| `/root-set-label <key> <label>` | Update root label |
| `/root-remove <key> [--reassign <target>] [--force]` | Safely remove root |

### Aliases & Favorites

| Command | Description |
|---|---|
| `/alias-add <alias> <project>` | Create shortcut name |
| `/alias-remove <alias>` | Remove alias |
| `/favorites` | List favorite projects |
| `/favorite-add <project>` | Mark as favorite |
| `/favorite-remove <project>` | Unmark favorite |

### Entire Integration

| Command | Description |
|---|---|
| `/entire-status <project> [--root <root>]` | Show Entire status |
| `/entire-enable <project> [--root <root>]` | Enable Entire (default: claude-code, manual-commit) |
| `/entire-rewind-list <project> [--root <root>]` | List rewind points |

## How Switch Works

```
/switch my-app
```

1. Fuzzy-match name in registry (scoped by root if provided)
2. If multiple matches → score & rank candidates:
   - `+50` root exact match
   - `+30` name exact match
   - `+20` name prefix match
   - `+10` most recent commit
   - `-10` missing path, `-5` no repo
3. Auto-select #1, or use `--index <n>` to pick
4. Load context: git status, branch, recent commits, open issues
5. Aliases resolve transparently (`/switch rh` → RunnersHeart)

## Registry Schema

```json
{
  "schema": "osori.registry",
  "version": 2,
  "updatedAt": "2026-02-16T00:00:00Z",
  "roots": [
    { "key": "default", "label": "Default", "paths": [] }
  ],
  "aliases": {
    "rh": "RunnersHeart"
  },
  "projects": [
    {
      "name": "MyProject",
      "path": "/absolute/path",
      "repo": "owner/repo",
      "lang": "swift",
      "tags": ["ios"],
      "root": "default",
      "favorite": false,
      "addedAt": "2026-02-16"
    }
  ]
}
```

**Safety guarantees:**
- Atomic write with rollback fallback
- Auto-backup on migration: `osori.json.bak-<timestamp>`
- Corrupted files preserved as: `osori.json.broken-<timestamp>`
- Auto-migration from legacy formats (v1 array → v2 object)

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `OSORI_REGISTRY` | `$HOME/.openclaw/osori.json` | Registry file path |
| `OSORI_SEARCH_PATHS` | — | Additional discovery paths (colon-separated) |
| `OSORI_CACHE_FILE` | `$HOME/.openclaw/osori-cache.json` | GitHub count cache |
| `OSORI_CACHE_TTL` | `600` | Cache TTL in seconds (≤0 forces refresh) |

## Project Structure

```
osori/
├── SKILL.md                          # OpenClaw skill definition
├── LICENSE
├── README.md
├── scripts/
│   ├── telegram-commands.sh          # Main command dispatcher
│   ├── registry_lib.py               # Core registry library
│   ├── add-project.sh                # /add
│   ├── scan-projects.sh              # /scan
│   ├── project-fingerprints.sh       # /fingerprints
│   ├── doctor.sh                     # /doctor
│   ├── root-manager.sh              # /root-* commands
│   ├── alias-favorite-manager.sh    # /alias-*, /favorite-*
│   ├── entire-manager.sh            # /entire-* commands
│   └── github_cache.py              # GitHub PR/issue count cache
├── tests/
│   └── run_tests.sh                  # 132 tests
└── docs/
    ├── roadmap-v1.5.md
    ├── multi-root-design.md
    └── v1.5-execution-board.md
```

## License

[MIT](LICENSE)
