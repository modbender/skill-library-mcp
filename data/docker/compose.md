# Compose Traps

## depends_on

- `depends_on: [db]` espera que CONTAINER arranque — no que servicio esté ready
- `condition: service_healthy` requiere healthcheck definido — sin él, falla silenciosamente
- Circular dependency no es error — compose intenta resolver y puede fallar random
- depends_on no afecta `docker compose run` — servicios dependency no arrancan

## Environment

- `.env` debe estar junto a `docker-compose.yml` — en subdirectorio no se lee
- `${VAR}` undefined = string vacío, no error — bugs silenciosos
- `${VAR:-default}` solo aplica si VAR undefined — VAR="" usa vacío, no default
- `env_file` no acepta export syntax — `export VAR=x` falla

## Volumes

- Volume mount sobre directorio con archivos = archivos del container desaparecen
- Bind mount de directorio host vacío = directorio container vacío
- `./path` relativo al compose file, no al cwd
- Named volume primera vez copia contenido del container — después no

## Networks

- Default bridge no tiene DNS entre containers — nombres no resuelven
- Container name ≠ service name — usar service name para DNS
- `network_mode: host` desactiva toda la red de compose — no solo para ese container
- External network no se crea automáticamente — debe existir

## Build

- `build: .` usa Dockerfile, `build: { dockerfile: X }` para otro nombre
- Build context se envía completo al daemon — directorio grande = build lento
- `image:` + `build:` juntos = build y tag con ese nombre
- Cache de build no se comparte entre diferentes compose projects por defecto

## Healthcheck

- Healthcheck en compose override el del Dockerfile
- `start_period` no cuenta para retries — primeros N segundos ignora fallos
- `test: ["CMD", "curl", ...]` — CMD usa exec, CMD-SHELL usa shell
- Exit code 0 = healthy, 1 = unhealthy, 2 = reserved (don't use)
