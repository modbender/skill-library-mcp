---
name: rpi-cpu-monitor
description: 树莓派 CPU 温度监控。当需要监控树莓派 CPU 温度时使用此 skill。功能：(1) 读取当前 CPU 温度，(2) 设置定时监控任务，(3) 温度超标时自动告警。支持 crontab 方案（零消耗，推荐）和 OpenClaw cron 方案。
---

# 树莓派 CPU 温度监控

## 快速开始

### 方案 1：crontab 方案（推荐，零消耗）

```bash
# 创建监控脚本
cat > /path/to/scripts/cpu-temp-monitor.sh << 'EOF'
#!/bin/bash
TEMP=$(vcgencmd measure_temp 2>/dev/null | cut -d= -f2 | cut -d\' -f1)
[ -z "$TEMP" ] && TEMP=$(cat /sys/class/thermal/thermal_zone0/temp | awk '{print $1/1000}')
TEMP_INT=${TEMP%.*}

if [ "$TEMP_INT" -gt 70 ]; then
  curl -s -X POST "http://localhost:3000/api/sessions/agent:main:main/message" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $(cat /home/weiye/.openclaw/gateway-token)" \
    -d '{"message":"⚠️ CPU温度过高: '${TEMP}'°C", "channel":"feishu"}'
fi
EOF

chmod +x /path/to/scripts/cpu-temp-monitor.sh

# 添加到 crontab（每 35 分钟执行）
crontab -e
# 添加: */35 * * * * /path/to/scripts/cpu-temp-monitor.sh
```

### 方案 2：OpenClaw cron 方案

```bash
# 启用 OpenClaw 内置 cron（每次调用大模型）
openclaw cron add --name "CPU温度监控" --schedule "*/35 * * * *" \
  --message "检查CPU温度：运行 vcgencmd measure_temp，如果>70°C发送警告" \
  --session isolated
```

## 对比

| 方案 | 大模型调用 | 适用场景 |
|------|-----------|---------|
| crontab | 0 次（仅超标时 API） | 生产环境，推荐 |
| OpenClaw cron | 每次 1 次 | 测试/开发 |

## 配置项

- 温度阈值：默认 70°C，可修改脚本中的 `70`
- 监控间隔：默认 35 分钟，修改 crontab 表达式
- 告警渠道：默认飞书，修改 API 调用中的 channel 参数
