# Review Manager - 고객사 리뷰 통합 관리 시스템

여러 플랫폼의 리뷰를 자동 수집하고, AI 기반 답글 생성, 악성 리뷰 알림, 주간 분석 리포트를 제공하는 OpenClaw 스킬입니다.

## 설치

1. **설정 파일 생성**

```bash
cd ~/.openclaw/workspace/skills/review-manager
cp config.template.json config.json
```

2. **config.json 편집**

- 매장 정보 (ID, 이름, 플랫폼 URL)
- Discord 채널 ID (알림용)
- 임계값 설정 (별점, 키워드)
- 경쟁사 정보

## 사용법

### 1. 리뷰 수집

```bash
# 모든 매장, 모든 플랫폼
node scripts/collect-reviews.js

# 특정 매장만
node scripts/collect-reviews.js --store store1

# 특정 플랫폼만
node scripts/collect-reviews.js --platform naver
```

### 2. 자동 답글 생성

```bash
# 미리보기 (실제 등록 안 함)
node scripts/auto-reply.js --preview

# 실제 등록 (TODO: 구현 필요)
node scripts/auto-reply.js --apply
```

### 3. 악성 리뷰 체크

```bash
node scripts/check-negative.js
```

**cron 등록 예시 (매 시간 체크)**:
```bash
0 * * * * cd ~/.openclaw/workspace/skills/review-manager && node scripts/check-negative.js
```

### 4. 주간 리포트

```bash
# 리포트 생성 (콘솔 출력 + 파일 저장)
node scripts/weekly-report.js

# Discord로 전송
node scripts/weekly-report.js --send discord
```

### 5. 경쟁사 비교

```bash
node scripts/compare-competitors.js
```

## 데이터 구조

```
~/.openclaw/workspace/skills/review-manager/
├── config.json              # 설정 파일
├── data/
│   ├── reviews/             # 수집된 리뷰 (플랫폼별 월별 JSON)
│   │   ├── store1-naver-2026-02.json
│   │   └── store1-google-2026-02.json
│   ├── replies/             # 생성된 답글
│   │   └── generated-replies.json
│   ├── reports/             # 주간/경쟁사 리포트
│   │   ├── weekly-2026-W07.json
│   │   └── competitor-comparison-2026-02-18.json
│   └── alert-state.json     # 알림 발송 이력 (중복 방지)
```

## 자동화 (OpenClaw Heartbeat)

`HEARTBEAT.md`에 추가:

```markdown
## 리뷰 관리

- **매 1시간**: 리뷰 수집 + 악성 리뷰 체크
- **매주 월요일 09:00**: 주간 리포트 전송

```bash
# 리뷰 수집
if (hour % 1 === 0) {
  exec('node ~/.openclaw/workspace/skills/review-manager/scripts/collect-reviews.js');
  exec('node ~/.openclaw/workspace/skills/review-manager/scripts/check-negative.js');
}

# 주간 리포트 (월요일 09:00)
if (day === 'monday' && hour === 9) {
  exec('node ~/.openclaw/workspace/skills/review-manager/scripts/weekly-report.js --send discord');
}
```
\`\`\`

## TODO (추후 개발)

- [ ] 실제 플랫폼 스크래핑 구현 (browser tool 활용)
  - [ ] 네이버 플레이스
  - [ ] 구글 리뷰 (Google Places API)
  - [ ] 배달의민족 (로그인 필요)
  - [ ] 쿠팡이츠 (로그인 필요)
- [ ] 답글 자동 등록 기능 (플랫폼별 API/자동화)
- [ ] Claude/GPT API 연동 (더 정교한 답글 생성)
- [ ] 감성 분석 고도화 (AI 모델 활용)
- [ ] 대시보드 웹 UI (Canvas)

## 트러블슈팅

| 문제 | 해결 |
|------|------|
| config.json 없음 | `cp config.template.json config.json` |
| Discord 알림 안 옴 | `config.json`에 `discordChannelId` 확인 |
| 리뷰 수집 실패 | 플랫폼 URL 유효성 확인, User-Agent 변경 |
| 권한 에러 | `chmod +x scripts/*.js` |

## 라이선스

MIT
