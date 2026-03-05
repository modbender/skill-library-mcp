# Read Layer (Spotify-first)

Goal: Read as much as Spotify allows (user scopes permitting), store unique payloads, and track counters.

## Current covered endpoints
- `GET /me` -> source `profile`
- `GET /me/player/currently-playing` -> source `currently-playing`
- `GET /me/player/recently-played?limit=50` -> source `recently-played`
- `GET /me/top/tracks?time_range=short_term&limit=50` -> source `top-short`
- `GET /me/top/tracks?time_range=medium_term&limit=50` -> source `top-medium`
- `GET /me/top/tracks?time_range=long_term&limit=50` -> source `top-long`
- `GET /me/playlists?limit=50` -> source `playlists`

## Run single source (recommended)
From `skills/spotify-intelligence`:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run-with-vault-env.ps1 -Command "powershell -ExecutionPolicy Bypass -File .\scripts\read\sync-read-one.ps1 -Source recently-played -Limit 20 -MaxPages 1"
```

List available sources:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\read\list-read-sources.ps1
```

Safe small batch (disk-friendly):

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run-with-vault-env.ps1 -Command "powershell -ExecutionPolicy Bypass -File .\scripts\read\sync-safe-sample.ps1"
```

## Run full read-sync
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run-with-vault-env.ps1 -Command "powershell -ExecutionPolicy Bypass -File .\scripts\read\sync-read-all.ps1"
```

## Sync playlist track memberships (added_at etc.)
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run-with-vault-env.ps1 -Command "powershell -ExecutionPolicy Bypass -File .\scripts\read\sync-playlist-items.ps1 -MaxPlaylists 50 -TracksPerPlaylist 200"
```

## Sync Spotify track feature flags (energy/tempo/valence etc.)
Liked Songs:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run-with-vault-env.ps1 -Command "powershell -ExecutionPolicy Bypass -File .\scripts\read\sync-track-features.ps1 -Mode liked -LimitTracks 500"
```

Specific playlist:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run-with-vault-env.ps1 -Command "powershell -ExecutionPolicy Bypass -File .\scripts\read\sync-track-features.ps1 -Mode playlist -PlaylistName 'Lieblingssongs' -LimitTracks 500"
```

Fast/high-energy query:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\read\query-fast-liked.ps1 -MinEnergy 0.7 -MinTempo 120 -Top 50
```

Hinweis: Sync läuft als Playlist-Snapshot. Tracks, die im neuesten Snapshot fehlen, werden in `playlist_track_membership` auf `currently_present=0` gesetzt und zusätzlich in `playlist_track_removals` archiviert (statt gelöscht).

## Removal/Restore Workflow (DB-first)
Removal-Log lesen:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\read\query-removal-log.ps1 -Top 100 -OnlyAvailable
```

Restore-Intent markieren:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\read\mark-restore-intent.ps1 -RemovalId 42 -Status restore_pending
```

Einzelne Wiederherstellung via Spotify API:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run-with-vault-env.ps1 -Command "powershell -ExecutionPolicy Bypass -File .\scripts\read\restore-from-removal.ps1 -RemovalId 42"
```

Batch-Wiederherstellung aller `restore_pending`:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run-with-vault-env.ps1 -Command "powershell -ExecutionPolicy Bypass -File .\scripts\read\restore-pending.ps1 -Limit 20"
```

Dry-run (ohne API-Write):
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run-with-vault-env.ps1 -Command "powershell -ExecutionPolicy Bypass -File .\scripts\read\restore-pending.ps1 -Limit 20 -DryRun"
```

## Output
- One line per source with ingest result
- SQLite DB updated at `data/spotify-intelligence.sqlite`
- Duplicate payloads are counted, not re-stored

## Pagination + performance telemetry
- `sync-read-one.ps1` paginiert über `next` (wenn vorhanden) und `-MaxPages`.
- `sync-playlist-items.ps1` lädt Playlist-Tracks seitenweise (`limit/offset`).
- Jede API-Seite wird in `api_request_metrics` protokolliert (Latenz, Bytes, Items, Status, Fehler).

Strategie-Auswertung:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\read\query-sync-strategy.ps1
```

Aktivitätsadaptiver Plan (wichtig wenn du Tage gar nicht hörst):
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\read\query-adaptive-sync-plan.ps1
```

Das berechnet/speichert empfohlene Sync-Intervalle je Source in `sync_source_strategy` und den aktivitätsabhängigen Feinschliff in `adaptive_sync_plan`.
- Wenn lange keine Aktivität: `currently-playing` stark runtertakten.
- Trotzdem `recently-played` periodisch lassen (Cross-Device Backfill).

## Adaptive runner (automatisch ausführen)
Einmaliger Durchlauf (führt nur fällige Sources aus):
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run-with-vault-env.ps1 -Command "powershell -ExecutionPolicy Bypass -File .\scripts\read\run-adaptive-sync-once.ps1"
```

Dauerbetrieb (Prüfung jede Minute):
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run-with-vault-env.ps1 -Command "powershell -ExecutionPolicy Bypass -File .\scripts\read\run-adaptive-sync-loop.ps1 -CheckEverySec 60"
```

Nächste fällige Syncs anzeigen:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\read\query-next-sync-due.ps1
```

## Skip-time / played-time capture
Single run:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run-with-vault-env.ps1 -Command "powershell -ExecutionPolicy Bypass -File .\scripts\read\capture-playback-once.ps1"
```

Continuous loop:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run-with-vault-env.ps1 -Command "powershell -ExecutionPolicy Bypass -File .\scripts\read\capture-playback-loop.ps1 -IntervalSec 8"
```

Stats query:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\read\query-play-stats.ps1 -Top 20
```

## Extend with more endpoints
1. Add source routing in `scripts/read/sync-read-one.ps1`
2. Add source handling in `scripts/read/store_spotify_read.py`
3. Optionally include source in `sync-read-all.ps1`
4. Update this file + `references/db-schema.md`
