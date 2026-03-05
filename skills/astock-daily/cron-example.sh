#!/bin/bash
# A 股每日精选 - Cron 定时任务配置示例
# 每天上午 9 点运行（A 股开盘后）

# 添加到 crontab:
# crontab -e
# 然后粘贴以下内容:

# 环境变量（如果需要 SMTP 发送邮件）
# export SMTP_CONFIG='{"host":"smtp.gmail.com","port":587,"secure":false,"user":"your@gmail.com","pass":"your-app-password","from":"your@gmail.com"}'

# 每天 9:00 运行
0 9 * * 1-5 cd /Users/batype/.openclaw/workspace-work/skills/astock-daily && /usr/local/bin/node index.js >> /tmp/astock-daily.log 2>&1

# 或者每天 9:30 运行（避开开盘高峰）
# 30 9 * * 1-5 cd /Users/batype/.openclaw/workspace-work/skills/astock-daily && /usr/local/bin/node index.js >> /tmp/astock-daily.log 2>&1

# 查看日志:
# tail -f /tmp/astock-daily.log

# 查看 node 路径:
# which node
