---
name: mupibox-media-db
description: "Manage MuPiBox media database (data.json) through the MuPiBox backend API: list, add, remove, move, edit fields, and restore entries."
---

# MuPiBox Media DB

Manage the MuPiBox media database (`data.json`) via the backend API.

## Requirements

- Access to a running MuPiBox backend instance (MuPiBox host is often `http://mupibox/`, API for this script defaults to `http://mupibox:8200`; override with `--base-url`)
- Python 3
- Bundled script available at `./scripts/mupibox_media_manager.py`

## API basics

- Read: `GET /api/data`
- Write: `POST /api/add`, `POST /api/edit`, `POST /api/delete`

## Example commands

> Script path: `./scripts/mupibox_media_manager.py`. Default API endpoint is `http://mupibox:8200` (override with `--base-url`).

```bash
# Show list
python3 ./scripts/mupibox_media_manager.py --base-url <BASE_URL> list --limit 30

# Filter (for example spotify + music)
python3 ./scripts/mupibox_media_manager.py --base-url <BASE_URL> list --type spotify --category music --limit 100

# Manual backup
python3 ./scripts/mupibox_media_manager.py --base-url <BASE_URL> backup
```

## Add entries

```bash
# 1) Raw JSON
python3 ./scripts/mupibox_media_manager.py --base-url <BASE_URL> add \
  --json '{"type":"spotify","category":"audiobook","artist":"Example Artist","id":"SPOTIFY_ID"}'

# 2) Spotify URL with automatic ID extraction
python3 ./scripts/mupibox_media_manager.py --base-url <BASE_URL> add \
  --type spotify --category audiobook --artist "Example Artist" \
  --spotify-url "https://open.spotify.com/album/SPOTIFY_ID"
```

## Remove entries

```bash
# By index
python3 ./scripts/mupibox_media_manager.py --base-url <BASE_URL> remove --index 42

# By Spotify ID
python3 ./scripts/mupibox_media_manager.py --base-url <BASE_URL> remove --spotify-id SPOTIFY_ID
```

## Move / reorder

```bash
python3 ./scripts/mupibox_media_manager.py --base-url <BASE_URL> move --from 20 --to 3
```

## Update fields

```bash
python3 ./scripts/mupibox_media_manager.py --base-url <BASE_URL> set --index 10 \
  --field artist="New Artist" \
  --field category="audiobook" \
  --field shuffle=true
```

`--field` accepts JSON values (`true`, `false`, numbers, strings).

## Restore

```bash
python3 ./scripts/mupibox_media_manager.py --base-url <BASE_URL> restore \
  --file ~/.mupibox-db-backups/data-YYYYMMDD-HHMMSS-before-add.json
```

## Agent workflow

1. For `add`: resolve missing IDs/metadata first, then add.
2. For `remove`: identify entry via `list` first, then remove.
3. For `move`: confirm target positions, then move.
4. Verify changes using `list`.

## Quality checks for Spotify audiobooks

- Prefer album IDs over playlist IDs (unless playlists are explicitly requested).
- Avoid box sets/compilations when a single canonical release is intended.
- Choose consistent versions when duplicates exist.
- Ask for clarification if uncertain instead of adding blindly.

## Safety

- No external side effects outside the MuPiBox API.
- The bundled script creates a local backup before mutations.
- Restore only from trusted backup files.
- On failure, report the latest backup file.