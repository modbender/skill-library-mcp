# Recommendation Layer v1

Modi:
- `passend`
- `mood-shift`
- `explore`

## Scripts
- `scripts/recommend/recommend-now.py`
- `scripts/recommend/recommend-commands.ps1`

## Ablauf
1. Run erzeugen
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\recommend\recommend-commands.ps1 -Action run -Mode passend -Top 10
```

2. Anzeigen
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\recommend\recommend-commands.ps1 -Action show -Top 10
```

3. Top-N in Queue
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run-with-vault-env.ps1 -Command "powershell -ExecutionPolicy Bypass -File .\scripts\recommend\recommend-commands.ps1 -Action queue -Top 5 -DeviceName 'Alle'"
```

## Quality Guards
- Hard negative filter: stark negativ bewertete Tracks ohne positives Gegensignal werden ausgeschlossen.
- Diversity pass: Top-Liste begrenzt Dominanz desselben Lead-Artists.

## Explainability
Jeder Track enthält `score` + `reason` (warum vorgeschlagen).
