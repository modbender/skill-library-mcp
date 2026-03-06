---
name: molit-real-estate
description: MOLIT apartment real transaction price API
version: 2.2.0
author: chumjibot
created: 2026-02-10
updated: 2026-02-19
tags: [real-estate, korea, openapi, data.go.kr]
connectors: [~~realestate, ~~law, ~~search, ~~notify]
---

# Real Estate Transaction Skill

MOLIT apartment sale transaction data + law integration.

## Overview

| Key | Value |
|-----|-------|
| Provider | MOLIT (Ministry of Land, Infrastructure and Transport) |
| Service ID | 15126469 |
| Auth | `~/.config/data-go-kr/api_key` |
| Endpoint | `https://apis.data.go.kr/1613000/RTMSDataSvcAptTrade` |
| Legal basis | Real Estate Transaction Report Act |
| Playbook | `playbook.md` |

## Scripts

```
scripts/
└── real_estate.sh [district_code] [YYYYMM] [rows]
```

## Workflow

### Step 1: Identify district & period
- "강남 아파트" → Gangnam-gu (11680), current month
- Refer to `playbook.md` for watchlist areas
- Default: current month; if empty, try recent 3 months

### Step 2: Fetch transaction data
- `real_estate.sh [code] [YYYYMM]`

### Step 3: Analyze
- Price per pyeong (area ÷ 3.3058)
- YoY comparison (on request)
- ~~search for market trend supplement

### Step 4: Law integration (~~law, optional)
- Rental disputes → Housing Lease Protection Act
- Sales → Real Estate Transaction Report Act

### Step 5: Structured response

## Output Template

```markdown
## 🏠 [District] Apartment Transactions

### Recent Transactions
| Apt | Area | Floor | Price | Per Pyeong | Date |
|-----|------|-------|-------|-----------|------|

### 📊 Summary
- Avg price: X억
- Avg per pyeong: X만/평
- Total transactions: X

### 💡 Notes
[Trend / related law info]
```

## Key District Codes (Seoul)

| District | Code | District | Code |
|----------|------|----------|------|
| Jongno | 11110 | Mapo | 11440 |
| Yongsan | 11170 | Gangnam | 11680 |
| Seocho | 11650 | Songpa | 11710 |
| Gangdong | 11740 | Yeongdeungpo | 11560 |
| Seongdong | 11200 | Gwanak | 11620 |

### Other Cities
| District | Code |
|----------|------|
| Busan Haeundae | 26350 |
| Daegu Suseong | 27200 |
| Incheon Yeonsu | 28185 |
| Daejeon Yuseong | 30200 |

## Response Fields (XML → English keys since 2026)

| Key | Description |
|-----|-------------|
| aptNm | Apartment name |
| umdNm | District name |
| excluUseAr | Exclusive area (㎡) |
| floor | Floor |
| dealAmount | Price (만원, comma-separated) |
| dealYear/Month/Day | Transaction date |
| dealingGbn | Transaction type |
| buildYear | Year built |

## Connectors

| Placeholder | Purpose | Current Tool |
|-------------|---------|-------------|
| `~~realestate` | Transaction API | MOLIT data.go.kr |
| `~~law` | Legal references | law.go.kr |
| `~~search` | Trend supplement | Brave Search |
| `~~notify` | Alerts | Telegram |

## Intent Router

| # | Intent | Trigger Expression | Output |
|---|--------|--------------------|--------|
| 1 | Price Check | "강남 아파트 실거래가", "최근 거래 보여줘" | Transaction list + summary |
| 2 | Trend Analysis | "송파 시세 추이", "6개월간 가격 변화" | Multi-month comparison |
| 3 | Area Comparison | "강남 vs 서초 비교", "강남3구 어디가 비싸?" | Side-by-side district table |

Details: see Workflow above.

## Cross-Skill Integration

| Trigger | Partner Skill | How |
|---------|---------------|-----|
| "관련 법률도", 임대차/전세 분쟁 | `law-search` (~~law) | 주택임대차보호법, 부동산거래신고법 검색 |
| "주변 환경도", 입지 분석 | `kma-weather` (~~weather) | 해당 지역 기후/환경 데이터 보강 |
| "투자 관점에서" | `finance-sector-analysis` | 부동산 섹터(XLRE) 분석 연동 |

### Cross-Skill: Real Estate + Legal Context
1. `real_estate.sh` → transaction data
2. `law-search` → 관련 법률 (주택임대차보호법, 부동산거래신고법 등) (via ~~law)
3. Append legal references to report

### Cross-Skill: Real Estate + Location Environment
1. `real_estate.sh` → transaction data
2. `kma-weather` → 지역 기후/미세먼지 데이터 (via ~~weather)
3. Add environmental context to area comparison

## Notes
1. District code: 5 digits (시군구 level)
2. Contract month: YYYYMM format
3. dealAmount contains commas → parse as string
4. Data delay: 1-2 months after actual transaction
5. Pagination: increase pageNo for large datasets

---
*Cowork architecture v2.2 — 🦞 chumjibot (2026-02-19)*

## 🔧 Setup (공공데이터 포털 API)

1. [data.go.kr](https://www.data.go.kr) 회원가입
2. 로그인 → 마이페이지 → **일반 인증키(Decoding)** 복사
3. API 키 저장:
   ```bash
   mkdir -p ~/.config/data-go-kr
   echo "YOUR_API_KEY" > ~/.config/data-go-kr/api_key
   ```
4. 아래 서비스 **활용신청** 후 사용 (자동승인)
   - [국토부 아파트매매 실거래가](https://www.data.go.kr/data/15057511/openapi.do) (15057511)
