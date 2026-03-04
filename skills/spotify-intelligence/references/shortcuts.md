# Agent Shortcuts

Token-sparende Kurzkommandos für Agenten.

Script:
- `scripts/playback/shortcut-commands.ps1`

## Actions
- `louder` / `quieter`
- `forward` / `back`
- `play-on` (Song + optional Artist/Device)
- `queue-top-passend`
- `queue-top-mood`
- `queue-top-explore`

## Beispiele
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\playback\shortcut-commands.ps1 -Action louder -Step 10
powershell -ExecutionPolicy Bypass -File .\scripts\playback\shortcut-commands.ps1 -Action play-on -Query "APT" -Artist "Bruno Mars" -DeviceName "Alle"
powershell -ExecutionPolicy Bypass -File .\scripts\playback\shortcut-commands.ps1 -Action queue-top-mood -Top 3 -DeviceName "Alle"
```
