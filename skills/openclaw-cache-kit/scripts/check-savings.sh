#!/bin/bash
# openclaw-cache-kit: 오늘 캐시 절약 금액 계산
#
# 계산식:
#   cacheRead 토큰 × ($3.00 - $0.30) / 1,000,000 = 절약 금액
#
# 사용법: bash scripts/check-savings.sh [날짜 YYYY-MM-DD]
#         bash scripts/check-savings.sh            # 오늘
#         bash scripts/check-savings.sh 2026-02-19 # 특정 날짜

set -euo pipefail

LOG_FILE="${OPENCLAW_CACHE_LOG:-$HOME/.openclaw/logs/cache-trace.jsonl}"
TARGET_DATE="${1:-$(date '+%Y-%m-%d')}"

# 가격 상수 (USD per 1M tokens)
PRICE_INPUT=3.00
PRICE_CACHE_READ=0.30

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 OpenClaw 캐시 절약 리포트"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📅 대상 날짜: $TARGET_DATE"
echo ""

if [[ ! -f "$LOG_FILE" ]]; then
  echo "⚠️  로그 파일 없음: $LOG_FILE"
  echo ""
  echo "💡 캐시 추적을 활성화하려면:"
  echo "   bash scripts/apply.sh"
  exit 0
fi

# Python으로 JSONL 파싱 및 계산
python3 - "$LOG_FILE" "$TARGET_DATE" "$PRICE_INPUT" "$PRICE_CACHE_READ" << 'PYEOF'
import json, sys
from datetime import datetime

log_file   = sys.argv[1]
target_date = sys.argv[2]
price_input = float(sys.argv[3])
price_cache = float(sys.argv[4])

total_cache_read   = 0
total_cache_write  = 0
total_input        = 0
total_output       = 0
record_count       = 0

with open(log_file, encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except Exception:
            continue

        # 날짜 필터
        ts = rec.get("timestamp") or rec.get("ts") or rec.get("created_at") or ""
        if ts and not ts.startswith(target_date):
            continue

        usage = rec.get("usage") or rec.get("tokens") or rec
        cache_read  = usage.get("cache_read_input_tokens") or usage.get("cacheRead") or 0
        cache_write = usage.get("cache_creation_input_tokens") or usage.get("cacheWrite") or 0
        inp         = usage.get("input_tokens") or usage.get("input") or 0
        out         = usage.get("output_tokens") or usage.get("output") or 0

        total_cache_read  += int(cache_read)
        total_cache_write += int(cache_write)
        total_input       += int(inp)
        total_output      += int(out)
        record_count      += 1

# 절약 금액 계산
# 캐시 히트 없었을 때 비용 = cacheRead × price_input
# 실제 비용 = cacheRead × price_cache
savings = total_cache_read * (price_input - price_cache) / 1_000_000
actual_cost = total_cache_read * price_cache / 1_000_000
would_cost  = total_cache_read * price_input / 1_000_000

print(f"  요청 건수        : {record_count:,} 건")
print(f"  cacheRead 토큰   : {total_cache_read:,}")
print(f"  cacheWrite 토큰  : {total_cache_write:,}")
print(f"  일반 Input 토큰  : {total_input:,}")
print(f"  Output 토큰      : {total_output:,}")
print("")
print(f"  캐시 없을 때 비용: ${would_cost:.4f}")
print(f"  실제 비용        : ${actual_cost:.4f}")
print(f"  💰 절약 금액     : ${savings:.4f}")
print("")
if total_cache_read > 0:
    pct = savings / would_cost * 100 if would_cost > 0 else 0
    print(f"  절약률           : {pct:.1f}%")
else:
    print("  ℹ️  오늘 캐시 히트 기록 없음")
    print("  (diagnostics.cacheTrace.enabled: true 확인)")
PYEOF

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "전체 기간 누적 보려면:"
echo "  bash scripts/check-savings.sh all"
