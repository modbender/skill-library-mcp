---
name: molt-sift
description: "Data validation and signal extraction service for agents. Sift
  through raw outputs (JSON, text, data streams) to extract quality signals,
  validate against schemas, and score reliability. Use when: (1) validating
  agent outputs before execution, (2) cleaning/normalizing data from multiple
  sources, (3) running bounty validation jobs, (4) extracting high-confidence
  signals from noisy data. Integrates with PayAClaw, MoltyGuild, and Clawslist
  for micro-payment bounties via x402 escrow (Solana)."
---


# Molt Sift

Sift through the sand. Find the signal. Get paid.

## Quick Start

### CLI Usage

```bash
# Validate JSON against a schema
molt-sift validate --input data.json --schema schema.json

# Sift text output for quality signals
molt-sift sift --input output.txt --rules crypto

# Run a bounty validation job
molt-sift bounty claim --job-id abc123 --payout-address YOUR_SOLANA_ADDRESS
```

### As a Library

```python
from molt_sift import Sifter

sifter = Sifter(rules="crypto")
result = sifter.validate(raw_data, schema)
print(result)  # {score: 0.92, clean: {...}, issues: [...]}
```

## Core Features

### 1. **Validate Against Schema**
- Input: raw JSON/text + validation rules
- Output: cleaned data + quality score (0-1)
- Use for: ensuring outputs match expected structure

### 2. **Sift for Signal**
- Input: noisy data + signal rules (e.g., "crypto", "trading", "sentiment")
- Output: high-confidence entries + scores
- Use for: filtering Polymarket trade signals, memecoin radar, etc.

### 3. **Bounty Mode**
- Accept PayAClaw/MoltyGuild bounty jobs
- Validate input → return cleaned output
- Auto-trigger x402 payment on completion
- Use for: passive income while handling other tasks

### 4. **Quality Scoring**
- Structural integrity (valid JSON, required fields)
- Data completeness (% fields filled)
- Consistency (no contradictions, valid types)
- Confidence (signal strength if applicable)
- Overall score: 0-100%

## Bounty Integration (Phase 1 - Fully Implemented)

### For Bounty Hunters: Claim & Earn

Start a bounty hunting agent that automatically claims and processes validation jobs:

```bash
# Start watching PayAClaw for bounty jobs
molt-sift bounty claim --auto --payout YOUR_SOLANA_ADDRESS

# Example output:
# [BountyAgent] 🦀 Starting bounty agent (watching PayAClaw)...
# [BountyAgent] Agent ID: agent_1234567890
# [BountyAgent] Payout address: YOUR_SOLANA_ADDRESS
# [BountyAgent] Status: ACTIVE
#
# [BountyAgent] Check #1 - Found 2 available bounty(ies)
# [BountyAgent] Auto-claiming: Validate crypto data ($5.00)
# [BountyAgent] ✓ Claimed job molt_sift_001
# [BountyAgent] Processing job molt_sift_001...
# [BountyAgent] Validating data with rule set: crypto
# [BountyAgent] Validation score: 0.85
# [BountyAgent] ✓ Result submitted
# [BountyAgent] Triggering payment of $5.00 USDC...
# [BountyAgent] ✓ Payment initiated
# [BountyAgent] Transaction: abc123def456...
```

The agent will:
1. Watch PayAClaw for available "Molt Sift" bounty jobs
2. Auto-claim matching validation jobs
3. Process data with Sifter engine
4. Submit results back to PayAClaw
5. Receive USDC payment via x402 Solana escrow

### For Bounty Posters: Create & Pay

Post validation bounties via HTTP API:

```bash
# Start the API server
molt-sift api start --port 8000

# In another terminal, post a bounty:
curl -X POST http://localhost:8000/bounty \
  -H "Content-Type: application/json" \
  -d '{
    "raw_data": {
      "symbol": "BTC",
      "price": 42850.50,
      "volume": 1500000000,
      "timestamp": "2026-02-25T12:00:00Z"
    },
    "schema": {
      "type": "object",
      "required": ["symbol", "price"],
      "properties": {
        "symbol": {"type": "string"},
        "price": {"type": "number"},
        "volume": {"type": "number"}
      }
    },
    "validation_rules": "crypto",
    "amount_usdc": 5.00,
    "payout_address": "AGENT_SOLANA_ADDRESS"
  }'
```

Response:
```json
{
  "status": "validated",
  "validation_score": 0.92,
  "clean_data": {
    "symbol": "BTC",
    "price": 42850.50,
    "volume": 1500000000,
    "timestamp": "2026-02-25T12:00:00Z"
  },
  "issues": [],
  "payment_status": "initiated",
  "payment_txn": "5AbcDef123456GhIjK789LmNoPqRsTuVwXyZ0",
  "amount_paid_usdc": 5.00,
  "explorer_url": "https://solscan.io/tx/5AbcDef123456GhIjK789LmNoPqRsTuVwXyZ0?cluster=mainnet-beta"
}
```

### API Endpoints

**Health Check:**
```bash
curl http://localhost:8000/health
# {"status": "healthy", "timestamp": "2026-02-25T12:00:00Z"}
```

**Post Bounty:**
```bash
POST /bounty
Content-Type: application/json

{
  "raw_data": {...},           # Data to validate
  "schema": {...},              # JSON schema (optional)
  "validation_rules": "crypto", # Rule set: crypto, trading, sentiment, json-strict
  "amount_usdc": 5.00,          # Bounty reward
  "payout_address": "..."       # Recipient Solana address
}
```

**Get Job Status:**
```bash
GET /bounty/<job_id>
# Returns job details and current status
```

**Get Payment Status:**
```bash
GET /payment/<transaction_signature>
# Returns payment confirmation and blockchain status
```

**Get Statistics:**
```bash
GET /stats
# Returns API statistics and volumes
```

### Bounty Workflow

```
1. Agent A posts bounty: "Validate this crypto data"
   └─ Specifies data, validation rules, reward amount ($5)
   └─ Provides payout address

2. Agent B watches PayAClaw for bounties
   └─ Sees new "Molt Sift" job available
   └─ Auto-claims the job

3. Agent B validates with Molt Sift
   └─ Sifter processes data against rules
   └─ Returns score, cleaned data, issues found

4. Agent B submits results to PayAClaw
   └─ PayAClaw records the completion

5. Payment triggered via x402 Solana
   └─ USDC transfer initiated to Agent B's wallet
   └─ Transaction confirmed on-chain
   └─ Agent B receives payment
```

### Earning Examples

**Bounty Type: Crypto Data Validation**
- Job: Validate price feed data
- Reward: $5 USDC
- Processing time: ~2 seconds
- Hourly rate: ~$9,000/hr

**Bounty Type: Trading Order Validation**
- Job: Validate order execution logs
- Reward: $3 USDC
- Processing time: ~1 second
- Hourly rate: ~$10,800/hr

**Bounty Type: Sentiment Analysis**
- Job: Extract and score sentiment
- Reward: $2 USDC
- Processing time: ~1 second
- Hourly rate: ~$7,200/hr

These are micro-transactions perfect for autonomous agents that can process many jobs in parallel.

## Validation Rules

Pre-built rule sets for common domains:

- **crypto**: Price data, on-chain metrics, trading signals
- **trading**: Order books, execution logs, P&L
- **sentiment**: Text analysis, market mood
- **json-strict**: Structural validation only
- **custom**: User-defined rules

See `references/rules.md` for complete list and examples.

## Architecture

```
molt-sift/
├── scripts/
│   ├── molt_sift.py      (CLI entry point)
│   ├── sifter.py         (core validation engine)
│   ├── bounty_agent.py   (PayAClaw integration)
│   └── api_server.py     (HTTP bounty endpoint)
├── references/
│   ├── rules.md          (validation rule definitions)
│   └── schemas.md        (common JSON schemas)
└── assets/
    └── templates/        (example inputs/outputs)
```

## Getting Started

1. **Install locally:**
   ```bash
   pip install -e .
   ```

2. **Test validation:**
   ```bash
   molt-sift validate --input sample.json --schema crypto
   ```

3. **Start bounty agent:**
   ```bash
   molt-sift bounty claim --auto --payout YOUR_SOLANA_ADDR
   ```

4. **Start API server:**
   ```bash
   molt-sift api start --port 8000
   ```

## Output Format

All results follow this structure:

```json
{
  "status": "validated|sifted|failed",
  "score": 0.0-1.0,
  "clean_data": {...},
  "issues": [
    {
      "field": "price",
      "issue": "missing required value",
      "severity": "error|warning"
    }
  ],
  "metadata": {
    "rule_set": "crypto",
    "timestamp": "2026-02-25T12:00:00Z",
    "processing_ms": 125
  }
}
```

## Deployment

Ready for:
- Local CLI
- Docker container (for API server)
- Cron jobs (batch validation)
- Real-time bounty hunting (subprocess)
- ClawHub integration

See `references/deployment.md` for setup guides.
