# Cron Scheduler

Manage scheduled tasks and automation on your system using cron.

**Category:** automation, productivity
**API Key Required:** No

## What It Does

Create, manage, and monitor scheduled tasks (cron jobs) on your machine. Automate backups, health checks, cleanup scripts, API calls, notifications — anything that should run on a schedule. Your agent handles the cron syntax so you don't have to.

## Agent Commands

### List all cron jobs
```bash
echo "=== User crontab ==="
crontab -l 2>/dev/null || echo "(empty)"
echo ""
echo "=== System cron ==="
ls /etc/cron.d/ 2>/dev/null
echo ""
echo "=== Cron directories ==="
echo "Hourly:  $(ls /etc/cron.hourly/ 2>/dev/null | wc -l) jobs"
echo "Daily:   $(ls /etc/cron.daily/ 2>/dev/null | wc -l) jobs"
echo "Weekly:  $(ls /etc/cron.weekly/ 2>/dev/null | wc -l) jobs"
echo "Monthly: $(ls /etc/cron.monthly/ 2>/dev/null | wc -l) jobs"
```

### Add a cron job
```bash
# Add to user crontab
(crontab -l 2>/dev/null; echo "SCHEDULE COMMAND") | crontab -

# Common schedules:
# Every minute:        * * * * *
# Every 5 minutes:     */5 * * * *
# Every hour:          0 * * * *
# Every day at 2am:    0 2 * * *
# Every Monday 9am:    0 9 * * 1
# Every 1st of month:  0 0 1 * *
# Weekdays at 8am:     0 8 * * 1-5
```

### Remove a cron job
```bash
# Edit crontab interactively
crontab -e

# Or remove a specific line
crontab -l | grep -v "PATTERN_TO_REMOVE" | crontab -
```

### Check cron logs
```bash
# Recent cron activity
grep CRON /var/log/syslog | tail -20

# Or on systems using journald
journalctl -u cron --since "1 hour ago" --no-pager | tail -20
```

### Test a cron command
```bash
# Run the command manually first to make sure it works
COMMAND_HERE

# Check it produces expected output
echo "Exit code: $?"
```

### Cron syntax reference
```
┌───────────── minute (0-59)
│ ┌───────────── hour (0-23)
│ │ ┌───────────── day of month (1-31)
│ │ │ ┌───────────── month (1-12)
│ │ │ │ ┌───────────── day of week (0-7, 0 and 7 = Sunday)
│ │ │ │ │
* * * * * command
```

### Common patterns

```bash
# Disk space alert daily at 8am
0 8 * * * df -h / | awk 'NR==2 && $5+0 > 80 {print "Disk alert: " $5 " used"}' | mail -s "Disk Warning" you@email.com

# Clean /tmp weekly
0 3 * * 0 find /tmp -type f -mtime +7 -delete

# Backup database nightly
0 2 * * * pg_dump mydb > /backups/db_$(date +\%Y\%m\%d).sql

# Restart a service if it crashes (every 5 min check)
*/5 * * * * systemctl is-active myservice || systemctl restart myservice

# Log system stats every 15 minutes
*/15 * * * * echo "$(date): $(uptime)" >> /var/log/system-stats.log
```

### Environment variables in cron
```bash
# Cron runs with minimal environment. Set what you need:
(crontab -l 2>/dev/null; echo "PATH=/usr/local/bin:/usr/bin:/bin
SHELL=/bin/bash
0 2 * * * /home/user/backup.sh >> /var/log/backup.log 2>&1") | crontab -
```

### Redirect output (important!)
```bash
# Log output
* * * * * command >> /var/log/myjob.log 2>&1

# Discard output
* * * * * command > /dev/null 2>&1

# Email output (if mail is configured)
MAILTO=you@email.com
0 8 * * * command
```

## Examples

**User:** "Run my backup script every night at 2am"
→ `(crontab -l 2>/dev/null; echo "0 2 * * * /home/user/backup.sh >> /var/log/backup.log 2>&1") | crontab -`

**User:** "Check disk space every hour and alert me if it's over 80%"
→ Create a check script + cron job

**User:** "What scheduled tasks are running?"
→ List all crontabs and system cron directories

**User:** "Stop the daily cleanup job"
→ Find and remove the specific cron entry

## Constraints

- Cron runs with minimal PATH — use absolute paths for commands
- Always redirect output (>> logfile 2>&1) or cron fills up mail spool
- Cron uses the system timezone — check with `timedatectl`
- Minimum resolution is 1 minute — for sub-minute, use a loop in a script
- User crontabs don't survive user deletion
- Test commands manually before scheduling
