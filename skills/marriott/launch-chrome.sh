#!/bin/bash
# launch-chrome.sh — 用远程调试模式启动 Chrome
# 运行后在 Chrome 中手动登录万豪，然后运行 claude 使用 /marriott skill

echo "正在启动 Chrome（远程调试端口 9222）..."
echo "启动后请在 Chrome 中："
echo "  1. 打开 https://www.marriott.com.cn"
echo "  2. 手动登录账号"
echo "  3. 然后回到终端运行 claude，使用 /marriott 呼叫 skill"
echo ""

CHROME_ARGS=(
  --remote-debugging-port=9222
  --no-first-run
  --no-default-browser-check
  --disable-blink-features=AutomationControlled
)

if [[ "$(uname)" == "Darwin" ]]; then
  # macOS
  pkill -f "Google Chrome" 2>/dev/null || true
  sleep 1
  open -a "Google Chrome" --args "${CHROME_ARGS[@]}"
else
  # Linux
  pkill -f "google-chrome" 2>/dev/null || true
  sleep 1
  google-chrome "${CHROME_ARGS[@]}" &
fi
