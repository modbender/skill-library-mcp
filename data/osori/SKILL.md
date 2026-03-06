---
name: osori
description: "Osori v1.6.1 — Local project registry & context loader with Telegram slash commands. Registry versioning + auto-migration + root filters + root management + doctor (preview-first + risk gate) + safe root remove + switch multi-match + GitHub count cache + alias/favorite + Entire integration commands. Find, switch, list, add/remove projects, check status. Triggers: work on X, find project X, list projects, project status, project switch. | 오소리 — 텔레그램 슬래시 명령어 지원 로컬 프로젝트 레지스트리."
homepage: https://github.com/oozoofrog/osori
metadata: { "openclaw": { "emoji": "🦦", "requires": { "bins": ["python3", "git", "gh"] }, "os": ["darwin", "linux"] } }
---

# Osori (오소리)

Local project registry & context loader for AI agents.

## Prerequisites

- **macOS**: `mdfind` (Spotlight, built-in), `python3`, `git`, `gh` CLI
- **Linux**: `mdfind` unavailable → uses `find` as fallback automatically. `python3`, `git`, `gh` CLI required.
- **Entire integration (optional)**: `entire` CLI installed (for `/entire-*` commands)

## Dependencies

- **python3** — Required. Used for JSON processing.
- **git** — Project detection and status checks.
- **entire** — Optional. Required only for `/entire-status`, `/entire-enable`, `/entire-rewind-list`.

## Telegram Bot Commands (Updated in v1.6.1)

Osori now supports Telegram slash commands for quick project management:

```
/list [root] — Show registered projects (optional root filter)
/status [root] — Check status of projects (optional root filter)
/find <name> [root|--root <root>] — Find a project by name (optional root scope)
/switch <name> [root|--root <root>] [--index <n>] — Switch to project and load context (multi-match selection)
/fingerprints [name] [--root <root>] — Show repo remote + last commit + open PR/issue counts
/doctor [--fix] [--dry-run] [--yes] [--json] — Registry health check (preview-first, risk-gated)
/list-roots — List roots, labels, paths, and project counts
/root-add <key> [label] — Add root (or update label)
/root-path-add <key> <path> — Add discovery path to root
/root-path-remove <key> <path> — Remove discovery path from root
/root-set-label <key> <label> — Update root label
/root-remove <key> [--reassign <target>] [--force] — Safely remove root
/alias-add <alias> <project> — Add alias for project
/alias-remove <alias> — Remove alias
/favorites — Show favorite projects
/favorite-add <project> — Mark project as favorite
/favorite-remove <project> — Unmark favorite
/entire-status <project> [root|--root <root>] — Show Entire status in a project
/entire-enable <project> [root|--root <root>] [--agent <name>] [--strategy <name>] — Enable Entire in a project
/entire-rewind-list <project> [root|--root <root>] — List rewind points in a project
/add <path> — Add project to registry
/remove <name> — Remove project from registry
/scan <path> [root] — Scan directory for git projects, optional root key
/help — Show command help
```

### Setup

Add to your OpenClaw agent's TOOLS.md or Telegram bot config:

```bash
# In Telegram bot commands (BotFather)
list - Show all projects (or by root)
status - Check project statuses (or by root)
find - Find project by name
switch - Switch to project
fingerprints - Show repo/commit/PR/issue fingerprint
doctor - Health check (preview-first, risk-gated fix)
list-roots - Show roots and discovery paths
root-add - Add root
root-path-add - Add path to root
root-path-remove - Remove path from root
root-set-label - Rename root label
root-remove - Safely remove root (with reassign/force options)
alias-add - Add alias for a project
alias-remove - Remove alias
favorites - Show favorite projects
favorite-add - Mark favorite project
favorite-remove - Unmark favorite project
entire-status - Show Entire status for a project
entire-enable - Enable Entire for a project
entire-rewind-list - List rewind points for a project
add - Add project to registry
remove - Remove project
scan - Scan directory (optional root)
help - Show help
```

### Usage Examples

```
/list work
/status personal
/find agent-avengers work
/switch Tesella --root personal
/switch Tesella --root personal --index 1
/fingerprints Tesella --root personal
/doctor --fix
/list-roots
/root-add work Work
/root-path-add work /path/to/workspace
/root-remove work --reassign default
/alias-add rh RunnersHeart
/favorite-add RunnersHeart
/favorites
/entire-status osori
/entire-enable osori --agent claude-code --strategy manual-commit
/add /Volumes/disk/MyProject
/scan /path/to/workspace work
```

## Registry

`${OSORI_REGISTRY:-$HOME/.openclaw/osori.json}`

Override with the `OSORI_REGISTRY` environment variable.

### Versioning & Migration (v1.6.1)

- Current schema: `osori.registry`
- Current version: `2`
- On every load, Osori auto-migrates older registry formats:
  - legacy array (`[]`) → versioned object
  - object without `schema/version` → normalized versioned object
- Normalized registry fields:
  - top-level `roots[]`
  - top-level `aliases{}` (alias → project name)
  - each `projects[]` item includes `favorite: bool`
- Migration safety:
  - creates backup: `osori.json.bak-<timestamp>`
  - corrupted JSON is preserved as: `osori.json.broken-<timestamp>`
  - write path uses atomic replace + rollback fallback

## Finding Projects (when path is unknown)

When the project path is unknown, search in order:

1. **Registry lookup** — Fuzzy match name in `osori.json`
2. **mdfind** (macOS only) — `mdfind "kMDItemFSName == '<name>'" | head -5`
3. **find fallback** — Search priority:
   1) `roots[].paths` from registry (if root is specified, that root first)
   2) paths from `OSORI_SEARCH_PATHS`
   Command form: `find <search_paths> -maxdepth 4 -type d -name '<name>' 2>/dev/null`
4. **Ask the user** — If all methods fail, ask for the project path directly.
5. Offer to register the found project in the registry.

## Commands

### List
Show all registered projects. Optional root filter supported in Telegram command:

```bash
/list [root]
```

(Example: `/list work`)

### Switch
Supports optional root scope and explicit candidate selection:

```bash
/switch <name> [root|--root <root>] [--index <n>]
```

Flow:
1. Search registry (fuzzy match, root-scoped if provided)
2. If multiple matches:
   - show candidate list (name/root/path/last commit/dirty/score)
   - `--index <n>` to pick explicitly
   - no index => auto-pick highest score
3. If not found → run "Finding Projects" flow above and suggest add path
4. Load context:
   - `git status --short`
   - `git branch --show-current`
   - `git log --oneline -5`
   - `gh issue list -R <repo> --limit 5` (when repo is set)
5. Present summary

Auto score policy:
- +50 root exact (if root scope provided)
- +30 name exact
- +20 name prefix
- +10 latest commit recency
- -10 missing path
- -5 repo missing
- tie-break: latest commit, then name

### Fingerprints
Show a one-shot project fingerprint view:
- repo remote URL
- last commit hash/date
- open PR count
- open issue count

```bash
bash {baseDir}/scripts/project-fingerprints.sh [project-name]
bash {baseDir}/scripts/project-fingerprints.sh --root <root-key> [project-name]
```

GitHub open-count cache (PR/Issue):
- default cache file: `$HOME/.openclaw/osori-cache.json`
- default TTL: `600` seconds
- env overrides:
  - `OSORI_CACHE_FILE`
  - `OSORI_CACHE_TTL`

### Add
```bash
bash {baseDir}/scripts/add-project.sh <path> [--tag <tag>] [--name <name>]
```
Auto-detects: git remote, language, description.

### Scan
```bash
bash {baseDir}/scripts/scan-projects.sh <root-dir> [--depth 3]
OSORI_ROOT_KEY=work bash {baseDir}/scripts/scan-projects.sh <root-dir> [--depth 3]
```
Bulk-scan a directory for git repos and add them to the registry.

Telegram command supports optional root key too:

```bash
/scan <path> [root]
```

### Remove
Delete an entry from `osori.json` by name.

### Status
Run `git status` + `gh issue list` for one or all projects.

Telegram root filter:

```bash
/status [root]
```

### Doctor
Registry health check with preview-first pipeline and risk-gated fixes.

**Default** (no flags): analyze + preview plan — no changes applied.

```bash
/doctor                     # preview only (default)
/doctor --fix               # preview + apply (high-risk blocked)
/doctor --fix --yes         # preview + apply all (including high-risk)
/doctor --dry-run           # explicit preview only (never applies)
/doctor --json              # machine-readable JSON output
```

Risk levels:
- 🟢 **low** — schema normalization, migration, missing fields
- 🟡 **medium** — duplicate removal, root reference repair
- 🔴 **high** — registry re-initialization from corrupted state

Shell equivalent:

```bash
bash {baseDir}/scripts/doctor.sh [--fix] [--dry-run] [--yes] [--json]
```

See also: [Doctor Safe Fix Guide](docs/examples/doctor-safe-fix.md)

### Root Management

```bash
/list-roots
/root-add <key> [label]
/root-path-add <key> <path>
/root-path-remove <key> <path>
/root-set-label <key> <label>
/root-remove <key> [--reassign <target>] [--force]
```

Shell equivalents:

```bash
bash {baseDir}/scripts/root-manager.sh list
bash {baseDir}/scripts/root-manager.sh add <key> [label]
bash {baseDir}/scripts/root-manager.sh path-add <key> <path>
bash {baseDir}/scripts/root-manager.sh path-remove <key> <path>
bash {baseDir}/scripts/root-manager.sh set-label <key> <label>
bash {baseDir}/scripts/root-manager.sh remove <key> [--reassign <target>] [--force]
```

Safety rules for remove:
- `default` root cannot be removed
- if projects exist in root:
  - `--reassign <target>` to move projects then remove
  - or `--force` to move projects to `default` and remove

### Alias & Favorites

```bash
/alias-add <alias> <project>
/alias-remove <alias>
/favorites
/favorite-add <project>
/favorite-remove <project>
```

Shell equivalents:

```bash
bash {baseDir}/scripts/alias-favorite-manager.sh alias-add <alias> <project>
bash {baseDir}/scripts/alias-favorite-manager.sh alias-remove <alias>
bash {baseDir}/scripts/alias-favorite-manager.sh aliases
bash {baseDir}/scripts/alias-favorite-manager.sh favorite-add <project>
bash {baseDir}/scripts/alias-favorite-manager.sh favorite-remove <project>
bash {baseDir}/scripts/alias-favorite-manager.sh favorites
```

Aliases are case-insensitive and are resolved by `/find`, `/switch`, and `project-fingerprints.sh` name queries.

### Entire Integration

Run Entire CLI commands in a registered project context:

```bash
/entire-status <project> [root|--root <root>]
/entire-enable <project> [root|--root <root>] [--agent <name>] [--strategy <name>]
/entire-rewind-list <project> [root|--root <root>]
```

Shell equivalent:

```bash
bash {baseDir}/scripts/entire-manager.sh status <project> [root|--root <root>]
bash {baseDir}/scripts/entire-manager.sh enable <project> [root|--root <root>] [entire enable flags...]
bash {baseDir}/scripts/entire-manager.sh rewind-list <project> [root|--root <root>]
```

Defaults:
- `entire enable` defaults to `--agent claude-code --strategy manual-commit` when not provided.
- `/entire-rewind-list` uses non-destructive JSON listing (`entire rewind --list`).

## Schema

```json
{
  "schema": "osori.registry",
  "version": 2,
  "updatedAt": "2026-02-16T00:00:00Z",
  "roots": [
    {
      "key": "default",
      "label": "Default",
      "paths": []
    }
  ],
  "aliases": {
    "rh": "RunnersHeart"
  },
  "projects": [
    {
      "name": "string",
      "path": "/absolute/path",
      "repo": "owner/repo",
      "lang": "swift|typescript|python|rust|go|ruby|unknown",
      "tags": ["personal", "ios"],
      "description": "Short description",
      "addedAt": "YYYY-MM-DD",
      "root": "default",
      "favorite": false
    }
  ]
}
```

## Auto-trigger Rules

- "work on X" / "X 프로젝트 작업하자" → switch X
- "find project X" / "X 찾아줘" / "X 경로" → registry search or discover
- "list projects" / "프로젝트 목록" → list
- "add project" / "프로젝트 추가" → add
- "project status" / "프로젝트 상태" → status all
