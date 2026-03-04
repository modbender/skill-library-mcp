---
name: mcp-ssh-manager
description: This skill should be used when the user asks to "run ssh command", "execute on server", "ssh session", "upload file", "download file", "ssh tunnel", "check server status", "monitor server", "deploy files", "backup server", or needs remote server management. This skill emphasizes session reuse, workdir organization, and content persistence for sustainable operations.
version: 0.1.0
metadata:
  clawdbot:
    emoji: "🖥️"
    requires:
      mcp_servers: ["ssh-manager"]
---

# MCP SSH Manager Skill

> **Original MCP Server**: [mcp-ssh-manager](https://github.com/bvisible/mcp-ssh-manager) by [@bvisible](https://github.com/bvisible)
>
> This skill provides documentation, workflows, and best practices for using the MCP ssh-manager server.

Manage remote SSH servers using MCP ssh-manager tools. Emphasizes session reuse, workdir organization, and content persistence for sustainable operations.

## Quick Reference

### Connection Management

| Task | Tool | Example |
|------|------|---------|
| List servers | `ssh_list_servers` | `ssh_list_servers` |
| Execute command | `ssh_execute` | `ssh_execute server="rock5t" command="df -h"` |
| Execute with sudo | `ssh_execute_sudo` | `ssh_execute_sudo server="rock5t" command="apt update"` |
| Check status | `ssh_connection_status` | `ssh_connection_status action="status"` |

### Session Management

| Task | Tool | Example |
|------|------|---------|
| Start session | `ssh_session_start` | `ssh_session_start server="rock5t" name="deploy"` |
| Send command | `ssh_session_send` | `ssh_session_send session="xxx" command="cd /var"` |
| List sessions | `ssh_session_list` | `ssh_session_list` |
| Close session | `ssh_session_close` | `ssh_session_close session="xxx"` |

### File Operations

| Task | Tool | Example |
|------|------|---------|
| Upload file | `ssh_upload` | `ssh_upload server="rock5t" localPath="." remotePath="/tmp"` |
| Download file | `ssh_download` | `ssh_download server="rock5t" remotePath="/var/log/syslog" localPath="."` |
| Sync files | `ssh_sync` | `ssh_sync server="rock5t" source="local:./dist" destination="remote:/var/www"` |

### Monitoring

| Task | Tool | Example |
|------|------|---------|
| Tail log | `ssh_tail` | `ssh_tail server="rock5t" file="/var/log/syslog" lines=20` |
| Health check | `ssh_health_check` | `ssh_health_check server="rock5t"` |
| Monitor resources | `ssh_monitor` | `ssh_monitor server="rock5t" type="overview"` |
| Service status | `ssh_service_status` | `ssh_service_status server="rock5t" services="nginx,docker"` |

### Tunneling

| Task | Tool | Example |
|------|------|---------|
| Create tunnel | `ssh_tunnel_create` | `ssh_tunnel_create server="rock5t" type="local" localPort=8080 remoteHost="localhost" remotePort=80` |
| List tunnels | `ssh_tunnel_list` | `ssh_tunnel_list` |
| Close tunnel | `ssh_tunnel_close` | `ssh_tunnel_close tunnelId="xxx"` |

### Backup

| Task | Tool | Example |
|------|------|---------|
| Create backup | `ssh_backup_create` | `ssh_backup_create server="rock5t" type="files" name="data"` |
| List backups | `ssh_backup_list` | `ssh_backup_list server="rock5t"` |
| Restore backup | `ssh_backup_restore` | `ssh_backup_restore server="rock5t" backupId="xxx"` |
| Schedule backup | `ssh_backup_schedule` | `ssh_backup_schedule server="rock5t" schedule="0 2 * * *" type="files" name="daily"` |

## Usage Examples

### Example 1: Single Command

```bash
# Simple command - no session needed
ssh_execute server="rock5t" command="df -h"
```

### Example 2: Multi-step Deployment with Session

```bash
# Check existing sessions first
ssh_session_list

# Start a persistent session
ssh_session_start server="rock5t" name="deploy"

# Get session ID from previous response
ssh_session_send session="xxx" command="cd /home/imax/project"
ssh_session_send session="xxx" command="git pull origin main"
ssh_session_send session="xxx" command="npm install"
ssh_session_send session="xxx" command="npm run build"
ssh_session_send session="xxx" command="pm2 restart all"

# Close when done
ssh_session_close session="xxx"
```

### Example 3: System Health Check

```bash
# Check overall health
ssh_health_check server="rock5t"

# Monitor specific resources
ssh_monitor server="rock5t" type="cpu" interval=5 duration=30

# Check specific services
ssh_service_status server="rock5t" services="nginx,docker,postgres"
```

### Example 4: File Deployment

```bash
# Upload deployment package
ssh_upload server="rock5t" localPath="./dist/app.tar.gz" remotePath="/tmp/app.tar.gz"

# Extract and restart
ssh_execute server="rock5t" command="cd /tmp && tar -xzf app.tar.gz && cp -r app/* /var/www/ && pm2 restart app"
```

### Example 5: Log Monitoring

```bash
# Tail real-time logs
ssh_tail server="rock5t" file="/var/log/nginx/access.log" lines=50 follow=true

# Filter with grep
ssh_tail server="rock5t" file="/var/log/syslog" grep="error" lines=100
```

### Example 6: Create SSH Tunnel

```bash
# Local port forward (access remote service locally)
ssh_tunnel_create server="rock5t" type="local" localPort=5432 remoteHost="localhost" remotePort=5432

# Now connect to local:5432 to access remote database
```

## Workdir Management

Store SSH operation results in `~/.ssh-workdir/{hostname}/{YYYY-MM-DD}-{topic}/` for reuse and comparison.

### Structure

```
~/.ssh-workdir/
└── {hostname}/
    └── {YYYY-MM-DD}-{topic}/
        ├── commands.md    # All executed commands
        ├── output/        # Command outputs
        │   ├── df-h.txt
        │   ├── cpu.txt
        │   └── memory.txt
        ├── status.json    # Host status snapshot
        └── summary.md     # Findings and notes
```

### Create Workdir

```bash
# Create new workdir
mkdir -p ~/.ssh-workdir/{hostname}/{YYYY-MM-DD}-{topic}/output

# Create commands log
touch ~/.ssh-workdir/{hostname}/{YYYY-MM-DD}-{topic}/commands.md
```

### Log Commands

```bash
# Add command to log
echo "## $(date)" >> ~/.ssh-workdir/{hostname}/{YYYY-MM-DD}-{topic}/commands.md
echo 'df -h' >> ~/.ssh-workdir/{hostname}/{YYYY-MM-DD}-{topic}/commands.md
```

### Save Output

```bash
# Execute and save
ssh_execute server="{hostname}" command="df -h" > ~/.ssh-workdir/{hostname}/{YYYY-MM-DD}-{topic}/output/df-h.txt
```

### Write Summary

```bash
# Write findings
echo '## System Check Findings' >> ~/.ssh-workdir/{hostname}/{YYYY-MM-DD}-{topic}/summary.md
echo '- Disk usage: 75% on /dev/sda1' >> ~/.ssh-workdir/{hostname}/{YYYY-MM-DD}-{topic}/summary.md
echo '- Memory: 4GB/16GB used' >> ~/.ssh-workdir/{hostname}/{YYYY-MM-DD}-{topic}/summary.md
```

### Reuse Previous Context

```bash
# Check if recent work exists
ls ~/.ssh-workdir/{hostname}/

# Read previous summary
cat ~/.ssh-workdir/{hostname}/{previous-date}-{topic}/summary.md

# Compare outputs
diff ~/.ssh-workdir/{hostname}/{yesterday}-{topic}/output/df-h.txt \
     ~/.ssh-workdir/{hostname}/{today}-{topic}/output/df-h.txt
```

## Session Management Guidelines

### When to Use Sessions

**Use session for:**
- Multi-step deployments
- Tasks requiring state (cd, environment)
- Long-running workflows (more than 3 commands)
- Tasks where command order matters

**Don't use session for:**
- Single quick commands (`df -h`, `pwd`)
- Unrelated commands that don't need state
- Read-only monitoring tasks

### Session Lifecycle

```bash
# 1. Check existing sessions first
ssh_session_list

# 2. Reuse existing session if available and still active
ssh_session_send session="existing-id" command="..."

# 3. Start new session only if necessary
ssh_session_start server="{hostname}" name="{task-name}"

# 4. ALWAYS close when done
ssh_session_close session="{session-id}"
```

### Timeout Considerations

- SSH server may close idle sessions (typically 3-5 minutes by default)
- Configure `ClientAliveInterval` on server for longer keepalive
- For long-running tasks, consider periodic lightweight commands to keepalive
- If session becomes unresponsive, create a new one

## Best Practices

### Before SSH Operations

1. **Check existing sessions**
   ```bash
   ssh_session_list
   ```

2. **Check recent workdir**
   ```bash
   ls ~/.ssh-workdir/{hostname}/
   ```

3. **Create new workdir if starting new task**
   ```bash
   mkdir -p ~/.ssh-workdir/{hostname}/{YYYY-MM-DD}-{topic}/output
   ```

### During SSH Operations

1. **Use appropriate tool for the task**
   - Single command: `ssh_execute`
   - Multi-step: `ssh_session_start` → `ssh_session_send` → `ssh_session_close`
   - File transfer: `ssh_upload/download/sync`
   - Monitoring: `ssh_monitor`, `ssh_tail`, `ssh_health_check`

2. **Log commands to workdir**
   ```bash
   echo "command" >> ~/.ssh-workdir/{hostname}/{YYYY-MM-DD}-{topic}/commands.md
   ```

3. **Save important outputs**
   ```bash
   ssh_execute server="{hostname}" command="df -h" > ~/.ssh-workdir/{hostname}/{YYYY-MM-DD}-{topic}/output/df-h.txt
   ```

### After SSH Operations

1. **Close sessions**
   ```bash
   ssh_session_close session="{session-id}"
   ```

2. **Write summary**
   ```bash
   echo '## Findings' >> ~/.ssh-workdir/{hostname}/{YYYY-MM-DD}-{topic}/summary.md
   ```

3. **Clean up**
   - Close tunnels: `ssh_tunnel_close`
   - Verify all sessions closed: `ssh_session_list`

## Tips

- Use `ssh_session_list` before starting new tasks to reuse existing sessions
- Create workdir for each task to maintain organized history
- Write summaries to quickly recall previous work
- Use `ssh_connection_status action="status"` to check connection health
- For server comparison, store outputs with consistent naming across hosts
- Close sessions when done to free resources
- Configure server-side `ClientAliveInterval` for longer session timeouts if needed

## Additional Resources

### Reference Files

- **`references/sessions.md`** - Session management deep dive
- **`references/workspace.md`** - Workdir structure and usage
- **`references/comparison.md`** - How to compare historical data

### Example Files

- **`examples/system-check.md`** - Complete system health check workflow
- **`examples/deployment.md`** - Multi-step deployment example
- **`examples/troubleshooting.md`** - Problem diagnosis workflow

### Scripts

- **`scripts/create-workdir.sh`** - Create new workdir structure
- **`scripts/log-command.sh`** - Log command to workdir
- **`scripts/save-status.sh`** - Capture and save host status
