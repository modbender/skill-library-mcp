# Decision Engine v1 (Playlist Reorg + Safe Delete)

Ziel: Nicht nur Cleanup, sondern playlistübergreifende, sinnvolle Vorschläge zum Sortieren/Umschichten.

## Prinzipien
1. **Nie direkt löschen**.
2. Erst in Vorschlags-/Zielplaylist **stagen**.
3. Erst nach Bestätigung aus Quell-Playlist entfernen.
4. Jede Aktion mit Grundmetrik loggen (undo-fähig).

## Tabellen
- `playlist_reorg_rules` – Regelkatalog (inkl. Proxy-Schwellen `min_speed_proxy`, `min_energy_proxy`, `min_focus_proxy`)
- `life_phase_flags` – Kontextflags (z. B. `relationship_happy=true`)
- `playlist_reorg_runs` – Run-Metadaten (auch wenn 0 Kandidaten)
- `playlist_reorg_candidates` – konkrete Vorschläge pro Run
- `decision_action_log` – Audit/Undo-Log
- `playlist_track_removals` – Soft-delete Archiv

## Reason-Metrik
Jeder Vorschlag/Schritt speichert eine Begründung (`rationale` / `reason_metric`), z. B.:
- zu selten gespielt
- passt nicht zur aktuellen Lebensphase
- alt in Playlist + geringe Gesamtspielzeit
- erstellt/befüllt wegen bestimmter Präferenzen (z. B. Gym)

## Workflow
### 1) Lebensphase-Flag setzen (optional)
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\decision\decision-commands.ps1 -Action set-flag -Key relationship_happy -Value true
```

### 2) Vorschläge bauen
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\decision\decision-commands.ps1 -Action suggest-reorg -Top 100
```

### 3) Vorschläge ansehen
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\decision\decision-commands.ps1 -Action show-reorg -Top 50
```

### 4) In Vorschlagsplaylist stagen (noch kein Delete)
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run-with-vault-env.ps1 -Command "powershell -ExecutionPolicy Bypass -File .\scripts\decision\decision-commands.ps1 -Action apply-reorg -Top 50 -HumanConfirmed"
```

Dry-run:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run-with-vault-env.ps1 -Command "powershell -ExecutionPolicy Bypass -File .\scripts\decision\decision-commands.ps1 -Action apply-reorg -Top 50 -DryRun"
```

### 5) Bestätigtes Löschen aus Quell-Playlist
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run-with-vault-env.ps1 -Command "powershell -ExecutionPolicy Bypass -File .\scripts\decision\decision-commands.ps1 -Action confirm-delete -Top 25 -HumanConfirmed"
```

### 6) Audit-Log prüfen
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\decision\decision-commands.ps1 -Action show-log -Top 100
```
