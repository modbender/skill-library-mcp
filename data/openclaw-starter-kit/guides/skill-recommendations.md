# 추천 스킬 가이드

## 🟢 필수 (바로 설치)

| 스킬 | 용도 | 설치 명령어 |
|------|------|------------|
| Brave Search | 웹 검색 | `openclaw configure --section web` |
| weather | 날씨 조회 | `openclaw skills install weather` |
| summarize | 웹/PDF/영상 요약 | `openclaw skills install summarize` |

## 🟡 추천 (용도에 따라)

| 스킬 | 용도 | 설치 명령어 |
|------|------|------------|
| github | GitHub 이슈/PR 관리 | `openclaw skills install github` |
| youtube-transcript | 유튜브 자막 추출 | `openclaw skills install youtube-transcript` |
| gog | Google 캘린더/메일 | `openclaw skills install gog` |
| notion | Notion 연동 | `openclaw skills install notion` |

## 🔴 고급 (나중에)

| 스킬 | 용도 | 설치 명령어 |
|------|------|------------|
| coding-agent | 코딩 에이전트 실행 | `openclaw skills install coding-agent` |
| supabase | 벡터DB/데이터베이스 | `openclaw skills install supabase` |
| nano-pdf | PDF 편집 | `openclaw skills install nano-pdf` |

## Brave Search API 키 발급 방법
1. https://brave.com/search/api/ 접속
2. "Get Started for Free" 클릭
3. 회원가입 (이메일)
4. Free 플랜 선택 (월 2,000회 무료)
5. API Key 복사
6. 터미널에서: `openclaw configure --section web`
7. API Key 입력

→ 이제 에이전트가 웹 검색 가능!
