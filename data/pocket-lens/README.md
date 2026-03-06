# PocketLens Skill for OpenClaw

> Scan receipts and card statements with AI, then automatically record transactions to PocketLens.
>
> AI로 영수증과 카드 명세서를 스캔하고, PocketLens에 자동으로 거래를 기록합니다.

---

## Prerequisites / 사전 준비

- A [PocketLens](https://pocketlens.app) account with at least one active subscription.
- [OpenClaw](https://openclaw.ai) installed and running.
- Node.js 18 or later (for the helper script).

---

- [PocketLens](https://pocketlens.app) 계정 (활성 구독 필요)
- [OpenClaw](https://openclaw.ai) 설치 및 실행 중
- Node.js 18 이상 (헬퍼 스크립트 실행용)

---

## 1. Generate an API Key / API 키 발급

1. Log in to [PocketLens](https://pocketlens.app).
2. Go to **Settings > API Keys**.
3. Click **Create New Key**.
4. Set the permission to **write** (or **full**).
5. Copy the generated key (starts with `pk_`).

---

1. [PocketLens](https://pocketlens.app)에 로그인합니다.
2. **설정 > API 키**로 이동합니다.
3. **새 키 생성**을 클릭합니다.
4. 권한을 **write** (또는 **full**)로 설정합니다.
5. 생성된 키를 복사합니다 (`pk_`로 시작).

---

## 2. Install the Skill / 스킬 설치

### Option A: ClawHub (Recommended)

```bash
clawhub install pocket-lens
```

### Option B: Manual Installation

Copy the `openclaw-skill/` directory into your OpenClaw skills folder:

```bash
cp -r openclaw-skill/ ~/.openclaw/skills/pocket-lens/
```

---

### Option A: ClawHub (권장)

```bash
clawhub install pocket-lens
```

### Option B: 수동 설치

`openclaw-skill/` 디렉토리를 OpenClaw 스킬 폴더에 복사합니다:

```bash
cp -r openclaw-skill/ ~/.openclaw/skills/pocket-lens/
```

---

## 3. Configuration / 설정

Set the following environment variables in your OpenClaw configuration:

| Variable | Required | Description |
|----------|----------|-------------|
| `POCKET_LENS_API_KEY` | Yes | Your PocketLens API key (`pk_...`) |
| `POCKET_LENS_API_URL` | No | API base URL (default: `https://pocketlens.app`) |

### Example: `.env` file

```env
POCKET_LENS_API_KEY=pk_your_api_key_here
POCKET_LENS_API_URL=https://pocketlens.app
```

### Example: OpenClaw config

If OpenClaw supports environment configuration in its settings UI, add the
variables there. Otherwise, export them in your shell profile:

```bash
export POCKET_LENS_API_KEY="pk_your_api_key_here"
```

---

OpenClaw 설정에서 다음 환경변수를 설정합니다:

| 변수 | 필수 | 설명 |
|------|------|------|
| `POCKET_LENS_API_KEY` | 예 | PocketLens API 키 (`pk_...`) |
| `POCKET_LENS_API_URL` | 아니오 | API 기본 URL (기본값: `https://pocketlens.app`) |

### 예시: `.env` 파일

```env
POCKET_LENS_API_KEY=pk_여기에_API_키_입력
POCKET_LENS_API_URL=https://pocketlens.app
```

---

## 4. Usage / 사용법

### Verify Connection / 연결 확인

Send a message to OpenClaw:

> "PocketLens 연결 확인해줘"

or

> "Check my PocketLens connection"

The assistant will verify your API key and display your account information.

---

### Scan a Receipt / 영수증 스캔

Upload an image of a receipt or card statement and say:

> "이 영수증 등록해줘"

or

> "Record this receipt"

The assistant will:
1. Analyze the image using Vision AI.
2. Extract merchant name, amount, date, and card info.
3. Submit the transactions to PocketLens.
4. Show a summary of what was recorded.

---

### Scan a Card Statement / 카드 명세서 스캔

Upload a screenshot of a credit card statement (e.g., from a banking app) and say:

> "이 결제 내역 입력해줘"

or

> "Log these payments"

The assistant will extract all visible transactions and record them in batch.

---

### Manual Entry / 수동 입력

You can also dictate transactions verbally:

> "오늘 점심 김밥천국에서 7000원 썼어"

> "어제 택시비 15000원"

> "I spent 45000 won at Olive Young today"

---

### View Categories / 카테고리 확인

> "카테고리 목록 보여줘"

or

> "Show my categories"

---

### Check Spending Summary / 지출 요약 확인

Ask about your monthly spending:

> "이번 달 얼마 썼어?"

or

> "Show this month's spending summary"

You can also ask about a specific month:

> "지난달 지출 요약 보여줘"

> "Show spending for January"

The assistant will show:
1. Total spending and transaction count.
2. Daily average and month-over-month comparison.
3. Breakdown by category and by card.

---

월간 지출에 대해 물어볼 수 있습니다:

> "이번 달 얼마 썼어?"

> "카테고리별 지출 알려줘"

특정 월을 조회할 수도 있습니다:

> "1월 지출 요약 보여줘"

어시스턴트가 다음 정보를 보여줍니다:
1. 총 지출액과 거래 건수
2. 일 평균 지출과 전월 대비 비교
3. 카테고리별, 카드별 지출 내역

---

### Check Card Bills / 카드 청구 확인

Ask about your card billing amounts:

> "카드 청구 금액 알려줘"

or

> "How much are my card bills this month?"

You can also ask about a specific month:

> "다음 달 카드값 얼마야?"

The assistant will show:
1. Each card's billing amount and due date.
2. Payment status (paid or pending).
3. Total pending and paid amounts.

---

카드 청구 금액을 물어볼 수 있습니다:

> "카드 청구 금액 알려줘"

> "다음 달 카드값 얼마야?"

어시스턴트가 다음 정보를 보여줍니다:
1. 카드별 청구 금액과 결제일
2. 결제 상태 (결제완료 또는 대기중)
3. 미결제 총액과 결제 완료 총액

---

## 5. Supported Image Types / 지원되는 이미지 유형

| Type | Examples |
|------|----------|
| Paper receipts | Restaurant bills, convenience store receipts, cafe receipts |
| Card statements | Monthly credit card statement screenshots |
| Banking app screenshots | Transaction notifications from banking apps |
| Digital receipts | Email or app order confirmations |

---

| 유형 | 예시 |
|------|------|
| 종이 영수증 | 음식점 계산서, 편의점 영수증, 카페 영수증 |
| 카드 명세서 | 월별 신용카드 명세서 스크린샷 |
| 뱅킹 앱 스크린샷 | 은행 앱 거래 알림 캡처 |
| 디지털 영수증 | 이메일 또는 앱 주문 확인서 |

---

## 6. Troubleshooting / 문제 해결

### "Invalid or missing API key" / "API 키가 유효하지 않습니다"

- Verify that `POCKET_LENS_API_KEY` is set correctly.
- Check that the key has not expired in PocketLens Settings.
- Make sure the key starts with `pk_`.

---

- `POCKET_LENS_API_KEY`가 올바르게 설정되었는지 확인합니다.
- PocketLens 설정에서 키가 만료되지 않았는지 확인합니다.
- 키가 `pk_`로 시작하는지 확인합니다.

---

### "Insufficient permissions" / "권한이 부족합니다"

- The API key must have **write** or **full** permission to create transactions.
- Go to PocketLens Settings > API Keys and create a new key with the correct permission.

---

- 거래를 생성하려면 API 키에 **write** 또는 **full** 권한이 필요합니다.
- PocketLens 설정 > API 키에서 올바른 권한으로 새 키를 생성하세요.

---

### "Network error" / "네트워크 오류"

- Check your internet connection.
- If using a custom `POCKET_LENS_API_URL`, verify the URL is correct and reachable.
- Make sure there is no firewall blocking the connection.

---

- 인터넷 연결을 확인합니다.
- 커스텀 `POCKET_LENS_API_URL`을 사용하는 경우 URL이 올바르고 접근 가능한지 확인합니다.
- 방화벽이 연결을 차단하지 않는지 확인합니다.

---

### Image not recognized / 이미지 인식 불가

- Make sure the image is clear and well-lit.
- Crop the image to show only the receipt/statement.
- For card statements, ensure the text is large enough to read.
- Try taking the photo from directly above (not at an angle).

---

- 이미지가 선명하고 밝은지 확인합니다.
- 영수증/명세서 부분만 보이도록 이미지를 자릅니다.
- 카드 명세서의 경우 텍스트가 읽을 수 있을 만큼 큰지 확인합니다.
- 비스듬하지 않고 바로 위에서 촬영해 보세요.

---

## 7. Testing the Script Directly / 스크립트 직접 테스트

You can test the helper script without OpenClaw:

```bash
# Set your API key
export POCKET_LENS_API_KEY="pk_your_key_here"

# Verify connection
node scripts/pocket-lens.mjs verify-connection

# List categories
node scripts/pocket-lens.mjs list-categories

# Create a test transaction
node scripts/pocket-lens.mjs create-transaction '{"transactions": [{"merchant": "Test Store", "amount": 1000, "date": "2025-12-05T12:00:00+09:00"}]}'

# Get spending summary for current month
node scripts/pocket-lens.mjs spending-summary

# Get spending summary for a specific month
node scripts/pocket-lens.mjs spending-summary --month 2026-01

# Get card bills for current month
node scripts/pocket-lens.mjs card-bills

# Get card bills for a specific month
node scripts/pocket-lens.mjs card-bills --month 2026-02
```

---

OpenClaw 없이 헬퍼 스크립트를 직접 테스트할 수 있습니다:

```bash
# API 키 설정
export POCKET_LENS_API_KEY="pk_여기에_키_입력"

# 연결 확인
node scripts/pocket-lens.mjs verify-connection

# 카테고리 목록
node scripts/pocket-lens.mjs list-categories

# 테스트 거래 생성
node scripts/pocket-lens.mjs create-transaction '{"transactions": [{"merchant": "테스트 가게", "amount": 1000, "date": "2025-12-05T12:00:00+09:00"}]}'

# 이번 달 지출 요약
node scripts/pocket-lens.mjs spending-summary

# 특정 월 지출 요약
node scripts/pocket-lens.mjs spending-summary --month 2026-01

# 이번 달 카드 청구
node scripts/pocket-lens.mjs card-bills

# 특정 월 카드 청구
node scripts/pocket-lens.mjs card-bills --month 2026-02
```

---

## License

MIT
