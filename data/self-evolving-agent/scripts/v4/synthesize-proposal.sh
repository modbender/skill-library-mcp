#!/usr/bin/env bash
# ============================================================
# synthesize-proposal.sh — Self-Evolving Agent v4.2 최종 제안서 합성기
#
# 역할 (명세서 v4.2):
#   중간 데이터를 모두 읽어 최종 마크다운 제안서를 생성한다.
#   LLM이 설정되어 있으면 (anthropic/openai/ollama) 제안 품질을
#   AI로 강화한다. none 설정이면 순수 휴리스틱으로만 동작.
#
# 입력:
#   /tmp/sea-v4/analysis.json   (analyze-behavior.sh 또는 semantic-analyze.sh 출력)
#   /tmp/sea-v4/benchmarks.json (benchmark.sh 출력)
#   /tmp/sea-v4/effects.json    (measure-effects.sh 출력)
#   ~/openclaw/AGENTS.md        (현재 에이전트 설정)
#
# 출력 구조 (명세서 필수):
#   📊 Effect Report  — 과거 제안이 효과 있었는가?
#   🔍 New Findings   — 이번 주 분석 결과
#   💡 Proposals      — severity + evidence + before/after diff + expected impact
#   🤖 LLM Enrichment — AI 강화 제안 (LLM 설정 시에만)
#   📈 Quality Trend  — 품질 추세
#
# 출력:
#   /tmp/sea-v4/proposal.md (파일 저장 + stdout 출력)
#
# 사용법:
#   bash synthesize-proposal.sh [--dry-run] [--no-llm]
# ============================================================

# SECURITY MANIFEST:
# Environment variables accessed: SEA_TMP_DIR, DRY_RUN, LLM_PROVIDER, LLM_MODEL
# External endpoints called:
#   anthropic/openai (via llm-call.sh, only if configured and not --no-llm)
#   ollama localhost (via llm-call.sh, only if configured and not --no-llm)
# Local files read:
#   /tmp/sea-v4/analysis.json    (from semantic-analyze.sh or analyze-behavior.sh)
#   /tmp/sea-v4/benchmarks.json  (from benchmark.sh)
#   /tmp/sea-v4/effects.json     (from measure-effects.sh)
#   ~/openclaw/AGENTS.md         (last-modified timestamp and metadata)
#   <skill_dir>/config.yaml      (LLM provider 설정)
# Local files written:
#   <SEA_TMP_DIR>/proposal.md  (default: /tmp/sea-v4/proposal.md)
#   Also written to stdout (tee).
# Network: Conditional (see above)

# -e 제외: 데이터 누락 시에도 계속 진행
set -o pipefail  # -u 제거: bash 3.2 empty array 호환

# ── 경로 설정 ──────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
LLM_CALL_SH="${SCRIPT_DIR}/llm-call.sh"

AGENTS_MD="${HOME}/openclaw/AGENTS.md"
TMP_DIR="${SEA_TMP_DIR:-/tmp/sea-v4}"
ANALYSIS_FILE="$TMP_DIR/analysis.json"
BENCHMARKS_FILE="$TMP_DIR/benchmarks.json"
EFFECTS_FILE="$TMP_DIR/effects.json"
OUTPUT_FILE="$TMP_DIR/proposal.md"

# 옵션
DRY_RUN=false
NO_LLM=false
for arg in "$@"; do
  [ "$arg" = "--dry-run" ] && DRY_RUN=true || true
  [ "$arg" = "--no-llm"  ] && NO_LLM=true  || true
done

# DRY_RUN=true면 LLM 호출 생략
[ "$DRY_RUN" = "true" ] && NO_LLM=true || true

mkdir -p "$TMP_DIR" || true
echo "📝 [synthesize-proposal] 제안서 합성 시작" >&2

# ── LLM 제공자 감지 ────────────────────────────────────────
# config.yaml에서 읽거나 환경변수로 오버라이드 가능
_SEA_LLM_PROVIDER=""
if [ "$NO_LLM" = "false" ] && [ -f "${SKILL_DIR}/config.yaml" ]; then
  _SEA_LLM_PROVIDER=$(python3 -c "
import sys, re
try:
    with open('${SKILL_DIR}/config.yaml', 'r') as f:
        content = f.read()
    try:
        import yaml
        cfg = yaml.safe_load(content)
        print(cfg.get('llm', {}).get('provider', 'none'))
    except ImportError:
        m = re.search(r'^\s*provider:\s*[\"\'']?(\w+)[\"\'']?', content, re.MULTILINE)
        print(m.group(1) if m else 'none')
except Exception:
    print('none')
" 2>/dev/null || echo "none")
fi

# 환경변수 우선
_SEA_LLM_PROVIDER="${LLM_PROVIDER:-${_SEA_LLM_PROVIDER:-none}}"
[ "$NO_LLM" = "true" ] && _SEA_LLM_PROVIDER="none" || true

echo "  → LLM 제공자: ${_SEA_LLM_PROVIDER}" >&2

# ── 헬퍼 ───────────────────────────────────────────────────
HAS_JQ=false; command -v jq &>/dev/null && HAS_JQ=true || true

# JSON 안전 이스케이프
je() { local s="$1"; s="${s//\\/\\\\}"; s="${s//\"/\\\"}"; s="${s//$'\n'/ }"; s="${s//$'\t'/ }"; printf '%s' "$s"; }

# jq 안전 쿼리 (파일 없거나 jq 없으면 default 반환)
jqs() {
  local file="$1" query="$2" default="${3:-}"
  $HAS_JQ && [ -f "$file" ] && jq -r "$query // \"$default\"" "$file" 2>/dev/null || echo "$default"
}

# 파일 존재 확인 (없으면 경고만)
chk() { [ -f "$1" ] || echo "  ⚠️  $2 없음: $1 (기본값 사용)" >&2; }

# ── 입력 파일 확인 ──────────────────────────────────────────
echo "  → 입력 파일 확인..." >&2
chk "$ANALYSIS_FILE"   "analysis.json"
chk "$BENCHMARKS_FILE" "benchmarks.json"
chk "$EFFECTS_FILE"    "effects.json"

# ═══════════════════════════════════════════════════════════
# 데이터 추출: effects.json
# ═══════════════════════════════════════════════════════════
echo "  → effects.json 읽는 중..." >&2

EFF_EFFECTIVE=$(jqs "$EFFECTS_FILE" '.effective_count'          "0")
EFF_INEFFECTIVE=$(jqs "$EFFECTS_FILE" '.ineffective_count'      "0")
EFF_TOTAL=$(jqs "$EFFECTS_FILE" '.total_proposal_files'         "0")
EFF_OVERALL=$(jqs "$EFFECTS_FILE" '.overall_improvement'        "측정 불가")
EFF_REJECTED=$(jqs "$EFFECTS_FILE" '.rejected_count'            "0")
EFF_Q_PREV=$(jqs "$EFFECTS_FILE" '.quality_trend.prev_week'     "null")
EFF_Q_THIS=$(jqs "$EFFECTS_FILE" '.quality_trend.this_week'     "null")
EFF_Q_SUM=$(jqs "$EFFECTS_FILE"  '.quality_trend.summary'       "측정 불가")

# 효과 측정 테이블 행 (있을 때만)
EFF_TABLE_ROWS=""
if $HAS_JQ && [ -f "$EFFECTS_FILE" ]; then
  EFF_TABLE_ROWS=$(jq -r '
    .applied_proposals[]?
    | "| `\(.id // "?")` | \((.date // "?")[:10]) | \((.description // "?")[:45]) | \(.pattern_before) → \(.pattern_after) | \(if .effective == true then "✅ 효과" elif .effective == false then "❌ 미효과" else "❓ 측정불가" end) |"
  ' "$EFFECTS_FILE" 2>/dev/null | head -15 || echo "")
fi

# 비효과적 제안 목록
EFF_INEFF_LIST=""
if $HAS_JQ && [ -f "$EFFECTS_FILE" ]; then
  EFF_INEFF_LIST=$(jq -r '
    .ineffective_proposals[]?
    | "- **`\(.id // "?")`**: \((.description // "?")[:55]) (before:\(.pattern_before), after:\(.pattern_after))"
  ' "$EFFECTS_FILE" 2>/dev/null | head -8 || echo "")
fi

# ═══════════════════════════════════════════════════════════
# 데이터 추출: analysis.json
# ═══════════════════════════════════════════════════════════
echo "  → analysis.json 읽는 중..." >&2

# v3 (analyze-behavior.sh) 및 v4 (semantic-analyze.sh) 양쪽 필드 지원
ANA_SESSIONS=$(jqs "$ANALYSIS_FILE"  '.sessions_analyzed // .analysis_summary.session_count // .summary.sessions_analyzed' "0")
ANA_RETRIES=$(jqs "$ANALYSIS_FILE"   '.exec_loops.total_events // .analysis_summary.retry_events // .summary.exec_retries' "0")
ANA_COMPLAINTS=$(jqs "$ANALYSIS_FILE" '.frustration_events | length // .analysis_summary.total_complaint_hits // .summary.complaint_hits' "0")
ANA_HEAVY=$(jqs "$ANALYSIS_FILE"     '.failure_patterns | map(select(.type=="overloaded_session")) | length // .analysis_summary.heavy_sessions // .summary.heavy_sessions' "0")
ANA_TIMESTAMP=$(jqs "$ANALYSIS_FILE" '.generated_at // .timestamp'     "$(date -u +"%Y-%m-%dT%H:%M:%SZ")")
ANA_PROP_COUNT=0

if $HAS_JQ && [ -f "$ANALYSIS_FILE" ]; then
  ANA_PROP_COUNT=$(jq -r '.proposals | length' "$ANALYSIS_FILE" 2>/dev/null || echo 0)
fi

# ═══════════════════════════════════════════════════════════
# 데이터 추출: benchmarks.json
# ═══════════════════════════════════════════════════════════
echo "  → benchmarks.json 읽는 중..." >&2

BM_GH_STATUS=$(jqs "$BENCHMARKS_FILE" '.github.status'               "unknown")
BM_GH_TAG=$(jqs "$BENCHMARKS_FILE"    '.github.tag'                  "unknown")
BM_GH_DATE=$(jqs "$BENCHMARKS_FILE"   '.github.release_date'         "unknown")
BM_GH_URL=$(jqs "$BENCHMARKS_FILE"    '.github.url'                  "")
BM_CH_STATUS=$(jqs "$BENCHMARKS_FILE" '.clawhub.status'              "unknown")
BM_CH_RANK=$(jqs "$BENCHMARKS_FILE"   '.clawhub.sea_rank'            "unknown")
BM_AG_LINES=$(jqs "$BENCHMARKS_FILE"  '.agents_md.lines'             "0")
BM_AG_H2=$(jqs "$BENCHMARKS_FILE"     '.agents_md.h2_sections'       "0")
BM_AG_SCORE=$(jqs "$BENCHMARKS_FILE"  '.agents_md.structure_score'   "0")
BM_AG_SIZE=$(jqs "$BENCHMARKS_FILE"   '.agents_md.size_assessment'   "unknown")
BM_AG_LABEL=$(jqs "$BENCHMARKS_FILE"  '.agents_md.score_label'       "unknown")
BM_ELAPSED=$(jqs "$BENCHMARKS_FILE"   '.elapsed_seconds'             "?")

BM_BREAKING=""; BM_FEATURES=""; BM_MISS_SEC=""
if $HAS_JQ && [ -f "$BENCHMARKS_FILE" ]; then
  BM_BREAKING=$(jq -r '.github.breaking_changes[]? | "- \(.)"' "$BENCHMARKS_FILE" 2>/dev/null || echo "")
  BM_FEATURES=$(jq -r  '.github.new_features[]?    | "- \(.)"' "$BENCHMARKS_FILE" 2>/dev/null || echo "")
  BM_MISS_SEC=$(jq -r  '.agents_md.missing_sections[]? | "- \(.)"' "$BENCHMARKS_FILE" 2>/dev/null || echo "")
fi

# ═══════════════════════════════════════════════════════════
# AGENTS.md 메타정보
# ═══════════════════════════════════════════════════════════
AGENTS_UPDATED="unknown"
if [ -f "$AGENTS_MD" ]; then
  AGENTS_UPDATED=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M" "$AGENTS_MD" 2>/dev/null \
    || stat -c "%y" "$AGENTS_MD" 2>/dev/null | cut -c1-16 \
    || echo "unknown")
fi

# ═══════════════════════════════════════════════════════════
# 제안 블록 생성 함수 (명세서 필수 항목 포함)
# ═══════════════════════════════════════════════════════════
gen_proposal_block() {
  local idx="$1" pid="$2" title="$3" severity="$4"
  local evidence="$5" before="$6" after="$7"
  local section="${8:-AGENTS.md 일반}" diff_type="${9:-agents_md_addition}"

  # severity 이모지
  local sev_icon="🟡"
  case "$severity" in
    critical|high) sev_icon="🔴" ;;
    medium)        sev_icon="🟡" ;;
    low)           sev_icon="🟢" ;;
  esac

  # diff_type 레이블
  local diff_label
  case "$diff_type" in
    agents_md_addition) diff_label="AGENTS.md 추가"  ;;
    agents_md_update)   diff_label="AGENTS.md 수정"  ;;
    agents_md_removal)  diff_label="AGENTS.md 삭제"  ;;
    config_change)      diff_label="설정 변경"        ;;
    script_change)      diff_label="스크립트 변경"    ;;
    *)                  diff_label="규칙 변경"         ;;
  esac

  # expected impact (severity 기반)
  local impact
  case "$severity" in
    critical|high) impact="높음 — 즉시 적용 권장" ;;
    medium)        impact="보통 — 이번 주 내 적용 권장" ;;
    low)           impact="낮음 — 편의성 개선" ;;
    *)             impact="unknown" ;;
  esac

  cat <<BLOCK

### 💡 제안 ${idx}: ${title}

| 항목 | 내용 |
|------|------|
| **ID** | \`${pid}\` |
| **심각도** | ${sev_icon} ${severity} |
| **대상 섹션** | ${section} |
| **변경 유형** | ${diff_label} |
| **예상 효과** | ${impact} |

**📋 근거 (Evidence):**

\`\`\`
${evidence}
\`\`\`

**🔴 Before (현재 상태):**

\`\`\`
${before}
\`\`\`

**🟢 After (적용 시 변경):**

\`\`\`
${after}
\`\`\`

---
BLOCK
}

# ═══════════════════════════════════════════════════════════
# 타임스탬프
# ═══════════════════════════════════════════════════════════
NOW_KST=$(TZ="Asia/Seoul" date "+%Y-%m-%d %H:%M KST" 2>/dev/null || date "+%Y-%m-%d %H:%M")

echo "  → 마크다운 제안서 생성 중 (제안 ${ANA_PROP_COUNT}개)..." >&2

# ═══════════════════════════════════════════════════════════
# 본문 생성 (tee로 파일 + stdout 동시 출력)
# ═══════════════════════════════════════════════════════════
{

# ── 헤더 ────────────────────────────────────────────────────
cat <<HDR
# 🤖 Self-Evolving Agent v4.0 — 주간 제안서

> **생성**: ${NOW_KST}  
> **분석 세션**: ${ANA_SESSIONS}개 | **총 제안**: ${ANA_PROP_COUNT}개  
> **분석 기준**: ${ANA_TIMESTAMP}

---

## 📊 Effect Report — 과거 제안 효과 측정

> 지난주 적용 제안들이 실제로 효과가 있었는가?

| 지표 | 값 |
|------|----|
| 분석한 제안 파일 | ${EFF_TOTAL}개 |
| ✅ 효과 있음 | ${EFF_EFFECTIVE}개 |
| ❌ 효과 없음 | ${EFF_INEFFECTIVE}개 |
| 🚫 거절됨 | ${EFF_REJECTED}개 |
| **전체 개선율** | **${EFF_OVERALL}** |

HDR

# 효과 측정 테이블
if [ -n "$EFF_TABLE_ROWS" ]; then
cat <<ETABLE
### 제안별 효과 측정 결과

| ID | 날짜 | 설명 | 패턴 변화 | 판정 |
|----|------|------|-----------|------|
${EFF_TABLE_ROWS}

ETABLE
else
echo "> 📝 *측정할 과거 제안 없음 또는 로그 데이터 부족*"
echo "> (다음 주부터 이번 주 제안들이 자동 측정됩니다)"
echo ""
fi

# 비효과 목록
if [ -n "$EFF_INEFF_LIST" ]; then
cat <<INEFF

### ❌ 효과 없었던 제안 (재검토 권장)

${EFF_INEFF_LIST}

> 💡 *재설계하거나 다른 접근법으로 대체 고려*

INEFF
fi

# ── 벤치마크 섹션 ────────────────────────────────────────────
cat <<BM_HDR

---

## 🏷️ Benchmark — 외부 기준점 (${BM_ELAPSED}초 소요)

### OpenClaw GitHub 릴리스

BM_HDR

case "$BM_GH_STATUS" in
  ok|ok_no_jq)
cat <<GH_OK
| 항목 | 값 |
|------|----|
| 최신 릴리스 | \`${BM_GH_TAG}\` |
| 릴리스 날짜 | ${BM_GH_DATE} |
$([ -n "$BM_GH_URL" ] && echo "| URL | <${BM_GH_URL}> |" || true)

GH_OK
    [ -n "$BM_BREAKING" ] && printf '**⚠️ Breaking Changes:**\n\n%s\n\n' "$BM_BREAKING" || true
    [ -n "$BM_FEATURES" ] && printf '**✨ New Features:**\n\n%s\n\n' "$BM_FEATURES" || true
    ;;
  *)
    echo "> ℹ️ *GitHub API 응답 없음 (오프라인 / 비공개 레포) — skip*"
    echo ""
    ;;
esac

cat <<CH_HDR
### ClawHub Trending Skills

CH_HDR
case "$BM_CH_STATUS" in
  ok)
    echo "> 📈 트렌딩 데이터 수신 완료"
    echo ">"
    [ "$BM_CH_RANK" != "unknown" ] && echo "> self-evolving-agent 현재 순위: **${BM_CH_RANK}**" || true
    echo ""
    ;;
  *)
    echo "> ℹ️ *ClawHub API 응답 없음 — skip (정상, API 미공개)*"
    echo ""
    ;;
esac

cat <<AGENTS_BM
### AGENTS.md 구조 평가

| 항목 | 값 | 상태 |
|------|----|------|
| 줄 수 | ${BM_AG_LINES}줄 | ${BM_AG_SIZE} |
| H2 섹션 | ${BM_AG_H2}개 | — |
| 구조 점수 | ${BM_AG_SCORE}/100 | ${BM_AG_LABEL} |
| 마지막 수정 | ${AGENTS_UPDATED} | — |

AGENTS_BM

[ -n "$BM_MISS_SEC" ] && printf '**누락된 권장 섹션:**\n\n%s\n\n' "$BM_MISS_SEC" || true

# ── New Findings 섹션 ────────────────────────────────────────
cat <<FINDINGS

---

## 🔍 New Findings — 이번 주 분석 결과

| 지표 | 값 | 해석 |
|------|----|------|
| 분석 세션 수 | **${ANA_SESSIONS}개** | — |
| exec 재시도 이벤트 | **${ANA_RETRIES}건** | $([ "${ANA_RETRIES:-0}" -gt 50 ] && echo "🔴 높음" || [ "${ANA_RETRIES:-0}" -gt 20 ] && echo "🟡 보통" || echo "🟢 양호") |
| 사용자 불만 패턴 | **${ANA_COMPLAINTS}건** | $([ "${ANA_COMPLAINTS:-0}" -gt 10 ] && echo "🔴 높음" || [ "${ANA_COMPLAINTS:-0}" -gt 3 ] && echo "🟡 보통" || echo "🟢 양호") |
| 과부하 세션 | **${ANA_HEAVY}개** | $([ "${ANA_HEAVY:-0}" -gt 5 ] && echo "🔴 많음" || [ "${ANA_HEAVY:-0}" -gt 1 ] && echo "🟡 보통" || echo "🟢 양호") |

FINDINGS

# ── Proposals 섹션 ──────────────────────────────────────────
cat <<PROP_HDR

---

## 💡 Proposals — 개선 제안

> ⚠️ 각 제안: **severity** / **evidence** / **before-after diff** / **expected impact** 포함

PROP_HDR

PROP_COUNT=0
if $HAS_JQ && [ -f "$ANALYSIS_FILE" ] && [ "$ANA_PROP_COUNT" -gt 0 ]; then
  while IFS= read -r prop_json; do
    PROP_COUNT=$((PROP_COUNT + 1))

    pid=$(echo "$prop_json"      | jq -r '.id       // "unknown"'   2>/dev/null || echo "unknown")
    title=$(echo "$prop_json"    | jq -r '.title    // "제목 없음"'  2>/dev/null || echo "제목 없음")
    severity=$(echo "$prop_json" | jq -r '.severity // .priority // "medium"' 2>/dev/null || echo "medium")
    evidence=$(echo "$prop_json" | jq -r '.evidence // "근거 없음"'  2>/dev/null || echo "근거 없음")
    # before/after: 직접 필드 우선, 없으면 description/implementation에서 파생
    before=$(echo "$prop_json"   | jq -r '.before   // .current_state // "현재 상태 미제공"' 2>/dev/null || echo "현재 상태 미제공")
    after=$(echo "$prop_json"    | jq -r '.after    // .implementation // .proposed_state // "제안 내용 미제공"' 2>/dev/null || echo "제안 내용 미제공")
    section=$(echo "$prop_json"  | jq -r '.section  // .category // "AGENTS.md 일반"' 2>/dev/null || echo "AGENTS.md 일반")
    diff_type=$(echo "$prop_json"| jq -r '.diff_type // "agents_md_addition"' 2>/dev/null || echo "agents_md_addition")

    gen_proposal_block \
      "$PROP_COUNT" "$pid" "$title" "$severity" \
      "$evidence" "$before" "$after" "$section" "$diff_type"

  done < <(jq -c '.proposals[]?' "$ANALYSIS_FILE" 2>/dev/null | head -10 || true)
fi

if [ "$PROP_COUNT" -eq 0 ]; then
  echo "> ✅ *이번 주 새 제안 없음* — 에이전트 동작 안정적"
  echo ""
  echo "> analysis.json이 필요합니다:"
  echo "> \`\`\`bash"
  echo "> bash ~/openclaw/skills/self-evolving-agent/scripts/analyze-behavior.sh"
  echo "> \`\`\`"
  echo ""
fi

# ── LLM 강화 제안 (선택적) ───────────────────────────────────
# LLM 제공자가 none이 아니면 분석 데이터를 LLM에 전달해 제안을 강화한다.
if [ "${_SEA_LLM_PROVIDER}" != "none" ] && [ -f "$LLM_CALL_SH" ] && [ -f "$ANALYSIS_FILE" ]; then

  cat <<LLM_HDR

---

## 🤖 LLM 강화 제안 (${_SEA_LLM_PROVIDER})

> AI가 분석 데이터를 재해석한 추가 인사이트입니다.  
> 휴리스틱 분석의 맹점을 보완합니다.

LLM_HDR

  # 분석 요약 추출 (LLM 프롬프트용)
  _ANA_SUMMARY=""
  if $HAS_JQ && [ -f "$ANALYSIS_FILE" ]; then
    _ANA_SUMMARY=$(jq -r '{
      sessions: .sessions_analyzed,
      quality: .quality_score,
      insights: (.key_insights // [] | .[0:5]),
      top_frustration: (.frustration_events // [] | .[0:3] | map({pattern, severity, context})),
      exec_loops: (.exec_loops // [] | .[0:3] | map({command_base, count})),
      violations: (.rule_violations // [] | .[0:3] | map({rule, violation, count}))
    }' "$ANALYSIS_FILE" 2>/dev/null || echo '{}')
  fi

  # LLM 프롬프트 구성 + 호출
  _LLM_PROMPT="You are reviewing a self-evolving AI agent's weekly behavior analysis.
Based on the following structured data, provide 2-3 specific, actionable improvement proposals.

For each proposal:
1. State the problem clearly (1 sentence)
2. Give the evidence from the data (cite numbers)
3. Provide a concrete rule to add/modify in AGENTS.md (before/after format)
4. Estimate impact (high/medium/low)

Analysis data:
${_ANA_SUMMARY}

Format your response as clean markdown with ### headers for each proposal.
Be specific and evidence-based. No vague suggestions."

  _LLM_RESPONSE=""
  _LLM_RESPONSE=$(echo "$_LLM_PROMPT" | bash "$LLM_CALL_SH" \
    --provider "${_SEA_LLM_PROVIDER}" \
    --system "You are an expert AI behavior analyst. Generate specific, evidence-based AGENTS.md improvement proposals." \
    2>/tmp/sea-v4/llm-call.log) || {
    echo "> ⚠️ *LLM 호출 실패 — 휴리스틱 결과만 사용*" 
    echo "> 오류 상세: \`cat /tmp/sea-v4/llm-call.log\`"
    echo ""
  }

  if [ -n "$_LLM_RESPONSE" ] && [ "$_LLM_RESPONSE" != "{}" ]; then
    echo "$_LLM_RESPONSE"
    echo ""
    echo "> 💡 *LLM 제공자: ${_SEA_LLM_PROVIDER} | 위 제안은 AI 생성 — 적용 전 검토 필수*"
  else
    echo "> ℹ️ *LLM 응답 없음 또는 빈 응답 — provider=${_SEA_LLM_PROVIDER}*"
  fi
  echo ""
fi

# 벤치마크 기반 추가 제안 (구조 점수 낮을 때)
if [ "${BM_AG_SCORE:-100}" -lt 70 ] && [ -n "$BM_MISS_SEC" ]; then
  PROP_COUNT=$((PROP_COUNT + 1))
  gen_proposal_block \
    "${PROP_COUNT}" \
    "agents-structure-bm" \
    "AGENTS.md 구조 개선 (벤치마크 권장)" \
    "medium" \
    "벤치마크 구조 점수: ${BM_AG_SCORE}/100\n누락 섹션:\n${BM_MISS_SEC}" \
    "AGENTS.md에 일부 권장 섹션 누락" \
    "아래 섹션 추가:\n${BM_MISS_SEC}" \
    "AGENTS.md 전반" \
    "agents_md_addition"
fi

# ── Quality Trend 섹션 ────────────────────────────────────────
cat <<QT_HDR

---

## 📈 Quality Trend — 품질 추세

QT_HDR

if [ "$EFF_Q_PREV" != "null" ] && [ "$EFF_Q_PREV" != "" ] \
   && [ "$EFF_Q_THIS" != "null" ] && [ "$EFF_Q_THIS" != "" ]; then

  QDELTA=""
  command -v bc &>/dev/null && QDELTA=$(echo "$EFF_Q_THIS - $EFF_Q_PREV" | bc 2>/dev/null || echo "") || true

  if echo "${QDELTA:-0}" | grep -q "^-"; then
    QARROW="📉 하락"; QCOLOR="🔴"
  elif [ -z "${QDELTA}" ] || echo "${QDELTA}" | grep -q "^0"; then
    QARROW="➡️ 유지"; QCOLOR="🟡"
  else
    QARROW="📈 상승"; QCOLOR="🟢"
  fi

cat <<QT_DATA
| 기간 | 품질 점수 |
|------|---------|
| 지난 주 | ${EFF_Q_PREV} |
| 이번 주 | ${EFF_Q_THIS} |
| **변화** | **${QCOLOR} ${QDELTA:+${QDELTA}} (${QARROW})** |

> ${EFF_Q_SUM}

QT_DATA
else
cat <<QT_NA
> 📝 *품질 점수 데이터 없음 (self-review 데이터 필요)*
>
> \`\`\`bash
> bash ~/openclaw/scripts/self-review-logger.sh [크론명] [점수] [...]
> \`\`\`

QT_NA
fi

# ── 요약 푸터 ────────────────────────────────────────────────
HIGH_COUNT=$(jqs "$ANALYSIS_FILE" '[.proposals[]? | select(.severity=="high" or .severity=="critical")] | length' "?")
MED_COUNT=$(jqs  "$ANALYSIS_FILE" '[.proposals[]? | select(.severity=="medium")] | length' "?")
LOW_COUNT=$(jqs  "$ANALYSIS_FILE" '[.proposals[]? | select(.severity=="low")] | length'    "?")

cat <<FOOTER

---

## 📋 요약 및 다음 단계

| 항목 | 값 |
|------|----|
| 총 제안 수 | **${PROP_COUNT}개** |
| 🔴 즉시 적용 (high/critical) | **${HIGH_COUNT}개** |
| 🟡 이번 주 내 (medium) | **${MED_COUNT}개** |
| 🟢 편의 개선 (low) | **${LOW_COUNT}개** |
| 전체 개선 효과 | **${EFF_OVERALL}** |
| AGENTS.md 구조 점수 | **${BM_AG_SCORE}/100 (${BM_AG_LABEL})** |

### ✅ 적용 절차

1. **제안 검토** — 각 제안의 before/after 확인
2. **승인 선택** — severity 높은 것부터
3. **AGENTS.md 수정** — after 내용 반영
4. **상태 업데이트** — proposals/ 파일 \`status: "applied"\`로 변경
5. **다음 주 효과 측정** — measure-effects.sh가 자동 검증

---

*generated by self-evolving-agent v4.2 synthesize-proposal.sh — ${NOW_KST} | LLM: ${_SEA_LLM_PROVIDER}*
$([ "$DRY_RUN" = "true" ] && echo "*[DRY RUN 모드 — LLM 호출 없음]*" || true)
FOOTER

} | tee "$OUTPUT_FILE"

# ── Discord 리액션 지시 푸터 추가 ──────────────────────────
INTERACTIVE_APPROVE="${SKILL_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}/scripts/v4/interactive-approve.sh"
if [ -f "$INTERACTIVE_APPROVE" ]; then
  bash "$INTERACTIVE_APPROVE" --discord-footer >> "$OUTPUT_FILE" 2>/dev/null || true
fi

# ── 완료 ────────────────────────────────────────────────────
OUTLINES=$(wc -l < "$OUTPUT_FILE" 2>/dev/null | tr -d ' ' || echo "?")
echo "" >&2
echo "✅ [synthesize-proposal] 완료" >&2
echo "   출력: $OUTPUT_FILE (${OUTLINES}줄)" >&2
