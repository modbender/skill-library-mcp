#!/usr/bin/env bash
# ============================================================
# orchestrator-v5.sh — Self-Evolving Agent v5.0 메인 오케스트레이터
#
# v4 대비 변경점:
#   Stage 2: semantic-analyze.sh → embedding-analyze.sh
#            (Ollama 시맨틱 임베딩 분석, 키워드 매칭 대체)
#
# 폴백 체인:
#   embedding-analyze.sh 실패 → v4 semantic-analyze.sh 자동 폴백
#   Ollama 없음              → OpenAI 또는 v4 휴리스틱으로 폴백
#
# 나머지 스테이지 (Stage 1, 3, 4, 5)는 v4 스크립트 재사용.
# 완전한 하위 호환성 유지 (v4 analysis.json 형식 호환).
#
# 사용법:
#   bash scripts/v5/orchestrator-v5.sh
#   DRY_RUN=true bash scripts/v5/orchestrator-v5.sh   # LLM 없이 테스트
#   VERBOSE=true bash scripts/v5/orchestrator-v5.sh   # 상세 로그
#   EMBED_MODEL=nomic-embed-text bash scripts/v5/orchestrator-v5.sh
#
# 환경변수:
#   OLLAMA_URL           Ollama 서버 주소 (기본: http://localhost:11434)
#   EMBED_MODEL          임베딩 모델 (기본: nomic-embed-text)
#   SIMILARITY_THRESHOLD 좌절 감지 임계값 (기본: 0.75)
#   SEA_TMP_DIR          임시 파일 저장 위치 (기본: /tmp/sea-v5)
#   DRY_RUN              true면 LLM 호출 없이 테스트
#   VERBOSE              true면 상세 로그 출력
#   MAX_SESSIONS         분석할 최대 세션 수 (기본: 30)
#   COLLECT_DAYS         수집 기간 일수 (기본: 7)
#
# 성능 목표: Ollama 실행 중 30개 세션 < 60초
#
# 변경 이력:
#   v5.0 (2026-02-18) — 시맨틱 임베딩 분석 (embedding-analyze.sh)
#   v4.0 (2026-02-17) — 초기 구현
# ============================================================

# SECURITY MANIFEST:
# (v4 manifest와 동일 + 아래 추가)
# External endpoints called:
#   localhost:11434/api/embeddings  (Ollama, local only)
#   localhost:11434/api/tags        (Ollama health check, local only)
#   api.openai.com/v1/embeddings    (OpenAI fallback, only if OPENAI_API_KEY set)
# Local files read: (v4와 동일 +)
#   /tmp/sea-v5/embedding-cache.json  (임베딩 캐시)
#   <SKILL_DIR>/data/embeddings/frustration-vectors.json  (좌절 패턴 벡터)
# Local files written: (v4와 동일, 경로만 /tmp/sea-v5/로 변경)

set -euo pipefail

# ── 에러 카운터 ─────────────────────────────────────────────
_ORCH_ERRS=0
trap '_ORCH_ERRS=$(( _ORCH_ERRS + 1 ))' ERR

# ── 전역 설정 ──────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
V4_SCRIPT_DIR="${SKILL_DIR}/scripts/v4"

# v5는 /tmp/sea-v5/ 사용 (v4와 분리)
TMP_DIR="${SEA_TMP_DIR:-/tmp/sea-v5}"
VERBOSE="${VERBOSE:-false}"
DRY_RUN="${DRY_RUN:-false}"
MAX_SESSIONS="${MAX_SESSIONS:-30}"
COLLECT_DAYS="${COLLECT_DAYS:-7}"
WORKSPACE="${WORKSPACE:-$HOME/openclaw}"

# v5 전용 설정
OLLAMA_URL="${OLLAMA_URL:-http://localhost:11434}"
EMBED_MODEL="${EMBED_MODEL:-nomic-embed-text}"
SIMILARITY_THRESHOLD="${SIMILARITY_THRESHOLD:-0.75}"

# Stage 2에서 v4 로그를 참조 (collect-logs.sh는 v4 버전 재사용)
# v4 logs.json → v5 분석에 입력
V4_TMP_DIR="/tmp/sea-v4"

# ── config.yaml 검증 ────────────────────────────────────────
if [[ -f "$SKILL_DIR/scripts/validate-config.sh" ]]; then
  bash "$SKILL_DIR/scripts/validate-config.sh" --quiet 2>/dev/null || {
    echo "⚠️  Config 검증 실패 — 기본값으로 계속" >&2
  }
fi 2>/dev/null || true

# ── config.yaml 로딩 ────────────────────────────────────────
_CONFIG_LOADER="${SKILL_DIR}/scripts/lib/config-loader.sh"
if [[ -f "$_CONFIG_LOADER" ]]; then
  source "$_CONFIG_LOADER" 2>/dev/null || true
  sea_load_config 2>/dev/null || true

  # config.yaml의 v5 설정 반영
  COLLECT_DAYS="${COLLECT_DAYS:-${SEA_DAYS:-7}}"
  MAX_SESSIONS="${MAX_SESSIONS:-${SEA_MAX_SESSIONS:-30}}"

  # config.yaml analysis.embedding 섹션에서 v5 설정 로드
  _CFG="${SKILL_DIR}/config.yaml"
  if [[ -f "$_CFG" ]]; then
    _OLLAMA_MODEL=$(python3 -c "
import sys
try:
    content = open('$_CFG').read()
    # analysis.embedding.model 파싱
    import re
    m = re.search(r'embedding:\s*\n(?:[^\n]*\n)*?\s*model:\s*[\"']?([^\"'\n]+)[\"']?', content)
    if m: print(m.group(1).strip())
    else: print('')
except: print('')
" 2>/dev/null || echo "")
    [[ -n "$_OLLAMA_MODEL" ]] && EMBED_MODEL="$_OLLAMA_MODEL" || true

    _SIM_THRESHOLD=$(python3 -c "
import sys
try:
    content = open('$_CFG').read()
    import re
    m = re.search(r'similarity_threshold:\s*([0-9.]+)', content)
    if m: print(m.group(1).strip())
    else: print('')
except: print('')
" 2>/dev/null || echo "")
    [[ -n "$_SIM_THRESHOLD" ]] && SIMILARITY_THRESHOLD="$_SIM_THRESHOLD" || true
  fi

  export COLLECT_DAYS MAX_SESSIONS SEA_DAYS SEA_MAX_SESSIONS SEA_DISCORD_CHANNEL
fi

# 스테이지 파일 경로
LOGS_JSON="${V4_TMP_DIR}/logs.json"           # Stage 1: v4 collect-logs.sh 출력
ANALYSIS_JSON="${TMP_DIR}/analysis.json"       # Stage 2: v5 embedding-analyze.sh 출력
BENCHMARKS_JSON="${TMP_DIR}/benchmarks.json"   # Stage 3: v4 benchmark.sh 출력
PROPOSAL_MD="${TMP_DIR}/proposal.md"           # Stage 5: v4 synthesize-proposal.sh 출력
EFFECTS_JSON="${TMP_DIR}/effects.json"         # Stage 4: v4 measure-effects.sh 출력
RUN_META_JSON="${TMP_DIR}/run-meta.json"

# 스테이지 상태
_ST_collect_logs="pending"
_ST_embedding_analyze="pending"
_ST_benchmark="pending"
_ST_measure_effects="pending"
_ST_synthesize="pending"

# ── 로그 유틸 ──────────────────────────────────────────────
log_info() { [[ "$VERBOSE" == "true" ]] && echo "[SEA-v5 $(date '+%H:%M:%S')] $*" >&2 || true; }
log_err()  { echo "[SEA-v5 ERR $(date '+%H:%M:%S')] $*" >&2; }
log_always() { echo "[SEA-v5 $(date '+%H:%M:%S')] $*" >&2; }

# ── run_stage (v4에서 동일 — bash 3.2 호환) ─────────────────
run_stage() {
  local _key="$1"
  local _outfile="$2"
  local _script="$3"
  shift 3

  log_info "스테이지 시작: ${_key}"
  local _t0
  _t0=$(date +%s)

  if [[ ! -f "$_script" ]]; then
    log_err "스크립트 없음: ${_script}"
    eval "_ST_${_key}=\"skipped:missing\""
    return 0
  fi

  local _tout=""
  command -v timeout &>/dev/null && _tout="timeout 180" || true

  local _log="${TMP_DIR}/stage-${_key}.log"

  set +u
  local _extra_env=""
  local _pos_args=""
  local _sep_found=false
  for _arg in "$@"; do
    if [[ "$_arg" == "--" ]]; then
      _sep_found=true
    elif [[ "$_sep_found" == "false" ]]; then
      _extra_env="${_extra_env} ${_arg}"
    else
      _pos_args="${_pos_args} '${_arg}'"
    fi
  done

  # v5 환경변수 추가 (Ollama 관련)
  local _env_str="SHELLOPTS= BASHOPTS="
  _env_str="${_env_str} SEA_TMP_DIR='${TMP_DIR}'"
  _env_str="${_env_str} DRY_RUN='${DRY_RUN}'"
  _env_str="${_env_str} VERBOSE='${VERBOSE}'"
  _env_str="${_env_str} MAX_SESSIONS='${MAX_SESSIONS}'"
  _env_str="${_env_str} COLLECT_DAYS='${COLLECT_DAYS}'"
  _env_str="${_env_str} WORKSPACE='${WORKSPACE}'"
  # v5 신규 환경변수
  _env_str="${_env_str} OLLAMA_URL='${OLLAMA_URL}'"
  _env_str="${_env_str} EMBED_MODEL='${EMBED_MODEL}'"
  _env_str="${_env_str} SIMILARITY_THRESHOLD='${SIMILARITY_THRESHOLD}'"
  if [[ -n "${_extra_env# }" ]]; then
    _env_str="${_env_str} ${_extra_env}"
  fi

  eval "env ${_env_str} ${_tout} bash '${_script}'${_pos_args}" \
    > "$_log" 2>&1 || true
  set -u

  local _elapsed=$(( $(date +%s) - _t0 ))

  if [[ "$VERBOSE" == "true" && -f "$_log" ]]; then
    cat "$_log" >&2 || true
  fi

  if [[ -n "$_outfile" && -f "$_outfile" && -s "$_outfile" ]]; then
    eval "_ST_${_key}=\"ok:${_elapsed}s\""
    log_info "✅ 스테이지 완료: ${_key} (${_elapsed}s)"
  else
    eval "_ST_${_key}=\"failed:${_elapsed}s\""
    log_err "❌ 스테이지 실패: ${_key} (${_elapsed}s)"
    if [[ "$VERBOSE" != "true" && -f "$_log" ]]; then
      tail -5 "$_log" >&2 2>/dev/null || true
    fi
  fi

  return 0
}

# ── 초기화 ──────────────────────────────────────────────────
mkdir -p "$TMP_DIR" 2>/dev/null || true
mkdir -p "$V4_TMP_DIR" 2>/dev/null || true

RUN_ID="sea-v5-$(date +%Y%m%d-%H%M%S)"
RUN_START=$(date +%s)

# 실행 메타 파일 생성
python3 - > "$RUN_META_JSON" 2>/dev/null <<PYEOF || true
import json
print(json.dumps({
    "run_id": "${RUN_ID}",
    "version": "v5.0",
    "started_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "dry_run": "${DRY_RUN}" == "true",
    "ollama_url": "${OLLAMA_URL}",
    "embed_model": "${EMBED_MODEL}",
    "similarity_threshold": float("${SIMILARITY_THRESHOLD}"),
    "tmp_dir": "${TMP_DIR}",
    "max_sessions": int("${MAX_SESSIONS}"),
    "collect_days": int("${COLLECT_DAYS}"),
}, indent=2, ensure_ascii=False))
PYEOF

log_always "=== SEA v5.0 오케스트레이터 시작 (${RUN_ID}) ==="
log_always "임베딩 엔진: ${EMBED_MODEL} @ ${OLLAMA_URL}"
log_always "유사도 임계값: ${SIMILARITY_THRESHOLD}"
log_always "세션: ${MAX_SESSIONS}개 | 기간: ${COLLECT_DAYS}일"

# ════════════════════════════════════════════════════════════
# 스테이지 실행
# ════════════════════════════════════════════════════════════

# ── Stage 1: 로그 수집 (v4 스크립트 재사용) ─────────────────
log_always "Stage 1/5: 로그 수집..."
run_stage "collect_logs" "$LOGS_JSON" \
  "${V4_SCRIPT_DIR}/collect-logs.sh" \
  -- "$LOGS_JSON"

# ── Stage 2: 시맨틱 임베딩 분석 (v5 신규!) ──────────────────
log_always "Stage 2/5: 시맨틱 임베딩 분석 (v5 핵심)..."
run_stage "embedding_analyze" "$ANALYSIS_JSON" \
  "${SCRIPT_DIR}/embedding-analyze.sh" \
  "LOGS_JSON=${LOGS_JSON}" "OUTPUT_JSON=${ANALYSIS_JSON}" \
  "SEA_VERBOSE=${VERBOSE}"

# Stage 2 실패 시: v4 시맨틱 분석으로 폴백
_ST2_STATUS=$(eval "echo \"\${_ST_embedding_analyze:-failed}\"")
if [[ "$_ST2_STATUS" == failed* ]] || [[ ! -f "$ANALYSIS_JSON" ]] || [[ ! -s "$ANALYSIS_JSON" ]]; then
  log_err "⚠️  v5 임베딩 분석 실패 — v4 휴리스틱으로 폴백"
  run_stage "embedding_analyze" "$ANALYSIS_JSON" \
    "${V4_SCRIPT_DIR}/semantic-analyze.sh" \
    "LOGS_JSON=${LOGS_JSON}" "OUTPUT_JSON=${ANALYSIS_JSON}"

  # v4 폴백 성공 시 v5 메타 추가
  if [[ -f "$ANALYSIS_JSON" && -s "$ANALYSIS_JSON" ]]; then
    python3 -c "
import json, os
try:
    with open('$ANALYSIS_JSON') as f:
        data = json.load(f)
    data.setdefault('semantic_analysis', {})
    data['semantic_analysis']['engine'] = 'heuristic_v4_fallback'
    data['semantic_analysis']['note'] = 'v5 embedding failed, fell back to v4'
    data['metadata'] = data.get('metadata', {})
    data['metadata']['version'] = 'v5.0-fallback'
    with open('$ANALYSIS_JSON', 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
except Exception as e:
    print(f'메타 추가 실패: {e}', end='')
" 2>/dev/null || true
    log_always "✅ v4 폴백 성공"
  fi
fi

# ── Stage 3: 벤치마크 수집 (v4 스크립트 재사용) ─────────────
log_always "Stage 3/5: 벤치마크 수집..."
run_stage "benchmark" "$BENCHMARKS_JSON" \
  "${V4_SCRIPT_DIR}/benchmark.sh"

# ── Stage 4: 효과 측정 (v4 스크립트 재사용) ─────────────────
log_always "Stage 4/5: 효과 측정..."
run_stage "measure_effects" "$EFFECTS_JSON" \
  "${V4_SCRIPT_DIR}/measure-effects.sh" \
  -- "$EFFECTS_JSON"

# ── Stage 5: 제안 합성 (v4 스크립트 재사용) ─────────────────
log_always "Stage 5/5: 제안 합성..."
run_stage "synthesize" "$PROPOSAL_MD" \
  "${V4_SCRIPT_DIR}/synthesize-proposal.sh" \
  -- "$ANALYSIS_JSON" "$BENCHMARKS_JSON" "$EFFECTS_JSON" "$PROPOSAL_MD"

# ════════════════════════════════════════════════════════════
# 실행 결과 집계
# ════════════════════════════════════════════════════════════
ELAPSED=$(( $(date +%s) - RUN_START ))

STAGE_JSON="{"
_is_first=true
for _k in collect_logs embedding_analyze benchmark measure_effects synthesize; do
  [[ "$_is_first" == "true" ]] && _is_first=false || STAGE_JSON+=","
  _v=$(eval "echo \"\${_ST_${_k}:-unknown}\"")
  STAGE_JSON+="\"${_k}\":\"${_v}\""
done
STAGE_JSON+="}"

# 메타 업데이트
python3 - > "${RUN_META_JSON}.tmp" 2>/dev/null <<PYEOF && mv "${RUN_META_JSON}.tmp" "$RUN_META_JSON" 2>/dev/null || true
import json
try:
    with open("${RUN_META_JSON}") as f:
        m = json.load(f)
except Exception:
    m = {"run_id": "${RUN_ID}"}

# 분석 결과에서 시맨틱 분석 메타 읽기
semantic_meta = {}
try:
    with open("${ANALYSIS_JSON}") as f:
        analysis = json.load(f)
    semantic_meta = analysis.get("semantic_analysis", {})
except Exception:
    pass

m.update({
    "completed_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "elapsed_seconds": ${ELAPSED},
    "stages": ${STAGE_JSON},
    "error_count": ${_ORCH_ERRS},
    "semantic_engine": semantic_meta.get("engine", "unknown"),
    "embeddings_computed": semantic_meta.get("embeddings_computed", 0),
    "cache_hits": semantic_meta.get("cache_hits", 0),
})
print(json.dumps(m, indent=2, ensure_ascii=False))
PYEOF

# 성능 요약 출력
EMBED_ENGINE=$(python3 -c "
import json
try:
    d = json.load(open('$ANALYSIS_JSON'))
    print(d.get('semantic_analysis', {}).get('engine', 'unknown'))
except:
    print('unknown')
" 2>/dev/null || echo "unknown")

EMBED_STATS=$(python3 -c "
import json
try:
    d = json.load(open('$ANALYSIS_JSON'))
    sa = d.get('semantic_analysis', {})
    comp = sa.get('embeddings_computed', 0)
    hits = sa.get('cache_hits', 0)
    clusters = len(sa.get('failure_semantic_clusters', []))
    frustration = len(d.get('frustration_events', []))
    print(f'임베딩:{comp}계산+{hits}캐시 | 클러스터:{clusters}개 | 좌절:{frustration}건')
except:
    print('통계 없음')
" 2>/dev/null || echo "통계 없음")

log_always "완료: ${ELAPSED}초 | 엔진: ${EMBED_ENGINE}"
log_always "임베딩 결과: ${EMBED_STATS}"
log_always "스테이지: ${STAGE_JSON}"

# ════════════════════════════════════════════════════════════
# 최종 출력 (stdout → 크론 배달)
# ════════════════════════════════════════════════════════════

if [[ -f "$PROPOSAL_MD" && -s "$PROPOSAL_MD" ]]; then
  # v5 헤더 추가 후 출력
  echo "<!-- SEA v5.0 | Engine: ${EMBED_ENGINE} | Elapsed: ${ELAPSED}s -->"
  echo ""
  cat "$PROPOSAL_MD"

elif [[ -f "$ANALYSIS_JSON" && -s "$ANALYSIS_JSON" ]]; then
  log_err "proposal.md 없음 — 폴백 요약 생성"
  python3 - "$ANALYSIS_JSON" "$STAGE_JSON" 2>/dev/null <<'PYEOF' || true
import json, sys

with open(sys.argv[1]) as f:
    data = json.load(f)

sa = data.get("semantic_analysis", {})
engine = sa.get("engine", "unknown")
computed = sa.get("embeddings_computed", 0)
hits = sa.get("cache_hits", 0)
clusters = sa.get("failure_semantic_clusters", [])

print("## 🤖 SEA v5.0 요약 (폴백)")
print()
print(f"- 분석 엔진: **{engine}**")
print(f"- 세션: {data.get('sessions_analyzed', 'N/A')}개")
print(f"- 좌절 이벤트: {len(data.get('frustration_events', []))}건 (시맨틱)")
print(f"- 임베딩: {computed}계산 + {hits}캐시")
print(f"- exec 클러스터: {len(clusters)}개")
print()

insights = data.get("key_insights", [])
if insights:
    print("### 핵심 인사이트")
    for ins in insights[:3]:
        print(f"- {ins}")
else:
    print("_이번 주기 특별한 개선 사항 없음_")

print()
print(f"---")
print(f"*SEA v5.0 | 스테이지: {sys.argv[2]}*")
PYEOF

else
  echo "## SEA v5.0 실행 결과"
  echo ""
  echo "_분석 데이터 없음 — 로그 확인 필요_"
  echo ""
  echo "- Run ID: ${RUN_ID}"
  echo "- 소요: ${ELAPSED}초"
  echo "- 스테이지: ${STAGE_JSON}"
fi

# ── 배달 (v4와 동일, discord는 OpenClaw가 자동 처리) ────────
_DELIVER_PLATFORM="${SEA_DELIVERY_PLATFORM:-discord}"
if [[ "$_DELIVER_PLATFORM" != "discord" && -f "$PROPOSAL_MD" && -s "$PROPOSAL_MD" ]]; then
  _DELIVER_SCRIPT="${V4_SCRIPT_DIR}/deliver.sh"
  if [[ -f "$_DELIVER_SCRIPT" ]]; then
    PLATFORM="$_DELIVER_PLATFORM" bash "$_DELIVER_SCRIPT" "$PROPOSAL_MD" 2>&1 | \
      while IFS= read -r _line; do log_info "[deliver] ${_line}"; done || true
  fi
fi

# ── 임시 파일 정리 ───────────────────────────────────────────
find "$TMP_DIR" -maxdepth 1 -name "stage-*.log" -mtime +30 -delete 2>/dev/null || true

log_always "=== SEA v5.0 오케스트레이터 종료 ==="
exit 0
