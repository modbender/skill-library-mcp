---
name: mac-cleaner
description: Analyze and safely clean disk space on macOS. Use when the user asks about Mac storage, "System Data" taking too much space, disk cleanup, freeing up space, or managing storage on macOS. Covers caches, iOS simulators, Xcode data, trash, logs, and browser caches. Safe for everyday Mac users.
---

# Mac Cleaner

Safely analyze and reclaim disk space on macOS. Designed for everyday Mac users — no technical knowledge required.

## When to use

- "My Mac says System Data is taking too much space"
- "How do I free up disk space?"
- "Why is my disk full?"
- "Clean up my Mac storage"
- "What's taking up space on my Mac?"

## What this skill covers

| Category | Safe to Clean | Notes |
|----------|---------------|-------|
| User Caches | ✅ Yes | App temporary files |
| iOS Simulators | ✅ Yes | Unused simulator devices |
| Xcode Derived Data | ✅ Yes | Build artifacts (rebuildable) |
| Browser Caches | ✅ Yes | Chrome, Safari, Firefox |
| System Logs | ✅ Old only | 7+ days old, requires sudo |
| Trash | ✅ Yes | Empty trash |
| iOS Backups | ⚠️ Review | Check if backups are needed |
| Parallels VMs | ⚠️ Review | Only if Windows not needed |
| Time Machine Snapshots | ⚠️ Review | Can delete old snapshots |

## NEVER delete

- `/System` folder contents
- `/Library/Extensions` or kernel extensions
- `/private/var/db` (system databases)
- Active iOS backups you need
- Parallels VMs you use

## Quick start

### Analyze (safe, read-only)

```bash
bash scripts/mac-cleanup.sh analyze
```

Shows disk usage and identifies large items without making changes.

### Clean (with confirmation)

```bash
bash scripts/mac-cleanup.sh clean
```

Performs safe cleanup after user confirmation.

## What gets cleaned

1. **User Caches** (`~/Library/Caches/*`)
   - App temporary files, thumbnails, downloaded content
   - Safe: apps rebuild these automatically

2. **Xcode Derived Data** (`~/Library/Developer/Xcode/DerivedData/*`)
   - Build artifacts and intermediate files
   - Safe: rebuilds on next compile

3. **iOS Simulators** (unavailable devices only)
   - Old iOS simulator images
   - Safe: easily re-downloaded via Xcode

4. **Browser Caches**
   - Chrome, Safari, Firefox cache files
   - Safe: websites reload, login sessions preserved

5. **Old System Logs** (7+ days)
   - Requires sudo password
   - Preserves recent logs for debugging

6. **Trash**
   - Empties `.Trash` folder
   - Safe: user already chose to delete these

## Manual cleanup for large items

If the script identifies large items you want to handle manually:

### iOS Device Backbacks (~/Library/Application Support/MobileSync/Backup)

```bash
# List backups
ls -lah ~/Library/Application\ Support/MobileSync/Backup/

# Delete specific backup (use folder name from above)
rm -rf ~/Library/Application\ Support/MobileSync/Backup/[FOLDER_NAME]
```

Or use **Finder → Locations → [Your iPhone] → Manage Backups**

### Time Machine Local Snapshots

```bash
# List snapshots
tmutil listlocalsnapshots /

# Delete all local snapshots
sudo tmutil deletelocalsnapshots /

# Or delete specific date
sudo tmutil deletelocalsnapshots 2024-01-15-123456
```

### Parallels VMs

Open **Parallels Desktop**:
- Right-click VM → **Reclaim Disk Space** (safest)
- Or **Delete** if you don't need Windows

### WeChat / Large Apps

Clear from within the app:
- WeChat: Settings → General → Storage → Manage
- Telegram: Settings → Data and Storage → Storage Usage
- Slack: Help → Troubleshooting → Clear Cache

## Large folders to review manually

| Path | What it is | Safe to delete? |
|------|-----------|-----------------|
| `~/Downloads` | Downloaded files | Review first |
| `~/Movies` | Videos | Review first |
| `~/Parallels` | Windows VMs | Only if not using |
| `~/Library/Containers/com.tencent.xinWeChat` | WeChat data | Clear from WeChat app |
| `~/Library/Application Support` | App data | Review per app |

## Expected results

Typical cleanup results for an everyday Mac user:

- **Light user**: 2-5 GB freed
- **Developer**: 20-50 GB freed (Xcode, simulators)
- **Heavy messaging apps**: 50-100 GB freed (WeChat, Telegram)
- **With VMs**: 50-200 GB freed (if deleting Parallels)

## Troubleshooting

### "Operation not permitted" errors

Grant Terminal Full Disk Access:
1. System Settings → Privacy & Security → Full Disk Access
2. Add Terminal (or iTerm)
3. Restart terminal

### Cleanup didn't free much space

Run the analyze mode again:
```bash
bash scripts/mac-cleanup.sh analyze
```

Look for:
- iOS device backups (often 50-200GB)
- Parallels VMs (20-100GB each)
- WeChat/Telegram data (can be 100GB+)
- Time Machine snapshots (can accumulate)

These require manual review before deletion.

## References

- Apple's storage documentation: https://support.apple.com/guide/mac-help/check-storage-space-mchlc03eb677/mac
- Safe macOS cleanup practices: https://support.apple.com/en-us/HT202083
