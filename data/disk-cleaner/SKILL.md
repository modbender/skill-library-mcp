---
name: disk-cleaner
description: Analyze disk usage, find large/old files, and suggest safe cleanup actions.
---


# Disk Cleaner

Analyze disk usage and identify cleanup opportunities.

## Instructions

1. **Filesystem overview**:
   ```bash
   df -h --output=source,size,used,avail,pcent,target | grep -v tmpfs
   ```

2. **Directory analysis** (top space consumers):
   ```bash
   du -sh /path/* 2>/dev/null | sort -rh | head -20
   ```

3. **Find large files**:
   ```bash
   find /path -type f -size +100M -exec ls -lh {} \; 2>/dev/null | sort -k5 -rh | head -20
   ```

4. **Find old files** (not modified in 90+ days):
   ```bash
   find /path -type f -mtime +90 -size +10M -exec ls -lh {} \; 2>/dev/null | sort -k5 -rh
   ```

5. **Common cleanup targets**:
   ```bash
   # Package caches
   du -sh ~/.cache/pip ~/.npm/_cacache ~/.cache/yarn 2>/dev/null
   # Docker
   docker system df 2>/dev/null
   # Logs
   du -sh /var/log/* 2>/dev/null | sort -rh | head -10
   # Trash
   du -sh ~/.local/share/Trash 2>/dev/null
   # Temp
   du -sh /tmp 2>/dev/null
   ```

6. **Report format**:
   ```
   💾 Disk Report — /home (85% used, 12GB free)

   ## Top Space Users
   | Path | Size | Last Modified |
   |------|------|---------------|
   | ~/Downloads | 8.2 GB | various |
   | ~/.cache | 3.1 GB | today |

   ## Cleanup Suggestions
   | Action | Saves | Command | Risk |
   |--------|-------|---------|------|
   | Clear npm cache | ~1.2 GB | npm cache clean --force | 🟢 Safe |
   | Docker prune | ~4.5 GB | docker system prune -a | 🟡 Review |
   | Old logs | ~800 MB | find /var/log -mtime +30 -delete | 🟡 Review |
   ```

## Security

- **Never auto-delete** — always show commands and let user confirm
- Use `trash` over `rm` when available (recoverable)
- Skip `/proc`, `/sys`, `/dev` in scans
- Don't scan directories outside user's permission

## Edge Cases

- **Permission denied**: Use `2>/dev/null` to suppress; note inaccessible dirs
- **Symlinks**: Use `-not -type l` to avoid counting symlinked data twice
- **Mounted drives**: Identify mount points; don't accidentally clean external storage

## Requirements

- Standard Unix tools: `du`, `df`, `find`, `sort`
- No API keys needed
