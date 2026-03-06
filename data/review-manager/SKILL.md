---
name: review-manager
description: "고객사 리뷰 수집·자동답글·알림·리포트 통합 관리. 네이버플레이스/구글/배민/쿠팡 리뷰 모니터링 + 감성분석 + 경쟁사 비교"
homepage: https://github.com/openclaw/review-manager
metadata:
  {
    "openclaw":
      {
        "emoji": "⭐",
        "requires": { "bins": ["node"] },
        "install": [],
      },
  }
---

# Review Manager

고객사용 리뷰 통합 관리 시스템. 여러 플랫폼의 리뷰를 자동 수집하고, AI 기반 답글 생성, 악성 리뷰 알림, 주간 분석 리포트를 제공합니다.

## 주요 기능

1. **리뷰 수집** — 네이버 플레이스, 구글 리뷰, 배달의민족, 쿠팡 리뷰 스크래핑
2. **자동 답글** — 긍정 리뷰 감사 답글, 부정 리뷰 공감+해결 답글 자동 생성
3. **악성 리뷰 알림** — 별점 2 이하 or 키워드 감지 시 즉시 알림
4. **주간 리포트** — 평균 별점 추이, 키워드 분석, 감성 분석 요약
5. **경쟁사 비교** — 같은 카테고리 경쟁사 리뷰 점수 모니터링

## 설정

`~/.openclaw/workspace/skills/review-manager/config.json` 생성:

```json
{
  "stores": [
    {
      "id": "store1",
      "name": "무펭이 카페 강남점",
      "platforms": {
        "naver": "https://m.place.naver.com/restaurant/1234567890",
        "google": "ChIJN1t_tD...",
        "baemin": "https://www.baemin.com/...",
        "coupang": "https://www.coupangeats.com/..."
      }
    }
  ],
  "alert": {
    "channels": ["discord"],
    "discordChannelId": "1234567890",
    "thresholds": {
      "lowRating": 2,
      "keywords": ["불친절", "더럽", "환불", "최악"]
    }
  },
  "competitors": [
    {
      "name": "경쟁업체A",
      "naver": "https://m.place.naver.com/restaurant/9876543210"
    }
  ],
  "schedule": {
    "collectInterval": "1h",
    "weeklyReportDay": "monday",
    "weeklyReportTime": "09:00"
  }
}
```

템플릿 복사:

```bash
cp {baseDir}/config.template.json ~/.openclaw/workspace/skills/review-manager/config.json
```

## 사용법

### 1. 리뷰 수집

모든 플랫폼에서 최신 리뷰 수집:

```bash
node {baseDir}/scripts/collect-reviews.js
```

특정 매장만:

```bash
node {baseDir}/scripts/collect-reviews.js --store store1
```

특정 플랫폼만:

```bash
node {baseDir}/scripts/collect-reviews.js --platform naver
```

### 2. 자동 답글 생성

미답변 리뷰에 자동 답글 생성 (실제 등록은 하지 않고 미리보기):

```bash
node {baseDir}/scripts/auto-reply.js --preview
```

실제 등록 (플랫폼 API 또는 브라우저 자동화 필요):

```bash
node {baseDir}/scripts/auto-reply.js --apply
```

### 3. 악성 리뷰 체크

설정된 임계값/키워드에 따라 부정 리뷰 감지 및 알림:

```bash
node {baseDir}/scripts/check-negative.js
```

cron/heartbeat 등록 예시:

```bash
# 매 시간 체크
0 * * * * cd ~/.openclaw/workspace/skills/review-manager && node scripts/check-negative.js
```

### 4. 주간 리포트

지난 7일 리뷰 통계 + 감성 분석 + 키워드 트렌드:

```bash
node {baseDir}/scripts/weekly-report.js
```

Discord로 전송:

```bash
node {baseDir}/scripts/weekly-report.js --send discord
```

### 5. 경쟁사 비교

경쟁사 리뷰 점수 비교 분석:

```bash
node {baseDir}/scripts/compare-competitors.js
```

## 데이터 저장

모든 수집된 리뷰는 `~/.openclaw/workspace/skills/review-manager/data/` 에 JSON 형태로 저장:

```
data/
├── reviews/
│   ├── store1-naver-2026-02.json
│   ├── store1-google-2026-02.json
│   └── ...
├── replies/
│   └── generated-replies.json
└── reports/
    └── weekly-2026-W07.json
```

## 답글 생성 로직

- **별점 4-5**: 감사 + 브랜드 톤앤매너 유지
- **별점 3**: 중립 + 개선 의지 표명
- **별점 1-2**: 공감 + 사과 + 구체적 해결 방안 제시

AI 모델(Claude/GPT)을 활용하여 자연스러운 문장 생성.

## 주의사항

- 플랫폼마다 스크래핑 정책이 다르므로 과도한 요청은 차단될 수 있음
- 네이버 플레이스는 모바일 웹 버전 파싱 권장
- 배민/쿠팡은 로그인 필요할 수 있음 (브라우저 자동화 활용)
- 자동 답글 등록 시 플랫폼 정책 준수 필요

## 팁

- OpenClaw heartbeat과 연동하여 주기적 리뷰 체크 자동화
- Discord webhook으로 실시간 알림 연동
- 답글 톤은 config.json에 브랜드별 커스터마이징 가능

## 트러블슈팅

| 문제 | 해결 |
|------|------|
| 네이버 플레이스 403 에러 | User-Agent 변경, 요청 간격 증가 |
| 구글 리뷰 스크래핑 실패 | Google Places API 사용 검토 |
| 배민 로그인 필요 | browser tool로 쿠키 획득 후 재사용 |
| 답글 생성 품질 낮음 | config.json에 브랜드 가이드라인 추가 |
