# 日历管理参考资料

## gcal CLI

### 安装
```bash
# macOS
brew install gcalcli

# Python
pip install gcalcli
```

### 配置
```bash
# OAuth 登录
gcalcli --oauth2

# 或使用凭据
gcalcli --client-id ID --client-secret SECRET ...
```

### 常用命令

```bash
# 列出今天
gcalcli calw

# 列出本周
gcalcli calw -n 2

# 搜索事件
gcalcli search "会议"

# 快速添加
gcalcli quick "Meeting" tomorrow 3pm

# 详细添加
gcalcli add \
  "团队会议" \
  --when "2026-02-25 14:00" \
  --duration 60 \
  --where "会议室A" \
  --description "讨论项目进度"
```

## icalBuddy (macOS)

### 安装
```bash
brew install ical-buddy
```

### 常用命令

```bash
# 今天事件（含详情）
icalBuddy eventsToday+

# 明天事件
icalBuddy eventsTomorrow

# 指定范围
icalBuddy eventsFrom:2026-02-24 to:2026-02-28

# 未完成的任务
icalBuddy uncompletedTasks

# 带颜色输出
icalBuddy -c eventsToday
```

## Cron 格式

```
┌───────────── 分钟 (0 - 59)
│ ┌───────────── 小时 (0 - 23)
│ │ ┌───────────── 日期 (1 - 31)
│ │ │ ┌───────────── 月份 (1 - 12)
│ │ │ │ ┌───────────── 星期 (0 - 6) (周日=0)
│ │ │ │ │
* * * * *
```

### 示例
```bash
# 每小时
0 * * * *

# 每天 8 点
0 8 * * *

# 每周一 9 点
0 9 * * 1

# 每月 1 号 10 点
0 10 1 * *

# 每 30 分钟
*/30 * * * *
```

## Windows 任务计划

```powershell
# 创建每日任务
$action = New-ScheduledTaskAction -Execute "python.exe" -Argument "script.py"
$trigger = New-ScheduledTaskTrigger -Daily -At "8:00AM"
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "DailyTask"
```
