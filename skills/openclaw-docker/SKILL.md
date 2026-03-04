---
name: openclaw-docker
description: "Manage Docker containers and Compose projects via OpenClaw tools"
---

# @elvatis_com/openclaw-docker

OpenClaw plugin for Docker container operations and Docker Compose project control.

## Features

- Docker daemon connection via unix socket or TCP
- Optional TLS for remote daemon access
- Read and write container tools
- Docker Compose integration via `docker compose` CLI
- Safety controls with `readOnly` and `allowedOperations`
- Configurable command timeout

## Prerequisites

- **Docker Engine** installed and running on the host
- **Docker CLI** (`docker` command) available in PATH (required for Compose operations)
- Access to the Docker socket (`/var/run/docker.sock`) or a remote Docker daemon via TCP

## Installation

```bash
npm install @elvatis_com/openclaw-docker
```

## Security Notes

- **Use `readOnly: true`** if you only need observation (ps, logs, inspect). This limits the blast radius.
- **TLS keys:** If using TCP with TLS, keep your PEM files protected. Only configure trusted certificate paths.
- **Compose directories:** The plugin runs `docker compose` commands in whichever directories you configure as `composeProjects`. Only configure trusted project paths.
- **Least privilege:** Run the plugin in an environment with minimal Docker permissions when possible.

## Configuration

### Local socket (default)

```json
{
  "plugins": {
    "openclaw-docker": {
      "socketPath": "/var/run/docker.sock",
      "readOnly": false,
      "allowedOperations": ["ps", "logs", "inspect", "start", "stop", "restart", "compose_up", "compose_down", "compose_ps"],
      "composeProjects": [
        { "name": "aegis", "path": "/opt/aegis" }
      ],
      "timeoutMs": 15000
    }
  }
}
```

### Remote Docker daemon with TLS

```json
{
  "plugins": {
    "openclaw-docker": {
      "host": "10.0.0.20",
      "port": 2376,
      "tls": {
        "caPath": "/etc/openclaw/docker/ca.pem",
        "certPath": "/etc/openclaw/docker/cert.pem",
        "keyPath": "/etc/openclaw/docker/key.pem",
        "rejectUnauthorized": true
      },
      "readOnly": true,
      "composeProjects": []
    }
  }
}
```

## Available Tools

- `docker_ps`
- `docker_logs`
- `docker_inspect`
- `docker_start`
- `docker_stop`
- `docker_restart`
- `docker_compose_up`
- `docker_compose_down`
- `docker_compose_ps`

## Usage Examples

- "List all running containers"
- "Show the last 200 lines from api-gateway logs"
- "Inspect redis container"
- "Restart identity-service"
- "Bring aegis compose project up"
- "Show status of aegis compose services"

## Safety and Permissions

- `readOnly: true` allows only `ps`, `logs`, `inspect`, and `compose_ps`
- `allowedOperations` limits which tools can be executed
- Compose operations are limited to projects in `composeProjects`
- Commands use timeout protection via `timeoutMs`

## Development

```bash
npm install
npm run build
npm test
```

## License

MIT
