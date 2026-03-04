---
name: email-organizer
version: "2.0.0"
description: >
  Organizes Gmail using the gog CLI: moves emails between labels/folders,
  marks as read/unread/starred, archives old messages, deletes spam,
  and applies bulk operations. Use when the user wants to organize,
  move, archive, delete, label, or clean up their Gmail inbox.
homepage: https://gogcli.sh
metadata:
  clawdbot:
    emoji: "🗂️"
    requires:
      bins: ["gog"]
      env:
        - name: GOG_ACCOUNT
          description: "Tu dirección de Gmail"
    install:
      - id: brew
        kind: brew
        formula: steipete/tap/gogcli
        bins: ["gog"]
        label: "Install gog CLI (brew)"
---

# Email Organizer

Organiza tu Gmail con el CLI `gog`. Mueve, archiva, etiqueta
y limpia correos en batch.

## Cuándo usar esta skill

- "Mueve los correos de facturacion@empresa.com a la carpeta Facturas"
- "Archiva todos los correos de más de 6 meses"
- "Marca como leídos todos los newsletters"
- "Elimina el spam"
- "Destaca los correos de mi jefe"
- "Limpia mi bandeja de entrada"
- "Borra todos los correos de promociones de más de 30 días"

## Operaciones disponibles

### Buscar correos para operar sobre ellos
Primero busca los IDs de los correos objetivo:
```bash
# Correos de un remitente específico
gog gmail search 'from:facturacion@empresa.com' --max 100 --json

# Spam antiguo
gog gmail search 'in:spam older_than:7d' --max 500 --json

# Newsletters no leídas de más de 30 días
gog gmail search 'label:newsletters older_than:30d is:unread' --max 100 --json

# Correos sin etiquetar y antiguos
gog gmail search 'in:inbox older_than:180d -is:starred' --max 200 --json
```

### Enviar correos a la papelera (trash)
```bash
# Un correo por ID
gog gmail trash <MESSAGE_ID>

# Varios a la vez — obtener IDs del search y hacer loop
gog gmail search 'in:spam older_than:7d' --max 500 --json \
  | jq -r '.[].id' \
  | xargs -I{} gog gmail trash {}
```

### Archivar correos (quitar de inbox, no borrar)
```bash
# Archivar correos antiguos del inbox
gog gmail search 'in:inbox older_than:180d -is:starred' --max 200 --json \
  | jq -r '.[].id' \
  | xargs -I{} gog gmail archive {}
```

### Marcar como leído
```bash
gog gmail mark-read <MESSAGE_ID>

# En batch
gog gmail search 'label:newsletters is:unread' --max 100 --json \
  | jq -r '.[].id' \
  | xargs -I{} gog gmail mark-read {}
```

### Marcar como no leído
```bash
gog gmail mark-unread <MESSAGE_ID>
```

### Destacar / quitar estrella
```bash
gog gmail star <MESSAGE_ID>
gog gmail unstar <MESSAGE_ID>
```

### Etiquetar correos
```bash
# Añadir etiqueta a un correo
gog gmail label add <MESSAGE_ID> "Clientes"

# Quitar etiqueta
gog gmail label remove <MESSAGE_ID> "INBOX"

# Mover = añadir etiqueta destino + quitar INBOX
gog gmail label add <MESSAGE_ID> "Proyectos"
gog gmail label remove <MESSAGE_ID> "INBOX"
```

### Enviar correo directamente (sin pasar por trash)
```bash
# Borrado permanente — ⚠️ IRREVERSIBLE
gog gmail delete <MESSAGE_ID>
```

## Flujo de limpieza de spam

Cuando el usuario pide limpiar el spam:

1. Buscar cuántos hay:
```bash
gog gmail search 'in:spam' --max 500 --json | jq 'length'
```

2. Mostrar resumen al usuario y pedir confirmación:
```
🗑️  Encontré 87 correos en spam.
    ¿Los elimino permanentemente? (sí/no)
```

3. Si confirma, borrar:
```bash
gog gmail search 'in:spam' --max 500 --json \
  | jq -r '.[].id' \
  | xargs -I{} gog gmail trash {}
```

## Flujo de organización automática por remitente

Cuando el usuario dice "organiza mis correos de facturacion@empresa.com":

1. Buscar todos sus correos:
```bash
gog gmail search 'from:facturacion@empresa.com' --max 200 --json
```

2. Proponer acción al usuario:
```
📂 Encontré 23 correos de facturacion@empresa.com
   Propuesta: mover todos a la etiqueta "Facturas"
   ¿Confirmas? (sí/no)
```

3. Si confirma, mover en batch.

## Protocolo de confirmación — OBLIGATORIO

**NUNCA ejecutar acciones destructivas sin confirmación explícita.**

Antes de cualquier borrado o movimiento masivo, mostrar siempre:
```
⚠️  Estoy a punto de:
    → [ACCIÓN] sobre [N] correos
    → Afecta correos de: [REMITENTES]
    → Esta acción [es/no es] reversible

    ¿Confirmas? (sí/no)
```

Solo continuar si el usuario responde afirmativamente.

## Registro de acciones

Guardar cada acción en `~/.openclaw/workspace/email_audit.log`:
```
2026-02-25 10:30 | TRASH  | 87 correos | SPAM
2026-02-25 10:31 | MOVE   | 23 correos | INBOX → Facturas
2026-02-25 10:32 | READ   | 45 correos | newsletters
```

Esto permite al usuario pedir "deshaz lo último" consultando el log.
