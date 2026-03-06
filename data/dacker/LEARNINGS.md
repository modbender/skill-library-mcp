# Learnings — Docker Skill

Notes from using and integrating the Docker skill with OpenClaw, nanobot, and Docker Test.

---

## Installation and usage

- **Installation:** Documented in [SKILL.md](SKILL.md) (macOS Docker Desktop/Homebrew, Linux apt, Windows). After install, start the daemon and verify with `docker run hello-world`.
- **Usage examples:** See [SKILL.md](SKILL.md) — run one-off containers, named create/stop/rm, build and run with port mapping, and `docker compose` up/down.
- **Test pipeline:** The Docker Test skill can run this skill end-to-end with a query that asks to create, run, and delete a container; the test uses `benchmark_mount/query_docker_e2e.txt` and mounts the host Docker socket so the agent can run `docker` inside the container. See Docker Test skill docs for the full pipeline.

---

## Documentation

- **Always prefer official Docker docs** for install steps, CLI syntax, and Dockerfile instructions. Fetch from canonical URLs (see SKILL.md); training data can be outdated for version-specific details.
- **Canonical URLs:** [Get Docker](https://docs.docker.com/get-started/get-docker/), [Dockerfile reference](https://docs.docker.com/reference/dockerfile/), [CLI reference](https://docs.docker.com/reference/cli/docker/).

---

## Dockerfile COPY and paths with spaces

- **Quote COPY destinations (and sources) that contain spaces** so the Dockerfile parser does not split the path (e.g. `COPY . "/app/Docker Skill"`). Unquoted paths with spaces can cause build failures or wrong destinations.

## Volume mounts

- **Use stable host paths** for bind mounts. Paths from `mktemp` or other temporary directories can fail to mount in some environments (sandboxes, CI, remote Docker).
- Prefer a directory under the project or skill root (e.g. `./benchmark_mount`, `./data`) so Docker can reliably mount it.

---

## macOS

- **Docker Desktop** is the standard; after install, ensure the app is running so the daemon is available.
- **Colima:** If using Colima instead, set `DOCKER_HOST` (e.g. `unix://$HOME/.colima/default/docker.sock`) so the CLI and scripts find the daemon.
- **Homebrew:** For automation/OpenClaw, `brew install --cask docker` then start Docker Desktop.

---

## Daemon and errors

- **"Cannot connect to the Docker daemon"** — Start Docker Desktop or the engine service; confirm with `docker run hello-world`.
- **Permission denied (Linux)** — Add user to `docker` group; log out/in or `newgrp docker`.

---

## Integration with Docker Test

- The **Docker Test** skill builds images and runs containers that need Docker on the host. The **Docker** skill is the right place to look for install/usage when Docker is missing or when writing Dockerfiles/commands.
- When adding or testing skills in Docker (e.g. nanobot in a container), ensure the host has Docker installed and the daemon running; use stable paths for any mounted query or results directories.

### When this skill runs inside Docker Test

- The test container is built **with Docker CLI installed** (docker-cli package) and the **host Docker socket mounted** at `/var/run/docker.sock`. So when the Docker skill is the one under test, **Docker is already available**: the agent should run `docker` directly (e.g. `docker run`, `docker stop`, `docker rm`, `docker rmi`) and need not install Docker or use sudo. If `which docker` or `docker --version` fails, the agent can try `/usr/bin/docker` or `/usr/local/bin/docker` (both are present in that environment).
