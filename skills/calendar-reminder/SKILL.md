---
name: calendar-reminder
description: "每晚22:00自动扫描明天的Outlook日历，上午日程提前2小时提醒，下午日程12:00统一提醒，通过飞书发送通知。依赖 owa-outlook skill。"
metadata: { "openclaw": { "emoji": "📅", "requires": { "bins": ["python3", "openclaw"] } } }
---

# Calendar Reminder 日历提醒

## 功能

每晚 22:00 自动扫描明天的 Outlook 日历，按时间段设置提醒：
- 上午日程（< 12:00）→ 提前 2 小时飞书提醒
- 下午日程（>= 12:00）→ 当天 12:00 统一飞书提醒
- 扫描完成后立即发送汇报消息

## 依赖

- `owa-outlook` skill（提供 `owa_calendar.py`）
- `openclaw` CLI
- Python 3.9+（需要 `zoneinfo` 模块）

## 安装后配置

### 1. 注册每晚扫描 cron

```bash
openclaw cron add \
  --name "calendar-daily-scan" \
  --cron "0 22 * * *" \
  --tz "Asia/Shanghai" \
  --session main \
  --system-event "CALENDAR_SCAN: 请立即运行 python3 ~/.openclaw/workspace/skills/calendar-reminder/calendar_reminder.py 并等待完成" \
  --description "每晚22:00扫描明天日历并设置提醒"
```

### 2. 修改脚本中的飞书 open_id

编辑 `calendar_reminder.py`，将 `send_feishu` 函数中的 `target` 改为你自己的飞书 open_id：

```python
"--target", "user:ou_xxxxxxxxxxxxxxxx",
```

## 手动运行

```bash
python3 ~/.openclaw/workspace/skills/calendar-reminder/calendar_reminder.py
```
