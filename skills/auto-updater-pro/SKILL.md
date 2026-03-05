---
name: auto-updater-pro
description: "Enhanced auto-updater with detailed logging, missed run recovery, and Gateway restart protection."
metadata: {"version":"1.1.0","clawdbot":{"emoji":"🔄","os":["darwin","linux"]}}
---

# Auto-Updater Pro

Enhanced auto-updater with detailed logging, missed run recovery, and Gateway restart protection.

**Version**: 1.1.0 (Updated 2026-02-22)

**What's New**:
- ✅ Detailed logging at each step (prevents state loss on restart)
- ✅ Missed run recovery (auto-runs if Gateway was offline)
- ✅ 30-second delay after updates (prevents interruption)
- ✅ Email report support (less intrusive than chat messages)
- ✅ Better error handling and retry logic

**Note**: This is an enhanced version of the original `auto-updater` skill with production-ready features.

---

## What It Does

This skill sets up a daily cron job that:

1. Updates Clawdbot itself (via `clawdbot doctor` or package manager)
2. Updates all installed skills (via `clawdhub update --all`)
3. Messages you with a summary of what was updated
4. **New**: Logs every step to prevent state loss on Gateway restart
5. **New**: Auto-recovers if the scheduled time was missed

---

## Setup

### Quick Start

Ask Clawdbot to set up the auto-updater:

```
Set up daily auto-updates for yourself and all your skills.
```

Or manually add the cron job:

```bash
clawdbot cron add \
  --name "Daily Auto-Update" \
  --cron "0 4 * * *" \
  --tz "America/Los_Angeles" \
  --session isolated \
  --wake now \
  --deliver \
  --message "Run daily auto-updates: check for Clawdbot updates and update all skills. Report what was updated."
```

### Recommended Configuration (v1.1.0+)

For production use, add these settings to your cron job:

```json
{
  "schedule": {
    "expr": "0 4 * * *",
    "kind": "cron",
    "tz": "Asia/Shanghai"
  },
  "missedRunPolicy": "run-immediately",
  "payload": {
    "kind": "agentTurn",
    "message": "...",
    "timeoutSeconds": 600
  }
}
```

**Key Settings**:
- `missedRunPolicy: "run-immediately"` - Auto-runs if Gateway was offline at scheduled time
- `timeoutSeconds: 600` - Allow 10 minutes for updates to complete
- `tz: "Asia/Shanghai"` - Set to your timezone

---

## Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| Time | 4:00 AM | When to run updates (use `--cron` to change) |
| Timezone | System default | Set with `--tz` |
| Delivery | Main session | Where to send the update summary |
| Timeout | 300s | Recommended: 600s for npm updates |
| Missed Run | None | Recommended: `run-immediately` |

---

## How Updates Work

### Clawdbot Updates

For **npm/pnpm/bun installs**:
```bash
npm update -g clawdbot@latest
# or: pnpm update -g clawdbot@latest
# or: bun update -g clawdbot@latest
```

For **source installs** (git checkout):
```bash
clawdbot update
```

Always run `clawdbot doctor` after updating to apply migrations.

### Skill Updates

```bash
clawdhub update --all
```

This checks all installed skills against the registry and updates any with new versions available.

---

## Update Summary Format

After updates complete, you'll receive a message like:

```
🔄 Daily Auto-Update Complete

**Clawdbot**: Updated to v2026.1.10 (was v2026.1.9)

**Skills Updated (3)**:
- prd: 2.0.3 → 2.0.4
- browser: 1.2.0 → 1.2.1  
- nano-banana-pro: 3.1.0 → 3.1.2

**Skills Already Current (5)**:
gemini, sag, things-mac, himalaya, peekaboo

No issues encountered.
```

---

## Detailed Logging (v1.1.0+)

To prevent state loss during Gateway restarts, the update process logs every step:

### Log File Location

```
~/.openclaw/workspace/memory/openclaw-update-YYYY-MM-DD.md
```

### Log Format

```markdown
# OpenClaw 更新日志 YYYY-MM-DD

## 更新前
- 开始时间：HH:mm:ss
- 当前版本：x.x.x
- 最新版本：x.x.x

## 更新中
- 更新开始：HH:mm:ss
- 更新命令：...
- 更新完成：HH:mm:ss
- 验证版本：x.x.x

## 更新后
- 状态：已是最新 / 已更新 / 更新失败
- 报告发送：成功 / 失败
- 完成时间：HH:mm:ss

## 更新内容
（从 CHANGELOG 或 npm 获取）
```

### Six-Phase Update Process

**Phase 1: Preparation**
- Record start time
- Check current version
- Write to log file immediately

**Phase 2: Check for Updates**
- Check latest version (npm view)
- Append to log file
- Compare versions

**Phase 3: Execute Update**
- Record update start
- Run `openclaw update run` or `npm install -g openclaw@latest`
- **Immediately** log completion
- Verify new version

**Phase 4: Persist State**
- Append full results to log
- **Wait 3 seconds** for disk sync

**Phase 5: Send Report**
- Send email/chat report
- Log delivery status

**Phase 6: Delay Restart (Critical!)**
- **Wait 30 seconds** before any Gateway restart
- Ensures npm processes complete
- Prevents state loss

---

## Manual Commands

Check for updates without applying:
```bash
clawdhub update --all --dry-run
```

View current skill versions:
```bash
clawdhub list
```

Check Clawdbot version:
```bash
clawdbot --version
```

---

## Troubleshooting

### Updates Not Running

1. Verify cron is enabled: check `cron.enabled` in config
2. Confirm Gateway is running continuously
3. Check cron job exists: `clawdbot cron list`
4. Check if missed run policy is set: `missedRunPolicy: "run-immediately"`

### Update Failures

If an update fails, the summary will include the error. Common fixes:

- **Permission errors**: Ensure the Gateway user can write to skill directories
- **Network errors**: Check internet connectivity
- **Package conflicts**: Run `clawdbot doctor` to diagnose
- **Gateway restart interruption**: Check log file for partial completion

### Gateway Restart During Update

If Gateway restarts during update (common with npm installs):

1. **Check log file**: `~/.openclaw/workspace/memory/openclaw-update-*.md`
2. **Verify version**: `openclaw --version`
3. **Manually send report** if needed (log file has all info)

### Disabling Auto-Updates

Remove the cron job:
```bash
clawdbot cron remove "Daily Auto-Update"
```

Or disable temporarily in config:
```json
{
  "cron": {
    "enabled": false
  }
}
```

---

## Best Practices

### 1. Schedule During Low Activity

Choose a time when you're unlikely to be using the system:
```json
"expr": "0 4 * * *"  // 4:00 AM
```

### 2. Enable Missed Run Recovery

Prevents missing updates if Gateway is offline:
```json
"missedRunPolicy": "run-immediately"
```

### 3. Use Email for Reports

Less intrusive than chat messages:
- Configure email-163-com or similar skill
- Send plain text reports
- Include log file path

### 4. Log Everything

Always write to log file before sending reports:
- Prevents state loss
- Enables debugging
- Provides audit trail

### 5. Wait After Updates

Add 30-second delay before any Gateway restart:
```bash
sleep 30
```

---

## Resources

- [Clawdbot Updating Guide](https://docs.clawd.bot/install/updating)
- [ClawdHub CLI](https://docs.clawd.bot/tools/clawdhub)
- [Cron Jobs](https://docs.clawd.bot/cron)
- [Change Log](~/.openclaw/workspace/memory/openclaw-update-*.md)

---

## Version History

### v1.1.0 (2026-02-22)

**Improvements**:
- ✅ Added detailed logging at each step
- ✅ Added missed run recovery policy
- ✅ Added 30-second delay after updates
- ✅ Added email report support
- ✅ Improved error handling

**Bug Fixes**:
- 🐛 Fixed state loss on Gateway restart
- 🐛 Fixed missed scheduled runs
- 🐛 Fixed report delivery failures

### v1.0.0 (2026-01-13)

- ✅ Initial release
- ✅ Basic daily update check
- ✅ Simple report format

---

**Published**: 2026-02-22  
**Maintainer**: OpenClaw Team  
**License**: MIT
