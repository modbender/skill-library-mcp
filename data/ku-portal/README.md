# KU Portal — 고려대학교 KUPID 포털 스킬

고려대학교 KUPID 포털, 도서관, Canvas LMS 정보를 OpenClaw에서 조회하는 스킬.

> 원본: [SonAIengine/ku-portal-mcp](https://github.com/SonAIengine/ku-portal-mcp)를 OpenClaw 스킬로 래핑.

## 기능

| 기능 | 로그인 | 설명 |
|------|--------|------|
| 도서관 좌석 | 불필요 | 6개 도서관 53개 열람실 실시간 좌석 현황 |
| 공지사항 | SSO | 목록 조회 + 상세 + 키워드 검색 |
| 학사일정 | SSO | 학사일정 목록 + 상세 |
| 장학공지 | SSO | 장학공지 목록 |
| 시간표 | SSO | 주간 시간표 + ICS 내보내기 |
| 수강과목 | SSO | 수강신청 내역, 개설과목 검색, 강의계획서 |
| LMS | KSSO | 과제, 강의자료, 성적, 퀴즈, 대시보드 |

## 설치

```bash
# 1. 스킬 설치
clawhub install garibong-labs/ku-portal

# 2. Python venv 생성 + 패키지 설치
cd ~/.openclaw/workspace/skills/ku-portal
python3 -m venv .venv
source .venv/bin/activate
pip install ku-portal-mcp

# 3. 자격 증명 설정 (로그인 기능 사용 시)
mkdir -p ~/.config/ku-portal
cat > ~/.config/ku-portal/credentials.json << 'EOF'
{"id": "your-kupid-id", "pw": "your-kupid-password"}
EOF
chmod 600 ~/.config/ku-portal/credentials.json
```

## 사용법

```bash
# venv 활성화 후 실행
source ~/.openclaw/workspace/skills/ku-portal/.venv/bin/activate

# 도서관 좌석 (로그인 불필요)
python3 ku_query.py library
python3 ku_query.py library --name 중앙도서관

# 공지사항
python3 ku_query.py notices --limit 10
python3 ku_query.py notices --detail <message_id>

# 학사일정 / 장학공지
python3 ku_query.py schedules
python3 ku_query.py scholarships

# 통합 검색
python3 ku_query.py search 수강신청

# 시간표
python3 ku_query.py timetable
python3 ku_query.py timetable --day 월
python3 ku_query.py timetable --ics

# 수강과목
python3 ku_query.py mycourses
python3 ku_query.py courses --college 정보대학 --dept 컴퓨터학과
python3 ku_query.py syllabus COSE101

# LMS
python3 ku_query.py lms courses
python3 ku_query.py lms assignments <course_id>
python3 ku_query.py lms todo
python3 ku_query.py lms dashboard
python3 ku_query.py lms grades <course_id>
```

## 보안

- 자격 증명은 `~/.config/ku-portal/credentials.json`에 저장 (chmod 600)
- 워크스페이스 밖이라 git 추적 안 됨
- 세션 캐시: `~/.cache/ku-portal-mcp/session.json` (30분 TTL)

## 라이선스

MIT — 원본 [ku-portal-mcp](https://github.com/SonAIengine/ku-portal-mcp) MIT 라이선스 준수.

## 문의

contact@garibong.dev
