---
name: email-organizer
description: Organize Gmail via gog CLI (preferred) or Python scripts (fallback). Label, archive, trash, star, bulk ops, auto-rules.
metadata:
  clawdbot:
    emoji: "🗂️"
    requires:
      bins: ["gog"]
      env:
        - name: GOG_ACCOUNT
    install:
      - id: brew
        kind: brew
        formula: steipete/tap/gogcli
        bins: ["gog"]
        label: "Install gog CLI (brew)"
    routing:
      recommended: "google/gemini-2.5-flash"
      alternatives: ["openrouter/google/gemini-2.5-flash", "openai/gpt-4o-mini"]
      reason: "Structured ops, moderate reasoning. Flash handles label/move logic well."
---

# email-organizer

## Cuándo usar
Usuario pide mover, archivar, etiquetar, eliminar, limpiar, destacar correos, crear carpetas, o definir reglas automáticas.

## Backend A — gog CLI (preferido)

```bash
# Buscar IDs objetivo primero
gog gmail search '<query>' --max 100 --json --no-input

# Acciones individuales
gog gmail trash <ID>          # papelera (reversible)
gog gmail archive <ID>        # archivar (quita de inbox)
gog gmail mark-read <ID>
gog gmail mark-unread <ID>
gog gmail star <ID>
gog gmail unstar <ID>
gog gmail label add    <ID> "Etiqueta"
gog gmail label remove <ID> "INBOX"
gog gmail delete <ID>         # ⚠️ IRREVERSIBLE

# Batch via pipe
gog gmail search '<query>' --max 500 --json --no-input \
  | jq -r '.[].id' | xargs -I{} gog gmail <acción> {} --no-input
```

Mover = `label add <destino>` + `label remove INBOX`

### Flujo spam
```bash
# 1. Contar
gog gmail search 'in:spam older_than:7d' --max 500 --json --no-input | jq 'length'
# 2. Confirmar → 3. Batch
gog gmail search 'in:spam older_than:7d' --max 500 --json --no-input \
  | jq -r '.[].id' | xargs -I{} gog gmail trash {} --no-input
```

### Flujo mover por remitente
```bash
gog gmail search 'from:<email>' --max 200 --json --no-input \
  | jq -r '.[].id' | xargs -I{} sh -c \
  'gog gmail label add {} "Destino" --no-input && gog gmail label remove {} INBOX --no-input'
```

## Backend B — Python (fallback)

```bash
# Acciones batch por query o IDs
python3 scripts/organizer.py --action trash   --query "in:spam older_than:7d" --max 500
python3 scripts/organizer.py --action archive --query "in:inbox older_than:180d" --max 200
python3 scripts/organizer.py --action read    --query "label:newsletters" --max 100
python3 scripts/organizer.py --action move    --move-to "Facturas" --query "from:billing@"
python3 scripts/organizer.py --action trash   --ids "ID1,ID2,ID3"
python3 scripts/organizer.py --undo           # revertir última acción

# Gestión de etiquetas
python3 scripts/manage_labels.py --action list
python3 scripts/manage_labels.py --action create --name "Proyectos 2026"
python3 scripts/manage_labels.py --action rename --id <ID> --new-name "Clientes VIP"
python3 scripts/manage_labels.py --action delete --id <ID>

# Reglas automáticas
python3 scripts/rules_engine.py --create                        # interactivo
python3 scripts/rules_engine.py --list
python3 scripts/rules_engine.py --apply --emails-file emails.json
```

Formato regla en `rules.json`:
```json
{"id":"rule_001","nombre":"Facturas","condiciones":{"asunto_contiene":["factura","recibo"]},"accion":{"mover_a":"Finanzas","marcar_como":"leído"},"activa":true}
```

## ⚠️ Confirmación OBLIGATORIA
Antes de toda acción destructiva o masiva:
```
⚠️ [ACCIÓN] sobre [N] correos de [REMITENTES]
   [Reversible / IRREVERSIBLE] — ¿Confirmas? (sí/no)
```
NUNCA ejecutar sin confirmación explícita.

## Audit log
`~/.openclaw/workspace/email_audit.log`:
`YYYY-MM-DD HH:MM | ACCIÓN | N correos | DETALLE`

## Errores
- `gog` missing → `brew install steipete/tap/gogcli`
- `GOG_ACCOUNT` unset → pedir Gmail
- Token expired → `gog auth add <email>`
