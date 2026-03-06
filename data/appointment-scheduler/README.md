# Appointment Scheduler - Setup Guide

고객사용 예약 자동관리 스킬입니다.

## 🚀 Quick Setup

### 1. Install Dependencies

```bash
cd /Users/mupeng/.openclaw/workspace/skills/appointment-scheduler/scripts
npm install
```

### 2. Initialize Configuration

```bash
node init-config.js
```

이 명령은 `~/.openclaw/workspace/config/appointment-scheduler.json` 파일을 생성합니다.
비즈니스에 맞게 설정을 수정하세요:

- 영업시간 (business_hours)
- 서비스 종류 및 소요 시간 (services)
- 리마인더 설정 (reminders)
- 노쇼 정책 (noshow_policy)

### 3. Test Basic Booking

```bash
# 예약 생성
node book.js \
  --date "2026-02-20" \
  --time "15:00" \
  --duration 60 \
  --service "컷" \
  --customer "김철수" \
  --phone "01012345678"

# 일정 확인
node check-schedule.js --date 2026-02-20
```

## 📱 Natural Language Booking

예약 요청을 자연어로 파싱:

```bash
node parse-booking.js --text "내일 오후 3시에 컷 예약 가능할까요? - 김철수 010-1234-5678"
```

출력:
```json
{
  "parsed": {
    "date": "2026-02-20",
    "time": "15:00",
    "service": "컷",
    "customer_name": "김철수",
    "phone": "01012345678"
  }
}
```

## 🔔 Reminder System

### Manual Test

```bash
# 하루 전 리마인더
node send-reminders.js --type day-before

# 2시간 전 리마인더
node send-reminders.js --type hour-before
```

### Cron Setup (자동화)

```bash
# crontab -e 실행 후 추가:

# 매일 오전 9시: 하루 전 리마인더
0 9 * * * cd /Users/mupeng/.openclaw/workspace/skills/appointment-scheduler/scripts && node send-reminders.js --type day-before

# 매 시간: 2시간 전 리마인더
0 * * * * cd /Users/mupeng/.openclaw/workspace/skills/appointment-scheduler/scripts && node send-reminders.js --type hour-before
```

## 📊 No-Show Management

```bash
# 노쇼 기록
node mark-noshow.js --booking-id abc123

# 노쇼 리포트
node noshow-report.js

# 특정 고객 조회
node noshow-report.js --customer "김철수"

# 월별 리포트
node noshow-report.js --month 2026-02

# 반복 노쇼 고객 플래그
node noshow-report.js --flag-repeat
```

## 📋 Waitlist Management

```bash
# 대기 명단 추가
node waitlist.js add \
  --date "2026-02-20" \
  --time "15:00" \
  --customer "이영희" \
  --phone "01099998888"

# 대기 명단 조회
node waitlist.js list --date 2026-02-20

# 취소 시 대기 명단 알림
node waitlist.js notify --booking-id abc123
```

## 🔄 Google Calendar Sync

### Setup

1. **Google Cloud Console에서 Calendar API 활성화**
   - https://console.cloud.google.com/ 접속
   - "Google Calendar API" 검색 및 활성화
   - "OAuth 2.0 클라이언트 ID" 생성
   - 데스크톱 앱으로 설정

2. **Credentials 다운로드**
   - JSON 파일 다운로드
   - `~/.secrets/google-calendar-credentials.json` 에 저장

3. **첫 인증**
   ```bash
   node sync-google-calendar.js
   ```
   - 브라우저에서 Google 계정 인증
   - 토큰이 `~/.secrets/google-calendar-token.json` 에 저장됨

4. **자동 동기화 (cron)**
   ```bash
   # 30분마다 캘린더 동기화
   */30 * * * * cd /Users/mupeng/.openclaw/workspace/skills/appointment-scheduler/scripts && node sync-google-calendar.js
   ```

## 🛠️ Advanced Features

### Block Time Slots

```bash
node block-time.js \
  --date "2026-02-20" \
  --start "12:00" \
  --end "13:00" \
  --reason "점심시간"
```

### Cancel Booking with Waitlist Notification

```bash
node cancel-booking.js --booking-id abc123 --notify-waitlist
```

## 📁 Data Structure

```
~/.openclaw/workspace/
├── config/
│   └── appointment-scheduler.json      # 설정 파일
├── data/appointments/
│   ├── bookings/
│   │   ├── 2026-02-20.json            # 일별 예약 기록
│   │   └── ...
│   ├── waitlist/
│   │   ├── 2026-02-20.json            # 일별 대기 명단
│   │   └── ...
│   ├── noshow/
│   │   ├── history.json               # 노쇼 이력
│   │   └── flagged-customers.json     # 플래그된 고객
│   └── reminders/
│       └── sent.json                  # 리마인더 발송 로그
└── events/
    └── appointment-YYYY-MM-DD.json    # 이벤트 로그
```

## 🎯 Integration with OpenClaw

### Message Tool Integration

리마인더와 대기 명단 알림은 `SEND_REMINDER` / `NOTIFY_WAITLIST` JSON을 출력합니다.
OpenClaw 에이전트가 이를 감지하여 `message` tool로 자동 전송합니다.

### Example Flow

1. **예약 요청 수신** (DM/카톡)
2. **파싱**: `parse-booking.js`
3. **충돌 체크 & 예약**: `book.js`
4. **리마인더 자동 발송**: cron → `send-reminders.js` → message tool
5. **노쇼 기록**: `mark-noshow.js`
6. **대기 명단 관리**: `waitlist.js`

## 🐛 Troubleshooting

### "Config not found" error
```bash
node init-config.js
```

### 파싱 실패
- `chrono-node` 라이브러리 한계 (한국어 날짜 표현 일부 지원)
- 명확한 날짜/시간 형식 사용 권장

### 캘린더 동기화 에러
- OAuth 토큰 만료: `~/.secrets/google-calendar-token.json` 삭제 후 재인증
- API 할당량 초과: Google Cloud Console에서 할당량 확인

## 📚 Documentation

전체 스킬 문서: `SKILL.md`

---

> 🐧 Built by **무펭이** — [무펭이즘(Mupengism)](https://github.com/mupeng) 생태계 스킬
