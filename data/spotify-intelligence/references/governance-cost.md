# Governance & Cost Guardrails

Ziel: Unnötige Aktionen vermeiden, Kosten kontrollieren, Entscheidungen bewusst halten.

## Komponenten
- `governance_policy` (DB): Trigger-/Prompt-Policy
- `action_budget` (DB): Wochenbudget je Aktionstyp
- `trigger_events` (DB): Nachvollziehbarer Trigger-/Entscheidungslog
- `preflight-action-check.py`: Blockt Aktionen bei fehlender Human-Bestätigung/QuietHours/Budget

## Default-Policy
- `cleanup_prompt_cooldown_hours = 72`
- `cleanup_prompt_max_per_week = 2`
- `cleanup_prompt_quiet_hours = 23-08`
- `auto_cleanup_enabled = false`
- `cost_mode = lean`

## Befehle
Init:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\governance\governance-commands.ps1 -Action init
```

Status:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\governance\governance-commands.ps1 -Action show
```

Policy ändern:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\governance\governance-commands.ps1 -Action set-policy -Key cleanup_prompt_cooldown_hours -Value 96
```

Review:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\governance\governance-commands.ps1 -Action review
```

Cleanup-Trigger-Check ("Soll ich aufräumen?"):
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\governance\check-cleanup-trigger.ps1
```

Logik: nur triggern bei Kandidaten + außerhalb Quiet Hours + nach Cooldown + innerhalb Wochenbudget.
