# Multi-step Deployment Workflow Example

This example demonstrates a complete multi-step deployment workflow using MCP ssh-manager with session management and workdir organization.

## Scenario

Deploy a new version of an application to the rock-5t server, maintaining session state throughout the deployment process.

## Pre-deployment Preparation

### Step 1: Check Existing Session and Workdir

```bash
# Check for existing sessions
ssh_session_list

# Expected output (if session exists):
# [{"id":"sess-xxx","name":"previous-task","server":"rock-5t","state":"active"}]

# If session exists and related, reuse it
# Otherwise, close it and start new

# Check previous deployments
ls ~/.ssh-workdir/rock-5t/ | grep deployment
```

### Step 2: Create Workdir

```bash
# Create deployment workdir
mkdir -p ~/.ssh-workdir/rock-5t/2026-02-07-deployment/output
mkdir -p ~/.ssh-workdir/rock-5t/2026-02-07-deployment/rollback

# Create tracking files
cat > ~/.ssh-workdir/rock-5t/2026-02-07-deployment/commands.md << 'EOF'
# Deployment Commands - 2026-02-07

## Pre-deployment
1. Backup current version
2. Check service status

## Deployment Steps
3. Pull latest code
4. Install dependencies
5. Run tests
6. Build production bundle
7. Restart services

## Rollback Commands (if needed)
1. Restore from backup
2. Restart services
EOF
```

### Step 3: Pre-deployment Checks

```bash
# Check current service status
ssh_execute server="rock-5t" command="pm2 status"
ssh_execute server="rock-5t" command="pm2 info myapp | grep status"

# Check disk space
ssh_execute server="rock-5t" command="df -h /home /var"

# Check current version
ssh_execute server="rock-5t" command="cd /home/imax/app && git describe --tags"

# Save pre-deployment status
cat > ~/.ssh-workdir/rock-5t/2026-02-07-deployment/pre-status.json << 'EOF'
{
  "timestamp": "2026-02-07T10:00:00Z",
  "version": "v1.2.3",
  "service_status": "running",
  "disk_root": "70%",
  "disk_var": "55%"
}
EOF
```

## Deployment Process

### Step 4: Start Deployment Session

```bash
# Start a named session for tracking
ssh_session_start server="rock-5t" name="deployment-2026-02-07"
```

Response:
```json
{
  "session_id": "sess-abc123",
  "name": "deployment-2026-02-07",
  "server": "rock-5t"
}
```

### Step 5: Backup Current Version

```bash
# Create timestamped backup
ssh_session_send session="sess-abc123" command="cd /home/imax/app && tar -czf /tmp/backup-$(date +%Y%m%d).tar.gz ."
ssh_session_send session="sess-abc123" command="cp /tmp/backup-$(date +%Y%m%d).tar.gz ~/.ssh-workdir/rock-5t/2026-02-07-deployment/rollback/"

# Save backup info
echo "## Backup" >> ~/.ssh-workdir/rock-5t/2026-02-07-deployment/summary.md
echo "Timestamp: $(date)" >> ~/.ssh-workdir/rock-5t/2026-02-07-deployment/summary.md
echo "Location: /tmp/backup-$(date +%Y%m%d).tar.gz" >> ~/.ssh-workdir/rock-5t/2026-02-07-deployment/summary.md
```

### Step 6: Pull Latest Code

```bash
# Pull with output
ssh_session_send session="sess-abc123" command="cd /home/imax/app && git fetch origin main" > ~/.ssh-workdir/rock-5t/2026-02-07-deployment/output/git-fetch.txt
ssh_session_send session="sess-abc123" command="cd /home/imax/app && git pull origin main" > ~/.ssh-workdir/rock-5t/2026-02-07-deployment/output/git-pull.txt

# Get commit info
COMMIT=$(ssh_session_send session="sess-abc123" command="cd /home/imax/app && git rev-parse HEAD")
echo "## Git Info" >> ~/.ssh-workdir/rock-5t/2026-02-07-deployment/summary.md
echo "Commit: $COMMIT" >> ~/.ssh-workdir/rock-5t/2026-02-07-deployment/summary.md
```

### Step 7: Install Dependencies

```bash
# Install npm dependencies
ssh_session_send session="sess-abc123" command="cd /home/imax/app && npm ci" > ~/.ssh-workdir/rock-5t/2026-02-07-deployment/output/npm-ci.txt 2>&1

# Check for errors
if grep -q "ERR\|Error\|error" ~/.ssh-workdir/rock-5t/2026-02-07-deployment/output/npm-ci.txt; then
    echo "⚠️ npm install had warnings/errors - review output" >> ~/.ssh-workdir/rock-5t/2026-02-07-deployment/summary.md
else
    echo "Dependencies installed successfully" >> ~/.ssh-workdir/rock-5t/2026-02-07-deployment/summary.md
fi
```

### Step 8: Run Tests

```bash
# Run tests
ssh_session_send session="sess-abc123" command="cd /home/imax/app && npm test" > ~/.ssh-workdir/rock-5t/2026-02-07-deployment/output/npm-test.txt 2>&1

# Check test results
if grep -q "FAIL\|failed\|0 passing" ~/.ssh-workdir/rock-5t/2026-02-07-deployment/output/npm-test.txt; then
    echo "❌ Tests failed - review output" >> ~/.ssh-workdir/rock-5t/2026-02-07-deployment/summary.md
    echo "Tests failed. Continue anyway? (y/n)" >&2
    # Wait for user confirmation before proceeding
else
    echo "✅ Tests passed" >> ~/.ssh-workdir/rock-5t/2026-02-07-deployment/summary.md
fi
```

### Step 9: Build Production Bundle

```bash
# Build
ssh_session_send session="sess-abc123" command="cd /home/imax/app && npm run build" > ~/.ssh-workdir/rock-5t/2026-02-07-deployment/output/npm-build.txt 2>&1

# Check build success
if [ $? -eq 0 ]; then
    echo "✅ Build successful" >> ~/.ssh-workdir/rock-5t/2026-02-07-deployment/summary.md
else
    echo "❌ Build failed - review output" >> ~/.ssh-workdir/rock-5t/2026-02-07-deployment/summary.md
    # Rollback decision point
fi
```

### Step 10: Restart Services

```bash
# Stop old service
ssh_session_send session="sess-abc123" command="pm2 stop myapp" > ~/.ssh-workdir/rock-5t/2026-02-07-deployment/output/pm2-stop.txt
ssh_session_send session="sess-abc123" command="pm2 delete myapp" > ~/.ssh-workdir/rock-5t/2026-02-07-deployment/output/pm2-delete.txt

# Start new service
ssh_session_send session="sess-abc123" command="cd /home/imax/app && pm2 start npm --name myapp -- run start:prod" > ~/.ssh-workdir/rock-5t/2026-02-07-deployment/output/pm2-start.txt

# Wait for startup
sleep 5

# Check status
ssh_session_send session="sess-abc123" command="pm2 status" > ~/.ssh-workdir/rock-5t/2026-02-07-deployment/output/pm2-status.txt
```

### Step 11: Verify Deployment

```bash
# Check service health
ssh_session_send session="sess-abc123" command="pm2 info myapp | grep -E 'status|restart_time|uptime'" > ~/.ssh-workdir/rock-5t/2026-02-07-deployment/output/pm2-info.txt

# Test endpoint
ssh_session_send session="sess-abc123" command="curl -s -o /dev/null -w '%{http_code}' http://localhost:3000/health" > ~/.ssh-workdir/rock-5t/2026-02-07-deployment/output/health-check.txt
ssh_session_send session="sess-abc123" command="curl -s http://localhost:3000/health" > ~/.ssh-workdir/rock-5t/2026-02-07-deployment/output/health-response.txt

# Check logs for errors
ssh_session_send session="sess-abc123" command="pm2 logs myapp --lines 50 --nostream" > ~/.ssh-workdir/rock-5t/2026-02-07-deployment/output/pm2-logs.txt 2>&1
```

### Step 12: Close Session

```bash
# Close the deployment session
ssh_session_close session="sess-abc123"
```

## Post-deployment Documentation

### Step 13: Save Status and Write Final Summary

```bash
# Save final status
ssh_health_check server="rock-5t" > ~/.ssh-workdir/rock-5t/2026-02-07-deployment/post-status.json

# Write final summary
cat > ~/.ssh-workdir/rock-5t/2026-02-07-deployment/summary.md << 'EOF'
# Deployment Summary - 2026-02-07

## Deployment Info
- **Date**: 2026-02-07
- **Time**: 10:00 - 10:30 UTC
- **Server**: rock-5t
- **Session**: deployment-2026-02-07

## Version Information
- **Previous Version**: v1.2.3
- **New Version**: v1.2.4
- **Git Commit**: abc123def456...

## Deployment Steps

### ✅ Pre-deployment
- Backup created: /tmp/backup-20260207.tar.gz
- Disk space checked: OK

### ✅ Git
- Fetched latest: OK
- Pulled main: OK

### ✅ Dependencies
- npm ci: OK
- No errors

### ✅ Tests
- All tests: PASSED

### ✅ Build
- Build: SUCCESS

### ✅ Deployment
- Service stopped: OK
- Service started: OK

### ✅ Verification
- Health check: HTTP 200
- Service status: running

## Rollback Information
- Backup location: ~/.ssh-workdir/rock-5t/2026-02-07-deployment/rollback/
- Rollback command:
  ```
  cd /home/imax/app && tar -xzf ~/.ssh-workdir/rock-5t/2026-02-07-deployment/rollback/backup-20260207.tar.gz && pm2 restart myapp
  ```

## Issues Found

None.

## Next Steps

1. Monitor error logs for next 24 hours
2. Check performance metrics
3. Schedule follow-up check in 1 week

## Files Generated

- commands.md: All executed commands
- output/: Command outputs
- pre-status.json: Pre-deployment status
- post-status.json: Post-deployment status
- rollback/: Backup files
- summary.md: This summary
EOF
```

## Rollback Procedure (If Needed)

```bash
# If deployment fails, execute rollback

# Start session
ssh_session_start server="rock-5t" name="rollback-2026-02-07"

# Restore backup
ssh_session_send session="sess-xxx" command="cd /home/imax/app && rm -rf *"
ssh_session_send session="sess-xxx" command="cd /home/imax/app && tar -xzf ~/.ssh-workdir/rock-5t/2026-02-07-deployment/rollback/backup-20260207.tar.gz"

# Restart service
ssh_session_send session="sess-xxx" command="pm2 restart myapp"

# Verify
ssh_session_send session="sess-xxx" command="pm2 status"
ssh_session_send session="sess-xxx" command="curl -s http://localhost:3000/health"

# Close
ssh_session_close session="sess-xxx"
```

## Complete Workdir Structure

```
~/.ssh-workdir/
└── rock-5t/
    └── 2026-02-07-deployment/
        ├── commands.md              # All executed commands
        ├── summary.md               # Deployment summary
        ├── pre-status.json         # Pre-deployment status
        ├── post-status.json        # Post-deployment status
        ├── output/
        │   ├── git-fetch.txt
        │   ├── git-pull.txt
        │   ├── npm-ci.txt
        │   ├── npm-test.txt
        │   ├── npm-build.txt
        │   ├── pm2-stop.txt
        │   ├── pm2-delete.txt
        │   ├── pm2-start.txt
        │   ├── pm2-status.txt
        │   ├── pm2-info.txt
        │   ├── health-check.txt
        │   ├── health-response.txt
        │   └── pm2-logs.txt
        └── rollback/
            └── backup-20260207.tar.gz
```

## Key Takeaways

1. **Use named sessions** - Easy to identify in `ssh_session_list`
2. **Save all outputs** - Critical for debugging deployment issues
3. **Create backup before changes** - Enables quick rollback
4. **Verify at each step** - Catch issues early
5. **Document rollback procedure** - Needed if something goes wrong
6. **Write comprehensive summary** - Future reference for the team
