# Self-Evolving Agent — 아키텍처 문서 v2.0

> 작성: 2026-02-17 | 기술 아키텍트 리뷰 기반

---

## 1. 개요

Self-Evolving Agent는 AI 비서의 대화 기록을 주기적으로 분석하여, 행동 규칙(AGENTS.md)의 개선안을 자동으로 제안하는 자동화 파이프라인이다.

```
                ┌──────────────────────────────────────────────────┐
                │           Self-Evolving Agent 파이프라인          │
                │                                                  │
  세션 기록       │  analyze-behavior.sh  →  generate-proposal.sh   │
  .learnings/   │          ↓                        ↓              │
  MEMORY.md     │     분석 JSON                  Discord 리포트     │
  크론 에러      │                                                  │
                │         사용자 승인 → AGENTS.md 반영              │
                └──────────────────────────────────────────────────┘
```

---

## 2. 파일 구조

```
skills/self-evolving-agent/
├── SKILL.md                          # 스킬 메타데이터 + 설치 가이드
├── README.md                         # ClawHub 배포용 공개 문서
├── config.yaml                       # 🆕 설정 파일 (v2.0)
│
├── scripts/
│   ├── analyze-behavior.sh           # 행동 분석기 (JSON 출력)
│   ├── generate-proposal.sh          # 개선안 생성기 (Discord 출력)
│   ├── register-cron.sh              # 크론 등록/업데이트/제거
│   └── lib/
│       └── config-loader.sh          # 🆕 config.yaml 파서
│
├── templates/
│   └── proposal-template.md          # 제안 형식 참조
│
├── data/                             # 런타임 데이터 (자동 생성)
│   ├── proposals/                    # 생성된 제안 JSON
│   │   └── archive/                  # 🆕 만료 제안 아카이브
│   └── rejected-proposals.json       # 거부된 제안 + 이유
│
└── docs/
    └── architecture.md               # 이 파일
```

---

## 3. 데이터 플로우

### 3.1 전체 파이프라인

```
[크론: 매주 일요일 22:00]
        │
        ▼
generate-proposal.sh
        │
        ├─► analyze-behavior.sh ──────────────────────┐
        │       │                                     │
        │       ├─ ~/.openclaw/agents/*/sessions/*.jsonl ← 세션 기록
        │       ├─ ~/.openclaw/cron/jobs.json           ← 크론 에러
        │       ├─ ~/.openclaw/logs/*.log               ← 로그 파일
        │       ├─ ~/openclaw/.learnings/               ← self-improving-agent
        │       └─ ~/openclaw/MEMORY.md                 ← 장기 메모리
        │               │
        │               ▼
        │       /tmp/self-evolving-analysis.json (중간 결과)
        │               │
        ├───────────────┘
        │
        ├─► 제안 생성 (Python)
        │       │
        │       ├─ 불만 패턴 → 규칙 강화 제안
        │       ├─ 크론 에러 → 알림 규칙 제안
        │       ├─ 위반 패턴 → 규칙 강화 제안
        │       ├─ .learnings/ → 미해결 이슈 승격 제안  ← 🆕
        │       ├─ 반복 요청 → 템플릿 자동화 제안
        │       └─ MEMORY.md → 정리 제안               ← 🆕
        │
        ├─► data/proposals/proposal_YYYYMMDD_HHMMSS.json (저장)
        │
        └─► Discord #your-channel 리포트 출력
```

### 3.2 데이터 흐름 세부 사항

```
bash → Python 데이터 전달 방식 (v2.0 핵심 설계 결정)

❌ v1.x 방식 (버그 있음):
   learnings_json="${json_output}"
   python3 << PYEOF
   data = ${learnings_json}   # JSON true/false → Python NameError!
   PYEOF

✅ v2.0 방식 (안전):
   echo "${json_output}" > /tmp/sea-$$/learnings.json
   python3 << PYEOF
   with open('/tmp/sea-$$/learnings.json') as f:
       data = json.load(f)   # 올바른 JSON 파싱
   PYEOF
```

---

## 4. 컴포넌트 상세

### 4.1 analyze-behavior.sh

**역할:** 다양한 소스에서 데이터를 수집·분석하여 JSON 출력

**입력 소스 (v2.0)**

| 소스 | 경로 | 분석 내용 |
|------|------|---------|
| 세션 트랜스크립트 | `~/.openclaw/agents/*/sessions/*.jsonl` | 사용자 불만 패턴, 위반 패턴, 반복 요청 |
| 크론 상태 | `~/.openclaw/cron/jobs.json` | consecutiveErrors > 0 |
| 로그 파일 | `~/.openclaw/logs/` | error/failed/exception 패턴 |
| .learnings/ | `~/openclaw/.learnings/` | 미해결 ERR/LRN/FEAT 항목 |
| MEMORY.md | `~/openclaw/MEMORY.md` | 이슈/TODO 패턴 |

**분석 알고리즘**

```
불만 패턴 감지:
  v1.x: str.count(pattern) → 중복 문장 포함
  v2.0: 문장 단위 분리 → seen_sentences 중복 제거 → 더 정확한 카운트

세션 정렬:
  v1.x: xargs ls -t → macOS 전용
  v2.0: Python os.path.getmtime() → 크로스플랫폼

정렬 데이터 전달:
  v1.x: printf ... | sort_by_mtime  → heredoc이 stdin 점유 → 빈 결과 버그
  v2.0: 임시 파일 → sort_by_mtime_file → 올바른 결과
```

**출력 JSON 구조 (v2.0)**

```json
{
  "meta": {
    "analysis_date": "YYYY-MM-DD",
    "analysis_timestamp": "ISO8601",
    "analysis_days": 7,
    "session_count": 30,
    "version": "2.0.0"
  },
  "complaints": {
    "session_count": 30,
    "total_complaint_hits": 61,
    "patterns": [{"pattern": "다시", "count": 22}]
  },
  "errors": {
    "cron_errors": [{"name": "크론명", "consecutive_errors": 1}],
    "log_errors": [{"file": "파일명", "error_count": 18, "recent_samples": [...]}]
  },
  "violations": {
    "violations": [{"rule": "규칙명", "pattern": "regex", "hit_count": 13, "severity": "high"}]
  },
  "repeat_requests": [{"phrase": "확인해줘", "count": 25}],
  "learnings": {
    "total_pending": 0,
    "total_high_priority": 0,
    "top_errors": [],
    "top_learnings": [],
    "feature_requests": []
  },
  "memory_md": {
    "exists": true,
    "issue_count": 6,
    "patterns": ["문제: ...", "⚠️ ..."],
    "word_count": 768
  },
  "previously_rejected": []
}
```

---

### 4.2 generate-proposal.sh

**역할:** 분석 JSON을 읽어 Discord 리포트 생성

**제안 소스 우선순위**

| 순위 | 소스 | 트리거 조건 |
|------|------|----------|
| 1 | 사용자 불만 패턴 | total_complaint_hits ≥ 2 |
| 2 | 크론 에러 | consecutiveErrors > 0 |
| 3 | AGENTS.md 위반 | hit_count ≥ min_hits |
| 4 | .learnings/ 고우선순위 | total_high_priority > 0 |
| 5 | .learnings/ 미처리 | total_pending > 5 |
| 6 | 반복 요청 | count ≥ 5 |
| 7 | MEMORY.md 이슈 | issue_count > 3 |

**v1.x → v2.0 핵심 수정**

```
1. get_date_range() 버그 수정
   v1.x: macOS date -v / Linux date -d 분기 → 실제로 date_from 미반환
   v2.0: Python datetime.timedelta → 크로스플랫폼 보장

2. set -euo pipefail 제거
   이유: Python 서브프로세스 실패 시 크론 에러 노출 (AGENTS.md 규칙)
   대안: 각 단계별 || echo "fallback" 패턴

3. 제안 JSON → Python 전달
   v1.x: proposals = $proposals_json (인라인 → NameError 위험)
   v2.0: echo "$json" > /tmp/파일 → python3 with open() 로드

4. 소스 표시 이모지 추가
   각 제안의 출처를 source_emoji로 명시 (가독성 향상)

5. 만료 제안 아카이브
   expire_days 설정으로 오래된 제안 자동 정리
```

---

### 4.3 config-loader.sh

**역할:** `config.yaml`을 bash 환경변수로 파싱

**설계 결정:**
- bash에서 YAML을 직접 파싱하기 어려우므로 Python 위임
- PyYAML 미설치 환경을 위해 간단한 라인 파서 폴백 내장
- 모든 설정에 환경변수 오버라이드 지원 (CI/테스트 환경)

```bash
# 환경변수 우선순위:
# 1. 직접 환경변수 (ANALYSIS_DAYS, AGENTS_DIR 등)
# 2. config.yaml 값 (SEA_* prefix)
# 3. 스크립트 기본값
```

**노출 변수**

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `SEA_DAYS` | 7 | 분석 기간 (일) |
| `SEA_MAX_SESSIONS` | 30 | 최대 세션 수 |
| `SEA_INCLUDE_MEMORY` | true | MEMORY.md 포함 여부 |
| `SEA_COMPLAINT_MIN` | 2 | 불만 패턴 최소 감지 수 |
| `SEA_REPEAT_MIN` | 3 | 반복 요청 최소 횟수 |
| `SEA_CRON_SCHEDULE` | `0 22 * * 0` | 크론 스케줄 |
| `SEA_MODEL` | sonnet-4-5 | 사용 모델 |
| `SEA_DISCORD_CHANNEL` | `YOUR_CHANNEL_ID` | 결과 채널 |
| `SEA_COMPLAINT_PATTERNS` | (한국어 목록) | 불만 패턴 (쉼표 구분) |
| `SEA_LOG_FILES` | (로그 목록) | 분석 대상 로그 |
| `SEA_LEARNINGS_PATHS` | (경로 목록) | .learnings/ 경로 |

---

### 4.4 register-cron.sh

**역할:** OpenClaw 크론 시스템에 주간 분석 작업 등록

**v2.0 개선 사항:**
- `--update` 플래그: 기존 크론 설정 업데이트
- `--remove` 플래그: 크론 안전 제거
- config.yaml에서 스케줄/모델/채널 읽기
- 크론 파일 JSON 유효성 사전 확인
- 실패 시 명확한 에러 메시지

---

## 5. self-improving-agent 연동

### 5.1 연동 구조

```
self-improving-agent                    self-evolving-agent
─────────────────────────────          ─────────────────────────────
대화 중 에러/교정 발생               →  .learnings/ 파일 감지
        │                                       │
        ▼                                       ▼
.learnings/ERRORS.md                   analyze-behavior.sh
.learnings/LEARNINGS.md                read_learnings() 함수
.learnings/FEATURE_REQUESTS.md         │
                                       ▼
                                  learnings 분석 결과
                                       │
                                       ▼
                               generate-proposal.sh
                               제안 소스 4, 5번 활용
                                       │
                                       ▼
                               Discord: "미해결 고우선순위 이슈"
                               → 사용자가 AGENTS.md 승격 결정
```

### 5.2 연동 원칙 (중복 방지)

| 역할 | self-improving-agent | self-evolving-agent |
|------|---------------------|---------------------|
| 이슈 감지 | ✅ (대화 중 실시간) | ❌ |
| 이슈 기록 | ✅ (.learnings/) | ❌ |
| 이슈 분석 | ❌ | ✅ (주간 배치) |
| 규칙 제안 | ❌ | ✅ |
| AGENTS.md 승격 | ❌ | ✅ (사용자 승인 후) |

---

## 6. 성능 설계

### 6.1 대규모 세션 처리 (1000+ 세션)

```
문제: 세션이 1000개 이상이면 전부 분석 시 느림

해결:
1. find -newer 필터 → 최근 N일만 (기본 7일)
2. sort_by_mtime_file → Python mtime 정렬 후 상위 30개만
3. MAX_SESSIONS=0 설정 → 제한 없음 (전체 분석, 느림)

시간 복잡도:
  세션 파일 탐색: O(N) → find 명령
  정렬: O(K log K) K = 최근 N일 세션 수
  분석: O(M) M = MAX_SESSIONS 수
```

### 6.2 임시 파일 관리

```bash
# run_analysis에서 trap으로 자동 정리
local tmp_dir="/tmp/sea-$$"
trap 'rm -rf "$tmp_dir"' EXIT INT TERM
```

---

## 7. 에러 핸들링 전략

### 7.1 AGENTS.md 규칙 준수

```
규칙: "exec는 절대로 실패하면 안 된다"
→ 크론에서 이 스크립트가 실패하면 Discord에 에러 노출됨

대응:
1. set -euo pipefail 사용 금지 (generate-proposal.sh)
2. Python 서브프로세스는 항상 2>/dev/null || fallback 패턴
3. analyze-behavior.sh 실패 시 fallback JSON 생성
4. 빈 proposals → 기본 "이번 주 이상 없음" 메시지
```

### 7.2 단계별 에러 격리

```
analyze-behavior.sh 실패
    → fallback JSON 생성 (빈 구조)
    → generate-proposal.sh는 계속 실행

generate_proposals() 실패
    → no-issues-found 기본 메시지
    → 스크립트는 계속 실행

save_proposal() 실패
    → 저장 실패 로그 (stderr)
    → Discord 출력은 계속

build_report() 실패
    → 내부 Python 예외 처리
    → 최소한 헤더는 출력
```

---

## 8. 크로스플랫폼 호환성

### 8.1 macOS (bash 3.2) 호환

```bash
# ❌ bash 4+ 전용 (macOS 기본 bash 3.2에서 동작 안 함)
declare -A assoc_array

# ✅ 호환 방식
python3 -c "import json; ..."   # Python으로 위임
```

### 8.2 macOS/Linux 공통 패턴

| 작업 | macOS | Linux | v2.0 해결 |
|------|-------|-------|---------|
| 날짜 계산 | `date -v -7d` | `date -d "7 days ago"` | Python datetime |
| 파일 정렬 | `ls -t` (macOS 특화) | `ls -t` | Python `os.path.getmtime()` |
| 기준 시간 파일 | `python3 -c "os.utime..."` | 동일 | Python (공통) |

---

## 9. 보안 및 안전 원칙

1. **제안만 함** — 사용자 승인 없이 AGENTS.md 직접 수정 금지
2. **개인정보 노출 방지** — transcript 전체를 Discord에 올리지 않음 (패턴 요약만)
3. **임시 파일 정리** — `trap EXIT` + PID 기반 파일명으로 충돌 방지
4. **거부 학습** — `rejected-proposals.json`에 거부 이유 기록, 재제시 방지

---

## 10. 향후 개선 방향

### v2.1 계획
- [ ] `config.yaml` PyYAML 미설치 시 간단 파서 개선 (현재: 스칼라 값만)
- [ ] `.learnings/` 항목별 우선순위 가중치 조정
- [ ] 제안 ID 중복 방지 (현재: 항상 동일 ID 생성)

### v3.0 장기 목표
- [ ] LLM 기반 패턴 분석 (단순 grep → 의미론적 분석)
- [ ] 자동 승인 옵션 (low severity 제안은 자동 적용)
- [ ] ClawHub 배포 표준화

---

*최종 수정: 2026-02-17 | Self-Evolving Agent v2.0 아키텍처 리뷰*
