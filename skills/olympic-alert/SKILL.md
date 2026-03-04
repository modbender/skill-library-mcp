---
name: olympic-alert
description: 올림픽 경기 알림. 경기 15분 전 알림 발송, 일정 관리(추가/삭제), 중계 링크 포함. 2026 밀라노 동계올림픽 한국팀 기본 설정 포함.
metadata:
  openclaw:
    requires:
      bins: ["python3"]
    triggers:
      - 올림픽
      - Olympic
      - 동계올림픽
      - 경기 알림
      - 밀라노
---

# Olympic Alert Skill

올림픽 경기 알림을 15분 전에 발송합니다. 한국팀 경기 기본 설정 포함.

## 포함 파일

| 파일 | 설명 |
|------|------|
| `SKILL.md` | 이 문서 |
| `scripts/check_olympic.py` | 메인 스크립트 (Python 3.6+, 표준 라이브러리만 사용) |
| `scripts/events.json` | 경기 일정 데이터 (2026 밀라노 동계올림픽 한국팀 기본값) |

## 의존성
- Python 3.6+ (표준 라이브러리만 사용, 추가 패키지 불필요)

## 사용법

스킬 디렉토리 기준 상대경로로 실행합니다:

```bash
SKILL_DIR="<workspace>/skills/olympic-alert"

# 알림 체크 (HEARTBEAT에서 호출)
python3 "$SKILL_DIR/scripts/check_olympic.py"

# 다가오는 경기 목록
python3 "$SKILL_DIR/scripts/check_olympic.py" list

# 경기 추가
python3 "$SKILL_DIR/scripts/check_olympic.py" add "2026-02-15 14:00" "🏒 쇼트트랙 준결승" "최민정"

# 경기 삭제 (이름 패턴 매칭)
python3 "$SKILL_DIR/scripts/check_olympic.py" remove "준결승"
```

## 설정

### events.json

`scripts/events.json` 파일에서 경기 일정 관리:

```json
{
  "country": "Korea",
  "flag": "🇰🇷",
  "links": {
    "네이버 스포츠": "https://m.sports.naver.com/milanocortina2026",
    "치지직": "https://chzzk.naver.com/search?query=올림픽"
  },
  "events": [
    {"time": "2026-02-10 18:00", "name": "🏒 쇼트트랙", "athletes": "최민정"}
  ]
}
```

### 상태 파일

`~/.config/olympic-alert/state.json` — 알림 발송 기록 (중복 방지)

## HEARTBEAT.md 설정

```markdown
## 올림픽 경기 알림 (every heartbeat)
On each heartbeat:
1. Run `python3 <skill_dir>/scripts/check_olympic.py`
2. If output is not "알림 없음" → 사용자에게 알림 전송
```

## 일정 업데이트

예선 결과에 따라 일정 변경 필요:
- 진출 시: `add` 명령으로 준결승/결승 추가
- 탈락 시: `remove` 명령으로 해당 경기 삭제
- 또는 `events.json` 직접 편집

## 알림 예시

```
🇰🇷 10분 후
🏒 쇼트트랙 여자1500m 결승
👤 최민정 3연속 금 도전

📺 네이버 스포츠 | 치지직
```

## 다른 국가/대회 적용

`events.json`의 `country`, `flag`, `links`, `events`를 수정하여 다른 국가나 대회에 적용 가능.

## 문의 / Feedback

버그 리포트, 기능 요청, 피드백은 아래로 보내주세요.
- Email: contact@garibong.dev
- Developer: Garibong Labs (가리봉랩스)
