---
name: ku-portal
description: 고려대학교 KUPID 포털 조회. 공지사항, 학사일정, 장학공지, 도서관 좌석, 시간표, 수강과목, LMS 연동. (SonAIengine/ku-portal-mcp 기반)
metadata:
  openclaw:
    min: "2026.2.0"
---

# KU Portal - 고려대학교 KUPID 포털 스킬

고려대학교 KUPID 포털, 도서관, LMS 정보를 조회하는 OpenClaw 스킬.

## 사용법

모든 명령은 venv 활성화 후 실행:
```bash
source ~/.openclaw/workspace/skills/ku-portal/.venv/bin/activate
python3 ~/.openclaw/workspace/skills/ku-portal/ku_query.py <command> [options]
```

## 명령어

### 로그인 불필요
- `library` — 전체 도서관 좌석 현황
- `library --name 중앙도서관` — 특정 도서관 좌석

### 로그인 필요 (KUPID SSO)
자격 증명: `~/.config/ku-portal/credentials.json`
```json
{"id": "your-kupid-id", "pw": "your-kupid-password"}
```

- `notices [--limit 10]` — 공지사항 목록
- `notices --detail <message_id>` — 공지사항 상세
- `schedules [--limit 10]` — 학사일정
- `scholarships [--limit 10]` — 장학공지
- `search <keyword>` — 공지/일정/장학 통합 검색
- `timetable [--day 월]` — 시간표 (요일 지정 가능)
- `timetable --ics` — ICS 파일 생성
- `courses --college 정보대학 --dept 컴퓨터학과` — 개설과목 검색
- `syllabus <course_id>` — 강의계획서
- `mycourses` — 내 수강신청 내역

### LMS (Canvas)
- `lms courses` — LMS 수강과목
- `lms assignments <course_id>` — 과제 목록
- `lms modules <course_id>` — 강의자료
- `lms todo` — 할 일 목록
- `lms dashboard` — 대시보드
- `lms grades <course_id>` — 성적
- `lms submissions <course_id>` — 과제 제출 현황
- `lms quizzes <course_id>` — 퀴즈 목록

## 출처
- 원본: https://github.com/SonAIengine/ku-portal-mcp
- 포크: https://github.com/garibong-labs/ku-portal-mcp
