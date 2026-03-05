---
name: email-scheduler
description: Schedule email automation via OpenClaw heartbeat/cron (preferred) or system cron + Python scripts (fallback). Timed sends, follow-up reminders, cost-optimized.
metadata:
  clawdbot:
    emoji: "⏰"
    requires:
      bins: ["gog"]
      env:
        - name: GOG_ACCOUNT
        - name: NOTIFY_CHANNEL
          description: "Canal notificación: telegram/slack/whatsapp/imessage/discord"
    install:
      - id: brew
        kind: brew
        formula: steipete/tap/gogcli
        bins: ["gog"]
        label: "Install gog CLI (brew)"
    routing:
      recommended: "google/gemini-2.5-flash-lite"
      alternatives: ["openrouter/google/gemini-2.5-flash-lite"]
      reason: "Config/scheduling only. Minimal reasoning, cheapest model."
---

# email-scheduler

## Cuándo usar
Usuario pide automatizar revisión de correo, programar reportes, limpiezas recurrentes, envíos diferidos, o recordatorios de follow-up.

## Backend A — OpenClaw (preferido)

### Heartbeat (`~/.openclaw/openclaw.json`)
```json
{
  "agents": {
    "defaults": {
      "heartbeat": {
        "every": "30m",
        "model": "google/gemini-2.5-flash-lite",
        "activeHours": {"start": "08:00", "end": "22:00"}
      }
    }
  }
}
```

`HEARTBEAT.md` checklist:
```
- Inbox urgentes (prioridad>=8) → notificar inmediatamente
- Spam >50 → sugerir limpieza
- Sin respuesta >3d → recordar
- Remitentes VIP (ceo@, legal@) → alerta inmediata
- Horario silencio 22:00-07:00: solo prioridad=10
```

### Cron jobs (`~/.openclaw/openclaw.json`)
```json
{
  "cron": {
    "daily-report":    {"schedule": "0 9 * * *",   "command": "email-reporter reporte diario",    "model": "google/gemini-2.5-flash"},
    "spam-cleanup":    {"schedule": "0 22 * * 0",  "command": "email-organizer limpiar spam >7d", "model": "google/gemini-2.5-flash-lite"},
    "follow-up-check": {"schedule": "0 10 * * 1,4","command": "email-reporter pendientes >5d",    "model": "google/gemini-2.5-flash"}
  }
}
```

### Envío diferido
```bash
# 1. Crear borrador
gog gmail draft create --to "dest@" --subject "Asunto" --body "Texto" --no-input

# 2. Cron one-shot para enviar en momento exacto
# En openclaw.json:
{"send-draft-feb27": {"schedule": "0 8 27 2 *", "command": "enviar borrador [ASUNTO]", "once": true}}
```

### Gestión
```bash
openclaw heartbeat pause
openclaw heartbeat resume
cat ~/.openclaw/openclaw.json | jq '.agents.defaults.heartbeat'
openclaw cron list
```

## Backend B — Python + cron sistema (fallback)

```bash
# Ejecutar agente completo (una vez)
python3 scripts/scheduler.py --once

# Con acciones automáticas ⚠️
python3 scripts/scheduler.py --once --auto

# Solo limpieza de spam
python3 scripts/scheduler.py --once --action spam-cleanup

# Loop continuo
python3 scripts/scheduler.py --interval 30 --notify-threshold 7
```

### Cron del sistema operativo
```bash
crontab -e

# Revisión cada 30 min, horario laboral
*/30 9-20 * * 1-5 cd /ruta && python3 scripts/scheduler.py --once >> logs/cron.log 2>&1

# Limpieza spam diaria 8am
0 8 * * * cd /ruta && python3 scripts/scheduler.py --once --action spam-cleanup >> logs/cron.log 2>&1

# Limpieza directa sin Python (zero tokens)
0 22 * * 0 gog gmail search 'in:spam older_than:7d' --max 500 --json \
  | jq -r '.[].id' | xargs -I{} gog gmail trash {}
```

## Optimización de costos
| Tarea | Modelo recomendado |
|-------|-------------------|
| Heartbeat / scheduling | `gemini-2.5-flash-lite` |
| Reports / summaries | `gemini-2.5-flash` |
| Spam cleanup (solo bash) | `0 tokens` — solo `gog` + `jq` |
| Análisis / respuestas | `claude-sonnet-4` |

## Errores
- Heartbeat no dispara → verificar `activeHours` y zona horaria
- `gog` missing → `brew install steipete/tap/gogcli`
- Token expired → `gog auth add <email>`
