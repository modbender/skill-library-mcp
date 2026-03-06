# SEA v5.0 Architecture — Multi-Agent Fleet Analysis

> **v5.0 핵심**: 단일 에이전트 자기 분석 → **모든 에이전트 동시 분석 + 교차 학습**

## 개요

SEA(Self-Evolving Agent) v5.0은 OpenClaw 설정의 **모든 에이전트를 동시에 분석**하고,
에이전트 간 비교·공통 패턴·규칙 이전을 통해 전체 플릿을 체계적으로 개선하는 엔진입니다.

```
v4.0 (단일): opus → 자기분석 → 제안 → AGENTS.md 업데이트
v5.0 (플릿): opus
             sonnet  → 플릿 분석 → 교차 비교 → 공통 패턴 → 모든 AGENTS.md
             haiku
             main
             default
```

---

## 아키텍처 다이어그램

```
┌──────────────────────────────────────────────────────────────────┐
│                    SEA v5.0 Fleet Engine                          │
│                                                                    │
│  ~/.openclaw/agents/                                              │
│  ├── opus/sessions/*.jsonl    ──┐                                 │
│  ├── sonnet/sessions/*.jsonl  ──┤                                 │
│  ├── haiku/sessions/*.jsonl   ──┤──► fleet-analyzer.sh           │
│  ├── main/sessions/*.jsonl    ──┤      │                          │
│  └── default/sessions/*.jsonl ──┘      │                          │
│                                        ▼                          │
│                              data/fleet/<agent>-analysis.json    │
│                                        │                          │
│                                        ▼                          │
│                              fleet-report.json                    │
│                              ┌──────────────────┐                │
│                              │ agent_scores     │                │
│                              │ rankings         │                │
│                              │ shared_patterns  │                │
│                              │ recommendations  │                │
│                              └──────────────────┘                │
│                                        │                          │
│                            ┌───────────┴───────────┐             │
│                            ▼                       ▼             │
│              cross-agent-proposals.sh      sea fleet CLI         │
│                            │               sea fleet run         │
│                            ▼               sea fleet compare     │
│              data/proposals/               sea fleet proposals   │
│              proposal-cross-*.json         sea fleet sync        │
│                            │               sea fleet health      │
│                            ▼                                     │
│                    sea approve                                    │
│                    (per-agent AGENTS.md 업데이트)                 │
└──────────────────────────────────────────────────────────────────┘
```

---

## 핵심 컴포넌트

### 1. `scripts/v5/fleet-analyzer.sh`

**역할**: 모든 에이전트를 독립적으로 분석하고 fleet-report.json 생성

**분석 단계**:
1. **에이전트 열거** — `~/.openclaw/agents/*/sessions/` 탐색
2. **에이전트별 독립 분석** — 각 에이전트의 세션 데이터 수집 및 파싱
3. **메트릭 계산**:
   - `quality_score` (1-10): 전반적 응답 품질
   - `exec_safety` (1-10): exec 명령 안전성 비율
   - `frustration_count`: 사용자 좌절 이벤트 수
   - `error_count`: Tool 실행 에러 수
   - `rule_violations`: AGENTS.md 규칙 위반 건수
4. **크로스 에이전트 비교** — 랭킹, 공통 패턴, 시스템 이슈 도출

**출력 파일**:
```
data/fleet/
├── fleet-report.json          # 전체 플릿 요약
├── opus-analysis.json         # 에이전트별 상세
├── sonnet-analysis.json
├── haiku-analysis.json
└── sync-<rule>-<date>.json    # sync 기록
```

**fleet-report.json 스키마**:
```json
{
  "generated_at": "2026-02-18T...",
  "fleet_days": 7,
  "agents_analyzed": 5,
  "active_agents": 3,
  "agent_scores": {
    "opus":   {"quality": 8.2, "exec_safety": 9.0, "frustration": 1, "error_count": 3},
    "sonnet": {"quality": 7.8, "exec_safety": 7.5, "frustration": 4, "error_count": 8},
    "haiku":  {"quality": 7.1, "exec_safety": 8.5, "frustration": 0, "error_count": 1}
  },
  "rankings": {
    "quality_best":      [{"agent": "opus",   "value": 8.2}, ...],
    "exec_safety_best":  [{"agent": "opus",   "value": 9.0}, ...],
    "most_frustration":  [{"agent": "sonnet", "value": 4},   ...],
    "least_violations":  [{"agent": "haiku",  "value": 0},   ...]
  },
  "shared_patterns": [
    {
      "pattern": "git_direct_cmd",
      "description": "git 직접 명령 (git-sync.sh 미사용)",
      "agents_affected": ["opus", "sonnet"],
      "agent_count": 2,
      "total_violations": 7,
      "is_systemic": false
    }
  ],
  "systemic_issues": [...],
  "recommendations": [
    {
      "priority": "high",
      "type": "transfer_rule",
      "target": "sonnet",
      "source": "opus",
      "proposal": "Exec 안전 규칙을 opus에서 sonnet으로 이전 ..."
    }
  ],
  "fleet_health": 8.1,
  "summary": {
    "total_sessions": 45,
    "total_errors": 12,
    "total_frustration": 5,
    "avg_quality": 7.7,
    "avg_exec_safety": 8.3
  }
}
```

---

### 2. `scripts/v5/cross-agent-proposals.sh`

**역할**: fleet-report.json을 바탕으로 여러 에이전트에 적용 가능한 제안 생성

**제안 유형**:

| 유형 | 설명 | 예시 |
|------|------|------|
| `systemic` | 시스템 공통 문제 — 모든/대부분 에이전트에 존재 | "3/5 에이전트에 git 직접 명령 패턴" |
| `transfer` | 규칙 이전 — Agent A의 효과적 규칙을 Agent B로 복사 | "opus의 exec 안전 규칙 → sonnet" |
| `all_agents` | 전체 에이전트 공통 적용 | "플릿 건강도 개선 — 공통 규칙 추가" |
| `improvement` | 특정 에이전트 개선 | "sonnet 좌절 감소 전략" |

**출력**:
- `data/fleet/cross-proposals-<DATETIME>.json` — 전체 제안 목록
- `data/proposals/proposal-cross-*.json` — `sea proposals`로 관리 가능

---

### 3. `sea fleet` CLI

```bash
# 플릿 현황 한눈에 보기
sea fleet

# 전체 플릿 분석 실행
sea fleet run
sea fleet run --days 14     # 14일치 분석
sea fleet run --dry-run     # 실제 저장 없이 테스트

# 에이전트 간 나란히 비교
sea fleet compare
sea fleet compare --focus exec_safety   # 특정 메트릭 집중

# 크로스 에이전트 제안 생성
sea fleet proposals
sea fleet proposals --dry-run   # 미리보기만

# 규칙 이전
sea fleet sync exec_safety --from opus --to sonnet
sea fleet sync core_rules --from opus --to-all

# 플릿 건강도
sea fleet health
sea fleet health --json
```

---

## Exec 안전성 점수 계산법

```
exec_safety = f(safe_ratio, unsafe_abs_count)

safe_ratio  = safe_commands / total_commands
penalty     = min(unsafe_count * 0.3, 3.0)
score       = min(10, max(0, safe_ratio * 10 - penalty))
```

**Safe 패턴** (점수 증가):
- `|| true`, `|| echo ...`, `|| :`
- `2>/dev/null`, `2>&1`
- `curl -sf`, `curl -f`
- `safe-exec.sh` 래퍼 사용
- `[ -f ... ]`, `command -v` 사전 체크

**Unsafe 패턴** (점수 감소):
- `git pull/push/fetch` 직접 사용
- `rm -rf` (trash 대신)
- `curl https://...` (핸들링 없음)
- `python3 script.py` (에러 핸들링 없음)
- `launchctl bootout/kickstart`
- `openclaw gateway restart` 직접 호출

---

## 품질 점수 계산법

```
quality = 8.0
        - frustration_penalty   (좌절 이벤트: high×0.3, med×0.15, low×0.05 / sessions)
        - violation_penalty     (규칙 위반: min(count/5, 0.3) / sessions)
        + exec_safety_bonus     ((exec_safety - 5.0) × 0.1)

범위: 1.0 ~ 10.0
```

---

## 플릿 건강도 (fleet_health)

```
fleet_health = avg_quality × 0.6 + avg_exec_safety × 0.4
```

| 점수 | 해석 |
|------|------|
| 8.5+ | 🟢 우수 — 안정적인 플릿 운영 |
| 7.0~ | 🟡 양호 — 일부 개선 여지 |
| 5.0~ | 🟠 주의 — 적극적 개선 필요 |
| ~5.0 | 🔴 위험 — 즉각 조치 필요 |

---

## v4 → v5 마이그레이션

| v4.0 | v5.0 |
|------|------|
| 단일 에이전트 분석 | **전체 플릿 분석** |
| 에이전트 자기 평가 | **에이전트 간 상호 비교** |
| 개별 AGENTS.md 업데이트 | **공통 패턴 → 일괄 업데이트** |
| 수동 규칙 작성 | **검증된 규칙 자동 이전 제안** |
| `sea run` | `sea run` + **`sea fleet run`** |
| `sea proposals` | `sea proposals` + **`sea fleet proposals`** |

---

## 설계 원칙

1. **비파괴적 분석** — 세션 파일 읽기 전용, 절대 수정 없음
2. **에이전트 독립성** — 각 에이전트 분석은 독립 실행, 하나 실패해도 나머지 계속
3. **우선순위 명확화** — critical → high → medium → low 순으로 제안 정렬
4. **인간 승인 필수** — `sea fleet sync`는 미리보기만, 실제 적용은 `sea approve`
5. **bash 3.2 호환** — macOS 기본 bash에서 동작 (declare -A 없는 구조)
6. **항상 exit 0** — fleet 분석 실패가 크론 에러로 Discord에 노출되지 않도록

---

## 향후 로드맵

- **v5.1**: LLM 기반 크로스 에이전트 의미 분석 (패턴 유사성 시맨틱 비교)
- **v5.2**: 시계열 트렌드 — 에이전트별 점수 변화 추적 (`data/fleet/history/`)
- **v5.3**: GitHub Actions 연동 — fleet 보고서를 PR 댓글로 자동 게시
- **v5.4**: 자동 동기화 — 승인된 규칙을 모든 에이전트에 자동 적용
- **v6.0**: 에이전트 역할 특화 분석 (opus=복잡 작업, haiku=빠른 응답 최적화)
