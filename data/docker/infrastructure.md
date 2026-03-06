# Infrastructure Traps

## Networking

- `localhost` en container es el container, no el host — usar `host.docker.internal`
- `0.0.0.0` bind necesario para que container sea accesible — `127.0.0.1` solo local al container
- `-p 5432:5432` sin IP = bind a todas interfaces = público si no hay firewall
- Container restart cambia IP — usar network aliases, no IPs hardcoded

## DNS

- DNS default es 127.0.0.11 interno — no usa /etc/resolv.conf del host
- `--dns` override completo — no se añade, reemplaza
- DNS caching en daemon — cambios DNS externos tardan en propagarse
- Container sin network no tiene DNS — ni siquiera localhost resuelve

## Volumes

- Volume anónimo (`VOLUME` en Dockerfile) acumula sin límite — nunca se borran automáticamente
- `docker system prune` NO borra volumes — necesita `--volumes` explícito
- Bind mount permissions: container user vs host user — mismatch = permission denied
- NFS volumes con latencia = performance horrible — especialmente para node_modules

## Storage Driver

- `overlay2` default pero overlayfs en kernel viejo = bugs sutiles
- Storage driver diferente entre dev/prod = comportamiento diferente
- Logs sin limit crecen infinito — `--log-opt max-size=10m`
- `/var/lib/docker` lleno = daemon se cuelga — monitoring esencial

## Resources

- Sin `--memory` limit = container puede usar toda la RAM y triggerar OOM killer
- `--memory` sin `--memory-swap` = swap = 2x memory — puede ser mucho
- `--cpus=0.5` es limit, no reservation — otros containers pueden usar
- Java en container sin `-XX:+UseContainerSupport` no ve el límite correcto

## Security

- `--privileged` desactiva TODA la seguridad — casi nunca necesario
- `--cap-add` granular mejor que privileged — solo lo que necesitas
- Root en container puede ser root en host — user namespaces para evitar
- Secrets en env vars visibles con `docker inspect` — usar secrets/mounts
