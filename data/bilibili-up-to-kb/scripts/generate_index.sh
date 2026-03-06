#!/usr/bin/env bash
# generate_index.sh — Generate index.md from .meta.json files in a knowledge base directory
# Usage: generate_index.sh <kb_dir>
set -euo pipefail

DIR="$1"
cd "$DIR"

python3 << 'PYEOF'
import json, glob, os

metas = sorted(glob.glob("*.meta.json"))
if not metas:
    print("No .meta.json files found, skipping index generation.")
    exit(0)

uploader = ""
rows = []
for m in metas:
    try:
        d = json.load(open(m))
    except:
        continue
    if not uploader:
        uploader = d.get("uploader", "")
    dur = int(d.get("duration", 0) or 0)
    date = str(d.get("upload_date", ""))
    if len(date) == 8:
        date = f"{date[:4]}-{date[4:6]}-{date[6:]}"
    views = int(d.get("view_count", 0) or 0)
    bv = d.get("bvid", "")
    title = d.get("title", "")
    desc = d.get("description", "")[:100]
    # Determine the transcript filename
    fb = d.get("filename_base", bv)
    has_raw = os.path.exists(f".raw/{fb}.txt") or os.path.exists(f".raw/{bv}.txt")
    has_clean = os.path.exists(f"{fb}.txt") or os.path.exists(f"{bv}.txt")
    rows.append((bv, title, f"{dur//60}:{dur%60:02d}", date, views, has_raw, has_clean))

with open("index.md", "w") as f:
    f.write(f"# 知识库: {uploader}\n\n")
    f.write(f"视频数: {len(rows)}\n\n")
    f.write("| # | BV号 | 标题 | 时长 | 上传日期 | 播放量 | 状态 |\n")
    f.write("|---|------|------|------|----------|--------|------|\n")
    for i, (bv, title, dur, date, views, has_r, has_c) in enumerate(rows, 1):
        if has_c:
            status = "✅"
        elif has_r:
            status = "⏳ 待清洗"
        else:
            status = "❌"
        f.write(f"| {i} | {bv} | {title} | {dur} | {date} | {views:,} | {status} |\n")

print(f"index.md: {len(rows)} videos by {uploader}")
PYEOF
