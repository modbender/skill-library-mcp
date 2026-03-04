# Playback Control Layer

Steuerbefehle für Spotify-Wiedergabe (Start/Stop/Device/Skip/Seek etc.).

## Script
- `scripts/playback/playback-control.ps1`

## Aktionen
- `status`
- `devices`
- `transfer` (Device wechseln)
- `play`
- `pause`
- `next`
- `previous`
- `seek` (`-PositionMs`)
- `seek-rel` (`-DeltaSec`, z. B. +15 oder -15)
- `volume` (`-VolumePercent 0..100`)
- `shuffle` (`-ShuffleState $true/$false`)
- `repeat` (`-RepeatState off|track|context`)
- `play-track` (Track-Suche + direkt abspielen)
- `queue-add` (Track-Suche + zur Queue hinzufügen)
- `queue-status` (aktuell + nächste Queue-Einträge)

## Beispiele
Status:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run-with-vault-env.ps1 -Command "powershell -ExecutionPolicy Bypass -File .\scripts\playback\playback-control.ps1 -Action status"
```

Geräte:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run-with-vault-env.ps1 -Command "powershell -ExecutionPolicy Bypass -File .\scripts\playback\playback-control.ps1 -Action devices"
```

Play/Pause/Skip:
```powershell
... -Action play
... -Action pause
... -Action next
... -Action previous
```

Vorspulen / Zurückspulen:
```powershell
... -Action seek-rel -DeltaSec 15
... -Action seek-rel -DeltaSec -15
```

Song direkt spielen:
```powershell
... -Action play-track -Query "Die ganze Nacht lang" -Artist "Daniel Aubeck"
```

Song in Queue:
```powershell
... -Action queue-add -Query "Numb" -Artist "Linkin Park"
... -Action queue-status
```
