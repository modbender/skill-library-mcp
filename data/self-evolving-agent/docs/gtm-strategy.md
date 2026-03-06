# Self-Evolving Agent — GTM 전략

> 작성일: 2026-02-17  
> 역할: 시장 전략가 / GTM 전문가  
> 목적: ClawHub 성공 진입을 위한 구체적 실행 계획

---

## 0. 시장 상황 요약 (의사결정 전제)

### 핵심 데이터 (2026-02 기준)

| 지표 | 수치 | 출처 |
|---|---|---|
| ClawHub 총 스킬 | 3,286개 (악성 제거 후) | claw-hub.net |
| 총 다운로드 | 1.5M+ | claw-hub.net |
| 1위 Capability Evolver | 35,581 다운로드 | claw-hub.net |
| self-improving-agent | 15,962 다운로드 / 132 ⭐ | claw-hub.net |
| 운영 인스턴스 | 18,000+ 공개 노출 | Reddit 조사 |

### 2월 보안 사태 — 우리에게 기회

2026년 2월, ClawHub는 대규모 보안 사태를 겪었다:
- 341개 악성 스킬 데이터 탈취 적발
- 2,419개 의심 스킬 일괄 삭제 (5,705 → 3,286)
- VirusTotal 파트너십으로 자동 스캔 도입

**의미:** 사용자들이 지금 신뢰할 수 있는 스킬을 찾고 있다. "투명한 승인 루프"를 앞세우는 우리 포지셔닝이 타이밍상 완벽하다.

### 최대 경쟁자 현황

- **Capability Evolver (1위, 35K+ 다운로드)**: autogame-17 계정 정지됨. 스킬 검색 안 됨. 사실상 공석.
- **self-improving-agent (pskoett)**: 15,962 다운로드, v1.0.5, 지속 관리 중. 가장 강한 경쟁자.

---

## 1. GTM 전략

### 1-1. 타이밍 — 언제 올릴까?

**권장 시점: 지금부터 2주 내 (2026-03-03 이전)**

근거:
1. **보안 사태 후 공백기**: 사용자들이 안전한 대안을 찾는 중 (신뢰 수요 최고조)
2. **Capability Evolver 공석**: 1위 경쟁자가 계정 정지. 자기진화 카테고리 1위 자리가 비어있음
3. **HN 흥행 모멘텀**: OpenClaw 관련 HN 쓰레드가 지금도 활발 ("OpenClaw is changing my life" — 15시간 전)
4. **v2.0 준비 완료**: 코드, SKILL.md, README.md, 문서가 이미 있음

**론칭 데이는 화요일 오전 (서울 기준 화요일 밤 11시 ~ 수요일 오전 2시)**  
→ HN 투표는 미국 서부 시간대 오전에 최고. 화요일이 가장 활성도 높음.

---

### 1-2. 어디에 올릴까 — 채널별 전략

#### 🏆 1순위: ClawHub (핵심)
- 즉시 등록. 메타데이터 최적화가 전부.
- `tags`: `[self-improvement, automation, cron, analytics, agents, meta, safety]`
- 첫 버전은 **v2.0.0** (v1이 아닌 이유: 이미 v2.0 코드가 완성됨. 처음부터 성숙한 이미지)
- README에 "ClawHavoc 대응 설계" 언급 → 보안 의식 있는 스킬임을 어필

#### 🐙 2순위: GitHub (openclaw/skills PR)
- `openclaw/skills` 레포에 PR 제출
- 좋은 PR = 좋은 첫인상. 커밋 메시지 공들이기.
- `awesome-openclaw-skills` 레포에도 따로 PR

#### 🟠 3순위: Reddit
- **r/OpenClaw** (가장 직접적)
- **r/LocalLLaMA** (오픈소스 AI 커뮤니티, 자기진화 = 흥미 포인트)
- **타이밍**: ClawHub 등록 후 24시간 내
- **제목 예시**: `"I built a skill that analyzes your OpenClaw chat logs and auto-improves AGENTS.md — with approval loop"`
- 한국어 커뮤니티: r/Korea AI 그룹, OpenClaw 카톡/디스코드

#### 🟡 4순위: HackerNews
- Show HN 형식: `Show HN: Self-Evolving Agent – cron-based chat log analyzer that proposes AGENTS.md edits`
- HN은 타이밍과 초기 댓글 품질이 전부. 처음 2시간이 결정.
- 설명에 "단순 크론+프롬프트가 아닌 이유" 선제적으로 언급 (비판 차단)

#### 🐦 5순위: Twitter/X
- OpenClaw 커뮤니티 계정 태그
- 스크린샷: 실제 제안이 올라온 Discord 화면 (비포/애프터)
- 개발자 감성: "내 AI가 스스로 학습하게 만들었는데, 보안 사태 이후 설계를 완전히 바꿨다"

---

### 1-3. 론칭 시퀀스 (D-Day 기준)

```
D-7  (화) ─ README.md 영어화 완성 + ClawHub 메타데이터 최종 확인
D-5  (목) ─ GitHub PR 제출 (openclaw/skills)
D-3  (토) ─ awesome-openclaw-skills PR 제출
D-1  (월) ─ 한국어 커뮤니티 사전 공유 (친한 개발자들한테 먼저)
D+0  (화) ─ ClawHub 공식 등록 (밤 11시 KST = HN 골든타임)
D+1  (수) ─ Reddit r/OpenClaw 포스트
D+2  (목) ─ HackerNews Show HN
D+3  (금) ─ Twitter/X 스레드 (스크린샷 포함)
D+7  (다) ─ 1주 성과 리뷰 + Reddit r/LocalLLaMA 2차 포스트
```

---

### 1-4. 첫 주 목표 KPI

| 지표 | 최소 목표 | 현실적 목표 | 대박 시나리오 |
|---|---|---|---|
| ClawHub 다운로드 | 50+ | 200+ | 500+ |
| ClawHub ⭐ | 10+ | 40+ | 100+ |
| GitHub PR 병합 | 1개 | 1개 | 1개 |
| Reddit 업보트 | 20+ | 80+ | 200+ |
| HN 포인트 | 10+ | 40+ | 100+ |
| GitHub Discussions 댓글 | 3+ | 10+ | 30+ |

**참조 기준**: self-improving-agent가 약 6주에 15,962 다운로드 달성.  
우리는 후발주자이므로 1주 200 다운로드는 현실적이다.  
단, Capability Evolver 공석 + 보안 타이밍 결합 시 500도 가능.

---

## 2. 포지셔닝 매트릭스

### 2-1. 경쟁 지형도

| 스킬 | 핵심 방식 | 자동화 수준 | 투명성 | 상태 |
|---|---|---|---|---|
| **self-improving-agent** | 에러/수정 이벤트 훅 | 반자동 (트리거 기반) | 낮음 (파일 저장) | ✅ 활성 |
| **Capability Evolver** | 런타임 히스토리 분석, 코드 자동 생성 | 완전 자동 | 없음 | 🚫 계정 정지 |
| **self-evolving-skill** (whtoo) | 예측 코딩 + 가치 기반 메커니즘 | 자동 | 불명 | ⚠️ 소규모 |
| **self-reflection** (hopyky) | 구조화된 회고 + 메모리 | 수동 반성 | 낮음 | ⚠️ 소규모 |
| **🎯 self-evolving-agent** | 크론 분석 + 외부 벤치마킹 + 승인 루프 | 자동 분석 / 수동 승인 | **높음 (핵심)** | ✅ 신규 |

### 2-2. 포지셔닝 한 줄 (각 경쟁자 대비)

- vs. self-improving-agent: *"그건 에러가 나야만 배우지만, 우리는 아무 일이 없어도 주기적으로 돌아봅니다"*
- vs. Capability Evolver: *"그건 자동이라 무섭지만, 우리는 사람이 승인해야 바뀝니다"*
- vs. self-evolving-skill: *"그건 이론적이지만, 우리는 실제 채팅 로그에서 패턴을 찾습니다"*
- **전체 포지셔닝 한 줄**: **"AI가 스스로 배우되, 인간이 허락해야 적용된다"**

### 2-3. 현실적 달성 가능 목표

```
3개월 후 목표:
- ClawHub 다운로드: 2,000~5,000
- ClawHub ⭐: 80~150
- GitHub 레포 ⭐: 100~300

6개월 후 목표:
- ClawHub 다운로드: 8,000~15,000 (self-improving-agent 수준 도달)
- ClawHub ⭐: 200~400
- 기여자: 3~10명
```

---

## 3. 리스크 완화 전략

### 3-1. "그냥 크론+프롬프트 아니야?" 비판 대응

**예상 댓글**: *"cron으로 claude 돌려서 grep하는 거잖아? 이게 왜 스킬이야?"*

**대응 전략 — 선제적으로 인정하고 역공**:

```
README / HN 게시물에 직접 포함:
"Yes, technically this is a cron job calling Claude to analyze logs.
But 'technically a cron+prompt' is also what most production ML pipelines
reduce to once you strip away the abstractions.

The value is in what it DOESN'T do:
- It doesn't autonomously rewrite your config (approval loop required)
- It doesn't trigger on errors only (scheduled review, not reactive)
- It doesn't hallucinate benchmarks (real external data via search)

Think of it as 'scheduled self-audit' not 'magic AI self-improvement'.
We think the honest framing is more valuable than the magic framing."
```

이 접근의 장점:
- 솔직함 = 신뢰 (보안 사태 직후 커뮤니티가 원하는 것)
- 비판자가 할 말을 먼저 해버리면 비판의 힘이 반감됨
- "조용히 실행되는 AI"보다 "설명할 수 있는 AI"를 원하는 사용자층 확보

### 3-2. 제안 품질이 낮을 경우 Plan B

**문제**: grep 기반 분석의 한계 → 뻔하거나 잘못된 제안 생성 가능성

**Plan B 옵션들**:

| 대안 | 실행 방법 | 난이도 |
|---|---|---|
| **웜업 모드 추가** | 첫 3회 제안은 "연습 제안"으로 표시, 사용자 교육 | 낮음 |
| **제안 퀄리티 점수화** | 제안 생성 시 Claude가 자체 신뢰도 (1~10) 함께 출력 | 낮음 |
| **분석 깊이 선택** | config.yaml에 `analysis_depth: shallow/deep` 옵션 추가 | 중간 |
| **사용자 피드백 학습** | 거부된 제안 패턴 분석해서 다음 제안 개선 | 높음 |
| **멀티모달 분석** | grep → AST 파싱 → 의미론적 유사도 비교로 업그레이드 | 높음 |

**즉시 실행 가능한 Plan B**: 출시 전 `quality-gate.sh` 추가.  
제안 생성 후 Claude가 "이 제안이 실제로 유용한가?" 자기검토하고,  
신뢰도가 낮으면 제안을 스킵하거나 낮은 우선순위 표시.

### 3-3. self-improving-agent 작자(pskoett)와의 관계

**현실**: pskoett의 스킬이 가장 성숙하고 지속 관리 중임.  
경쟁 대신 공생 가능성 검토.

**공생 시나리오**:

```
시나리오 A — 보완 포지셔닝 (추천)
─────────────────────────────────
self-improving-agent: 실시간 이벤트 기반 학습 (에러 발생 시)
self-evolving-agent:  주기적 소급 분석 (크론 기반)

→ 두 스킬이 함께 설치되면 더 강력. README에 명시:
"pair with self-improving-agent for real-time learning"
→ pskoett에게 DM: "저희 스킬이 보완적입니다. 서로 recommend 어떤가요?"
```

```
시나리오 B — 공식 협업
────────────────────────
self-improving-agent의 `.learnings/` 데이터를 self-evolving-agent가 분석에 활용.
데이터 파이프라인 통합으로 더 정확한 분석 가능.
→ 구현 복잡도 높음. v3.0 목표.
```

```
시나리오 C — Fork (비추천)
──────────────────────────
이미 차별점이 있는데 fork하면 희석됨.
그냥 공생이 낫다.
```

**행동 계획**: 출시 당일, pskoett에게 정중한 메시지 전송.  
경쟁이 아닌 생태계 기여자로 관계 설정.

---

## 4. 커뮤니티 빌딩

### 4-1. GitHub Discussions 활용

**즉시 생성할 Discussion 카테고리**:

| 카테고리 | 목적 | 첫 포스트 |
|---|---|---|
| 📋 Proposals Showcase | 실제 생성된 제안 공유 | "이번 주 내 에이전트가 만든 제안들" |
| 🐛 Bug Reports | 품질 낮은 제안 신고 | 템플릿 제공 |
| 💡 Feature Requests | 기능 요청 | 로드맵 투표 |
| 🏆 Community Wins | 자기진화 성공 사례 | "이 스킬 덕에 반복 수정이 줄었어요" |
| ❓ Q&A | 설치/사용 질문 | FAQ 선작성 |

**Discussions 활성화 전략**:
- 출시 1주 내에 제작자(나)가 **직접 모든 댓글에 답변**
- "이번 주 베스트 제안" 주간 하이라이트 포스트
- 좋은 제안을 공유한 사용자 README Credits에 추가

### 4-2. 사용자 피드백 루프

```
사용자가 제안 수락/거부
        ↓
rejected-proposals.json에 이유 기록 (현재 구현됨)
        ↓
주간 크론: "지난주 거부율 X%, 가장 자주 거부된 패턴: Y"
        ↓
제작자에게 주간 리포트 → 분석 로직 개선
        ↓
다음 버전에서 반영
```

**구현할 것들**:
- [ ] 제안 수락/거부 시 1줄 이유 입력 (optional)
- [ ] 주간 메타 리포트 크론 추가
- [ ] 사용자별 제안 품질 추적 대시보드

### 4-3. 기여자 유치 전략

**현실적 목표**: 첫 달에 3~5명 외부 기여자 확보

**전략**:

1. **Good First Issues 선작성** (출시 전)
   - "일본어 지원 추가" (i18n)
   - "Claude Code 지원" (OpenClaw 외 플랫폼)
   - "proposal 퀄리티 점수 추가"

2. **Hacktoberfest 스타일 라벨링**
   - `beginner-friendly`, `help-wanted` 라벨 적극 사용

3. **기여자 인센티브**
   - README Contributors 섹션
   - PR 병합 시 "thank you" 코멘트 with emoji

4. **기술 블로그 연계**
   - "이 스킬의 grep 분석 방식을 NLP로 바꿔볼까요?" 식의 개선 글 작성
   - 기여하고 싶은 개발자를 자연스럽게 끌어들임

---

## 5. 수익화 가능성 — 솔직한 평가

### 5-1. 이걸로 돈 벌 수 있나?

**단기 (6개월): 직접 수익 — NO**

ClawHub는 현재 무료 마켓플레이스다. 다운로드로 수익이 발생하지 않는다.  
self-improving-agent의 pskoett도 수익화하지 않고 있다.

**중기 (1~2년): 간접 수익 가능성 — MAYBE**

| 수익 경로 | 가능성 | 선제 조건 |
|---|---|---|
| 컨설팅/강의 | 중간 | OpenClaw 전문가 포지션 확립 |
| 스폰서십 | 낮음 | GitHub ⭐ 1,000+ 이상 필요 |
| SaaS 파생 | 낮음~중간 | "Hosted self-evolving" 서비스화 |
| 취업/이직 레버리지 | **높음** | 바로 활용 가능 |

**직접 수익화의 현실적 장벽**:
- OpenClaw 생태계 자체가 "무료 + 오픈소스" 정체성
- 유료 스킬 = 커뮤니티 반발 위험
- 경쟁 스킬이 모두 무료인 상황에서 유료화하면 다운로드 0

### 5-2. 그럼 뭘 위해 하나? — 현실적 가치 평가

**포트폴리오/평판 목적: 명확하게 YES, 그리고 이게 더 가치 있다**

```
시나리오 분석:

"self-evolving-agent, ClawHub ⭐100, 5K 다운로드"
        ↓
LinkedIn 프로필: "OpenClaw 생태계 기여자, 자기진화 AI 시스템 설계"
        ↓
AI 에이전트 관련 포지션 인터뷰에서 즉시 화제
        ↓
현실적 기대: 연봉 협상 레버리지 500만원~2000만원 상승 가능성
```

**더 구체적 가치**:
- AI 에이전트 아키텍처 이해를 **코드로 증명**한 공개 레퍼런스
- "이런 거 만들어봤어요" = 10페이지 이력서보다 설득력 있음
- OpenClaw 커뮤니티 내 신뢰도 → 협업 기회 (더 큰 프로젝트 참여)

### 5-3. 현실적 기대값 요약

```
☑ 확실한 것:
  - 포트폴리오 가치 ← 바로 시작됨
  - 기술 학습 (배포, 커뮤니티 관리, GTM)
  - ClawHub 생태계 평판

☐ 가능한 것 (조건부):
  - 커뮤니티 통한 협업/채용 기회
  - OpenClaw 관련 컨설팅 의뢰
  - 미래 유료 도구의 마케팅 채널

✗ 현실적으로 어려운 것:
  - 스킬 자체로 직접 수익
  - 단기 스폰서십
  - 대규모 기여자 생태계 (초기에)
```

---

## 6. 종합 실행 우선순위

### 이번 주 해야 할 것 (High Impact, Low Effort)

1. **README.md 영어화** — ClawHub 노출의 핵심. 영어 사용자가 90%+
2. **"비판 선제 대응" 섹션 README에 추가** — "솔직한 스킬"이라는 브랜드 시작
3. **Good First Issues 3개 선작성** — 기여자 유치 준비
4. **pskoett에게 친선 DM 초안 작성** — 경쟁 대신 공생

### 다음 달 할 것 (Medium Impact, Medium Effort)

5. quality-gate.sh 구현 (제안 자기검토)
6. GitHub Discussions 카테고리 설정
7. 주간 메타 리포트 크론 추가
8. 영어 HN/Reddit 커뮤니티 포스트

### 3개월 후 (High Impact, High Effort)

9. self-improving-agent `.learnings/` 데이터 통합 (v3.0 기능)
10. Claude Code / 다른 플랫폼 지원 확장
11. "Proposal Quality" 공개 대시보드

---

## 부록: Reddit 포스트 초안 (영어)

> **r/OpenClaw 용**

**제목**: I built a skill that reads your chat logs every week and proposes edits to AGENTS.md — with a required human approval step

**본문 핵심 포인트**:
- 보안 사태 이후 "자율 실행"보다 "승인 루프" 설계를 선택한 이유
- 실제 제안 예시 스크린샷 첨부
- "Yes, it's basically a cron job — here's why that's actually fine" 선제 인정
- pskoett의 self-improving-agent와 함께 쓰는 방법

---

*작성: self-evolving-agent GTM 전략 서브에이전트*  
*데이터 기준: 2026-02-17, ClawHub 공개 지표 기반*
