---
name: macro-pipeline
description: Create and manage macro-task pipelines (QA, roadmaps, feature rollouts) using PIPELINE.md + HEARTBEAT.md pattern. Use when building multi-step project plans that agents execute autonomously via cron.
metadata:
  { "openclaw": { "emoji": "🔧" } }
---

# Macro Pipeline Skill v3

## Architecture

### Two files, two locations:

| File | Location | Purpose | Mutable? |
|------|----------|---------|----------|
| `PIPELINE.md` | **Project repo** (`~/Documents/proyectos/<project>/`) | State + progress | ✅ Yes (subagents update directly) |
| `HEARTBEAT.md` | **Agent workspace** (`~/.openclaw/workspace-<agent>/`) | Instructions (read-only) | ❌ No (locked with `chflags uchg`) |

### Why PIPELINE in the repo?
- Subagents work in the repo → can update status without cross-path issues
- Git-trackable (commits show when steps completed)
- Eliminates zombie steps from path access failures

### Why HEARTBEAT in workspace?
- Operational instructions for the OpenClaw agent
- Should not contaminate project code
- Locked to prevent agents from overwriting their own instructions

---

## PIPELINE.md Format

```markdown
# PIPELINE — <Project Name>: <Pipeline Title>
# Proyecto: ~/Documents/proyectos/<project>
# Objetivo: <one-line goal>
# Creado: YYYY-MM-DD

## Step 1: <Title> [PENDING]
- engine: claude-code
- description: <what to do>
- files: <key files to touch>
- verify: <command that proves step is done>
- artifacts: <outputs for next steps>

## Step 2: <Title> [PENDING]
- engine: claude-code
- depends_on: [1]
- description: <what to do>
- verify: <verification command>
```

### Status values:
- `[PENDING]` — not started
- `[RUNNING YYYY-MM-DDTHH:MM]` — in progress (with timestamp)
- `[✅ COMPLETED]` — done
- `[FAILED]` — failed (include error reason)
- `[BLOCKED]` — waiting on human or external dependency

### Step fields:
- `engine:` — `claude-code` | `human` | `deploy`
- `depends_on:` — list of step numbers that must be ✅ first
- `parallel:` — list of steps that can run simultaneously
- `verify:` — shell command to validate completion
- `artifacts:` — outputs passed to dependent steps
- `files:` — key files modified

---

## HEARTBEAT.md Format

```markdown
# HEARTBEAT — <Agent Name>

> ⚠️ NUNCA modifiques este archivo (HEARTBEAT.md). Es read-only.

## Pipeline activo: ~/Documents/proyectos/<project>/PIPELINE.md

## Protocolo cada heartbeat:
1. Lee el pipeline activo (ruta absoluta arriba)
2. Si hay step [PENDING] sin dependencias bloqueadas → ejecútalo
3. Marca [RUNNING YYYY-MM-DDTHH:MM] con timestamp actual
4. Ejecuta: sessions_spawn(task=..., thread=true)
5. Un step por heartbeat máximo

## Zombie Detection
Si un step lleva >2h en [RUNNING], resetear a [PENDING] y reportar.

## En sesión activa con usuario
Priorizar responder. HEARTBEAT_OK.
```

---

## Cron Setup

Always use CLI, never edit openclaw.json:
```bash
openclaw cron add --name "<Project> Pipeline" --agent <agent-id> --every 30m --message "Heartbeat: lee HEARTBEAT.md y ejecuta siguiente step"
```

### Stagger schedules to avoid collisions:
- `:00/:30` → Group A
- `:15/:45` → Group B

---

## Subagent Task Template

Include in the task prompt:
```
Al terminar:
1. Actualiza <absolute-path-to-PIPELINE.md>: cambia Step X de [RUNNING] a [✅ COMPLETED] con output y artifacts
2. Si fallas, marca [FAILED] con el error
3. Notifica a Discord (action=send, channel=discord, target="channel:<id>") con resumen
```

---

## Multiple Pipelines Per Project

An agent can have multiple pipeline files. HEARTBEAT specifies priority order:
```
Lee PIPELINE_ACTIVE.md (prioritario). Si todos completados, lee PIPELINE.md como fallback.
```

---

## Parallel Execution

Steps sin dependencias cruzadas pueden ejecutarse en paralelo:
```markdown
## Step 1: Task A [PENDING]
- parallel: [2, 3]

## Step 2: Task B [PENDING]
- parallel: [1, 3]

## Step 3: Task C [PENDING]
- parallel: [1, 2]

## Step 4: Task D [PENDING]
- depends_on: [1, 2, 3]
```
El heartbeat puede lanzar múltiples steps paralelos en un mismo ciclo si no hay dependencias.

---

## Git Tagging

Cada step completado debe crear un commit taggeado:
```bash
git add . && git commit -m "pipeline/<project>/step-<N>: <step title>"
```
Esto da trazabilidad completa del progreso en git log.

---

## Key Rules
1. **PIPELINE.md siempre en el repo** — nunca en workspace
2. **HEARTBEAT.md siempre en workspace** — nunca en repo
3. **HEARTBEAT es immutable** — locked con `chflags uchg`
4. **Crons vía CLI** — `openclaw cron add`, nunca editar openclaw.json
5. **Un step por heartbeat** — evita saturación (salvo paralelos explícitos)
6. **verify: obligatorio** — cada step debe tener comando de verificación
7. **Rutas absolutas** — siempre usar `~/Documents/proyectos/...` en HEARTBEAT
8. **Git tag por step** — commit con `pipeline/<project>/step-<N>: <title>`
9. **Parallel explícito** — steps sin dependencias pueden correr en paralelo si tienen `parallel:`
