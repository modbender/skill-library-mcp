---
name: vscode-tunnel
description: Start VS Code Remote Tunnel in Docker containers for remote terminal access
---

# VS Code Tunnel

Start a VS Code Remote Tunnel in Docker container environments, enabling remote terminal access through VS Code.

## Trigger Phrases

- "start vscode tunnel"
- "open vscode tunnel"
- "connect vscode"
- "launch code tunnel in container"
- "vscode remote"

## Commands

```bash
# Start tunnel (interactive name prompt)
bash /path/to/tunnel.sh start

# Start tunnel with specific name
bash /path/to/tunnel.sh start my-tunnel-name

# Stop tunnel
bash /path/to/tunnel.sh stop

# View status
bash /path/to/tunnel.sh status

# View logs
bash /path/to/tunnel.sh log
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VSCODE_TUNNEL_NAME` | Tunnel name | Interactive input |
| `VSCODE_CLI_DIR` | CLI installation directory | `~/.vscode-cli` |

## Usage Examples

```
User: start vscode tunnel
Agent: Starting VS Code Tunnel...
[Executes: bash tunnel.sh start]
Agent: Tunnel started. Please enter this code in VS Code to authorize: xxxx-xxxx
```

```
User: launch a tunnel named dev-env
Agent: Starting tunnel dev-env...
[Executes: bash tunnel.sh start dev-env]
```

## Commands Reference

| Command | Description |
|---------|-------------|
| `start [name]` | Start tunnel with optional name |
| `stop` | Stop running tunnel |
| `status` | Display tunnel status |
| `log` | View tunnel logs (live) |

## Dependencies

- `curl` - Download CLI
- `tar` - Extract CLI
- `grep` - Log processing

## Notes

1. First-time startup requires Microsoft account authorization
2. Authorization code will be displayed in the log output
3. Tunnel runs in background; needs restart after container reboot

## Platform Support

- Linux x64 (Alpine/Debian/Ubuntu)
- Docker container environments
