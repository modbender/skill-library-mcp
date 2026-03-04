# Deployment & Operations Guide

This guide covers running Curated Search in production-like environments: setup as a service, monitoring, backups, updates, and maintenance.

---

## 1. Installation Scenarios

### 1.1 Manual / Development

Already covered in `README.md`. Clone/copy skill, `npm install`, configure, `npm run crawl`.

### 1.2 System-wide (ClawHub)

Future: `openclaw skill install curated-search` will automate this.

---

## 2. Running the Crawler Periodically

The index needs to be refreshed periodically to capture updates. You can run the crawler:

- **Manually**: `npm run crawl`
- **Via cron**: Simple and effective
- **Via systemd timer**: Better logging, restart on failure

### 2.1 Cron Job (Simple)

```bash
# crontab -e (for user 'q')
0 2 * * 0 cd /home/q/.openclaw/workspace/skills/curated-search && /usr/bin/npm run crawl >> /var/log/curated-search/crawl.log 2>&1
```

Runs weekly at 2 AM Sunday. Adjust as needed.

### 2.2 systemd Timer (Recommended)

Provides structured logging, restart on failure, and status monitoring.

**Service file** (`systemd/curated-search-crawler.service`):

```ini
[Unit]
Description=Curated Search Crawler
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
User=q
WorkingDirectory=/home/q/.openclaw/workspace/skills/curated-search
ExecStart=/usr/bin/npm run crawl
# Standard output goes to journal
StandardOutput=journal
StandardError=journal
# Resource limits (optional)
MemoryLimit=500M
CPUQuota=50%
# On failure, don't retry immediately (timer controls next run)
```

**Timer file** (`systemd/curated-search-crawler.timer`):

```ini
[Unit]
Description=Weekly crawl of Curated Search index
Requires=curated-search-crawler.service

[Timer]
# Run weekly on Sunday at 2:00 AM
OnCalendar=weekly
Persistent=true
# Also run 5 minutes after boot if missed
OnBootSec=5min

[Install]
WantedBy=timers.target
```

**Install**:

```bash
# Copy to systemd directory (as root)
sudo cp systemd/curated-search-crawler.service systemd/curated-search-crawler.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now curated-search-crawler.timer
```

**Check status**:

```bash
systemctl status curated-search-crawler.timer
systemctl list-timers | grep curated
journalctl -u curated-search-crawler.service -f
```

---

## 3. OpenClaw Integration Persistence

OpenClaw loads the skill at startup. No separate daemon is needed for search queries.

**Ensure**:
- Skill directory is in OpenClaw's skill search path (workspace or global)
- `skill.yaml` is valid
- OpenClaw has been restarted after adding/changing skill

**Verification**:
```bash
openclaw tools list | grep curated-search
```

---

## 4. Logging

- **Crawler** (when run via systemd or cron): logs go to journal or file (redirection)
- **Search tool**: verbose logs go to stderr; OpenClaw captures these in its own logs
- **Application logs**: See `logs/curated-search.log` if configured (see `config.yaml`)

**Log rotation**: If writing to file, set up logrotate:

`/etc/logrotate.d/curated-search`:
```
/home/q/.openclaw/workspace/skills/curated-search/logs/*.log {
  daily
  rotate 7
  compress
  missingok
  notifempty
  create 640 q q
  sharedscripts
  postrotate
    systemctl reload openclaw > /dev/null 2>&1 || true
  endscript
}
```

---

## 5. Backup & Recovery

### 5.1 What to Back Up

- `config.yaml` — your domain whitelist and settings
- `data/index.json` and `data/index-docs.json` — the search index
- `data/crawl-state.json` — crawler resume state (optional)
- `logs/` — for historical analysis (optional)

Do **not** back up `node_modules/` (reinstall with `npm ci`).

### 5.2 Backup Command

```bash
tar -czf /backup/curated-search-$(date +%Y%m%d).tar.gz \
  --exclude=node_modules \
  --exclude=data/tmp \
  /home/q/.openclaw/workspace/skills/curated-search/
```

Store backups off-disk or remote.

### 5.3 Recovery Steps

1. Stop OpenClaw (optional)
2. Restore tarball: `tar -xzf backup.tar.gz -C /home/q/.openclaw/workspace/skills/`
3. Reinstall dependencies: `npm ci`
4. Restart OpenClaw if stopped
5. Test search: `openclaw tool curated-search.search --query="test"`

If index is corrupted:
```bash
rm data/index.json data/index-docs.json
npm run crawl
```

---

## 6. Health Monitoring

### 6.1 Manual Health Check

Run the search tool with a known query:

```bash
node scripts/search.js --query="test" --limit=1
```

Exit 0 and JSON output means healthy.

### 6.2 Automated Health Check Script

`scripts/health-check.js`:

```javascript
#!/usr/bin/env node
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const skillDir = path.resolve(__dirname, '..');

function fail(msg) {
  console.error('FAIL:', msg);
  process.exit(1);
}

// 1. Check index exists
const indexPath = path.join(skillDir, 'data', 'index.json');
if (!fs.existsSync(indexPath)) fail('Index missing');

// 2. Quick query test
try {
  const out = execSync('node scripts/search.js --query="test" --limit=1', {
    cwd: skillDir,
    encoding: 'utf8'
  });
  const res = JSON.parse(out);
  if (!Array.isArray(res)) fail('Invalid response format');
  console.log('OK: Index healthy');
} catch (e) {
  fail('Search failed: ' + e.message);
}
```

Make it executable: `chmod +x scripts/health-check.js`

**Cron check** (every hour):
```
0 * * * * /home/q/.openclaw/workspace/skills/curated-search/scripts/health-check.js || echo "ALERT: CuratedSearch down" | mail -s "CuratedSearch Alert" you@example.com
```

---

## 7. Updates & Versioning

### 7.1 Skill Versioning

Follow semantic versioning in `skill.yaml`. Update version on breaking changes.

### 7.2 Updating From Git

```bash
cd /home/q/.openclaw/workspace/skills/curated-search
git pull origin main
npm ci                    # install new dependencies
# If config schema changed, merge config.yaml carefully
openclaw gateway restart
```

### 7.3 Rollback

```bash
git checkout v1.0.0
npm ci
openclaw gateway restart
```

Or restore from backup.

---

## 8. Performance Tuning

| Symptom | Likely Cause | Adjustment |
|---------|--------------|------------|
| Slow search | Cold index (first query) | Acceptable; subsequent fast |
| Slow search (persistent) | Index too large for memory | Reduce `max_documents` or upgrade RAM |
| Crawl takes days | Low `delay` + many domains | Increase `delay` to avoid blocking, or accept long crawl |
| No results | Whitelist too narrow, depth too low | Add domains to `domains`, increase `depth` |
| Blocked by sites | `delay` too aggressive | Increase `delay` (e.g., 2000ms) |

---

## 9. Security & Permissions

- Skill directory readable by OpenClaw user
- `config.yaml` may contain domain lists (no secrets)
- Crawler respects robots.txt; does not hammer servers
- No external network calls from search tool (pure local file read)

Recommended permissions:
```bash
chmod 750 ~/.openclaw/workspace/skills/curated-search
chmod 640 config.yaml
chmod 600 data/*.json  # optional
```

---

## 10. Disaster Scenarios

| Scenario | Recovery |
|----------|----------|
| Disk failure | Restore from backup (config + index) |
| Index corrupted | Delete `data/index*.json` and re-run `npm run crawl` |
| OpenClaw config lost | Re-link skill dir, restart OpenClaw |
| Node upgrade breaks | Use nvm to pin Node version; test upgrades in staging first |

---

## 11. Monitoring Metrics

Track these (manually or via script):

- **Index size** (`du -h data/index.json`)
- **Crawl duration** (log timestamp)
- **Documents indexed** (from stats in crawl log)
- **Search latency** (measure with `time node scripts/search.js --query=test`)
- **Disk free** (`df -h` on data partition)

---

## 12. Maintenance Schedule

- **Daily**: Nothing (unless crawler running continuously)
- **Weekly** (after timer crawl): Check cron/systemd logs for errors; verify disk space
- **Monthly**: Review domain whitelist (remove dead domains, add new ones); check index growth; test backup restore
- **Quarterly**: Full re-crawl (delete index first) to clear accumulated artifacts; update dependencies (`npm update` then test)

---

## 13. Additional Resources

- `README.md` — main user guide
- `SKILL.md` — agent reference
- `PLAN.md` — original build plan
- `specs/` — detailed technical specs (Phases 1–8)

---

**End of Deployment Guide**
