# Image Building Traps

## Layer Cache

- `COPY . .` antes de `RUN npm install` = cache invalidado en cada cambio de código
- `apt-get update` y `apt-get install` en RUNs separados = packages stale semanas después
- `--no-cache` en build borra TODO el cache — no solo del paso actual
- Cache de un stage no se usa en otro stage — multi-stage rebuild from scratch

## Multi-Stage

- `--from=builder` con typo = copia de stage equivocado silenciosamente
- `COPY --from=0` es primer stage, no stage llamado "0"
- Stage sin nombre + reorden de stages = `--from=N` apunta a stage diferente
- Files copiados de stage anterior pierden permisos — copiar con `--chmod`

## Base Images

- `python:latest` hoy ≠ `python:latest` mañana — builds no reproducibles
- `alpine` sin glibc = muchos binarios no funcionan — errores crípticos
- `slim` images sin shell tools = debugging imposible
- Imagen "latest" puede ser major version diferente — breaking changes

## COPY vs ADD

- `ADD` con URL descarga pero no cachea — rebuild = re-download
- `ADD` con .tar.gz extrae automáticamente — sorpresa si no lo esperabas
- `COPY` no expande wildcards como shell — `COPY *.json ./` puede no hacer lo que esperas
- `.dockerignore` ignorado en builds remotos (docker build - < Dockerfile)

## ARG vs ENV

- `ARG` no disponible después de `FROM` — cada stage necesita re-declarar
- `ARG` con valor default + override vacío = usa el default, no vacío
- `ARG` visible en `docker history` — no para secrets
- `ENV` persiste en runtime — `ARG` solo en build

## Size Traps

- `rm -rf /var/lib/apt/lists` en RUN separado = espacio no recuperado (layers)
- `npm install --production` después de `npm install` = dev dependencies todavía en layer anterior
- `.git` copiado = megas extra si no hay .dockerignore
- Múltiples `RUN apt-get` = cada uno es layer con cache de apt
