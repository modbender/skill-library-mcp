# 🌅 Raon OS

**스타트업의 첫 번째 AI 동료 — 아이디어를 사업으로 만드는 OS**

[![npm](https://img.shields.io/npm/v/@yeomyeonggeori/raon-os?color=f59e0b&label=npm)](https://www.npmjs.com/package/@yeomyeonggeori/raon-os)
[![license](https://img.shields.io/npm/l/@yeomyeonggeori/raon-os?color=22c55e)](./LICENSE)

> 사업계획서 평가부터 정부 지원사업 매칭, 투자자 연결까지.
> 한국 스타트업 파운더를 위한 AI Companion Skill.

---

## ✨ Features

| 기능 | 설명 | 상태 |
|------|------|------|
| 📄 **사업계획서 평가** | PDF/텍스트 → 100점 만점 종합 점수 + 항목별 개선안 | ✅ |
| 🏛️ **정부 지원사업 매칭** | TIPS, 예비창업패키지 등 최적 프로그램 추천 (가중치 스코어링) | ✅ |
| 📝 **지원서 초안** | 사업계획서 기반 정부 지원사업 지원서 자동 생성 | ✅ |
| 🔄 **다중 문서 비교** | 2개 이상 사업계획서 비교 분석 | ✅ |
| 🔍 **RAG 하이브리드 검색** | bge-m3 벡터 + BM25 키워드 매칭 — 한국어 프로그램명 정확 검색 | ✅ |
| 🔁 **Reranker** | LLM 기반 Top-10 → Top-3 재정렬 (`--rerank`) | ✅ |
| 🔤 **형태소 분석** | kiwipiepy 한국어 BM25 토크나이저 — 조사/어미 분리로 검색 정확도 향상 | ✅ |
| 💬 **멀티턴 대화형 평가** | interactive CLI + `/v1/chat` API 세션 — 대화로 사업계획 개선 | ✅ |
| 💰 **기업 밸류에이션** | Scorecard/Berkus/Revenue Multiple + 한국 시장 보정 | ✅ |
| 📊 **Eval Pipeline** | LLM 평가 vs 실제 심사결과 정확도 검증 | ✅ |
| 📊 **JSON 출력** | `--json` 옵션으로 구조화된 데이터 반환 | ✅ |
| 📁 **파일 저장** | `--output result.md`로 결과 파일 저장 | ✅ |
| 📜 **히스토리** | 평가 이력 자동 기록 + `history` 명령어 조회 | ✅ |
| 🎯 **온보딩** | 첫 실행 시 환경 자동 감지 + 가이드 | ✅ |
| 💰 **투자자 프로필 분석** | 투자자 관점 매력도 분석 + Deal Summary + Red Flags | ✅ |
| 🌐 **HTTP API 서버** | `raon.sh serve` — REST API로 웹챗/외부 서비스 연동 | ✅ |

## 🚀 Quick Start

### OpenClaw 스킬로 설치

```bash
# OpenClaw에서 바로 사용
clawhub install @yeomyeonggeori/raon-os
```

### CLI로 직접 사용

```bash
# 사업계획서 평가
raon.sh biz-plan evaluate --file 사업계획서.pdf

# 대화형 평가 (멀티턴)
raon.sh biz-plan interactive --file plan.pdf

# JSON 형식 출력
raon.sh biz-plan evaluate --file 사업계획서.pdf --json

# 결과를 파일로 저장
raon.sh biz-plan evaluate --file 사업계획서.pdf --output result.md

# 두 사업계획서 비교 분석
raon.sh biz-plan evaluate --file plan_a.pdf --file plan_b.pdf

# 정부 지원사업 매칭 (가중치 스코어링)
raon.sh gov-funding match --industry "AI/SaaS" --stage "early"

# TIPS 심사 기준 확인
raon.sh gov-funding info --program "TIPS"

# 지원서 초안 생성
raon.sh gov-funding draft --program "TIPS" --file 사업계획서.pdf

# 기업 밸류에이션
raon.sh valuation estimate --stage seed --industry ai --tips

# 투자자 관점 프로필 분석
raon.sh investor-match profile --file 사업계획서.pdf

# RAG 검색 + Reranker
python3 rag_pipeline.py search --query "TIPS" --rerank

# HTTP API 서버 수동 실행
python3 scripts/server.py       # 기본 포트 8400

# 시스템 자동시작 설정 (선택)
bash scripts/install-service.sh

# 평가 히스토리 조회
raon.sh history
```

## 📊 평가 항목

사업계획서를 6가지 핵심 항목으로 분석합니다:

```
1. 문제 정의 및 솔루션 적합성
2. 시장 규모 및 경쟁 분석
3. 비즈니스 모델 타당성
4. 팀 역량
5. 재무 계획
6. 기술 차별성
```

정부 심사위원 기준 + 500+ 스타트업 평가 데이터 기반.

## 💰 기업 밸류에이션

초기 스타트업을 위한 3가지 밸류에이션 방법론을 지원합니다:

| 방법론 | 설명 | 적합 단계 |
|--------|------|-----------|
| **Scorecard** | 엔젤 투자 평균 밸류 대비 팀·시장·제품 등 6개 항목 가중 비교 | Pre-seed / Seed |
| **Berkus** | 기술 리스크 5개 축(아이디어·프로토타입·팀·전략적 관계·매출) 각 최대 ₩1B | Pre-revenue |
| **Revenue Multiple** | 업종별 매출 배수 × 연간 매출/ARR | Seed+ (매출 발생) |

모든 방법론에 **한국 시장 보정**이 적용됩니다:
- 한국 VC 평균 밸류에이션 데이터 반영
- TIPS 선정 여부에 따른 프리미엄 (`--tips`)
- 업종별 국내 비교 기업 벤치마크

## 🏛️ 정부 지원사업 프로그램

| 프로그램 | 총 예산 | 규모 | 대상 |
|----------|--------|------|------|
| TIPS (창업성장기술개발) | 7,864억 | 최대 8억원 | 창업 7년 이내 (신산업 10년) |
| 초격차 스타트업 프로젝트 | 1,456억 | - | 딥테크 업력 10년 이내 |
| 민관공동창업자발굴육성 | 1,237억 | - | 투자받은 7년 이내 |
| 청년창업사관학교 | 1,025억 | - | 만 39세 이하 청년 |
| 창업중심대학 | 883억 | - | 예비~업력 7년 이내 |
| 창업도약패키지 | 728억 | 최대 3억원 | 창업 3~7년 |
| 글로벌 기업 협업 프로그램 | 600억 | - | 업력 7년 이내 |
| 초기창업패키지 | 559억 | 최대 1억원 | 창업 3년 이내 |
| 예비창업패키지 | 491억 | 최대 1억원 | 예비 창업자 |
| 재도전성공패키지 | 150억 | - | 재창업 7년 이내 |
| Global TIPS | - | 최대 50억원 | TIPS 선정 + 해외투자 |

> 📊 2026 통합공고 기준 (중기부 공고 제2025-648호, 총 508개 사업 3.46조원)

## 🌐 HTTP API 서버

웹챗이나 외부 서비스에서 REST API로 연동할 수 있습니다:

```bash
# 서버 수동 실행
python3 scripts/server.py       # http://localhost:8400

# 시스템 자동시작 설정 (선택)
bash scripts/install-service.sh
```

| 엔드포인트 | 메서드 | 설명 |
|-----------|--------|------|
| `/health` | GET | 헬스체크 |
| `/v1/modes` | GET | 지원 모드 목록 |
| `/v1/evaluate` | POST | 사업계획서 평가 |
| `/v1/improve` | POST | 개선안 생성 |
| `/v1/match` | POST | 정부 지원사업 매칭 |
| `/v1/draft` | POST | 지원서 초안 (program 필수) |
| `/v1/checklist` | POST | 지원 준비 점검 (program 필수) |
| `/v1/investor` | POST | 투자자 프로필 분석 |
| `/v1/chat` | POST | 멀티턴 대화형 평가 세션 |
| `/v1/valuation` | POST | 기업 밸류에이션 산출 |
| `/v1/feedback` | POST | 평가 결과 피드백 저장 |

CORS 지원 — 웹 프론트엔드에서 바로 호출 가능.

### `/v1/feedback` 상세

```
POST /v1/feedback
Body: {"evaluation_id": "uuid", "rating": 1 또는 -1, "comment": "선택"}
Response: {"ok": true}
```

평가 결과에 대한 좋아요(1) / 싫어요(-1) 피드백을 저장합니다. `comment` 필드는 선택사항입니다.

## ⚙️ 환경변수 설정

`.env` 파일 또는 셸 환경에서 아래 변수를 설정합니다. **실제 값은 절대 공유하지 마세요.**

### K-Startup AI 엔진 (선택)

K-Startup AI 엔진 연동 시 더 정밀한 평가가 가능합니다:

```bash
RAON_API_URL=https://api.k-startup.ai   # API 서버 URL
RAON_API_KEY=<발급받은 키>               # API 인증 키
```

API 미설정 시 로컬 LLM + RAG 모드로 동작합니다.

👉 API 키 발급: [k-startup.ai](https://k-startup.ai)

### Supabase 피드백 저장 (선택)

`/v1/feedback` 피드백 데이터를 Supabase에 영속 저장하려면 아래 변수를 설정합니다:

```bash
SUPABASE_URL=<Supabase 프로젝트 URL>             # Supabase 프로젝트 URL
SUPABASE_SERVICE_KEY=<서비스 롤 키>               # Supabase 서비스 키 (비공개)
SUPABASE_ACCESS_TOKEN=<Management API 토큰>       # 테이블 자동 생성용 (선택)
```

- `SUPABASE_URL` — Supabase 프로젝트 URL (선택, 로컬 피드백 저장용)
- `SUPABASE_SERVICE_KEY` — Supabase 서비스 키 (선택, 쓰기 권한 필요)
- `SUPABASE_ACCESS_TOKEN` — Supabase Management API 토큰 (테이블 자동 생성용, 선택)

미설정 시 피드백 데이터는 로컬 SQLite에만 저장됩니다.

## 🔒 보안 제한사항

### Admin API 접근 제한
`/api/keys/*` 엔드포인트는 **localhost에서만 접근 가능**합니다. 외부 네트워크에서 admin API를 호출하면 `403 Forbidden`이 반환됩니다.

### 외부 URL 차단 (`fetch_realtime`)
`fetch_realtime` 기능은 허용된 도메인만 접근 가능합니다:
- **허용 도메인 예시**: `jointips.or.kr`, `k-startup.go.kr` 등 정부/파트너 사이트
- 모든 외부 URL은 내부 `is_allowed_url()` 함수로 검사 후, 허용 목록에 없으면 **자동 차단**됩니다.
- 임의의 외부 URL을 `fetch_realtime`에 전달해도 실행되지 않습니다.

> ⚠️ 서버를 공개 인터넷에 노출할 경우 nginx/방화벽으로 `/api/keys/*` 경로를 추가 차단하세요.

## 🔍 RAG 하이브리드 검색

554건의 정부 지원사업 데이터(TIPS, 예비/초기창업패키지, 성공사례 등)를 벡터 + 키워드 하이브리드로 검색합니다:

```bash
# 벡터 검색 (bge-m3 한국어 임베딩)
python3 scripts/rag_pipeline.py search --query "AI 스타트업 TIPS 합격 전략"

# Reranker로 Top-3 정밀 추출
python3 scripts/rag_pipeline.py search --query "TIPS" --rerank

# 데이터 인제스트
python3 scripts/rag_pipeline.py ingest --data-dir eval_data

# 검색 품질 평가
python3 scripts/rag_pipeline.py eval
```

- **임베딩**: `bge-m3` (한국어 최적화, Ollama)
- **토크나이저**: `kiwipiepy` 한국어 형태소 분석 — BM25 정확도 향상
- **검색**: 0.6 × 벡터 유사도 + 0.4 × BM25 키워드 매칭
- **Reranker**: LLM 기반 Top-10 → Top-3 재정렬
- **Top-1 정확도**: 100% (v2026.2.18 기준)
- **데이터**: TIPS 317 / 정부사업 206 / 심사기준 21 / 성공사례 10

## 🏗️ Roadmap

- [x] 사업계획서 평가 (biz-plan)
- [x] 정부 지원사업 매칭 (gov-funding) — 가중치 스코어링
- [x] 다중 문서 비교 분석
- [x] JSON 출력 + 파일 저장
- [x] 평가 히스토리 로깅
- [x] 온보딩 + 진행률 표시
- [x] 투자자 프로필 분석 (investor-match profile)
- [x] HTTP API 서버 (serve)
- [x] Eval Pipeline — LLM 평가 정확도 검증
- [x] RAG 하이브리드 검색 — bge-m3 + BM25
- [x] Reranker — LLM 기반 Top-10 → Top-3 재정렬
- [x] 멀티턴 대화형 평가 — interactive CLI + /v1/chat
- [x] 기업 밸류에이션 — Scorecard/Berkus/Revenue Multiple
- [x] 형태소 분석 — kiwipiepy 한국어 토크나이저
- [ ] 마케팅 ROI 예측 (marketing-roi)

## 🤝 About

[주식회사 여명거리](https://dawn.kim) | **0→1 AI Agent for Korean Startups**

TIPS Selected 2025 · 정주영 창업경진대회 대상 · 500+ Startups Served · 520x Efficiency

**v2026.2.21** — Reranker + 멀티턴 대화형 평가 + 기업 밸류에이션 + kiwipiepy 형태소 분석 · 90 tests passing

---

<p align="center">
  <b>From ideation to exit, AI infrastructure for every stage.</b><br>
  <a href="https://k-startup.ai">k-startup.ai</a> · <a href="https://ir.dawn.kim">IR</a> · <a href="mailto:iam@dawn.kim">Contact</a>
</p>
