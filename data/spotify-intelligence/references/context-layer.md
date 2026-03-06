# Context Layer (Ratings/Tags/Mood)

Ziel: Nicht bei jedem Song fragen, sondern dezent und lernend.

## Datenmodell (SQLite)
- `track_ratings` – manuelle Bewertungen pro Track
- `track_tags` – langlebige Tags (`focus`, `nostalgia`, `gym`, ...)
- `track_context_events` – situativer Kontext (mood/intent/note)
- `context_prompt_policy` – Drosselung für Fragen
- `context_prompt_log` – wann zuletzt gefragt wurde

## Gentle Prompt Policy
Standardwerte:
- `min_minutes_between_prompts = 90`
- `max_prompts_per_day = 4`
- Modus: `gentle`

## Commands
Vorschlag, ob eine Frage sinnvoll ist:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\context\context-commands.ps1 -Action suggest-prompt
```

Kontext speichern:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\context\context-commands.ps1 -Action rate-tag -TrackId <id> -Rating 8 -Tags "focus,night" -Mood "ruhig" -Intent "deep_work" -Note "hilft beim Konzentrieren"
```

## Prinzip
- Erst automatisch lernen aus Verhalten
- Menschenfragen selten und gezielt
- Antworten dauerhaft speichern, damit Wiederholungen sinken
