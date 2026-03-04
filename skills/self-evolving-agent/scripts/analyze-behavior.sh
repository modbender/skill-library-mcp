#!/usr/bin/env bash
# ============================================================
# analyze-behavior.sh — Self-Evolving Agent 행동 분석기 v3.0
#
# 변경 이력:
#   v3.0 (2026-02-17) — 품질 비평 기반 전면 개선
#     - 버그 수정: tool_use → toolCall (실제 필드명)
#     - 연속 도구 재시도 분석 추가 (exec 5210회 패턴 감지)
#     - 불만 패턴 맥락 필터링 강화 (일반 요청과 구분)
#     - 반복 에러 루트 코즈 분석 (같은 에러 N회 = 버그 미수정)
#     - violations를 exec 명령에서만 탐지 (응답 전체 grep 제거)
#     - 세션 길이 이상치 감지 (compaction 횟수)
#   v2.0 (2026-02-17) — config.yaml 지원, .learnings/ 연동
#   v1.1 (2026-02-16) — 초기 버전
#
# 사용법:
#   bash analyze-behavior.sh [출력JSON경로]
#   ANALYSIS_DAYS=14 bash analyze-behavior.sh
# ============================================================

# SECURITY MANIFEST:
# Environment variables accessed: SEA_DAYS, ANALYSIS_DAYS, SEA_MAX_SESSIONS,
#   AGENTS_DIR, LOGS_DIR, AGENTS_MD, MEMORY_MD, SEA_ANALYSIS_JSON, SEA_VERBOSE,
#   SEA_LEARNINGS_PATHS, SEA_LOG_FILES, SEA_COMPLAINT_PATTERNS,
#   SEA_INCLUDE_MEMORY, SEA_REPEAT_MIN
# External endpoints called: None
# Local files read:
#   ~/.openclaw/agents/*/sessions/*.jsonl  (session transcripts — conversation history)
#   ~/.openclaw/logs/*.log                 (cron/heartbeat logs)
#   ~/openclaw/AGENTS.md                   (agent config)
#   ~/openclaw/MEMORY.md                   (long-term memory, if SEA_INCLUDE_MEMORY=true)
#   ~/openclaw/.learnings/{ERRORS,LEARNINGS,FEATURE_REQUESTS}.md
#   <SKILL_DIR>/data/rejected-proposals.json
# Local files written:
#   <OUTPUT_JSON>  (default: /tmp/self-evolving-analysis.json)
#   <SKILL_DIR>/data/  (directory created if missing)
#   /tmp/.sea-ref-$$, /tmp/sea-sort-input-$$, /tmp/sea-$$/  (temp, auto-deleted)
# Network: None

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

if [ -f "$SCRIPT_DIR/lib/config-loader.sh" ]; then
  source "$SCRIPT_DIR/lib/config-loader.sh"
  sea_load_config 2>/dev/null || true
fi

ANALYSIS_DAYS="${SEA_DAYS:-${ANALYSIS_DAYS:-7}}"
MAX_SESSIONS="${SEA_MAX_SESSIONS:-50}"
AGENTS_DIR="${AGENTS_DIR:-$HOME/.openclaw/agents}"
LOGS_DIR="${LOGS_DIR:-$HOME/.openclaw/logs}"
AGENTS_MD="${AGENTS_MD:-$HOME/openclaw/AGENTS.md}"
MEMORY_MD="${MEMORY_MD:-$HOME/openclaw/MEMORY.md}"
OUTPUT_JSON="${1:-${SEA_ANALYSIS_JSON:-/tmp/self-evolving-analysis.json}}"
VERBOSE="${SEA_VERBOSE:-true}"

LEARNINGS_PATHS=()
if [ -n "${SEA_LEARNINGS_PATHS:-}" ]; then
  IFS=',' read -ra LEARNINGS_PATHS <<< "$SEA_LEARNINGS_PATHS"
else
  LEARNINGS_PATHS=("openclaw/.learnings" ".openclaw/.learnings")
fi

LOG_FILES=()
if [ -n "${SEA_LOG_FILES:-}" ]; then
  IFS=',' read -ra LOG_FILES <<< "$SEA_LOG_FILES"
else
  LOG_FILES=("cron-catchup.log" "heartbeat-cron.log" "context-monitor.log" "metrics-cron.log")
fi

mkdir -p "$SKILL_DIR/data"
mkdir -p "$(dirname "$OUTPUT_JSON")"

log() {
  [ "$VERBOSE" = "true" ] && echo "[$(date '+%H:%M:%S')] $*" >&2 || true
}

find_recent_sessions() {
  local ref_file="/tmp/.sea-ref-$$"
  python3 -c "
import os, time
ref = time.time() - (${ANALYSIS_DAYS} * 86400)
open('${ref_file}', 'w').close()
os.utime('${ref_file}', (ref, ref))
" 2>/dev/null || touch "$ref_file"

  if [ ! -d "$AGENTS_DIR" ]; then
    rm -f "$ref_file"
    return 0
  fi

  find "$AGENTS_DIR" -name "*.jsonl" -path "*/sessions/*" -newer "$ref_file" 2>/dev/null || true
  rm -f "$ref_file"
}

sort_by_mtime_file() {
  local input_file="$1"
  local max_count="${2:-50}"
  python3 - "$input_file" "$max_count" << 'PYEOF' 2>/dev/null
import sys, os
input_file = sys.argv[1]
max_count = int(sys.argv[2])
with open(input_file) as f:
    files = [line.strip() for line in f if line.strip()]
files = [f for f in files if os.path.exists(f)]
files.sort(key=lambda f: os.path.getmtime(f), reverse=True)
print('\n'.join(files[:max_count]))
PYEOF
}

read_learnings() {
  python3 << PYEOF 2>/dev/null
import os, re, json
raw_paths = """${LEARNINGS_PATHS[*]}"""
paths = [p.strip() for p in raw_paths.split() if p.strip()]
home = os.path.expanduser("~")
result = {'errors':[],'learnings':[],'feature_requests':[],'total_pending':0,'total_high_priority':0}
for path_rel in paths:
    path = path_rel if path_rel.startswith('/') else os.path.join(home, path_rel)
    if not os.path.isdir(path):
        continue
    for fname, key, id_prefix, content_key in [
        ('ERRORS.md', 'errors', 'ERR', 'summary'),
        ('LEARNINGS.md', 'learnings', 'LRN', 'summary'),
        ('FEATURE_REQUESTS.md', 'feature_requests', 'FEAT', 'capability'),
    ]:
        fpath = os.path.join(path, fname)
        if not os.path.exists(fpath):
            continue
        with open(fpath, encoding='utf-8', errors='ignore') as f:
            content = f.read()
        entries = re.findall(
            rf'## \[({id_prefix}-\d{{8}}-\w+)\].*?\n\*\*Status\*\*: (pending|in_progress).*?\n### (?:Summary|Requested Capability)\n(.*?)\n',
            content, re.DOTALL
        )
        for eid, status, text in entries:
            result[key].append({'id':eid,'status':status,content_key:text.strip()[:200]})
        high_count = len(re.findall(r'\*\*Priority\*\*: (?:high|critical)', content))
        result['total_high_priority'] += high_count
result['total_pending'] = sum(len(result[k]) for k in ['errors','learnings','feature_requests'])
print(json.dumps(result, ensure_ascii=False))
PYEOF
}

analyze_memory_md() {
  if [ "${SEA_INCLUDE_MEMORY:-true}" != "true" ]; then
    echo "{}"
    return 0
  fi
  python3 << PYEOF 2>/dev/null
import os, re, json
memory_path = '$MEMORY_MD'
result = {'exists':False,'issue_count':0,'patterns':[],'word_count':0}
if not os.path.exists(memory_path):
    print(json.dumps(result)); import sys; sys.exit(0)
with open(memory_path, encoding='utf-8', errors='ignore') as f:
    content = f.read()
result['exists'] = True
result['word_count'] = len(content.split())
issue_patterns = re.findall(
    r'(?:문제|실수|오류|개선점|TODO|주의|⚠️|❌)[^\n]{0,100}',
    content, re.MULTILINE
)
result['issue_count'] = len(issue_patterns)
result['patterns'] = [p.strip() for p in issue_patterns[:5]]
print(json.dumps(result, ensure_ascii=False))
PYEOF
}

run_analysis() {
  log "세션 파일 검색 중... (최근 ${ANALYSIS_DAYS}일, 최대 ${MAX_SESSIONS}개)"

  local session_files=()
  while IFS= read -r f; do
    [ -n "$f" ] && session_files+=("$f")
  done < <(find_recent_sessions)

  local session_count=${#session_files[@]}
  log "발견된 세션: ${session_count}개"

  if [ "$MAX_SESSIONS" -gt 0 ] && [ "$session_count" -gt "$MAX_SESSIONS" ]; then
    log "세션 수 제한: 최신 ${MAX_SESSIONS}개만 분석"
    local sort_input="/tmp/sea-sort-input-$$"
    printf '%s\n' "${session_files[@]}" > "$sort_input"
    local sorted_files=()
    while IFS= read -r f; do
      [ -n "$f" ] && sorted_files+=("$f")
    done < <(sort_by_mtime_file "$sort_input" "$MAX_SESSIONS")
    rm -f "$sort_input"
    session_files=("${sorted_files[@]}")
    session_count=${#session_files[@]}
  fi

  log ".learnings/ 분석 중..."
  local learnings_json
  learnings_json="$(read_learnings)"
  [ -z "$learnings_json" ] && learnings_json='{"total_pending":0,"errors":[],"learnings":[],"feature_requests":[],"total_high_priority":0}'

  log "MEMORY.md 분석 중..."
  local memory_json
  memory_json="$(analyze_memory_md)"
  [ -z "$memory_json" ] && memory_json='{"exists":false,"issue_count":0,"patterns":[]}'

  local tmp_dir="/tmp/sea-$$"
  mkdir -p "$tmp_dir"
  trap 'rm -rf "$tmp_dir"' EXIT INT TERM

  if [ ${#session_files[@]} -eq 0 ]; then
    echo "[]" > "$tmp_dir/sessions.json"
  else
    printf '%s\n' "${session_files[@]}" | python3 -c "
import sys, json
files = [line.rstrip('\n') for line in sys.stdin if line.strip()]
print(json.dumps(files))
" 2>/dev/null > "$tmp_dir/sessions.json" || echo "[]" > "$tmp_dir/sessions.json"
  fi

  echo "$learnings_json" > "$tmp_dir/learnings.json"
  echo "$memory_json" > "$tmp_dir/memory.json"

  # 불만 패턴: 일반 요청 표현(확인해줘, 진행해) 제외
  # 실제 불만 신호: 재촉, 과거 참조, 반복 표현
  local patterns_str="${SEA_COMPLAINT_PATTERNS:-말했잖아,했잖아,이미 말했,왜 또,몇 번,또?,기억 못,저번에도,왜 자꾸,또 그러네,안 되잖아,또 하네,다시 해야,다시 또}"
  python3 -c "
import json
patterns = [p.strip() for p in '''$patterns_str'''.split(',') if p.strip()]
print(json.dumps(patterns))
" 2>/dev/null > "$tmp_dir/patterns.json" || echo '[]' > "$tmp_dir/patterns.json"

  printf '%s\n' "${LOG_FILES[@]}" | python3 -c "
import sys, json
files = [line.strip() for line in sys.stdin if line.strip()]
print(json.dumps(files))
" 2>/dev/null > "$tmp_dir/logfiles.json" || echo '[]' > "$tmp_dir/logfiles.json"

  # Python 분석 스크립트를 파일로 저장 후 실행 (heredoc 인덴트 문제 방지)
  cat > "$tmp_dir/analysis.py" << 'ANALYSIS_PY_EOF'
import json, re, os, sys
from collections import Counter, defaultdict
from datetime import datetime

tmp_dir = sys.argv[1]
output_path = sys.argv[2]
logs_dir = sys.argv[3]
agents_md_path = sys.argv[4]
skill_dir = sys.argv[5]
analysis_days = int(sys.argv[6])

with open(f'{tmp_dir}/sessions.json', encoding='utf-8') as f:
    session_files = json.load(f)
with open(f'{tmp_dir}/learnings.json', encoding='utf-8') as f:
    learnings_data = json.load(f)
with open(f'{tmp_dir}/memory.json', encoding='utf-8') as f:
    memory_data = json.load(f)
with open(f'{tmp_dir}/patterns.json', encoding='utf-8') as f:
    complaint_patterns = json.load(f)
with open(f'{tmp_dir}/logfiles.json', encoding='utf-8') as f:
    log_files_target = json.load(f)

# ── 1. 세션 심층 분석 (v3.0 핵심 개선) ────────────────────
user_texts = []
assistant_texts = []
exec_commands = []          # exec 도구에 실제 전달된 명령어만

# 도구 분석 데이터
tool_seq_per_session = []   # 세션별 도구 호출 순서
compaction_counts = []      # 세션별 컴팩션 횟수
session_lengths = []        # 세션별 메시지 수

for filepath in session_files:
    try:
        tool_seq = []
        compaction_count = 0
        msg_count = 0

        with open(filepath, encoding='utf-8', errors='ignore') as f:
            for line in f:
                try:
                    d = json.loads(line)
                    t = d.get('type')

                    if t == 'compaction':
                        compaction_count += 1

                    elif t == 'message':
                        msg = d.get('message', {})
                        role = msg.get('role', '')
                        content = msg.get('content', '')
                        msg_count += 1

                        text = ''
                        if isinstance(content, str):
                            text = content
                        elif isinstance(content, list):
                            for c in content:
                                if not isinstance(c, dict):
                                    continue
                                c_type = c.get('type', '')

                                # v3.0 수정: 실제 필드명 toolCall (구버전 tool_use 제거)
                                if c_type == 'toolCall':
                                    name = c.get('name', '')
                                    tool_seq.append(name)
                                    # exec 명령어 추출 (violations 분석용)
                                    if name == 'exec':
                                        args = c.get('arguments', '')
                                        if isinstance(args, str):
                                            try:
                                                args_dict = json.loads(args.replace("'", '"'))
                                            except Exception:
                                                # 파이썬 dict 형식일 수 있음
                                                m = re.search(r"'command'\s*:\s*'([^']+)'", args)
                                                if m:
                                                    exec_commands.append(m.group(1))
                                            else:
                                                cmd = args_dict.get('command', '')
                                                if cmd:
                                                    exec_commands.append(cmd)
                                    elif c_type == 'text':
                                        text += c.get('text', '')

                        if text:
                            if role == 'user':
                                user_texts.append(text)
                            elif role == 'assistant':
                                assistant_texts.append(text)
                except (json.JSONDecodeError, KeyError):
                    pass

        tool_seq_per_session.append(tool_seq)
        compaction_counts.append(compaction_count)
        session_lengths.append(msg_count)

    except (IOError, OSError):
        pass

all_user_text = '\n'.join(user_texts)
all_exec_cmds = '\n'.join(exec_commands)  # violations는 exec 명령에서만 탐지

# ── 2. 연속 도구 재시도 분석 (v3.0 핵심 신호) ────────────
# 같은 "효과 도구"를 연속 호출 = 실패/재시도 패턴 (에이전트 혼선 신호)
# 제외: read/write/edit/image/tts/canvas (순차 파일 I/O는 정상 패턴)
RETRY_EXCLUDE_TOOLS = frozenset({'read', 'write', 'edit', 'image', 'tts', 'canvas'})
RETRY_SESSION_THRESHOLD = 5   # 세션 카운팅: 5회 이상 연속 = 재시도 신호
RETRY_WORST_THRESHOLD = 10    # worst_streaks 기록: 10회 이상 연속 = 심각한 루프

retry_tool_counts = Counter()
retry_sequences = []  # (도구명, 연속횟수) 리스트

for tool_seq in tool_seq_per_session:
    # 효과 도구만 필터링
    action_seq = [t for t in tool_seq if t not in RETRY_EXCLUDE_TOOLS]
    current_tool = None
    current_streak = 1

    for tool in action_seq:
        if tool == current_tool:
            current_streak += 1
        else:
            if current_tool and current_streak >= RETRY_SESSION_THRESHOLD:
                retry_tool_counts[current_tool] += 1
                if current_streak >= RETRY_WORST_THRESHOLD:
                    retry_sequences.append({
                        'tool': current_tool,
                        'streak': current_streak
                    })
            current_tool = tool
            current_streak = 1

    if current_tool and current_streak >= RETRY_SESSION_THRESHOLD:
        retry_tool_counts[current_tool] += 1
        if current_streak >= RETRY_WORST_THRESHOLD:
            retry_sequences.append({
                'tool': current_tool,
                'streak': current_streak
            })

retry_analysis = {
    'high_retry_tools': [
        {'tool': t, 'sessions_with_streak': c}
        for t, c in retry_tool_counts.most_common(5)
    ],
    'total_retry_events': sum(retry_tool_counts.values()),
    'worst_streaks': sorted(retry_sequences, key=lambda x: x['streak'], reverse=True)[:5]
}

# ── 3. 세션 길이 이상치 감지 (컴팩션 = 과도한 작업 신호) ──
heavy_sessions = sum(1 for c in compaction_counts if c >= 5)
avg_compaction = sum(compaction_counts) / len(compaction_counts) if compaction_counts else 0
max_compaction = max(compaction_counts) if compaction_counts else 0

session_health = {
    'total_sessions': len(session_files),
    'heavy_sessions': heavy_sessions,  # 컴팩션 5회 이상
    'avg_compaction_per_session': round(avg_compaction, 2),
    'max_compaction': max_compaction,
    'avg_msg_count': round(sum(session_lengths) / len(session_lengths), 1) if session_lengths else 0
}

# ── 4. 불만 패턴 분석 (맥락 필터링 강화) ────────────────
# v3.0: 일반 요청("확인해줘", "진행해")과 실제 불만 표현 구분
# 불만 신호 조건: 과거 참조 + 재촉 + 반복 표현

complaint_results = []
total_hits = 0
seen_sentences = set()

sentences = re.split(r'[.!?\n]+', all_user_text)

for pattern in complaint_patterns:
    hit_sentences = []
    for sent in sentences:
        if pattern in sent and sent not in seen_sentences:
            # 추가 맥락 필터: 해당 문장이 실제 불만 문맥인지 확인
            # 예: "다시 확인해줘" (정상) vs "다시 또 오류야" (불만)
            cleaned = sent.strip()
            if len(cleaned) > 5:  # 너무 짧은 문장 제외
                hit_sentences.append(cleaned)
                seen_sentences.add(sent)
    if hit_sentences:
        complaint_results.append({'pattern': pattern, 'count': len(hit_sentences), 'examples': hit_sentences[:2]})
        total_hits += len(hit_sentences)

complaints = {
    'session_count': len(session_files),
    'total_complaint_hits': total_hits,
    'patterns': complaint_results
}

# ── 5. 반복 에러 루트 코즈 분석 (같은 에러 반복 = 버그 미수정) ──
log_errors = []

for logfile in log_files_target:
    logpath = os.path.join(logs_dir, logfile)
    try:
        with open(logpath, errors='ignore') as f:
            content = f.read()

        err_patterns = re.findall(
            r'(?i)(?:error|failed|exception|traceback|panic|fatal)[^\n]{0,150}',
            content
        )

        # 에러 시그니처 추출 (파일별 독립 dict — 파일 간 오염 방지)
        file_error_signatures = defaultdict(list)
        for err in err_patterns:
            # 타임스탬프, 숫자 제거해서 "같은 에러인지" 판별
            sig = re.sub(r'\d{4}-\d{2}-\d{2}|\d{2}:\d{2}:\d{2}|\b\d+\b', 'N', err)
            sig = sig.strip()[:100]
            file_error_signatures[sig].append(err)

        err_count = len(err_patterns)
        if err_count > 0:
            # 반복 에러 감지 (같은 파일 내에서만 집계)
            repeating = [(sig, len(occ)) for sig, occ in file_error_signatures.items() if len(occ) >= 3]
            repeating.sort(key=lambda x: x[1], reverse=True)

            log_errors.append({
                'file': logfile,
                'error_count': err_count,
                'unique_errors': len(file_error_signatures),
                'repeating_errors': [
                    {'signature': sig[:80], 'occurrences': count}
                    for sig, count in repeating[:3]
                ],
                'recent_samples': [p.strip() for p in err_patterns[-3:]]
            })
    except (IOError, OSError):
        pass

# ── 6. 에러 크론 분석 ────────────────────────────────────
cron_errors = []
try:
    cron_file = os.path.expanduser('~/.openclaw/cron/jobs.json')
    with open(cron_file, encoding='utf-8') as f:
        cron_data = json.load(f)
    for job in cron_data.get('jobs', []):
        state = job.get('state', {})
        errs = state.get('consecutiveErrors', 0)
        last_status = state.get('lastStatus', 'ok')
        if errs > 0 or last_status == 'error':
            cron_errors.append({
                'name': job.get('name', ''),
                'consecutive_errors': errs,
                'last_status': last_status,
                'last_duration_ms': state.get('lastDurationMs', 0)
            })
except (IOError, OSError, json.JSONDecodeError, KeyError):
    pass

errors = {
    'cron_errors': cron_errors,
    'log_errors': log_errors
}

# ── 7. AGENTS.md 위반 분석 (v3.0: exec 명령에서만 탐지) ──
# 이전: 에이전트 응답 전체 텍스트에서 grep → 오탐 다수
# 개선: exec 도구에 전달된 실제 명령어에서만 탐지
violations = []
violation_config = [
    {
        'pattern': r'\bgit\s+(?:pull|push|fetch)\b',
        'rule': 'git 직접 명령 (git-sync.sh 우회)',
        'severity': 'high',
        'min_hits': 1,
        'source': 'exec_commands',
        'fix': 'bash ~/openclaw/scripts/git-sync.sh'
    },
    {
        'pattern': r'\brm\s+-rf?\b',
        'rule': 'rm 직접 사용 (trash 사용 필요)',
        'severity': 'medium',
        'min_hits': 2,
        'source': 'exec_commands',
        'fix': 'trash <경로>  # brew install trash'
    },
    {
        'pattern': r'curl\s+https?://[^\s]+(?<!-f)(?<!-s)',
        'rule': 'curl 실패 핸들링 누락',
        'severity': 'low',
        'min_hits': 3,
        'source': 'exec_commands',
        'fix': 'curl -sf <URL> || echo "API 실패"'
    }
]

search_text = all_exec_cmds  # exec 명령에서만

for vc in violation_config:
    hit_count = len(re.findall(vc['pattern'], search_text))
    if hit_count >= vc.get('min_hits', 1):
        # 실제 위반 예시 추출
        examples = re.findall(vc['pattern'], search_text)[:3]
        violations.append({
            'rule': vc['rule'],
            'pattern': vc['pattern'],
            'hit_count': hit_count,
            'severity': vc['severity'],
            'examples': examples,
            'fix': vc.get('fix', '')
        })

violation_data = {'violations': violations}

# ── 8. 반복 요청 패턴 (한국어, 맥락 기반) ──────────────
# 단순 동사 카운팅이 아닌 "작업 유형" 추출
action_patterns = re.findall(
    r'([가-힣a-zA-Z]{2,15}(?:해줘|해봐|수정해|고쳐|바꿔|추가해|삭제해|분석해|검토해|파악해))',
    all_user_text
)
counter = Counter(action_patterns)
# "확인해줘", "진행해" 같은 일반 표현은 제외 (작업 특정성이 없음)
generic_verbs = {'확인해줘', '확인해봐', '확인해', '진행해', '진행해줘', '해줘', '해봐', '해', '보여줘'}
repeat_requests = [
    {'phrase': k, 'count': v}
    for k, v in counter.most_common(10)
    if v >= int(os.environ.get('SEA_REPEAT_MIN', '3')) and k not in generic_verbs
]

# ── 9. .learnings/ 요약 ─────────────────────────────────
learnings_summary = {
    'total_pending': learnings_data.get('total_pending', 0),
    'total_high_priority': learnings_data.get('total_high_priority', 0),
    'top_errors': learnings_data.get('errors', [])[:3],
    'top_learnings': learnings_data.get('learnings', [])[:3],
    'feature_requests': learnings_data.get('feature_requests', [])[:3]
}

# ── 결과 조립 ────────────────────────────────────────────
result = {
    'meta': {
        'analysis_date': datetime.now().strftime('%Y-%m-%d'),
        'analysis_timestamp': datetime.now().isoformat(),
        'analysis_days': analysis_days,
        'session_count': len(session_files),
        'version': '3.0.0'
    },
    'complaints': complaints,
    'errors': errors,
    'violations': violation_data,
    'repeat_requests': repeat_requests,
    'learnings': learnings_summary,
    'memory_md': memory_data,
    # v3.0 신규 분석 결과
    'retry_analysis': retry_analysis,
    'session_health': session_health,
    'previously_rejected': []
}

try:
    rejection_log = os.path.join(skill_dir, 'data', 'rejected-proposals.json')
    with open(rejection_log, encoding='utf-8') as f:
        result['previously_rejected'] = json.load(f)
except (IOError, OSError, json.JSONDecodeError):
    pass

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(
    f'분석 완료: {len(session_files)}세션, '
    f'실제불만 {total_hits}건, '
    f'위반 {len(violations)}건, '
    f'도구재시도이벤트 {retry_analysis["total_retry_events"]}건, '
    f'미해결학습 {learnings_data.get("total_pending", 0)}건'
)
ANALYSIS_PY_EOF

  # Python 분석 실행
  python3 "$tmp_dir/analysis.py" \
    "$tmp_dir" \
    "$OUTPUT_JSON" \
    "$LOGS_DIR" \
    "$AGENTS_MD" \
    "$SKILL_DIR" \
    "$ANALYSIS_DAYS" \
    2>/dev/null || echo "분석 실행 실패" >&2
}

main() {
  log "=== Self-Evolving Agent 행동 분석 v3.0 ==="
  log "분석 기간: 최근 ${ANALYSIS_DAYS}일 / 최대 ${MAX_SESSIONS}개 세션"
  log "에이전트 디렉토리: $AGENTS_DIR"

  run_analysis

  log "분석 완료 → $OUTPUT_JSON"

  if python3 -c "import json; json.load(open('$OUTPUT_JSON'))" 2>/dev/null; then
    log "JSON 유효성 확인: OK"
  else
    log "경고: JSON 유효성 검사 실패"
  fi

  cat "$OUTPUT_JSON"
}

main "$@"
