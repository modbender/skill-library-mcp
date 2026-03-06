#!/usr/bin/env bash
# ============================================================
# llm-call.sh — Self-Evolving Agent 범용 LLM 인터페이스
#
# 역할:
#   stdin에서 프롬프트를 읽어 LLM에 전달하고 응답을 stdout으로 출력.
#   provider/model은 config.yaml 또는 플래그로 지정.
#
# 지원 프로바이더:
#   anthropic  — Claude API (ANTHROPIC_API_KEY 필요)
#   openai     — OpenAI API (OPENAI_API_KEY 필요)
#   ollama     — 로컬 Ollama (API 키 없음, 완전 무료!)
#   none       — LLM 호출 없음 (빈 JSON 반환, 순수 휴리스틱 모드)
#
# 사용법:
#   echo "프롬프트" | bash llm-call.sh
#   echo "프롬프트" | bash llm-call.sh --provider ollama
#   echo "프롬프트" | bash llm-call.sh --provider anthropic --model claude-haiku-4-5
#   cat analysis.json | bash llm-call.sh --provider ollama --model mistral:7b
#
# 환경변수:
#   LLM_PROVIDER      — 프로바이더 (플래그보다 낮은 우선순위)
#   LLM_MODEL         — 모델명 (플래그보다 낮은 우선순위)
#   ANTHROPIC_API_KEY — Anthropic API 키
#   OPENAI_API_KEY    — OpenAI API 키
#   OLLAMA_URL        — Ollama 엔드포인트 (기본: http://localhost:11434)
#   SEA_CONFIG_PATH   — config.yaml 경로 (기본: 자동 탐색)
#
# 종료 코드:
#   0 — 성공 (응답 있음)
#   1 — LLM 호출 실패 (에러는 stderr)
#   2 — 프롬프트 없음
#   3 — config.yaml 없음 (none 모드로 폴백)
#
# SECURITY MANIFEST:
#   Environment variables accessed: LLM_PROVIDER, LLM_MODEL, ANTHROPIC_API_KEY,
#     OPENAI_API_KEY, OLLAMA_URL, SEA_CONFIG_PATH, SEA_TMP_DIR
#   External endpoints called:
#     - https://api.anthropic.com/v1/messages (anthropic provider)
#     - https://api.openai.com/v1/chat/completions (openai provider)
#     - http://localhost:11434/api/generate (ollama provider, local only)
#   Local files read:
#     - <skill_dir>/config.yaml (provider/model 설정)
#   Local files written: none
# ============================================================

set -o pipefail

# ── 경로 설정 ──────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

# ── 로그 함수 ──────────────────────────────────────────────
_llm_err() { echo "[llm-call] ERROR: $*" >&2; }
_llm_info() { echo "[llm-call] $*" >&2; }

# ── 인자 파싱 ──────────────────────────────────────────────
_PROVIDER=""
_MODEL=""
_SYSTEM_PROMPT="You are a helpful AI assistant analyzing agent behavior data and generating improvement proposals."

while [[ $# -gt 0 ]]; do
  case "$1" in
    --provider|-p)  _PROVIDER="${2:-}"; shift 2 ;;
    --model|-m)     _MODEL="${2:-}";    shift 2 ;;
    --system|-s)    _SYSTEM_PROMPT="${2:-}"; shift 2 ;;
    --help|-h)
      sed -n '3,30p' "${BASH_SOURCE[0]}" | grep '^#' | sed 's/^# \?//'
      exit 0 ;;
    *) _llm_err "알 수 없는 플래그: $1"; exit 1 ;;
  esac
done

# ── config.yaml 파싱 (Python3 + yaml, grep fallback) ───────
_parse_config() {
  local config="${SEA_CONFIG_PATH:-$SKILL_DIR/config.yaml}"
  if [[ ! -f "$config" ]]; then
    echo "none none none"
    return 3
  fi

  python3 - "$config" 2>/dev/null <<'PYEOF'
import sys, re

config_path = sys.argv[1]
provider = "anthropic"
model = ""
ollama_url = "http://localhost:11434"

try:
    with open(config_path, "r", encoding="utf-8") as f:
        content = f.read()

    # PyYAML 시도
    try:
        import yaml
        cfg = yaml.safe_load(content)
        llm = cfg.get("llm", {})
        provider = llm.get("provider", "anthropic")
        p_cfg = llm.get(provider, {})
        if isinstance(p_cfg, dict):
            model = p_cfg.get("model", "")
            if provider == "ollama":
                ollama_url = p_cfg.get("url", "http://localhost:11434")
    except ImportError:
        # 정규식 fallback
        m = re.search(r'^\s*provider:\s*["\']?(\w+)["\']?', content, re.MULTILINE)
        if m:
            provider = m.group(1)
        # provider별 모델 추출
        for line in content.splitlines():
            if "model:" in line and model == "":
                mv = re.search(r'model:\s*["\']?([^\s"\'\#]+)', line)
                if mv:
                    model = mv.group(1)
        m2 = re.search(r'url:\s*["\']?(http[^\s"\'\#]+)', content)
        if m2:
            ollama_url = m2.group(1)

except Exception as e:
    pass

print(f"{provider} {model or 'default'} {ollama_url}")
PYEOF
}

# config 읽기
_CONFIG_VALS=""
_CONFIG_VALS=$(_parse_config 2>/dev/null) || true

_CFG_PROVIDER=$(echo "$_CONFIG_VALS" | awk '{print $1}')
_CFG_MODEL=$(echo "$_CONFIG_VALS"    | awk '{print $2}')
_CFG_OLLAMA_URL=$(echo "$_CONFIG_VALS" | awk '{print $3}')

# 우선순위: 플래그 > 환경변수 > config.yaml > 기본값
PROVIDER="${_PROVIDER:-${LLM_PROVIDER:-${_CFG_PROVIDER:-anthropic}}}"
MODEL="${_MODEL:-${LLM_MODEL:-${_CFG_MODEL:-}}}"
OLLAMA_URL="${OLLAMA_URL:-${_CFG_OLLAMA_URL:-http://localhost:11434}}"

# provider가 none이면 바로 빈 응답 출력
if [[ "$PROVIDER" == "none" ]]; then
  _llm_info "provider=none → LLM 호출 생략 (순수 휴리스틱 모드)"
  echo '{}'
  exit 0
fi

# ── stdin에서 프롬프트 읽기 ────────────────────────────────
PROMPT=""
if [[ -p /dev/stdin ]]; then
  PROMPT=$(cat)
elif [[ -t 0 ]]; then
  _llm_err "stdin이 없습니다. echo '프롬프트' | bash llm-call.sh 형식으로 사용하세요."
  exit 2
else
  PROMPT=$(cat)
fi

if [[ -z "${PROMPT// /}" ]]; then
  _llm_err "프롬프트가 비어 있습니다."
  exit 2
fi

_llm_info "provider=${PROVIDER} model=${MODEL:-default}"

# ── JSON 안전 이스케이프 ────────────────────────────────────
_json_escape() {
  python3 -c "
import json, sys
text = sys.stdin.read()
# JSON 문자열로 인코딩 (따옴표 제외)
print(json.dumps(text)[1:-1])
" 2>/dev/null || echo "$1" | sed 's/\\/\\\\/g; s/"/\\"/g; s/$/\\n/' | tr -d '\n'
}

PROMPT_ESCAPED=$(echo "$PROMPT" | _json_escape)
SYSTEM_ESCAPED=$(echo "$_SYSTEM_PROMPT" | _json_escape)

# ════════════════════════════════════════════════════════════
# Anthropic Claude API
# ════════════════════════════════════════════════════════════
_call_anthropic() {
  local api_key="${ANTHROPIC_API_KEY:-}"
  if [[ -z "$api_key" ]]; then
    _llm_err "ANTHROPIC_API_KEY 환경변수가 설정되지 않았습니다."
    return 1
  fi

  local model="${MODEL:-claude-sonnet-4-5}"

  local response
  response=$(curl -sf --max-time 60 \
    "https://api.anthropic.com/v1/messages" \
    -H "Content-Type: application/json" \
    -H "x-api-key: ${api_key}" \
    -H "anthropic-version: 2023-06-01" \
    -d "{
      \"model\": \"${model}\",
      \"max_tokens\": 2048,
      \"system\": \"${SYSTEM_ESCAPED}\",
      \"messages\": [{
        \"role\": \"user\",
        \"content\": \"${PROMPT_ESCAPED}\"
      }]
    }" 2>/dev/null) || {
    _llm_err "Anthropic API 호출 실패"
    return 1
  }

  # 응답 텍스트 추출
  echo "$response" | python3 -c "
import json, sys
d = json.load(sys.stdin)
content = d.get('content', [{}])
if isinstance(content, list) and content:
    print(content[0].get('text', ''))
else:
    print(d.get('error', {}).get('message', '응답 없음'))
" 2>/dev/null || echo "$response"
}

# ════════════════════════════════════════════════════════════
# OpenAI API
# ════════════════════════════════════════════════════════════
_call_openai() {
  local api_key="${OPENAI_API_KEY:-}"
  if [[ -z "$api_key" ]]; then
    _llm_err "OPENAI_API_KEY 환경변수가 설정되지 않았습니다."
    return 1
  fi

  local model="${MODEL:-gpt-4.1}"

  local response
  response=$(curl -sf --max-time 60 \
    "https://api.openai.com/v1/chat/completions" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${api_key}" \
    -d "{
      \"model\": \"${model}\",
      \"max_tokens\": 2048,
      \"messages\": [
        {\"role\": \"system\", \"content\": \"${SYSTEM_ESCAPED}\"},
        {\"role\": \"user\",   \"content\": \"${PROMPT_ESCAPED}\"}
      ]
    }" 2>/dev/null) || {
    _llm_err "OpenAI API 호출 실패"
    return 1
  }

  echo "$response" | python3 -c "
import json, sys
d = json.load(sys.stdin)
choices = d.get('choices', [{}])
if choices:
    print(choices[0].get('message', {}).get('content', ''))
else:
    print(d.get('error', {}).get('message', '응답 없음'))
" 2>/dev/null || echo "$response"
}

# ════════════════════════════════════════════════════════════
# Ollama (로컬 LLM — 완전 무료!)
# ════════════════════════════════════════════════════════════
_call_ollama() {
  local model="${MODEL:-llama3.1:8b}"
  local url="${OLLAMA_URL:-http://localhost:11434}"

  # Ollama 서버 실행 확인
  if ! curl -sf --max-time 3 "${url}/api/tags" &>/dev/null; then
    _llm_err "Ollama 서버에 연결할 수 없습니다: ${url}"
    _llm_err "실행 방법: ollama serve (다른 터미널에서)"
    return 1
  fi

  # 모델 존재 확인 (없으면 자동 pull 안내)
  local model_exists
  model_exists=$(curl -sf --max-time 5 "${url}/api/tags" 2>/dev/null \
    | python3 -c "
import json, sys
d = json.load(sys.stdin)
models = [m.get('name','') for m in d.get('models', [])]
# 태그 없는 이름으로도 비교 (llama3.1:8b vs llama3.1)
base = '${model}'.split(':')[0]
found = any('${model}' in m or base == m.split(':')[0] for m in models)
print('yes' if found else 'no')
" 2>/dev/null || echo "unknown")

  if [[ "$model_exists" == "no" ]]; then
    _llm_err "Ollama 모델이 없습니다: ${model}"
    _llm_err "설치 방법: ollama pull ${model}"
    return 1
  fi

  _llm_info "Ollama 로컬 LLM 호출: ${model} @ ${url}"

  # 전체 프롬프트 (시스템 + 사용자)
  local full_prompt="${_SYSTEM_PROMPT}\n\n${PROMPT}"
  local full_escaped
  full_escaped=$(echo "$full_prompt" | _json_escape)

  # /api/generate 호출 (스트리밍 비활성화)
  local response
  response=$(curl -sf --max-time 120 \
    "${url}/api/generate" \
    -H "Content-Type: application/json" \
    -d "{
      \"model\": \"${model}\",
      \"prompt\": \"${full_escaped}\",
      \"stream\": false,
      \"options\": {
        \"num_predict\": 2048,
        \"temperature\": 0.7
      }
    }" 2>/dev/null) || {
    _llm_err "Ollama API 호출 실패 (타임아웃 또는 오류)"
    return 1
  }

  echo "$response" | python3 -c "
import json, sys
d = json.load(sys.stdin)
print(d.get('response', '응답 없음'))
" 2>/dev/null || echo "$response"
}

# ════════════════════════════════════════════════════════════
# 메인 디스패처
# ════════════════════════════════════════════════════════════
case "$PROVIDER" in
  anthropic)
    _call_anthropic
    ;;
  openai)
    _call_openai
    ;;
  ollama)
    _call_ollama
    ;;
  none)
    # 이미 위에서 처리됨 (여기에 오지 않음)
    echo '{}'
    ;;
  *)
    _llm_err "알 수 없는 provider: '${PROVIDER}' (anthropic|openai|ollama|none 중 선택)"
    exit 1
    ;;
esac

EXIT_CODE=$?
if [[ $EXIT_CODE -ne 0 ]]; then
  _llm_err "LLM 호출 실패 (exit ${EXIT_CODE})"
  exit 1
fi
exit 0
