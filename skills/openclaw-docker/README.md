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
- "Follow api-gateway logs for 30 seconds"
- "Inspect redis container"
- "Restart identity-service"
- "Bring aegis compose project up"
- "Show status of aegis compose services"

### Follow mode (docker_logs)

The `docker_logs` tool supports real-time log streaming via `follow: true`. Logs are collected for a bounded duration and returned as a single result.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `containerId` | string | (required) | Container name or ID |
| `tail` | number | 100 | Number of existing lines to include |
| `follow` | boolean | false | Enable real-time log streaming |
| `followDurationMs` | number | 10000 | How long to follow (ms), capped by `timeoutMs` |

## Safety and Permissions

- `readOnly: true` allows only `ps`, `logs`, `inspect`, and `compose_ps`
- `allowedOperations` limits which tools can be executed
- Compose operations are limited to projects in `composeProjects`
- Commands use timeout protection via `timeoutMs`

## Development

```bash
npm install
npm run build
npm test                # unit tests (mocked Docker client)
npm run test:integration # integration tests (requires running Docker daemon)
npm run test:all         # both unit and integration tests
```

### CI

The GitHub Actions workflow (`.github/workflows/ci.yml`) runs unit tests on every push and pull request to `main`, followed by integration tests against the real Docker daemon available on the CI runner.

## Shared Template

For automation that creates GitHub issues, use `src/templates/github-issue-helper.ts`.
It provides `isValidIssueRepoSlug()`, `resolveIssueRepo()`, and `buildGhIssueCreateCommand()`.

## License

MIT
