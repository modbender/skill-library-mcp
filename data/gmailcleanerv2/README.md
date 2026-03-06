# 📬 email-manager — OpenClaw Skills Pack v3.0

Pack de 6 skills para gestión completa de Gmail.
Cada skill tiene **dos backends**: `gog` CLI (preferido, sin dependencias) y scripts Python (fallback, más control).

---

## Skills

| Skill | Emoji | Función | Modelo |
|-------|-------|---------|--------|
| `email-reader` | 📬 | Leer inbox, buscar, hilos, IMAP | gemini-flash-lite |
| `email-organizer` | 🗂️ | Mover, archivar, etiquetar, reglas | gemini-flash |
| `email-analyzer` | 🤖 | Clasificar, phishing, prompts, tareas | claude-sonnet-4 |
| `email-responder` | ✉️ | Borradores, envíos, follow-up | claude-sonnet-4 |
| `email-scheduler` | ⏰ | Cron, heartbeat, envíos diferidos | gemini-flash-lite |
| `email-reporter` | 📊 | Informes, Sheets, audit log, undo | gemini-flash |

---

## Instalación

```bash
# 1. gog CLI (backend principal)
brew install steipete/tap/gogcli
gog auth credentials /ruta/credentials.json
gog auth add tu@gmail.com --services gmail,sheets,docs

# 2. Python (backend fallback)
pip install google-api-python-client google-auth-oauthlib \
            beautifulsoup4 cryptography python-dotenv anthropic

# 3. Skills en OpenClaw
cp -r email-manager/* ~/.openclaw/workspace/skills/
openclaw gateway restart
```

---

## Estructura de archivos

```
email-manager/
├── email-reader/
│   ├── SKILL.md              ← instrucciones del agente
│   └── scripts/
│       ├── auth.py           ← OAuth2 cifrado
│       ├── fetch_emails.py   ← leer correos (HTML, paginación, checkpoint)
│       ├── fetch_thread.py   ← hilo completo
│       ├── list_folders.py   ← etiquetas Gmail
│       └── imap_fetch.py     ← Outlook / Yahoo / IMAP genérico
├── email-organizer/
│   ├── SKILL.md
│   └── scripts/
│       ├── organizer.py      ← trash/archive/move/read/star (batch + undo)
│       ├── manage_labels.py  ← crear/renombrar/borrar etiquetas
│       └── rules_engine.py   ← motor de reglas automáticas
├── email-analyzer/
│   ├── SKILL.md
│   └── scripts/
│       ├── analyzer.py       ← análisis batch con Claude (15/llamada)
│       ├── phishing_check.py ← detección local de phishing
│       └── summarize_thread.py
├── email-responder/
│   ├── SKILL.md
│   └── scripts/
│       └── responder.py      ← draft/send/reply/template/follow-up
├── email-scheduler/
│   ├── SKILL.md
│   └── scripts/
│       └── scheduler.py      ← loop/once/auto + cron del sistema
└── email-reporter/
    ├── SKILL.md
    └── scripts/
        └── reporter.py       ← informes daily/weekly + Markdown + audit
```

---

## Variables de entorno

```bash
export GOG_ACCOUNT=tu@gmail.com
export ANTHROPIC_API_KEY=sk-ant-...   # solo para analyzer/responder
export NOTIFY_CHANNEL=telegram        # para scheduler
```

---

## Uso

```
"Revisa mi correo"
"¿Hay algo urgente?"
"Limpia el spam"
"Responde al correo de Juan"
"Activa la revisión automática cada 30 minutos"
"Dame el resumen semanal y expórtalo a mi Google Sheet"
```
