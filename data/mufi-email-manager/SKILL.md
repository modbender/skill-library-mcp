---
name: mufi-email-manager
description: 한국형 이메일 통합 관리 도구. Gmail, 네이버, 다음, 카카오 메일을 IMAP/SMTP로 통합 관리. 읽지 않은 메일 요약, 키워드 필터링, 자동 답장, 일일 다이제스트 생성.
---

# mufi-email-manager

한국 주요 이메일 서비스(Gmail, 네이버, 다음, 카카오)를 통합 관리하는 IMAP/SMTP 기반 도구입니다.

## 주요 기능

- 📬 **다중 계정 통합**: Gmail, 네이버, 다음, 카카오 메일 동시 관리
- 📊 **스마트 요약**: 읽지 않은 메일 자동 요약 및 분류
- 🔍 **키워드 필터링**: 중요 메일 자동 탐지 (업무, 결제, 보안 등)
- 🤖 **자동 답장**: 템플릿 기반 빠른 답장
- 📰 **일일 다이제스트**: 하루 메일 요약 리포트 생성

## 설정

### 환경 변수 설정

스킬 폴더에 `.env` 파일을 생성하거나 환경 변수로 설정:

```bash
# 기본 계정 (필수)
DEFAULT_ACCOUNT=gmail  # gmail, naver, daum, kakao 중 선택

# Gmail 계정
GMAIL_USER=your@gmail.com
GMAIL_PASS=your_app_password
GMAIL_IMAP_HOST=imap.gmail.com
GMAIL_IMAP_PORT=993
GMAIL_SMTP_HOST=smtp.gmail.com
GMAIL_SMTP_PORT=587

# 네이버 메일
NAVER_USER=your@naver.com
NAVER_PASS=your_password
NAVER_IMAP_HOST=imap.naver.com
NAVER_IMAP_PORT=993
NAVER_SMTP_HOST=smtp.naver.com
NAVER_SMTP_PORT=587

# 다음(Daum) 메일
DAUM_USER=your@daum.net
DAUM_PASS=your_password
DAUM_IMAP_HOST=imap.daum.net
DAUM_IMAP_PORT=993
DAUM_SMTP_HOST=smtp.daum.net
DAUM_SMTP_PORT=465

# 카카오(Kakao) 메일
KAKAO_USER=your@kakao.com
KAKAO_PASS=your_password
KAKAO_IMAP_HOST=imap.kakao.com
KAKAO_IMAP_PORT=993
KAKAO_SMTP_HOST=smtp.kakao.com
KAKAO_SMTP_PORT=465

# 필터 키워드 (쉼표로 구분)
IMPORTANT_KEYWORDS=결제,청구,납부,계약,승인,보안,비밀번호,urgent,invoice
SPAM_KEYWORDS=광고,홍보,이벤트,쿠폰,할인

# 다이제스트 설정
DIGEST_ENABLED=true
DIGEST_TIME=09:00
DIGEST_RECIPIENTS=your@gmail.com
```

## 한국 이메일 서버 정보

| 서비스 | IMAP 서버 | IMAP 포트 | SMTP 서버 | SMTP 포트 | 비고 |
|--------|-----------|-----------|-----------|-----------|------|
| Gmail | imap.gmail.com | 993 | smtp.gmail.com | 587 | 2단계 인증 시 앱 비밀번호 필요 |
| 네이버 | imap.naver.com | 993 | smtp.naver.com | 587 | IMAP/SMTP 설정 활성화 필요 |
| 다음 | imap.daum.net | 993 | smtp.daum.net | 465 | SSL 사용 |
| 카카오 | imap.kakao.com | 993 | smtp.kakao.com | 465 | SSL 사용 |
| 한메일 | imap.daum.net | 993 | smtp.daum.net | 465 | 다음과 동일 |

**중요:**
- **Gmail**: 2단계 인증 사용 시 앱 비밀번호 필수
- **네이버**: 메일 설정에서 IMAP/SMTP 사용 설정 필요
- **다음/카카오**: SMTP 포트 465 (SSL 직접 연결)

## 명령어

### 1. 통합 메일 확인

모든 계정의 읽지 않은 메일 확인:

```bash
node scripts/check-all.js [--limit 20]
```

특정 계정만 확인:

```bash
node scripts/check.js --account gmail [--limit 10]
node scripts/check.js --account naver [--limit 10]
```

### 2. 스마트 요약

읽지 않은 메일을 키워드 기반으로 분류하여 요약:

```bash
node scripts/summary.js [--account gmail] [--recent 24h]
```

출력 예시:
```
📬 읽지 않은 메일 요약 (Gmail)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔴 중요 (3건)
  - [결제] 카드 승인 내역 안내 (신한카드)
  - [보안] 새로운 기기에서 로그인 시도 (Google)
  - [업무] 프로젝트 마감 알림 (팀장님)

🟡 일반 (12건)
  - 주간 뉴스레터 (Tech News)
  - 배송 완료 알림 (쿠팡)
  ...

🔵 읽을만한 (5건)
  - 친구 초대장 (Facebook)
  ...
```

### 3. 중요 메일 필터링

키워드로 중요 메일만 추출:

```bash
node scripts/filter.js --keywords "결제,청구,승인" [--account all] [--recent 7d]
```

### 4. 자동 답장

템플릿 기반 빠른 답장:

```bash
# 템플릿 목록
node scripts/reply.js --list

# 템플릿 사용
node scripts/reply.js --uid 12345 --template thanks --account gmail

# 커스텀 답장
node scripts/reply.js --uid 12345 --body "감사합니다." --account gmail
```

기본 템플릿:
- `thanks`: 감사 인사
- `confirm`: 확인 완료
- `meeting`: 미팅 일정 조율
- `ooo`: 부재중 자동 응답

### 5. 일일 다이제스트

하루 메일 요약 리포트 생성:

```bash
node scripts/digest.js [--date 2026-02-16] [--accounts gmail,naver]
```

출력 형식:
- 텍스트 리포트
- HTML 이메일로 전송 옵션
- JSON 형식 지원

### 6. 메일 발송

통합 발송 인터페이스:

```bash
node scripts/send.js \
  --account gmail \
  --to recipient@example.com \
  --subject "안녕하세요" \
  --body "메일 본문입니다." \
  [--attach file.pdf]
```

### 7. 검색

모든 계정에서 통합 검색:

```bash
node scripts/search.js \
  --query "프로젝트" \
  [--accounts gmail,naver] \
  [--recent 30d] \
  [--limit 50]
```

## 템플릿 커스터마이징

`scripts/templates.json` 파일에서 답장 템플릿 수정 가능:

```json
{
  "thanks": {
    "subject": "Re: {original_subject}",
    "body": "안녕하세요,\n\n메일 감사합니다.\n확인 후 회신 드리겠습니다.\n\n감사합니다."
  },
  "confirm": {
    "subject": "Re: {original_subject}",
    "body": "확인 완료했습니다.\n추가 문의 사항 있으시면 연락 주세요."
  }
}
```

## 크론 작업 예시

매일 아침 9시 다이제스트 발송:

```bash
0 9 * * * cd /path/to/mufi-email-manager && node scripts/digest.js --send
```

30분마다 중요 메일 체크:

```bash
*/30 * * * * cd /path/to/mufi-email-manager && node scripts/filter.js --keywords "긴급,urgent" --notify
```

## 설치

```bash
cd skills/mufi-email-manager
npm install
```

## 보안 주의사항

- `.env` 파일을 `.gitignore`에 추가
- Gmail은 앱 비밀번호 사용 권장
- 비밀번호를 코드에 하드코딩하지 말 것
- 중요 메일은 자동 삭제하지 않도록 주의

## 트러블슈팅

**연결 실패:**
- 서버 주소와 포트 확인
- 방화벽 설정 확인

**인증 실패:**
- 이메일 주소와 비밀번호 재확인
- Gmail: 앱 비밀번호 사용 여부 확인
- 네이버: IMAP/SMTP 설정 활성화 여부 확인

**TLS/SSL 에러:**
- 다음/카카오는 SMTP 포트 465 (SSL 직접 연결)
- Gmail/네이버는 SMTP 포트 587 (STARTTLS)

## 라이센스

MIT
