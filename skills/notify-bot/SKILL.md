---
name: notify-bot
description: 向指定 Telegram bot 发送任务通知，激活其群组 session。
---

# notify-bot

向指定 Telegram bot 发送任务通知，激活其群组 session。

## 用法

```bash
notify_bot.sh <bot_name|bot1,bot2> <group_id> <topic_id> <message>
```

## 示例

```bash
# 通知单个 bot
notify_bot.sh imagebot -1003870994840 11 "生成32x32宝箱图标"

# 通知多个 bot
notify_bot.sh "imagebot,godot,cursor" -1003870994840 3 "任务通知"
```

## 工作流程

1. **notify_bot.sh** 发消息到指定群组/话题 → 激活 bot 的 session
2. **sessions_send** 给激活的 session 发指令 → bot 执行任务

## 注意事项

- Bot token 从 keychain 读取（`openclaw.telegram.<bot_name>.bot_token`）
- vision bot 的 key 是 `openclaw.telegram.vision.token`
- 消息发送后不会删除，直接留在群里
- 适用于需要精确控制哪些 bot 被通知的场景

## 脚本位置

`~/.openclaw/shared/notify_bot.sh`
