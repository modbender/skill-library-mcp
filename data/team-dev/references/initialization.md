# 初始化设置

首次使用前需要配置的定时任务。

## 首次使用检查

首次使用 skill 时，系统会自动检查配置：

```bash
# 检查脚本可执行权限
ls -la scripts/*.sh

# 检查 tmux 是否可用
tmux -V
```

## Cron 任务配置

### 方式 1: 使用 OpenClaw Cron (推荐)

使用 OpenClaw CLI 添加 cron 任务：

```bash
# 监控 agent 状态（每 10 分钟）
openclaw cron add \
  --name dev-team-monitor \
  --cron "*/10 * * * *" \
  --command scripts/check-agents.sh \
  --working-dir /Users/Vint/.openclaw/workspace/skills/dev-team \
  --session isolated \
  --no-deliver \
  --message "运行 dev-team 监控脚本 check-agents.sh 检查代理状态和 PR 状态机"

# 清理 worktree（每日凌晨 3 点）
openclaw cron add \
  --name dev-team-cleanup \
  --cron "0 3 * * *" \
  --command scripts/cleanup-worktrees.sh \
  --working-dir /Users/Vint/.openclaw/workspace/skills/dev-team \
  --session isolated \
  --no-deliver \
  --message "运行 dev-team 清理脚本 cleanup-worktrees.sh 清理已合并的 worktree"

# 归档历史任务（每日凌晨 3:10）
openclaw cron add \
  --name dev-team-prune-history \
  --cron "10 3 * * *" \
  --command "scripts/prune-history.sh --keep-days 7 --keep-count 50" \
  --working-dir /Users/Vint/.openclaw/workspace/skills/dev-team \
  --session isolated \
  --no-deliver \
  --message "运行 dev-team 归档脚本 prune-history.sh 归档过旧任务记录"
```

查看任务：
```bash
openclaw cron list
```

### 方式 2: 使用 macOS Cron

```bash
# 编辑 crontab
crontab -e

# 添加以下行
*/10 * * * * cd /path/to/skills/dev-team && ./scripts/check-agents.sh >> ./assets/logs/cron.log 2>&1
0 3 * * * cd /path/to/skills/dev-team && ./scripts/cleanup-worktrees.sh >> ./assets/logs/cleanup.log 2>&1
10 3 * * * cd /path/to/skills/dev-team && ./scripts/prune-history.sh --keep-days 7 --keep-count 50 >> ./assets/logs/prune.log 2>&1
```

### 方式 3: 使用 LaunchDaemon (macOS 开机自启)

创建 `~/Library/LaunchAgents/com.dev-team.agent-check.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.dev-team.agent-check</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>/path/to/skills/dev-team/scripts/check-agents.sh</string>
    </array>
    <key>StartInterval</key>
    <integer>600</integer>
</dict>
</plist>
```

加载:
```bash
launchctl load ~/Library/LaunchAgents/com.dev-team.agent-check.plist
```

### 方式 4: 使用 OpenClaw Heartbeat (补充方案)

Heartbeat 是主 session 的定期检查机制，适合轻量级任务。编辑主 session 的 `HEARTBEAT.md`：

```markdown
# HEARTBEAT.md

## 定期检查
- [ ] 运行 memory-heartbeat 逻辑
```

注意：Heartbeat 运行在主 session 上下文中，适合轻量检查。对于 dev-team 的监控任务，建议使用独立的 cron job（方式 1），可以避免主 session 上下文膨胀。

## 飞书通知

通知通过 OpenClaw 默认 channel 发送。检查脚本会：
1. 写入 `notifications.json`
2. OpenClaw 读取并通过飞书发送

## 日志位置

- 监控日志: `assets/logs/cron.log`
- 清理日志: `assets/logs/cleanup.log`
- 归档日志: `assets/logs/prune.log`
- Agent 日志: `assets/logs/`
- 通知队列: `assets/notifications.json`
- 历史归档: `assets/logs/archives/task-history-YYYY-MM.jsonl`

## 快速验证

```bash
# 测试监控脚本
./scripts/check-agents.sh

# 测试通知
# (OpenClaw 会自动读取 notifications.json)
```
