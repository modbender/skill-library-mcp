---
name: nextcloud
description: "Nextcloud file and folder management via WebDAV + OCS API. Use when: (1) creating, reading, writing, renaming, moving, copying, or deleting files/folders, (2) listing or searching directory contents, (3) toggling favorites or managing system tags, (4) checking storage quota. NOT for: Nextcloud Talk, Calendar/Contacts (use CalDAV), app management (requires admin), large binary transfers, or creating share links (share capability not included by default - see README)."
homepage: https://github.com/rwx-g/openclaw-skill-nextcloud
compatibility: Python 3.9+ · no external dependencies · network access to Nextcloud instance
metadata:
  {
    "openclaw": {
      "emoji": "☁️",
      "requires": { "env": ["NC_URL", "NC_USER", "NC_APP_KEY"] },
      "primaryEnv": "NC_APP_KEY"
    }
  }
ontology:
  reads: [files, folders, user, quota, capabilities]
  writes: [files, folders, tags, favorites]
---

# Nextcloud Skill

Full Nextcloud client: WebDAV (files/folders) + OCS (tags, user info). Zero external dependencies - stdlib only (urllib).
Credentials: `~/.openclaw/secrets/nextcloud_creds` · Config: `~/.openclaw/config/nextcloud/config.json`

## Trigger phrases

Load this skill immediately when the user says anything like:

- "upload / save / write this file on Nextcloud / NC / cloud"
- "create a folder on Nextcloud", "mkdir in NC"
- "list / browse / show what's in [folder] on Nextcloud"
- "search for [file] in NC", "find [file] on Nextcloud"
- "read / get / download [file] from Nextcloud"
- "rename / move / copy [file] on Nextcloud"
- "check my storage quota", "how much space on NC"
- "tag this file", "mark as favorite on Nextcloud"

## Quick Start

```bash
python3 scripts/nextcloud.py config    # verify credentials + active config
python3 scripts/nextcloud.py quota     # test connection + show storage
python3 scripts/nextcloud.py ls /      # list root directory
```

## Setup

```bash
python3 scripts/setup.py       # interactive: credentials + permissions + connection test
python3 scripts/init.py        # validate all configured permissions against live instance
```

> init.py only runs write/delete tests when both `allow_write=true` and `allow_delete=true`. When `allow_delete=false`, write tests are skipped - no test artifacts are created or left behind.

**Manual** - `~/.openclaw/secrets/nextcloud_creds` (chmod 600):
```
NC_URL=https://cloud.example.com
NC_USER=username
NC_APP_KEY=app-password
```
App password: Nextcloud → Settings → Security → App passwords.

**config.json** - behavior restrictions:

| Key | Default | Effect |
|-----|---------|--------|
| `base_path` | `"/"` | Restrict agent to subtree (e.g. `"/Jarvis"`) |
| `allow_write` | `false` | mkdir, write, rename, copy (enable explicitly) |
| `allow_delete` | `false` | delete files and folders (enable explicitly) |
| `readonly_mode` | `false` | override: block all writes regardless of above |

> **Safe defaults:** both `allow_write` and `allow_delete` are `false` by default. Enable each explicitly only when needed. Combine with a restricted `base_path` (e.g. `"/Jarvis"`) to limit the agent's scope.
> **Share capability** is not included by default. See README for instructions on how to restore it if needed.

## Storage & credentials

The skill reads and writes the following paths. All usage is intentional and documented:

| Path | Written by | Purpose |
|------|-----------|---------|
| `~/.openclaw/secrets/nextcloud_creds` | `setup.py` | Nextcloud credentials (NC_URL, NC_USER, NC_APP_KEY). chmod 600. Never committed. |
| `~/.openclaw/config/nextcloud/config.json` | `setup.py` | Behavior restrictions (base_path, allow_write, allow_delete, readonly_mode). No secrets. Not in skill dir - survives clawhub updates. |

Credentials can also be provided via environment variables (`NC_URL`, `NC_USER`, `NC_APP_KEY`) instead of the creds file. The skill checks env vars first.

**Cleanup on uninstall:** `clawhub uninstall nextcloud-files` removes the skill directory. To also remove credentials and config:
```bash
python3 scripts/setup.py --cleanup
```
On reinstall, any existing config at `~/.openclaw/config/nextcloud/config.json` is picked up automatically.

## Module usage

```python
from scripts.nextcloud import NextcloudClient
nc = NextcloudClient()
nc.write_file("/Jarvis/notes.md", "# Notes\n...")
nc.mkdir("/Jarvis/Articles")
items = nc.list_dir("/Jarvis")
```

## CLI reference

```bash
# Files & folders
python3 scripts/nextcloud.py mkdir /path/folder
python3 scripts/nextcloud.py write /path/file.md --content "# Title"
python3 scripts/nextcloud.py write /path/file.md --file local.md
python3 scripts/nextcloud.py write /path/file.md --content "new entry" --append
python3 scripts/nextcloud.py read  /path/file.md
python3 scripts/nextcloud.py rename /old /new
python3 scripts/nextcloud.py copy   /src /dst
python3 scripts/nextcloud.py delete /path
python3 scripts/nextcloud.py exists /path          # exit 0/1

# Listing & search
python3 scripts/nextcloud.py ls /path --depth 2 --json
python3 scripts/nextcloud.py search "keyword" --path /folder --limit 20

# Favorites & tags
python3 scripts/nextcloud.py favorite /path/file.md
python3 scripts/nextcloud.py tags
python3 scripts/nextcloud.py tag-create "research"
python3 scripts/nextcloud.py tag-assign <file_id> <tag_id>

# Account
python3 scripts/nextcloud.py quota
python3 scripts/nextcloud.py config
```

## Templates

### Structured workspace setup
```bash
python3 scripts/nc_setup.py --root Jarvis --folders Articles,LinkedIn,Recherche,Veille
```

### Append to a running log
```python
nc.append_to_file("/Jarvis/log.md", f"\n## {today}\n{entry}\n")
```

### Read and update a JSON list
```python
items = nc.read_json("/Jarvis/Veille/articles.json")
items["articles"].append(new_article)
nc.write_json("/Jarvis/Veille/articles.json", items)
```

### Tag a file after creation
```python
ls = nc.list_dir("/Jarvis/Articles", depth=1)
file_id = next(f["file_id"] for f in ls if f["name"] == "article.md")
tags = nc.get_tags()
tag_id = next(t["id"] for t in tags if t["name"] == "published")
nc.assign_tag(file_id, tag_id)
```

## Ideas
- Sandbox the agent with `base_path: "/Jarvis"` - it can't touch anything else
- Store agent-produced Markdown files and auto-share a read-only link in the reply
- Use `append_to_file` for rolling logs or changelogs
- Use `write_json` + `read_json` for persistent state between sessions
- Auto-tag files by category (research / draft / published)

## Combine with

| Skill | Workflow |
|-------|----------|
| **ghost** | Write a post → save Markdown draft to NC → publish to Ghost |
| **summarize** | Summarize a URL → save summary as `.md` to NC |
| **gmail** | Receive an attachment → save to NC for archiving |
| **obsidian** | Sync Obsidian vault notes to NC for remote backup |
| **self-improving-agent** | Log agent learnings to NC for persistent, searchable history |

## API reference
See `references/api.md` for WebDAV/OCS endpoint details, PROPFIND properties, and error codes.

## Troubleshooting
See `references/troubleshooting.md` for common errors and fixes.
