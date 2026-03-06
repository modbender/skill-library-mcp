#!/usr/bin/env bash
set -euo pipefail

INTERVAL="${1:-10m}"
WINDOW="${2:-20}"
NAME="${3:-weibo-fresh-posts}"

PROMPT_DIR="${HOME}/.openclaw/prompts"
PROMPT_FILE="${PROMPT_DIR}/${NAME}.prompt"

mkdir -p "${PROMPT_DIR}"

cat > "${PROMPT_FILE}" <<PROMPT
使用 weibo-fresh-posts 技能。
要求：
1) 使用 browser 的 profile=openclaw、target=host 打开 https://weibo.com。
2) 抓取前必须点击左侧“最新微博”。
3) 按发帖时间写入 YYYY-MM-DD HH:mm，禁止使用抓取时间。
4) 发帖内容列必须写原始贴文正文，不能写成总结。
5) 若卡片正文被截断，进入原帖详情提取完整正文。
6) 抓取窗口为最近 ${WINDOW} 分钟。
7) 按原始链接去重，写入 ~/weibo-digest/YYYY-MM-DD.md。
PROMPT

openclaw cron add \
  --name "${NAME}" \
  --every "${INTERVAL}" \
  --session isolated \
  --message "$(cat "${PROMPT_FILE}")" \
  --timeout-seconds 240 \
  --no-deliver

echo "已创建定时任务 '${NAME}'，间隔 ${INTERVAL}。"
echo "提示词文件：${PROMPT_FILE}"
