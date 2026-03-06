---
name: email-responder
description: Draft/send Gmail replies via gog CLI (preferred) or Python scripts (fallback). Tone matching, templates, follow-up, confirmations.
metadata:
  clawdbot:
    emoji: "✉️"
    requires:
      bins: ["gog"]
      env:
        - name: GOG_ACCOUNT
        - name: ANTHROPIC_API_KEY
          description: "Para generar borradores con IA"
    install:
      - id: brew
        kind: brew
        formula: steipete/tap/gogcli
        bins: ["gog"]
        label: "Install gog CLI (brew)"
    routing:
      recommended: "anthropic/claude-sonnet-4"
      alternatives: ["openrouter/anthropic/claude-sonnet-4", "openai/gpt-4o"]
      reason: "Nuanced writing: tone matching, multilingual, context-aware replies."
---

# email-responder

## Cuándo usar
Usuario pide responder, redactar, enviar, reenviar correos, generar borradores, o hacer follow-up.

## Backend A — gog CLI (preferido)

```bash
# Enviar nuevo correo
gog gmail send --to "dest@mail.com" --subject "Asunto" --body "Texto" --no-input

# Responder en hilo
gog gmail reply <ID> --body "Texto" --no-input

# Responder a todos
gog gmail reply <ID> --all --body "Texto" --no-input

# Reenviar
gog gmail forward <ID> --to "dest@mail.com" --body "Nota" --no-input

# Crear borrador (sin enviar)
gog gmail draft create --to "dest@mail.com" --subject "Asunto" --body "Texto" --no-input

# Follow-up: correos enviados sin respuesta
gog gmail search 'in:sent older_than:5d newer_than:30d' --max 100 --json --no-input
```

## Backend B — Python (fallback)

```bash
# Generar borrador con IA (usa hilo como contexto)
python3 scripts/responder.py --action draft --email-id <ID> --thread-file thread.json

# Crear borrador en Gmail
python3 scripts/responder.py --action create-draft \
  --to "dest@mail.com" --subject "Asunto" --body-file draft.txt --reply-to <ID>

# Enviar borrador existente
python3 scripts/responder.py --action send-draft --draft-id <DRAFT_ID>

# Verificar correos sin respuesta
python3 scripts/responder.py --action followup-check --days 5

# Usar plantilla
python3 scripts/responder.py --action use-template \
  --template acuse_recibo --to "dest@mail.com" --subject "Asunto"

# Guardar prompts detectados
python3 scripts/responder.py --action save-prompts --emails-file analysis.json
```

Plantillas disponibles: `acuse_recibo` · `confirmacion_reunion` · `fuera_oficina` · `solicitar_info` · `cotizacion_recibida`

## Flujo
1. Obtener correo original vía **email-reader** si falta contexto
2. Analizar: idioma, tono, formalidad, puntos clave del hilo
3. Generar borrador → coincidir idioma y tono del hilo original
4. Mostrar preview completo al usuario
5. Solo enviar con confirmación explícita

## ⚠️ Confirmación OBLIGATORIA
NUNCA enviar sin confirmación. Mostrar siempre:
```
✉️ Para: [DEST] | Asunto: [ASUNTO]
[PREVIEW del contenido]
¿Envío? (sí / editar / cancelar)
```

## Reglas
- NUNCA enviar sin confirmación explícita
- Coincidir idioma y formalidad del hilo original
- No inventar datos, fechas ni compromisos no mencionados
- Registrar envíos en `~/.openclaw/workspace/email_audit.log`
- Sin contexto → usar **email-reader** primero

## Errores
- Envío falla → mostrar error, verificar dirección
- `GOG_ACCOUNT` unset → pedir Gmail al usuario
- Token expired → `gog auth add <email>` / `python3 scripts/auth.py`
