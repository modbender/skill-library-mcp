---
name: ipo-alert
description: 한국 공모주 청약/신규상장 일정 알림. 38.co.kr에서 데이터 수집, D-1/당일 알림, 주간 요약 제공.
metadata:
  openclaw:
    requires:
      bins: ["python3", "curl"]
    triggers:
      - 공모주
      - IPO
      - 청약
      - 상장
      - 38.co.kr
---

# IPO Alert Skill

38.co.kr에서 공모주청약 일정과 신규상장 정보를 모니터링하고 알림을 보냅니다.

## 포함 파일

| 파일 | 설명 |
|------|------|
| `SKILL.md` | 이 문서 |
| `check_ipo.py` | 메인 스크립트 (Python 3.6+, 표준 라이브러리만 사용) |

## 데이터 소스
- 공모주청약 일정: https://www.38.co.kr/html/fund/index.htm?o=k
- 신규상장: https://www.38.co.kr/html/fund/index.htm?o=nw

## 의존성
- Python 3.6+ (표준 라이브러리만 사용, 추가 패키지 불필요)
- `curl` (38.co.kr 데이터 수집에 사용)

## 설치 후 설정

1. 상태 파일 디렉토리 생성: `mkdir -p ~/.config/ipo-alert`
2. 크론잡 또는 HEARTBEAT.md에 체크 추가

## 스크립트

스킬 디렉토리 기준 상대경로로 실행합니다:

```bash
# 스킬 경로 변수 (설치 위치에 맞게)
SKILL_DIR="<workspace>/skills/ipo-alert"

# 일일 체크 (청약 D-1, 당일 알림)
python3 "$SKILL_DIR/check_ipo.py" daily

# 주간 요약 (다음주 일정)
python3 "$SKILL_DIR/check_ipo.py" weekly

# 현재 일정 확인 (테스트용)
python3 "$SKILL_DIR/check_ipo.py" list
```

## 알림 규칙

### 일일 알림 (daily)
- 청약 시작 **하루 전** (D-1): "⏰ [내일 청약 시작]"
- 청약 시작 **당일** (D-day): "🚀 [오늘 청약 시작]"
- 신규상장 **하루 전**: "⏰ [내일 신규상장]"
- 신규상장 **당일**: "🎉 [오늘 신규상장]"

### 주간 요약 (weekly)
- 매주 일요일 저녁에 실행
- 다음주 월~금 청약/상장 일정 리스트

## 상태 파일
`~/.config/ipo-alert/state.json` - 이미 알림 보낸 종목 추적 (중복 알림 방지)

## HEARTBEAT.md 설정 예시

```markdown
## 공모주 알림 (every heartbeat)
On each heartbeat:
1. Run `python3 <skill_dir>/check_ipo.py daily`
2. If output contains alerts (not "알림 없음") → 사용자에게 알림 전송
```

## Cron 설정 (주간 요약)

일요일 저녁 7시에 다음주 일정 요약:
```json
{
  "schedule": { "kind": "cron", "expr": "0 19 * * 0", "tz": "Asia/Seoul" },
  "payload": { "kind": "agentTurn", "message": "공모주 주간 요약 발송해줘." }
}
```

## 알림 예시

### 일일 알림
```
⏰ [내일 청약 시작]
📋 [카나프테라퓨틱스](https://www.38.co.kr/html/fund/?o=v&no=2269)
   청약: 03/05(목)~06(금)
   공모가: 16,000~20,000
   주간사: 한국투자증권
```

### 주간 요약
```
📅 다음주 공모주 일정 (03/03 ~ 03/07)

【청약 일정】
📋 [카나프테라퓨틱스](https://www.38.co.kr/html/fund/?o=v&no=2269)
   청약: 03/05(목)~06(금)
   공모가: 16,000~20,000
   주간사: 한국투자증권

【신규상장】
🔔 [케이뱅크](https://www.38.co.kr/html/fund/?o=v&no=2271)
   상장일: 03/05(수)
   공모가: 8,300~9,500
```

## 라이선스
MIT

## 문의 / Feedback

버그 리포트, 기능 요청, 피드백은 아래로 보내주세요.
- Email: contact@garibong.dev
- Developer: Garibong Labs (가리봉랩스)
