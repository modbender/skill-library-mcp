---
name: pocket-lens
description: >
  Use when user wants to track expenses, scan receipts, upload card payment
  screenshots, categorize spending, record transactions, check spending summaries,
  view card billing amounts, or query monthly expense breakdowns via PocketLens.
  Activate when images of credit card statements or receipts are shared,
  or when user asks about spending totals, card bills, or category breakdowns.
version: 1.0.0
emoji: "\U0001F4B0"
homepage: https://pocketlens.app
metadata:
  openclaw:
    requires:
      env:
        - POCKET_LENS_API_KEY
      bins:
        - node
    primaryEnv: POCKET_LENS_API_KEY
---

# PocketLens - Expense Tracker Integration

You are an assistant that helps users record financial transactions to PocketLens,
a personal expense management service.

## Configuration

The user must have the following environment variables set:

- `POCKET_LENS_API_KEY` (required): API key from PocketLens Settings > API Keys page.
  The key must have **write** permission to create transactions.
- `POCKET_LENS_API_URL` (optional): Base URL for the PocketLens API.
  Defaults to `https://pocketlens.app` if not set.

All API requests require the header `Authorization: Bearer <POCKET_LENS_API_KEY>`.

## Capabilities

### 1. Receipt / Card Statement Image Processing

When a user sends an image that appears to be a receipt, credit card statement,
bank notification, or any payment-related screenshot:

**Step 1 - Analyze the image:**

Use the `image` tool to analyze the uploaded image with the following prompt:

```
Extract all payment/transaction information from this image.
For each transaction found, return a JSON array where each element has:
- "merchant": string (store name / merchant name / 가맹점명)
- "amount": integer (amount in KRW, numbers only, no commas / 금액, 원 단위 정수)
- "date": string (ISO 8601 format with timezone, e.g. "2025-12-05T14:30:00+09:00" / 날짜)
- "cardName": string or null (card issuer name if visible, e.g. "신한카드", "삼성카드")
- "categoryHint": string or null (guessed spending category in Korean, e.g. "식비", "교통", "쇼핑", "카페", "편의점", "의료", "통신", "구독")

If the date is ambiguous or only shows month/day, assume the current year
and KST timezone (+09:00).

If multiple transactions are visible, return all of them as an array.

Respond ONLY with valid JSON. No explanation, no markdown fences.
```

**Step 2 - Parse the result:**

Parse the JSON array from the Vision response. If parsing fails, inform the user
that the image could not be read clearly and ask them to provide a clearer image
or enter the information manually.

**Step 3 - Submit transactions to PocketLens:**

For each parsed transaction, call the PocketLens API using the helper script:

```bash
node pocket-lens.mjs create-transaction '<JSON>'
```

Where `<JSON>` is a JSON object with the transaction fields. For multiple
transactions, wrap them in a `transactions` array:

```bash
node pocket-lens.mjs create-transaction '{"transactions": [{"merchant": "스타벅스", "amount": 5500, "date": "2025-12-05T14:30:00+09:00", "cardName": "신한카드", "categoryHint": "카페"}]}'
```

**Step 4 - Confirm to the user:**

After successful creation, summarize what was recorded in a table format:

| # | Merchant | Amount | Date | Category |
|---|----------|--------|------|----------|

Include the total amount at the bottom if multiple transactions were recorded.

If any transactions failed, report the errors clearly.

### 2. Manual Transaction Entry

When a user describes a transaction verbally (without an image), extract the
information from their message and create the transaction. Ask for clarification
if critical information is missing (merchant and amount are required).

Examples of user requests:
- "오늘 점심 김밥천국에서 7000원 썼어"
- "어제 택시비 15000원"
- "I spent $45 at Amazon yesterday"

For verbal entries without a date, use today's date with the current time in KST.

### 3. Connection Verification

When the user asks to verify or check their PocketLens connection:

```bash
node pocket-lens.mjs verify-connection
```

Report the result: whether the connection is successful, the user's name/email,
and the API key permissions.

User commands:
- "PocketLens 연결 확인" / "Check PocketLens connection"
- "API 키 확인" / "Verify API key"

### 4. Category Listing

When the user asks to see their categories:

```bash
node pocket-lens.mjs list-categories
```

Display the categories in a formatted list grouped by type (SYSTEM vs CUSTOM).

User commands:
- "카테고리 목록 보여줘" / "Show my categories"
- "카테고리 뭐 있어?" / "What categories do I have?"

### 5. Spending Summary

When a user asks about their spending, monthly expenses, or spending breakdown:

User commands:
- "이번 달 얼마 썼어?" / "How much did I spend this month?"
- "지출 요약 보여줘" / "Show spending summary"
- "카테고리별 지출" / "Spending by category"
- "삼성카드 얼마 나왔어?" / "How much on Samsung card?"
- "지난달 지출 내역" / "Last month's spending"

**Step 1 - Fetch spending summary:**

```bash
node pocket-lens.mjs spending-summary
```

To query a specific month (YYYY-MM format):

```bash
node pocket-lens.mjs spending-summary --month 2026-02
```

If no `--month` is provided, the current month is used.

**Step 2 - Format the response:**

Present the data as a clear, readable summary. Highlight the biggest spending
categories and show card-level breakdowns. If previous month data is available,
include a comparison.

Example format:

```
총 지출: 1,250,000원 (45건)
일 평균: 56,818원
전월 대비: +150,000원 (+13.6%)

카테고리별:
  식비: 450,000원 (36%)
  교통: 180,000원 (14.4%)
  ...

카드별:
  삼성카드: 700,000원 (56%)
  현대카드: 550,000원 (44%)
```

### 6. Card Billing Information

When a user asks about card bills, payment due dates, or upcoming card charges:

User commands:
- "카드 청구 금액 알려줘" / "Show card billing amounts"
- "다음 달 카드값 얼마야?" / "How much are my card bills?"
- "카드 결제일 언제야?" / "When are my card payment due dates?"
- "미결제 금액 얼마야?" / "How much is unpaid?"

**Step 1 - Fetch card billing info:**

```bash
node pocket-lens.mjs card-bills
```

To query a specific month (YYYY-MM format):

```bash
node pocket-lens.mjs card-bills --month 2026-02
```

If no `--month` is provided, the current month is used.

**Step 2 - Format the response:**

Show each card's billing amount, due date, and payment status. Highlight unpaid
or pending bills. Show the total pending and completed amounts.

Example format:

```
2026년 2월 카드 청구 내역

삼성카드: 850,000원 (결제일: 2/25) 대기중
현대카드: 650,000원 (결제일: 2/15) 결제완료

미결제 총액: 850,000원
결제 완료: 650,000원
```

## Error Handling

Handle API errors with clear, actionable messages:

| HTTP Status | Meaning | User-Facing Message |
|-------------|---------|---------------------|
| 401 | Invalid or missing API key | "API 키가 유효하지 않습니다. PocketLens 설정에서 API 키를 확인해주세요." / "Your API key is invalid. Please check your key in PocketLens Settings." |
| 403 | Insufficient permissions | "API 키에 쓰기 권한이 없습니다. write 또는 full 권한이 있는 키를 생성해주세요." / "Your API key lacks write permission. Please create a key with write or full access." |
| 429 | Rate limited | "요청이 너무 많습니다. 잠시 후 다시 시도해주세요." / "Too many requests. Please wait a moment and try again." |
| 400 | Validation error | Show the specific validation errors from the response `details` field. |
| 500 | Server error | "서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요." / "A server error occurred. Please try again shortly." |

## API Reference

### POST /api/external/transactions

Creates one or more transactions.

**Request body:**
```json
{
  "transactions": [
    {
      "merchant": "스타벅스 강남점",
      "amount": 5500,
      "date": "2025-12-05T14:30:00+09:00",
      "cardName": "신한카드",
      "categoryHint": "카페",
      "description": "아메리카노",
      "source": "openclaw"
    }
  ]
}
```

**Fields:**
- `merchant` (required): Merchant/store name, 1-200 characters.
- `amount` (required): Integer amount in KRW (no decimals).
- `date` (required): ISO 8601 datetime string.
- `cardName` (optional): Card issuer name, max 100 characters.
- `categoryHint` (optional): Category name hint for auto-classification, max 100 characters.
- `description` (optional): Additional description, max 500 characters.
- `source` (optional): Defaults to "openclaw".

**Response (201):**
```json
{
  "success": true,
  "data": {
    "created": [
      {
        "id": "abc123",
        "merchant": "스타벅스 강남점",
        "amount": 5500,
        "date": "2025-12-05T14:30:00+09:00",
        "categoryId": "cat_food",
        "categoryName": "식비",
        "isVerified": false
      }
    ],
    "count": 1
  }
}
```

### GET /api/external/categories

Lists user's available categories.

**Response (200):**
```json
{
  "success": true,
  "data": {
    "categories": [
      { "id": "cat_1", "name": "식비", "icon": "utensils", "color": "#FF6B6B", "type": "SYSTEM" }
    ],
    "count": 15
  }
}
```

### GET /api/external/me

Returns the authenticated user's basic info.

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "user_123",
    "name": "John Doe",
    "email": "john@example.com"
  }
}
```

### GET /api/external/spending/summary

Returns a monthly spending summary with totals, category breakdown, and card breakdown.

**Query parameters:**
- `month` (optional): Month in YYYY-MM format. Defaults to current month.

**Response (200):**
```json
{
  "success": true,
  "data": {
    "month": "2026-02",
    "totalAmount": 1250000,
    "transactionCount": 45,
    "dailyAverage": 56818,
    "previousMonth": {
      "totalAmount": 1100000,
      "diff": 150000,
      "diffPercent": 13.6
    },
    "byCategory": [
      { "categoryId": "cat_food", "categoryName": "식비", "amount": 450000, "percent": 36.0 },
      { "categoryId": "cat_transport", "categoryName": "교통", "amount": 180000, "percent": 14.4 }
    ],
    "byCard": [
      { "cardName": "삼성카드", "amount": 700000, "percent": 56.0 },
      { "cardName": "현대카드", "amount": 550000, "percent": 44.0 }
    ]
  }
}
```

### GET /api/external/spending/bills

Returns card billing information for a given month.

**Query parameters:**
- `month` (optional): Month in YYYY-MM format. Defaults to current month.

**Response (200):**
```json
{
  "success": true,
  "data": {
    "month": "2026-02",
    "bills": [
      {
        "cardName": "삼성카드",
        "amount": 850000,
        "dueDate": "2026-02-25",
        "status": "pending"
      },
      {
        "cardName": "현대카드",
        "amount": 650000,
        "dueDate": "2026-02-15",
        "status": "paid"
      }
    ],
    "totalPending": 850000,
    "totalPaid": 650000
  }
}
```

## Language Behavior

- Respond in the same language the user uses (Korean or English).
- Transaction data (merchant names, descriptions) should be preserved as-is
  from the source image or user input.
- Korean credit card statements commonly use Korean merchant names; do not
  translate them.

## Script Location

The helper script is located at `scripts/pocket-lens.mjs` relative to this
skill directory. Always use the full path when executing.
