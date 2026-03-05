# Operations

## Disable sys-updater

### Temporary (one day)

Comment out cron entries:

```bash
crontab -e
# Comment the lines with #
```

### Permanent

```bash
# Remove cron entries
crontab -e  # Delete sys-updater lines

# Or if using systemd
sudo systemctl disable --now sys-updater-6am.timer
```

## Rollback / Recovery

### If a security update broke something

1. Check what was updated:
   ```bash
   cat state/apt/last_run.json | jq '.updatedPackages'
   # Or check apt history
   cat /var/log/apt/history.log | tail -100
   ```

2. Downgrade specific package:
   ```bash
   # Find available versions
   apt-cache policy <package-name>

   # Install specific version
   sudo apt-get install <package-name>=<version>
   ```

3. Block the package from future updates:
   ```bash
   sudo apt-mark hold <package-name>
   ```

### If state files are corrupted

```bash
# Backup corrupted files
mv state/apt/last_run.json state/apt/last_run.json.bak
mv state/apt/tracked.json state/apt/tracked.json.bak

# Re-run to regenerate
python3 scripts/apt_maint.py run_6am
```

## Command-Line Options

```bash
# Dry-run mode: simulate without executing sudo commands
python3 scripts/apt_maint.py run_6am --dry-run
python3 scripts/apt_maint.py run_6am -n

# Verbose mode: also log to console (stderr)
python3 scripts/apt_maint.py run_6am --verbose
python3 scripts/apt_maint.py run_6am -v

# Combine both
python3 scripts/apt_maint.py run_6am -n -v
```

## Troubleshooting

### "Another instance is running"

A lock file prevents parallel `run_6am` executions:

```bash
# Check if another instance is running
cat state/apt/.run_6am.lock

# If stale (process doesn't exist), remove manually
rm state/apt/.run_6am.lock
```

### "No data" in report

The 06:00 run hasn't executed or failed. Check:

```bash
# Check logs
tail -50 state/logs/apt_maint.log

# Check if state file exists
ls -la state/apt/

# Manual run
python3 scripts/apt_maint.py run_6am
```

### Sudo password prompt

Sudoers not configured. See [sudoers.md](sudoers.md).

### unattended-upgrade fails

```bash
# Check unattended-upgrades status
sudo unattended-upgrade -d -v

# Check configuration
cat /etc/apt/apt.conf.d/50unattended-upgrades
```

### Package stuck in "tracked"

Edit `tracked.json` manually:

```bash
vim state/apt/tracked.json
# Set reviewedAt to current timestamp, or blocked: true
```

## Maintenance Commands

```bash
# View current state
cat state/apt/last_run.json | python3 -m json.tool
cat state/apt/tracked.json | python3 -m json.tool

# Count pending packages
cat state/apt/tracked.json | jq '.items | length'

# List blocked packages
cat state/apt/tracked.json | jq '.items | to_entries | map(select(.value.blocked)) | .[].key'

# Clear old tracking (reset)
rm state/apt/tracked.json
python3 scripts/apt_maint.py run_6am
```
