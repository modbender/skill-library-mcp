# Molt Sift - Deployment Guide

## Local Installation

### Prerequisites
- Python 3.8+
- pip

### Install

```bash
cd molt-sift
pip install -e .
```

This installs the `molt-sift` CLI and makes the module available for import.

### Verify Installation

```bash
molt-sift --help
```

Should show CLI help.

---

## Using the CLI

### Validate Data

```bash
# Basic validation
molt-sift validate --input data.json --rules crypto

# With schema
molt-sift validate --input data.json --schema schema.json

# Save result
molt-sift validate --input data.json --rules crypto --output result.json
```

### Sift for Signals

```bash
molt-sift sift --input orders.json --rules trading
```

### Bounty Hunting

```bash
# Auto-watch and claim
molt-sift bounty claim --auto --payout YOUR_SOLANA_ADDRESS

# Check status
molt-sift bounty status --payout YOUR_SOLANA_ADDRESS
```

### API Server

```bash
molt-sift api start --port 8000
```

Then POST to `http://localhost:8000/bounty`

---

## Using as Python Library

```python
from molt_sift.sifter import Sifter

sifter = Sifter(rules="crypto")
result = sifter.validate({"symbol": "BTC", "price": 42850})
print(result)
```

---

## Docker Deployment

### Build Image

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY molt-sift /app

RUN pip install -e .

EXPOSE 8000

CMD ["molt-sift", "api", "start", "--port", "8000"]
```

Build:
```bash
docker build -t molt-sift .
```

Run:
```bash
docker run -p 8000:8000 molt-sift
```

---

## Cron Integration

Run bounty agent on a schedule:

```bash
# In crontab
*/5 * * * * /usr/local/bin/molt-sift bounty claim --auto --payout ADDR > /var/log/molt-sift.log 2>&1
```

This watches PayAClaw every 5 minutes and claims available bounties.

---

## Environment Variables (When Implemented)

Set before running:

```bash
export PAYACLAW_API_KEY="your_api_key"
export PAYACLAW_SECRET="your_secret"
export SOLANA_RPC="https://api.mainnet-beta.solana.com"
export SOLANA_WALLET="YOUR_SOLANA_ADDRESS"
export X402_API_KEY="your_x402_key"
```

---

## Monitoring

### Bounty Agent Health

```bash
molt-sift bounty status --payout YOUR_SOLANA_ADDRESS
```

Returns:
```json
{
  "status": "active",
  "payout_address": "YOUR_SOLANA_ADDRESS",
  "jobs_processed": 42,
  "total_earned_usdc": 128.50,
  "timestamp": "2026-02-25T12:00:00Z"
}
```

### Logs

Bounty agent logs to stdout and optionally to file:

```bash
molt-sift bounty claim --auto --payout ADDR > bounty-agent.log 2>&1 &
```

---

## ClawHub Installation

Once packaged:

```bash
openclaw install molt-sift
```

Or download from ClawHub UI.

---

## Troubleshooting

### Import Error
```
Error: Run 'pip install -e .' from molt-sift directory
```

Solution:
```bash
cd molt-sift
pip install -e .
```

### Invalid JSON Input
```
Error loading data.json: ...
```

Verify JSON is valid:
```bash
python -m json.tool data.json
```

### Missing Required Fields
Check the validation rule:
```bash
molt-sift validate --input data.json --rules crypto
```

Look for "missing_required_field" in issues.

### Payment Failed
When x402 integration is added, check:
- Solana address is valid
- Wallet has SOL for fees
- x402 API key is configured

---

## API Endpoint Reference

(Once Flask server is implemented)

### POST /bounty

**Request:**
```json
{
  "raw_data": {...},
  "schema": {...},
  "payment_address": "YOUR_SOLANA_ADDR",
  "amount_usdc": 5.00
}
```

**Response:**
```json
{
  "status": "validated",
  "score": 0.87,
  "clean_data": {...},
  "issues": [...],
  "payment_txn": "5Aabc..."
}
```

---

## Performance Targets

- **Validation:** <500ms per object
- **Bounty claim:** <2s end-to-end
- **API response:** <1s with payment

---

## Security

- ✓ Input validation on all endpoints
- ✓ Schema validation before processing
- ✓ Solana wallet key management (when implemented)
- ✓ Rate limiting on API (when implemented)

---

## Support

For issues or questions:
- Check `README.md`
- Review `SKILL.md`
- Check test suite in `test_molt_sift.py`
