# Self-Evolving Agent — 마케팅 플랜

> 작성일: 2026-02-17 | 타겟: ClawHub + GitHub + Reddit

---

## 🎯 핵심 메시지

**한 줄 훅:**
> "Your AI assistant reviews its own mistakes weekly and proposes rule improvements — automatically."

**한국어 버전:**
> "AI 비서가 매주 자신의 실수를 분석하고, 규칙 개선안을 자동으로 제안합니다."

**차별점 (USP):**
- self-improving-agent는 세션별 점수 → **self-evolving-agent는 시스템 차원의 영구 규칙 진화**
- 측정 가능한 데이터 기반 (967 세션, 85 패턴, 4 제안)
- 안전 게이트: 절대 AGENTS.md 자동 수정 안 함 → 사람이 승인

---

## 📊 타겟 오디언스

### Primary (1차 타겟)
| 세그먼트 | 특징 | 메시지 포인트 |
|---------|------|-------------|
| OpenClaw 헤비유저 | AGENTS.md 관리에 시간 소비 | "수동 편집 끝. 자동 진화 시작." |
| AI 개발자/리서처 | 에이전트 시스템 구축 관심 | "측정 가능한 self-improvement 루프" |
| Claude 파워유저 | CLAUDE.md 직접 관리 | "같은 실수 반복 루프 탈출" |

### Secondary (2차 타겟)
| 세그먼트 | 특징 | 메시지 포인트 |
|---------|------|-------------|
| r/AI_Agents 커뮤니티 | AI 에이전트 시스템 관심 | 기술적 상세 + 실측 데이터 |
| r/ClaudeAI 커뮤니티 | Claude 활용 팁 공유 | 실용적 워크플로우 개선 |
| GitHub AI 오픈소스 관심자 | 스타 / 포크 잠재 유저 | README → 설치 → 사용 경로 |

---

## 🚀 배포 채널별 전략

### 1. ClawHub (최우선)

**목표:** Featured Skills 진입, 첫 100 installs

**액션 아이템:**
- [ ] `_meta.json` 메타데이터 최적화 (태그, 설명, 카테고리)
- [ ] 데모 GIF 제작: "weekly report가 Discord에 도착하는 장면"
- [ ] Skill thumbnail 이미지 제작 (뇌 🧠 + 그래프 + 화살표)
- [ ] ClawHub 소개 글 작성 (self-improving과 시너지 강조)

**ClawHub 메타 최적화:**
```json
{
  "name": "self-evolving-agent",
  "displayName": "Self-Evolving Agent 🧠",
  "tagline": "Your AI reviews its own mistakes weekly and evolves its own rules.",
  "tags": ["self-improvement", "automation", "agents", "meta", "AGENTS.md", "weekly-review"],
  "category": "AI Agents / Meta"
}
```

---

### 2. GitHub

**목표:** 50+ stars, Reddit/HN 커뮤니티 inbound

**액션 아이템:**
- [ ] 리포지토리 공개 (현재 private이면 public 전환)
- [ ] README.md 영어 버전 완성 ✅ (이미 완료)
- [ ] GitHub Topics 추가: `claude`, `ai-agent`, `self-improvement`, `openclaw`, `automation`
- [ ] GitHub Releases: v1.0.0 태그 + changelog
- [ ] `CONTRIBUTING.md` 작성 (외부 기여자 온보딩)
- [ ] Issues 템플릿 추가 (bug report, feature request)

**바이럴 포인트:**
- Mermaid 아키텍처 다이어그램 (GitHub에서 렌더링)
- 실측 데이터 (967 sessions, 85 patterns) → 신뢰도 확보
- Before/After diff 예시 → 직관적 이해

---

### 3. Reddit

**목표:** r/AI_Agents 500+ upvotes, r/ClaudeAI 300+ upvotes

**포스팅 전략:**
- **타이밍:** 화~목요일 오전 9-11시 (EST) — 피크 트래픽
- **포맷:** 긴 글 (설명 충실) + TL;DR 맨 위
- **초기 댓글:** 스스로 vs self-improving-agent 비교 표 달기
- **교차 포스팅:** r/MachineLearning (메타러닝 각도), r/LocalLLaMA

**제목 후보 5개 (우선순위 순):**
1. "I built a skill that makes my Claude review its own mistakes and rewrite its own rules — here's what 967 sessions revealed"
2. "My AI assistant now proposes its own AGENTS.md improvements weekly. It's caught things I never would have noticed."
3. "Stop manually editing CLAUDE.md. I automated it with a self-evolving loop."
4. "After 3 months: 85 complaint patterns, 4 rule proposals, 3 accepted. My AI is genuinely getting better automatically."
5. "The missing piece in AI agent workflows: automated rule evolution (not just self-scoring)"

**추천 제목:** #1 (구체적 숫자 + 호기심 유발)

---

## 🎨 시각 자료 계획

### 필수 제작 (우선순위 순)

| 자료 | 목적 | 제작 방법 |
|------|------|---------|
| 데모 GIF | ClawHub + README 메인 | OBS 녹화 → 편집 |
| 아키텍처 다이어그램 | GitHub README | Mermaid (이미 작성) |
| Discord 리포트 스크린샷 | 실제 결과 증명 | 스크린샷 가공 |
| Before/After 코드 diff | 제안 형식 시각화 | Carbon.now.sh |
| 대시보드 목업 | v1.2 로드맵 포인트 | Figma 또는 ASCII |

### 데모 GIF 스크립트

```
장면 1: analyze-behavior.sh 실행 (터미널)
장면 2: JSON 결과 출력 → 패턴 감지 숫자들
장면 3: generate-proposal.sh 실행
장면 4: Discord에 리포트 도착 (모바일 뷰)
장면 5: "적용해줘" 입력 → AGENTS.md 업데이트 확인
장면 6: git log --oneline → "자동 커밋" 확인
```

---

## 📅 배포 타임라인

```
Week 1 (2026-02-17~21)
  ✅ README.md 영어 버전 완성
  ✅ 마케팅 문서 일체 작성
  ✅ _meta.json 메타데이터 최적화
  □ GitHub 리포 공개 + Topics 추가
  □ ClawHub 배포

Week 2 (2026-02-24~28)
  □ 데모 GIF 제작
  □ Reddit r/AI_Agents 포스팅
  □ Reddit r/ClaudeAI 포스팅

Week 3 (2026-03-03~07)
  □ 반응 분석 + FAQ 업데이트
  □ r/MachineLearning 교차 포스팅 (반응 좋으면)
  □ 첫 번째 외부 기여 이슈 오픈
```

---

## 💡 바이럴 포인트 분석

### 왜 바이럴될 수 있는가?

1. **공감 가능한 문제** — "같은 실수를 반복하는 AI" 는 모든 Claude 사용자의 공통 불만
2. **측정 가능한 결과** — "85 패턴, 4 제안, 3 승인" → 추상적이지 않고 구체적
3. **안전한 자동화** — "절대 자동 수정 안 함" → AI 불안감 해소
4. **저렴한 실행 비용** — 월 커피 1잔 이하 → 진입 장벽 낮음
5. **시너지 스토리** — self-improving + self-evolving 조합 → "AI 생태계 구축" 내러티브

### 잠재적 바이럴 트리거

- "967 sessions" 숫자 → 장기 사용자가 공유하는 리얼 데이터 신뢰감
- Before/after diff → 스크린샷 공유 가능한 비주얼
- "당신의 AI가 스스로 진화한다" → SF적 상상력 자극

---

## 🔧 v1.0 개선 우선순위 (사용자 피드백 예상)

| 예상 피드백 | 대응 계획 |
|---------|---------|
| "영어 complaint patterns 추가해줘" | i18n 패턴 라이브러리 PR 수용 |
| "Slack 알림도 되나요?" | v1.1 delivery 설정 확장 |
| "분석 기간 커스텀하고 싶어" | env var 문서화 |
| "CLAUDE.md도 지원해?" | 파일 경로 파라미터화 |
| "대시보드 언제 나와?" | v1.2 로드맵 공개 → 기대감 관리 |

---

## 📈 성공 지표 (KPI)

| 지표 | 1개월 목표 | 3개월 목표 |
|------|----------|----------|
| GitHub Stars | 50+ | 200+ |
| ClawHub Installs | 30+ | 100+ |
| Reddit Upvotes (합계) | 500+ | — |
| 외부 기여 PR | 1+ | 5+ |
| ClawHub Featured | — | 1회+ |

---

*마케팅 플랜 작성: 2026-02-17 | 업데이트 주기: 월 1회*
