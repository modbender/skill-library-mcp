# Self-Evolving Agent v4.0 — 아키텍처

> v4.0의 4단계 멀티에이전트 파이프라인과 효과 측정 루프에 대한 상세 기술 문서.

---

## v3.0과의 차이점

| 항목 | v3.0 | v4.0 |
|------|------|------|
| 에이전트 수 | 1개 (단일 실행) | 4개 전문 에이전트 |
| 분석 방식 | 순수 키워드 매칭 | 키워드 + 구조적 휴리스틱 |
| Role 필터 | 불완전 (부분 구현) | 완전 분리 (user/assistant) |
| 문맥 분석 | 없음 | 전후 3줄 context window |
| 효과 측정 | 없음 | 벤치마크 에이전트 (Stage 3) |
| Claude 호출 | 1회 (분석 + 제안 혼합) | 1회 (합성만, Stage 4) |
| False positive | ~40% | 추정 ~15% |
| 총 실행 시간 | ~5분 | <3분 목표 |
| 비용 | ~$0.05–$0.15 | <$0.05 목표 |

---

## 4단계 파이프라인 개요

```
일요일 22:00 (cron 트리거)
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│              orchestrator.sh (오케스트레이터)                    │
│                                                             │
│  Stage 1         Stage 2            Stage 3        Stage 4           │
│  [COLLECT]  →   [ANALYZE]     →  [BENCHMARK]  → [SYNTHESIZE]        │
│  collect-logs  semantic-analyze  benchmark.sh  synthesize-proposal   │
│                                                                      │
│  로그 수집        패턴 분석          효과 측정      제안 작성         │
│  구조화           휴리스틱           이전 추적       Claude 1회       │
│                                                                      │
│  Stage 5: [MEASURE-EFFECTS] — measure-effects.sh (폐쇄 피드백 루프)  │
└──────────────────────────────────────────────────────────────────────┘
         │
         ▼
Discord #your-channel 리포트 → 사용자 승인 대기
```

---

## 데이터 흐름 다이어그램 (ASCII)

```
입력 소스
══════════════════════════════════════════════════════════════

  ~/.openclaw/agents/          ~/.openclaw/logs/         AGENTS.md
  (채팅 로그 세션 파일)         (cron, heartbeat 로그)    (현재 규칙)
          │                          │                       │
          └──────────────────────────┴───────────────────────┘
                                     │
                                     ▼
══════════════════════════════════════════════════════════════
Stage 1: COLLECT (collect-logs.sh)
══════════════════════════════════════════════════════════════

  ┌─────────────────────────────────────────────────────┐
  │                   수집 에이전트                      │
  │                                                     │
  │  ① 채팅 로그 파싱          ② exec 재시도 추출        │
  │     └── 세션별 청크 분리        └── 연속 3회+ 탐지   │
  │                                                     │
  │  ③ 크론 에러 파싱          ④ 이전 제안 이력 로드      │
  │     └── 연속 에러 서명          └── 적용/거부 목록   │
  │                                                     │
  └──────────────────┬──────────────────────────────────┘
                     │
                     ▼
          data/collect-YYYYMMDD.json
          {
            "sessions": [...],
            "exec_retries": {...},
            "cron_errors": [...],
            "previous_proposals": [...]
          }

══════════════════════════════════════════════════════════════
Stage 2: ANALYZE (semantic-analyze.sh)
══════════════════════════════════════════════════════════════

  ┌─────────────────────────────────────────────────────┐
  │                   분석 에이전트                      │
  │                                                     │
  │  ① 역할 필터                                        │
  │     user 메시지 vs assistant 메시지 분리             │
  │     → assistant 발화는 complaint 분석 제외           │
  │                                                     │
  │  ② 키워드 매칭 (기존 방식)                           │
  │     "다시", "기억", "말했잖아" 등                    │
  │                                                     │
  │  ③ 구조적 휴리스틱 (v4.0 신규)                       │
  │     ┌── context_window: 전후 3줄 확인                │
  │     │     키워드가 정말 불만 문맥인지 검증            │
  │     ├── dedup_per_session: 세션 내 중복 제거          │
  │     │     같은 패턴 동일 세션에서 1회 계산            │
  │     └── emotion_boost: 감정 강화 신호 가중치          │
  │           "!!", "??", "왜", "또" 동반 시 1.5x        │
  │                                                     │
  │  ④ AGENTS.md 규칙 위반 교차 분석                     │
  │  ⑤ 세션 건강도 (컴팩션 카운트)                       │
  └──────────────────┬──────────────────────────────────┘
                     │
                     ▼
          data/analysis-YYYYMMDD.json
          {
            "complaint_signals": [...],  // 가중치 적용된 패턴
            "exec_issues": {...},
            "rule_violations": [...],
            "session_health": {...},
            "false_positive_estimate": 0.15
          }

══════════════════════════════════════════════════════════════
Stage 3: BENCHMARK (benchmark.sh)
══════════════════════════════════════════════════════════════

  ┌─────────────────────────────────────────────────────┐
  │                  벤치마크 에이전트                   │
  │                                                     │
  │  이전 주기에 적용된 제안 목록 로드                    │
  │         │                                           │
  │         ▼                                           │
  │  각 제안에 대해:                                     │
  │  ┌── 제안 타겟 패턴 추출                             │
  │  │     예: "다시" 키워드 빈도                        │
  │  ├── 적용 전 빈도 (이전 주기 분석 결과)              │
  │  ├── 적용 후 빈도 (이번 주기 분석 결과)              │
  │  └── 효과 분류:                                     │
  │        Effective: 빈도 30%+ 감소                    │
  │        Neutral:   ±30% 이내                         │
  │        Regressed: 빈도 증가 (재검토 플래그)          │
  └──────────────────┬──────────────────────────────────┘
                     │
                     ▼
          data/benchmarks/benchmark-YYYYMMDD.json
          {
            "measured_proposals": [
              {
                "proposal_id": "20260210-#2",
                "target_pattern": "다시",
                "before_freq": 22,
                "after_freq": 12,
                "change_pct": -45.5,
                "verdict": "Effective"
              },
              ...
            ],
            "summary": {
              "effective": 2,
              "neutral": 1,
              "regressed": 0
            }
          }

══════════════════════════════════════════════════════════════
Stage 4: SYNTHESIZE (synthesize-proposal.sh)
══════════════════════════════════════════════════════════════

  ┌─────────────────────────────────────────────────────┐
  │                  합성 에이전트                       │
  │                                                     │
  │  Stage 1 + 2 + 3 결과 종합                          │
  │         │                                           │
  │         ▼                                           │
  │  Claude API 호출 (1회, Sonnet 4.5)                  │
  │  ┌── 입력: 분석 결과 JSON                           │
  │  ├── 입력: 벤치마크 결과 JSON                       │
  │  ├── 입력: 현재 AGENTS.md                           │
  │  └── 입력: 거부 이력 (재제안 방지)                  │
  │                                                     │
  │  출력: diff 형식 개선안                              │
  │  ┌── 각 제안: before/after + 근거 데이터             │
  │  ├── 벤치마크 섹션: "지난주 #2 효과 있음 (-45%)"    │
  │  └── 심각도 분류: HIGH / MEDIUM / LOW               │
  └──────────────────┬──────────────────────────────────┘
                     │
                     ▼
          data/proposals/proposal_YYYYMMDD.json

══════════════════════════════════════════════════════════════
출력
══════════════════════════════════════════════════════════════

  Discord #your-channel
  ┌─────────────────────────────────────────────────────┐
  │  🧠 Self-Evolving Agent v4.0 주간 분석               │
  │                                                     │
  │  📈 지난 주 효과: #2 Effective (-45%), #3 Neutral   │
  │  📊 분석: 30 세션, 405 exec 재시도, 3 크론 에러      │
  │  📝 제안: 3개                                       │
  │                                                     │
  │  ### 제안 #1: HIGH                                  │
  │  Before: ...                                        │
  │  After:  ...                                        │
  │                                                     │
  │  ✅ 적용: "제안 #1 적용해줘"                         │
  │  ❌ 거부: "거부: [이유]"                             │
  └─────────────────────────────────────────────────────┘
         │
         ▼
  사용자 명시적 승인 대기 (AGENTS.md 절대 자동 수정 없음)
```

---

## 효과 측정 루프 (폐쇄 피드백)

v4.0의 핵심 차별점은 **폐쇄 피드백 루프**입니다:

```
Week N:
  분석 → 제안 → 승인 → AGENTS.md 수정

Week N+1:
  분석 → [벤치마크: Week N 제안 효과 측정] → 제안 → ...
                    │
                    ├── Effective? → 성공 리포트 + 계속
                    ├── Neutral?   → "효과 불명, 추가 관찰"
                    └── Regressed? → 재검토 제안 (제거 or 수정)
```

이전 버전들의 가장 큰 약점 — "제안이 실제로 도움됐는지 모름" — 을 v4.0이 해결합니다.

**측정 방법:**
1. 제안 적용 전 패턴 빈도 → `benchmarks/` 에 저장
2. 다음 주 분석 결과와 비교
3. 30%+ 감소 = Effective, ±30% = Neutral, 증가 = Regressed
4. Regressed 제안은 자동으로 재검토 플래그

**한계:** 빈도 기반 측정 — 다른 변수(사용 패턴 변화, 다른 규칙 영향 등)를 통제하지 못함. 인과관계 분석이 아닌 상관관계 측정.

---

## 구조적 휴리스틱 분석 상세

v3.0의 순수 키워드 매칭에서 발생하던 ~40% false positive를 줄이기 위한 v4.0 접근법:

### Role Filter (역할 필터)

```bash
# v3.0 (문제): assistant 발화도 포함
grep -c "다시" all_messages.txt

# v4.0 (개선): user 메시지만
grep -A1 '"role": "user"' transcript.json | grep "다시"
```

**효과:** "다시 한번 확인해드릴게요" 같은 assistant 발화 제거

### Context Window (문맥 창)

```bash
# 키워드 발견 시 전후 3줄 추출 → LLM mini-check
context=$(sed -n "$((line-3)),$((line+3))p" transcript.txt)
# "아, 다시 로그인해줘?" vs "다시 해봐" 구분
```

**효과:** 동일 키워드의 긍정/부정 맥락 구분

### Per-Session Deduplication (세션 내 중복 제거)

```bash
# 동일 세션에서 같은 패턴이 여러 번 나와도 1회 계산
# (한 가지 주제로 대화 전체에 걸쳐 나오는 경우 과대계산 방지)
declare -A session_seen
if [[ ! ${session_seen[$session_id_$pattern]+_} ]]; then
  count++
  session_seen[$session_id_$pattern]=1
fi
```

### Emotion Boost (감정 강화 신호)

```bash
# 감정 강화 신호 동반 시 가중치 1.5x
if echo "$context" | grep -qE '!!|\?\?|왜|또'; then
  score=$(echo "$score * 1.5" | bc)
fi
```

---

## 성능 목표

| 지표 | v3.0 실측 | v4.0 목표 |
|------|-----------|-----------|
| 총 실행 시간 | ~5분 | < 3분 |
| Claude API 비용 | $0.05–$0.15 | < $0.05 |
| False positive | ~40% | ~15% (추정) |
| 탐지 커버리지 | 키워드 목록 내 | 키워드 + 문맥 |
| 효과 측정 | 없음 | 이전 제안 전수 |

### 비용 구조 (Sonnet 4.5 기준)

```
Stage 1 (collect):    로컬 실행, 0원
Stage 2 (analyze):    로컬 실행, 0원
Stage 3 (benchmark):  로컬 실행, 0원
Stage 4 (synthesize): Claude 1회 호출
  → 입력: ~3,000 tokens (분석 결과 JSON)
  → 출력: ~1,500 tokens (제안 드래프트)
  → 비용: ~$0.02–$0.04

총계: < $0.05/회
```

---

## v3.0과의 하위 호환성

v3.0 스크립트(`scripts/analyze-behavior.sh`, `scripts/generate-proposal.sh`)는 **삭제되지 않습니다.**

- `register-cron.sh` — 기본값은 v4.0 파이프라인
- `register-cron.sh --v3` — v3.0 방식으로 등록 (레거시)
- `scripts/v4/orchestrator.sh` — v4.0 직접 호출

v4.0으로 마이그레이션하지 않아도 v3.0이 계속 동작합니다.

---

## 디렉토리 구조 (v4.0 신규 항목)

```
scripts/v4/
├── orchestrator.sh         ← 오케스트레이터 (여기서 시작)
├── collect-logs.sh         ← Stage 1: 수집
├── semantic-analyze.sh     ← Stage 2: 분석 (휴리스틱 포함)
├── benchmark.sh            ← Stage 3: 벤치마크
├── synthesize-proposal.sh  ← Stage 4: 합성 (Claude 호출)
└── measure-effects.sh      ← Stage 5: 효과 측정 (폐쇄 피드백 루프)

data/
├── proposals/           ← 기존 (제안 JSON)
├── benchmarks/          ← v4.0 신규 (효과 측정 결과)
│   ├── benchmark-20260217.json
│   └── benchmark-20260224.json
└── rejected-proposals.json  ← 기존
```

---

## 설계 원칙

1. **단계 격리**: 각 Stage는 독립 실행 가능. Stage 2만 따로 테스트 가능.
2. **로컬 우선**: Claude 호출은 최소화. 4단계 중 1단계(합성)만 API 사용.
3. **투명성**: 모든 중간 결과가 JSON 파일로 저장됨. 디버깅 용이.
4. **하위 호환**: v3.0 스크립트 삭제 없음. 마이그레이션 선택 사항.
5. **측정 가능성**: 효과를 측정하지 않는 개선은 개선이 아님.
6. **인간 통제**: 어떤 단계에서도 AGENTS.md 자동 수정 없음.
