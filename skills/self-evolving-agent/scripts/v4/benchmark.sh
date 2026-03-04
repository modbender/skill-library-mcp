#!/usr/bin/env bash
# ============================================================
# benchmark.sh — Self-Evolving Agent v4.0 외부 벤치마크 수집기
#
# 역할 (명세서 v4.0):
#   1. OpenClaw GitHub 최신 릴리스 / breaking changes 확인
#   2. ClawHub trending skills (API 있으면 수집, 없으면 skip)
#   3. 현재 AGENTS.md 구조 vs 권장 사항 비교
#
# 설계 원칙:
#   - 전체 실행 < 30초
#   - 모든 외부 호출: `|| true` (실패해도 계속)
#   - 의존성 없으면 graceful skip
#   - jq/curl 없어도 동작 (최소한의 출력 보장)
#
# 출력:
#   /tmp/sea-v4/benchmarks.json (+ stdout)
#
# 사용법:
#   bash benchmark.sh
#   OFFLINE=true bash benchmark.sh   # 오프라인 강제
# ============================================================

# SECURITY MANIFEST:
# Environment variables accessed: SEA_TMP_DIR, OFFLINE
# External endpoints called:
#   https://api.github.com/repos/openclaw-ai/openclaw/releases/latest
#     (GitHub public API, optional, max 10s timeout, 60 req/hr unauthenticated)
#   https://clawhub.com/api/v1/skills/trending
#     (ClawHub API, optional, may not exist — graceful skip)
#   Both calls skipped when OFFLINE=true or when curl is unavailable.
# Local files read:
#   ~/openclaw/AGENTS.md  (structure analysis: line count, section headers, patterns)
# Local files written:
#   <SEA_TMP_DIR>/benchmarks.json  (default: /tmp/sea-v4/benchmarks.json)
# Network: Optional. GitHub API + ClawHub API (both skippable, read-only, no auth)

# -e 제외: 외부 실패 시에도 계속 진행
set -o pipefail  # -u 제거: bash 3.2 empty array 호환

# ── 경로 및 환경변수 ────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
AGENTS_MD="${HOME}/openclaw/AGENTS.md"
OUTPUT_DIR="${SEA_TMP_DIR:-/tmp/sea-v4}"
OUTPUT_FILE="$OUTPUT_DIR/benchmarks.json"
OFFLINE="${OFFLINE:-false}"

START_TS=$(date +%s)
mkdir -p "$OUTPUT_DIR" || true

echo "⚡ [benchmark] 수집 시작 — 목표 30초 이내" >&2

# ── 헬퍼 ────────────────────────────────────────────────────
HAS_JQ=false;   command -v jq   &>/dev/null && HAS_JQ=true   || true
HAS_CURL=false; command -v curl &>/dev/null && HAS_CURL=true  || true
HAS_BC=false;   command -v bc   &>/dev/null && HAS_BC=true    || true

# 경과 시간 (초)
elapsed() { echo $(($(date +%s) - START_TS)); }

# JSON 안전 이스케이프
je() {
  local s="$1"
  s="${s//\\/\\\\}"; s="${s//\"/\\\"}"; s="${s//$'\n'/ }"; s="${s//$'\t'/ }"
  printf '%s' "$s"
}

# curl + 타임아웃 래퍼 (실패 시 빈 문자열)
safe_curl() {
  local url="$1"; shift
  $HAS_CURL || { echo ""; return; }
  [ "$OFFLINE" = "true" ] && { echo ""; return; }
  curl -sf --connect-timeout 5 --max-time 10 \
    -H "User-Agent: self-evolving-agent/4.0" \
    "$@" "$url" 2>/dev/null || echo ""
}

# ═══════════════════════════════════════════════════════════
# 섹션 1: OpenClaw GitHub 최신 릴리스 확인
# ═══════════════════════════════════════════════════════════
echo "  [1/3] GitHub 릴리스 확인..." >&2

GH_STATUS="skip"
GH_TAG="unknown"; GH_DATE="unknown"; GH_URL=""; GH_BODY=""
GH_BREAKING="[]"; GH_FEATURES="[]"

# GitHub API — 공개 rate limit 60회/hr
GH_API="https://api.github.com/repos/openclaw-ai/openclaw/releases/latest"
GH_RAW=$(safe_curl "$GH_API" -H "Accept: application/vnd.github+json")

if [ -n "$GH_RAW" ]; then
  if $HAS_JQ; then
    GH_TAG=$(echo "$GH_RAW"  | jq -r '.tag_name      // "unknown"' 2>/dev/null || echo "unknown")
    GH_DATE=$(echo "$GH_RAW" | jq -r '.published_at  // "unknown"' 2>/dev/null || echo "unknown")
    GH_URL=$(echo "$GH_RAW"  | jq -r '.html_url      // ""'        2>/dev/null || echo "")
    GH_BODY=$(echo "$GH_RAW" | jq -r '.body          // ""'        2>/dev/null || echo "")
    GH_STATUS="ok"
  else
    # jq 없음 — grep fallback
    GH_TAG=$(echo "$GH_RAW" | grep -o '"tag_name":"[^"]*"' | head -1 \
             | sed 's/"tag_name":"//;s/"//' || echo "unknown")
    GH_STATUS="ok_no_jq"
  fi
  echo "    최신 릴리스: $GH_TAG ($GH_DATE)" >&2
else
  GH_STATUS="unavailable"
  echo "    GitHub API 응답 없음 (오프라인 또는 비공개 레포)" >&2
fi

# 릴리스 노트에서 breaking / new features 파싱
if [ -n "$GH_BODY" ]; then
  # Breaking changes 줄 추출
  RAW_BREAK=$(echo "$GH_BODY" | grep -iE "breaking|BREAKING|호환성 변경|⚠️" | head -5 || echo "")
  RAW_FEAT=$(echo  "$GH_BODY" | grep -iE "^[-*]?\s*(feat|add|new|추가|신규|✨)" | head -5 || echo "")

  if [ -n "$RAW_BREAK" ]; then
    GH_BREAKING=$(echo "$RAW_BREAK" | awk '{printf "\"%s\",", $0}' | sed 's/,$//' \
                  | sed 's/^/[/;s/$/]/' 2>/dev/null || echo "[]")
  fi
  if [ -n "$RAW_FEAT" ]; then
    GH_FEATURES=$(echo "$RAW_FEAT" | awk '{printf "\"%s\",", $0}' | sed 's/,$//' \
                  | sed 's/^/[/;s/$/]/' 2>/dev/null || echo "[]")
  fi
fi

# ═══════════════════════════════════════════════════════════
# 섹션 2: ClawHub trending skills
# ═══════════════════════════════════════════════════════════
echo "  [2/3] ClawHub trending skills 확인..." >&2

CH_STATUS="skip"
CH_TRENDING="[]"
CH_SEA_RANK="unknown"

if [ "$(elapsed)" -lt 20 ]; then
  # ClawHub 공개 API (있으면 수집, 없으면 graceful skip)
  CH_API="https://clawhub.com/api/v1/skills/trending"
  CH_RAW=$(safe_curl "$CH_API")

  if [ -n "$CH_RAW" ] && $HAS_JQ; then
    # 여러 가능한 응답 구조 시도
    CH_TRENDING=$(echo "$CH_RAW" | jq -c '
      ( .skills // .data // . )
      | if type == "array" then .[0:5] else [] end
      | map({name: (.name // "?"), downloads: (.downloads // 0), category: (.category // "?")})
    ' 2>/dev/null || echo "[]")

    # self-evolving-agent 순위 확인
    CH_SEA_RANK=$(echo "$CH_RAW" | jq -r '
      ( .skills // .data // . )
      | if type == "array" then
          to_entries
          | map(select(.value.name == "self-evolving-agent"))
          | if length > 0 then (.[0].key + 1 | tostring) + "위" else "순위권 외" end
        else "알 수 없음" end
    ' 2>/dev/null || echo "unknown")

    CH_STATUS="ok"
    echo "    ClawHub: 트렌딩 데이터 수신 완료" >&2
  elif [ -n "$CH_RAW" ]; then
    CH_STATUS="ok_no_jq"
    echo "    ClawHub: 응답 수신 (jq 없어 파싱 제한)" >&2
  else
    CH_STATUS="unavailable"
    echo "    ClawHub API 응답 없음 (미공개 API 또는 오프라인)" >&2
  fi
else
  CH_STATUS="timeout_skip"
  echo "    시간 초과 임박 ($(elapsed)초) — ClawHub skip" >&2
fi

# ═══════════════════════════════════════════════════════════
# 섹션 3: AGENTS.md 구조 분석
# ═══════════════════════════════════════════════════════════
echo "  [3/3] AGENTS.md 구조 분석..." >&2

AGENTS_STATUS="not_found"
AGENTS_LINES=0; AGENTS_CHARS=0; AGENTS_H2=0; AGENTS_H3=0
AGENTS_SCORE=0; AGENTS_SIZE_NOTE="파일 없음"
MISSING_SECTIONS="[]"; MISSING_PATTERNS="[]"; STRUCT_ISSUES="[]"

# ── 권장 섹션 및 패턴 ──────────────────────────────────────
REC_SECTIONS=("First Run" "Every Session" "Memory" "Safety" "Git Sync" "Exec" "Heartbeat")
REC_PATTERNS=("|| true" "WAL Protocol" "subagent" "|| echo" "set -")

# 누락 목록 배열 — 반드시 if 블록 밖에서 초기화 (-u 플래그 대응)
MISS_SEC=()
MISS_PAT=()
ISSUES_LIST=()
# 최소/최대 권장 줄 수
MIN_LINES=100; MAX_LINES=3000

if [ -f "$AGENTS_MD" ]; then
  AGENTS_STATUS="found"

  AGENTS_LINES=$(wc -l < "$AGENTS_MD" 2>/dev/null | tr -d ' ' || echo 0)
  AGENTS_CHARS=$(wc -c < "$AGENTS_MD" 2>/dev/null | tr -d ' ' || echo 0)
  AGENTS_H2=$(grep -c "^## " "$AGENTS_MD" 2>/dev/null || echo 0)
  AGENTS_H3=$(grep -c "^### " "$AGENTS_MD" 2>/dev/null || echo 0)

  # 크기 평가
  if   [ "$AGENTS_LINES" -lt "$MIN_LINES" ]; then
    AGENTS_SIZE_NOTE="경고: 너무 짧음 (${AGENTS_LINES}줄, 최소 ${MIN_LINES}줄 권장)"
    AGENTS_SCORE=$((AGENTS_SCORE - 20))
  elif [ "$AGENTS_LINES" -gt "$MAX_LINES" ]; then
    AGENTS_SIZE_NOTE="경고: 너무 긺 (${AGENTS_LINES}줄, 최대 ${MAX_LINES}줄 권장)"
    AGENTS_SCORE=$((AGENTS_SCORE - 10))
  else
    AGENTS_SIZE_NOTE="적정 (${AGENTS_LINES}줄)"
    AGENTS_SCORE=$((AGENTS_SCORE + 20))
  fi

  # 권장 섹션 존재 여부
  for sec in "${REC_SECTIONS[@]}"; do
    if grep -qi "$sec" "$AGENTS_MD" 2>/dev/null; then
      AGENTS_SCORE=$((AGENTS_SCORE + 5))
    else
      MISS_SEC+=("$sec")
      AGENTS_SCORE=$((AGENTS_SCORE - 3))
    fi
  done

  # 권장 패턴 존재 여부
  for pat in "${REC_PATTERNS[@]}"; do
    if grep -qF "$pat" "$AGENTS_MD" 2>/dev/null; then
      AGENTS_SCORE=$((AGENTS_SCORE + 3))
    else
      MISS_PAT+=("$pat")
    fi
  done

  # 점수 정규화 (0~100)
  [ "$AGENTS_SCORE" -lt 0   ] && AGENTS_SCORE=0   || true
  [ "$AGENTS_SCORE" -gt 100 ] && AGENTS_SCORE=100 || true

  # 누락 목록 → JSON 배열
  if [ ${#MISS_SEC[@]} -gt 0 ]; then
    MISSING_SECTIONS=$(printf '"%s",' "${MISS_SEC[@]}" | sed 's/,$//' | sed 's/^/[/;s/$/]/' || echo "[]")
  fi
  if [ ${#MISS_PAT[@]} -gt 0 ]; then
    MISSING_PATTERNS=$(printf '"%s",' "${MISS_PAT[@]}" | sed 's/,$//' | sed 's/^/[/;s/$/]/' || echo "[]")
  fi

  # 구조 이슈 종합
  echo "$AGENTS_SIZE_NOTE" | grep -q "경고" && ISSUES_LIST+=("\"$(je "$AGENTS_SIZE_NOTE")\"") || true
  for s in "${MISS_SEC[@]}"; do ISSUES_LIST+=("\"권장 섹션 누락: $(je "$s")\""); done

  if [ ${#ISSUES_LIST[@]} -gt 0 ]; then
    STRUCT_ISSUES=$(printf '%s,' "${ISSUES_LIST[@]}" | sed 's/,$//' | sed 's/^/[/;s/$/]/' || echo "[]")
  fi

  echo "    AGENTS.md: ${AGENTS_LINES}줄 / H2: ${AGENTS_H2}개 / 구조점수: ${AGENTS_SCORE}/100" >&2
fi

# ── 점수 레이블 ─────────────────────────────────────────────
if   [ "$AGENTS_SCORE" -ge 70 ]; then SCORE_LABEL="양호"
elif [ "$AGENTS_SCORE" -ge 40 ]; then SCORE_LABEL="보통"
else SCORE_LABEL="개선 필요"
fi

# ═══════════════════════════════════════════════════════════
# 최종 JSON 출력
# ═══════════════════════════════════════════════════════════
ELAPSED=$(elapsed)
echo "  → benchmarks.json 작성 중 (총 ${ELAPSED}초)..." >&2

cat > "$OUTPUT_FILE" <<BMBODY
{
  "generated_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "elapsed_seconds": $ELAPSED,
  "github": {
    "status": "$GH_STATUS",
    "latest_release": "$(je "$GH_TAG")",
    "tag": "$(je "$GH_TAG")",
    "release_date": "$(je "$GH_DATE")",
    "url": "$(je "$GH_URL")",
    "breaking_changes": $GH_BREAKING,
    "new_features": $GH_FEATURES
  },
  "clawhub": {
    "status": "$CH_STATUS",
    "sea_rank": "$(je "$CH_SEA_RANK")",
    "trending_skills": $CH_TRENDING
  },
  "agents_md": {
    "status": "$AGENTS_STATUS",
    "lines": $AGENTS_LINES,
    "chars": $AGENTS_CHARS,
    "h2_sections": $AGENTS_H2,
    "h3_subsections": $AGENTS_H3,
    "size_assessment": "$(je "$AGENTS_SIZE_NOTE")",
    "structure_score": $AGENTS_SCORE,
    "score_label": "$SCORE_LABEL",
    "missing_sections": $MISSING_SECTIONS,
    "missing_patterns": $MISSING_PATTERNS
  },
  "structure_issues": $STRUCT_ISSUES,
  "summary": {
    "github_ok": $([ "$GH_STATUS" = "ok" ] || [ "$GH_STATUS" = "ok_no_jq" ] && echo "true" || echo "false"),
    "clawhub_ok": $([ "$CH_STATUS" = "ok" ] && echo "true" || echo "false"),
    "agents_score": $AGENTS_SCORE,
    "issues_count": ${#ISSUES_LIST[@]},
    "fast_enough": $([ "$ELAPSED" -lt 30 ] && echo "true" || echo "false")
  }
}
BMBODY

echo "✅ [benchmark] 완료 → $OUTPUT_FILE (${ELAPSED}초)" >&2
cat "$OUTPUT_FILE"
