# mufi-calendar

Google Calendar + 네이버 캘린더 통합 관리 스킬. 한국 SMB 고객용.

## 기능

- ✅ Google Calendar API 연동 (조회/추가/수정/삭제)
- ✅ 한국어 자연어 파싱 ("내일 3시 미팅" → 이벤트 생성)
- ✅ 일정 리마인더 (cron 연동)
- 🚧 네이버 캘린더 연동 (브라우저 자동화 or iCal 구독 방식)

## 설치

```bash
cd /Users/mupeng/.openclaw/workspace/skills/mufi-calendar
npm install
```

## 초기 설정

### 1. Google Cloud Console에서 OAuth 2.0 클라이언트 ID 생성

1. https://console.cloud.google.com/apis/credentials 접속
2. "사용자 인증 정보 만들기" → "OAuth 2.0 클라이언트 ID"
3. 애플리케이션 유형: "데스크톱 앱"
4. JSON 다운로드 → `~/.secrets/google-calendar-credentials.json`에 저장

### 2. Google Calendar API 활성화

1. https://console.cloud.google.com/apis/library/calendar-json.googleapis.com
2. "사용" 버튼 클릭

### 3. 초기 인증

```bash
npm run auth
```

브라우저가 열리고 Google 계정 인증 → `~/.secrets/google-calendar-token.json` 생성

## 사용법

상세한 사용법은 `SKILL.md` 참고.

### 일정 조회

```bash
npm run list
npm run list -- --date tomorrow
npm run list -- --days 7 --json
```

### 일정 추가

```bash
# 한국어 자연어
npm run add -- "내일 오후 3시 미팅"
npm run add -- "2026-02-20 10:00 개발팀 회의"

# 명시적 파라미터
npm run add -- --title "회의" --start "2026-02-20T10:00:00+09:00" --end "2026-02-20T11:00:00+09:00"
```

### 일정 수정

```bash
npm run update -- EVENT_ID --title "새 제목"
```

### 일정 삭제

```bash
npm run delete -- EVENT_ID
```

### 리마인더 (cron용)

```bash
npm run remind
npm run remind -- --channel 1468204132920725535  # Discord 전송
```

## 한국어 자연어 파싱

`scripts/lib/parse-korean.js`가 다음 패턴 인식:

- **날짜**: 오늘, 내일, 모레, 다음주 월요일, 2월 20일, 2026-02-20
- **시간**: 오전 9시, 오후 3시, 15:00, 3시 30분
- **기간**: 1시간, 30분 (종료 시간 자동 계산)

예시:
```
"내일 오후 3시 미팅" → 2026-02-18 15:00 ~ 16:00
"2월 20일 10시 개발팀 회의 2시간" → 2026-02-20 10:00 ~ 12:00
```

## 아키텍처

```
skills/mufi-calendar/
├── SKILL.md              # OpenClaw 스킬 정의
├── README.md             # 개발자 문서
├── package.json          # Node.js 의존성
├── scripts/
│   ├── auth.js           # OAuth 인증
│   ├── list.js           # 일정 조회
│   ├── add.js            # 일정 추가
│   ├── update.js         # 일정 수정
│   ├── delete.js         # 일정 삭제
│   ├── remind.js         # 리마인더 (cron용)
│   └── lib/
│       ├── gcal.js       # Google Calendar 클라이언트
│       ├── parse-korean.js  # 한국어 자연어 파싱
│       └── date-utils.js    # 날짜 유틸리티
```

## 네이버 캘린더 연동 (TODO)

네이버 캘린더는 공식 API가 없어 두 가지 우회 방식 검토 중:

1. **iCal 구독** (읽기 전용): 네이버 캘린더 → 설정 → iCal 주소 복사 → Google Calendar로 동기화
2. **브라우저 자동화** (읽기/쓰기): OpenClaw browser tool로 네이버 캘린더 조작

## 트러블슈팅

| 문제 | 해결 |
|------|------|
| `Error: ENOENT: no such file or directory` | `~/.secrets/` 디렉토리 생성 + credentials.json 저장 |
| `401 Unauthorized` | `npm run auth` 재인증 |
| 한국어 파싱 실패 | `--start`, `--end` 명시적 지정 |

## 라이선스

MIT

## 작성자

MUFI (형님의 요청으로 제작)
