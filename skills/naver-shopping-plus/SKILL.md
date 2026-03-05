---
name: naver-shopping-plus
description: 한국형 쇼핑 검색 스킬. 네이버 쇼핑 API + 쿠팡/11번가 웹 스크래핑으로 배송비 포함 최저가를 자동 비교합니다.
---

# Naver Shopping Plus

네이버 쇼핑, 쿠팡, 11번가에서 상품을 검색하고 배송비 포함 최저가를 비교합니다.

## 기능

- **다중 플랫폼 검색**: 네이버 쇼핑 API + 쿠팡/11번가 웹 스크래핑
- **배송비 포함 가격**: 실제 구매 가격 자동 계산
- **최저가 자동 정렬**: 플랫폼별 최저가 상품 우선 표시
- **깔끔한 출력**: Discord/터미널 친화적 포맷

## 사용법

```bash
/Users/mupeng/.openclaw/workspace/skills/naver-shopping-plus/scripts/search.py "검색어"
```

### 옵션

- `--display <number>`: 플랫폼당 결과 수 (기본: 3, 최대: 10)
- `--platforms <naver,coupang,11st>`: 검색할 플랫폼 선택 (기본: 전체)
- `--sort <price|review>`: 정렬 기준 (price: 가격순, review: 리뷰순)
- `--max-price <number>`: 최대 가격 필터 (원 단위)

### 예시

```bash
# 기본 검색 (전체 플랫폼)
search.py "아이폰 16 프로"

# 네이버만 검색, 5개 결과
search.py "갤럭시 버즈" --platforms naver --display 5

# 최대 50만원, 가격순 정렬
search.py "노트북" --max-price 500000 --sort price
```

## 환경 변수

`.env` 파일에 다음 변수 필요:
- `NAVER_Client_ID`: 네이버 API 클라이언트 ID
- `NAVER_Client_Secret`: 네이버 API 시크릿 키

## 출력 형식

```
🛍️ [네이버 쇼핑] 갤럭시 버즈2 프로
   💰 159,000원 (배송비 무료) = 총 159,000원
   ⭐ 리뷰 1,234개 (4.5/5)
   🔗 https://shopping.naver.com/...

🛒 [쿠팡] 갤럭시 버즈2 프로
   💰 155,000원 (배송비 2,500원) = 총 157,500원 ⭐ 최저가!
   ⭐ 로켓배송
   🔗 https://coupang.com/...
```

## 의존성

```bash
pip install requests beautifulsoup4 lxml
```

## 주의사항

- 웹 스크래핑은 사이트 구조 변경 시 동작하지 않을 수 있습니다
- 과도한 요청 시 IP 차단될 수 있으니 적절히 사용하세요
- 쿠팡/11번가는 로그인 필요 없는 검색 결과만 수집합니다
