---
name: graceful-restart
description: 优雅重启 Gateway。解决重启后丢失会话上下文的问题，重启前设置一次性 cron 任务，重启后自动发送消息到主会话恢复任务。默认 10 秒后唤醒。依赖 openclaw CLI。触发词：重启、restart。
---

# graceful-restart skill

## 触发条件

当用户要求重启 Gateway 时，自动触发此 skill。

## 问题背景

Gateway 重启后，会丢失上一轮会话的任务上下文，导致：
- 主会话被中断，无法自动恢复
- 需要用户手动发送消息才能继续

## 功能

自动执行"重启后自唤醒"流程：
1. 设置一次性 cron 任务（默认 10 秒后触发）
2. 执行 Gateway 重启
3. 重启后自动发送消息到主会话

## English Description

**Problem:** After Gateway restarts, OpenClaw loses the previous session context - the main session is interrupted and cannot resume automatically.

**Solution:** Auto-restart Gateway with self-wakeup. Sets a one-time cron task (default 10s) before restart, then sends a message to main session after Gateway recovers to resume tasks.

**⚠️ Important: Must use this skill, NOT exec:**
```bash
# ✅ Correct
node ~/.openclaw/workspace/skills/graceful-restart/graceful-restart.js --task "config changed"

# ❌ Wrong
exec openclaw gateway restart  # Don't do this!
```

**Trigger:** "重启", "restart Gateway"

## 使用方式

用户说"重启"时，自动执行：
```
[自动触发 graceful-restart skill]
```

或者用户可以指定任务：
```
重启 Gateway，继续之前的任务：安装 Python 包
```

## 命令行调用

```bash
node ~/.openclaw/workspace/skills/graceful-restart/graceful-restart.js
node ~/.openclaw/workspace/skills/graceful-restart/graceful-restart.js --task "继续安装 Python 包"
node ~/.openclaw/workspace/skills/graceful-restart/graceful-restart.js --task "继续安装 Python 包" --delay 60
```

## 实现原理

使用 `--session main` + `--system-event`：
- Cron 在主会话里注入一个 system event
- Gateway 重启后，heartbeat 轮询到并交付给主会话
- 主会话收到消息后回复用户

## 注意事项

- Cron 任务时间可调整（默认 10 秒）
- 使用 `--delete-after-run` 确保一次性任务自动清理

## 📝 更新 SOUL.md

使用此 skill 后，建议在 `SOUL.md` 中添加自动触发规则（见上方）。

## ⚠️ 重要：禁止使用 exec

Gateway 重启**必须使用此 skill**，禁止直接用 exec 执行：

✅ **正确：**
```bash
node ~/.openclaw/workspace/skills/graceful-restart/graceful-restart.js --task "配置已修改，需要重启后生效"
```

❌ **错误：**
```bash
exec openclaw gateway restart  # 禁止！
```

这样写
