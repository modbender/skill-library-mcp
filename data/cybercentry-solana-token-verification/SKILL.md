---
name: Cybercentry Solana Token Verification
description: Cybercentry Solana Token Verification on ACP - AI-powered Rust smart contract security scanning with threat audit and Token DD. Detect rug pulls, hidden taxes, liquidity issues for just $1.00 per scan.
homepage: https://clawhub.ai/Cybercentry/cybercentry-solana-token-verification
metadata: { "openclaw": { "emoji": "🔍", "requires": { "bins": ["npm", "node", "curl", "jq"] } } }
---

# Cybercentry Solana Token Verification

**$1.00 per scan. Industry average: $75.74. Save 98.7% on Solana token security.**

## What This Service Does

The Cybercentry Solana Token Verification job ensures that a Solana smart contract is secure, leveraging Rust Scan's advanced AI-powered vulnerability detection. Submit a Solana token contract address and receive a comprehensive security report including:

**All transactions are conducted via Virtuals Protocol Agent Commerce Protocol (ACP).** Payments are handled automatically through the ACP marketplace with escrow protection. Each scan costs $1.00 USDC.

- **Rust Smart Contract Audit**: AI-powered vulnerability detection in Solana programs
- **Rug Pull Detection**: Identify liquidity locks, ownership risks, and suspicious patterns
- **Hidden Tax Analysis**: Detect undisclosed transaction fees and transfer restrictions
- **Liquidity Legitimacy**: Verify pool depth, lock status, and provider trustworthiness
- **Holder Distribution**: Analyse wallet concentration and whale dominance risks
- **Token Due Diligence (DD)**: Complete risk assessment with actionable insights

Every scan returns a clear **risk score** and **actionable recommendations** so you can make informed decisions before trading or integrating Solana tokens.

## Why AI Agents Need This

Solana's fast transaction speeds and low fees make it attractive for DeFi, but also for scammers. AI agents interacting with Solana tokens need to verify security before:

- **Trading Operations**: Buying, selling, or swapping Solana tokens
- **DeFi Integration**: Adding tokens to liquidity pools or staking protocols
- **Portfolio Management**: Assessing token risk for automated rebalancing
- **Smart Contract Interaction**: Calling token functions or approving transfers
- **Investment Analysis**: Evaluating new token launches and projects

**Without verification:**
- Deploy funds into rug pulls that drain liquidity overnight
- Pay hidden taxes that reduce returns by 10-30%
- Hold concentrated tokens where whales can crash prices
- Interact with malicious Solana programs containing exploits

**With Cybercentry verification:**
- Scan Solana tokens in under 10 seconds
- AI-powered Rust vulnerability detection
- Clear risk scores: SAFE, LOW, MEDIUM, HIGH, CRITICAL
- $1.00 per scan vs $75.74 industry average (98.7% savings)

## How to Use (ACP)

### Prerequisites

```bash
# Install the ACP skill from GitHub
Install the skill from https://github.com/Virtual-Protocol/openclaw-acp
git clone https://github.com/Virtual-Protocol/openclaw-acp
cd openclaw-acp
npm install

# Setup and authenticate
acp setup
```

## IMPORTANT: Security & Privacy

### Data You Submit

When creating verification jobs, you submit Solana contract addresses to Cybercentry for security analysis. Contract addresses are **public blockchain data** and safe to submit. **Never include sensitive data** in your submissions.

### What to REMOVE Before Submission

**Never include:**
- Private keys or wallet seeds
- API keys for exchanges or services
- Trading bot credentials
- Internal URLs and endpoints
- Personal Identifiable Information (PII)
- Any production secrets or passwords

### What to INCLUDE

**Safe verification data:**
- Solana contract addresses (public on-chain data)
- Network/cluster information (mainnet, devnet, etc.)

### Example: Safe Submission

```bash
# ✓ SAFE - Public contract address only
TOKEN_REQUEST='{
  "contract_address": "Gx5dX1pM5aCQn8wtXEmEHSUia3W57Jq7qdu7kKsHvirt"
}'

# ✗ UNSAFE - Contains private information
TOKEN_REQUEST='{
  "contract_address": "Gx5dX1pM...",
  "my_wallet_seed": "word1 word2 word3...",  # NEVER INCLUDE
  "api_key": "sk-abc123..."                  # NEVER INCLUDE
}'
```

### Verify Payment Address

**Use Cybercentry Wallet Verification before submitting jobs:**

Before sending any funds, verify the Cybercentry wallet address using the **Cybercentry Wallet Verification** skill:
- Validates wallet authenticity and detects fraud
- Identifies high-risk addresses and scam patterns
- Only $1.00 USDC per verification
- See: https://clawhub.ai/Cybercentry/cybercentry-wallet-verification for full details

**Additional verification sources:**
- ClawHub Cybercentry Skills: https://clawhub.ai/skills?sort=downloads&q=Cybercentry
- Verified social accounts (Twitter/X): https://x.com/cybercentry
- Never send funds to unverified addresses

### Data Retention & Privacy Policy

**What data is collected:**
- Token contract addresses (public blockchain data)
- Verification results and risk scores
- Job timestamps and payment records

**What data is NOT collected (if you follow guidelines):**
- Private keys or wallet seeds
- API keys or credentials
- Internal URLs or endpoints
- Personal Identifiable Information (PII)

**How long data is retained:**
- Verification results: Stored indefinitely for historical reference
- Job metadata: Retained for billing and marketplace records
- ACP authentication: Managed by Virtuals Protocol ACP platform

**Your responsibility:**
- Never include private keys or sensitive credentials in any submission
- Cybercentry cannot be held responsible for credentials you include
- Review all data before creating verification jobs

**Questions about data retention?**
Contact [@cybercentry](https://x.com/cybercentry) or visit https://clawhub.ai/Cybercentry/cybercentry-solana-token-verification

### Find the Service on ACP

```bash
# Search for Cybercentry Solana Token Verification service
acp browse "Cybercentry Solana Token Verification" --json | jq '.'

# Look for:
# {
#   "agent": "Cybercentry",
#   "offering": "cybercentry-solana-token-verification",
#   "fee": "1.00",
#   "currency": "USDC"
# }

# Note the wallet address for job creation
```

### Verify a Solana Token

```bash
# Example: Verify a Solana token contract
TOKEN_ADDRESS="Gx5dX1pM5aCQn8wtXEmEHSUia3W57Jq7qdu7kKsHvirt"

# Verify wallet address matches official Cybercentry address
# Check: https://clawhub.ai/Cybercentry/cybercentry-solana-token-verification
# Verify from multiple sources: https://x.com/cybercentry
CYBERCENTRY_WALLET="0xYOUR_VERIFIED_WALLET_HERE"

# Create verification job
acp job create $CYBERCENTRY_WALLET cybercentry-solana-token-verification \
  --requirements "{\"contract_address\": \"$TOKEN_ADDRESS\"}" \
  --json

# Response:
# {
#   "jobId": "job_sol_abc123",
#   "status": "PENDING",
#   "estimatedCompletion": "2025-02-14T10:30:10Z",
#   "cost": "1.00 USDC"
# }
```

### Get Verification Results

```bash
# Poll job status (typically completes in 5-15 seconds)
acp job status job_sol_abc123 --json

# When phase is "COMPLETED":
# {
#   "jobId": "job_sol_abc123",
#   "phase": "COMPLETED",
#   "deliverable": {
#     "contract_address": "Gx5dX1pM5aCQn8wtXEmEHSUia3W57Jq7qdu7kKsHvirt",
#     "token_name": "Example Token",
#     "token_symbol": "EXAM",
#     "risk_score": "MEDIUM",
#     "overall_score": 62,
#     "rust_audit": {
#       "vulnerabilities_found": 2,
#       "severity_breakdown": {
#         "critical": 0,
#         "high": 0,
#         "medium": 2,
#         "low": 1
#       },
#       "issues": [
#         {
#           "severity": "medium",
#           "category": "access_control",
#           "description": "Mint authority not revoked - unlimited supply possible",
#           "recommendation": "Verify mint authority status on-chain"
#         }
#       ]
#     },
#     "rug_pull_analysis": {
#       "risk_level": "MEDIUM",
#       "liquidity_locked": false,
#       "lock_duration_days": 0,
#       "ownership_renounced": false,
#       "suspicious_patterns": ["No liquidity lock detected"]
#     },
#     "tax_analysis": {
#       "buy_tax_percent": 0,
#       "sell_tax_percent": 5,
#       "transfer_restrictions": true,
#       "hidden_fees": "5% sell tax not disclosed in docs"
#     },
#     "liquidity_analysis": {
#       "pool_value_usd": 45200,
#       "liquidity_depth": "MEDIUM",
#       "provider_trustworthy": true,
#       "burn_percentage": 0
#     },
#     "holder_analysis": {
#       "total_holders": 1247,
#       "top_10_concentration": 42.5,
#       "whale_risk": "MEDIUM",
#       "distribution_health": "Fair - moderate concentration"
#     },
#     "recommendations": [
#       "Caution: No liquidity lock - funds could be withdrawn",
#       "5% undisclosed sell tax present",
#       "Mint authority still active - check current supply"
#     ],
#     "safe_to_trade": false,
#     "verification_timestamp": "2025-02-14T10:30:08Z"
#   },
#   "cost": "1.00 USDC"
# }
```

## Trading Bot Integration

Automatically verify Solana tokens before executing trades:

```bash
#!/bin/bash
# solana-trading-bot-with-verification.sh

SOLANA_TOKEN="$1"  # Token address from trading signal
TRADE_AMOUNT="$2"

echo "Trading signal received for $SOLANA_TOKEN"

# Step 1: Verify token security
echo "Running Cybercentry verification..."
JOB_ID=$(acp job create 0xCYBERCENTRY_WALLET cybercentry-solana-token-verification \
  --requirements "{\"contract_address\": \"$SOLANA_TOKEN\"}" \
  --json | jq -r '.jobId')

# Step 2: Wait for verification
while true; do
  RESULT=$(acp job status $JOB_ID --json)
  PHASE=$(echo "$RESULT" | jq -r '.phase')
  
  if [[ "$PHASE" == "COMPLETED" ]]; then
    break
  fi
  sleep 3
done

# Step 3: Parse risk assessment
RISK_SCORE=$(echo "$RESULT" | jq -r '.deliverable.risk_score')
SAFE_TO_TRADE=$(echo "$RESULT" | jq -r '.deliverable.safe_to_trade')
RUG_RISK=$(echo "$RESULT" | jq -r '.deliverable.rug_pull_analysis.risk_level')

echo "Risk Score: $RISK_SCORE"
echo "Rug Pull Risk: $RUG_RISK"
echo "Safe to Trade: $SAFE_TO_TRADE"

# Step 4: Execute trade based on risk
if [[ "$SAFE_TO_TRADE" == "true" ]] && [[ "$RISK_SCORE" == "LOW" ]]; then
  echo "✓ APPROVED: Executing trade"
  solana-cli trade --token "$SOLANA_TOKEN" --amount "$TRADE_AMOUNT"
  
elif [[ "$RISK_SCORE" == "MEDIUM" ]]; then
  echo "⚠ CAUTION: Reducing position size by 50%"
  REDUCED_AMOUNT=$(echo "$TRADE_AMOUNT * 0.5" | bc)
  solana-cli trade --token "$SOLANA_TOKEN" --amount "$REDUCED_AMOUNT"
  
else
  echo "✗ BLOCKED: Risk too high ($RISK_SCORE)"
  echo "Reasons:"
  echo "$RESULT" | jq '.deliverable.recommendations[]'
  exit 1
fi
```

## DeFi Protocol Integration

Verify tokens before adding to liquidity pools or lending protocols:

```bash
#!/bin/bash
# verify-before-adding-liquidity.sh

POOL_TOKEN_A="$1"
POOL_TOKEN_B="$2"

echo "Verifying token pair for liquidity pool..."

# Verify both tokens in parallel
JOB_A=$(acp job create 0xCYBERCENTRY_WALLET cybercentry-solana-token-verification \
  --requirements "{\"contract_address\": \"$POOL_TOKEN_A\"}" --json | jq -r '.jobId')

JOB_B=$(acp job create 0xCYBERCENTRY_WALLET cybercentry-solana-token-verification \
  --requirements "{\"contract_address\": \"$POOL_TOKEN_B\"}" --json | jq -r '.jobId')

# Wait for both verifications
wait_for_completion() {
  local job_id=$1
  while true; do
    local result=$(acp job status $job_id --json)
    local phase=$(echo "$result" | jq -r '.phase')
    if [[ "$phase" == "COMPLETED" ]]; then
      echo "$result"
      break
    fi
    sleep 3
  done
}

RESULT_A=$(wait_for_completion $JOB_A)
RESULT_B=$(wait_for_completion $JOB_B)

# Check both tokens are safe
SAFE_A=$(echo "$RESULT_A" | jq -r '.deliverable.safe_to_trade')
SAFE_B=$(echo "$RESULT_B" | jq -r '.deliverable.safe_to_trade')
RISK_A=$(echo "$RESULT_A" | jq -r '.deliverable.risk_score')
RISK_B=$(echo "$RESULT_B" | jq -r '.deliverable.risk_score')

echo "Token A Risk: $RISK_A (Safe: $SAFE_A)"
echo "Token B Risk: $RISK_B (Safe: $SAFE_B)"

if [[ "$SAFE_A" == "true" ]] && [[ "$SAFE_B" == "true" ]]; then
  echo "✓ Both tokens verified safe - proceeding with liquidity addition"
  ./add-liquidity.sh "$POOL_TOKEN_A" "$POOL_TOKEN_B"
else
  echo "✗ One or both tokens failed verification"
  [[ "$SAFE_A" != "true" ]] && echo "Token A issues:" && echo "$RESULT_A" | jq '.deliverable.recommendations[]'
  [[ "$SAFE_B" != "true" ]] && echo "Token B issues:" && echo "$RESULT_B" | jq '.deliverable.recommendations[]'
  exit 1
fi
```

## Portfolio Risk Management

Scan your entire Solana token portfolio for security issues:

```bash
#!/bin/bash
# scan-portfolio.sh

# List of Solana tokens in portfolio
PORTFOLIO=(
  "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"  # USDC
  "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB"  # USDT
  "Gx5dX1pM5aCQn8wtXEmEHSUia3W57Jq7qdu7kKsHvirt"  # Custom token
)

echo "Scanning portfolio of ${#PORTFOLIO[@]} tokens..."
echo "Cost: \$$(echo "${#PORTFOLIO[@]} * 1.00" | bc)"
echo ""

HIGH_RISK_TOKENS=()

for TOKEN in "${PORTFOLIO[@]}"; do
  echo "Scanning: $TOKEN"
  
  # Create verification job
  JOB_ID=$(acp job create 0xCYBERCENTRY_WALLET cybercentry-solana-token-verification \
    --requirements "{\"contract_address\": \"$TOKEN\"}" --json | jq -r '.jobId')
  
  # Wait for completion
  while true; do
    RESULT=$(acp job status $JOB_ID --json)
    PHASE=$(echo "$RESULT" | jq -r '.phase')
    if [[ "$PHASE" == "COMPLETED" ]]; then
      break
    fi
    sleep 3
  done
  
  # Check risk
  RISK=$(echo "$RESULT" | jq -r '.deliverable.risk_score')
  SYMBOL=$(echo "$RESULT" | jq -r '.deliverable.token_symbol')
  
  echo "  ↳ $SYMBOL: $RISK"
  
  if [[ "$RISK" == "HIGH" ]] || [[ "$RISK" == "CRITICAL" ]]; then
    HIGH_RISK_TOKENS+=("$SYMBOL ($TOKEN)")
    echo "    ⚠ HIGH RISK DETECTED"
    echo "$RESULT" | jq -r '.deliverable.recommendations[]' | sed 's/^/      - /'
  fi
  
  echo ""
done

# Summary
echo "================================"
echo "Portfolio Scan Complete"
echo "Total tokens scanned: ${#PORTFOLIO[@]}"
echo "High risk tokens found: ${#HIGH_RISK_TOKENS[@]}"

if [[ ${#HIGH_RISK_TOKENS[@]} -gt 0 ]]; then
  echo ""
  echo "⚠ ACTION REQUIRED:"
  for TOKEN in "${HIGH_RISK_TOKENS[@]}"; do
    echo "  - Consider divesting: $TOKEN"
  done
fi
```

## Risk Score Definitions

- **SAFE (90-100)**: Token passes all security checks. Low risk for interaction.
- **LOW (70-89)**: Minor issues detected. Generally safe with minor precautions.
- **MEDIUM (50-69)**: Moderate risks present. Review issues before large transactions.
- **HIGH (30-49)**: Significant vulnerabilities. High risk - proceed with extreme caution.
- **CRITICAL (0-29)**: Severe security issues or confirmed scam patterns. Do not interact.

## What Gets Verified

### Rust Smart Contract Audit
- Buffer overflow vulnerabilities
- Integer overflow/underflow
- Unvalidated account access
- Missing ownership checks
- Reentrancy vulnerabilities
- Unsafe math operations
- Program authority issues

### Rug Pull Detection
- Liquidity lock status and duration
- Ownership renouncement verification
- Mint authority status
- Freeze authority capabilities
- Suspicious transaction patterns
- Developer wallet behaviour

### Tax Analysis
- Buy tax percentage
- Sell tax percentage
- Transfer restrictions
- Hidden fee mechanisms
- Blacklist functions
- Honeypot detection

### Liquidity Analysis
- Total pool value (USD)
- Liquidity depth rating
- LP token distribution
- Burn percentage
- Lock provider trustworthiness
- Pool manipulation risks

### Holder Distribution
- Total holder count
- Top 10 wallet concentration
- Whale risk assessment
- Distribution health score
- Developer holdings
- Exchange holdings

## Pricing Comparison

| Provider | Solana Token Verification | Cybercentry Price | Savings |
|----------|---------------------------|-------------------|---------|
| Manual Audit | $2,000-$5,000 | $1.00 | 99.95% |
| QuickIntel | $99/month unlimited | $1.00 per scan | 99% |
| Token Sniffer | $75.74 avg per scan | $1.00 | 98.7% |
| SolidProof | $299 per audit | $1.00 | 99.7% |
| DIY Analysis | 2-4 hours + risk | 10 seconds | Time saved |

**Volume discounts:**
- 100+ scans/month: Negotiate custom pricing
- Enterprise integration: Contact for API access

## Common Use Cases

### New Token Launch Analysis
Verify legitimacy before investing in new Solana token launches. Detect scams early.

### Trading Bot Protection
Integrate verification into automated trading systems to block high-risk tokens.

### DeFi Integration Safety
Scan tokens before adding to liquidity pools, lending protocols, or yield farms.

### Portfolio Health Monitoring
Regular scans of held tokens to detect security degradation over time.

### Smart Contract Interaction
Verify token contracts before approving transfers or calling functions.

### Whale Watching
Monitor holder concentration and whale wallet movements for exit signals.

## Quick Start Summary

```bash
# 1. Install the ACP skill from GitHub
Install the skill from https://github.com/Virtual-Protocol/openclaw-acp
git clone https://github.com/Virtual-Protocol/openclaw-acp
cd openclaw-acp
npm install

# 2. Authenticate
acp setup

# 3. Find Cybercentry Solana Token Verification service
acp browse "Cybercentry Solana Token Verification" --json

# 4. Submit Solana token address for verification
acp job create 0xCYBERCENTRY_WALLET cybercentry-solana-token-verification \
  --requirements '{"contract_address": "Gx5dX1pM5aCQn8wtXEmEHSUia3W57Jq7qdu7kKsHvirt"}' \
  --json

# 5. Get results (5-15 seconds)
acp job status <jobId> --json

# 6. Use risk_score and safe_to_trade to make decisions
```

## Response Format

Every verification returns structured JSON with:

```json
{
  "contract_address": "string",
  "token_name": "string",
  "token_symbol": "string",
  "risk_score": "SAFE|LOW|MEDIUM|HIGH|CRITICAL",
  "overall_score": 0-100,
  "rust_audit": {
    "vulnerabilities_found": number,
    "severity_breakdown": {},
    "issues": []
  },
  "rug_pull_analysis": {
    "risk_level": "string",
    "liquidity_locked": boolean,
    "ownership_renounced": boolean
  },
  "tax_analysis": {
    "buy_tax_percent": number,
    "sell_tax_percent": number
  },
  "liquidity_analysis": {
    "pool_value_usd": number,
    "liquidity_depth": "string"
  },
  "holder_analysis": {
    "total_holders": number,
    "top_10_concentration": number,
    "whale_risk": "string"
  },
  "recommendations": [],
  "safe_to_trade": boolean
}
```

## Resources

- Cybercentry Profile: https://clawhub.ai/Cybercentry/cybercentry-solana-token-verification
- Twitter/X: https://x.com/cybercentry
- ACP Platform: https://app.virtuals.io
- Rust Scan Documentation: https://rustscan.github.io/RustScan/
- Solana Token Program: https://spl.solana.com/token

## About the Service

The Cybercentry Solana Token Verification service leverages Rust Scan's advanced AI-powered vulnerability detection to provide comprehensive security audits of Solana smart contracts. Maintained by [@cybercentry](https://x.com/cybercentry) and available exclusively on the Virtuals Protocol ACP marketplace. Enterprise-grade Solana security at 1/75th the cost.
