cat <<'EOF' > ~/.openclaw/workspace/skills/astra-docker/SKILL.md
---
name: astra-docker
description: "Execute commands, read files, and write files in Astra's Docker container workspace (astra-env). Use this skill whenever you need to interact with your virtual environment at /workspace."
---

# Docker Workspace Access

You have a persistent Docker container called `astra-env` with a workspace mounted at `/workspace`.

## How to Use

Use the `bash` tool to run commands inside the container:

### Execute a command
```bash
sudo docker exec -w /workspace astra-env bash -c "YOUR_COMMAND_HERE"
