---
name: ClawHQ Dashboard Connector
description: Report agent status, heartbeats, and task completions to your ClawHQ dashboard.
---

# ClawHQ Dashboard Connector

Report agent status, heartbeats, and task completions to your ClawHQ dashboard.

## Requirements

Environment variable must be set:
- `CLAWHQ_API_KEY` — Your ClawHQ API key (generate in Settings → API Keys)

## Behavior

### On Session Start
Report status "working" with the current task:

**Windows (PowerShell):**
```powershell
$headers = @{ "Authorization" = "Bearer $env:CLAWHQ_API_KEY"; "Content-Type" = "application/json" }
$body = @{ agent = "<agent_name>"; status = "working"; task = "<current task summary>" } | ConvertTo-Json
Invoke-RestMethod -Uri "https://app.clawhq.co/api/agents/report" -Method Post -Headers $headers -Body $body
```

**Mac/Linux (curl):**
```bash
curl -s -X POST "https://app.clawhq.co/api/agents/report" \
  -H "Authorization: Bearer $CLAWHQ_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"agent":"<agent_name>","status":"working","task":"<current task summary>"}'
```

### On Session End
Report status "idle":

**Windows:**
```powershell
$headers = @{ "Authorization" = "Bearer $env:CLAWHQ_API_KEY"; "Content-Type" = "application/json" }
$body = @{ agent = "<agent_name>"; status = "idle" } | ConvertTo-Json
Invoke-RestMethod -Uri "https://app.clawhq.co/api/agents/report" -Method Post -Headers $headers -Body $body
```

**Mac/Linux:**
```bash
curl -s -X POST "https://app.clawhq.co/api/agents/report" \
  -H "Authorization: Bearer $CLAWHQ_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"agent":"<agent_name>","status":"idle"}'
```

### On Heartbeat
Post a heartbeat to keep the dashboard current. Use the same commands above with `"status":"heartbeat"`.

## Notes
- All calls should be fire-and-forget — wrap in try/catch so failures never block the agent.
- Replace `<agent_name>` with the agent's name (e.g. "Eros", "Atlas").
- The API auto-creates agents on first report — no setup needed in the dashboard.
