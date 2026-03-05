#!/usr/bin/env bash
# ============================================================
# collect-logs.sh — SEA v4.0 로그 수집기
#
# 역할: 최근 7일간의 다양한 로그를 수집하여 구조화된 JSON으로 출력.
#       이 데이터는 semantic-analyze.sh의 입력으로 사용됨.
#
# 수집 대상:
#   1. 세션 트랜스크립트 (~/.openclaw/agents/*/sessions/*.jsonl)
#   2. 크론 에러 로그 (~/.openclaw/logs/*.log)
#   3. exec 연속 재시도 패턴 (같은 명령어 연속 실행 횟수)
#   4. 하트비트 로그 (heartbeat-cron.log 등)
#
# 사용법:
#   bash collect-logs.sh [출력JSON경로]
#   COLLECT_DAYS=14 bash collect-logs.sh
#
# 변경 이력:
#   v4.0 (2026-02-17) — SEA v4.0 파이프라인용 새 구현
# ============================================================

# SECURITY MANIFEST:
# Environment variables accessed: COLLECT_DAYS, MAX_SESSIONS, AGENTS_BASE,
#   LOGS_DIR, SEA_TMP_DIR
# External endpoints called: None
# Local files read:
#   ~/.openclaw/agents/*/sessions/*.jsonl  (session transcripts — conversation history)
#   ~/.openclaw/logs/cron-catchup.log
#   ~/.openclaw/logs/heartbeat-cron.log
#   ~/.openclaw/logs/context-monitor.log
#   ~/.openclaw/logs/metrics-cron.log
#   ~/.openclaw/logs/memory-cron.log
#   ~/.openclaw/logs/latency-cron.log
#   ~/.openclaw/logs/rate-monitor-cron.log
#   ~/.openclaw/logs/security-cron.log
#   ~/.openclaw/logs/daily-report.log
#   ~/.openclaw/logs/safe-exec.log
#   ~/.openclaw/logs/emergency-recovery-trigger.log
#   <SKILL_DIR>/data/proposals/*.json  (past proposals, up to 20 files)
# Local files written:
#   <OUTPUT_JSON>  (default: /tmp/sea-v4/logs.json)
#   /tmp/sea-v4/collect-work/  (work directory, not explicitly cleaned)
# Network: None

set -euo pipefail

# ── 에러 트랩: 실패해도 빈 JSON 출력 후 종료 (블로킹 방지) ──
COLLECT_ERROR=false
_on_error() {
  local exit_code=$?
  local line=$1
  COLLECT_ERROR=true
  echo "[collect-logs ERR line ${line}] exit=${exit_code}" >&2
}
trap '_on_error $LINENO' ERR

# ── 환경변수 및 경로 설정 ────────────────────────────────────
COLLECT_DAYS="${COLLECT_DAYS:-7}"                 # 수집 기간 (일)
MAX_SESSIONS="${MAX_SESSIONS:-30}"                # 최대 세션 샘플 수
AGENTS_BASE="${AGENTS_BASE:-$HOME/.openclaw/agents}"
LOGS_DIR="${LOGS_DIR:-$HOME/.openclaw/logs}"
TMP_DIR="${SEA_TMP_DIR:-/tmp/sea-v4}"
OUTPUT_JSON="${1:-${TMP_DIR}/logs.json}"

# 출력 디렉토리 보장
mkdir -p "$(dirname "$OUTPUT_JSON")" 2>/dev/null || true
mkdir -p "$TMP_DIR" 2>/dev/null || true

# 임시 작업 디렉토리
WORK_DIR="${TMP_DIR}/collect-work"
mkdir -p "$WORK_DIR" 2>/dev/null || true

# ── 이식성 있는 epoch → 날짜 변환 함수 ──────────────────────
# GNU date: -d @epoch (Linux), BSD date: -r epoch (macOS)
portable_date_from_epoch() {
    local epoch="$1" fmt="${2:-%Y-%m-%dT%H:%M:%SZ}"
    date -u -d "@$epoch" +"$fmt" 2>/dev/null \
        || date -u -r "$epoch" +"$fmt" 2>/dev/null \
        || python3 -c "import datetime; print(datetime.datetime.utcfromtimestamp($epoch).strftime('$fmt'))" 2>/dev/null \
        || echo "unknown"
}

# ── 기준 타임스탬프 (N일 전 epoch) ──────────────────────────
CUTOFF_EPOCH=$(( $(date +%s) - COLLECT_DAYS * 86400 ))
CUTOFF_DATE=$(portable_date_from_epoch "$CUTOFF_EPOCH")

echo "[collect-logs] 수집 기간: 최근 ${COLLECT_DAYS}일 (${CUTOFF_DATE} 이후)" >&2

# ============================================================
# 헬퍼 함수
# ============================================================

# 파일 수정 시간이 N일 이내인지 확인
# 사용법: is_recent <파일경로>
is_recent() {
  local file="$1"
  # -mtime -N 은 N일 이내를 의미
  find "$file" -maxdepth 0 -mtime "-${COLLECT_DAYS}" 2>/dev/null | grep -q . 2>/dev/null || return 1
}

# JSON 문자열 이스케이프 (Python 사용)
json_escape() {
  python3 -c "import json,sys; print(json.dumps(sys.stdin.read()))" 2>/dev/null || echo '""'
}

# ============================================================
# 1단계: 세션 트랜스크립트 수집
# ============================================================
collect_sessions() {
  echo "[collect-logs] 세션 수집 시작..." >&2

  # 모든 에이전트의 세션 파일 목록 (최신순 정렬)
  local session_files=()

  # ~/.openclaw/agents/*/sessions/*.jsonl 탐색
  while IFS= read -r -d '' file; do
    if is_recent "$file" 2>/dev/null || true; then
      session_files+=("$file")
    fi
  done < <(find "$AGENTS_BASE" -name "*.jsonl" -path "*/sessions/*" \
    -mtime "-${COLLECT_DAYS}" -print0 2>/dev/null | sort -rz 2>/dev/null) || true

  # 세션 없으면 빈 배열 반환
  if [[ ${#session_files[@]} -eq 0 ]]; then
    echo "[collect-logs] 세션 파일 없음 (기간: ${COLLECT_DAYS}일)" >&2
    echo "[]"
    return 0
  fi

  # MAX_SESSIONS 개로 제한 (가장 최신 N개)
  local total=${#session_files[@]}
  if [[ $total -gt $MAX_SESSIONS ]]; then
    session_files=("${session_files[@]:0:$MAX_SESSIONS}")
  fi

  echo "[collect-logs] 세션 ${#session_files[@]}개 분석 중 (전체 ${total}개)..." >&2

  # Python으로 세션 파일들을 배치 파싱
  python3 - "${session_files[@]}" <<'PYEOF' 2>/dev/null || echo "[]"
import json
import sys
import os
from pathlib import Path

session_files = sys.argv[1:]
results = []

for filepath in session_files:
    try:
        events = []
        session_meta = {}
        messages = []
        tool_calls = []
        tool_results = []
        compaction_count = 0
        agent_id = "unknown"

        # 에이전트 ID 파싱 (경로에서 추출)
        # ~/.openclaw/agents/{agent}/sessions/{uuid}.jsonl
        parts = Path(filepath).parts
        for i, part in enumerate(parts):
            if part == "agents" and i + 1 < len(parts):
                agent_id = parts[i + 1]
                break

        with open(filepath, encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue

                etype = event.get("type", "")
                ts = event.get("timestamp", "")

                # 세션 메타
                if etype == "session":
                    session_meta = {
                        "id": event.get("id", ""),
                        "timestamp": ts,
                        "cwd": event.get("cwd", ""),
                        "agent": agent_id,
                    }

                # 메시지 추출 (user/assistant 역할)
                elif etype == "message":
                    msg = event.get("message", {})
                    role = msg.get("role", "")
                    content = msg.get("content", "")

                    # content가 리스트인 경우 텍스트만 추출
                    if isinstance(content, list):
                        text_parts = []
                        for item in content:
                            if isinstance(item, dict) and item.get("type") == "text":
                                text_parts.append(item.get("text", ""))
                        content = " ".join(text_parts)

                    if isinstance(content, str):
                        messages.append({
                            "role": role,
                            "text": content[:500],  # 앞 500자만
                            "timestamp": ts,
                        })

                # 도구 호출 (exec, message 등)
                elif etype == "tool_call" or etype == "toolCall":
                    tool_name = (
                        event.get("toolName")
                        or event.get("tool_name")
                        or event.get("name", "unknown")
                    )
                    tool_input = event.get("input", event.get("toolInput", {}))

                    # exec 도구면 명령어 기록
                    cmd = ""
                    if tool_name == "exec" and isinstance(tool_input, dict):
                        cmd = str(tool_input.get("command", ""))[:200]

                    tool_calls.append({
                        "tool": tool_name,
                        "command": cmd,
                        "timestamp": ts,
                    })

                # 도구 결과 (에러 포함)
                elif etype == "tool_result" or etype == "toolResult":
                    is_error = event.get("isError", event.get("is_error", False))
                    content = event.get("content", "")
                    if isinstance(content, list):
                        content = " ".join(
                            c.get("text", "") for c in content
                            if isinstance(c, dict)
                        )
                    tool_results.append({
                        "is_error": is_error,
                        "content_snippet": str(content)[:200],
                        "timestamp": ts,
                    })

                # 컴팩션 카운트
                elif etype == "compact" or (
                    etype == "custom" and event.get("customType", "") == "compact"
                ):
                    compaction_count += 1

        # exec 연속 재시도 패턴 탐지 (같은 명령어 N회 연속)
        exec_calls = [tc for tc in tool_calls if tc["tool"] == "exec" and tc["command"]]
        retry_groups = []
        if exec_calls:
            i = 0
            while i < len(exec_calls):
                cmd = exec_calls[i]["command"]
                count = 1
                j = i + 1
                while j < len(exec_calls) and exec_calls[j]["command"] == cmd:
                    count += 1
                    j += 1
                if count >= 3:  # 3회 이상 연속이면 재시도 패턴
                    retry_groups.append({
                        "command": cmd[:100],
                        "count": count,
                        "timestamp": exec_calls[i]["timestamp"],
                    })
                i = j

        # 불만 패턴 탐지 (user 메시지에서) — v4.1: ko/en 분리, config.yaml 우선 로드
        # config.yaml에서 패턴 로드 시도 (파싱 실패 시 아래 기본값 사용)
        _ko_defaults = [
            "확인중", "다시", "아까", "반복", "기억", "말했잖아", "했잖아",
            "이미 말했", "계속", "물어보지 말고", "전부 다 해줘", "왜 또",
            "몇 번", "또?", "저번에도", "왜 자꾸", "또 그러네", "안 되잖아",
            "또 하네", "다시 또", "다시 해야",
        ]
        _en_defaults = [
            "you forgot", "again?", "same mistake", "stop doing that",
            "how many times", "wrong again", "you already", "I told you",
            "keep doing", "still broken", "not what I asked", "try again",
            "that's not right", "still not working", "told you", "as I said",
        ]
        try:
            import os as _os, re as _re
            _skill_dir = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', '..')
            _config_path = _os.path.join(_skill_dir, 'config.yaml')
            _ko_cfg, _en_cfg = [], []
            if _os.path.isfile(_config_path):
                with open(_config_path, encoding='utf-8') as _cf:
                    _section = None
                    for _line in _cf:
                        _s = _line.strip()
                        if _re.match(r'ko\s*:', _s):
                            _section = 'ko'
                        elif _re.match(r'en\s*:', _s):
                            _section = 'en'
                        elif _re.match(r'auto_detect\s*:', _s):
                            _section = None
                        elif _section and _s.startswith('- '):
                            _v = _s[2:].strip().strip('"').strip("'")
                            if _v:
                                (_ko_cfg if _section == 'ko' else _en_cfg).append(_v)
                        elif _s and not _s.startswith('-') and ':' in _s and not _re.match(r'^\s*(ko|en)\s*:', _line):
                            _section = None
            _ko_patterns = _ko_cfg or _ko_defaults
            _en_patterns = _en_cfg or _en_defaults
        except Exception:
            _ko_patterns, _en_patterns = _ko_defaults, _en_defaults

        # 세션 언어 감지: 첫 10개 user 메시지 중 >50%에 한글이면 ko
        import re as _re2
        _user_sample = [m for m in messages if m["role"] == "user"][:10]
        _korean_hits = sum(1 for m in _user_sample if _re2.search(r'[가-힣]', m.get("text", "")))
        _lang = 'ko' if (_user_sample and _korean_hits / len(_user_sample) > 0.5) else 'en'
        complaint_keywords = _ko_patterns if _lang == 'ko' else _en_patterns
        user_complaints = []
        for msg in messages:
            if msg["role"] != "user":
                continue
            text = msg["text"].lower()
            for kw in complaint_keywords:
                if kw.lower() in text:
                    user_complaints.append({
                        "keyword": kw,
                        "timestamp": msg["timestamp"],
                        "snippet": msg["text"][:150],
                    })
                    break  # 세션당 1건만

        # 에러 결과 수집
        error_results = [r for r in tool_results if r["is_error"]]

        result = {
            "session_id": session_meta.get("id", Path(filepath).stem),
            "agent": session_meta.get("agent", agent_id),
            "timestamp": session_meta.get("timestamp", ""),
            "cwd": session_meta.get("cwd", ""),
            "message_count": len(messages),
            "tool_call_count": len(tool_calls),
            "error_count": len(error_results),
            "compaction_count": compaction_count,
            "exec_retry_patterns": retry_groups,
            "user_complaints": user_complaints,
            "error_snippets": [r["content_snippet"] for r in error_results[:5]],
            "filepath": filepath,
        }
        results.append(result)

    except Exception as e:
        results.append({
            "session_id": Path(filepath).stem,
            "error": str(e),
            "filepath": filepath,
        })

print(json.dumps(results, ensure_ascii=False))
PYEOF
}

# ============================================================
# 2단계: 크론 에러 로그 수집
# ============================================================
collect_cron_logs() {
  echo "[collect-logs] 크론 에러 로그 수집..." >&2

  # 분석할 로그 파일 목록 (설정 파일 연동 가능)
  local log_files=(
    "cron-catchup.log"
    "heartbeat-cron.log"
    "context-monitor.log"
    "metrics-cron.log"
    "memory-cron.log"
    "latency-cron.log"
    "rate-monitor-cron.log"
    "security-cron.log"
    "daily-report.log"
    "safe-exec.log"        # exec 실패 기록
    "emergency-recovery-trigger.log"
  )

  python3 - "${LOGS_DIR}" "${COLLECT_DAYS}" "${log_files[@]}" <<'PYEOF' 2>/dev/null || echo "[]"
import json
import sys
import os
import re
from pathlib import Path
from datetime import datetime, timedelta, timezone

logs_dir = sys.argv[1]
collect_days = int(sys.argv[2])
log_files = sys.argv[3:]

cutoff = datetime.now(timezone.utc) - timedelta(days=collect_days)
results = []

# 에러 패턴 정규식
ERROR_PATTERNS = [
    (re.compile(r'\bERROR\b|\bERR\b|\bFAIL\b|\bfailed?\b', re.IGNORECASE), "error"),
    (re.compile(r'exit (?:code )?[1-9]\d*', re.IGNORECASE), "nonzero_exit"),
    (re.compile(r'Timeout|timed? ?out', re.IGNORECASE), "timeout"),
    (re.compile(r'Ambiguous|ambiguous', re.IGNORECASE), "ambiguous"),
    (re.compile(r'Permission denied', re.IGNORECASE), "permission"),
    (re.compile(r'No such file|not found', re.IGNORECASE), "not_found"),
    (re.compile(r'⚠️|🔧|Exec.*failed', re.IGNORECASE), "exec_fail"),
]

for log_name in log_files:
    log_path = Path(logs_dir) / log_name
    if not log_path.exists():
        continue

    # 최근 N일 이내 수정된 파일만
    mtime = datetime.fromtimestamp(log_path.stat().st_mtime, tz=timezone.utc)
    if mtime < cutoff:
        continue

    try:
        with open(log_path, encoding="utf-8", errors="replace") as f:
            lines = f.readlines()

        error_lines = []
        total_lines = len(lines)

        # 최근 500줄만 분석 (성능)
        for line in lines[-500:]:
            line_strip = line.strip()
            if not line_strip:
                continue

            for pattern, ptype in ERROR_PATTERNS:
                if pattern.search(line_strip):
                    error_lines.append({
                        "type": ptype,
                        "text": line_strip[:200],
                    })
                    break  # 줄당 1개 패턴만

        # 에러 타입별 집계
        error_summary = {}
        for err in error_lines:
            etype = err["type"]
            error_summary[etype] = error_summary.get(etype, 0) + 1

        results.append({
            "log_file": log_name,
            "last_modified": mtime.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "total_lines": total_lines,
            "error_count": len(error_lines),
            "error_summary": error_summary,
            "recent_errors": [e["text"] for e in error_lines[-10:]],  # 최근 10개
        })

    except Exception as e:
        results.append({
            "log_file": log_name,
            "error": str(e),
        })

print(json.dumps(results, ensure_ascii=False))
PYEOF
}

# ============================================================
# 3단계: exec 전역 재시도 패턴 집계
# ============================================================
collect_exec_retries() {
  echo "[collect-logs] exec 재시도 패턴 전역 집계..." >&2

  # safe-exec.log에서 반복 실패 명령어 추출
  local safe_exec_log="${LOGS_DIR}/safe-exec.log"

  python3 - "$safe_exec_log" "$COLLECT_DAYS" <<'PYEOF' 2>/dev/null || echo "[]"
import json
import sys
import re
from pathlib import Path
from datetime import datetime, timedelta, timezone
from collections import Counter

log_path = sys.argv[1]
collect_days = int(sys.argv[2])
cutoff = datetime.now(timezone.utc) - timedelta(days=collect_days)

if not Path(log_path).exists():
    print(json.dumps([]))
    sys.exit(0)

try:
    with open(log_path, encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    # 명령어 실패 카운트 (safe-exec.log 포맷 파싱)
    # 포맷 예: [YYYYMMDD-HHMMSS] [작업명] FAILED: 명령어
    cmd_failures = Counter()
    recent_failures = []

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if "FAIL" in line.upper() or "ERROR" in line.upper():
            # 명령어 추출 시도
            cmd_match = re.search(r'FAILED?:\s*(.+)$', line, re.IGNORECASE)
            if cmd_match:
                cmd = cmd_match.group(1).strip()[:100]
                cmd_failures[cmd] += 1
                if len(recent_failures) < 20:
                    recent_failures.append({"command": cmd, "line": line[:200]})

    # 3회 이상 반복 실패 명령어만
    repeated = [
        {"command": cmd, "failure_count": count}
        for cmd, count in cmd_failures.most_common(20)
        if count >= 3
    ]

    print(json.dumps({
        "repeated_failures": repeated,
        "total_failure_lines": sum(cmd_failures.values()),
        "unique_failed_commands": len(cmd_failures),
        "recent_failures": recent_failures,
    }, ensure_ascii=False))

except Exception as e:
    print(json.dumps({"error": str(e)}))
PYEOF
}

# ============================================================
# 4단계: 하트비트 로그 수집
# ============================================================
collect_heartbeat_logs() {
  echo "[collect-logs] 하트비트 로그 수집..." >&2

  local hb_logs=(
    "${LOGS_DIR}/heartbeat-cron.log"
    "${LOGS_DIR}/heartbeat-monitor.log"
  )

  python3 - "$COLLECT_DAYS" "${hb_logs[@]}" <<'PYEOF' 2>/dev/null || echo "{}"
import json
import sys
import re
from pathlib import Path
from datetime import datetime, timedelta, timezone

collect_days = int(sys.argv[1])
log_paths = sys.argv[2:]

stats = {
    "heartbeat_ok_count": 0,
    "heartbeat_fail_count": 0,
    "heartbeat_total": 0,
    "no_reply_count": 0,       # NO_REPLY (불필요한 응답 억제)
    "proactive_actions": [],   # 하트비트에서 수행한 자발적 작업
    "error_lines": [],
}

for log_path_str in log_paths:
    log_path = Path(log_path_str)
    if not log_path.exists():
        continue

    try:
        with open(log_path, encoding="utf-8", errors="replace") as f:
            lines = f.readlines()

        for line in lines[-1000:]:  # 최근 1000줄
            line = line.strip()
            if not line:
                continue

            if "HEARTBEAT_OK" in line:
                stats["heartbeat_ok_count"] += 1
                stats["heartbeat_total"] += 1
            elif "NO_REPLY" in line:
                stats["no_reply_count"] += 1
                stats["heartbeat_total"] += 1
            elif re.search(r'error|fail|exception', line, re.IGNORECASE):
                stats["heartbeat_fail_count"] += 1
                stats["heartbeat_total"] += 1
                if len(stats["error_lines"]) < 5:
                    stats["error_lines"].append(line[:200])
            # 자발적 작업 탐지 (메모리 업데이트, git 커밋 등)
            if re.search(r'memory|git commit|self-review|자발적', line, re.IGNORECASE):
                if len(stats["proactive_actions"]) < 10:
                    stats["proactive_actions"].append(line[:150])

    except Exception as e:
        stats["error_lines"].append(f"파싱 에러: {e}")

# OK 비율 계산
total = stats["heartbeat_total"]
if total > 0:
    stats["ok_rate"] = round(stats["heartbeat_ok_count"] / total, 3)
else:
    stats["ok_rate"] = None

print(json.dumps(stats, ensure_ascii=False))
PYEOF
}

# ============================================================
# 5단계: 이전 제안 목록 수집 (효과 측정용)
# ============================================================
collect_past_proposals() {
  echo "[collect-logs] 이전 제안 목록 수집..." >&2

  local skill_dir
  skill_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
  local proposals_dir="${skill_dir}/data/proposals"

  python3 - "$proposals_dir" "$COLLECT_DAYS" <<'PYEOF' 2>/dev/null || echo "[]"
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone

proposals_dir = sys.argv[1]
collect_days = int(sys.argv[2])
cutoff = datetime.now(timezone.utc) - timedelta(days=collect_days * 4)  # 4주치 과거 제안

if not Path(proposals_dir).exists():
    print(json.dumps([]))
    sys.exit(0)

proposals = []
for f in sorted(Path(proposals_dir).glob("*.json"), reverse=True)[:20]:
    try:
        mtime = datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc)
        if mtime < cutoff:
            continue

        with open(f) as fp:
            data = json.load(fp)

        proposals.append({
            "id": data.get("id", f.stem),
            "created_at": data.get("created_at", ""),
            "title": data.get("title", "")[:100],
            "status": data.get("status", "unknown"),
            "applied": data.get("applied", False),
        })
    except Exception:
        continue

print(json.dumps(proposals, ensure_ascii=False))
PYEOF
}

# ============================================================
# 메인: 모든 단계 실행 후 JSON 합성
# ============================================================

echo "[collect-logs] 데이터 수집 시작 (${COLLECT_DAYS}일, 최대 ${MAX_SESSIONS}개 세션)" >&2

# 각 단계 실행 (에러 시 빈 값 사용)
SESSIONS_JSON=$(collect_sessions 2>/dev/null || echo "[]")
CRON_LOGS_JSON=$(collect_cron_logs 2>/dev/null || echo "[]")
EXEC_RETRIES_JSON=$(collect_exec_retries 2>/dev/null || echo "{}")
HEARTBEAT_JSON=$(collect_heartbeat_logs 2>/dev/null || echo "{}")
PAST_PROPOSALS_JSON=$(collect_past_proposals 2>/dev/null || echo "[]")

# ── 전체 집계 통계 계산 ──────────────────────────────────────
python3 - \
  "$COLLECT_DAYS" \
  "$MAX_SESSIONS" \
  "$OUTPUT_JSON" \
  <<PYEOF 2>/dev/null || true
import json
import sys
from datetime import datetime, timezone

collect_days = int(sys.argv[1])
max_sessions = int(sys.argv[2])
output_path = sys.argv[3]

# 각 단계 결과 파싱 (실패 시 기본값)
try:
    sessions = json.loads("""${SESSIONS_JSON}""")
except Exception:
    sessions = []

try:
    cron_logs = json.loads("""${CRON_LOGS_JSON}""")
except Exception:
    cron_logs = []

try:
    exec_retries = json.loads("""${EXEC_RETRIES_JSON}""")
except Exception:
    exec_retries = {}

try:
    heartbeat = json.loads("""${HEARTBEAT_JSON}""")
except Exception:
    heartbeat = {}

try:
    past_proposals = json.loads("""${PAST_PROPOSALS_JSON}""")
except Exception:
    past_proposals = []

# 집계 통계
total_messages = sum(s.get("message_count", 0) for s in sessions if isinstance(s, dict))
total_tool_calls = sum(s.get("tool_call_count", 0) for s in sessions if isinstance(s, dict))
total_errors = sum(s.get("error_count", 0) for s in sessions if isinstance(s, dict))
total_compactions = sum(s.get("compaction_count", 0) for s in sessions if isinstance(s, dict))

# 모든 exec 재시도 패턴 병합
all_retry_patterns = []
for s in sessions:
    if isinstance(s, dict):
        all_retry_patterns.extend(s.get("exec_retry_patterns", []))
all_retry_patterns.sort(key=lambda x: x.get("count", 0), reverse=True)

# 모든 불만 패턴 병합
all_complaints = []
for s in sessions:
    if isinstance(s, dict):
        all_complaints.extend(s.get("user_complaints", []))

# 크론 에러 집계
total_cron_errors = sum(l.get("error_count", 0) for l in cron_logs if isinstance(l, dict))

# 최종 JSON 구성
output = {
    "collected_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "collection_period_days": collect_days,
    "summary": {
        "sessions_analyzed": len(sessions),
        "total_messages": total_messages,
        "total_tool_calls": total_tool_calls,
        "total_errors": total_errors,
        "total_compactions": total_compactions,
        "exec_retry_groups": len(all_retry_patterns),
        "complaint_hits": len(all_complaints),
        "cron_error_count": total_cron_errors,
    },
    "sessions": sessions,
    "cron_logs": cron_logs,
    "exec_retries": exec_retries,
    "exec_retry_patterns": all_retry_patterns[:20],  # 상위 20개
    "user_complaints": all_complaints,
    "heartbeat": heartbeat,
    "past_proposals": past_proposals,
}

# 파일 저장
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

# 요약을 stderr로 출력
summary = output["summary"]
print(f"[collect-logs] 완료: 세션 {summary['sessions_analyzed']}개, "
      f"불만 {summary['complaint_hits']}건, "
      f"exec재시도 {summary['exec_retry_groups']}건, "
      f"크론에러 {summary['cron_error_count']}건", file=__import__('sys').stderr)
print(f"[collect-logs] 출력: {output_path}", file=__import__('sys').stderr)
PYEOF

# 최종 확인
if [[ -f "$OUTPUT_JSON" && -s "$OUTPUT_JSON" ]]; then
  echo "[collect-logs] 성공: ${OUTPUT_JSON}" >&2
  exit 0
else
  echo "[collect-logs] 실패: 출력 파일이 비어있거나 생성되지 않음" >&2
  # 빈 JSON으로 폴백 (오케스트레이터가 다음 스테이지 진행 가능하도록)
  echo '{"collected_at":"","collection_period_days":7,"summary":{},"sessions":[],"cron_logs":[],"exec_retries":{},"exec_retry_patterns":[],"user_complaints":[],"heartbeat":{},"past_proposals":[]}' \
    > "$OUTPUT_JSON" 2>/dev/null || true
  exit 1
fi
