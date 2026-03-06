# Docker Reference — CLI and Dockerfile Essentials

Condensed reference for daily use. Full specs: [Docker CLI](https://docs.docker.com/reference/cli/docker/), [Dockerfile](https://docs.docker.com/reference/dockerfile/), [Compose file](https://docs.docker.com/reference/compose-file/).

---

## Docker CLI (frequently used)

| Command | Purpose |
|--------|---------|
| `docker run [OPTIONS] IMAGE [COMMAND]` | Create and start a container |
| `docker run -d` | Run in background (detached) |
| `docker run -p HOST:CONTAINER` | Publish port (e.g. `-p 3000:3000` or `-p 127.0.0.1:3000:3000`) |
| `docker run -it IMAGE CMD` | Interactive TTY (e.g. `docker run -it ubuntu /bin/bash`) |
| `docker run --name NAME` | Set container name |
| `docker run -v HOST:CONTAINER` | Bind mount volume (use **stable host paths**, e.g. under project root; avoid temp dirs so mounts work in all environments) |
| `docker run -e VAR=value` | Set env var |
| `docker build -t TAG [PATH]` | Build image; default path `.` |
| `docker build -f Dockerfile.path .` | Use alternate Dockerfile |
| `docker ps` | List running containers |
| `docker ps -a` | List all containers |
| `docker images` | List images |
| `docker pull IMAGE` | Pull image from registry |
| `docker stop CONTAINER` | Stop container |
| `docker rm CONTAINER` | Remove container |
| `docker rmi IMAGE` | Remove image |
| `docker logs CONTAINER` | Show container logs |
| `docker exec -it CONTAINER CMD` | Run command in running container |
| `docker system prune -a` | Remove unused data (images, containers, networks) |

**Compose (v2 plugin):**

| Command | Purpose |
|--------|---------|
| `docker compose up -d` | Start services in background |
| `docker compose down` | Stop and remove containers/networks |
| `docker compose build` | Build service images |
| `docker compose logs -f` | Follow logs |

---

## Dockerfile essentials

- **Location:** Usually project root, named `Dockerfile` (no extension).
- **Syntax:** `# syntax=docker/dockerfile:1` (optional, recommended for reproducible builds).

| Instruction | Purpose |
|-------------|---------|
| `FROM image[:tag]` | Base image (e.g. `FROM node:24-alpine`) |
| `WORKDIR /path` | Set working directory |
| `COPY src dest` | Copy files from build context (e.g. `COPY . .`). **Quote src or dest if the path contains spaces** (e.g. `COPY . "/app/Docker Skill"`). |
| `ADD src dest` | Like COPY but supports URLs/tarballs; prefer COPY when possible |
| `RUN command` | Run command in layer (e.g. `RUN npm install`) |
| `ENV KEY=value` | Set environment variable |
| `EXPOSE port` | Document port (does not publish; use `-p` at run) |
| `CMD ["exec","arg"]` | Default command when container starts (exec form preferred) |
| `ENTRYPOINT ["exec","arg"]` | Fixed entrypoint; CMD becomes args |

**Example (Node app):**

```dockerfile
# syntax=docker/dockerfile:1
FROM node:24-alpine
WORKDIR /app
COPY . .
RUN npm install --omit=dev
CMD ["node", "src/index.js"]
EXPOSE 3000
```

**Paths with spaces:** Quote the COPY destination (or source) when the path contains spaces so the parser does not split on them (e.g. `COPY . "/app/My Project"` or `COPY "./Docker Skill" /app`).

**Best practices:** Use specific tags (e.g. `node:24-alpine`), order instructions to maximize cache (deps before app copy), use `.dockerignore` to exclude unneeded files.

---

## Compose file (minimal)

Default file: `compose.yaml` or `docker-compose.yaml` in project root.

```yaml
services:
  app:
    build: .
    ports:
      - "127.0.0.1:3000:3000"
    environment:
      - NODE_ENV=production
  # db:
  #   image: postgres:16-alpine
  #   volumes:
  #     - dbdata:/var/lib/postgresql/data
# volumes:
#   dbdata:
```

Run: `docker compose up -d`. Full spec: [Compose file reference](https://docs.docker.com/reference/compose-file/).

---

## Troubleshooting

- **"Cannot connect to the Docker daemon"** — Start Docker Desktop (Mac/Windows) or `sudo systemctl start docker` (Linux). On macOS with Colima, set `DOCKER_HOST` (e.g. `unix://$HOME/.colima/default/docker.sock`).
- **Permission denied (Linux)** — Add user to `docker` group: `sudo usermod -aG docker $USER`; log out/in or `newgrp docker`.
- **Volume mount empty or missing in container** — Use a stable host path (e.g. under project root), not a temp dir; see [LEARNINGS.md](LEARNINGS.md).
- **Port already in use** — Change host port in `-p` (e.g. `-p 127.0.0.1:3001:3000`) or stop the process using the port.
- **Build context too large** — Add entries to `.dockerignore` (e.g. `node_modules`, `.git`, `*.log`).
- **COPY fails or wrong path when dir has spaces** — Quote the destination (and source if needed) in the Dockerfile (e.g. `COPY . "/app/Docker Skill"`).

For more, see [Docker troubleshooting](https://docs.docker.com/desktop/troubleshoot-and-support/troubleshoot/) and [reference](https://docs.docker.com/reference/).
