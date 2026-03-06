# Docker and Docker Compose Patterns

## Basic Web App with Database

```yaml
# docker-compose.yml
services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=postgres://user:pass@db:5432/myapp
    depends_on:
      - db
    restart: unless-stopped
  
  db:
    image: postgres:16-alpine
    volumes:
      - pgdata:/var/lib/postgresql/data
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=myapp
    restart: unless-stopped

volumes:
  pgdata:
```

## With Reverse Proxy (Traefik)

```yaml
services:
  traefik:
    image: traefik:v3.0
    command:
      - "--api.insecure=true"
      - "--providers.docker=true"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.letsencrypt.acme.httpchallenge=true"
      - "--certificatesresolvers.letsencrypt.acme.email=you@example.com"
      - "--certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - letsencrypt:/letsencrypt
    restart: unless-stopped

  app:
    build: .
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.app.rule=Host(`app.example.com`)"
      - "traefik.http.routers.app.entrypoints=websecure"
      - "traefik.http.routers.app.tls.certresolver=letsencrypt"
    restart: unless-stopped

volumes:
  letsencrypt:
```

## Self-Hosted Services

### Nextcloud

```yaml
services:
  nextcloud:
    image: nextcloud:latest
    ports:
      - "8080:80"
    volumes:
      - nextcloud:/var/www/html
    environment:
      - POSTGRES_HOST=db
      - POSTGRES_DB=nextcloud
      - POSTGRES_USER=nextcloud
      - POSTGRES_PASSWORD=changeme
    depends_on:
      - db
    restart: unless-stopped

  db:
    image: postgres:16-alpine
    volumes:
      - db:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=nextcloud
      - POSTGRES_USER=nextcloud
      - POSTGRES_PASSWORD=changeme
    restart: unless-stopped

volumes:
  nextcloud:
  db:
```

### Plex Media Server

```yaml
services:
  plex:
    image: plexinc/pms-docker
    network_mode: host
    environment:
      - PLEX_UID=1000
      - PLEX_GID=1000
      - TZ=Europe/Madrid
    volumes:
      - ./config:/config
      - /path/to/media:/media
    restart: unless-stopped
```

## Common Commands

```bash
# Start services
docker compose up -d

# View logs
docker compose logs -f app

# Rebuild after code changes
docker compose up -d --build

# Enter container shell
docker compose exec app sh

# Stop everything
docker compose down

# Stop and remove volumes (destructive!)
docker compose down -v
```

## Networking Notes

- Services in same compose file reach each other by service name (e.g., `db:5432`)
- To reach host from container: `host.docker.internal` (macOS/Windows) or `172.17.0.1` (Linux)
- Use `network_mode: host` only when necessary (Plex, game servers with UDP)
- For multiple compose files sharing a network, create external network first
