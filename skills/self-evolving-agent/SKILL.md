---
name: self-evolving-agent
version: 5.0.0
description: "AI 비서가 자기 로그를 분석해서 AGENTS.md 개선안을 제안하는 자동화. v5.0: 시맨틱 임베딩(Ollama nomic-embed-text, FP ~8%), 실시간 스트리밍 모니터(<30초 알림), 플릿 분석(다중 인스턴스). v4.3: 대화형 승인, 멀티포맷 리포트, GitHub Issues. v4.2: Ollama LLM. v4.1: 멀티플랫폼 배달. v4.0: 4단계 파이프라인. 제안만 함, 직접 수정 절대 없음."
author: ramsbaby
tags: [self-improvement, automation, agents, meta, exec-safety, multi-agent, semantic-analysis, effect-measurement, ollama, local-llm, zero-cost, embeddings, streaming, fleet-analysis]
---

# Self-Evolving Agent 🧠 (v5.0.0)

**매주 로그를 읽고, 시맨틱 임베딩으로 의미론적 패턴을 찾고, 실시간 모니터링으로 즉각 알리고, 효과가 측정된 AGENTS.md 개선안을 제안하는 자동화 시스템.**  
**제안만 합니다. AGENTS.md는 사용자가 승인해야만 수정됩니다.**

---

## 솔직한 설명

이 스킬은 "AI 자기진화"라는 이름을 달고 있지만 실제 동작은 투명합니다:

1. **실시간**: 스트리밍 모니터가 로그를 감시, 임계치 초과 시 즉각 알림
2. **매주 일요일 22시**: 6단계 파이프라인 시작
3. **수집 에이전트**: 로그 스캔 + 실시간 알림 통합
4. **임베딩 분석 에이전트**: Ollama 시맨틱 임베딩으로 의미론적 패턴 감지
5. **트렌드 에이전트**: 4주간 패턴 추세 비교 (Emerging/Resolved)
6. **플릿 에이전트**: 다중 에이전트 인스턴스 교차 분석
7. **벤치마크 에이전트**: 이전 제안 효과 측정 (개선됐나? 악화됐나?)
8. **합성 에이전트**: 전체 데이터 종합 → 제안 초안 작성
9. Discord로 전송 → 사용자 승인 필요

과대 광고 아닙니다. 완벽하지 않습니다. 하지만 v4.x보다 훨씬 정확합니다.

**v5.0에서 달라진 것 (2026-02-18):**
- **시맨틱 임베딩** (Pillar 1): `sea patterns` — Ollama `nomic-embed-text` 로컬 임베딩으로 의미론적 불만 감지, FP ~15% → ~8%
- **스트리밍 모니터** (Pillar 2): `sea monitor` — 실시간 로그 감시, 임계치 초과 즉각 알림 (<30초)
- **플릿 분석** (Pillar 3): `sea fleet` — 다중 에이전트 인스턴스 교차 분석
- **트렌드 분석**: `sea trends` — 4주간 패턴 추세 (Emerging/Resolved/Stable)
- **폴백 내성**: Ollama 오프라인 시 v4 휴리스틱 자동 폴백 (시스템 중단 없음)
- **신규 CLI**: `sea monitor`, `sea alerts`, `sea trends`, `sea patterns`, `sea fleet`

**v4.3에서 달라진 것:**
- **대화형 승인**: `sea watch` — 30초 폴링, macOS 데스크탑 알림, 터미널 대화형 approve/reject
- **Discord 리액션 지시**: 제안 전달 시 `✅ ❌ 🔍` 리액션 지시 자동 추가
- **멀티포맷 리포트**: `sea export` — markdown/html/json/pdf/all 형식 지원
- **GitHub Issues**: `sea github` — 제안별 이슈 생성, 승인 시 자동 종료, 레이블 관리

**v4.2에서 달라진 것:**
- **Ollama/로컬 LLM 완전 지원**: `config.yaml`에서 `provider: "ollama"` 설정 한 줄로 전환
- **Zero-Cost 모드**: Ollama + `provider: "none"` 조합으로 API 비용 $0.00/주 운영
- **범용 LLM 인터페이스**: `scripts/v4/llm-call.sh` — anthropic/openai/ollama/none 통합
- **합성 단계 LLM 강화**: synthesize-proposal.sh가 llm-call.sh를 통해 AI 제안 생성

**v4.1에서 달라진 것:**
- **영어 + 한국어 불만 패턴 동시 지원**: config.yaml에서 `ko` / `en` 분리 구조
- **자동 언어 감지**: 세션 첫 10개 user 메시지 중 >50%에 한글이면 ko, 아니면 en 패턴 적용
- `config.yaml`의 `auto_detect: true` 설정으로 제어 가능

**v4.0에서 달라진 것:**
- **멀티에이전트 파이프라인**: 단일 Claude 호출 → 4개 전문 에이전트 협력
- **구조적 휴리스틱 분석**: 순수 키워드 매칭 → 문맥·위치·역할 고려한 패턴 분석
- **효과 측정 루프**: 제안 적용 후 실제로 도움됐는지 다음 주기에 측정
- **False positive 감소**: ~40% → 추정 ~15%

---

## 파일 구조

```
~/openclaw/skills/self-evolving-agent/
├── SKILL.md                        ← 이 파일
├── README.md                       ← 영어, ClawHub 배포용
├── _meta.json                      ← ClawHub 메타데이터
├── config.yaml                     ← 설정 파일
├── scripts/
│   ├── analyze-behavior.sh         ← v3.0 분석 (하위 호환 유지)
│   ├── generate-proposal.sh        ← v3.0 제안 생성
│   ├── register-cron.sh            ← 크론 등록/업데이트
│   ├── lib/
│   │   └── config-loader.sh        ← config.yaml 파서
│   ├── v4/                         ← v4.0 파이프라인 (하위 호환 유지)
│   │   ├── orchestrator.sh         ← v4 오케스트레이터 (직접 실행 가능)
│   │   ├── collect-logs.sh         ← Stage 1: 로그 수집 + 구조화
│   │   ├── semantic-analyze.sh     ← Stage 2: 구조적 패턴 분석
│   │   ├── benchmark.sh            ← Stage 3: 효과 측정 + 이전 제안 추적
│   │   ├── synthesize-proposal.sh  ← Stage 4: 합성 에이전트 → 최종 제안
│   │   ├── llm-call.sh             ← 범용 LLM 인터페이스
│   │   ├── measure-effects.sh      ← 제안 효과 측정 루프
│   │   ├── deliver.sh              ← 멀티플랫폼 배달기 (Slack/Telegram/Webhook)
│   │   ├── interactive-approve.sh  ← 대화형 승인 + sea watch
│   │   ├── export-report.sh        ← 멀티포맷 리포트 내보내기
│   │   └── github-issue.sh         ← GitHub Issues 통합
│   └── v5/                         ← v5.0 신규 파이프라인 ⭐
│       ├── orchestrator.sh         ← v5 오케스트레이터 (v4 폴백 내장)
│       ├── embedding-analyze.sh    ← 시맨틱 임베딩 분석 ⭐ (Pillar 1)
│       ├── stream-monitor.sh       ← 실시간 스트리밍 모니터 ⭐ (Pillar 2)
│       ├── fleet-analyzer.sh       ← 플릿 다중 인스턴스 분석 ⭐ (Pillar 3)
│       └── trend-analyzer.sh       ← 주간 트렌드 분석 ⭐
├── dashboard/                      ← 로컬 웹 대시보드
│   ├── index.html                  ← 단일 파일 대시보드 (의존성 없음)
│   ├── load-data.js                ← 데이터 로더 모듈
│   ├── build-index.sh              ← 데이터 인덱스 빌더
│   ├── serve.sh                    ← 로컬 HTTP 서버 실행
│   └── README.md                   ← 대시보드 사용 가이드
├── templates/
│   └── proposal-template.md        ← 개선안 출력 형식
├── docs/
│   ├── architecture.md             ← v3.0 아키텍처 (레거시)
│   ├── v4-architecture.md          ← v4.0 아키텍처 상세
│   ├── v5-architecture.md          ← v5.0 아키텍처 상세 ⭐
│   ├── migration-v4-to-v5.md       ← v4 → v5 마이그레이션 가이드 ⭐
│   ├── roadmap.md                  ← 로드맵
│   ├── devils-advocate.md          ← 악마의 변호인 비판 분석
│   ├── test-results.md             ← QA 테스트 결과
│   └── quality-review.md           ← 품질 검토
├── bin/                            ← CLI 도구
│   ├── sea                         ← 메인 CLI v2.0 (proposals/run/status/... + v5 명령)
│   └── sea-completion.bash         ← Bash 탭 자동완성
├── tests/
│   ├── fixtures/                   ← 테스트 픽스처
│   ├── test-cli.sh                 ← CLI 테스트
│   ├── test-pipeline.sh            ← v4 파이프라인 테스트
│   └── test-v5.sh                  ← v5 컴포넌트 테스트 ⭐
└── data/                           ← 런타임 자동 생성
    ├── proposals/                  ← 생성된 제안 JSON
    ├── benchmarks/                 ← 효과 측정 결과
    ├── stream-alerts/              ← 실시간 알림 큐 ⭐
    ├── fleet/                      ← 플릿 분석 결과 ⭐
    ├── trends/                     ← 트렌드 분석 결과 ⭐
    ├── undelivered/                ← 배달 실패 시 폴백 저장
    └── rejected-proposals.json     ← 거부 기록
```

---

## 🛠️ sea CLI (v2.0.0)

`sea`는 Self-Evolving Agent의 명령줄 인터페이스입니다. 제안 관리, 파이프라인 실행, AGENTS.md 적용을 터미널에서 직접 수행할 수 있습니다.

### PATH 설정

```bash
# ~/.zshrc 또는 ~/.bashrc에 추가
export PATH="$HOME/openclaw/skills/self-evolving-agent/bin:$PATH"

# 탭 자동완성 활성화 (bash 전용)
source ~/openclaw/skills/self-evolving-agent/bin/sea-completion.bash
```

### 주요 명령어

```bash
# ── 기존 명령어 (v4에서 유지) ─────────────────────────────
sea run                        # 전체 파이프라인 실행 (v5 오케스트레이터)
sea run --v4                   # v4 파이프라인 강제 실행
sea run --stage 2              # Stage 2(분석)만 실행
sea status                     # 마지막 실행 요약 (한 줄)
sea proposals                  # 대기 중인 제안 목록
sea proposals --all            # 모든 제안 (전체 상태)
sea approve <id>               # 제안 승인: diff → AGENTS.md 패치 → git commit
sea approve --all              # 대기 중인 모든 제안 승인
sea reject <id> "이유"          # 이유와 함께 거부
sea watch                      # 30초 폴링, 새 제안 알림 + 대화형 승인
sea export --format html       # HTML 리포트 내보내기
sea export --format all --output-dir ./reports/   # 모든 형식 내보내기
sea github create --all        # 모든 pending 제안 GitHub 이슈 생성
sea github sync                # proposals/ ↔ GitHub 이슈 동기화
sea github list                # self-evolving 이슈 목록
sea history                    # 전체 제안 이력 (적용/거부/대기)
sea health                     # AGENTS.md 건강도 점수 + 통계
sea config                     # 현재 설정 표시
sea config set analysis.days 14  # 설정값 업데이트
sea version                    # 버전 확인
sea help                       # 도움말

# ── v5.0 신규 명령어 ⭐ ───────────────────────────────────
sea monitor                    # 실시간 스트리밍 모니터 시작 (Ctrl+C로 종료)
sea monitor --poll             # 폴링 모드 (30초 간격, 비대화형 환경)
sea alerts                     # 스트림 알림 목록 (주간 집계)
sea alerts --clear             # 알림 초기화 (처리 완료 후)
sea trends                     # 주간 트렌드 분석 (Emerging/Resolved/Stable)
sea trends --json              # JSON 출력 (CI/자동화용)
sea patterns                   # 시맨틱 패턴 라이브러리 확인
sea patterns add "<text>" --label frustration  # 앵커 패턴 추가
sea fleet                      # 플릿 분석 (전체 에이전트 인스턴스)
sea fleet --agents opus,sonnet # 특정 에이전트만 분석

# 모든 명령에 --json 플래그 추가 가능
sea status --json
sea history --json
sea fleet --json
```

### `sea approve` 동작 방식

1. `data/proposals/<id>.json`에서 제안 읽기
2. `before` / `after` diff 출력
3. `AGENTS.md`의 `before` 텍스트를 `after`로 교체
4. 제안 JSON의 `status`를 `"applied"`로 업데이트
5. `git commit -m "agents: apply proposal <id>"`

---

## 설치

```bash
# 1. Clone
git clone https://github.com/Ramsbaby/self-evolving-agent ~/openclaw/skills/self-evolving-agent

# 2. 설정 마법사 실행 (대화형)
bash ~/openclaw/skills/self-evolving-agent/scripts/setup-wizard.sh
```

비대화형 설치 (CI/자동화용):

```bash
bash ~/openclaw/skills/self-evolving-agent/scripts/setup-wizard.sh \
  --platform discord \
  --channel YOUR_CHANNEL_ID \
  --lang auto \
  --days 7 \
  --yes
```

설정 검증만 실행:

```bash
bash ~/openclaw/skills/self-evolving-agent/scripts/validate-config.sh --fix
```

크론 수동 등록/업데이트:

```bash
bash ~/openclaw/skills/self-evolving-agent/scripts/register-cron.sh
```

크론 JSON 예시 (`~/.openclaw/cron/jobs.json`에 추가):

```json
{
  "name": "🧠 Self-Evolving Agent v4.0 주간 파이프라인",
  "enabled": true,
  "schedule": {
    "kind": "cron",
    "expr": "0 22 * * 0",
    "tz": "Asia/Seoul"
  },
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "model": "anthropic/claude-sonnet-4-5",
    "message": "bash ~/openclaw/skills/self-evolving-agent/scripts/v4/orchestrator.sh 실행. 결과 텍스트만 출력."
  },
  "delivery": {
    "mode": "announce",
    "channel": "discord",
    "to": "channel:YOUR_CHANNEL_ID"
  }
}
```

---

## 📊 로컬 대시보드 (v4.1 신규) ⭐

제안 이력, 품질 추세, 패턴 빈도, 규칙 효과를 시각화하는 로컬 웹 대시보드.

```bash
# 빠른 시작 (스킬 루트에서 실행)
bash dashboard/serve.sh
# → http://localhost:8420/dashboard/ 에서 열기

# 새 제안 후 인덱스 갱신
bash dashboard/build-index.sh
```

**주요 패널:**
- 📈 Quality Trend — 시간별 품질 점수 라인 차트
- 🏥 AGENTS.md Health — 구조 점수 링 + 히스토리 스파크라인
- 🔍 Pattern Frequency — 불만 패턴 스택 바 차트
- 📋 Proposal History — 전체 제안 이력 테이블
- ⚡ Active Rules Effectiveness — 규칙 효과 측정 (녹색/적색)

> 상세: `dashboard/README.md`

---

## 4단계 파이프라인 아키텍처 (v4.0)

### Stage 1: 수집 (collect)
```
collect-logs.sh
├── 채팅 로그 스캔 (세션별 청크 분리)
├── exec 재시도 이벤트 추출 (연속 3회+ 탐지)
├── 크론 에러 로그 파싱
├── 이전 제안 + 적용 이력 로드
└── → data/collect-YYYYMMDD.json
```

### Stage 2: 분석 (analyze)
```
semantic-analyze.sh
├── 키워드 매칭 (기존 방식 유지)
├── 구조적 휴리스틱 분석 (v4.0 신규)
│   ├── 역할 필터: user vs assistant 메시지 분리
│   ├── 문맥 윈도우: 키워드 전후 3줄 확인
│   ├── 반복 임계값: 동일 세션 내 중복 제거
│   └── 감정 강화 신호: "!!", "??" 동반 여부
├── AGENTS.md 규칙 위반 교차 분석
├── 세션 건강도 지표
└── → data/analysis-YYYYMMDD.json
```

### Stage 3: 벤치마크 (benchmark)
```
benchmark.sh
├── 이전 적용 제안 목록 로드
├── 제안 적용 전후 패턴 빈도 비교
├── 효과 분류: Effective / Neutral / Regressed
├── 효과 없는 제안 재검토 플래그
└── → data/benchmarks/benchmark-YYYYMMDD.json
```

### Stage 4: 합성 (synthesize)
```
synthesize-proposal.sh
├── Stage 1-3 결과 종합
├── Claude API 호출 1회 (합성 에이전트)
│   ├── 분석 데이터 → 자연어 제안
│   ├── 벤치마크 결과 → "지난 주 #2 제안 효과 있음" 포함
│   └── diff 형식으로 before/after 작성
└── → Discord #your-channel 게시
```

### Stage 5: 효과 측정 (measure-effects)
```
measure-effects.sh
├── 과거 제안의 타겟 패턴 빈도 비교
├── 세션 트랜스크립트 + 크론 로그만 스캔 (gateway 로그 제외)
├── 효과 분류: Effective / Neutral / Regressed
└── → /tmp/sea-v4/effects.json
```

---

## 분석 항목 (v4.0)

### 1. 구조적 휴리스틱 분석 (v4.0 신규) ⭐

키워드 매칭에 문맥 분석을 보강:

```yaml
heuristic_analysis:
  role_filter: true              # user 메시지만 분석 (assistant 제외)
  context_window: 3              # 키워드 전후 3줄 확인
  dedup_per_session: true        # 동일 세션 내 중복 패턴 1회 계산
  emotion_boost_signals:         # 감정 강화 신호 (가중치 +1.5x)
    - "!!"
    - "??"
    - "왜"
    - "또"
```

이 결과 false positive: ~40% → 추정 ~15%

### 2. 사용자 불만 패턴 (키워드 매칭 + 자동 언어 감지, v4.1) ⭐

v4.1부터 한국어/영어 패턴이 분리되고, 세션 언어를 자동 감지해 적용합니다.

```yaml
complaint_patterns:
  ko:                        # 한국어 세션에 적용
    - "확인중"
    - "다시"
    - "아까"
    - "반복"
    - "기억"
    - "말했잖아"
    - "계속"
    - "물어보지 말고"
    - "전부 다 해줘"
    - "왜 또"
  en:                        # 영어 세션에 적용
    - "you forgot"
    - "again?"
    - "same mistake"
    - "stop doing that"
    - "how many times"
    - "wrong again"
    - "I told you"
    - "still broken"
    - "not what I asked"
  auto_detect: true          # 세션 언어 자동 감지 (ko/en 자동 선택)
```

**자동 언어 감지 로직:** 세션의 첫 10개 user 메시지 중 >50%에 `[가-힣]`이 포함되면 ko, 아니면 en 패턴 적용.

⚠️ **여전한 한계:** 단어 목록에 없는 패턴은 미탐지. config.yaml에서 커스터마이징 필수.

### 3. exec 연속 재시도 감지

```
같은 exec 명령을 3회 이상 연속 재시도한 세션 탐지
→ 에이전트가 루프에 갇혀 있다는 신호
→ 119회 연속 재시도 실제 발견 (v3.0 테스트, v4.0에서도 유지)
```

### 4. 크론 에러 반복 탐지

```
~/.openclaw/logs/cron-catchup.log
~/.openclaw/logs/heartbeat-cron.log
→ 동일 에러 5회 이상 반복 = 구조적 버그
```

### 5. AGENTS.md 규칙 위반

```
AGENTS.md 규칙 목록 추출 → 실제 transcript와 교차 분석
→ "규칙은 있지만 안 지킨 것" 식별
→ "규칙 없는데 자주 실수한 것" 식별
```

### 6. 세션 건강도

```
컴팩션 5회 이상 = 세션이 너무 길거나 복잡
→ 서브에이전트 분리 권고 제안 트리거
```

### 7. 효과 측정 루프 (v4.0 신규) ⭐

```
이전 주기에 적용된 제안들의 효과를 추적:
→ 적용 전 패턴 빈도 vs 적용 후 패턴 빈도 비교
→ Effective: 빈도 30%+ 감소
→ Neutral: ±30% 이내
→ Regressed: 빈도 증가 (재검토 필요)
```

---

## 제안 형식

Discord `#your-channel`에 이런 형식으로 게시:

```markdown
## 🧠 Self-Evolving Agent v4.0 주간 분석

📅 분석 기간: 2026-02-10 ~ 2026-02-17
📊 분석된 세션: 30개 (전체 964개 중 샘플)
⚡ exec 재시도 이벤트: 405건 (최대 119회 연속)
🔴 활성 크론 에러: 3개
📈 지난 주 제안 효과: #2 Effective (패턴 -43%), #3 Neutral

📝 제안: 3개

---

### 제안 #1: exec 연속 재시도 제한 (HIGH)

**근거:** 7일간 405건 재시도 이벤트, 최대 119회 연속 재시도
**역할 필터:** user 메시지 기준 (assistant 제외)

**Before:** 연속 재시도 시 규칙 없음 (무한 루프 가능)

**After:**
같은 exec 3회 실패 시:
1. 에러 즉시 사용자 보고
2. 2번째 시도는 방법 변경
3. 3번째 실패 = 중단 + 수동 확인 요청

---

✅ 적용: "제안 #1 적용해줘"
❌ 거부: "거부: [이유]"
```

---

---

## 🆓 LLM 제공자 설정 (v4.2 신규)

`config.yaml`의 `llm` 섹션으로 합성 단계의 LLM을 선택합니다.

```yaml
llm:
  provider: "ollama"   # anthropic | openai | ollama | none
```

| 제공자 | 비용 | API 키 | 인터넷 | 품질 |
|--------|------|--------|--------|------|
| **anthropic** | ~$0.05/주 | ANTHROPIC_API_KEY | 필요 | ⭐⭐⭐⭐⭐ |
| **openai** | ~$0.05/주 | OPENAI_API_KEY | 필요 | ⭐⭐⭐⭐⭐ |
| **ollama** 🆓 | **$0.00** | **없음** | **없음** | ⭐⭐⭐⭐ |
| **none** | **$0.00** | **없음** | **없음** | 휴리스틱만 |

### 💡 Ollama 설정 (완전 무료!)

```bash
# 1. Ollama 설치
brew install ollama

# 2. 모델 다운로드 (1회만)
ollama pull llama3.1:8b      # 추천: 균형 잡힌 성능
# 또는
ollama pull mistral:7b        # 더 빠름
ollama pull gemma3:9b         # Google 모델

# 3. 서버 실행 (백그라운드)
ollama serve &

# 4. config.yaml 설정
# llm:
#   provider: "ollama"
#   ollama:
#     model: "llama3.1:8b"
#     url: "http://localhost:11434"
```

### 💡 none 모드 (순수 휴리스틱)

LLM 없이 쉘 스크립트 휴리스틱 분석만 수행합니다. API 비용 $0, 인터넷 불필요.

```yaml
llm:
  provider: "none"
```

> 합성 단계에서 LLM 강화 제안 섹션이 생략됩니다. 기본 분석/제안은 그대로 제공됩니다.

### llm-call.sh 직접 사용

```bash
# Ollama로 프롬프트 전송
echo "분석 결과를 요약해줘" | bash scripts/v4/llm-call.sh --provider ollama

# Anthropic으로 전송
echo "분석 결과를 요약해줘" | bash scripts/v4/llm-call.sh --provider anthropic --model claude-haiku-4-5

# 제공자 없음 (빈 JSON 반환)
echo "테스트" | bash scripts/v4/llm-call.sh --provider none

# config.yaml 자동 읽기 (플래그 생략 가능)
echo "분석 결과를 요약해줘" | bash scripts/v4/llm-call.sh
```

---

## 커스터마이징

```yaml
# config.yaml
analysis:
  days: 14                          # 분석 기간 (기본 7일)
  max_sessions: 50                  # 최대 세션 수
  complaint_patterns:               # v4.1: 언어별 분리 구조
    ko:                             # 한국어 패턴 커스터마이징
      - "물어보지 말고"
      - "전부 다 해줘"
      - "나보고 하라고"
    en:                             # 영어 패턴 커스터마이징
      - "you're useless"
      - "that's wrong again"
      - "stop asking me"
    auto_detect: true               # 세션 언어 자동 감지
  exec_retry_threshold: 3           # 몇 회 재시도부터 탐지할지
  log_error_repeat_threshold: 5     # 동일 에러 몇 회부터 심각으로 볼지

  # v4.0 신규
  heuristic:
    role_filter: true               # user 메시지만 분석
    context_window: 3               # 전후 몇 줄 확인
    dedup_per_session: true         # 세션 내 중복 제거
    emotion_boost: true             # 감정 강화 신호 가중치

  benchmark:
    enabled: true                   # 효과 측정 활성화
    effective_threshold: 0.30       # 30% 감소 = Effective 판정

cron:
  schedule: "0 22 * * 0"           # 일요일 22시 (기본)
  discord_channel: ""  # Required: set your Discord channel ID
```

---

## 배달 설정 (Multi-Platform Delivery)

`config.yaml`의 `delivery` 섹션으로 제안서 전송 플랫폼을 선택합니다.

```yaml
delivery:
  platform: "discord"  # discord | slack | telegram | webhook
```

### Discord (기본)

OpenClaw 크론의 `delivery` 설정을 그대로 사용합니다. `deliver.sh` 호출 없음.

```yaml
delivery:
  platform: "discord"
  discord:
    channel_id: "YOUR_CHANNEL_ID"
```

### Slack

Slack Incoming Webhook을 사용합니다. [Slack Webhook 생성 가이드](https://api.slack.com/messaging/webhooks)

```yaml
delivery:
  platform: "slack"
  slack:
    webhook_url: "https://hooks.slack.com/services/T.../B.../..."
```

### Telegram

BotFather에서 발급한 토큰과 채팅방 ID가 필요합니다.

```yaml
delivery:
  platform: "telegram"
  telegram:
    bot_token: "123456:ABC-DEF..."
    chat_id: "-1001234567890"   # 채널은 -100으로 시작
```

### Generic Webhook

JSON POST로 임의 엔드포인트에 전송합니다.

```yaml
delivery:
  platform: "webhook"
  webhook:
    url: "https://your-server.example.com/sea-proposals"
    method: "POST"
```

Payload 형식:
```json
{
  "source": "self-evolving-agent",
  "version": "4.0",
  "timestamp": "2026-02-18T00:00:00Z",
  "proposal": "## 🧠 SEA v4.0 ...(마크다운)..."
}
```

### 배달 실패 시 폴백

전송에 실패하면 `data/undelivered/YYYYMMDD-HHMMSS-<platform>.md`에 저장됩니다.  
수동 재전송: `PLATFORM=slack bash scripts/v4/deliver.sh data/undelivered/<파일>`

---

## 안전 규칙 (보안 강조)

- ✅ **제안만 합니다** — AGENTS.md를 직접 수정하는 코드 경로 없음
- ✅ **diff 형식** — before/after로 명확한 변경사항 제시
- ✅ **근거 필수** — 측정된 데이터(실제 카운트)가 없으면 제안 없음
- ✅ **승인 후 적용** — 사용자 명시적 승인 시에만 AGENTS.md 반영 + git commit
- ✅ **거부 기록** — 거부 이유를 다음 분석 사이클에 반영
- ✅ **로컬 우선** — 분석은 로컬에서, API 호출은 합성 에이전트 1회뿐
- ✅ **코드 투명성** — 전체 분석 스크립트 ~400줄, 15분이면 다 읽음
- ✅ **효과 측정** — 적용된 제안의 효과를 다음 주기에 리포트

---

## 한계 (솔직하게)

| 한계 | v3.0 | v4.0 개선 | v5.0 개선 |
|------|------|-----------|-----------|
| 키워드 매칭 (의미론 아님) | FP ~40% | 휴리스틱으로 ~15% | **임베딩으로 ~8%** ✅ |
| assistant 발화 필터 불완전 | "다시", "계속" 과다 계산 | role_filter로 개선 | 동일 (유지) |
| 키워드 목록에 없으면 미탐지 | 자율실행 요구 패턴 놓침 | 여전히 동일 | **임베딩 유사도로 목록 외 패턴 감지** ✅ |
| 개선 효과 미측정 | 도움됐는지 모름 | **벤치마크 루프로 해결** ✅ | 동일 (유지) |
| 영어 세션 패턴 미지원 | 영어 감지 불가 | **ko/en + auto_detect** ✅ | 동일 (유지) |
| 데이터 부족 시 제안 품질 하락 | generic 제안 | 여전히 동일 | 여전히 동일 |
| Cold start | 처음 2-4주 데이터 없음 | 여전히 동일 | 여전히 동일 |
| 주 1회 배치만 가능 | 주간 사각지대 있음 | 여전히 동일 | **실시간 스트리밍 모니터로 해결** ✅ |
| 단일 인스턴스만 분석 | 다중 에이전트 분석 불가 | 여전히 동일 | **플릿 분석으로 해결** ✅ |

**v5.0에서 여전히 해결 못 한 것:**
- 혼용 세션 (한영 혼합) 정밀 처리 — 임베딩이 완화하지만 완전 해결은 아님
- 효과 측정은 빈도 기반 상관관계 — 인과관계 분석 아님 (v5.2 계획)
- 스트리밍 모니터는 별도 프로세스 필요 — 크론 외 상시 가동 필요
- 플릿 분석은 4주+ 이력이 있어야 의미 있는 트렌드 도출 가능

---

## v5.0 변경사항 (2026-02-18)

- ✅ **`scripts/v5/embedding-analyze.sh`** 신설 — Ollama `nomic-embed-text` 시맨틱 임베딩 분석 (Pillar 1)
- ✅ **`scripts/v5/stream-monitor.sh`** 신설 — 실시간 스트리밍 모니터 + 임계치 알림 (Pillar 2)
- ✅ **`scripts/v5/fleet-analyzer.sh`** 신설 — 다중 에이전트 인스턴스 교차 분석 (Pillar 3)
- ✅ **`scripts/v5/trend-analyzer.sh`** 신설 — 4주간 패턴 추세 비교 (Emerging/Resolved)
- ✅ **`scripts/v5/orchestrator.sh`** 신설 — v5 6단계 오케스트레이터 (v4 폴백 내장)
- ✅ **`bin/sea`** v2.0.0 — `monitor`, `alerts`, `trends`, `patterns`, `fleet` 커맨드 추가
- ✅ **`config.yaml`** — `embedding`, `streaming`, `fleet`, `trends` 섹션 추가
- ✅ **`tests/test-v5.sh`** 신설 — v5 컴포넌트 독립 테스트 (Ollama 불필요)
- ✅ **`docs/v5-architecture.md`** 신설 — 전체 아키텍처 문서 (ASCII 다이어그램)
- ✅ **`docs/migration-v4-to-v5.md`** 신설 — v4 → v5 마이그레이션 가이드
- ✅ **`Makefile`** — `make test-v5`, `make test` v5 포함

## v4.3 변경사항 (2026-02-18)

- ✅ **`scripts/v4/interactive-approve.sh`** 신설 — sea watch, macOS 알림, 대화형 approve/reject
- ✅ **`scripts/v4/export-report.sh`** 신설 — markdown/html/json/pdf/all 리포트 내보내기
- ✅ **`scripts/v4/github-issue.sh`** 신설 — GitHub Issues 통합 (생성/종료/동기화/레이블)
- ✅ **`bin/sea`** v1.1.0 — `watch`, `export`, `github` 커맨드 추가
- ✅ **`synthesize-proposal.sh`** — Discord 리액션 지시 푸터 자동 추가
- ✅ **`config.yaml`** — `github`, `interactive`, `export` 섹션 추가
- ✅ **`sea approve`** → GitHub 이슈 자동 종료 연동 (GH_TOKEN 있을 때)

## v4.2 변경사항 (2026-02-18)

- ✅ **Ollama/로컬 LLM 완전 지원**: config.yaml `llm.provider` 설정 한 줄로 전환
- ✅ **`scripts/v4/llm-call.sh`** 신설 — anthropic/openai/ollama/none 통합 인터페이스
- ✅ **Zero-Cost 모드**: `provider: "ollama"` 또는 `provider: "none"` → API 비용 $0/주
- ✅ **`synthesize-proposal.sh`**: LLM 강화 제안 섹션 추가 (none이면 생략)
- ✅ **`config.yaml`**: `llm` 섹션 추가 (provider/anthropic/openai/ollama/none)

## v4.1 변경사항 (2026-02-18)

- ✅ **멀티플랫폼 배달 지원**: Slack / Telegram / Generic Webhook
- ✅ **`scripts/v4/deliver.sh`** 신설 — 플랫폼별 독립 핸들러 (각 <30줄)
- ✅ **`data/undelivered/`** 디렉토리 — 배달 실패 시 자동 저장 (유실 방지)
- ✅ **`config.yaml`**: `delivery` 섹션 추가
- ✅ **`config-loader.sh`**: 배달 설정 자동 노출 (`SEA_DELIVERY_PLATFORM` 등)
- ✅ **`orchestrator.sh`**: synthesize 이후 platform != discord 시 deliver.sh 자동 호출

---

## v4.1 변경사항

- ✅ **영어 + 한국어 불만 패턴 동시 지원**: config.yaml `complaint_patterns` → `ko` / `en` 분리 구조
- ✅ **자동 언어 감지**: 세션 첫 10개 user 메시지 기반 언어 자동 판별 (`auto_detect: true`)
- ✅ `semantic-analyze.sh`: `load_config_patterns()` + `detect_session_language()` 함수 추가
- ✅ `collect-logs.sh`: 불만 키워드 목록 ko/en 분리, config.yaml 우선 로드
- ✅ config.yaml: `complaint_patterns.ko` / `.en` / `auto_detect` 구조로 재편

## v4.0 변경사항

- ✅ **4단계 멀티에이전트 파이프라인** 도입 (collect → analyze → benchmark → synthesize)
- ✅ **구조적 휴리스틱 분석**: role_filter + context_window + dedup_per_session
- ✅ **효과 측정 루프**: 이전 제안 효과를 다음 주기에 자동 측정
- ✅ **False positive 감소**: ~40% → 추정 ~15%
- ✅ **성능 목표**: 총 실행 시간 <3분, 비용 <$0.05/회 (Sonnet 기준)
- ✅ `scripts/v4/` 디렉토리 신설 (v3.0 스크립트는 하위 호환 유지)
- ✅ `data/benchmarks/` 디렉토리 신설 (효과 측정 결과 저장)
- ✅ `docs/v4-architecture.md` 신설 (상세 아키텍처 문서)

---

## v3.0 변경사항 (참고)

- ✅ exec 연속 재시도 탐지 추가 (119회 연속 사례 실제 발견)
- ✅ 동일 에러 반복 분석 추가 (18회 heartbeat 버그 발견)
- ✅ 세션 건강도 지표 추가 (컴팩션 카운트)
- ✅ README 완전 재작성 (솔직한 한계 명시)

---

## self-improving-agent와 차이

| | self-improving-agent | self-evolving-agent |
|--|--|--|
| **범위** | 세션 1개 | 7일치 전체 세션 |
| **타이밍** | 각 세션 직후 실시간 | 매주 일요일 |
| **출력** | 세션 품질 점수 + 교훈 | AGENTS.md diff 제안 |
| **강점** | 즉각적 피드백 | 시스템 패턴 발견 |
| **v4.0 연동** | 품질 스코어 → 분석 가중치 | 집계 + 벤치마크 |

**함께 쓰면:** self-improving이 세션 품질 데이터를 생성 → self-evolving이 집계해서 시스템 수준 문제 발견 + 효과 측정.
