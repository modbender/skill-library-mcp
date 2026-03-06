# Architecture Overview

Technical reference for contributors and maintainers.

## System Diagram

```
┌────────────────────────────────────────────────┐
│                  SKILL.md                       │
│  (AI instructions — intent detection, routing)  │
└──────────────────┬─────────────────────────────┘
                   │ calls
                   ▼
┌──────────────────────────────────────────┐
│            Python Scripts                │
│                                          │
│  ┌──────────────┐  ┌─────────────────┐   │
│  │ file_manager │  │ config_manager  │   │
│  │  (CRUD ops)  │  │  (settings)     │   │
│  └──────┬───────┘  └────────┬────────┘   │
│         │                   │            │
│  ┌──────┴───────┐  ┌───────┴────────┐   │
│  │index_manager │  │dashboard_server│   │
│  │  (search)    │  │  (HTTP + API)  │   │
│  └──────┬───────┘  └───────┬────────┘   │
│         │                   │            │
│  ┌──────┴───────────────────┴────────┐   │
│  │            utils.py               │   │
│  │  (slugs, YAML, file I/O, IDs)    │   │
│  └───────────────────────────────────┘   │
└──────────────────┬───────────────────────┘
                   │ reads/writes
                   ▼
┌──────────────────────────────────────────┐
│           Workspace (filesystem)         │
│                                          │
│  .nlplanner/config.json                  │
│  projects/*/README.md                    │
│  projects/*/tasks/task-NNN.md            │
│  projects/*/attachments/*                │
│  archive/...                             │
└──────────────────────────────────────────┘
                   ▲
                   │ serves via HTTP
┌──────────────────┴───────────────────────┐
│         Dashboard (browser)              │
│                                          │
│  index.html + app.js + styles.css        │
│  ┌─────────────────────────────┐         │
│  │ Kanban │ Projects │ Timeline│         │
│  └─────────────────────────────┘         │
│  Polls /api/* endpoints for data         │
└──────────────────────────────────────────┘
```

## Module Responsibilities

### `utils.py` — Foundation Layer

Shared utilities with zero internal dependencies.

| Function | Purpose |
|---|---|
| `generate_slug()` | Filesystem-safe names from text |
| `generate_task_id()` | Sequential `task-NNN` IDs |
| `parse_frontmatter()` | YAML frontmatter → dict + body |
| `serialize_frontmatter()` | dict + body → Markdown string |
| `safe_read_file()` / `safe_write_file()` | Error-handled file I/O |
| `ensure_directory()` | Recursive mkdir |
| `validate_status()` / `validate_priority()` | Input validation |

### `config_manager.py` — Settings

Manages `.nlplanner/config.json`. Provides typed getters/setters for all
user-configurable settings. Merges with defaults so new settings are always
available after upgrades.

**Key design decision**: The config path is set once via `set_config_path()`
and cached at module level. This avoids threading the workspace path through
every function call.

### `file_manager.py` — Core CRUD

All create/read/update/list/archive operations for projects and tasks.

**Key functions**:
- `init_workspace()` — creates the full directory tree
- `create_project()` / `create_task()` — write new Markdown files
- `get_project()` / `get_task()` — read and parse files
- `list_tasks()` — glob-based listing with filter support
- `update_task()` — merge updates into existing frontmatter
- `archive_task()` / `archive_project()` — move to `archive/`
- `move_task()` — relocate between projects
- `link_tasks()` — add dependency relationships (with circular check)

**Task ID strategy**: Sequential counters (`task-001`, `task-002`, ...) scanned
from all existing files. This is simple, human-readable, and avoids conflicts
as long as there's a single writer (the AI assistant).

### `index_manager.py` — Search & Analytics

In-memory index rebuilt from disk on demand. Provides:
- Full-text search across titles, bodies, tags
- Due-soon / overdue queries
- Check-in staleness detection
- Summary statistics

The index is also persisted to `.nlplanner/index.json` (without body text)
for potential future use by external tools.

### `dashboard_server.py` — Web Interface

Lightweight HTTP server using Python's `http.server` stdlib module.

**Static files**: Served from `templates/dashboard/` (or workspace copy).

**API routes**:

| Endpoint | Returns |
|---|---|
| `GET /api/stats` | Summary statistics |
| `GET /api/projects` | All projects |
| `GET /api/tasks` | All tasks (filterable via query params) |
| `GET /api/task/<id>` | Single task detail |
| `GET /api/project/<id>` | Single project detail |
| `GET /api/search?q=...` | Search results |
| `GET /api/due-soon?days=N` | Tasks due within N days |
| `GET /api/overdue` | Overdue tasks |

**Threading**: The server runs in a daemon thread so it doesn't block the
AI assistant. `start_dashboard()` / `stop_dashboard()` control the lifecycle.

## Data Format

### Frontmatter Schema — Tasks

```yaml
id: task-001          # Unique, sequential
title: string         # Short description
project: string       # Parent project slug
status: todo | in-progress | done | archived
priority: low | medium | high
created: YYYY-MM-DD
due: YYYY-MM-DD | ''
last_checkin: YYYY-MM-DD
tags: [string]
dependencies: [task-id]
```

### Frontmatter Schema — Projects

```yaml
id: project-slug      # URL/filesystem-safe
title: string
created: YYYY-MM-DD
status: active | archived
tags: [string]
color: '#hex'         # Accent colour — auto-assigned from palette, user-overridable
```

## Error Handling Strategy

1. All file I/O goes through `safe_read_file()` / `safe_write_file()` which
   catch OS errors and return `None` / `False`.
2. Functions that can fail return `Optional` types — callers check for `None`.
3. The `logging` module is used throughout (never `print()`).
4. Validation functions (`validate_status`, etc.) reject bad input before
   it reaches the filesystem.

## Cross-Platform Notes

- All paths use `pathlib.Path` — forward/backward slashes handled automatically.
- `~` expansion via `Path.expanduser()`.
- File encoding is always UTF-8.
- The dashboard binds to `127.0.0.1` by default. Set
  `dashboard_allow_network` to `true` to bind to `0.0.0.0` (all
  interfaces) for LAN access on headless / remote devices.

## Extension Points

The architecture is designed to be extended:

- **New file types**: Add a new `create_*` / `get_*` pattern in `file_manager.py`
- **New API endpoints**: Add routes in `DashboardHandler._handle_api()`
- **New dashboard views**: Add HTML section + JS render function + CSS
- **Import/export**: Write converters that read/write the Markdown format
- **CLI**: Import `file_manager` functions directly from a CLI script
- **Sync**: The Markdown-on-filesystem design is naturally git-friendly

## Performance Considerations

- **< 100 tasks**: No optimisation needed; glob scanning is fast.
- **100–1000 tasks**: The in-memory index helps; `rebuild_index()` scans once.
- **1000+ tasks**: Consider adding SQLite as an optional index backend
  (the Markdown files remain the source of truth).

## Security

- Dashboard runs on `127.0.0.1` by default (not accessible from network).
  When `dashboard_allow_network` is enabled it binds to `0.0.0.0`.
- No authentication — when network access is enabled, anyone on the LAN
  can view the dashboard.
- No data leaves the machine.
- File operations are confined to the workspace directory.
