---
name: korean-invoice
description: 한국형 견적서/세금계산서 자동 생성 (사업자등록번호, 부가세 자동 계산)
version: 1.0.0
author: 무펭이 🐧
---

# korean-invoice

**한국형 견적서/세금계산서 생성기** — 한국 표준 양식으로 견적서와 세금계산서를 자동 생성. 사업자등록번호, 공급가액, 부가세 자동 계산 지원.

## 언제 사용하나요?

- 고객에게 견적서 발송
- 세금계산서 발행
- 거래처 정보 관리
- 자주 쓰는 품목 DB 관리
- PDF/HTML 형식으로 출력

## 빠른 시작

```bash
# 견적서 생성 (대화형)
korean-invoice quote

# 거래처 저장된 경우
korean-invoice quote --client "무펭이즘"

# 세금계산서 생성
korean-invoice tax --client "무펭이즘"

# 거래처 추가
korean-invoice client add "무펭이즘" --business-number "123-45-67890" --ceo "김형님"

# 품목 추가
korean-invoice item add "포토부스 대여" --price 500000 --unit "일"

# 거래처 목록
korean-invoice client list

# 품목 목록
korean-invoice item list
```

## 견적서 필드

| 필드 | 설명 | 필수 |
|------|------|------|
| client | 거래처명 (저장된 거래처 ID) | ✅ |
| items | 품목 리스트 (품목명, 수량, 단가) | ✅ |
| issueDate | 작성일자 (기본: 오늘) | ❌ |
| validUntil | 유효기간 (기본: +30일) | ❌ |
| notes | 비고 | ❌ |
| includeVAT | 부가세 포함 여부 (기본: true) | ❌ |

## 세금계산서 필드

| 필드 | 설명 | 필수 |
|------|------|------|
| client | 공급받는자 (거래처 ID) | ✅ |
| items | 품목 리스트 | ✅ |
| issueDate | 작성일자 | ✅ |
| type | 영수/청구 (기본: 영수) | ❌ |
| notes | 비고 | ❌ |

## 자동 계산

```
공급가액:     500,000 원
부가세(10%):   50,000 원
합계:         550,000 원
```

- 공급가액 입력 시 부가세 10% 자동 계산
- 총액 입력 시 역산 (총액 ÷ 1.1)
- 품목별 소계 자동 합산

## 거래처 관리

```bash
# 거래처 추가
korean-invoice client add "무펭이즘" \
  --business-number "123-45-67890" \
  --ceo "김형님" \
  --address "서울시 강남구..." \
  --phone "010-1234-5678" \
  --email "contact@mufism.com"

# 거래처 수정
korean-invoice client edit "무펭이즘" --phone "010-9999-9999"

# 거래처 삭제
korean-invoice client remove "무펭이즘"

# 거래처 상세 조회
korean-invoice client view "무펭이즘"
```

거래처 데이터는 `data/clients.json`에 저장됩니다.

## 품목 관리

```bash
# 품목 추가
korean-invoice item add "포토부스 대여" --price 500000 --unit "일"

# 품목 수정
korean-invoice item edit "포토부스 대여" --price 600000

# 품목 삭제
korean-invoice item remove "포토부스 대여"

# 품목 목록
korean-invoice item list
```

품목 데이터는 `data/items.json`에 저장됩니다.

## 템플릿

### 견적서 템플릿
- 공급자 정보 (사업자등록번호, 상호, 대표자, 주소, 연락처)
- 공급받는자 정보
- 작성일자, 유효기간
- 품목 테이블 (품명, 규격, 수량, 단가, 공급가액)
- 합계 (공급가액, 부가세, 총액)
- 비고

### 세금계산서 템플릿
- 승인번호 (임의 생성)
- 공급자/공급받는자 정보 (사업자등록번호, 상호, 성명, 주소)
- 작성일자
- 품목 테이블
- 합계 (공급가액, 세액)
- 영수/청구 구분

## 출력 형식

- **HTML**: 브라우저에서 바로 확인
- **PDF**: HTML → PDF 변환 (puppeteer 사용)
- 저장 경로: `output/YYYY-MM-DD-{type}-{client}.pdf`

## 내 정보 설정

내 사업자 정보는 `data/my-info.json`에 저장:

```json
{
  "businessNumber": "123-45-67890",
  "companyName": "무펭이즘",
  "ceo": "김무펭",
  "address": "서울시 강남구...",
  "phone": "010-1234-5678",
  "email": "contact@mufism.com",
  "bankAccount": "우리은행 1002-123-456789"
}
```

## 사용 예시

### 1. 간단한 견적서 생성
```bash
korean-invoice quote \
  --client "무펭이즘" \
  --items "포토부스 대여,2,500000" \
  --notes "부가세 별도"
```

### 2. 저장된 품목 사용
```bash
# 품목 미리 저장
korean-invoice item add "포토부스 대여" --price 500000 --unit "일"
korean-invoice item add "출장비" --price 100000 --unit "회"

# 품목 ID로 견적서 생성
korean-invoice quote --client "무펭이즘" --item-ids "포토부스 대여,출장비"
```

### 3. 세금계산서 발행
```bash
korean-invoice tax --client "무펭이즘" --items "포토부스 대여,1,500000" --type 영수
```

## 통합

- `message` 스킬과 연동하여 이메일/Discord로 전송
- `daily-report`에서 작업 시간 → 견적서 변환
- `calendar` 스킬로 유효기간 알림 설정

## 주의사항

- 사업자등록번호는 `123-45-67890` 형식으로 입력
- 금액은 원 단위로 입력 (콤마 없이 숫자만)
- PDF 생성은 OpenClaw 브라우저가 실행중이어야 함
