#!/usr/bin/env bash
set -euo pipefail

IDS=$(openclaw cron list --all --json | node -e 'let s="";process.stdin.on("data",d=>s+=d);process.stdin.on("end",()=>{const j=JSON.parse(s);const arr=Array.isArray(j)?j:(j.jobs||[]);for(const r of arr){if(r.name==="drink-water-reminder") console.log(r.id)}})')

if [[ -z "$IDS" ]]; then
  echo "未找到 drink-water-reminder 任务"
  exit 0
fi

while IFS= read -r id; do
  [[ -z "$id" ]] && continue
  openclaw cron rm "$id"
done <<< "$IDS"

echo "已删除 drink-water-reminder"
