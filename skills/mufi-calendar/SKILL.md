---
name: mufi-calendar
description: Google Calendar + 네이버 캘린더 통합 관리. 한국어 자연어 일정 파싱, 리마인더 지원.
metadata: {"clawdbot":{"emoji":"📆","requires":{"bins":["node","python3"]},"install":[{"id":"npm","kind":"npm","packages":["@google-cloud/calendar"],"label":"Install Google Calendar Node.js library"}]}}
---

# MUFI Calendar

Google Calendar + 네이버 캘린더 통합 관리 스킬. 한국 SMB 고객용.

## 기능

- ✅ Google Calendar 연동 (조회/추가/수정/삭제)
- ✅ 한국어 자연어 파싱 ("내일 3시 미팅" → 이벤트 생성)
- ✅ 일정 리마인더 (cron 연동)
- 🚧 네이버 캘린더 연동 (브라우저 자동화 or iCal 구독 방식)

## 설정

### 1. Google Calendar API 설정

Google Cloud Console에서 OAuth 2.0 클라이언트 ID 생성:
1. https://console.cloud.google.com/apis/credentials
2. "OAuth 2.0 클라이언트 ID" 생성 → "데스크톱 앱"
3. JSON 다운로드 → `~/.secrets/google-calendar-credentials.json` 저장

### 2. 초기 인증

```bash
node /Users/mupeng/.openclaw/workspace/skills/mufi-calendar/scripts/auth.js
```

브라우저가 열리고 Google 계정 인증 → `~/.secrets/google-calendar-token.json` 생성

### 3. 환경 변수 (선택)

```bash
export GOOGLE_CALENDAR_ID="primary"  # 기본 캘린더 ID (primary = 주 캘린더)
```

## 사용법

### 일정 조회

```bash
# 오늘 일정
node scripts/list.js

# 내일 일정
node scripts/list.js --date tomorrow

# 특정 날짜
node scripts/list.js --date 2026-02-20

# 다음 7일
node scripts/list.js --days 7

# JSON 출력
node scripts/list.js --json
```

### 일정 추가 (자연어)

```bash
# 한국어 자연어 파싱
node scripts/add.js "내일 오후 3시 미팅"
node scripts/add.js "2026-02-20 10:00 개발팀 회의"
node scripts/add.js "다음주 월요일 2시 치과"

# 명시적 파라미터
node scripts/add.js \
  --title "개발팀 회의" \
  --start "2026-02-20T10:00:00+09:00" \
  --end "2026-02-20T11:00:00+09:00" \
  --location "본사 회의실 A" \
  --description "Q1 스프린트 회고"
```

### 일정 수정

```bash
# 이벤트 ID로 수정
node scripts/update.js EVENT_ID \
  --title "새 제목" \
  --start "2026-02-20T15:00:00+09:00"
```

### 일정 삭제

```bash
node scripts/delete.js EVENT_ID
```

### 리마인더 설정

```bash
# cron 등록 (매일 9시 오늘 일정 알림)
crontab -e
# 추가: 0 9 * * * node /Users/mupeng/.openclaw/workspace/skills/mufi-calendar/scripts/remind.js
```

## 한국어 자연어 파싱 규칙

`scripts/parse-korean.js`가 다음 패턴을 인식:

- **날짜**: 오늘, 내일, 모레, 다음주 월요일, 2월 20일, 2026-02-20
- **시간**: 오전 9시, 오후 3시, 15:00, 3시 30분
- **기간**: 1시간, 30분 (종료 시간 자동 계산)

예시:
```
"내일 오후 3시 미팅" 
→ 2026-02-18 15:00 ~ 16:00 (기본 1시간)

"2월 20일 10시 개발팀 회의 2시간"
→ 2026-02-20 10:00 ~ 12:00

"다음주 월요일 2시 치과"
→ 2026-02-24 14:00 ~ 15:00
```

## 네이버 캘린더 연동 (실험적)

네이버 캘린더는 공식 API가 없어 두 가지 방식 지원:

### 방식 1: iCal 구독 (읽기 전용)

1. 네이버 캘린더 → 설정 → iCal 주소 복사
2. `~/.secrets/naver-calendar-ical-url.txt`에 저장
3. `node scripts/sync-naver.js` 실행 → Google Calendar로 복사

### 방식 2: 브라우저 자동화 (읽기/쓰기)

OpenClaw 브라우저로 네이버 캘린더 조작:

```bash
# 일정 추가
node scripts/naver-add.js "2026-02-20 10:00 회의"

# 일정 조회 (snapshot + OCR)
node scripts/naver-list.js
```

**제약**: 로그인 상태 유지 필요, UI 변경 시 스크립트 수정 필요

## 출력 형식

### 텍스트 (기본)

```
📅 2026-02-20 (목)
  10:00-11:00  개발팀 회의
  15:00-16:00  미팅

📅 2026-02-21 (금)
  종일  공휴일
```

### JSON

```json
{
  "events": [
    {
      "id": "abc123",
      "summary": "개발팀 회의",
      "start": "2026-02-20T10:00:00+09:00",
      "end": "2026-02-20T11:00:00+09:00",
      "location": "본사 회의실 A",
      "description": "Q1 스프린트 회고"
    }
  ]
}
```

## Discord 알림

리마인더를 Discord로 전송:

```bash
# 오늘 일정을 형님 DM 채널로
node scripts/remind.js --channel 1468204132920725535
```

`openclaw` CLI의 `message` 스킬과 연동.

## 트러블슈팅

| 문제 | 해결 |
|------|------|
| 401 Unauthorized | `node scripts/auth.js` 재인증 |
| 토큰 만료 | `rm ~/.secrets/google-calendar-token.json` → 재인증 |
| 한국어 파싱 실패 | `--start`, `--end` 명시적 지정 |
| 네이버 로그인 필요 | OpenClaw 브라우저에서 naver.com 로그인 후 재시도 |

## 참고

- Google Calendar API: https://developers.google.com/calendar/api/v3/reference
- 자연어 파싱: `chrono-node` 라이브러리 + 한국어 패턴 추가
- 네이버 캘린더 API 미제공 → 우회 방식만 가능
