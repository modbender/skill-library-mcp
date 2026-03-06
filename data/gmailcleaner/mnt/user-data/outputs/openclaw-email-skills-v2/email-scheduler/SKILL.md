---
name: email-scheduler
version: "2.0.0"
description: >
  Automates periodic Gmail management using OpenClaw cron jobs and heartbeat
  with gog CLI. Sets up scheduled email checks, spam cleanup, priority alerts,
  and weekly reports. Use when the user wants to automate email checking,
  set up recurring tasks, or run the email agent periodically in the background.
homepage: https://gogcli.sh
metadata:
  clawdbot:
    emoji: "⏰"
    requires:
      bins: ["gog"]
      env:
        - name: GOG_ACCOUNT
          description: "Tu dirección de Gmail"
        - name: NOTIFY_CHANNEL
          description: "Canal de notificación (telegram/slack/whatsapp/imessage)"
    install:
      - id: brew
        kind: brew
        formula: steipete/tap/gogcli
        bins: ["gog"]
        label: "Install gog CLI (brew)"
---

# Email Scheduler

Automatiza la gestión del correo usando el sistema de cron
y heartbeat de OpenClaw con `gog` como backend.

## Cuándo usar esta skill

- "Revisa mi correo cada hora y avísame si hay algo importante"
- "Limpia el spam automáticamente todos los días a las 8am"
- "Mándame un resumen de correos cada mañana"
- "Activa el agente de correo en modo automático"
- "¿Qué automatizaciones de correo tengo activas?"
- "Desactiva la revisión automática"

## Configuración de Cron Jobs

Añadir a `~/.openclaw/openclaw.json`:

```json
{
  "cron": {
    "jobs": [
      {
        "id": "email-morning-check",
        "schedule": "0 8 * * *",
        "description": "Revisión matutina de correos importantes",
        "message": "Busca correos no leídos del inbox de las últimas 12 horas con gog. Analiza su prioridad. Si hay alguno con prioridad 8 o más, notifícame con el remitente y asunto.",
        "enabled": true
      },
      {
        "id": "email-spam-cleanup",
        "schedule": "0 9 * * *",
        "description": "Limpieza diaria de spam a las 9am",
        "message": "Busca correos en spam con más de 7 días usando gog. Muéstrame cuántos hay y pídeme confirmación antes de eliminarlos.",
        "enabled": true
      },
      {
        "id": "email-priority-alert",
        "schedule": "*/30 9-20 * * 1-5",
        "description": "Alerta de correos críticos cada 30min (horario laboral)",
        "message": "Busca correos no leídos en inbox de los últimos 30 minutos con gog. Si alguno tiene asunto urgente o es de remitentes conocidos como mi jefe, notifícame inmediatamente.",
        "enabled": true
      },
      {
        "id": "email-weekly-report",
        "schedule": "0 9 * * MON",
        "description": "Informe semanal los lunes",
        "message": "Genera un resumen de los correos de la última semana: cuántos recibí, cuánto spam, remitentes más frecuentes, correos que aún no he respondido. Usa gog para obtener los datos.",
        "enabled": true
      },
      {
        "id": "email-followup-check",
        "schedule": "0 10 * * 2,4",
        "description": "Revisión de seguimientos martes y jueves",
        "message": "Busca correos que envié hace más de 5 días y no han recibido respuesta usando gog. Muéstrame la lista y pregúntame si quiero enviar seguimientos.",
        "enabled": false
      }
    ]
  }
}
```

### Activar/desactivar jobs
```bash
openclaw cron enable email-morning-check
openclaw cron disable email-spam-cleanup
openclaw cron list
openclaw cron run email-weekly-report   # ejecutar manualmente
```

## Configuración de Heartbeat

Añadir en `HEARTBEAT.md` del workspace de OpenClaw:

```markdown
## Email Monitor

Cada 15 minutos, si hay correos nuevos en inbox:
1. Ejecuta: gog gmail search 'in:inbox is:unread newer_than:15m' --max 10 --json --no-input
2. Si hay resultados, analiza brevemente cada uno
3. Si alguno parece urgente (de remitentes conocidos, asunto con palabras
   como "urgente", "importante", "hoy", "ahora", "deadline"), notifícame
   inmediatamente con el resumen
4. No notificar si son solo newsletters o correos de sistema
5. En horario de silencio (22:00-07:00), solo notificar si prioridad = 10
```

## Notificaciones por canal

El agente envía alertas al canal configurado en `NOTIFY_CHANNEL`.
Canales disponibles en OpenClaw: Telegram, Slack, WhatsApp, iMessage, Discord.

**Formato de alerta de correo urgente:**
```
📧 CORREO URGENTE [Prioridad 9/10]
────────────────────────────────
De: ceo@empresa.com
Asunto: "Reunión urgente — responder antes de las 15h"
Recibido: hace 3 minutos

¿Quieres que redacte una respuesta?
```

**Formato de resumen matutino:**
```
☀️ Buenos días — Resumen de correos
────────────────────────────────
📥 Inbox: 12 nuevos (3 no leídos)
⭐ Importantes: 2 correos
🗑️ Spam eliminado: 34 correos
📋 Sin respuesta: 1 correo (de hace 6 días)

Correos que requieren tu atención:
• ceo@empresa.com — "Decisión contrato"
• cliente@empresa.com — "Aprobación presupuesto"
```

## Configuración de horario de silencio

```json
{
  "email_scheduler": {
    "quiet_hours": {
      "enabled": true,
      "start": "22:00",
      "end": "07:00",
      "timezone": "America/Bogota"
    },
    "notify_priority_threshold": 7,
    "weekend_alerts": false
  }
}
```

## Activación rápida completa

Cuando el usuario dice "activa el agente de correo automático":

1. Verificar que `gog auth list` muestra la cuenta activa
2. Preguntar:
   - ¿A qué hora quieres el resumen matutino?
   - ¿Cada cuántos minutos revisar correos urgentes?
   - ¿Por dónde notificarte? (Telegram/Slack/WhatsApp)
3. Generar la configuración de cron personalizada
4. Confirmar: "✅ Agente de correo activado. Te avisaré por [CANAL] cuando llegue algo importante."
