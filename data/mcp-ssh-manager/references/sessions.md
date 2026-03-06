# Session Management Deep Dive

This document provides detailed information about SSH session management using MCP ssh-manager.

## Session Lifecycle

### 1. Check Existing Sessions

Always check for existing sessions before starting a new one:

```bash
ssh_session_list
```

Response format:
```json
[
  {
    "id": "session-123",
    "name": "deploy",
    "server": "rock5t",
    "state": "active",
    "started": "2026-02-07T10:00:00Z"
  }
]
```

### 2. Start a Session

```bash
ssh_session_start server="rock5t" name="deploy"
```

Response includes:
- `session_id`: Unique identifier for the session
- `name`: Optional name for identification
- `server`: Target server name
- `state`: Session state (connecting, connected, etc.)

### 3. Send Commands

```bash
ssh_session_send session="{session_id}" command="cd /home/imax"
ssh_session_send session="{session_id}" command="pwd"  # Will be in /home/imax
```

### 4. Close Session

```bash
ssh_session_close session="{session_id}"
# or close all sessions
ssh_session_close session="all"
```

## Session State Management

### Checking Session State

```bash
ssh_connection_status action="status"
```

States:
- **connecting**: Session is being established
- **connected**: Active and ready for commands
- **idle**: Connected but no recent activity
- **expired**: Server-side timeout occurred
- **closed**: Session was explicitly closed

### Reconnecting Expired Sessions

If a session becomes unresponsive:

```bash
# Check current state
ssh_connection_status action="status"

# If expired, create new session
ssh_session_start server="rock5t" name="retry-task"
```

### Session Persistence

Sessions persist based on:
1. **Server configuration**: `/etc/ssh/sshd_config`
   ```
   ClientAliveInterval 60
   ClientAliveCountMax 3
   ```
   - `ClientAliveInterval`: Seconds between keepalive checks
   - `ClientAliveCountMax`: Max unanswered keepalives before disconnect
   - Default: 60s × 3 = 3 minutes of inactivity

2. **Network stability**: Unstable networks may cause disconnects

3. **Server restart**: Always terminates sessions

## Session Best Practices

### For Short Tasks

```bash
# No session needed
ssh_execute server="rock5t" command="df -h"
ssh_execute server="rock5t" command="free -h"
```

### For Multi-step Tasks

```bash
# Check existing
ssh_session_list

# Start session
ssh_session_start server="rock5t" name="deployment"

# Execute steps
ssh_session_send session="{id}" command="cd /home/imax/app"
ssh_session_send session="{id}" command="git pull"
ssh_session_send session="{id}" command="npm install"
ssh_session_send session="{id}" command="npm run build"
ssh_session_send session="{id}" command="pm2 restart app"

# Close
ssh_session_close session="{id}"
```

### For Long-running Monitoring

```bash
# Start session with monitoring
ssh_session_start server="rock5t" name="monitor-log"

# Periodic checks (session stays alive)
ssh_session_send session="{id}" command="tail -n 100 /var/log/app.log"
sleep 60
ssh_session_send session="{id}" command="tail -n 100 /var/log/app.log"

# Close
ssh_session_close session="{id}"
```

## Session Troubleshooting

### Session Becomes Unresponsive

1. **Check session state**
   ```bash
   ssh_connection_status action="status"
   ```

2. **Try ping**
   ```bash
   ssh_session_send session="{id}" command="echo pong"
   ```

3. **If still unresponsive, create new session**
   ```bash
   ssh_session_start server="rock5t" name="replacement"
   ```

### Connection Dropped

If connection drops:

1. Check network connectivity
2. Verify server is online: `ssh_connection_status action="status"`
3. Start new session if needed

### Too Many Sessions

If you have many idle sessions:

```bash
# List all sessions
ssh_session_list

# Close specific session
ssh_session_close session="{id}"

# Or close all
ssh_session_close session="all"
```

## Server-Side Configuration

For longer session timeouts, server admin can configure `/etc/ssh/sshd_config`:

```
# Keepalive settings
ClientAliveInterval 120      # 2 minutes
ClientAliveCountMax 10       # 10 checks = 20 minutes total

# Or disable keepalive (not recommended)
ClientAliveInterval 0
```

Reload SSH daemon after changes:
```bash
sudo systemctl reload sshd
```

## Session and Workdir Integration

Combine sessions with workdir for complete tracking:

```bash
# 1. Create workdir
mkdir -p ~/.ssh-workdir/rock5t/2026-02-07-deployment/output

# 2. Start session
ssh_session_start server="rock5t" name="deployment"

# 3. Log and execute
echo "## Deployment Commands" > ~/.ssh-workdir/rock5t/2026-02-07-deployment/commands.md
echo "git pull" >> ~/.ssh-workdir/rock5t/2026-02-07-deployment/commands.md

ssh_session_send session="{id}" command="git pull origin main" > ~/.ssh-workdir/rock5t/2026-02-07-deployment/output/git-pull.txt

# 4. Continue logging
echo "npm install" >> ~/.ssh-workdir/rock5t/2026-02-07-deployment/commands.md
ssh_session_send session="{id}" command="npm install" > ~/.ssh-workdir/rock5t/2026-02-07-deployment/output/npm-install.txt

# 5. Close session
ssh_session_close session="{id}"

# 6. Write summary
echo "## Deployment Summary" > ~/.ssh-workdir/rock5t/2026-02-07-deployment/summary.md
echo "Status: Successful" >> ~/.ssh-workdir/rock5t/2026-02-07-deployment/summary.md
echo "Git commit: $(cat ~/.ssh-workdir/rock5t/2026-02-07-deployment/output/git-pull.txt | grep -o 'commit [a-f0-9]*')" >> ~/.ssh-workdir/rock5t/2026-02-07-deployment/summary.md
```
