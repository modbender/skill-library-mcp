---
name: cs-autoresponder
description: Multi-channel customer service auto-responder with FAQ matching, escalation, and daily summaries.
homepage: https://github.com/openclaw/skills
metadata:
  {
    "openclaw":
      {
        "emoji": "🎧",
        "requires": { "bins": ["node"] },
        "install":
          [
            {
              "id": "node-brew",
              "kind": "brew",
              "formula": "node",
              "bins": ["node"],
              "label": "Install Node.js (brew)",
            },
          ],
      },
  }
---

# 🎧 CS Auto-Responder

고객사용 CS 자동응답 스킬. 멀티채널 고객 문의를 수신하고, FAQ 기반 자동 응답, 에스컬레이션, 일일 요약을 제공합니다.

## 핵심 기능

1. **멀티채널 수신** — 카카오톡 알림톡, 인스타 DM, 이메일 등에서 고객 문의 감지
2. **FAQ 매칭** — 고객사별 FAQ DB (JSON)에서 의미 기반 매칭 → 자동 답변
3. **에스컬레이션** — 복잡한 문의 / 불만 감지 시 사장님한테 Discord/카톡 알림
4. **응답 톤 커스텀** — 고객사 브랜드 톤에 맞춘 답변 생성
5. **로그 기록** — 모든 CS 대화 로그 저장 (일별)
6. **대시보드 요약** — 일일 CS 요약 (총 문의수, 자동처리율, 에스컬레이션 건수)

## 초기 설정

### 1. 고객사 설정 파일 생성

```bash
cd {baseDir}
cp config/template.json config/고객사명.json
```

`config/고객사명.json` 편집:
- `clientId`: 고유 ID
- `name`: 고객사 이름
- `channels`: 연동할 채널 (kakao, instagram, email)
- `tone`: 응답 톤 (formal, friendly, casual)
- `escalationTarget`: Discord 채널 ID 또는 카톡 번호
- `faqPath`: FAQ DB 파일 경로

### 2. FAQ DB 생성

```bash
cp config/faq-template.json config/고객사명-faq.json
```

FAQ 항목 추가 (JSON 배열):
```json
[
  {
    "id": "faq001",
    "question": "영업시간이 어떻게 되나요?",
    "keywords": ["영업시간", "몇시", "언제", "운영"],
    "answer": "저희는 평일 10:00-22:00, 주말 12:00-20:00 영업합니다.",
    "category": "운영정보"
  }
]
```

## 사용법

### 채널 모니터링 시작

```bash
node {baseDir}/scripts/monitor.js --config config/고객사명.json
```

백그라운드 실행 (pm2 권장):
```bash
pm2 start {baseDir}/scripts/monitor.js --name cs-mufi -- --config config/고객사명.json
pm2 logs cs-mufi
```

### 수동 응답 테스트

```bash
node {baseDir}/scripts/respond.js \
  --config config/고객사명.json \
  --channel instagram \
  --user "iam.dawn.kim" \
  --message "영업시간 알려주세요"
```

### 일일 대시보드 요약

```bash
node {baseDir}/scripts/dashboard.js --config config/고객사명.json --date 2026-02-18
```

출력 예시:
```
📊 CS 대시보드 - MUFI 포토부스 (2026-02-18)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
총 문의수: 47건
자동 처리: 38건 (80.9%)
에스컬레이션: 9건 (19.1%)

카테고리별:
  • 운영정보: 18건
  • 가격/예약: 15건
  • 기술문제: 9건
  • 불만/환불: 5건

채널별:
  • Instagram DM: 28건
  • 카카오톡: 13건
  • 이메일: 6건

평균 응답시간: 3.2초
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 에스컬레이션 수동 발송

```bash
node {baseDir}/scripts/escalate.js \
  --config config/고객사명.json \
  --channel instagram \
  --user "angry_customer" \
  --message "환불 요청합니다" \
  --reason "환불 요청"
```

## 디렉토리 구조

```
cs-autoresponder/
├── SKILL.md
├── scripts/
│   ├── monitor.js       # 채널 모니터링 메인 루프
│   ├── respond.js       # FAQ 매칭 & 자동 응답
│   ├── escalate.js      # 에스컬레이션 알림
│   └── dashboard.js     # 일일 요약 대시보드
├── lib/
│   ├── channels.js      # 채널 어댑터 (mock API)
│   ├── matcher.js       # 의미 기반 FAQ 매칭
│   └── logger.js        # 대화 로그 기록
├── config/
│   ├── template.json    # 고객사 설정 템플릿
│   └── faq-template.json # FAQ DB 템플릿
└── logs/
    └── YYYY-MM-DD/      # 일별 대화 로그 (clientId별)
```

## 채널 어댑터 (Mock)

현재는 mock API로 동작. Production 연동 시 `lib/channels.js` 수정:

- **카카오톡**: Kakao Alimtalk API
- **Instagram**: `tools/insta-cli/v2.js` 활용
- **이메일**: himalaya 또는 Gmail API

## 의미 기반 매칭 로직

`lib/matcher.js`는 간단한 키워드 매칭을 사용:
1. 고객 문의를 소문자로 변환
2. FAQ 키워드와 비교 (부분 일치)
3. 매칭 점수 계산 (여러 키워드 매칭 시 가중치 증가)
4. 임계값(0.6) 이상이면 자동 응답, 미만이면 에스컬레이션

Production 시 OpenAI Embeddings 또는 Claude 활용 권장.

## 에스컬레이션 조건

다음 조건 중 하나라도 해당하면 에스컬레이션:
- FAQ 매칭 점수 < 0.6
- 부정 키워드 감지 (환불, 불만, 화남, 실망, 최악)
- 고객이 "담당자", "사람", "사장님" 요청
- 연속 3회 이상 동일 고객 문의

## 로그 형식

`logs/YYYY-MM-DD/{clientId}.jsonl`:
```jsonl
{"timestamp":"2026-02-18T12:34:56.789Z","channel":"instagram","user":"iam.dawn.kim","message":"영업시간?","response":"평일 10-22시 영업합니다","faqId":"faq001","score":0.85,"escalated":false}
{"timestamp":"2026-02-18T12:40:11.123Z","channel":"kakao","user":"010-1234-5678","message":"환불하고 싶어요","response":null,"faqId":null,"score":0.0,"escalated":true,"reason":"환불 키워드"}
```

## 주의사항

- **톤 일관성**: 고객사별 톤 설정을 준수하세요
- **개인정보**: 로그에 민감한 정보(주민번호, 카드번호) 저장 금지
- **응답 속도**: FAQ 매칭은 3초 이내 응답 목표
- **에스컬레이션 피로**: 너무 많은 에스컬레이션은 피로감 유발 → FAQ 지속 보강

## 확장 가능성

- [ ] OpenAI Embeddings 기반 의미 매칭
- [ ] 대화 컨텍스트 유지 (세션 관리)
- [ ] A/B 테스트 (응답 톤 실험)
- [ ] 멀티턴 대화 지원
- [ ] 자동 FAQ 학습 (고빈도 질문 감지)
- [ ] 고객 만족도 설문 (응답 후 별점)

---

**Note**: 이 스킬은 mock API로 제작되었습니다. Production 환경에서는 실제 채널 API 연동이 필요합니다.
