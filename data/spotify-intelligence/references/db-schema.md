# DB Schema (v2 normalized read model)

Database: `data/spotify-intelligence.sqlite`

## Ziel
Objektbasiert speichern (Track/Album/Artist/Playlist/User je einmal) und bei erneuten Reads nur Zähler erhöhen.

## Tables

### `endpoint_stats`
Pull-Statistik je Quelle (`pull_count`, unique/duplicate payload fingerprints, last status).

### `payload_fingerprints`
Nur Fingerprints je Source (`source + payload_hash`) inkl. `seen_count`.
Kein großes Raw-JSON-Archiv nötig.

### `users`
Spotify-Profilobjekte (`user_id` PK).

### `artists`
Artist-Objekte (`artist_id` PK).

### `albums`
Album-Objekte (`album_id` PK).

### `tracks`
Track-Objekte (`track_id` PK) mit Metadaten + `album_id`.

### `track_artists`
N:M-Zuordnung Track ↔ Artist inkl. Reihenfolge.

### `playlists`
Playlist-Objekte (`playlist_id` PK) inkl. owner/snapshot/tracks_total.

### `read_counters`
Zähler je Quelle und Entität:
- PK: `(source, entity_type, entity_id)`
- `seen_total`, `first_seen_at`, `last_seen_at`

Beispiele:
- `source=recently-played`, `entity_type=track`, `entity_id=<track_id>`
- `source=playlists`, `entity_type=playlist`, `entity_id=<playlist_id>`

### `playback_events`
Ein Event pro erkanntem Trackwechsel inkl. Klassifikation (`skip/completed/uncertain`).

### `track_play_stats`
Aggregierte Skip-/Completion-Metriken pro Track.

### `track_decision_metrics`
Materialisierte Entscheidungsmetriken (inkl. `confidence_score`) für spätere Agent-Entscheidungen.

### `playlist_track_membership`
Speichert pro Playlist+Track die Mitgliedschaft inklusive Zeitbezug:
- `added_at`
- `first_added_at`
- `last_added_at`
- `first_seen_at` / `last_seen_at`
- `times_seen`, `currently_present`

Damit sind Aussagen möglich wie: „seit 4 Jahren in Playlist, aber nur 10 Minuten Gesamtspielzeit".

### `playlist_track_removals`
Archiviert entfernte Playlist-Einträge statt hart zu löschen:
- `removed_at`
- `playlist_id`
- `track_id`
- `source`, `removal_reason`
- vorherige Membership-Felder (`previous_*`)
- `restore_status` (`available`, `restore_pending`, `restored`, `ignored`)
- `restored_at`

Wiederherstellung:
- `scripts/read/restore-from-removal.ps1` (einzeln)
- `scripts/read/restore-pending.ps1` (Batch)

Damit sind Löschvorgänge nachvollziehbar und später reversibel.

### `playlist_cleanup_candidates`
Read-only Kandidatenlisten pro Lauf (`run_id`) inkl. genutztem Zeitfenster/Schwellwerten und Score.
Zusätzlich gespeichert: `years_in_playlist`, `total_played_minutes`, `oldest_playlist_added_at`, `playlist_count`.

### `system_meta`
Systemweite Metadaten und Zeitbezug, z. B.:
- `counting_started_at`
- `last_cleanup_run_id`
- `last_cleanup_window_months`
- `last_cleanup_window_start`

### `api_request_metrics`
Seiten-/Request-Metriken für Effizienz-Tuning:
- `source`, `endpoint`, `page`, `limit_value`, `offset_value`
- `request_ms`, `payload_bytes`, `items_count`
- `status`, `http_code`, `error_message`

### `sync_source_strategy`
Aggregierte Strategie je Source inkl. vorgeschlagenem Intervall:
- `p90_request_ms`, `error_rate`, `avg_payload_bytes`, `avg_items_count`
- `recommended_interval_sec`

### `adaptive_sync_plan`
Aktivitätsabhängige Intervall-Empfehlungen (z. B. bei 2 Tagen ohne Musik):
- `activity_ref_at`, `activity_age_minutes`
- `strategy_interval_sec` (Basis aus Metriken)
- `adaptive_interval_sec` (dynamisch angepasst)
- `reason`

Wird vom Runner genutzt:
- `scripts/read/run-adaptive-sync-once.ps1`
- `scripts/read/run-adaptive-sync-loop.ps1`

### `spotify_track_features`
Spotify-Feature-Flags pro Track (zum Koppeln mit eigenen Kontextdaten):
- `energy`, `tempo`, `valence`, `danceability`
- weitere Audio-Feature-Felder
- `fetched_at`, `source`

## Design notes
- Upserts halten Objekte aktuell (latest metadata).
- Wiederholte Abfragen blähen nicht auf, sondern erhöhen `seen_total`.
- Dadurch disk-schonend und analytics-freundlich.
- Metriken liegen in SQLite, nicht in verstreuten JSON-Dateien.
