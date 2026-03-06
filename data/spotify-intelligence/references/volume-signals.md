# Volume Signals (Implicit Preference)

Ziel: Lautstärkeverhalten als passives Signal für Song-Affinität nutzen.

## Tabellen
- `volume_events`
- `track_device_volume_stats`

## Capture
Ein Snapshot der aktuellen Lautstärke + Device + Track:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run-with-vault-env.ps1 -Command "powershell -ExecutionPolicy Bypass -File .\scripts\read\capture-current-volume.ps1"
```

## Nutzung
`rebuild-derived-features.py` nutzt Volumen-Samples als Zusatzsignal (`volume_affinity`) und hebt damit u. a. `energy_proxy` + `confidence` adaptiv an.

## Hinweis
Lautstärke ist ein weiches Signal (Kontextabhängig: Uhrzeit/Nachbarn/Device). Daher nur moderat gewichtet.
