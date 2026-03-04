---
name: korean-scraper
description: Korean website specialized scraper with anti-bot protection (Naver, Coupang, Daum, Instagram)
version: 1.0.0
author: 무펭이 🐧
---

# korean-scraper

**한국 웹사이트 전문 스크래퍼** — Playwright 기반으로 네이버, 쿠팡, 다음 등 한국 주요 사이트에서 구조화된 데이터를 추출합니다. Anti-bot 보호 우회 기능 포함.

## When to Use

- 네이버 블로그 검색 결과 수집 또는 특정 블로그 본문 추출
- 네이버 카페 인기글/최신글 스크래핑
- 쿠팡 상품 정보 (가격, 리뷰, 별점) 수집
- 네이버 뉴스/다음 뉴스 기사 본문 추출
- 한국 사이트 대상 자동화된 데이터 수집

## Installation

```bash
cd skills/korean-scraper
npm install
npx playwright install chromium
```

## Quick Start

### 네이버 블로그
```bash
# 검색 결과 수집
node scripts/naver-blog.js search "맛집 추천" --limit 10

# 특정 블로그 본문 추출
node scripts/naver-blog.js extract "https://blog.naver.com/..."
```

### 네이버 카페
```bash
# 인기글 수집
node scripts/naver-cafe.js popular "카페URL" --limit 20

# 최신글 수집
node scripts/naver-cafe.js recent "카페URL" --limit 20
```

### 쿠팡 상품
```bash
# 상품 정보 추출
node scripts/coupang.js product "상품URL"

# 검색 결과 수집
node scripts/coupang.js search "무선 이어폰" --limit 20
```

### 네이버 뉴스
```bash
# 검색 결과 수집
node scripts/naver-news.js search "AI" --limit 10

# 기사 본문 추출
node scripts/naver-news.js extract "https://n.news.naver.com/..."
```

### 다음 뉴스
```bash
# 검색 결과 수집
node scripts/daum-news.js search "경제" --limit 10

# 기사 본문 추출
node scripts/daum-news.js extract "https://v.daum.net/..."
```

## Output Format

모든 스크립트는 구조화된 JSON을 반환합니다:

### 네이버 블로그 검색
```json
{
  "status": "success",
  "query": "맛집 추천",
  "count": 10,
  "results": [
    {
      "title": "서울 강남 맛집 추천 BEST 5",
      "url": "https://blog.naver.com/...",
      "blogger": "맛집탐험가",
      "date": "2026-02-15",
      "snippet": "강남역 근처 숨은 맛집들을..."
    }
  ]
}
```

### 네이버 블로그 본문
```json
{
  "status": "success",
  "url": "https://blog.naver.com/...",
  "title": "서울 강남 맛집 추천 BEST 5",
  "author": "맛집탐험가",
  "date": "2026-02-15",
  "content": "# 서울 강남 맛집 추천 BEST 5\n\n1. ...",
  "images": ["https://..."],
  "tags": ["맛집", "강남", "서울"]
}
```

### 쿠팡 상품
```json
{
  "status": "success",
  "url": "https://www.coupang.com/...",
  "productName": "애플 에어팟 프로 2세대",
  "price": 299000,
  "originalPrice": 359000,
  "discount": "17%",
  "rating": 4.8,
  "reviewCount": 1523,
  "rocketDelivery": true,
  "seller": "쿠팡",
  "images": ["https://..."]
}
```

### 네이버 카페
```json
{
  "status": "success",
  "cafeUrl": "https://cafe.naver.com/...",
  "type": "popular",
  "count": 20,
  "posts": [
    {
      "title": "신입 회원 인사드립니다",
      "url": "https://cafe.naver.com/.../12345",
      "author": "닉네임",
      "date": "2026-02-17",
      "views": 523,
      "comments": 12
    }
  ]
}
```

### 뉴스 기사
```json
{
  "status": "success",
  "url": "https://n.news.naver.com/...",
  "title": "AI 시장 규모 급성장 전망",
  "media": "조선일보",
  "author": "홍길동 기자",
  "date": "2026-02-17 09:30",
  "content": "# AI 시장 규모 급성장 전망\n\n...",
  "category": "IT/과학",
  "images": ["https://..."]
}
```

## Anti-Bot Features

- **navigator.webdriver 숨김** — 자동화 탐지 회피
- **실제 User-Agent 사용** — 모바일/데스크탑 랜덤
- **인간 행동 모방** — 랜덤 딜레이, 스크롤
- **Stealth Plugin** — Playwright extra stealth
- **Cloudflare 우회** — 대기 시간 자동 조정

## Rate Limiting

모든 스크립트는 기본적으로 사이트를 보호합니다:

- 요청당 2-5초 랜덤 딜레이
- 동일 도메인 1초당 최대 1회 요청
- 429 응답 시 자동 백오프
- `--fast` 플래그로 딜레이 축소 가능 (주의)

## Error Handling

| 상황 | 동작 |
|------|------|
| 404 | JSON으로 에러 반환, 계속 진행 |
| 403/차단 | 재시도 (최대 3회) |
| 타임아웃 | 대기 시간 연장 후 재시도 |
| 로그인 필요 | 경고 메시지 + 가능한 데이터만 반환 |

## Environment Variables

```bash
# Headless 모드 끄기 (디버깅용)
HEADLESS=false node scripts/naver-blog.js ...

# 스크린샷 저장
SCREENSHOT=true node scripts/coupang.js ...

# 대기 시간 조정 (ms)
WAIT_TIME=10000 node scripts/naver-cafe.js ...

# User-Agent 커스텀
USER_AGENT="..." node scripts/naver-news.js ...
```

## Integration Examples

### OpenClaw Agent 통합
```javascript
// 네이버 블로그 검색
const result = await exec({
  command: 'node scripts/naver-blog.js search "AI 트렌드" --limit 5',
  workdir: '/path/to/skills/korean-scraper'
});
const data = JSON.parse(result.stdout);
```

### Batch Processing
```bash
# 여러 URL 일괄 처리
cat urls.txt | while read url; do
  node scripts/naver-blog.js extract "$url" >> results.jsonl
done
```

## Limitations

- **로그인 필요 콘텐츠**: 현재 비로그인 상태로만 스크래핑 (쿠팡 일부 리뷰 등)
- **동적 로딩**: 무한 스크롤은 기본 10개까지만 (--scroll 플래그로 확장 가능)
- **CAPTCHA**: 수동 우회 필요 (자동화 불가)
- **IP 차단**: 과도한 요청 시 일시적 차단 가능 (rate limiting 준수 필요)

## Compliance & Ethics

- ✅ 공개된 정보만 수집
- ✅ robots.txt 준수 (기본값)
- ✅ Rate limiting으로 서버 부하 최소화
- ❌ 개인정보 수집 금지
- ❌ 로그인 필요 콘텐츠 무단 접근 금지
- ❌ 저작권 침해 목적 사용 금지

## Troubleshooting

### 문제: 403 Forbidden
**해결책**: 
1. User-Agent 변경 시도
2. 대기 시간 늘리기 (`WAIT_TIME=15000`)
3. Headless 모드 끄기 (`HEADLESS=false`)

### 문제: 빈 결과 반환
**해결책**:
1. URL 형식 확인
2. 사이트 구조 변경 가능성 (셀렉터 업데이트 필요)
3. 로그인 필요 여부 확인

### 문제: Timeout
**해결책**:
1. `WAIT_TIME` 늘리기
2. 인터넷 연결 확인
3. 사이트 접근 가능 여부 확인 (VPN 필요 등)

## Maintenance

한국 사이트들은 UI를 자주 변경하므로, 셀렉터 업데이트가 필요할 수 있습니다.

셀렉터 위치: `scripts/` 내 각 파일 상단 `SELECTORS` 객체

```javascript
const SELECTORS = {
  blogTitle: '.se-title-text',
  blogContent: '.se-main-container',
  // ...
};
```

## Future Improvements

- [ ] 인스타그램 게시물 스크래핑
- [ ] 네이버 쇼핑 가격 비교
- [ ] 유튜브 한국 채널 메타데이터
- [ ] 배치 처리 최적화 (병렬 실행)
- [ ] 쿠키/세션 관리 (로그인 유지)
- [ ] Proxy 지원

## References

- [Playwright Official Docs](https://playwright.dev/)
- [playwright-extra-plugin-stealth](https://github.com/berstend/puppeteer-extra/tree/master/packages/puppeteer-extra-plugin-stealth)
- [네이버 개발자 센터](https://developers.naver.com/)
