#!/usr/bin/env bash
set -euo pipefail

INTERVAL="${1:-1h}"
MSG="${2:-喝水提醒：现在喝几口水。}"
NAME="drink-water-reminder"

# 若已存在同名任务，先删除再创建，避免重复
EXISTING_ID=$(openclaw cron list --all --json | node -e 'let s="";process.stdin.on("data",d=>s+=d);process.stdin.on("end",()=>{try{const j=JSON.parse(s);const arr=Array.isArray(j)?j:(j.jobs||[]);const hit=arr.find(x=>x.name==="drink-water-reminder");if(hit) process.stdout.write(hit.id||"");}catch{}})')
if [[ -n "$EXISTING_ID" ]]; then
  openclaw cron rm "$EXISTING_ID" >/dev/null 2>&1 || true
fi

openclaw cron add \
  --name "$NAME" \
  --description "定时喝水提醒" \
  --every "$INTERVAL" \
  --session isolated \
  --announce \
  --message "$MSG"
