#!/usr/bin/env bash
# ============================================================
# semantic-analyze.sh — Self-Evolving Agent v4.0 시맨틱 분석기
#
# 역할: 키워드 매칭 대신 구조적 휴리스틱으로 세션 패턴 추출
#       → /tmp/sea-v4/analysis.json 생성
#       → stdout에 LLM용 분석 프롬프트 출력 (오케스트레이터가 LLM에 전달)
#
# 데이터 구조 (실제 확인된 jsonl 포맷):
#   type: message  → message.role: user|assistant
#   assistant content: [{type:"text"}, {type:"thinking"}, {type:"toolCall", name:"exec", arguments:{command:"..."}}]
#   user content: [{type:"text"}, {type:"image"}]
#   type: compaction → summary 필드
#   type: custom    → customType: "model-snapshot" 등
#
# 사용법:
#   bash semantic-analyze.sh
#   MAX_SESSIONS=20 bash semantic-analyze.sh
#   ANALYSIS_DAYS=14 bash semantic-analyze.sh
# ============================================================

# SECURITY MANIFEST:
# Environment variables accessed: SEA_DAYS, COLLECT_DAYS, MAX_SESSIONS,
#   SEA_MAX_SESSIONS, AGENTS_DIR, AGENTS_MD, LOGS_JSON, OUTPUT_JSON, SEA_VERBOSE
# External endpoints called: None
# Local files read:
#   <LOGS_JSON>  (default: /tmp/sea-v4/logs.json, from collect-logs.sh)
#   ~/.openclaw/agents/*/sessions/*.jsonl  (fallback if logs.json has no paths)
#   ~/openclaw/AGENTS.md  (rule extraction for violation detection)
# Local files written:
#   <OUTPUT_JSON>  (default: /tmp/sea-v4/analysis.json)
#   /tmp/sea-v4/  (directory created if missing)
# Network: None

set -euo pipefail

# ── 설정 ──────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

ANALYSIS_DAYS="${SEA_DAYS:-${COLLECT_DAYS:-7}}"
MAX_SESSIONS="${MAX_SESSIONS:-${SEA_MAX_SESSIONS:-30}}"
AGENTS_DIR="${AGENTS_DIR:-$HOME/.openclaw/agents}"
AGENTS_MD="${AGENTS_MD:-$HOME/openclaw/AGENTS.md}"
LOGS_JSON="${LOGS_JSON:-/tmp/sea-v4/logs.json}"
OUTPUT_JSON="${OUTPUT_JSON:-/tmp/sea-v4/analysis.json}"
VERBOSE="${SEA_VERBOSE:-false}"

# 출력 디렉토리 보장
mkdir -p /tmp/sea-v4 2>/dev/null || true
mkdir -p "$(dirname "$OUTPUT_JSON")" 2>/dev/null || true

# ── 로그 함수 ─────────────────────────────────────────────────
log() {
  [ "$VERBOSE" = "true" ] && echo "[$(date '+%H:%M:%S')] $*" >&2 || true
}

export SKILL_DIR  # Python에서 os.environ.get('SKILL_DIR') 로 접근

log "=== SEA v4.1 시맨틱 분석기 시작 ==="
log "분석 기간: ${ANALYSIS_DAYS}일, 최대 세션: ${MAX_SESSIONS}개"

# ── 핵심 분석 (Python3) ───────────────────────────────────────
python3 << PYEOF
import json
import os
import sys
import re
import glob
import time
from collections import defaultdict
from datetime import datetime, timezone

# ── 설정값 ──────────────────────────────────────────────────
ANALYSIS_DAYS   = int(os.environ.get('ANALYSIS_DAYS', '7'))
MAX_SESSIONS    = int(os.environ.get('MAX_SESSIONS', os.environ.get('SEA_MAX_SESSIONS', '30')))  # orchestrator=MAX_SESSIONS, legacy=SEA_MAX_SESSIONS
AGENTS_DIR      = os.environ.get('AGENTS_DIR', os.path.expanduser('~/.openclaw/agents'))
AGENTS_MD_PATH  = os.environ.get('AGENTS_MD', os.path.expanduser('~/openclaw/AGENTS.md'))
LOGS_JSON       = os.environ.get('LOGS_JSON', '/tmp/sea-v4/logs.json')
OUTPUT_JSON     = os.environ.get('OUTPUT_JSON', '/tmp/sea-v4/analysis.json')
SKILL_DIR       = os.environ.get('SKILL_DIR', os.path.join(os.path.dirname(os.path.abspath(__file__ if '__file__' in dir() else '.')), '..', '..'))

# ── AGENTS.md 규칙 파싱 ─────────────────────────────────────
def load_agents_rules():
    """AGENTS.md에서 핵심 규칙을 추출한다."""
    rules = []
    try:
        with open(AGENTS_MD_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
        # 중요 규칙 섹션들 추출
        rule_patterns = [
            # exec 에러 노출 금지
            ('exec_error_exposure', r'exec.*실패.*금지|non-zero 종료.*노출|failed: .*에러'),
            # git 직접 명령 금지
            ('git_direct_cmd', r'git pull|git push.*직접.*금지'),
            # gateway restart 제한
            ('gateway_restart', r'gateway restart.*2번 이상 금지'),
            # 채널 라우팅
            ('channel_routing', r'your-channel|your-dev-channel|your-lite-channel'),
            # WAL protocol
            ('wal_protocol', r'WAL|Write-Ahead|FIRST.*respond|write.*before'),
            # 메시지 단편화 금지
            ('msg_fragmentation', r'단편화 금지|하나의 메시지|짧은 메시지.*연속'),
        ]
        # AGENTS.md에서 금지 규칙 코드블록 추출
        code_blocks = re.findall(r'❌[^\n]*\n([^\n]+)', content)
        for block in code_blocks[:20]:
            rules.append(block.strip())
    except Exception as e:
        pass
    return {
        'raw_rules': rules,
        'key_rules': [
            'exec 명령 실패 시 ||true 또는 핸들링 필수',
            'git 직접 명령 금지 (git-sync.sh 사용)',
            'gateway restart 같은 이유로 2회 이상 금지',
            'exec 에러 노출 시 Discord에 자동 표시됨',
            '메시지 단편화 금지 (하나의 메시지로 통합)',
            'WAL Protocol: 중요 정보는 파일에 먼저 기록',
            '채널 라우팅: dev작업→your-channel, 빠른질문→your-lite-channel',
        ]
    }

# ── config.yaml 불만 패턴 로드 (v4.1: ko/en 분리) ──────────
def load_config_patterns(skill_dir=None):
    """
    config.yaml에서 complaint_patterns.ko / .en / auto_detect를 읽는다.
    yaml 파서 없으면 정규식 fallback. 실패 시 하드코딩 기본값 반환.
    """
    if skill_dir is None:
        skill_dir = os.path.expanduser('~/openclaw/skills/self-evolving-agent')

    # 하드코딩 기본값 (config.yaml 파싱 실패 시)
    default_ko = [
        "확인중", "다시", "아까", "반복", "기억", "말했잖아", "했잖아",
        "이미 말했", "계속", "물어보지 말고", "전부 다 해줘", "왜 또",
        "몇 번", "또?", "저번에도", "왜 자꾸", "또 그러네", "안 되잖아",
        "또 하네", "다시 또", "다시 해야",
    ]
    default_en = [
        "you forgot", "again?", "same mistake", "stop doing that",
        "how many times", "wrong again", "you already", "I told you",
        "keep doing", "still broken", "not what I asked", "try again",
        "that's not right", "still not working", "told you", "as I said",
    ]

    config_path = os.path.join(skill_dir, 'config.yaml')
    if not os.path.isfile(config_path):
        return default_ko, default_en, True

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # PyYAML 시도
        try:
            import yaml
            cfg = yaml.safe_load(content)
            cp = cfg.get('analysis', {}).get('complaint_patterns', {})
            if isinstance(cp, dict):
                ko = [str(p) for p in cp.get('ko', default_ko)]
                en = [str(p) for p in cp.get('en', default_en)]
                auto = bool(cp.get('auto_detect', True))
                return ko, en, auto
        except ImportError:
            pass  # yaml 없으면 정규식 fallback

        # 정규식 fallback 파서
        ko, en = [], []
        section = None
        for line in content.splitlines():
            stripped = line.strip()
            if re.match(r'ko\s*:', stripped):
                section = 'ko'
            elif re.match(r'en\s*:', stripped):
                section = 'en'
            elif re.match(r'auto_detect\s*:', stripped):
                section = None
            elif section and stripped.startswith('- '):
                val = stripped[2:].strip().strip('"').strip("'")
                if val:
                    (ko if section == 'ko' else en).append(val)
            elif stripped and not stripped.startswith('-') and ':' in stripped:
                # 새 키 → 섹션 종료 가드
                if section and not re.match(r'^\s*(ko|en)\s*:', line):
                    section = None

        return (ko or default_ko), (en or default_en), True

    except Exception:
        return default_ko, default_en, True


# ── 세션 언어 자동 감지 (v4.1) ──────────────────────────────
def detect_session_language(session):
    """
    세션의 첫 10개 user 메시지를 검사.
    그 중 >50%에 한글 문자([가-힣])가 포함되어 있으면 'ko', 아니면 'en' 반환.
    """
    user_msgs = [m for m in session.get('messages', []) if m.get('role') == 'user'][:10]
    if not user_msgs:
        return 'ko'  # 기본값

    korean_count = sum(
        1 for m in user_msgs
        if re.search(r'[가-힣]', m.get('text', ''))
    )
    return 'ko' if (korean_count / len(user_msgs)) > 0.5 else 'en'


# ── 세션 파일 수집 ──────────────────────────────────────────
def collect_session_files():
    """logs.json 또는 agents 디렉토리에서 세션 파일 수집."""
    sessions = []

    # 1순위: /tmp/sea-v4/logs.json
    if os.path.isfile(LOGS_JSON):
        try:
            with open(LOGS_JSON) as f:
                data = json.load(f)
            # logs.json이 파일 경로 목록인 경우
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, str) and os.path.isfile(item):
                        sessions.append(item)
                    elif isinstance(item, dict) and ('path' in item or 'filepath' in item):
                        p = item.get('path') or item.get('filepath')
                        if os.path.isfile(p):
                            sessions.append(p)
            elif isinstance(data, dict) and 'sessions' in data:
                for item in data['sessions']:
                    if isinstance(item, str) and os.path.isfile(item):
                        sessions.append(item)
                    elif isinstance(item, dict):
                        p = item.get('path') or item.get('filepath')
                        if p and os.path.isfile(p):
                            sessions.append(p)
        except Exception:
            pass

    # 2순위: agents 디렉토리 스캔 (fallback)
    if not sessions:
        cutoff = time.time() - (ANALYSIS_DAYS * 86400)
        pattern = os.path.join(AGENTS_DIR, '*/sessions/*.jsonl')
        all_files = glob.glob(pattern)
        # 수정 시간 기준 필터링
        recent = [f for f in all_files if os.path.getmtime(f) >= cutoff]
        # 크기 순 정렬 (작은 cron 세션 제외, 50KB 미만 스킵)
        recent = [f for f in recent if os.path.getsize(f) > 50 * 1024]
        # 최신 수정 순으로 정렬
        recent.sort(key=os.path.getmtime, reverse=True)
        sessions = recent

    # 최대 MAX_SESSIONS개로 제한
    sessions = sessions[:MAX_SESSIONS]
    return sessions

# ── 세션 파싱 ───────────────────────────────────────────────
def parse_session(filepath):
    """jsonl 세션 파일을 파싱해 구조화된 데이터 반환."""
    result = {
        'path': filepath,
        'session_id': os.path.splitext(os.path.basename(filepath))[0],
        'agent': '',
        'messages': [],          # {role, text, timestamp}
        'tool_calls': [],         # {name, command, timestamp, msg_idx}
        'compactions': [],        # {summary, timestamp}
        'model': '',
        'start_time': None,
        'end_time': None,
    }

    # agent 이름 추출 (경로에서)
    parts = filepath.split(os.sep)
    for i, p in enumerate(parts):
        if p == 'agents' and i + 1 < len(parts):
            result['agent'] = parts[i + 1]
            break

    msg_idx = 0
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    d = json.loads(line)
                except Exception:
                    continue

                ts = d.get('timestamp', '')
                t = d.get('type', '')

                # 세션 시작 메타
                if t == 'session':
                    result['start_time'] = ts
                    continue

                # 모델 스냅샷
                if t == 'custom' and d.get('customType') == 'model-snapshot':
                    result['model'] = d.get('data', {}).get('modelId', '')
                    continue

                # 컴팩션
                if t == 'compaction':
                    result['compactions'].append({
                        'summary': d.get('summary', '')[:500],
                        'timestamp': ts,
                    })
                    continue

                # 메시지
                if t == 'message':
                    msg = d.get('message', {})
                    role = msg.get('role', '')
                    content = msg.get('content', [])

                    # 텍스트 추출
                    text_parts = []
                    if isinstance(content, list):
                        for c in content:
                            if not isinstance(c, dict):
                                continue
                            ct = c.get('type', '')

                            # 사용자/어시스턴트 텍스트
                            if ct == 'text':
                                txt = c.get('text', '').strip()
                                if txt:
                                    text_parts.append(txt)

                            # 도구 호출 (toolCall 형식 - 실제 확인된 구조)
                            elif ct == 'toolCall':
                                tool_name = c.get('name', '')
                                args = c.get('arguments', {})
                                cmd = ''
                                if isinstance(args, dict):
                                    # exec 도구: command 필드
                                    cmd = args.get('command', '')
                                    if not cmd:
                                        # 다른 도구 표현
                                        cmd = str(args)[:200]
                                elif isinstance(args, str):
                                    cmd = args[:200]

                                result['tool_calls'].append({
                                    'name': tool_name,
                                    'command': cmd,
                                    'timestamp': ts,
                                    'msg_idx': msg_idx,
                                })

                            # 구형 tool_use 형식 (하위 호환)
                            elif ct == 'tool_use':
                                tool_name = c.get('name', '')
                                inp = c.get('input', {})
                                cmd = inp.get('command', str(inp)[:200]) if isinstance(inp, dict) else str(inp)[:200]
                                result['tool_calls'].append({
                                    'name': tool_name,
                                    'command': cmd,
                                    'timestamp': ts,
                                    'msg_idx': msg_idx,
                                })

                    full_text = ' '.join(text_parts)
                    if role or full_text:
                        result['messages'].append({
                            'role': role,
                            'text': full_text,
                            'timestamp': ts,
                            'idx': msg_idx,
                        })
                        result['end_time'] = ts
                        msg_idx += 1

    except Exception as e:
        pass

    return result

# ── 좌절감 감지 (시맨틱 휴리스틱 + config 패턴) ────────────
def detect_frustration(session, ko_patterns=None, en_patterns=None, auto_detect=True):
    """
    키워드 매칭이 아닌 대화 패턴으로 사용자 좌절 감지.

    v4.1 신규:
    - config.yaml의 ko/en 패턴을 로드해 언어별로 적용
    - auto_detect=True 시 첫 10개 user 메시지로 언어 자동 감지
    - >50% 한글 → ko 패턴, 그 외 → en 패턴

    접근법:
    - 짧고 반복적인 재요청 패턴
    - 이전 발화와 의미적으로 유사한 요청이 재등장
    - 부정/수정 신호 + 맥락 확인 (단순 요청어와 구분)
    - 동일 주제에서 user→assistant 교환 횟수
    """
    events = []
    messages = session['messages']
    n = len(messages)

    # ── 언어 자동 감지 (v4.1) ────────────────────────────
    lang = detect_session_language(session) if auto_detect else 'ko'

    # ── config.yaml 기반 키워드 패턴 (언어별 선택) ──────
    config_keywords = (ko_patterns or []) if lang == 'ko' else (en_patterns or [])
    # 키워드 → 정규식 패턴 변환 (신뢰도 0.65)
    config_frustration_patterns = [
        (re.escape(kw), 'config_keyword', 0.65)
        for kw in config_keywords
        if kw  # 빈 문자열 제외
    ]

    # ── 구조적 휴리스틱 패턴 (언어별) ───────────────────
    # 한국어: 재요청, 실망, 반복 지시
    ko_heuristic_patterns = [
        # 재요청 패턴 (에이전트에게 직접 지시하는 맥락)
        (r'다시\s*(해|해줘|해주세요|시작|실행|확인|봐)', 'retry_request', 0.7),
        (r'(아까|저번에|방금|전에)\s*(말|얘기|했잖|했는데|했어)', 'context_loss', 0.9),
        (r'왜\s*(또|이렇게|안|못)', 'repeated_failure', 0.8),
        (r'(제대로|똑바로|정확히|올바르게)\s*(해|해줘|해주|좀)', 'quality_complaint', 0.7),
        (r'(틀렸|잘못됐|오류|에러|실패).{0,20}(또|계속|왜|다시)', 'persistent_error', 0.85),
        (r'내\s*말\s*(무시|못\s*들어|이해\s*못)', 'comprehension_fail', 0.95),
        (r'(이게\s*뭐야|뭘\s*하는\s*거야|뭔\s*짓)', 'confusion_frustration', 0.8),
        (r'(그게\s*아니라|그거\s*말고|다른\s*거)', 'misdirection', 0.6),
        (r'(몇\s*번|몇\s*번을|몇\s*번이나|또|계속)\s*(말|얘기|설명|했)', 'repetition_complaint', 0.9),
    ]
    # 영어: 수정 요청, 반복 지시, 중단 명령
    en_heuristic_patterns = [
        (r"(that'?s\s+wrong|incorrect|wrong\s+again|not\s+what\s+i\s+(asked|said|meant))", 'correction', 0.7),
        (r'(again|once\s+more|as\s+i\s+(said|mentioned|told\s+you))', 'repetition_en', 0.6),
        (r'(stop|why\s+(are\s+you|keep|do\s+you))\s+\w+ing', 'stop_command', 0.75),
        (r'(you\s+forgot|you\s+already|i\s+told\s+you)', 'context_loss_en', 0.85),
        (r'(same\s+mistake|keep\s+doing|still\s+broken|still\s+not\s+working)', 'persistent_error_en', 0.8),
        (r"(not\s+what\s+i\s+asked|that'?s\s+not\s+right|try\s+again)", 'correction_en', 0.7),
        (r'how\s+many\s+times', 'repetition_complaint_en', 0.9),
        (r'stop\s+doing\s+that', 'stop_command_en', 0.8),
    ]

    # 언어에 따라 휴리스틱 패턴 선택 (+ config 패턴 합산)
    frustration_patterns = (
        ko_heuristic_patterns if lang == 'ko' else en_heuristic_patterns
    ) + config_frustration_patterns

    # 연속 메시지 창에서 패턴 감지
    user_msgs = [(i, m) for i, m in enumerate(messages) if m['role'] == 'user']

    for seq_idx, (msg_i, msg) in enumerate(user_msgs):
        text = msg['text']

        # 빈 메시지 또는 시스템 메시지 스킵
        if not text or len(text) > 3000:
            continue

        # 시스템 자동 메시지 제외 (cron 하트비트, 컴팩션 플러시 등)
        system_prefixes = (
            'Pre-compaction',
            'HEARTBEAT',
            'Read HEARTBEAT',
            'Conversation info (untrusted',
            '<<<EXTERNAL_UNTRUSTED',
            'Untrusted context',
            '[System Message]',   # OpenClaw 내부 시스템 메시지
            'System: [',          # cron 시스템 메시지
        )
        if any(text.startswith(p) for p in system_prefixes):
            continue
        # untrusted metadata 포함 메시지도 제외 (에이전트가 수신하는 채널 메타)
        if 'UNTRUSTED' in text or 'untrusted metadata' in text.lower():
            continue
        # 타임스탬프 접두사가 붙은 시스템 메시지 필터 (예: "[Tue ...] [System Message]")
        if '[System Message]' in text[:200]:
            continue
        # sessionId가 포함된 OpenClaw 내부 메시지
        if '[sessionId:' in text[:200]:
            continue

        # Discord/채널 헤더 제거 후 실제 사용자 텍스트 추출
        clean_text = re.sub(r'\[Discord[^\]]*\][^\n]*\n', '', text)
        clean_text = re.sub(r'\[from:[^\]]*\]', '', clean_text)
        clean_text = re.sub(r'<<<[^>]*?>>>', '', clean_text, flags=re.DOTALL)
        clean_text = re.sub(r'\[message_id:[^\]]*\]', '', clean_text)
        # Telegram/채널 헤더 제거
        clean_text = re.sub(r'^\[[^\]]{5,80}\]\s*\n', '', clean_text, flags=re.MULTILINE)
        clean_text = clean_text.strip()

        # 정리 후 실질 내용이 없거나 너무 짧으면 스킵
        if not clean_text or len(clean_text) < 5:
            continue
        # 순수 JSON이면 스킵 (채널 메타 잔여물)
        if clean_text.startswith('{') or clean_text.startswith('['):
            try:
                json.loads(clean_text)
                continue  # 파싱되면 JSON → 스킵
            except Exception:
                pass

        for pattern, ptype, confidence in frustration_patterns:
            if re.search(pattern, clean_text, re.IGNORECASE):
                # 맥락 확인: 바로 앞의 assistant 메시지와의 관계
                # 이전 1-2개 메시지가 assistant 응답인지 확인
                is_directed_at_agent = False
                if seq_idx > 0:
                    # 직전 메시지가 assistant라면 에이전트에게 향한 것
                    prev_i, prev_m = user_msgs[seq_idx - 1] if seq_idx > 0 else (0, {})
                    if msg_i > 0:
                        prev_msg = messages[msg_i - 1]
                        if prev_msg.get('role') == 'assistant':
                            is_directed_at_agent = True
                else:
                    # 첫 메시지면 에이전트 맥락 아님
                    pass

                # 독립 대화에서도 패턴이 강하면 감지
                effective_confidence = confidence if is_directed_at_agent else confidence * 0.5

                if effective_confidence >= 0.5:
                    severity = 'high' if confidence >= 0.85 else ('medium' if confidence >= 0.7 else 'low')
                    context_preview = clean_text[:120].replace('\n', ' ')
                    events.append({
                        'session': session['session_id'],
                        'agent': session.get('agent', ''),
                        'pattern': ptype,
                        'context': context_preview,
                        'severity': severity,
                        'confidence': round(effective_confidence, 2),
                        'directed_at_agent': is_directed_at_agent,
                        'timestamp': msg.get('timestamp', ''),
                    })
                    break  # 메시지당 하나의 이벤트

    return events

# ── Exec 재시도 루프 감지 ────────────────────────────────────
def detect_exec_loops(session):
    """
    동일/유사 exec 명령이 3회 이상 연속 실행되는 패턴 감지.
    명령 정규화 후 비교 (변수명, 경로 등 추상화).
    """
    loops = []
    exec_calls = [tc for tc in session['tool_calls'] if tc['name'] == 'exec']

    if len(exec_calls) < 3:
        return loops

    def normalize_cmd(cmd):
        """명령을 추상화해 유사성 비교."""
        # UUID, 타임스탬프 제거
        cmd = re.sub(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', 'UUID', cmd)
        cmd = re.sub(r'\b\d{10,13}\b', 'TIMESTAMP', cmd)
        # 가변 인자 정규화 (숫자 → N)
        cmd = re.sub(r'\b\d+\b', 'N', cmd)
        # 공백 정규화
        cmd = re.sub(r'\s+', ' ', cmd).strip()
        # 첫 토큰 (주 명령어) 추출
        base = cmd.split()[0] if cmd.split() else cmd
        # 전체를 60자로 압축한 서명
        return cmd[:60]

    # 슬라이딩 윈도우로 연속 유사 명령 감지
    normalized = [(tc, normalize_cmd(tc['command'])) for tc in exec_calls]

    i = 0
    while i < len(normalized):
        tc, norm = normalized[i]
        count = 1
        j = i + 1
        while j < len(normalized) and normalized[j][1] == norm:
            count += 1
            j += 1

        if count >= 3:
            loops.append({
                'type': 'exec_loop',
                'session': session['session_id'],
                'agent': session.get('agent', ''),
                'command_base': norm[:80],
                'count': count,
                'examples': [normalized[k][0]['command'][:100] for k in range(i, min(i + 3, j))],
            })

        i = j if j > i else i + 1

    # 비연속이지만 빈번한 동일 명령 (전체 세션에서 5회 이상)
    cmd_freq = defaultdict(list)
    for tc, norm in normalized:
        cmd_freq[norm].append(tc['command'][:100])

    for norm, cmds in cmd_freq.items():
        if len(cmds) >= 5 and not any(l['command_base'] == norm[:80] for l in loops):
            loops.append({
                'type': 'frequent_exec',
                'session': session['session_id'],
                'agent': session.get('agent', ''),
                'command_base': norm[:80],
                'count': len(cmds),
                'examples': cmds[:3],
            })

    return loops

# ── 룰 위반 감지 ────────────────────────────────────────────
def detect_rule_violations(session):
    """
    AGENTS.md 핵심 규칙 위반을 exec 명령 및 응답 패턴에서 감지.
    """
    violations = []

    # exec 명령에서 규칙 위반 패턴
    exec_cmds = [tc['command'] for tc in session['tool_calls'] if tc['name'] == 'exec']

    rule_checks = [
        # git 직접 명령 (git-sync.sh 대신)
        ('git_direct_cmd',
         r'^git\s+(pull|push|rebase|merge)\b',
         'git pull/push 직접 사용 (git-sync.sh 사용해야 함)',
         exec_cmds),

        # rm -rf 사용 (trash 대신)
        ('rm_destructive',
         r'rm\s+(-rf|-f|-r)\s+',
         'rm -rf 사용 (trash 명령 사용 권장)',
         exec_cmds),

        # openclaw gateway 직접 launchctl 조작
        ('gateway_launchctl',
         r'launchctl\s+(bootout|kickstart)',
         'launchctl 직접 사용 (openclaw gateway 명령 사용해야 함)',
         exec_cmds),

        # curl 에러 핸들링 없음
        ('curl_no_fallback',
         r'^\s*curl\s+(?!.*\|\|)(?!.*-sf\s)',
         'curl 실패 핸들링 없음 (|| echo 또는 -sf 사용해야 함)',
         exec_cmds),

        # python/node 에러 핸들링 없음
        ('script_no_fallback',
         r'^\s*(python3?|node)\s+\S+\.(?:py|js)\s*$',
         'Python/Node 스크립트 에러 핸들링 없음 (2>&1 || echo 추가 필요)',
         exec_cmds),
    ]

    for rule_id, pattern, description, targets in rule_checks:
        count = 0
        examples = []
        for target in targets:
            for line in target.split('\n'):
                line = line.strip()
                if line and re.search(pattern, line, re.IGNORECASE | re.MULTILINE):
                    count += 1
                    if len(examples) < 3:
                        examples.append(line[:100])

        if count > 0:
            violations.append({
                'rule': rule_id,
                'violation': description,
                'count': count,
                'examples': examples,
                'session': session['session_id'],
                'agent': session.get('agent', ''),
            })

    # 메시지 단편화 감지 (연속 짧은 assistant 메시지)
    # 단, cron/하트비트 세션 제외 (HEARTBEAT_OK 같은 짧은 응답이 정상인 경우)
    agent_name = session.get('agent', '')
    is_likely_cron = agent_name in ('cron', 'heartbeat') or 'cron' in session.get('path', '').lower()
    if not is_likely_cron:
        assistant_msgs = [m for m in session['messages'] if m['role'] == 'assistant']
        # 실질적 응답만 카운트 (HEARTBEAT_OK, NO_REPLY 등 자동 응답 제외)
        auto_response_patterns = ('HEARTBEAT_OK', 'NO_REPLY', '✅ New session')
        real_assistant_msgs = [
            m for m in assistant_msgs
            if not any(m['text'].startswith(p) for p in auto_response_patterns)
        ]
        short_consecutive = 0
        max_consecutive = 0
        frag_examples = []
        for m in real_assistant_msgs:
            if 0 < len(m['text']) < 80:  # 의미있지만 너무 짧은 응답 (80자 미만)
                short_consecutive += 1
                if short_consecutive > max_consecutive:
                    max_consecutive = short_consecutive
                    frag_examples.append(m['text'][:60])
            else:
                short_consecutive = 0

        if max_consecutive >= 4:
            violations.append({
                'rule': 'msg_fragmentation',
                'violation': f'짧은 assistant 메시지 {max_consecutive}개 연속 (단편화 금지 규칙 위반)',
                'count': max_consecutive,
                'examples': frag_examples[:3],
                'session': session['session_id'],
                'agent': session.get('agent', ''),
            })

    return violations

# ── 루프/컨텍스트 손실 감지 ─────────────────────────────────
def detect_failure_patterns(session):
    """
    실패 패턴: 컨텍스트 손실, 잘못된 도구, 반복 오류.
    """
    patterns = []
    messages = session['messages']

    # 1. 컨텍스트 손실 (Context Loss)
    # 특징: 이미 답한 질문을 다시 묻거나 이미 완료된 작업을 재실행
    compaction_count = len(session['compactions'])
    if compaction_count >= 3:
        patterns.append({
            'type': 'context_loss_risk',
            'session': session['session_id'],
            'agent': session.get('agent', ''),
            'count': compaction_count,
            'detail': f'컴팩션 {compaction_count}회 발생 (컨텍스트 손실 위험)',
        })

    # 2. 고착 루프 (Stuck Loop)
    # 특징: 동일 주제에서 5회 이상 user↔assistant 교환
    if len(messages) >= 10:
        # 주제 클러스터링 (단순 창 기반)
        window_size = 10
        for start in range(0, len(messages) - window_size, 5):
            window = messages[start:start + window_size]
            user_texts = [m['text'][:100] for m in window if m['role'] == 'user' and m['text']]
            asst_texts = [m['text'][:100] for m in window if m['role'] == 'assistant' and m['text']]

            # 유사성 체크: 같은 키워드가 모든 user 메시지에 등장하면 루프
            if len(user_texts) >= 5:
                # 첫 user 메시지의 핵심 단어 추출 (3글자 이상)
                first_words = set(w for w in re.findall(r'\b\w{3,}\b', user_texts[0], re.UNICODE) if not w.isdigit())
                # 다른 user 메시지들에 그 단어가 얼마나 등장하나
                overlap_scores = []
                for ut in user_texts[1:]:
                    ut_words = set(re.findall(r'\b\w{3,}\b', ut, re.UNICODE))
                    overlap = len(first_words & ut_words)
                    overlap_scores.append(overlap)
                avg_overlap = sum(overlap_scores) / len(overlap_scores) if overlap_scores else 0

                if avg_overlap >= 3:  # 평균 3개 이상 공통 단어 = 같은 주제
                    patterns.append({
                        'type': 'stuck_loop',
                        'session': session['session_id'],
                        'agent': session.get('agent', ''),
                        'count': len(user_texts),
                        'detail': f'동일 주제 반복 대화 {len(user_texts)}회 (창 {start}-{start+window_size})',
                        'topic_hint': user_texts[0][:60],
                    })
                    break  # 세션당 1개만

    # 3. 긴 응답 실패 (Hallucination Risk)
    # 특징: 매우 긴 assistant 응답 + 이후 user 수정
    for i, msg in enumerate(messages):
        if msg['role'] == 'assistant' and len(msg['text']) > 2000:
            # 이후 user 메시지에 수정 신호가 있나?
            if i + 1 < len(messages):
                next_msg = messages[i + 1]
                if next_msg['role'] == 'user':
                    next_text = next_msg['text'].lower()
                    correction_signals = ['틀렸', '아니', 'wrong', 'incorrect', '아니야', '그게 아니라']
                    if any(s in next_text for s in correction_signals):
                        patterns.append({
                            'type': 'long_response_correction',
                            'session': session['session_id'],
                            'agent': session.get('agent', ''),
                            'count': 1,
                            'detail': f'긴 응답({len(msg["text"])}자) 후 사용자 수정',
                        })

    return patterns

# ── 품질 점수 계산 ───────────────────────────────────────────
def compute_quality_score(frustration_events, failure_patterns, rule_violations, exec_loops, session_count):
    """
    10점 만점 품질 점수 (낮을수록 문제 많음).
    """
    if session_count == 0:
        return 7.0

    base = 8.0  # 기준점

    # 좌절 이벤트 패널티
    high = sum(1 for e in frustration_events if e['severity'] == 'high')
    med  = sum(1 for e in frustration_events if e['severity'] == 'medium')
    low  = sum(1 for e in frustration_events if e['severity'] == 'low')
    frustration_penalty = (high * 0.3 + med * 0.15 + low * 0.05) / max(session_count, 1)

    # exec 루프 패널티
    exec_penalty = sum(min(l['count'] / 10, 0.5) for l in exec_loops) / max(session_count, 1)

    # 실패 패턴 패널티
    failure_penalty = len(failure_patterns) * 0.1 / max(session_count, 1)

    # 규칙 위반 패널티
    violation_penalty = sum(min(v['count'] / 5, 0.3) for v in rule_violations) / max(session_count, 1)

    score = base - frustration_penalty - exec_penalty - failure_penalty - violation_penalty
    return round(max(1.0, min(10.0, score)), 1)

# ── 핵심 인사이트 생성 ──────────────────────────────────────
def generate_insights(frustration_events, failure_patterns, rule_violations, exec_loops, sessions_data):
    """분석 결과에서 실행 가능한 인사이트 도출."""
    insights = []

    # 좌절 패턴 분석
    if frustration_events:
        top_patterns = defaultdict(int)
        for e in frustration_events:
            top_patterns[e['pattern']] += 1
        most_common = sorted(top_patterns.items(), key=lambda x: -x[1])[:2]
        for ptype, cnt in most_common:
            ptype_map = {
                'context_loss': '컨텍스트 손실 (이전 내용 망각)',
                'retry_request': '반복 재요청 (첫 시도 실패)',
                'comprehension_fail': '의도 파악 실패',
                'misdirection': '엉뚱한 방향으로 진행',
                'persistent_error': '지속적 오류 미수정',
                'correction': '사용자 수정 필요',
                'repetition_complaint': '반복 설명 필요',
                'repeated_failure': '반복 실패 (왜 또/왜 안 되나)',
                'quality_complaint': '품질 불만 (제대로/똑바로 해달라)',
                'confusion_frustration': '혼란/당황 (이게 뭐야)',
                'repetition_en': '반복 설명 필요 (영어)',
                'stop_command': '중단 요청',
            }
            friendly = ptype_map.get(ptype, ptype)
            insights.append(f"좌절 주패턴: '{friendly}' ({cnt}회) — 루프 방지 메커니즘 강화 필요")

    # exec 루프 분석
    if exec_loops:
        worst = max(exec_loops, key=lambda x: x['count'])
        insights.append(
            f"Exec 루프 감지: '{worst['command_base'][:50]}' {worst['count']}회 반복 — "
            f"실패 후 자동 중단 로직 필요"
        )

    # 컴팩션 패턴
    high_compact = [s for s in sessions_data if len(s['compactions']) >= 3]
    if high_compact:
        avg_compact = sum(len(s['compactions']) for s in high_compact) / len(high_compact)
        insights.append(
            f"컨텍스트 팽창: {len(high_compact)}개 세션에서 평균 {avg_compact:.1f}회 컴팩션 — "
            f"작업 분리 (cron 위임) 개선 필요"
        )

    # 규칙 위반
    if rule_violations:
        top_viol = sorted(rule_violations, key=lambda x: -x['count'])[:2]
        for v in top_viol:
            insights.append(f"규칙 위반: '{v['violation']}' ({v['count']}건) — AGENTS.md 숙지 강화 필요")

    # 실패 패턴
    stuck = [p for p in failure_patterns if p['type'] == 'stuck_loop']
    if stuck:
        insights.append(f"고착 루프: {len(stuck)}개 세션에서 같은 주제 반복 — 접근법 전환 판단 기준 필요")

    # 이슈 없음
    if not insights:
        insights.append("분석 기간 중 주요 이슈 없음 — 정상 동작 중")

    return insights

# ── 메인 실행 ───────────────────────────────────────────────
def main():
    # 규칙 로드
    agents_rules = load_agents_rules()

    # config.yaml 불만 패턴 로드 (v4.1: ko/en 분리 + auto_detect)
    ko_patterns, en_patterns, auto_detect = load_config_patterns(SKILL_DIR)
    print(f"[분석기] 불만 패턴 로드: ko={len(ko_patterns)}개, en={len(en_patterns)}개, auto_detect={auto_detect}", file=sys.stderr)

    # 세션 파일 수집
    session_files = collect_session_files()
    total_files = len(session_files)
    print(f"[분석기] 세션 파일 {total_files}개 수집됨", file=sys.stderr)

    if not session_files:
        # 데이터 없음 — 기본 구조 출력
        result = {
            'sessions_analyzed': 0,
            'frustration_events': [],
            'failure_patterns': [],
            'rule_violations': [],
            'exec_loops': [],
            'quality_score': 7.0,
            'key_insights': ['세션 데이터 없음 — 분석 불가 (agents 디렉토리 확인 필요)'],
            'metadata': {
                'analyzed_at': datetime.now(timezone.utc).isoformat(),
                'analysis_days': ANALYSIS_DAYS,
                'agents_dir': AGENTS_DIR,
                'error': 'no_sessions_found',
            }
        }
        with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        return result

    # 세션별 분석
    all_frustration = []
    all_failure = []
    all_violations = []
    all_exec_loops = []
    sessions_data = []

    for i, fpath in enumerate(session_files):
        print(f"[분석기] {i+1}/{total_files} 파싱: {os.path.basename(fpath)}", file=sys.stderr)
        session = parse_session(fpath)
        sessions_data.append(session)

        # 시맨틱 분석 실행 (v4.1: 언어별 패턴 전달)
        frustration  = detect_frustration(session, ko_patterns, en_patterns, auto_detect)
        exec_loops   = detect_exec_loops(session)
        violations   = detect_rule_violations(session)
        failures     = detect_failure_patterns(session)

        all_frustration.extend(frustration)
        all_exec_loops.extend(exec_loops)
        all_violations.extend(violations)
        all_failure.extend(failures)

    # 중복 제거 및 집계
    # 규칙 위반: 세션 없이 집계
    violation_agg = defaultdict(lambda: {'rule': '', 'violation': '', 'count': 0, 'examples': [], 'sessions': []})
    for v in all_violations:
        key = v['rule']
        violation_agg[key]['rule'] = v['rule']
        violation_agg[key]['violation'] = v['violation']
        violation_agg[key]['count'] += v['count']
        violation_agg[key]['examples'].extend(v['examples'][:2])
        if v['session'] not in violation_agg[key]['sessions']:
            violation_agg[key]['sessions'].append(v['session'])

    # 실패 패턴: 타입별 집계
    failure_agg = defaultdict(lambda: {'type': '', 'count': 0, 'examples': []})
    for p in all_failure:
        key = p['type']
        failure_agg[key]['type'] = p['type']
        failure_agg[key]['count'] += 1
        if 'detail' in p:
            failure_agg[key]['examples'].append({'session': p['session'], 'detail': p['detail'][:100]})

    # 품질 점수
    quality_score = compute_quality_score(
        all_frustration, all_failure, all_violations, all_exec_loops, total_files
    )

    # 핵심 인사이트
    insights = generate_insights(
        all_frustration, all_failure,
        list(violation_agg.values()), all_exec_loops, sessions_data
    )

    # 세션별 요약
    session_summaries = []
    for s in sessions_data:
        session_summaries.append({
            'id': s['session_id'],
            'agent': s['agent'],
            'model': s['model'],
            'messages': len(s['messages']),
            'tool_calls': len(s['tool_calls']),
            'compactions': len(s['compactions']),
            'start': s['start_time'],
            'end': s['end_time'],
        })

    # 최종 결과
    result = {
        'sessions_analyzed': total_files,
        'frustration_events': sorted(all_frustration, key=lambda x: {'high': 0, 'medium': 1, 'low': 2}[x['severity']])[:20],
        'failure_patterns': [dict(v) for v in failure_agg.values()],
        'rule_violations': [
            {k: val for k, val in v.items() if k != 'sessions'}
            for v in sorted(violation_agg.values(), key=lambda x: -x['count'])
        ],
        'exec_loops': sorted(all_exec_loops, key=lambda x: -x['count'])[:10],
        'quality_score': quality_score,
        'key_insights': insights,
        'session_summaries': session_summaries[:10],
        'metadata': {
            'analyzed_at': datetime.now(timezone.utc).isoformat(),
            'analysis_days': ANALYSIS_DAYS,
            'max_sessions': MAX_SESSIONS,
            'agents_dir': AGENTS_DIR,
            'version': 'v4.1',
        }
    }

    # JSON 저장
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"[분석기] 저장 완료: {OUTPUT_JSON}", file=sys.stderr)
    return result

result = main()
PYEOF

# Python3 분석 완료 확인
ANALYSIS_EXIT=$?
if [ $ANALYSIS_EXIT -ne 0 ]; then
  echo "[ERROR] Python 분석 실패 (exit $ANALYSIS_EXIT)" >&2
  # 빈 결과 생성해서 후속 스텝이 깨지지 않게
  cat > /tmp/sea-v4/analysis.json << 'EMPTY'
{
  "sessions_analyzed": 0,
  "frustration_events": [],
  "failure_patterns": [],
  "rule_violations": [],
  "exec_loops": [],
  "quality_score": 7.0,
  "key_insights": ["분석 스크립트 실행 오류"],
  "metadata": {"error": "python_failed"}
}
EMPTY
fi 2>/dev/null || true

# ── LLM 프롬프트 생성 (stdout으로 출력) ─────────────────────
# 오케스트레이터가 이 출력을 캡처해 LLM 시맨틱 분석에 활용
log "=== LLM 시맨틱 분석 프롬프트 생성 중 ==="

# analysis.json 요약 읽기
ANALYSIS_SUMMARY=""
if [ -f "/tmp/sea-v4/analysis.json" ]; then
  QUALITY=$(python3 -c "
import json
try:
    d = json.load(open('/tmp/sea-v4/analysis.json'))
    print(d.get('quality_score', '?'))
except:
    print('?')
" 2>/dev/null || echo "?")

  SESSION_COUNT=$(python3 -c "
import json
try:
    d = json.load(open('/tmp/sea-v4/analysis.json'))
    print(d.get('sessions_analyzed', 0))
except:
    print(0)
" 2>/dev/null || echo "0")

  INSIGHTS=$(python3 -c "
import json
try:
    d = json.load(open('/tmp/sea-v4/analysis.json'))
    insights = d.get('key_insights', [])
    for ins in insights[:5]:
        print(f'  - {ins}')
except:
    pass
" 2>/dev/null || true)

  FRUSTRATION_COUNT=$(python3 -c "
import json
try:
    d = json.load(open('/tmp/sea-v4/analysis.json'))
    print(len(d.get('frustration_events', [])))
except:
    print(0)
" 2>/dev/null || echo "0")

  VIOLATIONS_COUNT=$(python3 -c "
import json
try:
    d = json.load(open('/tmp/sea-v4/analysis.json'))
    total = sum(v.get('count', 0) for v in d.get('rule_violations', []))
    print(total)
except:
    print(0)
" 2>/dev/null || echo "0")
fi

# ── stdout 프롬프트 출력 ────────────────────────────────────
# 오케스트레이터가 이 텍스트를 LLM에 전달해 최종 시맨틱 해석 수행
cat << PROMPT_EOF

=== SEA v4.1 시맨틱 분석 결과 (휴리스틱 전처리 완료, 언어 자동 감지 적용) ===

분석 기간: ${ANALYSIS_DAYS}일
분석된 세션 수: ${SESSION_COUNT:-0}개
현재 품질 점수 (휴리스틱 기준): ${QUALITY:-?}/10.0

## 발견된 주요 패턴
${INSIGHTS:-  - 데이터 부족}

## 감지된 이벤트 수
- 사용자 좌절 이벤트: ${FRUSTRATION_COUNT:-0}건
- 규칙 위반: ${VIOLATIONS_COUNT:-0}건
- 상세 데이터: /tmp/sea-v4/analysis.json

## LLM 시맨틱 검증 요청

아래 사항들을 /tmp/sea-v4/analysis.json의 원시 데이터를 참고해 시맨틱하게 재검증해주세요:

1. **좌절 이벤트 재평가**: 휴리스틱이 감지한 패턴들이 실제로 에이전트 실패 때문인지,
   아니면 단순 대화 흐름인지 맥락을 보고 판단해주세요.
   - "다시"가 에이전트 실패 재요청인지 vs 새 작업 시작인지
   - "아까 말했잖아"가 진짜 컨텍스트 손실인지 vs 보충 설명인지

2. **실패 패턴 심각도**: 감지된 exec 루프, 고착 루프가 실제 문제인지 아니면
   반복 작업 특성상 정상인지 판단해주세요.

3. **규칙 위반 맥락**: 감지된 위반이 실제로 AGENTS.md를 어긴 것인지,
   아니면 불가피한 예외적 상황인지 판단해주세요.

4. **개선 우선순위**: 위 분석을 종합해 가장 시급하게 개선할 항목 3개를 선정하고
   구체적인 rule proposal을 제시해주세요.

분석 원본: /tmp/sea-v4/analysis.json
AGENTS.md: ~/openclaw/AGENTS.md

=== END OF SEMANTIC ANALYSIS PROMPT ===

PROMPT_EOF

log "=== SEA v4.1 시맨틱 분석기 완료 (언어 자동 감지 포함) ==="
log "출력 파일: $OUTPUT_JSON"
