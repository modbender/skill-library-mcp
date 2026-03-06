---
name: weather-push
description: 每日天气推送 - 定时发送深圳天气+mihomo服务状态到飞书
emoji: 🌤️
metadata:
  cron: "0 8 * * *"
  requires:
    - python3 (lunarcalendar)
    - ssh access to mihomo server
---

# Weather Push Skill

定时推送深圳天气+mihomo服务状态到飞书

## 功能

- 深圳龙岗 + 福田两地天气
- 与昨日温度对比
- 农历日期
- 远程检测 mihomo 服务状态（10.144.1.3）

## 文件

- `push.sh` - 主脚本

## 定时任务

- 每天 8:00 自动推送
- 12:00 测试推送

## 手动运行

```bash
/home/aisulada/.openclaw/workspace-feishu/skills/weather-push/push.sh
```

## 依赖

- Python3 + lunarcalendar 库
- SSH 访问 MiHoMo 服务器 (10.144.1.3)
- OpenClaw 消息接口

## 配置

如需修改目标用户，编辑 `push.sh` 中的 `--target` 参数
