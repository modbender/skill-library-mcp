# Security Traps

## User

- Container corre como root por defecto — security scanners lo flaggean
- `USER` directive después de `RUN` que necesita root = build falla
- User en container con UID 1000 = puede ser otro user en host — confuso
- `--user` en runtime override USER de Dockerfile — pero permisos de archivos quedan

## Secrets

- `ENV SECRET=x` visible en `docker history` y `docker inspect`
- `ARG` para secrets también visible en history — no es seguro
- `COPY secrets.txt` baked en layer — aunque lo borres después, está en layer anterior
- `--env-file` seguro en runtime pero archivo debe protegerse en host

## BuildKit Secrets

- `RUN --mount=type=secret` no disponible sin DOCKER_BUILDKIT=1
- Secret mount solo disponible en ese RUN — no persiste
- Secret ID debe coincidir exacto — typo = build falla sin mensaje claro
- Secret no disponible en stages que no lo montan explícitamente

## Image Scanning

- Vulnerabilities en base image heredadas — actualizar base regularmente
- Scan en CI pero no en registry = images vulnerables en producción
- CVE "fixed" en package pero base image no actualizada = sigue vulnerable
- Distroless images difíciles de scanear — menos CVEs reportadas, no menos bugs

## Runtime

- `--privileged` = acceso completo a host devices, kernel modules, etc.
- `--cap-add SYS_ADMIN` casi tan malo como privileged — evitar
- `-v /:/host` monta root del host = game over si container comprometido
- `--pid=host` permite ver/kill procesos del host desde container

## Network

- Container en bridge network puede acceder a metadata service (169.254.x.x)
- Sin `--network=none`, container tiene acceso a red por defecto
- Published ports sin firewall = público a internet
- Container puede hacer requests a otros containers en misma network — no isolation

## Supply Chain

- Base image de registry público puede ser maliciosa — verificar publisher
- `latest` tag puede ser hijacked — usar digest para images críticas
- Dependencias descargadas en build pueden cambiar — lock files + verified mirrors
