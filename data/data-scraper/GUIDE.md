# data-scraper

**웹 데이터 수집** — 특정 웹페이지에서 구조화된 데이터를 추출하여 분석 가능한 형태로 저장합니다.

## 🎯 목적

웹사이트의 공개 데이터를 자동으로 수집하여 경쟁 분석, 트렌드 모니터링, 가격 추적 등에 활용합니다.

## 🔧 수집 방법

```
curl → HTML → 텍스트 추출 → 데이터 파싱 → 구조화
```

1. **curl**: URL에서 HTML 다운로드
2. **텍스트 추출**: HTML에서 텍스트만 추출 (lynx/html2text)
3. **파싱**: 텍스트에서 패턴 추출
4. **구조화**: JSON 또는 테이블 형식으로 변환

## 📊 주요 용도

### 1. 크몽 경쟁 서비스 가격 수집

```
URL: https://kmong.com/search?keyword=AI챗봇
추출: 서비스명, 가격, 평점, 판매수
```

**출력 예시 (테이블):**
| 서비스명 | 가격 | 평점 | 판매수 |
|---------|------|------|--------|
| AI 챗봇 개발 | 150,000원 | 4.9 | 230 |
| 챗봇 제작 | 120,000원 | 4.7 | 180 |

### 2. 기술 블로그 최신 글 목록

```
URL: https://toss.tech/
추출: 제목, 날짜, 카테고리, 링크
```

**출력 예시 (JSON):**
```json
{
  "blog": "toss.tech",
  "scraped_at": "2026-02-14T07:58:00+09:00",
  "posts": [
    {
      "title": "토스 디자인 시스템 2.0 공개",
      "date": "2026-02-10",
      "category": "design",
      "url": "https://toss.tech/article/design-system-2.0"
    }
  ]
}
```

### 3. 채용 공고 모니터링

```
URL: https://www.wanted.co.kr/wdlist/518/872
추출: 회사명, 포지션, 연봉, 마감일
```

### 4. 제품 가격 변동 추적

```
URL: 쿠팡, 11번가 등 상품 페이지
추출: 상품명, 현재가, 할인율
비교: 이전 가격과 비교하여 변동률 계산
```

## 💾 결과 저장

### 저장 위치
```
memory/scraped/
  ├── kmong-ai-chatbot-2026-02-14.json
  ├── toss-tech-posts-2026-02-14.json
  └── product-prices-2026-02-14.json
```

### 출력 형식

**JSON (기본):**
```json
{
  "source": "https://example.com",
  "scraped_at": "2026-02-14T07:58:00+09:00",
  "data": [
    { "field1": "value1", "field2": "value2" }
  ]
}
```

**마크다운 테이블 (Discord/WhatsApp용):**
```markdown
## 크몽 AI 챗봇 서비스 가격 (2026-02-14)

• AI 챗봇 개발 - 150,000원 (⭐ 4.9, 판매 230건)
• 챗봇 제작 - 120,000원 (⭐ 4.7, 판매 180건)
• 맞춤형 챗봇 - 200,000원 (⭐ 5.0, 판매 95건)
```

## 📊 이벤트 생성

수집 결과를 `events/scrape-result-YYYY-MM-DD.json`으로 저장:

```json
{
  "timestamp": "2026-02-14T07:58:00+09:00",
  "skill": "data-scraper",
  "source": "https://kmong.com/search?keyword=AI챗봇",
  "result_file": "memory/scraped/kmong-ai-chatbot-2026-02-14.json",
  "item_count": 15,
  "summary": "AI 챗봇 서비스 15건 수집 완료. 평균가 167,000원."
}
```

## 🎤 트리거

다음 키워드로 스킬을 활성화할 수 있습니다:

- "스크래핑"
- "데이터 수집"
- "scrape"
- "크롤링"
- "가격 조사"

## 🚀 사용 예시

### 기본 스크래핑
```
"크몽에서 AI 챗봇 서비스 가격 조사해줘"
```

### 정기 모니터링
```
"토스 테크 블로그 새 글 스크래핑해서 daily-report에 포함시켜줘"
```

### 가격 추적
```
"이 상품 페이지 가격 매일 체크해줘: https://..."
```

## ⚙️ 구현 가이드

### 1. URL 접근
```bash
curl -s -L "$URL" > /tmp/page.html
```

### 2. 텍스트 추출
```bash
# lynx 사용 (설치 필요: brew install lynx)
lynx -dump -nolist "$URL" > /tmp/page.txt

# 또는 간단한 sed 필터링
sed 's/<[^>]*>//g' /tmp/page.html > /tmp/page.txt
```

### 3. 패턴 추출
정규식 기반으로 데이터 추출:

```bash
# 예: 가격 패턴 추출
grep -oE '[0-9,]+원' /tmp/page.txt
```

### 4. JSON 저장
```bash
cat > "$OUTPUT_FILE" <<EOF
{
  "source": "$URL",
  "scraped_at": "$(date -u +"%Y-%m-%dT%H:%M:%S+09:00")",
  "data": $(echo "$EXTRACTED_DATA" | jq -R -s 'split("\n")')
}
EOF
```

## 🛡️ 주의사항

- **robots.txt 준수**: 크롤링 허용 여부 확인
- **요청 제한**: 과도한 요청으로 서버 부담 주지 않기 (1초 간격 권장)
- **개인정보 수집 금지**: 공개된 정보만 수집
- **저작권 존중**: 수집 데이터는 분석 목적으로만 사용

---

> 🐧 Built by **무펭이** — [무펭이즘(Mupengism)](https://github.com/mupeng) 생태계 스킬
