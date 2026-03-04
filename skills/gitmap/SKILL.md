# GitMap Skill

Version control for ArcGIS web maps — exposed as native OpenClaw tools.

## Overview

GitMap provides Git-like version control for ArcGIS Online and Enterprise Portal web maps. This skill wraps the `gitmap` CLI as thin subprocess calls, exposing branch, commit, diff, push/pull, and map discovery as callable tools.

**8 tools** | Thin CLI wrapper | No local database | Requires: `gitmap-core` Python package

---

## Prerequisites

### Install GitMap Core

```bash
pip install gitmap-core
```

### Configure Credentials

Set the following environment variables:

```bash
export PORTAL_URL="https://your-org.maps.arcgis.com"
export ARCGIS_USERNAME="your_username"
export ARCGIS_PASSWORD="your_password"
```

**Security Note:** Prefer using scoped API tokens over plaintext passwords when possible.

---

## Required environment variables

- **PORTAL_URL**: Your ArcGIS Portal or AGOL URL (e.g., `https://myorg.maps.arcgis.com`)
- **ARCGIS_USERNAME**: Portal username
- **ARCGIS_PASSWORD**: Portal password (prefer scoped API tokens over plaintext passwords)

---

## Tools

### Discovery & Status

- `gitmap_list` — List available web maps from Portal (with optional filters)
- `gitmap_status` — Show working tree status for a local GitMap repo
- `gitmap_log` — View commit history for a repo

### Versioning

- `gitmap_commit` — Commit current map state with a message
- `gitmap_branch` — List or create branches in a repo
- `gitmap_diff` — Show changes between commits or branches

### Portal Sync

- `gitmap_push` — Push committed changes to ArcGIS Portal
- `gitmap_pull` — Pull latest map from ArcGIS Portal

---

## Tool Reference

### `gitmap_list`

Discover web maps in Portal.

```python
gitmap_list(
    query=None,        # Search query (e.g., "title:MyMap")
    owner=None,        # Filter by owner username
    tag=None,          # Filter by tag
    max_results=50,    # Max results to return
    portal_url=None,   # Portal URL (or use PORTAL_URL env var)
    username=None,     # Portal username (or ARCGIS_USERNAME env var)
    password=None,     # Portal password (or ARCGIS_PASSWORD env var)
    cwd=None,          # Working directory (default: home)
)
```

### `gitmap_status`

Show repo status.

```python
gitmap_status(
    cwd,               # Path to GitMap repository (required)
)
```

### `gitmap_commit`

Commit current changes.

```python
gitmap_commit(
    message,           # Commit message (required)
    cwd,               # Path to GitMap repository (required)
    author=None,       # Override commit author
)
```

### `gitmap_branch`

List or create branches.

```python
gitmap_branch(
    cwd,               # Path to GitMap repository (required)
    name=None,         # Branch name to create (omit to list)
    delete=False,      # Delete the named branch
)
```

### `gitmap_diff`

Show changes between versions.

```python
gitmap_diff(
    cwd,               # Path to GitMap repository (required)
    branch=None,       # Compare with this branch
    commit=None,       # Compare with this commit hash
)
```

### `gitmap_push`

Push changes to Portal.

```python
gitmap_push(
    cwd,               # Path to GitMap repository (required)
    branch=None,       # Branch to push (default: current)
    portal_url=None,   # Portal URL
    username=None,     # Portal username
    password=None,     # Portal password
)
```

### `gitmap_pull`

Pull changes from Portal.

```python
gitmap_pull(
    cwd,               # Path to GitMap repository (required)
    branch=None,       # Branch to pull (default: current)
    portal_url=None,   # Portal URL
    username=None,     # Portal username
    password=None,     # Portal password
)
```

### `gitmap_log`

View commit history.

```python
gitmap_log(
    cwd,               # Path to GitMap repository (required)
    branch=None,       # Branch to show log for
    limit=None,        # Max commits to show
)
```

---

## Usage Examples

### Discover Maps and Clone

```python
# Find maps owned by a user
gitmap_list(owner="john.doe", max_results=20)
# → returns table of maps with item IDs

# Then clone manually:
# cd ~/maps && gitmap clone <item_id>
```

### Typical Edit → Commit → Push Loop

```python
# Check what changed
gitmap_status(cwd="~/maps/MyWebMap")

# Commit changes
gitmap_commit(message="Updated layer symbology", cwd="~/maps/MyWebMap")

# Push to Portal
gitmap_push(cwd="~/maps/MyWebMap")
```

### Feature Branch Workflow

```python
# List branches
gitmap_branch(cwd="~/maps/MyWebMap")

# Create a feature branch
gitmap_branch(name="feature/new-basemap", cwd="~/maps/MyWebMap")

# After editing, commit and push feature branch
gitmap_commit(message="Added satellite basemap", cwd="~/maps/MyWebMap")
gitmap_push(cwd="~/maps/MyWebMap", branch="feature/new-basemap")
```

### Review History

```python
# Recent commits
gitmap_log(cwd="~/maps/MyWebMap", limit=10)

# What changed since main?
gitmap_diff(cwd="~/maps/MyWebMap", branch="main")
```

---

## Server

HTTP server at `localhost:7400` (when running):

```bash
python server.py
```

Endpoints:
- `POST /tools/{tool_name}` — Call a tool with JSON body
- `GET /health` — Health check

---

## Installation

**Install command:**

```bash
pip install gitmap-core
```

The skill uses the `gitmap_core` Python package directly for API access.

---

## Notes & Known Limitations

- **Working directory is required** for most commands — GitMap repos are directory-based like Git.
- **Portal credentials** can be passed per-call or via environment variables (PORTAL_URL, ARCGIS_USERNAME, ARCGIS_PASSWORD).
- **`gitmap list`** doesn't require a local repo — it queries Portal directly.
- **Output is raw CLI text** — parsed lightly for structured responses where possible.
 NOT implement `clone`, `init`,- This skill does `merge`, `checkout`, `l`, or `setupsm`, `context-repos` — call the CLI directly for those.

---

## Related

- GitMap Project: https://github.com/14-TR/gitmap
