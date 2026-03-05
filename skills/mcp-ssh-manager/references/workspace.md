# Workdir Structure and Usage

This document describes how to organize SSH operation results using the workdir structure for sustainable reuse and comparison.

## Purpose

Store SSH operation results per host in an organized structure that enables:
- Historical tracking of operations
- Comparison over time
- Context reuse for troubleshooting
- Team sharing of findings

## Directory Structure

```
~/.ssh-workdir/
└── {hostname}/
    └── {YYYY-MM-DD}-{topic}/
        ├── commands.md     # Executed commands
        ├── output/        # Command outputs
        │   ├── {command}.txt
        │   └── ...
        ├── status.json    # Host status snapshot
        └── summary.md     # Findings and notes
```

## Examples

### System Check

```
~/.ssh-workdir/
└── rock-5t/
    └── 2026-02-07-system-check/
        ├── commands.md
        ├── output/
        │   ├── df-h.txt
        │   ├── cpu.txt
        │   ├── memory.txt
        │   └── network.txt
        ├── status.json
        └── summary.md
```

### Deployment

```
~/.ssh-workdir/
└── rock-5t/
    └── 2026-02-07-deployment/
        ├── commands.md
        ├── output/
        │   ├── git-pull.txt
        │   ├── npm-install.txt
        │   └── build.txt
        ├── status.json
        └── summary.md
```

### Troubleshooting

```
~/.ssh-workdir/
└── rock-5t/
    └── 2026-02-07-nginx-issue/
        ├── commands.md
        ├── output/
        │   ├── nginx-error-log.txt
        │   ├── nginx-config.txt
        │   └── curl-test.txt
        ├── status.json
        └── summary.md
```

## Creating Workdir

### Manual Creation

```bash
# Create workdir
mkdir -p ~/.ssh-workdir/{hostname}/{YYYY-MM-DD}-{topic}/output

# Create tracking files
touch ~/.ssh-workdir/{hostname}/{YYYY-MM-DD}-{topic}/commands.md
touch ~/.ssh-workdir/{hostname}/{YYYY-MM-DD}-{topic}/summary.md
```

### With Script

```bash
# Using provided script
bash scripts/create-workdir.sh {hostname} {YYYY-MM-DD}-{topic}
```

## Logging Commands

### Add Single Command

```bash
echo "## $(date +%Y-%m-%d\ %H:%M:%S)" >> ~/.ssh-workdir/{hostname}/{YYYY-MM-DD}-{topic}/commands.md
echo "df -h" >> ~/.ssh-workdir/{hostname}/{YYYY-MM-DD}-{topic}/commands.md
```

### Add Multiple Commands

```bash
cat > ~/.ssh-workdir/{hostname}/{YYYY-MM-DD}-{topic}/commands.md << 'EOF'
## System Check Commands

### Disk
df -h

### Memory
free -h

### CPU
top -bn1 | head -20
EOF
```

### Execute and Save

```bash
# Execute and save output
ssh_execute server="{hostname}" command="df -h" > ~/.ssh-workdir/{hostname}/{YYYY-MM-DD}-{topic}/output/df-h.txt
```

## Saving Outputs

### Save Single Output

```bash
# Command with file
ssh_execute server="{hostname}" command="df -h" > ~/.ssh-workdir/{hostname}/{YYYY-MM-DD}-{topic}/output/df-h.txt

# Command with grep
ssh_execute server="{hostname}" command="grep error /var/log/syslog" > ~/.ssh-workdir/{hostname}/{YYYY-MM-DD}-{topic}/output/errors.txt
```

### Capture Multiple Outputs

```bash
# Create output directory
mkdir -p ~/.ssh-workdir/{hostname}/{YYYY-MM-DD}-{topic}/output

# Capture multiple status commands
ssh_execute server="{hostname}" command="df -h" > ~/.ssh-workdir/{hostname}/{YYYY-MM-DD}-{topic}/output/df-h.txt
ssh_execute server="{hostname}" command="free -h" > ~/.ssh-workdir/{hostname}/{YYYY-MM-DD}-{topic}/output/memory.txt
ssh_execute server="{hostname}" command="top -bn1 | head -20" > ~/.ssh-workdir/{hostname}/{YYYY-MM-DD}-{topic}/output/cpu.txt
ssh_execute server="{hostname}" command="netstat -tulpn" > ~/.ssh-workdir/{hostname}/{YYYY-MM-DD}-{topic}/output/network.txt
```

## Saving Status Snapshot

### Full Health Check

```bash
# Get comprehensive health check
ssh_health_check server="{hostname}" > ~/.ssh-workdir/{hostname}/{YYYY-MM-DD}-{topic}/status.json
```

### Custom Status

```bash
# Create custom status snapshot
cat > ~/.ssh-workdir/{hostname}/{YYYY-MM-DD}-{topic}/status.json << 'EOF'
{
  "hostname": "rock-5t",
  "checked_at": "2026-02-07T10:00:00Z",
  "disk": {
    "command": "df -h",
    "result": "..."
  },
  "memory": {
    "command": "free -h",
    "result": "..."
  },
  "services": {
    "command": "systemctl list-units --type=service --state=running",
    "result": "..."
  }
}
EOF
```

## Writing Summaries

### Simple Summary

```markdown
# Deployment Summary

## Status
- Success: Yes
- Duration: 5 minutes

## Changes
- Updated to latest main branch
- Installed 23 npm packages
- Built production bundle

## Next Steps
- Monitor error logs
- Verify with curl test
```

### Detailed Summary

```markdown
# System Check Summary - 2026-02-07

## Overview
Regular weekly system health check.

## Disk
- Root: 75% used (15GB/20GB)
- /home: 45% used
- /var: 60% used
- Action needed: Clean up /var/log

## Memory
- Total: 16GB
- Used: 8GB (50%)
- Swap: 2GB/4GB

## Services
- nginx: Running ✅
- docker: Running ✅
- postgres: Running ✅
- fail2ban: Running ✅

## Issues Found
- /var/log at 85% capacity
- 3 failed login attempts in auth.log

## Recommendations
- Clean old log files in /var/log
- Review failed login attempts
- Consider expanding /var partition
```

## Reusing Previous Context

### Check Recent Work

```bash
# List recent workdirs
ls -la ~/.ssh-workdir/{hostname}/

# Output:
# drwxr-xr-x 2 user user 4096 Feb  5 2026-02-05-system-check
# drwxr-xr-x 2 user user 4096 Feb  6 2026-02-06-deployment
# drwxr-xr-x 2 user user 4096 Feb  7 2026-02-07-system-check
```

### Read Previous Summary

```bash
cat ~/.ssh-workdir/{hostname}/2026-02-05-system-check/summary.md
```

### Compare Outputs

```bash
# Compare disk usage over time
diff ~/.ssh-workdir/{hostname}/2026-02-05-system-check/output/df-h.txt \
     ~/.ssh-workdir/{hostname}/2026-02-07-system-check/output/df-h.txt

# Compare memory
diff ~/.ssh-workdir/{hostname}/2026-02-05-system-check/output/memory.txt \
     ~/.ssh-workdir/{hostname}/2026-02-07-system-check/output/memory.txt
```

### Continue Previous Work

```bash
# Check previous commands
cat ~/.ssh-workdir/{hostname}/2026-02-05-deployment/commands.md

# Create new workdir for continuation
mkdir -p ~/.ssh-workdir/{hostname}/2026-02-07-deployment-continued/output

# Reference previous work
echo "## Continuation of 2026-02-05 deployment" >> ~/.ssh-workdir/{hostname}/2026-02-07-deployment-continued/summary.md
echo "Previous work: 2026-02-05-deployment" >> ~/.ssh-workdir/{hostname}/2026-02-07-deployment-continued/summary.md
```

## Cross-Host Comparison

### Compare Multiple Hosts

```bash
# Get latest disk check from each host
cat ~/.ssh-workdir/{host1}/2026-02-07-system-check/output/df-h.txt
cat ~/.ssh-workdir/{host2}/2026-02-07-system-check/output/df-h.txt
cat ~/.ssh-workdir/{host3}/2026-02-07-system-check/output/df-h.txt
```

### Create Comparison Report

```markdown
# Cross-Host Comparison - 2026-02-07

## Disk Usage

### Host1
- Root: 75% used

### Host2  
- Root: 45% used

### Host3
- Root: 80% used ⚠️

## Memory

### Host1: 8GB/16GB (50%)
### Host2: 4GB/8GB (50%)
### Host3: 12GB/16GB (75%) ⚠️
```

## Integration with MCP Commands

### Complete Workflow Example

```bash
# 1. Create workdir
mkdir -p ~/.ssh-workdir/{hostname}/{YYYY-MM-DD}-{topic}/output

# 2. Start session
ssh_session_start server="{hostname}" name="{topic}"

# 3. Execute and log
ssh_session_send session="{session_id}" command="df -h" > ~/.ssh-workdir/{hostname}/{YYYY-MM-DD}-{topic}/output/df-h.txt
ssh_session_send session="{session_id}" command="free -h" > ~/.ssh-workdir/{hostname}/{YYYY-MM-DD}-{topic}/output/memory.txt
ssh_session_send session="{session_id}" command="top -bn1" > ~/.ssh-workdir/{hostname}/{YYYY-MM-DD}-{topic}/output/cpu.txt

# 4. Close session
ssh_session_close session="{session_id}"

# 5. Save health check
ssh_health_check server="{hostname}" > ~/.ssh-workdir/{hostname}/{YYYY-MM-DD}-{topic}/status.json

# 6. Write summary
cat > ~/.ssh-workdir/{hostname}/{YYYY-MM-DD}-{topic}/summary.md << 'EOF'
# System Check Summary - {date}

## Overview
Automated system health check.

## Disk
{df -h output}

## Memory
{free -h output}

## CPU
{top output}

## Issues
None detected.

## Recommendations
None.
EOF
```

## Best Practices

1. **Consistent naming**: Use `YYYY-MM-DD-{topic}` format
2. **Save outputs**: Don't just log commands, save their outputs
3. **Write summaries**: Quick reference for future you
4. **Compare over time**: Use diff to see changes
5. **Group related work**: Multiple commands in same workdir
6. **Clean up**: Remove old workdirs periodically (keep last N)
