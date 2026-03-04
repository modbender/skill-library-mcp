---
name: portainer
description: Comprehensive management for Portainer CE environments and stacks. Supports listing environments, managing Docker Compose/Swarm stacks, and executing raw Docker commands via proxy. Use when the user needs to deploy apps, check container status, or manage networks within Portainer. Requires a Portainer API Key configured in OpenClaw.
---

# Portainer Manager Skill

Manage your Docker infrastructure through the Portainer CE HTTP API.

## Setup

Add your Portainer API Key to your OpenClaw configuration:

```bash
openclaw config set portainer.apiKey "your_token_here"
```

## Functions

*   `list_environments()`: Retrieves all Portainer environments (endpoints).
*   `list_stacks(environment_id)`: Lists all stacks. Optional: filter by environment ID.
*   `inspect_stack(stack_id)`: Returns full JSON details for a specific stack.
*   `deploy_stack(stack_name, compose_content, environment_id)`: Launches a new Docker Compose stack from a string.
*   `remove_stack(stack_id)`: Deletes a stack by ID.
*   `execute_docker_command(environment_id, path, method, payload)`: Advanced. Proxies raw Docker API requests (e.g., `/containers/json`) through Portainer.
