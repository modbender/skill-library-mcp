#!/bin/bash
# korean-gov-programs: 수집 현황 출력
# 사용법: bash scripts/stats.sh [데이터디렉토리]
#         bash scripts/stats.sh ./data

set -euo pipefail

DATA_DIR="${1:-./data}"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 한국 정부지원사업 수집 현황"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📁 데이터 디렉토리: $DATA_DIR"
echo ""

if [[ ! -d "$DATA_DIR" ]]; then
  echo "⚠️  디렉토리 없음: $DATA_DIR"
  echo "   python3 scripts/collect.py --output $DATA_DIR 를 먼저 실행하세요."
  exit 0
fi

# JSONL 파일 통계 (Python으로 정확한 파싱)
python3 - "$DATA_DIR" << 'PYEOF'
import os, json, sys
from collections import defaultdict
from datetime import datetime

data_dir = sys.argv[1]
files = {
    "soho_programs.jsonl": "소상공인 지원사업",
    "gov_programs.jsonl":  "R&D / 기술창업",
}

total_all = 0

for filename, label in files.items():
    filepath = os.path.join(data_dir, filename)
    if not os.path.exists(filepath):
        print(f"  [{label}] 파일 없음: {filename}")
        continue

    records = []
    with open(filepath, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except Exception:
                    pass

    total = len(records)
    total_all += total

    # 카테고리별 집계
    by_category = defaultdict(int)
    by_source = defaultdict(int)
    latest = ""

    for rec in records:
        by_category[rec.get("category", "기타")] += 1
        by_source[rec.get("source", "미상")] += 1
        ts = rec.get("collected_at", "")
        if ts > latest:
            latest = ts

    print(f"  [{label}] {filename}")
    print(f"    총 건수: {total:,}건")

    if by_category:
        print("    카테고리:")
        for cat, cnt in sorted(by_category.items(), key=lambda x: -x[1]):
            print(f"      {cat}: {cnt:,}건")

    if by_source:
        print("    출처:")
        for src, cnt in sorted(by_source.items(), key=lambda x: -x[1]):
            print(f"      {src}: {cnt:,}건")

    if latest:
        print(f"    최근 수집: {latest[:19]}")
    print()

print(f"  합계: {total_all:,}건")
PYEOF

# 체크포인트 확인
CHECKPOINT="$DATA_DIR/.checkpoint.json"
if [[ -f "$CHECKPOINT" ]]; then
  echo ""
  echo "📍 체크포인트:"
  python3 -c "
import json
with open('$CHECKPOINT', encoding='utf-8') as f:
    cp = json.load(f)
for k, v in cp.items():
    print(f'  {k}: {v}')
"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "추가 수집:"
echo "  python3 scripts/collect.py --output $DATA_DIR"
