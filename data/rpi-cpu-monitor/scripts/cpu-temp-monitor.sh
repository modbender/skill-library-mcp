#!/bin/bash
# CPU 温度监控脚本 - 温度超标才发 API，正常时零消耗

TEMP=$(vcgencmd measure_temp 2>/dev/null | cut -d= -f2 | cut -d\' -f1)
[ -z "$TEMP" ] && TEMP=$(cat /sys/class/thermal/thermal_zone0/temp 2>/dev/null | awk '{print $1/1000}')

if [ -z "$TEMP" ]; then
  exit 1
fi

TEMP_INT=${TEMP%.*}

if [ "$TEMP_INT" -gt 70 ]; then
  # 温度超标，发送告警到 OpenClaw
  curl -s -X POST "http://localhost:3000/api/sessions/agent:main:main/message" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $(cat /home/weiye/.openclaw/gateway-token 2>/dev/null)" \
    -d '{"message":"⚠️ CPU温度过高: '${TEMP}'°C (阈值70°C)", "channel":"feishu"}' \
    > /dev/null 2>&1
fi

# 正常温度不调用任何 API
