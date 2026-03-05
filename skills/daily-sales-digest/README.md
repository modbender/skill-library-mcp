# daily-sales-digest

고객사용 일일 매출 요약 및 분석 OpenClaw 스킬

## 빠른 시작

### 1. 설정 파일 생성

```bash
mkdir -p ~/.openclaw/workspace/config
cp config.template.json ~/.openclaw/workspace/config/daily-sales-digest.json
```

설정 파일을 편집하여 API 키와 채널 정보를 입력하세요.

### 2. 데이터 디렉토리 생성

```bash
mkdir -p ~/.openclaw/workspace/data/sales
```

### 3. 테스트 실행

```bash
# 어제 데이터 수집 (mock 데이터)
node scripts/collect.js --date yesterday

# 요약 출력
node scripts/digest.js --date yesterday --format text

# 이상 탐지
node scripts/alert.js --date yesterday --threshold 0.3
```

## 스크립트

- `collect.js` — 매출 데이터 수집
- `digest.js` — 요약 리포트 생성
- `alert.js` — 이상 탐지 및 알림

## 자동화

OpenClaw cron을 사용하여 자동 실행:

```bash
# 매일 아침 8시 전일 매출 요약
openclaw cron add \
  --name "daily-sales-digest:daily" \
  --schedule "0 8 * * *" \
  --command "node /Users/mupeng/.openclaw/workspace/skills/daily-sales-digest/scripts/digest.js --date yesterday --deliver discord"
```

## API 연동

현재 mock 데이터를 반환합니다. 실제 API 연동은 각 스크립트의 TODO 섹션을 참고하여 구현하세요.

- 네이버 스마트스토어: https://developer.naver.com/docs/commerce/commerce-api/
- 쿠팡 Wing: https://wing-developers.coupang.com/
- 배민셀러: (별도 제공)

## 디렉토리 구조

```
skills/daily-sales-digest/
├── SKILL.md              # 스킬 메타데이터 및 문서
├── README.md             # 이 파일
├── config.template.json  # 설정 템플릿
└── scripts/
    ├── collect.js        # 데이터 수집
    ├── digest.js         # 요약 생성
    └── alert.js          # 이상 탐지
```

## 라이선스

MIT
