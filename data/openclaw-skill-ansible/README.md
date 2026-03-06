# openclaw-skill-ansible

Secure operations skill for the OpenClaw Ansible mesh.

Suggested positioning name:

- MeshOps Control Plane

This skill provides controlled gateway operations for:

1. plugin install/setup (`setup-ansible-plugin`)
2. health verification (`openclaw ansible status`)
3. optional high-risk operations behind explicit env gates (`run-cmd`, `deploy-skill`)

## Trust and Safety Highlights

1. caller authorization in `src/handler.py`
2. shell-injection-safe dispatch (argv execution)
3. required SHA-256 + HTTPS for artifact deployment
4. explicit high-risk toggles and allowlists

## Required Binaries

- `openclaw`, `jq`, `curl`, `tar`, `sha256sum`/`shasum`, `timeout`, `git`
