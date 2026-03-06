# Changelog

## v0.7.6 (2026-02-18)
### New Features — 소상공인 Track B + 금융맵 + 카카오톡 연동

- **`scripts/track_classifier.py`**: 트랙 자동 감지 모듈
  - `TrackClassifier.classify()`: 키워드 매칭 우선 → LLM 분류 폴백
  - Track A (기술창업/벤처), Track B (소상공인/로컬), Track AB (혼합)
  - `TRACK_B_KEYWORDS` / `TRACK_A_KEYWORDS` / `TRACK_AB_KEYWORDS` 키워드 사전
  - `get_track_prompt()`: 트랙별 평가 시스템 프롬프트 반환
  - `TRACK_B_SYSTEM_PROMPT`: 소상공인 전용 (5항목, 쉬운 언어, 기술성 기준 제외)

- **`scripts/financial_map.py`**: 융자/보증/크라우드펀딩 정보 제공
  - `FINANCIAL_PRODUCTS`: 6종 금융 상품 (KODIT, KIBO, 소진공, Wadiz, TIPS 등)
  - `FinancialMap.match()`: 트랙 + 키워드 + need_loan 기반 상품 매칭
  - `FinancialMap.format_recommendation()`: LLM 맞춤형 추천 텍스트 생성
  - `FinancialMap.get_summary()`: 트랙별 금융 지원 요약

- **`scripts/crawlers/semas_crawler.py`**: 소진공 지원사업 크롤러
  - robots.txt 확인 후 1.5초 딜레이 적용
  - 공고 목록 → 상세 페이지 파싱 → eval_data/semas_programs.jsonl APPEND

- **`scripts/crawlers/financial_crawler.py`**: KODIT/KIBO URL 유효성 체크 크롤러
  - FINANCIAL_PRODUCTS 전체 URL HEAD 요청으로 상태 확인
  - 금리 변동 감지 + eval_data/financial_products_updated.json 저장

- **`scripts/kakao_webhook.py`**: 카카오 i 오픈빌더 웹훅 서버 (핵심!)
  - `KakaoWebhook.process()`: utterance → 트랙 감지 → RAG/LLM → 카카오 응답
  - `KakaoWebhook.format_response()`: 900자 분할, 최대 5개 outputs
  - `KakaoWebhook.verify_signature()`: HMAC-SHA1 서명 검증
  - `KakaoWebhook.get_quick_buttons()`: 트랙별 빠른 응답 버튼
  - user_id 기반 세션 관리 (최대 20턴)

- **`scripts/server.py`**: `/kakao` POST 엔드포인트 추가
  - `RaonHandler._handle_kakao()`: 카카오 웹훅 처리
  - AgenticRAG 연동 (store 있을 때), LLM 폴백
  - 에러 발생 시에도 카카오 200 응답 보장

- **`scripts/evaluate.py`**: Track B 분기 추가
  - `evaluate()`: 트랙 자동 감지 → Track B/A 분기
  - `evaluate_track_b()`: 소상공인 전용 5항목 평가
  - `evaluate_track_a()`: 기존 TIPS 기준 평가 (하위 호환)
  - `TRACK_B_EVAL_PROMPT`: 쉬운 언어, 기술성 기준 제외

- **`KAKAO_SETUP.md`**: 카카오 i 오픈빌더 연동 3단계 가이드

### Tests
- `test_kakao.py`: 39개 테스트 (37 passed, 2 LLM-required skipped)
  - TrackClassifier: 10개 (키워드/LLM 분류, 치킨→B, AI SaaS→A, 푸드테크→AB)
  - FinancialMap: 8개 (트랙별 필터링, 추천 포맷)
  - KakaoWebhook.format_response: 6개 (1000자 분할, 버튼, outputs 제한)
  - KakaoWebhook.verify_signature: 4개 (HMAC 검증)
  - KakaoWebhook.process: 7개 (웹훅 처리, 세션, 버튼)
  - evaluate.py: 3개 (Track B 프롬프트, 함수 존재 확인)

---

## v0.7.5 (2026-02-18)
### New Features — Agentic RAG (Phase 1+2)
- **`agentic_rag.py`**: Agentic RAG 오케스트레이션 레이어
  - `QueryRouter`: LLM 기반 질문 유형 분류 (factual/search/realtime/multistep), heuristic 폴백
  - `HyDE`: Hypothetical Document Embeddings — 가상 문서로 실제 문서 검색 (미스매치 해결)
  - `Multi-Query RAG Fusion`: 3가지 변형 쿼리 + Reciprocal Rank Fusion (RRF)
  - `Speculative RAG`: 초안 답변 → 검증 쿼리 → 실제 문서 검색
  - `Recursive RAG (ReFRAG)`: CRAG Critic 미달 시 쿼리 리파인 후 재검색 (최대 3회)
  - `CRAG Critic`: LLM 기반 검색 결과 품질 평가 (relevant/sufficient/confident)
  - `Tools`: search_gov_programs (structured filter), check_eligibility, fetch_realtime (urllib)
  - `AgenticRAG.run()`: 전략별 검색 → CRAG 평가 → 재시도 → 최종 답변
- **`structured_extractor.py`**: 정부공고 JSON 스키마 추출기
  - `GOV_PROGRAM_SCHEMA`: program_name, operator, eligibility, excluded, budget_won, deadline, ...
  - `extract_program_schema()`: LLM 추출 + 규칙 기반 폴백
  - `filter_programs()`: 하드 필터 (deadline, excluded) + 소프트 랭킹 (industry, keywords)
- **`server.py`**: `/v1/chat` 엔드포인트에 AgenticRAG 연동
  - AgenticRAG import 실패 시 기존 Ollama 폴백 (try/except)
  - 응답에 `strategy` 필드 추가 (factual/search/realtime/multistep)

### Tests
- `test_agentic_rag.py`: 20개 테스트 (20 passed)
- 전체: 143 passed (기존 3개 test_rerank.py 실패는 pre-existing)

---

## v0.7.0 (2026-02-18)
### New Features
- **Data Collection Pipeline**: Multi-source crawler system
  - JointTIPS crawler — 3,972 TIPS-selected startups (2015~2024)
  - TheVC crawler — VC/accelerator profiles (Nuxt HTML parsing)
  - NextUnicorn crawler — Support programs via open API
  - DDG-based InnoForest data collection
  - `scripts/data_to_content.py` — Auto-generates SNS content from collected data
- **RAG Expansion**: 532 chunks across 7 data sources (7.2MB vector store)
  - New sources: thevc_investors, nextunicorn_programs, tips_companies_jointips

### Bug Fixes
- **Python 3.9 compatibility**: `from __future__ import annotations` in rag_pipeline.py
- **Gemini API endpoint**: Fixed 404 by using `gemini-2.5-flash-lite` model name

### Improvements
- **Cron timeouts**: All SNS upload crons bumped 300s→600s (prevents false timeouts)
- **Content pipeline**: `data-to-content-daily` cron at 08:00 KST

---

## v0.6.2 (2026-02-18)
### New Features
- Full-page web app (`raon-chat.html`) — dark mode, glassmorphism, 6 modes
- YC RFS idea recommendation — 62 ideas, CLI + API
- API key authentication (BYOK free + Managed paid)
- `data_to_content.py` initial version

### Bug Fixes
- `history.jsonl` not written by `/v1/evaluate` API endpoint — fixed
- FakeHandler missing `client_address`/`headers` in tests — fixed
- Score mismatch: `fix_score_text()` clamps sub-items, recalculates totals

### Tests
- 126 tests passing

---

## v0.6.1 (2026-02-17)
### New Features
- Gamification system (XP, levels, badges)
- DM auto-reply integration (Ollama + Gemini fallback)
- Ollama timeout 120s→300s

### Bug Fixes
- Cron state path fix (`~/.openclaw/cron/jobs.json`)
- XP sync: first sync grants XP for past successful runs

---

## v0.6.0 (2026-02-16)
### New Features
- RAG pipeline v2: bge-m3 + BM25 hybrid search (Top-1 accuracy 0%→100%)
- Reranker module (LLM-based Top-10→Top-3)
- Eval ground truth: 50 entries, F1 + confusion matrix
- Multi-turn conversational evaluation
- Valuation module (Scorecard/Berkus/Revenue Multiple)
- Morpheme analysis (kiwipiepy + bigram fallback)
