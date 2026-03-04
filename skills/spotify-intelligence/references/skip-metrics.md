# Skip & Playtime Metrics

## Ziel
Messen, wie lange ein Song durchschnittlich läuft, bevor zum nächsten gewechselt wird.

## Ansatz
Spotify liefert keinen perfekten Skip-Event-Stream. Daher:
1. `currently-playing` regelmäßig pollen (z. B. alle 8s)
2. Trackwechsel erkennen
3. Gespielte Zeit vor Wechsel schätzen (mit Gap-Cap gegen Ausreißer)
4. Event + Track-Aggregate speichern
5. Unsichere Fälle getrennt markieren (`classification=uncertain`)

## Scripts
- Einmaliger Snapshot:
  - `scripts/read/capture-playback-once.ps1`
- Polling Loop:
  - `scripts/read/capture-playback-loop.ps1 -IntervalSec 8 -Iterations 0`
- Ingest/Aggregation:
  - `scripts/read/ingest_playback_event.py`
- Statistik-Query:
  - `scripts/read/query-play-stats.ps1`

## Tabellen
- `playback_events` (ein Event pro beobachtetem Trackwechsel)
- `track_play_stats` (aggregierte Metriken je Track)
- `playback_session_state` (interner Zustand für Wechselerkennung)

## Kennzahlen
- `played_ms_before_switch`
- `completion_ratio`
- `classification` (`skip`, `completed`, `uncertain`)
- `reason` (z. B. `natural_end`, `near_end`, `stale_gap`, `paused_or_no_progress`)
- Pro Track:
  - `observed_switches`
  - `observed_skips`
  - `observed_completions`
  - `observed_uncertain`
  - `avg_played_ms_before_switch`
  - `confidence_score` (0..1, aus Samplegröße + Uncertain-Anteil)

Zusatz-Tabelle:
- `track_decision_metrics` (materialisierte Entscheidungsmetriken)

## Tuning
`ingest_playback_event.py` unterstützt:
- `--max-elapsed-ms` (Default 15000): begrenzt Zeitfortschritt pro Poll-Intervall
- `--stale-gap-ms` (Default 45000): markiert zu große Poll-Lücken als `uncertain`

## Cleanup-Kandidaten mit Zeitfenster
Read-only Kandidatenliste wird in SQLite materialisiert:
- Script: `scripts/read/query-cleanup-candidates.ps1`
- Tabelle: `playlist_cleanup_candidates`
- Metadaten inkl. Zeitraum in `system_meta`:
  - `counting_started_at`
  - `last_cleanup_window_months`
  - `last_cleanup_window_start`

Beispiel (6-Monatsfenster + Alters-/Playtime-Gates):
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\read\query-cleanup-candidates.ps1 -WindowMonths 6 -MinYearsInPlaylist 1 -MaxTotalPlayedMinutes 20 -Top 50
```

Wichtig: Vorher Playlist-Mitgliedschaften synchronisieren, damit `added_at`/Playlist-Alter vorhanden ist:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run-with-vault-env.ps1 -Command "powershell -ExecutionPolicy Bypass -File .\scripts\read\sync-playlist-items.ps1 -MaxPlaylists 50 -TracksPerPlaylist 200"
```

Outlier-Report „alt + kaum gehört“:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\read\query-playlist-age-outliers.ps1 -MinYearsInPlaylist 2 -MaxTotalPlayedMinutes 10 -Top 100
```

## Hinweis
Messgenauigkeit hängt vom Polling-Intervall ab. 5-10s ist ein guter Start.
