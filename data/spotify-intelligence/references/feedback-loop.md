# Feedback Loop (Like/Skip/Keep/Don't-Ask)

Ziel: Empfehlungen und Kontextfragen lernen aus direktem User-Feedback.

## Tabellen
- `track_feedback` (Einzelevents)
- `track_feedback_profile` (aggregierte Counts)
- `context_prompt_suppression` (`dont-ask-again` pro Track)

## Feedback setzen
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\context\feedback-commands.ps1 -Action set -TrackId <id> -Type like
powershell -ExecutionPolicy Bypass -File .\scripts\context\feedback-commands.ps1 -Action set -TrackId <id> -Type dislike
powershell -ExecutionPolicy Bypass -File .\scripts\context\feedback-commands.ps1 -Action set -TrackId <id> -Type skip
powershell -ExecutionPolicy Bypass -File .\scripts\context\feedback-commands.ps1 -Action set -TrackId <id> -Type keep
powershell -ExecutionPolicy Bypass -File .\scripts\context\feedback-commands.ps1 -Action set -TrackId <id> -Type dont-ask-again
```

## Wirkung
- Recommendation Scoring berücksichtigt positive/negative Feedback-Historie.
- `dont-ask-again` unterdrückt zukünftige Kontextfragen für den Track.
