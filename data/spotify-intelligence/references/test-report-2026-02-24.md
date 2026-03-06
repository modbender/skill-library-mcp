# Test Report — 2026-02-24 (updated)

## Scope
E2E smoke tests against real Spotify account + cold-start robustness checks.

## Executed (Live)
1. OAuth token exchange successful (`spotify-auth.ps1` with callback URL).
2. `get-current-track.ps1` executed (no active playback state handled).
3. Read syncs executed:
   - `sync-read-one.ps1 -Source profile`
   - `sync-read-one.ps1 -Source recently-played`
   - `sync-read-one.ps1 -Source playlists`
4. Playlist membership sync executed:
   - `sync-playlist-items.ps1 -MaxPlaylists 2 -TracksPerPlaylist 20`
5. Strategy/adaptive outputs executed:
   - `query-sync-strategy.ps1`
   - `query-adaptive-sync-plan.ps1`
   - `query-next-sync-due.ps1`
6. Cleanup/outlier/removal flows:
   - `query-cleanup-candidates.ps1`
   - `query-playlist-age-outliers.ps1`
   - `query-removal-log.ps1`
7. Restore batch dry-run:
   - `restore-pending.ps1 -DryRun`

## Bugs found during E2E and fixed
1. PowerShell reserved variable collisions:
   - `spotify-auth.ps1`: `$error` -> `$authError`
   - `sync-playlist-items.ps1`: `$pid` -> `$playlistId`
2. JSON BOM decode failure in Python readers:
   - switched to `utf-8-sig` for payload readers.
3. `sync-read-one.ps1` string interpolation parse bug (`$pagesDone:`):
   - replaced with format string.
4. Metrics logger invocation failed when error string empty:
   - switched to conditional `--error` argument.
5. Cold-start schema issues:
   - defensive table creation/migrations added across rebuild/ingest scripts.
6. Cleanup SQL ambiguity (`last_seen_at`):
   - aliased to `rc_last_seen_at`.
7. `currently-playing` empty payload handling:
   - now gracefully skips ingest when no item present.

## Current status
- Core read pipeline works live.
- Playlist membership snapshot ingest works live.
- Telemetry + adaptive interval generation works and persists in SQLite.
- Outlier query works and returns real candidates.
- Restore framework executes (no pending entries in this run).

## Remaining validation items
- Live restore end-to-end with a real removal row (`restore-from-removal.ps1`).
- Long-run adaptive loop behavior over >24h for interval convergence.
