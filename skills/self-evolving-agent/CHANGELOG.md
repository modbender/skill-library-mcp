# CHANGELOG — self-evolving-agent

모든 주요 변경 사항을 이 파일에 기록합니다.
[Semantic Versioning](https://semver.org/) 준수.

---

## [5.0.0] — 2026-02-18

### ✨ 추가 (Added)

- **Pillar 1: 시맨틱 임베딩 (`scripts/v5/embedding-analyze.sh`)** ⭐
  - Ollama `nomic-embed-text` 모델로 로컬 임베딩 생성 (API 비용 $0)
  - 코사인 유사도 > 0.78 → 불만 신호 확정 (의미론적 판단)
  - 임베딩 벡터 캐시 (`~/.sea-embeddings-cache/`) — 동일 세션 재계산 없음
  - 패턴 군집화 (k-means, k=5) — 자동 패턴 발견
  - 신뢰도 점수 (임베딩 유사도 × 역할 가중치 × 감정 신호)
  - 거짓양성률 ~15% → ~8% 감소 (추정)
  - Ollama 오프라인 시 v4 휴리스틱 자동 폴백

- **Pillar 2: 스트리밍 모니터 (`scripts/v5/stream-monitor.sh`)** ⭐
  - `tail -F` 기반 실시간 로그 감시 (주 1회 배치 → 실시간)
  - `--poll` 모드: 30초 간격 폴링 (테스트/CI/비대화형 환경)
  - 임계치 기반 즉각 알림: exec 5회 연속, 크론 에러 3회, 불만 급등
  - 조용한 시간 설정 (23:00–08:00 알림 억제)
  - `data/stream-alerts/` 큐 — 주간 분석에 자동 통합
  - 알림 지연 <30초

- **Pillar 3: 플릿 분석 (`scripts/v5/fleet-analyzer.sh`)** ⭐
  - `~/.openclaw/agents/` 내 모든 에이전트 인스턴스 자동 탐지
  - 교차 인스턴스 패턴 비교 (opus vs sonnet vs haiku)
  - 공통 패턴 → 시스템 수준 AGENTS.md 개선 권고
  - 인스턴스별 고유 패턴 → 모델 특화 조정 권고
  - 플릿 건강도 점수 (가중 평균)
  - `data/fleet/fleet-YYYYMMDD.json` 결과 저장

- **트렌드 분석 (`scripts/v5/trend-analyzer.sh`)** ⭐
  - 최근 4주 분석 결과 비교 (패턴 빈도 추세)
  - Emerging 패턴: 4주 평균 대비 2× 이상 급증
  - Resolved 패턴: 4주 평균 대비 20% 이하로 감소
  - 계절성 패턴 감지 (특정 요일/시간 집중)
  - `data/trends/trends-YYYYMMDD.json` 결과 저장

- **v5 오케스트레이터 (`scripts/v5/orchestrator.sh`)**
  - 신규 6단계 파이프라인 조율
  - Ollama 오프라인 감지 → v4 자동 폴백 (`EMBEDDING_FALLBACK=true`)
  - 스트림 알림 주간 배치 통합

- **신규 `sea` CLI 명령어 (v2.0.0)**
  - `sea monitor` — 실시간 스트리밍 모니터 시작
  - `sea monitor --poll` — 폴링 모드
  - `sea alerts` — 스트림 알림 목록
  - `sea alerts --clear` — 알림 초기화
  - `sea trends` — 주간 트렌드 분석
  - `sea trends --json` — JSON 출력
  - `sea patterns` — 시맨틱 패턴 라이브러리
  - `sea patterns add "<text>" --label <label>` — 앵커 패턴 추가
  - `sea fleet` — 플릿 분석
  - `sea fleet --agents opus,sonnet` — 특정 에이전트 분석

- **`config.yaml` v5 섹션 추가**
  - `embedding:` — 임베딩 모델, 캐시, 임계치 설정
  - `streaming:` — 실시간 모니터 임계치, 조용한 시간
  - `fleet:` — 플릿 에이전트 목록, 가중치
  - `trends:` — 트렌드 비교 주 수, 임계치

- **문서**
  - `docs/v5-architecture.md` 신설 — v5 아키텍처 전체 문서 (ASCII 다이어그램 포함)
  - `docs/migration-v4-to-v5.md` 신설 — v4 → v5 마이그레이션 단계별 가이드
  - `tests/test-v5.sh` 신설 — v5 컴포넌트 독립 테스트

### 🔧 변경 (Changed)

- `synthesize-proposal.sh` — 임베딩 분석 결과, 트렌드, 플릿 데이터를 합성 입력으로 통합
- `collect-logs.sh` — 스트림 알림 통합 (`data/stream-alerts/` 자동 스캔)
- `bin/sea` v2.0.0 — `monitor`, `alerts`, `trends`, `patterns`, `fleet` 명령 추가

### 🛡️ 보안 (Security)

- 임베딩 캐시에 민감 정보 포함 방지 (메시지 원문 미저장, 벡터만 저장)
- `~/.sea-embeddings-cache/` 권한 자동 설정 (600)

### ⚡ 성능 (Performance)

- 임베딩 캐시로 동일 세션 재분석 시 <10초 (캐시 없을 때 <5분)
- `--dry-run` 플래그 — 실제 임베딩 계산 없이 파이프라인 검증

---

## [4.3.0] — 2026-02-18

### ✨ 추가 (Added)

- **멀티플랫폼 배달 (`deliver.sh`)**
  - `scripts/v4/deliver.sh` 신규: Slack Incoming Webhook, Telegram Bot API, Generic Webhook 지원
  - Discord는 OpenClaw 크론 native delivery로 처리 (deliver.sh 미호출)
  - `config.yaml`에 `delivery:` 섹션 추가 — 플랫폼별 자격증명 구조화

- **`config.yaml` 불만 패턴 언어 분리 구조 (`ko/en`)**
  - 기존 flat list → `ko:` / `en:` 서브키 분리 구조로 변경
  - `auto_detect: true` 옵션: 세션 첫 10개 user 메시지 중 한글 비율로 언어 자동 감지
  - 오탐 위험 패턴(`"다시"`, `"계속"`, `"반복"` 등) 제거, 구체적 불만 표현으로 교체
  - 각 패턴에 배제 근거 주석 추가

- **문서**
  - `docs/migration-v3-to-v4.md` 신규: v3 → v4 마이그레이션 가이드 (단계별 지침 + FAQ)
  - `CONTRIBUTING.md` 전면 개선: 개발 환경 설정, 테스트 방법, 코드 스타일 가이드, 새 패턴/플랫폼 추가 방법, 이슈 라벨 설명
  - `.github/PULL_REQUEST_TEMPLATE.md` 신규: What/Why/How + 체크리스트 형식

- **GitHub 이슈 템플릿 개선**
  - `bug_report.yml`: OS, bash 버전, OpenClaw 버전, 파이프라인 전체 출력, 스테이지 로그 필드 추가
  - `feature_request.yml`: 사용 사례, 기대 동작, 대안 섹션 추가
  - `good_first_issue.yml`: 멘토링 가용 여부, 예상 소요 시간, 필요 기술 필드 추가

### 🔧 변경 (Changed)

- `config.yaml` `complaint_patterns` 구조 변경 (v3 flat list → v4 ko/en dict)
  - **마이그레이션 필요:** `docs/migration-v3-to-v4.md` 참조
- `register-cron.sh` 크론 메시지가 `generate-proposal.sh` 대신 `scripts/v4/orchestrator.sh` 호출

---

## [4.1.0] — 2026-02-18

### ✨ 추가 (Added)

- **멀티플랫폼 배달 (`deliver.sh`)**
  - `scripts/v4/deliver.sh` 신규: Slack Incoming Webhook, Telegram Bot API, Generic Webhook 지원
  - Discord는 OpenClaw 크론 native delivery로 처리 (deliver.sh 미호출)
  - `config.yaml`에 `delivery:` 섹션 추가 — 플랫폼별 자격증명 구조화

- **`config.yaml` 불만 패턴 언어 분리 구조 (`ko/en`)**
  - 기존 flat list → `ko:` / `en:` 서브키 분리 구조로 변경
  - `auto_detect: true` 옵션: 세션 첫 10개 user 메시지 중 한글 비율로 언어 자동 감지
  - 오탐 위험 패턴(`"다시"`, `"계속"`, `"반복"` 등) 제거, 구체적 불만 표현으로 교체
  - 각 패턴에 배제 근거 주석 추가

- **문서**
  - `docs/migration-v3-to-v4.md` 신규: v3 → v4 마이그레이션 가이드 (단계별 지침 + FAQ)
  - `CONTRIBUTING.md` 전면 개선: 개발 환경 설정, 테스트 방법, 코드 스타일 가이드, 새 패턴/플랫폼 추가 방법, 이슈 라벨 설명
  - `.github/PULL_REQUEST_TEMPLATE.md` 신규: What/Why/How + 체크리스트 형식

- **GitHub 이슈 템플릿 개선**
  - `bug_report.yml`: OS, bash 버전, OpenClaw 버전, 파이프라인 전체 출력, 스테이지 로그 필드 추가
  - `feature_request.yml`: 사용 사례, 기대 동작, 대안 섹션 추가
  - `good_first_issue.yml`: 멘토링 가용 여부, 예상 소요 시간, 필요 기술 필드 추가

### 🔧 변경 (Changed)

- `config.yaml` `complaint_patterns` 구조 변경 (v3 flat list → v4 ko/en dict)
  - **마이그레이션 필요:** `docs/migration-v3-to-v4.md` 참조
- `register-cron.sh` 크론 메시지가 `generate-proposal.sh` 대신 `scripts/v4/orchestrator.sh` 호출

---

## [4.0.0] — 2026-02-17

### ✨ 추가 (Added)

- **멀티 스테이지 파이프라인 (`scripts/v4/`)**
  - `orchestrator.sh`: v4 메인 진입점. 크론에 의해 호출되며 각 스테이지를 순서대로 실행
  - `collect-logs.sh` (Stage 1): 세션 로그 + 크론 로그 수집 → `logs.json`
  - `semantic-analyze.sh` (Stage 2): 불만 패턴 감지, exec 재시도 신호, 위반 패턴 추출 → `analysis.json`
  - `benchmark.sh` (Stage 3): GitHub star count, ClawHub 메트릭 수집 → `benchmarks.json`
  - `measure-effects.sh` (Stage 4): 과거 제안 효과 측정 (적용 전/후 패턴 카운트 비교) → `effects.json`
  - `synthesize-proposal.sh` (Stage 5): 전 스테이지 결과를 종합해 Markdown 제안서 생성 → `proposal.md`

- **오케스트레이터 설계 원칙**
  - bash 3.2 호환 (macOS 기본 셸): `declare -A` 미사용, 빈 배열 `${#arr[@]}` 미사용
  - `SHELLOPTS= BASHOPTS=` 전달로 부모 `set -euo pipefail` 전파 차단
  - `run_stage()` 래퍼: 스테이지 실패 시 다음 스테이지 계속 진행 (`|| true` 패턴)
  - 스테이지별 실행 시간 + 성공/실패 상태 집계 → `run-meta.json`
  - 전체 실행 목표: 3분 이하

- **`register-cron.sh` v2.0 개선**
  - `config.yaml`에서 스케줄/채널/모델 자동 로드
  - `--update` 플래그: 기존 크론 설정 업데이트
  - `--remove` 플래그: 크론 제거
  - Python 서브프로세스 실패 시 명확한 에러 메시지

- **CI (`ci.yml`)**
  - GitHub Actions: PR마다 `shellcheck` 자동 실행
  - 대상: `scripts/*.sh`, `scripts/lib/*.sh`, `scripts/v4/*.sh`

### 🔧 변경 (Changed)

- 기존 `scripts/analyze-behavior.sh` + `scripts/generate-proposal.sh` (v3 레거시)는 유지되나 적극 유지보수 대상에서 제외
- 임시 파일 경로: `/tmp/self-evolving-analysis.json` (단일 파일) → `/tmp/sea-v4/` (스테이지별 파일)
- 크론 배달 방식: `generate-proposal.sh` stdout → `orchestrator.sh` stdout (OpenClaw native delivery)

### 🛡️ 보안 (Security)

- 모든 `scripts/v4/` 스크립트에 SECURITY MANIFEST 주석 추가
- 외부 엔드포인트 접근: `benchmark.sh`만 GitHub API + ClawHub API (선택적, 실패 시 건너뜀)

---

## [3.0.0] — 2026-02-17

### 🔴 버그 수정 (Bug Fixes)

- **`build_report` heredoc 백틱 인터폴레이션 버그 수정**
  - `python3 << PYEOF` → 외부 Python 파일 (`sea-rpt-$$.py`) 방식으로 교체
  - 이전: `거부: [이유]`, `제안 #N을 이렇게 바꿔줘` 등이 셸 명령으로 실행됨
  - 수정: `command not found` 에러 완전 제거, 특수문자 안전하게 처리

- **`log_error_signatures` 파일 간 오염 버그 수정**
  - 이전: 전역 dict로 heartbeat-cron.log 에러 카운트가 metrics-cron.log에 누적됨
  - 수정: 파일별 독립 `file_error_signatures` dict 사용

- **`retry worst_streak_val` 다른 도구 값 오용 수정**
  - 이전: exec 제안의 "최대 연속 재시도"에 browser의 119회 streak이 표시됨
  - 수정: `worst_streaks`를 해당 도구명으로 필터링 후 참조

### ✨ 기능 개선 (Improvements)

- **retry 분석 정밀도 향상 (오탐 감소)**
  - 파일 I/O 도구 제외: `read`, `write`, `edit`, `image`, `tts`, `canvas`
  - 세션 카운팅 임계값: 3 → 5 (5회 이상 연속 호출만 "재시도 신호"로 분류)
  - `worst_streaks` 기록 임계값: 10회 이상 연속만 기록
  - 대상 도구 집중: `exec`, `process`, `browser`, `cron`, `web_search` 등 효과 도구만

- **`config.yaml` 불만 패턴 오탐 패턴 제거**
  - 제거: `"다시"`, `"아까"`, `"계속"`, `"반복"`, `"기억"`, `"확인중"` (일반 요청과 구분 불가)
  - 추가: `"다시 또"`, `"다시 해야"`, `"still not working"`, `"how many times"` (구체적 불만 표현)
  - 주석 추가: 오탐 위험 패턴 배제 근거 문서화

- **evidence 텍스트 정확도 향상**
  - "3회 이상 연속 재시도" → "5회 이상 연속 호출"로 수정
  - "read/write/edit/image 등 파일 I/O는 제외하고 집계" 명시

- **리포트 가독성 향상**
  - 근거 텍스트 줄바꿈 렌더링 개선 (`> 근거:` + 멀티라인)
  - backtick이 포함된 메시지 문구 이스케이프 없이 안전하게 출력

### 🧪 테스트 검증

- `python3 -m json.tool` JSON 유효성 검증 통과
- 엣지 케이스 검증:
  - 세션 0개 (`AGENTS_DIR=/tmp/empty`) → 정상 빈 JSON 출력
  - 에러 0개 → "no-issues-found" 제안 출력
  - `.learnings/` 없을 때 → learnings.total_pending = 0
- `generate-proposal.sh` 출력 안정성 확인 (shell 에러 없음)

---

## [2.0.0] — 2026-02-17

### ✨ 추가

- `config.yaml` 지원: 분석 기간, 패턴, 크론 스케줄 등 외부 설정 파일로 관리
- `scripts/lib/config-loader.sh`: YAML → bash 변수 자동 로드 (PyYAML 없어도 동작)
- `self-improving-agent .learnings/` 연동: ERRORS.md, LEARNINGS.md, FEATURE_REQUESTS.md 파싱
- v3.0 분석 신호 추가: exec 5210회 연속 재시도 패턴 감지 기원

### 🔧 변경

- 분석 아키텍처 리팩토링: 인라인 Python → 임시 파일 기반 (heredoc 안전성)
- `tool_use` → `toolCall` 실제 필드명 수정

---

## [1.0.0] — 2026-02-17

### ✨ 초기 릴리즈

- 주간 세션 로그 분석 (최근 N일, 최대 M개 세션)
- 불만 패턴 감지 (한국어/영어 키워드)
- AGENTS.md 규칙 위반 감지 (exec 명령 기반)
- 반복 요청 패턴 집계
- 크론 에러 분석 (consecutiveErrors)
- 로그 에러 분석 (cron-catchup.log 등)
- diff-format 개선 제안 생성
- 거부 기록 영속화 (`data/rejected-proposals.json`)
- 만료 제안 자동 아카이브

---

> **변경 유형 범례:**
> - ✨ 추가 (Added)
> - 🔧 변경 (Changed)
> - 🗑️ 제거 (Removed)
> - 🔴 버그 수정 (Fixed)
> - 🛡️ 보안 (Security)
