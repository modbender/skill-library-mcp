---
name: restart
description: Restart system services. Use when the user explicitly requests to restart picoclaw or other services. Executes `restart.sh`.
---

# Restart Service

## Usage

When user requests to restart a service (e.g., "重启 picoclaw"), execute:

```bash
/root/.picoclaw/workspace/skills/restart/restart.sh
```

## Notes

- Only restart services when explicitly requested
- Use `service` command for system service management
- Ensure the service name is correct before execution
