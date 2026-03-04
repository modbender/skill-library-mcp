---
name: docker
displayName: Docker
description: Installs and uses Docker reliably with official docs. Use when installing Docker (Desktop or Engine), building or running containers, writing Dockerfiles, using docker compose, or when the user asks about containers, images, or Docker CLI.
homepage: https://docs.docker.com/
metadata: {"openclaw": {"requires": {"anyBins": ["docker"]}, "install": {"brew": "docker"}, "primaryEnv": null}}
---

# Docker — Install and Use Containers

Enables OpenClaw (and Cursor) to install Docker and use it reliably. Base all guidance on **official Docker docs**; when in doubt, fetch from canonical URLs below.

## When to Apply

- User wants to **install Docker** (macOS, Linux, Windows)
- User asks about **containers**, **images**, **Dockerfile**, **docker compose**
- Building, running, or debugging **Docker** commands or workflows
- User asks for "latest Docker docs" or "how do I use Docker"

## Canonical Documentation URLs

| Purpose | URL |
|--------|-----|
| Get started / overview | https://docs.docker.com/get-started/overview/ |
| Get Docker (install) | https://docs.docker.com/get-started/get-docker/ |
| Develop with containers | https://docs.docker.com/get-started/introduction/develop-with-containers/ |
| Guides | https://docs.docker.com/guides/ |
| Manuals (install, config, use) | https://docs.docker.com/manuals/ |
| Reference (CLI, Dockerfile, API) | https://docs.docker.com/reference/ |
| Engine install (Linux) | https://docs.docker.com/engine/install/ |
| Docker Desktop Mac | https://docs.docker.com/desktop/install/mac-install/ |
| Docker CLI reference | https://docs.docker.com/reference/cli/docker/ |
| Dockerfile reference | https://docs.docker.com/reference/dockerfile/ |

**Rule:** For install steps, CLI syntax, or Dockerfile instructions, **fetch the relevant doc URL** and use that content. Do not rely on training data for version-specific install or command details.

---

## Installation (Reliable Paths)

### macOS

**Recommended: Docker Desktop**

1. Download from official docs: [Install Docker Desktop on Mac](https://docs.docker.com/desktop/install/mac-install/).
   - Apple Silicon: `https://desktop.docker.com/mac/main/arm64/Docker.dmg`
   - Intel: `https://desktop.docker.com/mac/main/amd64/Docker.dmg`
2. Open `Docker.dmg`, drag Docker to Applications, then open Docker.app and accept terms.
3. **CLI install (optional):** After downloading the DMG:
   ```bash
   sudo hdiutil attach Docker.dmg
   sudo /Volumes/Docker/Docker.app/Contents/MacOS/install
   sudo hdiutil detach /Volumes/Docker
   ```
4. Verify: `docker run hello-world`

**OpenClaw / automation:** If `docker` is missing and the user is on macOS, suggest installing via Homebrew: `brew install --cask docker`, then starting Docker Desktop so the daemon is running.

### Linux (Ubuntu example)

1. Prefer **Docker Engine from apt** (see [Install Docker Engine on Ubuntu](https://docs.docker.com/engine/install/ubuntu/)).
2. Remove conflicting packages first:
   ```bash
   sudo apt remove $(dpkg --get-selections docker.io docker-compose docker-compose-v2 docker-doc podman-docker containerd runc 2>/dev/null | cut -f1)
   ```
3. Add Docker’s apt repo, then:
   ```bash
   sudo apt update
   sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
   sudo systemctl start docker
   sudo docker run hello-world
   ```
4. Optional (run without sudo): [Linux postinstall](https://docs.docker.com/engine/install/linux-postinstall/) — add user to `docker` group.

**Convenience script (dev/test only):** `curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh`. Not recommended for production.

### Windows

Use [Get Docker](https://docs.docker.com/get-started/get-docker/) and follow **Docker Desktop for Windows** (WSL2 backend recommended).

---

## Core Workflow: Build and Run

1. **Dockerfile** in app directory (see [reference.md](reference.md) or [Dockerfile reference](https://docs.docker.com/reference/dockerfile/)).
2. **Build image:** `docker build -t <name> .`
3. **Run container:** `docker run -d -p HOST_PORT:CONTAINER_PORT <name>` (e.g. `-p 127.0.0.1:3000:3000`).
4. **List containers:** `docker ps` (running), `docker ps -a` (all).
5. **Stop/remove:** `docker stop <container>`, `docker rm <container>`.

Example from official getting-started:

```bash
docker build -t getting-started .
docker run -d -p 127.0.0.1:3000:3000 getting-started
# Open http://localhost:3000
```

---

## Daemon Must Be Running

- **Docker Desktop (Mac/Windows):** Ensure Docker Desktop app is running; `docker` CLI talks to its daemon.
- **Linux:** `sudo systemctl start docker` (and `enable` if needed).
- If the user sees "Cannot connect to the Docker daemon", direct them to start Docker Desktop or the engine service and try again.

---

## Quick Reference

- **Images:** `docker pull <image>`, `docker images`, `docker rmi <image>`
- **Containers:** `docker run`, `docker ps`, `docker stop`, `docker rm`, `docker logs <container>`
- **Compose:** `docker compose up -d`, `docker compose down` — use `compose.yaml` in project root (see [Compose file reference](https://docs.docker.com/reference/compose-file/)).
- **Cleanup:** `docker system prune -a` (removes unused images/containers/networks; use with care).

## Additional Resources

- For detailed CLI and Dockerfile syntax, see [reference.md](reference.md).
- For full specs, fetch from the official [reference](https://docs.docker.com/reference/) and [guides](https://docs.docker.com/guides/).
