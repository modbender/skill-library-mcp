#!/usr/bin/env bash
# ============================================================
# lib/config-loader.sh — config.yaml 로더
# YAML을 파싱해 bash 변수로 노출 (Python 사용)
# 사용: source "$(dirname "$0")/lib/config-loader.sh"
# ============================================================

# SECURITY MANIFEST:
# Environment variables accessed: SEA_CONFIG, ANALYSIS_DAYS
#   (exports: SEA_DAYS, SEA_MAX_SESSIONS, SEA_INCLUDE_MEMORY, SEA_COMPLAINT_MIN,
#    SEA_REPEAT_MIN, SEA_EXPIRE_DAYS, SEA_CRON_SCHEDULE, SEA_MODEL,
#    SEA_DISCORD_CHANNEL, SEA_ANALYSIS_JSON, SEA_VERBOSE, SEA_MAX_MSG_LEN,
#    SEA_COMPLAINT_PATTERNS, SEA_LOG_FILES, SEA_LEARNINGS_PATHS, SEA_AGENT_FILTER)
# External endpoints called: None
# Local files read:
#   <SEA_CONFIG>  (if set and exists)
#   ~/openclaw/skills/self-evolving-agent/config.yaml  (default search path)
# Local files written: None  (sets shell environment variables only)
# Network: None

# 이 파일은 직접 실행하지 않고 source로 로드합니다.

# ── config.yaml 경로 자동 탐색 ─────────────────────────────
_find_config() {
  # 1) 환경변수로 명시된 경우
  if [ -n "${SEA_CONFIG:-}" ] && [ -f "$SEA_CONFIG" ]; then
    echo "$SEA_CONFIG"
    return
  fi

  # 2) 스킬 디렉토리 (이 스크립트 기준 상위 디렉토리)
  local script_dir
  script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
  if [ -f "$script_dir/config.yaml" ]; then
    echo "$script_dir/config.yaml"
    return
  fi

  # 3) 기본 경로
  echo "$HOME/openclaw/skills/self-evolving-agent/config.yaml"
}

# ── Python으로 YAML 파싱 ────────────────────────────────────
_load_config_python() {
  local config_file="$1"

  python3 << PYEOF 2>/dev/null
import sys, os

# PyYAML 없으면 json+정규식 폴백
config_file = '$config_file'

# YAML 파싱 시도 (PyYAML이 없으면 간단한 라인 파서 사용)
def parse_simple_yaml(path):
    """간단한 YAML 파서 (PyYAML 없는 환경용). 스칼라 값만 파싱."""
    result = {}
    try:
        with open(path, encoding='utf-8') as f:
            lines = f.readlines()
    except:
        return {}

    current_section = None
    current_subsection = None

    for line in lines:
        # 주석 제거
        stripped = line.rstrip()
        if stripped.lstrip().startswith('#'):
            continue
        if not stripped.strip():
            continue

        # 들여쓰기 레벨 계산
        indent = len(line) - len(line.lstrip())

        if indent == 0 and stripped.endswith(':'):
            # 최상위 섹션
            current_section = stripped[:-1].strip()
            current_subsection = None
            result.setdefault(current_section, {})

        elif indent == 2 and current_section and ':' in stripped:
            # 중간 레벨 키
            key, _, val = stripped.strip().partition(':')
            key = key.strip()
            val = val.strip()
            if val:
                # 주석 제거
                val = val.split('#')[0].strip()
                # 따옴표 제거
                val = val.strip('"\'')
                result[current_section][key] = val
                current_subsection = None
            else:
                current_subsection = key
                result[current_section].setdefault(key, {})

        elif indent == 4 and current_section and current_subsection and ':' in stripped:
            # 깊은 레벨 키
            key, _, val = stripped.strip().partition(':')
            key = key.strip()
            val = val.strip().split('#')[0].strip().strip('"\'')
            if isinstance(result[current_section].get(current_subsection), dict):
                result[current_section][current_subsection][key] = val

    return result

try:
    import yaml
    with open(config_file, encoding='utf-8') as f:
        cfg = yaml.safe_load(f)
except ImportError:
    cfg = parse_simple_yaml(config_file)
except Exception:
    cfg = parse_simple_yaml(config_file)

if not cfg:
    # 기본값 출력
    cfg = {
        'analysis': {'days': 7, 'max_sessions': 30},
        'output': {'verbose': True}
    }

# shell 변수로 출력
analysis = cfg.get('analysis', {})
proposals = cfg.get('proposals', {})
cron = cfg.get('cron', {})
output = cfg.get('output', {})

# 스칼라 값들
print(f"SEA_DAYS={analysis.get('days', 7)}")
print(f"SEA_MAX_SESSIONS={analysis.get('max_sessions', 30)}")
print(f"SEA_INCLUDE_MEMORY={str(analysis.get('include_memory_md', True)).lower()}")
print(f"SEA_COMPLAINT_MIN={proposals.get('complaint_min_hits', 2)}")
print(f"SEA_REPEAT_MIN={proposals.get('repeat_request_min', 3)}")
print(f"SEA_EXPIRE_DAYS={proposals.get('expire_days', 30)}")
print(f"SEA_CRON_SCHEDULE={cron.get('schedule', '0 22 * * 0')}")
print(f"SEA_MODEL={cron.get('model', 'anthropic/claude-sonnet-4-5')}")
print(f"SEA_DISCORD_CHANNEL={cron.get('discord_channel', '')}")
print(f"SEA_ANALYSIS_JSON={output.get('analysis_json', '/tmp/self-evolving-analysis.json')}")
print(f"SEA_VERBOSE={str(output.get('verbose', True)).lower()}")
print(f"SEA_MAX_MSG_LEN={output.get('max_message_length', 3500)}")

# delivery 설정
delivery = cfg.get('delivery', {})
print(f"SEA_DELIVERY_PLATFORM={delivery.get('platform', 'discord')}")
slack = delivery.get('slack', {})
print(f"SEA_SLACK_WEBHOOK_URL={slack.get('webhook_url', '')}")
telegram = delivery.get('telegram', {})
print(f"SEA_TG_BOT_TOKEN={telegram.get('bot_token', '')}")
print(f"SEA_TG_CHAT_ID={telegram.get('chat_id', '')}")
webhook = delivery.get('webhook', {})
print(f"SEA_WEBHOOK_URL={webhook.get('url', '')}")
print(f"SEA_WEBHOOK_METHOD={webhook.get('method', 'POST')}")

# 배열 값들 (쉼표 구분 문자열로 출력)
patterns = analysis.get('complaint_patterns', [])
if isinstance(patterns, list):
    print(f"SEA_COMPLAINT_PATTERNS={','.join(str(p) for p in patterns)}")

log_files = analysis.get('log_files', [])
if isinstance(log_files, list):
    print(f"SEA_LOG_FILES={','.join(str(f) for f in log_files)}")

learnings = analysis.get('learnings_paths', [])
if isinstance(learnings, list):
    print(f"SEA_LEARNINGS_PATHS={','.join(str(p) for p in learnings)}")

agents = analysis.get('agent_filter', [])
if isinstance(agents, list):
    print(f"SEA_AGENT_FILTER={','.join(str(a) for a in agents)}")
PYEOF
}

# ── 공개 함수: 설정 로드 ───────────────────────────────────
sea_load_config() {
  local config_file
  config_file="$(_find_config)"

  if [ ! -f "$config_file" ]; then
    # config.yaml 없으면 기본값 사용
    export SEA_DAYS="${ANALYSIS_DAYS:-7}"
    export SEA_MAX_SESSIONS=30
    export SEA_INCLUDE_MEMORY=true
    export SEA_COMPLAINT_MIN=2
    export SEA_REPEAT_MIN=3
    export SEA_ANALYSIS_JSON="/tmp/self-evolving-analysis.json"
    export SEA_VERBOSE=true
    return 0
  fi

  # Python으로 파싱 후 eval
  local parsed
  parsed="$(_load_config_python "$config_file")"
  if [ -n "$parsed" ]; then
    # 각 줄을 export로 로드
    while IFS= read -r line; do
      # 값이 있는 줄만 export
      [[ "$line" =~ ^[A-Z_]+=.* ]] && export "$line" 2>/dev/null || true
    done <<< "$parsed"
  fi

  # 환경변수 오버라이드 지원 (config.yaml보다 환경변수 우선)
  [ -n "${ANALYSIS_DAYS:-}" ] && export SEA_DAYS="$ANALYSIS_DAYS"

  return 0
}

# ── 설정 확인용 출력 ────────────────────────────────────────
sea_print_config() {
  echo "=== Self-Evolving Agent 설정 ===" >&2
  echo "  분석 기간: ${SEA_DAYS:-7}일" >&2
  echo "  최대 세션: ${SEA_MAX_SESSIONS:-30}개" >&2
  echo "  MEMORY.md 포함: ${SEA_INCLUDE_MEMORY:-true}" >&2
  echo "  분석 JSON: ${SEA_ANALYSIS_JSON:-/tmp/self-evolving-analysis.json}" >&2
  echo "  Discord 채널: ${SEA_DISCORD_CHANNEL:-N/A}" >&2
  echo "================================" >&2
}
