# 🎧 CS Auto-Responder

고객사용 CS 자동응답 스킬. 멀티채널 고객 문의를 수신하고, FAQ 기반 자동 응답, 에스컬레이션, 일일 요약을 제공합니다.

## 디렉토리 구조

```
cs-autoresponder/
├── SKILL.md              # OpenClaw 스킬 문서
├── README.md             # 이 파일
├── scripts/              # 실행 스크립트
│   ├── monitor.js        # 채널 모니터링 메인 루프
│   ├── respond.js        # FAQ 매칭 & 자동 응답 (단일 메시지)
│   ├── escalate.js       # 에스컬레이션 알림
│   └── dashboard.js      # 일일 요약 대시보드
├── lib/                  # 유틸리티 라이브러리
│   ├── channels.js       # 채널 어댑터 (mock API)
│   ├── matcher.js        # 의미 기반 FAQ 매칭
│   └── logger.js         # 대화 로그 기록
├── config/               # 설정 파일
│   ├── template.json     # 고객사 설정 템플릿
│   └── faq-template.json # FAQ DB 템플릿
└── logs/                 # 대화 로그 (gitignore)
    └── YYYY-MM-DD/       # 일별 로그 디렉토리
```

## 빠른 시작

### 1. 고객사 설정 파일 생성

```bash
cd /Users/mupeng/.openclaw/workspace/skills/cs-autoresponder
cp config/template.json config/mufi.json
```

`config/mufi.json` 편집:
- `clientId`: "mufi-photobooth"
- `name`: "MUFI 포토부스"
- `channels`: 필요한 채널 활성화
- `escalationTarget`: Discord 채널 ID

### 2. FAQ DB 생성

```bash
cp config/faq-template.json config/mufi-faq.json
```

FAQ 항목 추가/수정

### 3. 단일 메시지 테스트

```bash
node scripts/respond.js \
  --config config/mufi.json \
  --channel instagram \
  --user "test_user" \
  --message "영업시간 알려주세요"
```

### 4. 모니터링 시작 (백그라운드)

```bash
pm2 start scripts/monitor.js --name cs-mufi -- --config config/mufi.json
pm2 logs cs-mufi
pm2 stop cs-mufi
```

### 5. 일일 대시보드 확인

```bash
node scripts/dashboard.js --config config/mufi.json --date 2026-02-18
```

## 핵심 기능

### 1. 멀티채널 수신
- Instagram DM
- 카카오톡 알림톡
- 이메일

### 2. FAQ 매칭
- 키워드 기반 자동 매칭
- 점수 계산 (0-1 스케일)
- 임계값 이상 → 자동 응답

### 3. 에스컬레이션
다음 조건 시 사장님에게 알림:
- FAQ 매칭 실패 (점수 < 0.6)
- 부정 키워드 (환불, 불만, 화남 등)
- 담당자 요청 (사람, 사장님 등)
- 연속 3회 이상 문의

### 4. 응답 톤 커스텀
- `friendly`: 친근하고 따뜻한 톤
- `formal`: 정중하고 격식 있는 톤
- `casual`: 편안하고 캐주얼한 톤

### 5. 로그 기록
- 일별 JSONL 형식
- 채널, 사용자, 메시지, 응답, FAQ ID, 점수 기록
- 90일 자동 보관

### 6. 대시보드 요약
- 총 문의수
- 자동 처리율
- 에스컬레이션 건수
- 카테고리별/채널별 집계

## Production 연동

현재는 **mock API**로 동작합니다. 실제 연동 시:

### Instagram DM
`lib/channels.js`의 `fetchInstagramDMs()` 수정:
```javascript
const { exec } = require('child_process');
const CLI = '/Users/mupeng/.openclaw/workspace/tools/insta-cli/v2.js';
const result = await execAsync(`node ${CLI} unread`);
```

### 카카오톡 알림톡
Kakao Business API 연동

### 이메일
himalaya 또는 Gmail API 활용

## 의미 매칭 업그레이드

현재는 단순 키워드 매칭. Production 시:

### OpenAI Embeddings
```javascript
const openai = new OpenAI();
const embedding = await openai.embeddings.create({
  model: "text-embedding-3-small",
  input: message
});
// FAQ 임베딩과 코사인 유사도 계산
```

### Claude API
```javascript
const response = await anthropic.messages.create({
  model: "claude-3-5-sonnet-20241022",
  messages: [{
    role: "user",
    content: `고객 문의: ${message}\n\nFAQ:\n${faqList}\n\n가장 적합한 FAQ를 찾아주세요.`
  }]
});
```

## 주의사항

- **개인정보 보호**: 로그에 민감한 정보 저장 금지
- **응답 속도**: FAQ 매칭 3초 이내 목표
- **톤 일관성**: 고객사별 톤 준수
- **에스컬레이션 피로**: FAQ 지속 보강으로 에스컬레이션 최소화

## 확장 계획

- [ ] OpenAI Embeddings 기반 의미 매칭
- [ ] 대화 컨텍스트 유지 (세션 관리)
- [ ] A/B 테스트 (응답 톤 실험)
- [ ] 멀티턴 대화 지원
- [ ] 자동 FAQ 학습 (고빈도 질문 감지)
- [ ] 고객 만족도 설문 (응답 후 별점)

## 라이선스

MIT
