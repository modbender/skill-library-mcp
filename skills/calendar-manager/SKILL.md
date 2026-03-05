---
name: calendar-manager
version: 1.0.0
description: 日历管理技能 - 让 AI 能够读取日程、创建事件、设置提醒。当用户要求查看日程、添加日历事件、提醒 upcoming events 时触发此技能。
---

# Calendar Manager - 日历管理技能

## 概述

赋予 AI 日历管理能力：
- 读取日历事件
- 创建/修改/删除事件
- 设置提醒
- 查找空闲时间

## 触发场景

1. 用户要求"查看今天/明天/本周的日程"
2. 用户要求"添加一个会议/事件"
3. 用户要求"设置提醒"
4. 用户询问"今天有什么安排"
5. 定时提醒用户 upcoming events

## 支持的日历服务

| 服务 | 说明 |
|------|------|
| Google Calendar | 需要 gcal CLI 或 API |
| Apple Calendar (macOS) | 使用 icalBuddy |
| Outlook | 使用 gog CLI |
| Fantastical | 第三方应用 |

## 使用方法

### Google Calendar (gog CLI)

```bash
# 列出今天的事件
gog calendar list today

# 列出明天的事件
gog calendar list tomorrow

# 列出这周的事件
gog calendar list this-week

# 创建事件
gog calendar create "会议名称" --when "2026-02-25 14:00" --duration 60

# 快速添加事件
gog calendar add "Team Meeting" tomorrow 3pm
```

### Apple Calendar (icalBuddy)

```bash
# 安装
brew install ical-buddy

# 列出今天的事件
icalBuddy eventsToday

# 列出明天的事件
icalBuddy eventsTomorrow

# 列出指定日期范围
icalBuddy eventsFrom:2026-02-24 to:2026-02-28
```

## 工作流

```
1. 检查可用的日历工具
2. 获取指定时间范围的事件
3. 筛选重要/即将到来的事件
4. 汇总呈现给用户
```

## 提醒设置

| 提醒时间 | 说明 |
|----------|------|
| 事件前 15 分钟 | 会议/约会 |
| 事件前 1 小时 | 重要事项 |
| 事件前 1 天 | 当天提醒 |
| 事件前 1 周 | 周计划 |

## 输出格式

向用户呈现日历时：
- 日期和时间
- 事件名称
- 地点（如果有）
- 参与人（如果有）
- 建议的准备事项

## 与邮件技能配合

可以与 email-reader 配合：
- 读取邮件中的会议邀请
- 自动创建日历事件
- 发送会议提醒邮件
