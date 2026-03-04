---
name: unified-invoice
description: 통합 견적서/세금계산서 생성기. 한국형 견적서(사업자등록번호, 부가세) + 프리랜서 인보이스(다국어, VAT). 거래처/품목 DB, PDF 출력, 자동 계산.
version: 1.0.0
author: 무펭이 🐧
---

# Unified Invoice Generator 📄🐧

> **통합됨**: 기존 `invoice-gen`, `korean-invoice` 스킬을 통합

한국형 견적서/세금계산서 + 프리랜서 인보이스를 하나로.

## 주요 기능

- 📋 **한국형 견적서**: 사업자등록번호, 공급가액, 부가세 자동 계산
- 🧾 **세금계산서**: 영수/청구 구분, 승인번호 생성
- 💼 **프리랜서 인보이스**: Markdown/PDF, 다국어 지원 (KRW/USD/EUR)
- 🏢 **거래처 관리**: 사업자 정보, 연락처 DB
- 📦 **품목 관리**: 자주 쓰는 품목 저장 및 재사용
- 📄 **PDF 출력**: HTML → PDF 자동 변환
- 🔢 **자동 계산**: 공급가액, 부가세, 총액 자동 계산

## 빠른 시작

### 한국형 견적서 생성

```bash
node scripts/generate.js quote \
  --client "무펭이즘" \
  --items "포토부스 대여,2,500000" \
  --notes "부가세 별도"
```

### 세금계산서 생성

```bash
node scripts/generate.js tax \
  --client "무펭이즘" \
  --items "포토부스 대여,1,500000" \
  --type 영수
```

### 프리랜서 인보이스 (영문)

```bash
node scripts/generate.js invoice \
  --client "Acme Corp" \
  --items "Web development,40h,50" \
  --currency USD \
  --lang en
```

## 문서 타입

| 타입 | 설명 | 용도 |
|------|------|------|
| `quote` | 한국형 견적서 | 고객에게 견적 제시 |
| `tax` | 세금계산서 | 부가세 신고용 정식 세금계산서 |
| `invoice` | 프리랜서 인보이스 | 국제 거래, 프리랜서 작업 |

## 견적서 필드

| 필드 | 설명 | 필수 | 기본값 |
|------|------|------|--------|
| `--client` | 거래처명 또는 ID | ✅ | - |
| `--items` | 품목 리스트 (품명,수량,단가) | ✅ | - |
| `--issue-date` | 작성일자 | ❌ | 오늘 |
| `--valid-until` | 유효기간 | ❌ | +30일 |
| `--notes` | 비고 | ❌ | - |
| `--include-vat` | 부가세 포함 여부 | ❌ | true |
| `--currency` | 통화 (KRW/USD/EUR) | ❌ | KRW |
| `--lang` | 언어 (ko/en) | ❌ | ko |

## 세금계산서 필드

| 필드 | 설명 | 필수 | 기본값 |
|------|------|------|--------|
| `--client` | 공급받는자 (거래처 ID) | ✅ | - |
| `--items` | 품목 리스트 | ✅ | - |
| `--issue-date` | 작성일자 | ✅ | - |
| `--type` | 영수/청구 | ❌ | 영수 |
| `--notes` | 비고 | ❌ | - |

## 자동 계산

### 한국형 (부가세 10%)

```
공급가액:     500,000 원
부가세(10%):   50,000 원
합계:         550,000 원
```

- 공급가액 입력 시 부가세 10% 자동 추가
- 총액 입력 시 역산 (총액 ÷ 1.1)
- 품목별 소계 자동 합산

### 프리랜서 (VAT + Withholding)

```
Subtotal:      $2,000
VAT (10%):       $200
Withholding:    -$66  (3.3% for Korean freelance)
Total:        $2,134
```

- 국가별 세율 커스터마이징 가능
- 원천징수세 자동 계산 (한국 프리랜서 3.3%)

## 거래처 관리

```bash
# 거래처 추가
node scripts/manage-clients.js add "무펭이즘" \
  --business-number "123-45-67890" \
  --ceo "김형님" \
  --address "서울시 강남구..." \
  --phone "010-1234-5678" \
  --email "contact@mufism.com"

# 거래처 목록
node scripts/manage-clients.js list

# 거래처 상세 조회
node scripts/manage-clients.js view "무펭이즘"

# 거래처 수정
node scripts/manage-clients.js edit "무펭이즘" --phone "010-9999-9999"

# 거래처 삭제
node scripts/manage-clients.js remove "무펭이즘"
```

거래처 데이터: `data/clients.json`

## 품목 관리

```bash
# 품목 추가
node scripts/manage-items.js add "포토부스 대여" \
  --price 500000 \
  --unit "일"

# 품목 목록
node scripts/manage-items.js list

# 품목 수정
node scripts/manage-items.js edit "포토부스 대여" --price 600000

# 품목 삭제
node scripts/manage-items.js remove "포토부스 대여"
```

품목 데이터: `data/items.json`

저장된 품목 사용:
```bash
node scripts/generate.js quote \
  --client "무펭이즘" \
  --item-ids "포토부스 대여,출장비"
```

## 템플릿

### 한국형 견적서 (`templates/quote.html`)
- 공급자 정보 (사업자등록번호, 상호, 대표자, 주소, 연락처)
- 공급받는자 정보
- 작성일자, 유효기간
- 품목 테이블 (품명, 규격, 수량, 단가, 공급가액)
- 합계 (공급가액, 부가세, 총액)
- 비고

### 세금계산서 (`templates/tax-invoice.html`)
- 승인번호 (임의 생성)
- 공급자/공급받는자 정보 (사업자등록번호, 상호, 성명, 주소)
- 작성일자
- 품목 테이블
- 합계 (공급가액, 세액)
- 영수/청구 구분

### 프리랜서 인보이스 (Markdown)
- Professional layout
- Sender/receiver info
- Itemized table with subtotals
- Tax calculation
- Payment terms and bank details
- Auto-incremented invoice number (INV-YYYY-NNN)

커스텀 템플릿 생성:
```bash
cp templates/quote.html templates/my-custom.html
# 수정 후
node scripts/generate.js quote --template my-custom ...
```

## 출력 형식

- **HTML**: 브라우저에서 바로 확인
- **PDF**: HTML → PDF 변환 (OpenClaw 브라우저 필요)
- **Markdown**: 프리랜서 인보이스 (편집 가능)

저장 경로: `output/YYYY-MM-DD-{type}-{client}.{html|pdf|md}`

## 내 정보 설정

`data/my-info.json`:

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

프리랜서 정보 (영문):
```json
{
  "name": "John Doe",
  "email": "john@freelancer.com",
  "address": "123 Main St, New York, NY 10001",
  "phone": "+1-555-1234",
  "bankAccount": "Bank of America, Account #12345678"
}
```

## 사용 예시

### 1. 한국 고객에게 견적서

```bash
# 거래처 미리 저장
node scripts/manage-clients.js add "무펭이즘" \
  --business-number "123-45-67890" \
  --ceo "김형님"

# 품목 미리 저장
node scripts/manage-items.js add "포토부스 대여" --price 500000 --unit "일"
node scripts/manage-items.js add "출장비" --price 100000 --unit "회"

# 견적서 생성
node scripts/generate.js quote \
  --client "무펭이즘" \
  --item-ids "포토부스 대여,출장비" \
  --notes "부가세 별도"
```

### 2. 세금계산서 발행

```bash
node scripts/generate.js tax \
  --client "무펭이즘" \
  --items "포토부스 대여,1,500000" \
  --type 영수 \
  --issue-date 2026-02-18
```

### 3. 해외 고객 인보이스

```bash
node scripts/generate.js invoice \
  --client "Acme Corp" \
  --items "Web development,40h,50" \
  --currency USD \
  --lang en \
  --notes "Payment due within 30 days"
```

## 통합 기능

- **message 스킬**: 이메일/Discord로 견적서 전송
- **daily-report**: 작업 시간 → 인보이스 자동 변환
- **calendar**: 유효기간/납기일 알림 설정
- **trello/notion**: 견적서 발행 → 태스크 자동 생성

## 설치

```bash
cd skills/unified-invoice
npm install
```

## 주의사항

- **사업자등록번호**: `123-45-67890` 형식 (하이픈 포함)
- **금액**: 원 단위 숫자만 입력 (콤마 없이)
- **PDF 생성**: OpenClaw 브라우저 실행 필요 (포트 18800)
- **템플릿 수정**: HTML 파일 직접 편집 가능
- **다국어**: `--lang en` 옵션으로 영문 출력

## 트러블슈팅

**PDF 생성 실패:**
- OpenClaw 브라우저 실행 확인 (`openclaw gateway status`)
- 포트 18800 접근 가능 확인

**거래처/품목 로드 안 됨:**
- `data/clients.json`, `data/items.json` 파일 존재 확인
- JSON 문법 오류 확인

**부가세 계산 오류:**
- `--include-vat false` 옵션으로 부가세 제외 가능
- 수동 계산 필요 시 `--items "품명,수량,공급가액"` 입력

## 디렉토리 구조

```
unified-invoice/
├── SKILL.md                      # 이 파일
├── package.json
├── scripts/
│   ├── generate.js               # 견적서/세금계산서/인보이스 생성
│   ├── manage-clients.js         # 거래처 관리
│   └── manage-items.js           # 품목 관리
├── templates/
│   ├── quote.html                # 한국형 견적서
│   ├── tax-invoice.html          # 세금계산서
│   └── freelance-invoice.md      # 프리랜서 인보이스 (Markdown)
├── data/
│   ├── clients.json              # 거래처 DB
│   ├── items.json                # 품목 DB
│   └── my-info.json              # 내 사업자 정보
└── output/                       # 생성된 문서 저장
```

## 통합 히스토리

| 원본 스킬 | 기여 내용 | 통합 날짜 |
|----------|----------|----------|
| korean-invoice | 한국형 견적서/세금계산서, 사업자등록번호, HTML 템플릿 | 2026-02-18 |
| invoice-gen | 프리랜서 인보이스, Markdown 템플릿, 다국어 지원 | 2026-02-18 |

---
> 🐧 Built by **무펭이** — [무펭이즘(Mupengism)](https://github.com/mupeng) 생태계 스킬
