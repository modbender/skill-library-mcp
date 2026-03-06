# Troubleshooting

## Common Issues

### File watcher not found

**Problem:** `⚠ No file watcher found. Auto-push disabled.`

**Linux:**
```bash
sudo apt-get install inotify-tools
```

**macOS:**
```bash
brew install fswatch
```

After installation, restart the daemon:
```bash
sync-daemon.sh restart
```

### Git authentication failed

**Problem:** `git push` asks for password or fails with auth error

**Solution:**
1. Use SSH key auth:
   ```bash
   git remote set-url origin git@github.com:USER/REPO.git
   ```
2. Ensure SSH key is added:
   ```bash
   ssh-add -l
   ```
3. Test connection:
   ```bash
   ssh -T git@github.com
   ```

### "No remote branch found" on pull

**Problem:** `No remote branch found. Nothing to pull.`

**Cause:** Fresh repo with no commits, or origin/HEAD not set

**Solution:**
1. Push first commit from another device
2. Or set HEAD manually:
   ```bash
   cd ~/openclaw-sync
   git remote set-head origin --auto
   ```

### Conflict loop

**Problem:** Keep getting conflicts after resolving

**Cause:** Both devices modifying same file simultaneously

**Solution:**
- Use device-prefixed memory files (auto-created)
- Avoid editing shared files (USER.md, SOUL.md) on multiple devices at once
- Increase sync frequency if needed (edit `sync_interval_minutes` in config)

### Large repo / slow sync

**Problem:** Sync takes too long

**Check:**
```bash
cd ~/openclaw-sync
du -sh .
git count-objects -vH
```

**Solution:**
- Add large files to `.gitignore`
- Clean old commits:
  ```bash
  git gc --aggressive
  ```

### Daemon stops unexpectedly

**Check logs:**
```bash
tail -f ~/.openclaw/sync-daemon.log
```

**Common causes:**
- Repo deleted or moved
- Git credentials expired
- Disk full
- Network issues

### Device name collision

**Problem:** Two devices using same name

**Solution:**
```bash
# Edit config
nano ~/.config/openclaw/sync-config.yaml
# Change device_name

# Re-initialize (will not overwrite existing files)
sync-init --device-name NEWNAME
```

### Symlinks broken

**Problem:** Files in workspace show as broken symlinks

**Cause:** Sync repo was deleted or moved

**Solution:**
1. Stop daemon: `sync-daemon.sh stop`
2. Clone repo again: `git clone git@github.com:USER/REPO.git ~/openclaw-sync`
3. Re-run init: `sync-init --device-name <name>`

### Push fails with "behind remote"

**Problem:** `⚠ Push failed, remote has changes`

**Cause:** Remote has commits you don't have locally

**Solution:**
The script should auto-pull and retry. If it fails:
```bash
cd ~/openclaw-sync
git pull --rebase origin main
git push origin main
```

### Nested git repository warning

**Problem:** `warning: adding embedded git repository`

**Cause:** A skills subdirectory contains its own `.git` folder

**Solution:**
```bash
cd ~/openclaw-sync
# Remove nested .git
rm -rf skills/some-skill/.git
# Commit the fix
git add -A && git commit -m "fix: remove nested git repo"
```

### Interactive installer issues

**Problem:** Installer doesn't prompt for input

**Cause:** Script running in non-interactive mode (piped input)

**Solution:**
Use environment variables instead:
```bash
curl -fsSL https://raw.githubusercontent.com/RegulusZ/multi-device-sync-github/main/install.sh | \
  REPO_URL="git@github.com:USER/openclaw_sync.git" \
  DEVICE_NAME="mydevice" \
  SYNC_MODE="first" \
  bash
```

## Debug Mode

Enable verbose logging:
```bash
export SYNC_DEBUG=1
sync-daemon.sh restart
tail -f ~/.openclaw/sync-daemon.log
```

## Manual Recovery

If everything breaks:

```bash
# 1. Stop daemon
sync-daemon.sh stop

# 2. Backup local changes
cp -r ~/openclaw-sync ~/openclaw-sync-backup-$(date +%s)

# 3. Reset to remote
cd ~/openclaw-sync
git fetch origin
git reset --hard origin/main

# 4. Re-apply local changes manually
# (from backup)

# 5. Restart
sync-daemon.sh start
```

## Check Status

Quick health check:
```bash
sync-status
```

This shows:
- Daemon status (pull + push watcher)
- Git status
- Remote connection
- Recent commits
- Conflict state

## Logs

Log file location:
```
~/.openclaw/sync-daemon.log
```

View recent activity:
```bash
tail -50 ~/.openclaw/sync-daemon.log
```
