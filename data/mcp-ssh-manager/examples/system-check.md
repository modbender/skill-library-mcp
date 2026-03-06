# System Check Workflow Example

This example demonstrates a complete system health check workflow using MCP ssh-manager with workdir organization.

## Scenario

Perform a weekly system health check on the rock-5t server, save results for comparison, and document findings.

## Workflow

### Step 1: Prepare Workdir

```bash
# Create workdir
mkdir -p ~/.ssh-workdir/rock-5t/2026-02-07-system-check/output

# Create tracking files
cat > ~/.ssh-workdir/rock-5t/2026-02-07-system-check/commands.md << 'EOF'
# System Check Commands - 2026-02-07

## Disk
df -h
df -i

## Memory
free -h

## CPU
top -bn1 | head -20

## Network
netstat -tulpn
ss -tulpn

## Services
systemctl list-units --type=service --state=running
systemctl list-units --type=service --failed

## Docker
docker ps -a

## Users
who
last | head -10
EOF

echo "## System Check Started: $(date)" > ~/.ssh-workdir/rock-5t/2026-02-07-system-check/summary.md
```

### Step 2: Check Existing Session

```bash
ssh_session_list
```

Response: No active sessions found.

### Step 3: Start Session

```bash
ssh_session_start server="rock-5t" name="system-check"
```

Response: session_id = "sess-abc123"

### Step 4: Execute Commands and Save Outputs

```bash
# Disk
ssh_session_send session="sess-abc123" command="df -h" > ~/.ssh-workdir/rock-5t/2026-02-07-system-check/output/df-h.txt
ssh_session_send session="sess-abc123" command="df -i" > ~/.ssh-workdir/rock-5t/2026-02-07-system-check/output/df-i.txt

# Memory
ssh_session_send session="sess-abc123" command="free -h" > ~/.ssh-workdir/rock-5t/2026-02-07-system-check/output/memory.txt

# CPU
ssh_session_send session="sess-abc123" command="top -bn1 | head -20" > ~/.ssh-workdir/rock-5t/2026-02-07-system-check/output/cpu.txt

# Network
ssh_session_send session="sess-abc123" command="netstat -tulpn" > ~/.ssh-workdir/rock-5t/2026-02-07-system-check/output/network.txt
ssh_session_send session="sess-abc123" command="ss -tulpn" > ~/.ssh-workdir/rock-5t/2026-02-07-system-check/output/ss.txt

# Services
ssh_session_send session="sess-abc123" command="systemctl list-units --type=service --state=running" > ~/.ssh-workdir/rock-5t/2026-02-07-system-check/output/services-running.txt
ssh_session_send session="sess-abc123" command="systemctl list-units --type=service --failed" > ~/.ssh-workdir/rock-5t/2026-02-07-system-check/output/services-failed.txt

# Docker
ssh_session_send session="sess-abc123" command="docker ps -a" > ~/.ssh-workdir/rock-5t/2026-02-07-system-check/output/docker.txt

# Users
ssh_session_send session="sess-abc123" command="who" > ~/.ssh-workdir/rock-5t/2026-02-07-system-check/output/who.txt
ssh_session_send session="sess-abc123" command="last | head -10" > ~/.ssh-workdir/rock-5t/2026-02-07-system-check/output/last.txt
```

### Step 5: Close Session

```bash
ssh_session_close session="sess-abc123"
```

### Step 6: Health Check

```bash
ssh_health_check server="rock-5t" > ~/.ssh-workdir/rock-5t/2026-02-07-system-check/status.json
```

### Step 7: Compare with Previous

```bash
# Check if previous check exists
ls ~/.ssh-workdir/rock-5t/ | grep system-check
# Output: 2026-01-31-system-check

# Compare disk usage
diff ~/.ssh-workdir/rock-5t/2026-01-31-system-check/output/df-h.txt \
     ~/.ssh-workdir/rock-5t/2026-02-07-system-check/output/df-h.txt

# Compare memory
diff ~/.ssh-workdir/rock-5t/2026-01-31-system-check/output/memory.txt \
     ~/.ssh-workdir/rock-5t/2026-02-07-system-check/output/memory.txt
```

### Step 8: Write Summary

```bash
cat > ~/.ssh-workdir/rock-5t/2026-02-07-system-check/summary.md << 'EOF'
# System Check Summary - 2026-02-07

## Overview
Weekly system health check for rock-5t server.

## Disk
- Root (/): 72% used (14G/20G) ⚠️ +2% from last week
- /home: 45% used
- /var: 58% used
- /dev/sda1 (data): 65% used

## Memory
- Total: 16GB
- Used: 7.2GB (45%)
- Free: 8.8GB
- Swap: 2GB/4GB (50%)

## CPU
- Load average: 0.5, 0.3, 0.2
- No processes using excessive CPU

## Network
- All ports normal
- No unusual connections detected

## Services
- nginx: Running ✅
- docker: Running ✅
- postgres: Running ✅
- fail2ban: Running ✅
- redis: Running ✅

## Docker
- 5 containers running
- 2 stopped (old images)

## Issues Found

### ⚠️ Disk Usage Increased
Root partition at 72%, up from 70% last week.
Recommend: Clean up /var/log and old Docker images.

### ⚠️ Redis Using More Memory
Redis using 850MB, up from 600MB last month.
Recommend: Check Redis configuration and memory limits.

## Recommendations

1. **High Priority**
   - Clean up old Docker images: `docker image prune -a`
   - Archive old log files in /var/log

2. **Medium Priority**
   - Review Redis memory configuration
   - Check if /data partition needs expansion

3. **Low Priority**
   - Remove stopped containers: `docker container prune`

## Comparison with Previous

| Metric | 2026-01-31 | 2026-02-07 | Change |
|--------|------------|------------|--------|
| Root disk | 70% | 72% | +2% |
| Memory used | 6.8GB | 7.2GB | +0.4GB |
| Running services | 5 | 5 | - |
| Failed services | 0 | 0 | - |

## Next Check
Schedule for 2026-02-14 (next Monday).
EOF
```

## Complete Workdir Structure

```
~/.ssh-workdir/
└── rock-5t/
    └── 2026-02-07-system-check/
        ├── commands.md           # Executed commands
        ├── output/
        │   ├── df-h.txt        # Disk usage
        │   ├── df-i.txt        # Disk inodes
        │   ├── memory.txt       # Memory info
        │   ├── cpu.txt         # CPU load
        │   ├── network.txt     # Network connections
        │   ├── ss.txt          # Socket stats
        │   ├── services-running.txt
        │   ├── services-failed.txt
        │   ├── docker.txt      # Docker containers
        │   ├── who.txt         # Logged in users
        │   └── last.txt        # Recent logins
        ├── status.json         # Health check JSON
        └── summary.md          # Findings and recommendations
```

## Key Takeaways

1. **Use session for multi-command tasks** - Efficient and maintains context
2. **Save all outputs** - Enables future comparison
3. **Write detailed summary** - Quick reference for future reviews
4. **Compare with previous** - Track trends and changes
5. **Categorize by priority** - Focus on important issues first
