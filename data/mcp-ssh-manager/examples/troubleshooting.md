# Troubleshooting Workflow Example

This example demonstrates a complete troubleshooting workflow using MCP ssh-manager with workdir organization and session management.

## Scenario

Investigate and resolve an issue where the nginx service on rock-5t is returning 502 Bad Gateway errors.

## Initial Investigation

### Step 1: Create Workdir

```bash
# Create troubleshooting workdir
mkdir -p ~/.ssh-workdir/rock-5t/2026-02-07-nginx-502/output
mkdir -p ~/.ssh-workdir/rock-5t/2026-02-07-nginx-502/config

# Create tracking files
cat > ~/.ssh-workdir/rock-5t/2026-02-07-nginx-502/commands.md << 'EOF'
# Nginx 502 Troubleshooting Commands - 2026-02-07

## Initial Checks
1. Check nginx status
2. Check nginx error logs
3. Check PHP-FPM status
4. Check PHP-FPM logs

## Service Configuration
5. Check nginx config
6. Check PHP-FPM pool config

## Network Checks
7. Check if ports are listening
8. Test localhost connection

## Process Analysis
9. Check running processes
10. Check resource usage
EOF
```

### Step 2: Start Troubleshooting Session

```bash
ssh_session_start server="rock-5t" name="nginx-502-troubleshoot"
```

## Investigation Process

### Step 3: Check Nginx Status

```bash
# Check if nginx is running
ssh_session_send session="sess-xxx" command="systemctl status nginx" > ~/.ssh-workdir/rock-5t/2026-02-07-nginx-502/output/nginx-status.txt 2>&1

# Check nginx error log
ssh_session_send session="sess-xxx" command="tail -50 /var/log/nginx/error.log" > ~/.ssh-workdir/rock-5t/2026-02-07-nginx-502/output/nginx-error.txt
```

### Step 4: Check PHP-FPM

```bash
# Check PHP-FPM status
ssh_session_send session="sess-xxx" command="systemctl status php8.2-fpm" > ~/.ssh-workdir/rock-5t/2026-02-07-nginx-502/output/php-fpm-status.txt 2>&1

# Check PHP-FPM error log
ssh_session_send session="sess-xxx" command="tail -50 /var/log/php8.2-fpm.log" > ~/.ssh-workdir/rock-5t/2026-02-07-nginx-502/output/php-fpm-error.txt

# Check PHP-FPM socket
ssh_session_send session="sess-xxx" command="ls -la /run/php/php8.2-fpm.sock" > ~/.ssh-workdir/rock-5t/2026-02-07-nginx-502/output/php-socket.txt
```

### Step 5: Check Listening Ports

```bash
# Check what's listening on ports 80 and 443
ssh_session_send session="sess-xxx" command="ss -tulpn | grep -E ':80|:443'" > ~/.ssh-workdir/rock-5t/2026-02-07-nginx-502/output/ports.txt

# Check nginx worker processes
ssh_session_send session="sess-xxx" command="ps aux | grep nginx" > ~/.ssh-workdir/rock-5t/2026-02-07-nginx-502/output/nginx-processes.txt
```

### Step 6: Test Localhost Connection

```bash
# Test nginx response locally
ssh_session_send session="sess-xxx" command="curl -s -o /dev/null -w '%{http_code}' http://localhost" > ~/.ssh-workdir/rock-5t/2026-02-07-nginx-502/output/curl-localhost.txt

# Test PHP-FPM socket directly
ssh_session_send session="sess-xxx" command="curl -s -o /dev/null -w '%{http_code}' http://localhost/status" > ~/.ssh-workdir/rock-5t/2026-02-07-nginx-502/output/curl-status.txt
```

## Root Cause Analysis

### Step 7: Examine Configuration

```bash
# Save nginx configuration
ssh_session_send session="sess-xxx" command="cat /etc/nginx/sites-available/default" > ~/.ssh-workdir/rock-5t/2026-02-07-nginx-502/config/nginx-site.txt

# Save PHP-FPM pool configuration
ssh_session_send session="sess-xxx" command="cat /etc/php/8.2/fpm/pool.d/www.conf | grep -E 'listen|user|group|socket'" > ~/.ssh-workdir/rock-5t/2026-02-07-nginx-502/config/php-fpm-pool.txt
```

### Step 8: Check Resource Usage

```bash
# Check disk space
ssh_session_send session="sess-xxx" command="df -h" > ~/.ssh-workdir/rock-5t/2026-02-07-nginx-502/output/disk.txt

# Check memory
ssh_session_send session="sess-xxx" command="free -h" > ~/.ssh-workdir/rock-5t/2026-02-07-nginx-502/output/memory.txt

# Check for OOM kills
ssh_session_send session="sess-xxx" command="dmesg | grep -i 'killed process'" | tail -20 > ~/.ssh-workdir/rock-5t/2026-02-07-nginx-502/output/oom.txt
```

## Identify the Issue

Based on investigation, the issue is:

```
PHP-FPM socket permissions are wrong:
- Socket exists but nginx can't access it
- Error: "Permission denied while connecting to upstream"
```

### Evidence from logs:

```bash
# Nginx error (from nginx-error.txt):
2026/02/07 10:15:01 [crit] 1234#1234: *5678 connect() to unix:/run/php/php8.2-fpm.sock failed (13: Permission denied) while connecting to upstream
```

## Resolution

### Step 9: Fix the Issue

```bash
# Check socket permissions
ssh_session_send session="sess-xxx" command="ls -la /run/php/php8.2-fpm.sock"
```

Response shows socket is owned by root:root with 0660 permissions.

```bash
# Fix socket ownership
ssh_session_send session="sess-xxx" command="sudo chown www-data:www-data /run/php/php8.2-fpm.sock"
ssh_session_send session="sess-xxx" command="sudo chmod 666 /run/php/php8.2-fpm.sock"

# Restart services
ssh_session_send session="sess-xxx" command="sudo systemctl restart php8.2-fpm"
ssh_session_send session="sess-xxx" command="sudo systemctl restart nginx"

# Verify both are running
ssh_session_send session="sess-xxx" command="systemctl status php8.2-fpm | grep Active"
ssh_session_send session="sess-xxx" command="systemctl status nginx | grep Active"
```

### Step 10: Verify Fix

```bash
# Test from local
ssh_session_send session="sess-xxx" command="curl -s -o /dev/null -w '%{http_code}' http://localhost" > ~/.ssh-workdir/rock-5t/2026-02-07-nginx-502/output/verify-fix.txt

# Should return 200
```

## Documentation

### Step 11: Write Summary

```bash
cat > ~/.ssh-workdir/rock-5t/2026-02-07-nginx-502/summary.md << 'EOF'
# Nginx 502 Troubleshooting Summary - 2026-02-07

## Issue
- **Symptom**: nginx returning 502 Bad Gateway
- **Started**: 2026-02-07 10:00 UTC
- **Environment**: rock-5t, nginx + PHP-FPM 8.2

## Investigation

### Commands Executed
1. `systemctl status nginx` - nginx active but not handling requests
2. `tail -50 /var/log/nginx/error.log` - Found permission denied errors
3. `systemctl status php8.2-fpm` - PHP-FPM running
4. `ls -la /run/php/php8.2-fpm.sock` - Socket exists with wrong permissions

### Logs Examined
- /var/log/nginx/error.log
- /var/log/php8.2-fpm.log

### Configs Examined
- /etc/nginx/sites-available/default
- /etc/php/8.2/fpm/pool.d/www.conf

## Root Cause

**PHP-FPM socket permissions**

The PHP-FPM socket `/run/php/php8.2-fpm.sock` was owned by `root:root` with `0660` permissions, preventing nginx (running as `www-data`) from connecting.

## Resolution

### Fix Applied
```bash
sudo chown www-data:www-data /run/php/php8.2-fpm.sock
sudo chmod 666 /run/php/php8.2-fpm.sock
sudo systemctl restart php8.2-fpm
sudo systemctl restart nginx
```

### Verification
- nginx returns HTTP 200
- No more permission denied errors
- PHP-FPM responding on socket

## Prevention

### Permanent Fix
Update PHP-FPM pool config `/etc/php/8.2/fpm/pool.d/www.conf`:
```
listen.owner = www-data
listen.group = www-data
listen.mode = 0660
```

Then restart: `sudo systemctl restart php8.2-fpm`

## Files Generated

### Commands Log
- commands.md: All troubleshooting commands

### Outputs
- nginx-status.txt: Nginx service status
- nginx-error.txt: Nginx error log
- php-fpm-status.txt: PHP-FPM status
- php-fpm-error.txt: PHP-FPM error log
- php-socket.txt: Socket permissions
- ports.txt: Listening ports
- curl-localhost.txt: Local connection test
- curl-status.txt: Status endpoint test
- disk.txt: Disk space check
- memory.txt: Memory usage
- oom.txt: OOM kill log
- verify-fix.txt: Post-fix verification

### Configs
- nginx-site.txt: Nginx site configuration
- php-fpm-pool.txt: PHP-FPM pool configuration

## Lessons Learned

1. **Always check socket permissions** - nginx and PHP-FPM need compatible ownership
2. **Check logs first** - Error messages usually point to the issue
3. **Document configuration** - Keep copies of working configs
4. **Permanent fix** - Don't just fix symptoms, fix the root cause in config

## Next Steps

1. ✅ Apply permanent fix to PHP-FPM pool config
2. ✅ Monitor for 24 hours
3. Schedule follow-up check: 2026-02-08
EOF
```

### Step 12: Close Session

```bash
ssh_session_close session="sess-xxx"
```

## Permanent Fix (Apply to Config)

```bash
# Apply permanent fix to prevent recurrence

# Edit PHP-FPM pool config
ssh_execute server="rock-5t" command="cat /etc/php/8.2/fpm/pool.d/www.conf | grep -E '^listen|^listen.owner|^listen.group|^listen.mode'"

# Expected output shows missing/broken settings

# Update config
ssh_execute server="rock-5t" command="sudo sed -i 's/^listen = \/run\/php\/php8.2-fpm.sock/listen = \/run\/php\/php8.2-fpm.sock\nlisten.owner = www-data\nlisten.group = www-data\nlisten.mode = 0660/' /etc/php/8.2/fpm/pool.d/www.conf"

# Restart PHP-FPM
ssh_execute server="rock-5t" command="sudo systemctl restart php8.2-fpm"

# Verify
ssh_execute server="rock-5t" command="cat /etc/php/8.2/fpm/pool.d/www.conf | grep -E 'listen\.(owner|group|mode)'"
```

## Complete Workdir Structure

```
~/.ssh-workdir/
└── rock-5t/
    └── 2026-02-07-nginx-502/
        ├── commands.md           # Executed commands
        ├── summary.md           # Troubleshooting summary
        ├── output/
        │   ├── nginx-status.txt
        │   ├── nginx-error.txt
        │   ├── php-fpm-status.txt
        │   ├── php-fpm-error.txt
        │   ├── php-socket.txt
        │   ├── ports.txt
        │   ├── curl-localhost.txt
        │   ├── curl-status.txt
        │   ├── disk.txt
        │   ├── memory.txt
        │   ├── oom.txt
        │   └── verify-fix.txt
        └── config/
            ├── nginx-site.txt
            └── php-fpm-pool.txt
```

## Key Takeaways

1. **Create workdir first** - Organize all investigation data
2. **Save all outputs** - Logs, configs, test results
3. **Use session** - Maintain context during investigation
4. **Check logs first** - Error messages point to root cause
5. **Document findings** - Summary helps future troubleshooting
6. **Apply permanent fix** - Don't just fix symptoms
7. **Schedule follow-up** - Verify fix over time
