# v4 → v5 마이그레이션 가이드

> **마이그레이션 필수 여부:** 아니오. v4 오케스트레이터는 v5.0 이후에도 그대로 동작합니다.  
> v5 기능(시맨틱 임베딩, 스트리밍 모니터, 플릿 분석)을 원할 때 이 가이드를 따르세요.

---

## 무엇이 달라졌나?

### 신규 기능 (3가지 기둥)

| 기능 | 파일 | 설명 |
|------|------|------|
| **시맨틱 임베딩** | `scripts/v5/embedding-analyze.sh` | Ollama 로컬 임베딩으로 의미론적 패턴 분석 |
| **스트리밍 모니터** | `scripts/v5/stream-monitor.sh` | 실시간 로그 감시 + 즉각 알림 |
| **플릿 분석** | `scripts/v5/fleet-analyzer.sh` | 다중 에이전트 인스턴스 교차 분석 |
| **트렌드 분석** | `scripts/v5/trend-analyzer.sh` | 주간 패턴 추세 비교 |
| **v5 오케스트레이터** | `scripts/v5/orchestrator.sh` | 신규 파이프라인 조율 (v4 폴백 내장) |

### 변경된 것 (Breaking)

없음. v5.0은 완전 상위 호환입니다.

### 추가된 CLI 명령어

| 명령어 | 기능 |
|--------|------|
| `sea monitor` | 실시간 스트리밍 모니터 시작 |
| `sea alerts` | 트리거된 스트림 알림 목록 |
| `sea trends` | 주간 트렌드 분석 결과 |
| `sea patterns` | 시맨틱 패턴 라이브러리 관리 |
| `sea fleet` | 플릿 분석 결과 (다중 인스턴스) |

### 추가된 데이터 디렉토리

```
data/stream-alerts/   ← 실시간 알림 큐
data/fleet/           ← 플릿 분석 결과
data/trends/          ← 트렌드 분석 결과
~/.sea-embeddings-cache/  ← 임베딩 벡터 캐시
```

---

## 새 의존성

### Ollama (권장, 없어도 동작)

v5.0은 Ollama가 없으면 **자동으로 v4 휴리스틱 모드로 폴백**합니다.

```bash
# macOS
brew install ollama

# 임베딩 모델 다운로드 (1회만, ~274MB)
ollama pull nomic-embed-text

# 백그라운드 실행
ollama serve &
```

Ollama 없이 v5를 실행하면:
```
[SEA v5] Ollama 오프라인 감지 → v4 휴리스틱 폴백 활성화
[SEA v5] 임베딩 분석 건너뜀 (EMBEDDING_FALLBACK=true)
[SEA v5] FP 추정: ~15% (v4 수준)
```

### jq (권장)

스트리밍 모니터와 플릿 분석이 JSON 파싱에 사용합니다.

```bash
brew install jq
```

없으면 python3로 폴백합니다.

---

## 새 config.yaml 섹션

`config.yaml`에 다음 섹션을 추가하세요. **기존 섹션은 수정 불필요합니다.**

```yaml
# ── v5.0 임베딩 설정 ─────────────────────────────────────
embedding:
  # Ollama 임베딩 모델 (nomic-embed-text 권장)
  model: "nomic-embed-text"
  url: "http://localhost:11434"

  # 코사인 유사도 임계치 (0.78 권장)
  similarity_threshold: 0.78

  # 임베딩 캐시 경로
  cache_dir: "~/.sea-embeddings-cache"

  # 캐시 TTL (일)
  cache_ttl_days: 30

  # Ollama 오프라인 시 자동 폴백 (true 권장)
  fallback_to_heuristic: true

# ── v5.0 스트리밍 모니터 설정 ────────────────────────────
streaming:
  # 감시 대상 로그 파일
  log_files:
    - "~/.openclaw/logs/cron-catchup.log"
    - "~/.openclaw/logs/heartbeat-cron.log"

  # 알림 임계치
  thresholds:
    exec_consecutive_retries: 5  # exec 5회 연속 재시도
    cron_error_repeats: 3        # 크론 에러 3회 반복
    frustration_burst: 3         # 10분 내 불만 신호 3회

  # 알림 채널
  alert_channel: ""  # Discord 채널 ID (비어 있으면 cron.discord_channel 사용)

  # 조용한 시간 (알림 억제)
  quiet_hours:
    start: "23:00"
    end: "08:00"
    tz: "Asia/Seoul"

# ── v5.0 플릿 설정 ───────────────────────────────────────
fleet:
  # 분석 대상 에이전트 목록 (빈 배열 = 전체 자동 감지)
  agents: []  # 예: ["opus", "sonnet", "haiku"]

  # 플릿 건강도 점수 가중치 (합계 = 1.0)
  weights:
    frustration: 0.4
    exec_retries: 0.3
    cron_errors: 0.3

  # 공통 패턴 임계치 (N개 이상 에이전트에서 발생 시 "공통"으로 분류)
  common_pattern_threshold: 2

# ── v5.0 트렌드 설정 ─────────────────────────────────────
trends:
  # 비교할 과거 주 수
  lookback_weeks: 4

  # Emerging 패턴 임계치 (이번 주 빈도가 4주 평균의 N배 이상)
  emerging_multiplier: 2.0

  # Resolved 패턴 임계치 (이번 주 빈도가 4주 평균의 N% 이하)
  resolved_threshold: 0.2
```

---

## 새 CLI 명령어

```bash
# 실시간 스트리밍 모니터 시작 (Ctrl+C로 종료)
sea monitor

# 폴링 모드 (30초 간격, 터미널 비대화형 환경용)
sea monitor --poll

# 주간 스트림 알림 목록
sea alerts

# 알림 초기화 (처리 후)
sea alerts --clear

# 주간 트렌드 분석
sea trends

# 트렌드를 JSON으로 (CI/자동화용)
sea trends --json

# 시맨틱 패턴 라이브러리 확인
sea patterns

# 앵커 패턴 추가 (임베딩 앵커로 등록)
sea patterns add "또 같은 실수를 반복했어" --label frustration

# 플릿 분석 (전체 에이전트 인스턴스)
sea fleet

# 특정 에이전트만 분석
sea fleet --agents opus,sonnet
```

---

## 하위 호환성 (v4 오케스트레이터)

v5를 설치해도 v4 오케스트레이터는 그대로 동작합니다.

```bash
# v4 파이프라인 직접 실행 (변화 없음)
bash scripts/v4/orchestrator.sh

# v5 파이프라인 실행 (Ollama 없으면 v4 자동 폴백)
bash scripts/v5/orchestrator.sh

# 크론을 v4로 유지하려면
bash scripts/register-cron.sh --v4

# 크론을 v5로 업그레이드
bash scripts/register-cron.sh --v5
```

---

## 마이그레이션 단계별 가이드

### Step 0: 현재 상태 확인 (선택 사항)

```bash
# 현재 버전 확인
sea version

# 현재 제안 상태 확인
sea proposals --all

# 기존 데이터 백업 (선택)
cp -r data/ data-v4-backup-$(date +%Y%m%d)/
```

### Step 1: Ollama 설치 및 임베딩 모델 준비

```bash
brew install ollama
ollama pull nomic-embed-text   # 274MB, 1회만
ollama serve &                  # 백그라운드 실행

# 동작 확인
curl -s http://localhost:11434/api/tags | grep nomic
```

### Step 2: config.yaml 업데이트

`config.yaml`에 v5 섹션 추가 (위 섹션 참조). 기존 섹션은 수정 불필요.

```bash
# config 검증
bash scripts/validate-config.sh --fix
```

### Step 3: 신규 데이터 디렉토리 생성

```bash
mkdir -p data/stream-alerts data/fleet data/trends
mkdir -p ~/.sea-embeddings-cache
```

v5 오케스트레이터가 자동 생성하지만, 미리 만들어도 됩니다.

### Step 4: 크론 업데이트 (선택)

```bash
# 기존 v4 크론을 v5로 업데이트
bash scripts/register-cron.sh --v5 --update
```

### Step 5: 스트리밍 모니터 시작 (선택)

상시 실시간 감지를 원하면 별도 크론으로 등록:

```bash
# 스트리밍 모니터는 별도 LaunchAgent 또는 백그라운드 프로세스로 실행
nohup bash scripts/v5/stream-monitor.sh --poll >> ~/.openclaw/logs/sea-monitor.log 2>&1 &
```

또는 `sea monitor` 명령으로 포그라운드 실행.

### Step 6: 첫 v5 실행 테스트

```bash
# v5 파이프라인 수동 테스트 실행
bash scripts/v5/orchestrator.sh --dry-run

# 임베딩 분석만 테스트
bash scripts/v5/embedding-analyze.sh --test
```

---

## FAQ

**Q: Ollama 없이 v5를 설치하면 어떻게 되나요?**

> 자동으로 v4 휴리스틱 모드로 폴백합니다. 임베딩 분석, 스트리밍 모니터는 비활성화되지만 플릿 분석과 트렌드 분석은 계속 동작합니다. 언제든 Ollama를 설치하면 자동으로 임베딩 경로로 전환됩니다.

**Q: v4 크론을 v5 크론으로 교체해야 하나요?**

> 교체를 권장하지만 필수는 아닙니다. v4 크론을 그대로 두고 v5 스크립트를 별도로 실행해도 됩니다. `sea fleet`와 `sea trends`는 크론 없이 수동 실행도 가능합니다.

**Q: 임베딩 캐시가 디스크를 많이 차지하나요?**

> 세션당 약 1.5KB (384차원 float32 벡터). 30세션 × 52주 = 약 2.3MB/년. 사실상 무시 가능합니다. `cache_ttl_days: 30` 설정으로 오래된 캐시는 자동 삭제됩니다.

**Q: 기존 제안 데이터가 유지되나요?**

> 모두 유지됩니다. `data/proposals/`는 v5에서도 동일하게 사용됩니다. `sea proposals`와 `sea approve`도 기존과 동일하게 동작합니다.

**Q: v4.x에서 v5.0으로 CHANGELOG를 보려면?**

> `CHANGELOG.md`의 `[5.0.0]` 섹션을 참조하세요.
