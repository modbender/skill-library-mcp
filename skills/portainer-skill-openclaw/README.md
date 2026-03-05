# Portainer Skill for OpenClaw

A powerful OpenClaw skill that allows you to manage your Docker infrastructure directly through your Portainer CE instance. Deploy stacks, inspect containers, and execute raw Docker commands without leaving your chat.

## Requirements

This skill uses a Python script to communicate with the Portainer API. You must ensure your OpenClaw environment has Python 3 installed along with the `requests` library.

### Dockerfile Setup
If you are building a custom OpenClaw image (recommended for persistence), add the following to your `Dockerfile`:

```dockerfile
# Install Python 3 and pip
RUN apt-get update && apt-get install -y python3 python3-pip

# Install required Python libraries
RUN pip3 install requests --break-system-packages
```

*(Note: `--break-system-packages` is often required on newer Debian/Ubuntu versions like Bookworm to install packages globally via pip. Alternatively, use a virtual environment.)*

## Features

- **Environment Management**: List and query all your Portainer environments (endpoints).
- **Stack Operations**:
  - List all running stacks across environments.
  - Inspect detailed configuration of specific stacks.
  - **Deploy new stacks** from raw Docker Compose content.
  - Remove stacks safely.
- **Advanced Control**: Execute raw Docker API commands via Portainer's proxy (e.g., restart containers, check logs, inspect networks).

## Prerequisites

- An active [Portainer CE](https://www.portainer.io/) instance.
- An **API Access Token** from your Portainer user settings.
- OpenClaw installed and running.

## Installation

### 1. Import the Skill
You can install this skill directly from GitHub:
```bash
openclaw skill install https://github.com/Leventsoft/portainer-skill-openclaw
```

### 2. Configure Authentication
Set your Portainer URL and API Key in the OpenClaw configuration:

```bash
# Set your Portainer URL (include protocol and port if necessary)
openclaw config set portainer.url "https://portainer.yourdomain.com"

# Set your API Access Token
openclaw config set portainer.apiKey "ptr_..."
```

## Usage

Once installed, you can ask OpenClaw to perform tasks like:

> "List all my running stacks on the home-server environment."
> "Deploy a new nginx stack called 'web-proxy' using this compose file..."
> "Restart the 'database' container on environment 2."

### Available Functions

| Function | Description |
|----------|-------------|
| `list_environments()` | Retrieves a list of all connected Portainer environments/endpoints. |
| `list_stacks(environment_id)` | Lists all stacks, optionally filtered by a specific Environment ID. |
| `inspect_stack(stack_id)` | Returns full JSON details for a specific stack (services, env vars, etc). |
| `deploy_stack(stack_name, compose_content, environment_id)` | Deploys a new stack using the provided Docker Compose YAML string. |
| `remove_stack(stack_id)` | Permanently removes a stack and its associated resources. |
| `execute_docker_command(environment_id, path, method, payload)` | Proxies a raw Docker API request through Portainer (e.g., `POST /containers/my-id/restart`). |

## Security Note

This skill requires an API Key with sufficient privileges to manage your Docker environments. Ensure your OpenClaw instance is secured, as this skill provides powerful access to your infrastructure.

## License

MIT
