# Naver Shopping Plus

한국형 쇼핑 검색 스킬 - 네이버 쇼핑 API + 쿠팡/11번가 웹 스크래핑 통합

## 특징

✅ **다중 플랫폼 검색**
- 네이버 쇼핑 API (공식)
- 쿠팡 웹 스크래핑
- 11번가 웹 스크래핑

✅ **배송비 포함 최저가 계산**
- 상품 가격 + 배송비 = 실제 구매 가격
- 플랫폼별 최저가 자동 표시

✅ **깔끔한 출력**
- Discord/터미널 친화적 포맷
- 가격 비교 한눈에 확인
- 로켓배송 등 배송 정보 표시

## 설치

### 1. 의존성 설치

```bash
pip install requests beautifulsoup4 lxml
```

### 2. 환경 변수 설정

`.env` 파일에 네이버 API 키 추가:

```env
NAVER_Client_ID=your_client_id
NAVER_Client_Secret=your_client_secret
```

네이버 API 키 발급: https://developers.naver.com/

### 3. 실행 권한 부여

```bash
chmod +x /Users/mupeng/.openclaw/workspace/skills/naver-shopping-plus/scripts/search.py
```

## 사용법

### 기본 검색

```bash
./scripts/search.py "검색어"
```

### 고급 옵션

```bash
# 플랫폼당 5개씩, 네이버만 검색
./scripts/search.py "갤럭시 버즈" --platforms naver --display 5

# 최대 50만원까지, 가격순 정렬
./scripts/search.py "노트북" --max-price 500000 --sort price

# JSON 출력 (API 용도)
./scripts/search.py "아이폰" --json
```

### 옵션 설명

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `--display` | 플랫폼당 결과 수 (1-10) | 3 |
| `--platforms` | 검색 플랫폼 (naver,coupang,11st) | 전체 |
| `--sort` | 정렬 기준 (price, review) | price |
| `--max-price` | 최대 가격 필터 (원) | 없음 |
| `--json` | JSON 형식 출력 | 텍스트 |

## 출력 예시

```
🔍 검색 결과: 9개 상품

🛒 [쿠팡] 갤럭시 버즈2 프로 그래파이트
   💰 155,000원 (배송비 무료) = 총 155,000원 ⭐ 최저가!
   🚀 로켓배송
   🔗 https://www.coupang.com/...

🛍️ [네이버쇼핑] 삼성전자 갤럭시버즈2 프로
   💰 159,000원 (배송비 무료) = 총 159,000원
   🏪 G마켓
   🔗 https://shopping.naver.com/...

🏬 [11번가] 갤럭시 버즈2 프로 SM-R510
   💰 158,900원 (배송비 2,500원) = 총 161,400원
   🔗 https://www.11st.co.kr/...
```

## 기술 스택

- **Python 3.7+**
- **requests**: HTTP 클라이언트
- **BeautifulSoup4**: HTML 파싱
- **lxml**: XML/HTML 파서
- **urllib**: 네이버 API 호출

## 제한사항

⚠️ **웹 스크래핑 관련**
- 쿠팡/11번가는 사이트 구조 변경 시 동작하지 않을 수 있습니다
- 과도한 요청 시 IP 차단 가능성이 있습니다
- 로그인이 필요한 정보는 수집할 수 없습니다

⚠️ **배송비 정보**
- 네이버 API는 배송비 정보를 제공하지 않습니다
- 쿠팡/11번가 배송비는 일반 상품 기준으로 추정됩니다
- 실제 배송비는 상품 페이지에서 확인하세요

## 개발자 정보

- **스킬 이름**: naver-shopping-plus
- **버전**: 1.0.0
- **제작**: OpenClaw Agent
- **라이선스**: MIT

## 문제 해결

### "의존성 설치 필요" 에러

```bash
pip install requests beautifulsoup4 lxml
```

### "네이버 API 에러"

`.env` 파일에 올바른 API 키가 있는지 확인:
```bash
echo $NAVER_Client_ID
echo $NAVER_Client_Secret
```

### 웹 스크래핑 에러

사이트 구조가 변경되었을 가능성이 있습니다. 이슈 리포트 부탁드립니다.

## 업데이트 계획

- [ ] 네이버 스마트스토어 직접 스크래핑 (배송비 정보 수집)
- [ ] 쿠팡 API 연동 (공식 API 사용 시)
- [ ] 옥션/G마켓 추가
- [ ] 리뷰 수/평점 기반 정렬
- [ ] 가격 히스토리 추적

## 기여

버그 리포트나 기능 제안은 환영합니다!
