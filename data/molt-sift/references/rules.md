# Molt Sift - Validation Rules

## Rule Sets

### json-strict
Minimal validation - checks only JSON structure and types.

**Checks:**
- Valid JSON structure (dict or list)
- Type consistency within data

**Use for:** Generic JSON validation, data integrity checks

**Example:**
```bash
molt-sift validate --input data.json --rules json-strict
```

---

### crypto
Specialized validation for cryptocurrency data (prices, on-chain metrics, trading signals).

**Required fields:**
- `symbol` - Ticker symbol (e.g., "BTC", "SOL")
- `price` - Current price (numeric, must be positive)

**Checks:**
- Structure validity
- Type consistency
- Required fields present
- Price is valid number and > 0
- Optional: volume, change_pct (numeric)

**Example:**
```json
{
  "symbol": "BTC",
  "price": 42500.50,
  "volume": 1200000000,
  "change_pct": 2.5,
  "timestamp": "2026-02-25T12:00:00Z"
}
```

**Usage:**
```bash
molt-sift validate --input btc_data.json --rules crypto
```

---

### trading
Validation for trading orders, execution logs, and P&L reports.

**Required fields:**
- `order_id` - Unique order identifier
- `symbol` - Trading pair (e.g., "BTC/USDT")
- `side` - "buy" or "sell"
- `price` - Execution price (numeric, > 0)
- `quantity` - Order quantity (numeric, > 0)

**Checks:**
- All required fields present
- Price and quantity are positive numbers
- Side is "buy" or "sell"
- Order ID is unique and non-empty

**Example:**
```json
{
  "order_id": "ord_123456",
  "symbol": "BTC/USDT",
  "side": "buy",
  "price": 42500.00,
  "quantity": 0.5,
  "timestamp": "2026-02-25T12:00:00Z",
  "status": "filled"
}
```

**Usage:**
```bash
molt-sift validate --input order.json --rules trading
```

---

### sentiment
Validation for text sentiment analysis and scores.

**Required fields:**
- `text` - Text content (string)
- `score` - Sentiment score (0.0-1.0 range)

**Checks:**
- Text field is non-empty string
- Score is numeric between 0 and 1
- Optional: source, timestamp, confidence

**Example:**
```json
{
  "text": "Bitcoin is looking bullish heading into Q1",
  "score": 0.85,
  "source": "twitter",
  "confidence": 0.92,
  "timestamp": "2026-02-25T12:00:00Z"
}
```

**Usage:**
```bash
molt-sift sift --input sentiment.json --rules sentiment
```

---

## Custom Rules

Create your own validation rules by editing `rules.md` or passing a custom rule set file:

```bash
molt-sift validate --input data.json --rules custom --schema custom_schema.json
```

---

## Quality Scoring

All validation results include a quality score (0.0 - 1.0):

- **1.0** - Perfect, no issues
- **0.7-0.99** - Valid, minor warnings
- **0.5-0.69** - Marginal, some errors but data usable
- **<0.5** - Invalid, significant errors

**Score Calculation:**
- Start at 1.0
- Deduct 0.3 for each **error**
- Deduct 0.05 for each **warning**
- Minimum score: 0.0

---

## Integration Examples

### Validate Polymarket trade signals

```bash
molt-sift validate \
  --input polymarket_signal.json \
  --rules crypto \
  --output validated_signal.json
```

### Sift trading orders for high-confidence signals

```bash
molt-sift sift \
  --input orders.json \
  --rules trading \
  --output sifted_orders.json
```

### Run as bounty job

```bash
molt-sift bounty claim --auto --payout YOUR_SOLANA_ADDRESS
```
