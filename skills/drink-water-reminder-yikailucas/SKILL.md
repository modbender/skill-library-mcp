---
name: drink-water-reminder
description: Create, manage, and remove periodic hydration reminders via OpenClaw cron jobs. Use when users ask for recurring drink-water reminders (e.g. every 1 minute / 30 minutes / hourly).
---

# drink-water-reminder

用 OpenClaw 的 cron 定时提醒喝水。

## 快速使用

```bash
cd skills/drink-water-reminder

# 每1分钟提醒
bash scripts/add_reminder.sh 1m

# 每30分钟提醒
bash scripts/add_reminder.sh 30m

# 每1小时提醒
bash scripts/add_reminder.sh 1h

# 查看当前提醒任务
bash scripts/list_reminder.sh

# 删除提醒任务
bash scripts/remove_reminder.sh
```

## 默认行为

- 任务名：`drink-water-reminder`
- 提醒文案：`喝水提醒：现在喝几口水。`
- 投递方式：announce 到当前会话

## 参数

`add_reminder.sh` 支持：

- 第一个参数：间隔（默认 `1h`，例如 `1m` / `30m` / `2h`）
- 第二个参数：提醒文案（可选）

示例：

```bash
bash scripts/add_reminder.sh 20m "喝水提醒：起身喝半杯温水。"
```
