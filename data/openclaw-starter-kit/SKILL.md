---
name: openclaw-starter-kit
description: OpenClaw 초보자를 위한 풀패키지 온보딩 스킬. 첫 세팅부터 보안 강화까지 대화형으로 안내한다. "초기 세팅", "처음 설정", "starter kit", "온보딩", "setup guide", "시작하기", "세팅 도와줘" 키워드에 반응.
---

# OpenClaw Starter Kit 🚀

새로운 OpenClaw 유저를 위한 **풀패키지 온보딩 스킬**.
대화형으로 하나씩 안내하며, 모든 핵심 파일을 자동 생성한다.

## 트리거
- "초기 세팅", "처음 설정", "starter kit", "온보딩"
- "setup guide", "시작하기", "세팅 도와줘"
- "보안 설정", "security setup"
- "세팅 리포트", "뭐 설치됐어"

## 실행 흐름

### Phase 1: 기본 세팅 (대화형)

**Step 1 — SOUL.md (에이전트 성격)**
사용자에게 5가지 질문:
1. "에이전트 이름을 뭘로 할까요?"
2. "말투는? (반말/존댓말/캐주얼/전문가)"
3. "주요 역할은? (비서/코딩도우미/학습파트너/만능)"
4. "하면 안 되는 것은? (경계선)"
5. "대표 이모지는?"

→ 답변을 기반으로 `templates/soul-template.md`를 참고하여 `SOUL.md` 생성
→ 사용자 확인 후 저장

**Step 2 — USER.md (사용자 정보)**
수집 항목:
- 이름, 호칭
- 직업/관심사
- 타임존 (기본: Asia/Seoul)
- 특이사항/선호

→ `templates/user-template.md` 참고하여 생성

**Step 3 — 메모리 구조**
자동 생성:
```
~/.openclaw/workspace/
├── MEMORY.md              ← 장기 기억 인덱스
├── memory/
│   ├── YYYY-MM-DD.md      ← 일일 로그 (첫 날 자동 생성)
│   ├── knowledge/          ← 학습 자료
│   ├── projects/           ← 프로젝트 기록
│   └── lessons/            ← 실수/교훈
```
→ `templates/memory-template.md` 기반

**Step 4 — HEARTBEAT.md (자동 체크인)**
용도 설명 후 기본 템플릿 생성:
- 날씨 체크
- 할 일 리마인더
- 사용자 맞춤 항목 추가

→ `templates/heartbeat-template.md` 기반

### Phase 2: 스킬 & 도구 설정

**Step 5 — Brave Search API**
1. https://brave.com/search/api/ 가입 안내 (무료 월 2,000회)
2. API 키 받으면 `openclaw configure --section web` 실행 안내
3. 설정 확인

**Step 6 — 추천 스킬 설치**
용도별 안내 → `guides/skill-recommendations.md` 참고:

| 용도 | 스킬 | 명령어 |
|------|------|--------|
| 웹 검색 | (Brave API) | `openclaw configure --section web` |
| 날씨 | weather | `openclaw skills install weather` |
| 요약 | summarize | `openclaw skills install summarize` |
| GitHub | github | `openclaw skills install github` |
| 유튜브 | youtube-transcript | `openclaw skills install youtube-transcript` |

**Step 7 — 크론잡 기초**
→ `guides/cron-basics.md` 참고
- 하트비트 vs 크론 차이
- 예시: "매일 아침 9시 일정 알려줘"
- 설정 방법 안내

### Phase 3: 보안 강화

**Step 8 — 보안 설정 (필수)**
→ `guides/security-guide.md` 참고

1. **API 키 관리**
   - SOUL.md/USER.md에 절대 키 넣지 않기
   - 환경변수 또는 `openclaw configure`로만 관리
   - `.env` 파일은 `.gitignore`에 추가

2. **외부 행동 제어**
   - 이메일/SNS 발송: 승인 모드 설정
   - `openclaw configure --section security`
   - allowlist로 허용 번호/채널만 허가

3. **파일 안전**
   - `rm` 대신 `trash` 사용 (복구 가능)
   - 민감 정보 별도 관리
   - 에이전트 접근 범위 명시

4. **채널 보안**
   - 텔레그램: allowlist에 본인 번호만
   - 그룹챗: 에이전트 발언 범위 제한
   - 모르는 사람 메시지 차단

5. **네트워크 보안**
   - gateway 토큰 외부 노출 금지
   - 공용 WiFi에서 대시보드 접속 주의
   - 정기적으로 `openclaw health` 실행

6. **데이터 보안**
   - 개인정보 관리 원칙
   - `memory/` 폴더 정기 백업
   - 공유 시 민감정보 마스킹

### Phase 4: 마무리

**Step 9 — 세팅 리포트 생성**
자동으로 현재 상태를 스캔하여 리포트 출력:
```
✅ 세팅 완료 리포트
━━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 설치된 스킬: [자동 감지]
🤖 에이전트: [이름] ([모델])
📡 채널: [연결된 채널]
🔍 웹 검색: [활성/비활성]
📂 워크스페이스: [경로]
📝 SOUL.md: [✅/❌]
👤 USER.md: [✅/❌]
🧠 MEMORY.md: [✅/❌]
💓 HEARTBEAT.md: [✅/❌]
🔒 보안: [allowlist 설정 여부]
⏰ 크론잡: [설정 수]

세팅 담당: [설정자 이름]
세팅 일자: [오늘 날짜]
━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Step 10 — 고급 로드맵 안내**
→ `guides/advanced-roadmap.md` 참고
- 멀티채널 연결
- 서브에이전트 활용
- 벡터DB (RAG) 구축
- 커스텀 스킬 제작

### 트러블슈팅
→ `guides/troubleshooting.md` 참고
- "gateway가 안 켜져요" → `openclaw doctor` 실행
- "봇이 응답 안 해요" → 토큰 확인 + allowlist 체크
- "스킬 설치 오류" → Node.js 버전 확인

## 파일 구조
```
openclaw-starter-kit/
├── SKILL.md
├── templates/
│   ├── soul-template.md
│   ├── user-template.md
│   ├── memory-template.md
│   ├── heartbeat-template.md
│   └── agents-template.md
├── guides/
│   ├── skill-recommendations.md
│   ├── cron-basics.md
│   ├── security-guide.md
│   ├── advanced-roadmap.md
│   └── troubleshooting.md
└── package.json
```
