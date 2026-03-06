#!/usr/bin/env bash
set -euo pipefail

openclaw cron list --all --json | node -e 'let s="";process.stdin.on("data",d=>s+=d);process.stdin.on("end",()=>{const j=JSON.parse(s);const arr=Array.isArray(j)?j:(j.jobs||[]);const rows=arr.filter(x=>x.name==="drink-water-reminder");if(!rows.length){console.log("未找到 drink-water-reminder 任务");return;}for(const r of rows){console.log(`id=${r.id}\nname=${r.name}\nenabled=${r.enabled}\nnextRunAtMs=${r.state?.nextRunAtMs||""}\n---`);}})'
