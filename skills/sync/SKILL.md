---
name: Sync
description: Synchronize files and directories between local, remote, and cloud storage reliably.
metadata: {"clawdbot":{"emoji":"🔄","requires":{"anyBins":["rsync","rclone"]},"os":["linux","darwin","win32"]}}
---

# File Synchronization Rules

## rsync Fundamentals
- Trailing slash matters: `rsync src/` copies contents, `rsync src` copies the folder itself — this is the #1 cause of wrong directory structures
- Always use `-avz` baseline: archive mode preserves permissions/timestamps, verbose shows progress, compress speeds transfers
- Add `--delete` only when you want destination to mirror source exactly — without it, deleted source files remain on destination
- Use `--dry-run` before any destructive sync — shows what would change without modifying anything

## Exclusions
- Create an exclude file instead of multiple `--exclude` flags: `rsync -avz --exclude-from=.syncignore src/ dest/`
- Standard excludes for code projects: `.git/`, `node_modules/`, `__pycache__/`, `.venv/`, `*.pyc`, `.DS_Store`, `Thumbs.db`
- Exclude patterns are relative to source root — `/logs/` excludes only top-level logs, `logs/` excludes logs/ anywhere

## Cloud Storage (rclone)
- `rclone sync` deletes destination files not in source; `rclone copy` only adds — use copy when unsure
- Configure remotes interactively: `rclone config` — never hardcode cloud credentials in scripts
- Test with `--dry-run` first, then `--progress` for visual feedback during actual sync
- For S3-compatible storage, set `--s3-chunk-size 64M` for large files to avoid timeouts

## Verification
- After critical syncs, verify with checksums: `rsync -avzc` uses checksums instead of size/time (slower but certain)
- For rclone, use `rclone check source: dest:` to compare without transferring
- Log sync operations to file for audit: `rsync -avz src/ dest/ | tee sync.log`

## Bidirectional Sync
- rsync is one-way only — for true bidirectional sync, use unison: `unison dir1 dir2`
- Unison detects conflicts when both sides change — resolve manually or set prefer rules
- Cloud services like Dropbox/Syncthing handle bidirectional automatically — don't reinvent with rsync

## Remote Sync
- For SSH remotes, use key-based auth: `rsync -avz -e "ssh -i ~/.ssh/key" src/ user@host:dest/`
- Specify non-standard SSH port: `-e "ssh -p 2222"`
- Use `--partial --progress` for large files over unreliable connections — allows resume on failure

## Common Pitfalls
- Syncing to mounted drives that unmount silently creates a local folder with the mount name — verify mount before sync
- Running sync without `--delete` repeatedly causes destination to accumulate deleted files forever
- Time-based sync fails across machines with clock skew — use `--checksum` for accuracy or sync NTP first
