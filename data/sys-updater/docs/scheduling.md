# Scheduling

## Scheduling Options

### Option A (recommended here): OpenClaw cron

This repo is usually scheduled by OpenClaw cron jobs (timezone set to Europe/Moscow in the job):
- 06:00 MSK → `scripts/apt_maint.py run_6am`
- 09:00 MSK → `scripts/apt_maint.py report_9am`

Check:
```bash
openclaw cron list
openclaw cron runs --id <jobId>
```

### Option B: System crontab

Add to crontab (`crontab -e` as moltuser):

```cron
# sys-updater: daily maintenance at 06:00 MSK (03:00 UTC)
0 3 * * * /usr/bin/python3 /home/moltuser/clawd/sys-updater/scripts/apt_maint.py run_6am >> /home/moltuser/clawd/sys-updater/state/logs/cron.log 2>&1

# sys-updater: daily report at 09:00 MSK (06:00 UTC)
# Note: actual Telegram sending is handled by the caller (e.g., OpenClaw cron job)
0 6 * * * /usr/bin/python3 /home/moltuser/clawd/sys-updater/scripts/apt_maint.py report_9am >> /home/moltuser/clawd/sys-updater/state/logs/cron.log 2>&1
```

## Alternative: Systemd Timer

Create `/etc/systemd/system/sys-updater-6am.service`:

```ini
[Unit]
Description=sys-updater 6am maintenance
After=network-online.target

[Service]
Type=oneshot
User=moltuser
ExecStart=/usr/bin/python3 /home/moltuser/clawd/sys-updater/scripts/apt_maint.py run_6am
```

Create `/etc/systemd/system/sys-updater-6am.timer`:

```ini
[Unit]
Description=Run sys-updater daily at 06:00 UTC

[Timer]
OnCalendar=*-*-* 06:00:00 UTC
Persistent=true

[Install]
WantedBy=timers.target
```

Enable:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now sys-updater-6am.timer
```

## Manual Execution

```bash
# Test run_6am (requires sudo permissions)
python3 scripts/apt_maint.py run_6am

# Test report_9am (no sudo needed, reads state files)
python3 scripts/apt_maint.py report_9am
```
