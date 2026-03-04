---
name: gsuite-sdk
description: Interact with Google Workspace APIs (Gmail, Calendar, Drive, Sheets) using gsuite-sdk.
metadata:
  openclaw:
    requires:
      env:
        - GOOGLE_CREDENTIALS_FILE
    primaryEnv: GOOGLE_CREDENTIALS_FILE
    install:
      - kind: pip
        package: gsuite-sdk
        bins: [gsuite]
    homepage: https://github.com/PabloAlaniz/google-suite
---

# Google Suite Skill

Skill para interactuar con Google Workspace APIs (Gmail, Calendar, Drive, Sheets) usando `gsuite-sdk`.

## Instalación

```bash
pip install gsuite-sdk
```

Con extras opcionales:
```bash
pip install gsuite-sdk[cloudrun]  # Para Secret Manager
pip install gsuite-sdk[all]       # Todas las dependencias
```

## Autenticación

### Primera vez (requiere navegador)

El usuario debe obtener `credentials.json` de Google Cloud Console y luego autenticarse:

```bash
# Via CLI
gsuite auth login

# O via Python (abre navegador)
from gsuite_core import GoogleAuth
auth = GoogleAuth()
auth.authenticate()
```

Ver [GETTING_CREDENTIALS.md](../docs/GETTING_CREDENTIALS.md) para guía completa.

### Sesiones siguientes

Una vez autenticado, los tokens se guardan localmente y se refrescan automáticamente:

```python
from gsuite_core import GoogleAuth

auth = GoogleAuth()
if auth.is_authenticated():
    # Listo para usar
    pass
else:
    # Necesita autenticarse (abre navegador)
    auth.authenticate()
```

## Gmail

### Leer mensajes

```python
from gsuite_core import GoogleAuth
from gsuite_gmail import Gmail, query

auth = GoogleAuth()
gmail = Gmail(auth)

# Mensajes no leídos
for msg in gmail.get_unread(max_results=10):
    print(f"De: {msg.sender}")
    print(f"Asunto: {msg.subject}")
    print(f"Fecha: {msg.date}")
    print(f"Preview: {msg.body[:200]}...")
    print("---")

# Buscar con query builder
mensajes = gmail.search(
    query.from_("notifications@github.com") & 
    query.newer_than(days=7)
)

# Marcar como leído
msg.mark_as_read()
```

### Enviar email

```python
gmail.send(
    to=["destinatario@example.com"],
    subject="Asunto del email",
    body="Contenido del mensaje",
)

# Con adjuntos
gmail.send(
    to=["user@example.com"],
    subject="Reporte",
    body="Adjunto el reporte.",
    attachments=["reporte.pdf"],
)
```

## Calendar

### Leer eventos

```python
from gsuite_core import GoogleAuth
from gsuite_calendar import Calendar

auth = GoogleAuth()
calendar = Calendar(auth)

# Eventos de hoy
for event in calendar.get_today():
    print(f"{event.start.strftime('%H:%M')} - {event.summary}")

# Próximos 7 días
for event in calendar.get_upcoming(days=7):
    print(f"{event.start}: {event.summary}")
    if event.location:
        print(f"  📍 {event.location}")

# Rango específico
from datetime import datetime
events = calendar.get_events(
    time_min=datetime(2026, 2, 1),
    time_max=datetime(2026, 2, 28),
)
```

### Crear eventos

```python
from datetime import datetime

calendar.create_event(
    summary="Reunión de equipo",
    start=datetime(2026, 2, 15, 10, 0),
    end=datetime(2026, 2, 15, 11, 0),
    location="Sala de conferencias",
)

# Con asistentes
calendar.create_event(
    summary="Sync semanal",
    start=datetime(2026, 2, 15, 14, 0),
    end=datetime(2026, 2, 15, 15, 0),
    attendees=["alice@company.com", "bob@company.com"],
    send_notifications=True,
)
```

## Drive

### Listar y descargar archivos

```python
from gsuite_core import GoogleAuth
from gsuite_drive import Drive

auth = GoogleAuth()
drive = Drive(auth)

# Listar archivos recientes
for file in drive.list_files(max_results=20):
    print(f"{file.name} ({file.mime_type})")

# Buscar
files = drive.list_files(query="name contains 'reporte'")

# Descargar
file = drive.get("file_id_aqui")
file.download("/tmp/archivo.pdf")
```

### Subir archivos

```python
# Subir archivo
uploaded = drive.upload("documento.pdf")
print(f"Link: {uploaded.web_view_link}")

# Subir a carpeta específica
uploaded = drive.upload("data.xlsx", parent_id="folder_id")

# Crear carpeta
folder = drive.create_folder("Reportes 2026")
drive.upload("q1.pdf", parent_id=folder.id)
```

## Sheets

### Leer datos

```python
from gsuite_core import GoogleAuth
from gsuite_sheets import Sheets

auth = GoogleAuth()
sheets = Sheets(auth)

# Abrir spreadsheet
spreadsheet = sheets.open("SPREADSHEET_ID")

# Leer worksheet
ws = spreadsheet.worksheet("Sheet1")
data = ws.get("A1:D10")  # Lista de listas

# Como diccionarios (primera fila = headers)
records = ws.get_all_records()
# [{"Nombre": "Alice", "Edad": 30}, ...]
```

### Escribir datos

```python
# Actualizar celda
ws.update("A1", "Nuevo valor")

# Actualizar rango
ws.update("A1:C2", [
    ["Nombre", "Edad", "Ciudad"],
    ["Alice", 30, "NYC"],
])

# Agregar filas al final
ws.append([
    ["Bob", 25, "LA"],
    ["Charlie", 35, "Chicago"],
])
```

## CLI

Si instalaste `gsuite-cli`:

```bash
# Autenticación
gsuite auth login
gsuite auth status

# Gmail
gsuite gmail list --unread
gsuite gmail send --to user@example.com --subject "Hola" --body "Mundo"

# Calendar
gsuite calendar today
gsuite calendar list --days 7

# Drive
gsuite drive list
gsuite drive upload archivo.pdf

# Sheets
gsuite sheets read SPREADSHEET_ID --range "A1:C10"
```

## Notas para agentes

1. **Primera autenticación requiere navegador** - El usuario debe completar OAuth manualmente la primera vez
2. **Tokens persisten** - Después de autenticar, los tokens se guardan en `tokens.db` y se refrescan automáticamente
3. **Scopes** - Por defecto pide acceso a Gmail, Calendar, Drive y Sheets. Se puede limitar con `--scopes`
4. **Errores comunes:**
   - `CredentialsNotFoundError`: Falta `credentials.json`
   - `TokenRefreshError`: Token expiró y no se pudo refrescar (re-autenticar)
   - `NotFoundError`: Recurso no existe o sin permisos
