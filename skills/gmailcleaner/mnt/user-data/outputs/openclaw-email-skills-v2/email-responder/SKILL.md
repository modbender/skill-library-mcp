---
name: email-responder
version: "2.0.0"
description: >
  Drafts and sends Gmail replies using gog CLI + AI. Generates smart replies
  with full thread context, sends emails, manages reply templates, and tracks
  unanswered messages. Use when the user wants to reply to, respond to,
  draft, write, send, or follow up on an email.
homepage: https://gogcli.sh
metadata:
  clawdbot:
    emoji: "✍️"
    requires:
      bins: ["gog"]
      env:
        - name: GOG_ACCOUNT
          description: "Tu dirección de Gmail"
        - name: ANTHROPIC_API_KEY
          description: "API Key de Anthropic para generar respuestas"
    install:
      - id: brew
        kind: brew
        formula: steipete/tap/gogcli
        bins: ["gog"]
        label: "Install gog CLI (brew)"
---

# Email Responder

Redacta y envía respuestas de correo usando `gog` + IA.

## Cuándo usar esta skill

- "Responde al correo de Juan sobre la propuesta"
- "Genera una respuesta para los correos importantes"
- "Envía el borrador que generaste"
- "Escribe un correo a maria@empresa.com sobre la reunión del viernes"
- "¿Qué correos enviados no han recibido respuesta?"
- "Genera un follow-up para el correo del cliente de hace 5 días"
- "Responde a todos agradeciendo el mensaje"

## Flujo de respuesta

### PASO 1 — Identificar el correo a responder
Buscar el correo por remitente, asunto o fecha:
```bash
gog gmail search 'from:juan@empresa.com subject:propuesta' --max 5 --json --no-input
```

### PASO 2 — Obtener el hilo completo para contexto
```bash
# Buscar todos los mensajes del mismo hilo
gog gmail search 'subject:"Re: Propuesta Q1 2026"' --max 20 --json --no-input
```
La respuesta debe ser coherente con TODO el hilo, no solo el último mensaje.

### PASO 3 — Generar borrador con IA
Usar el historial del hilo como contexto:

```
Eres un asistente de email profesional.
Redacta una respuesta para el correo indicado.
- Tono: profesional y cercano
- Longitud: máximo 150 palabras salvo que sea necesario más
- No incluyas asunto ni encabezados, solo el cuerpo
- Firma con el nombre del usuario

Historial del hilo (del más antiguo al más reciente):
[HILO_COMPLETO]

Correo al que debes responder (el último):
De: juan@empresa.com
Asunto: Propuesta Q1 2026
Mensaje: [CUERPO]

Genera la respuesta:
```

### PASO 4 — Mostrar borrador y confirmar
```
✍️  Borrador generado:
────────────────────────────────────────
Para: juan@empresa.com
Asunto: Re: Propuesta Q1 2026

Hola Juan,

Gracias por compartir la propuesta. He revisado los puntos
principales y me parece una dirección muy interesante.

¿Podríamos agendar una llamada esta semana para discutir
el presupuesto en detalle?

Quedo atento.
[Nombre]
────────────────────────────────────────

¿Qué hago?
  [1] Enviar ahora
  [2] Editar primero
  [3] Guardar como borrador en Gmail
  [4] Descartar
```

### PASO 5a — Enviar correo
⚠️ **SIEMPRE pedir confirmación antes de enviar. Sin excepciones.**

```bash
gog gmail send \
  --to "juan@empresa.com" \
  --subject "Re: Propuesta Q1 2026" \
  --body "Hola Juan,\n\nGracias por compartir..." \
  --no-input
```

Para responder en un hilo (con In-Reply-To):
```bash
gog gmail send \
  --to "juan@empresa.com" \
  --subject "Re: Propuesta Q1 2026" \
  --body "..." \
  --reply-to <MESSAGE_ID> \
  --no-input
```

### PASO 5b — Enviar nuevo correo (no respuesta)
```bash
gog gmail send \
  --to "maria@empresa.com" \
  --subject "Reunión del viernes" \
  --body "Hola María,\n\nTe escribo para confirmar..." \
  --no-input
```

Con CC o BCC:
```bash
gog gmail send \
  --to "maria@empresa.com" \
  --cc "equipo@empresa.com" \
  --subject "Reunión del viernes" \
  --body "..." \
  --no-input
```

## Detección de correos sin respuesta (follow-up)

Buscar correos enviados que no recibieron respuesta en X días:
```bash
# Correos enviados hace más de 5 días
gog gmail search 'in:sent older_than:5d newer_than:30d' --max 50 --json --no-input
```

Cruzar con respuestas recibidas para detectar los sin contestar,
y ofrecer generar mensajes de seguimiento.

```
📬 Correos sin respuesta (más de 5 días):

1. Para: cliente@empresa.com
   Asunto: "Cotización proyecto web"
   Enviado: hace 7 días
   ¿Genero un follow-up?

2. Para: proveedor@tech.com
   Asunto: "Solicitud de demo"
   Enviado: hace 12 días
   ¿Genero un follow-up?
```

## Plantillas de respuesta rápida

Plantillas predefinidas para casos comunes:

**Acuse de recibo:**
```
Hola [NOMBRE], gracias por tu mensaje. Lo revisaré y te responderé
a la brevedad. Saludos, [FIRMA]
```

**Confirmación de reunión:**
```
Hola [NOMBRE], confirmo mi asistencia a la reunión del [FECHA]
a las [HORA]. Hasta entonces. Saludos, [FIRMA]
```

**Solicitar más información:**
```
Hola [NOMBRE], gracias por contactarme. Para poder ayudarte mejor,
¿podrías compartirme más detalles sobre [TEMA]? Quedo atento. [FIRMA]
```

**Fuera de oficina:**
```
Gracias por tu mensaje. Estoy fuera de la oficina hasta el [FECHA].
Responderé a mi regreso. Para urgencias: [CONTACTO]. [FIRMA]
```

El usuario puede decir: "Usa la plantilla de acuse de recibo para
los 3 correos importantes" y el agente personaliza y envía cada uno.

## Regla de oro
`send_requires_confirmation: true` — **siempre.**
Nunca enviar un correo sin que el usuario lo haya visto y aprobado.
