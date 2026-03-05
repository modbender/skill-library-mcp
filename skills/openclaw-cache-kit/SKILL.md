---
name: OpenClaw Cache Kit
description: Automatically apply Claude prompt caching optimizations to OpenClaw. Reduces API costs by up to 89% via cacheRetention long, 59-minute heartbeat, cache-ttl pruning, and CRON.md separation strategy.
version: 1.1.1
author: raon
inspired_by: https://slashpage.com/thomasjeong/36nj8v2wq5zqj25ykq9z
---

# openclaw-cache-kit

> **Inspired by**: [OpenClaw 프롬프트 캐싱 최적화 가이드](https://slashpage.com/thomasjeong/36nj8v2wq5zqj25ykq9z)

Claude API 비용을 최대 89%까지 줄이는 OpenClaw 캐싱 최적화 킷.

---

## 왜 캐싱이 중요한가?

OpenClaw는 **매 요청마다** 다음 파일들을 시스템 프롬프트로 전송합니다:
- `SOUL.md` — 페르소나·운영 규칙 (수백~수천 토큰)
- `AGENTS.md`, `TOOLS.md`, `MEMORY.md` — 컨텍스트 파일들
- `CRON.md` — 크론 스케줄 (자주 실행될수록 비용 ↑)

기본 설정에서는 이 대용량 시스템 프롬프트가 **캐시 없이 매번 과금**됩니다.

Claude Sonnet 기준 토큰 가격:
| 유형 | 가격 |
|------|------|
| Input (캐시 미스) | $3.00 / 1M tokens |
| Cache Read (캐시 히트) | $0.30 / 1M tokens |
| **절약률** | **90%** |

---

## 4가지 핵심 설정

### 1. `cacheRetention: "long"`
캐시 보존 기간을 최대(5분 → 최대 지원값)로 설정. Sonnet 모델에 적용.

### 2. `contextPruning.ttl: "1h"`
오래된 컨텍스트를 1시간 단위로 정리해 캐시 히트율 유지.

### 3. `heartbeat.every: "59m"`
Claude의 캐시 TTL(보통 1시간) 만료 직전에 하트비트로 캐시 갱신.
59분 주기 = 만료 1분 전에 갱신 → 캐시 연속성 유지.

### 4. `diagnostics.cacheTrace.enabled: true`
`~/.openclaw/logs/cache-trace.jsonl`에 캐시 히트/미스 로그 기록.
절약 금액 실시간 확인 가능.

---

## 설치 및 적용

```bash
# 1. 캐싱 최적화 적용 (openclaw.json 자동 업데이트 + gateway 재시작)
bash scripts/apply.sh

# 2. 오늘 캐시 절약액 확인
bash scripts/check-savings.sh
```

---

## CRON.md 분리 전략

크론 메시지가 길면 매 실행마다 토큰 소비 증가. → **CRON.md를 짧게**.

상세 내용: `scripts/cron-md-template.md` 참고.

**핵심 원칙**:
- CRON.md에는 스케줄과 최소 지시문만
- 상세 운영 규칙은 SOUL.md·AGENTS.md에 위임
- 크론 메시지 1건당 목표: 50토큰 이하

---

## 절약 확인

```bash
bash scripts/check-savings.sh
# 예시 출력:
# 📊 오늘 캐시 절약 리포트 (2026-02-19)
# cacheRead 토큰: 1,234,567
# 절약 금액: $3.33 (vs 캐시 없을 때)
```

---

## 파일 구조

```
openclaw-cache-kit/
├── SKILL.md                    # 이 파일
└── scripts/
    ├── apply.sh                # 캐싱 설정 적용
    ├── check-savings.sh        # 절약 금액 확인
    └── cron-md-template.md     # CRON.md 분리 전략 템플릿
```
