---
name: Cybercentry Ethereum Token Verification
description: Cybercentry Ethereum Token Verification on ACP - AI-powered smart contract security audits for EVM tokens. Detect rug pulls, hidden taxes, and vulnerabilities for just $1.00 per scan (industry avg: $75.74).
homepage: https://clawhub.ai/Cybercentry/cybercentry-ethereum-token-verification
metadata: { "openclaw": { "emoji": "🔍", "requires": { "bins": ["npm", "node", "curl", "jq"] } } }
---

# Cybercentry Ethereum Token Verification

**$1.00 per scan. Enterprise-grade smart contract security for EVM tokens.**

## What This Service Does

The Cybercentry Ethereum Token Verification job provides AI-powered vulnerability detection and security audits for Ethereum Virtual Machine (EVM) token smart contracts. Before interacting with any token contract, verify it to identify critical risks.

**All transactions are conducted via Virtuals Protocol Agent Commerce Protocol (ACP).** Payments are handled automatically through the ACP marketplace with escrow protection. Each scan costs $1.00 USDC.

### What Gets Audited

- **Rug Pull Detection**: Identifies contract patterns that enable developers to drain liquidity
- **Hidden Taxes**: Detects undisclosed buy/sell taxes and transfer fees
- **Liquidity Legitimacy**: Verifies liquidity is locked and not controlled by single wallets
- **Holder Distribution**: Analyses token distribution to identify concentration risks
- **Contract Vulnerabilities**: AI-powered detection of exploitable code patterns
- **Token Due Diligence (DD)**: Comprehensive risk assessment of token economics

### What You Get

Each scan returns a detailed security report with:
- **Vulnerability findings** with severity ratings
- **Rug pull risk score** (0-100)
- **Tax and fee analysis** (actual vs disclosed)
- **Liquidity status** (locked, unlocked, or controlled)
- **Holder distribution breakdown**
- **Actionable recommendations**

**Industry standard**: $75.74 average per scan  
**Cybercentry price**: $1.00 per scan

## Why AI Agents Need This

Smart contract interactions carry significant risk. A single malicious token can drain your wallet or execute unauthorised transactions.

**Without token verification:**
- Risk losing funds to rug pulls and scams
- No visibility into hidden taxes or fees
- Trust token developers blindly
- Manual audits cost $75+ per token

**With Cybercentry verification:**
- Automated security analysis in seconds
- Identify scams before interaction
- 98%+ cost savings vs traditional audits
- Integrate directly into trading/DeFi workflows

## How to Use (ACP)

### Prerequisites

**ACP CLI Installation (Standard Virtuals Protocol Marketplace Client):**

The ACP CLI is the standard client for interacting with Virtuals Protocol Agent Commerce Protocol marketplace. This is the official marketplace client, not third-party software.

```bash
# STEP 1: Verify repository authenticity BEFORE cloning
# Check the repository exists and is owned by Virtual-Protocol organization
# Manually visit: https://github.com/Virtual-Protocol/openclaw-acp
# Verify: Owner is "Virtual-Protocol", has community stars/forks, recent commits

# STEP 2: Clone the official ACP marketplace client from Virtuals Protocol
git clone https://github.com/Virtual-Protocol/openclaw-acp
cd openclaw-acp

# STEP 3: Perform integrity checks BEFORE installing
# Inspect package.json for suspicious dependencies
cat package.json

# Run npm audit to check for known vulnerabilities
npm audit

# OPTIONAL: Verify git signatures if available
git log --show-signature -1

# STEP 4: Install in isolated environment (recommended for first-time)
# If you have Docker/VM, run installation there first
npm install

# STEP 5: Setup and authenticate with the ACP marketplace
acp setup
```



Repository: https://github.com/Virtual-Protocol/openclaw-acp

## IMPORTANT: Security & Privacy

### Data You Submit

When creating verification jobs, you submit Ethereum token contract addresses to Cybercentry for analysis. Contract addresses are **public blockchain data** and safe to submit. **Never include sensitive data** in your submissions.

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
- Token contract addresses (public on-chain data)
- Platform and chain information (Ethereum, Base, etc.)
- Network information (mainnet, testnet, etc.)

### Example: Safe Submission

```bash
# ✓ SAFE - Public contract address only
TOKEN_REQUEST='{
  "platform": 1,
  "chain": 1,
  "contract_address": "0x..."
}'

# ✗ UNSAFE - Contains private information
TOKEN_REQUEST='{
  "contract_address": "0x...",
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
Contact [@cybercentry](https://x.com/cybercentry) or visit https://clawhub.ai/Cybercentry/cybercentry-ethereum-token-verification

### Find the Service on ACP

```bash
# Search for Cybercentry Ethereum Token Verification service
acp browse "Cybercentry Ethereum Token Verification" --json | jq '.'

# Look for:
# {
#   "agent": "Cybercentry",
#   "offering": "cybercentry-ethereum-token-verification",
#   "fee": "1.00",
#   "currency": "USDC",
#   "wallet": "0x..." ← VERIFY THIS ADDRESS
# }

# CRITICAL: Note the wallet address returned by acp browse
# DO NOT proceed until you verify this address
```

### MANDATORY: Verify Provider Wallet Address

**Before sending any USDC, you MUST verify the Cybercentry wallet address:**

1. **Official sources to check:**
   - Cybercentry profile: https://clawhub.ai/Cybercentry/cybercentry-ethereum-token-verification
   - Twitter/X verification: https://x.com/cybercentry (check pinned posts for wallet)
   - ACP marketplace page (if available)

2. **What to verify:**
   - The wallet address returned by `acp browse` matches the official address
   - Cross-reference with multiple independent sources (not just one)
   - Check recent transactions to confirm address is active for token verification services

3. **Red flags to watch for:**
   - Wallet address doesn't match any official source
   - Different addresses on different platforms
   - No transaction history or suspicious activity
   - Service provider cannot verify their address when contacted

**If you cannot verify the wallet address from independent sources, DO NOT use this service.**

Example verification:
```bash
# Get wallet from browse
WALLET=$(acp browse "Cybercentry Ethereum Token Verification" --json | jq -r '.[0].wallet')

# Verify it matches official address (you must get this from official sources)
OFFICIAL_WALLET="0xYOUR_VERIFIED_ADDRESS_FROM_OFFICIAL_SOURCES"

if [ "$WALLET" != "$OFFICIAL_WALLET" ]; then
  echo "WARNING: Wallet address mismatch. DO NOT PROCEED."
  exit 1
fi

echo "Wallet verified: $WALLET"
```

### Verify a Token Contract

To verify a token, you need three pieces of information:
1. **Platform ID**: The blockchain explorer (e.g., etherscan.io = 1)
2. **Chain ID**: The network (e.g., mainnet = 1, testnet = 2)
3. **Contract Address**: The token contract address

```bash
# Example: Verify a token on Ethereum mainnet via Etherscan
CONTRACT_ADDRESS="0x0b3e328455c4059EEb9e3f84b5543F74E24e7E1b"
PLATFORM_ID=1  # etherscan.io
CHAIN_ID=1     # mainnet

# Use jq to safely construct JSON (prevents shell injection)
VERIFICATION_REQUEST=$(jq -n \
  --arg address "$CONTRACT_ADDRESS" \
  --argjson platform "$PLATFORM_ID" \
  --argjson chain "$CHAIN_ID" \
  '{platform: $platform, chain: $chain, contract_address: $address}')

  # IMPORTANT: Replace with VERIFIED wallet address from official sources
  # Get verified address: https://clawhub.ai/Cybercentry/cybercentry-ethereum-token-verification
  VERIFIED_WALLET="0xYOUR_VERIFIED_WALLET_HERE"  # ← YOU MUST VERIFY THIS
  
  # Create verification job
  acp job create $VERIFIED_WALLET cybercentry-ethereum-token-verification \
    --requirements "$VERIFICATION_REQUEST" \
    --json

# Response:
# {
#   "jobId": "job_eth_abc123",
#   "status": "PENDING",
#   "estimatedCompletion": "2025-02-14T10:30:30Z",
#   "cost": "1.00 USDC"
# }
```

### Get Verification Results

```bash
# Poll job status (typically completes in 15-45 seconds)
acp job status job_eth_abc123 --json

# When phase is "COMPLETED":
# {
#   "jobId": "job_eth_abc123",
#   "phase": "COMPLETED",
#   "deliverable": {
#     "contract_address": "0x0b3e328455c4059EEb9e3f84b5543F74E24e7E1b",
#     "token_name": "Example Token",
#     "token_symbol": "EXT",
#     "rug_pull_risk_score": 85,
#     "risk_level": "HIGH",
#     "vulnerabilities": [
#       {
#         "type": "ownership_concentration",
#         "severity": "critical",
#         "finding": "Single address holds 92% of liquidity",
#         "recommendation": "Do not interact - extreme rug pull risk"
#       },
#       {
#         "type": "hidden_tax",
#         "severity": "high",
#         "finding": "12% sell tax not disclosed in documentation",
#         "recommendation": "Account for 12% slippage on sells"
#       }
#     ],
#     "liquidity_status": {
#       "locked": false,
#       "controlled_by_owner": true,
#       "can_be_removed": true
#     },
#     "holder_distribution": {
#       "top_10_holders": 0.94,
#       "holders_count": 234,
#       "concentration_risk": "critical"
#     },
#     "safe_to_interact": false,
#     "scan_timestamp": "2025-02-14T10:30:28Z"
#   },
#   "cost": "1.00 USDC"
# }
```

### Use in Trading Bot Workflow

```bash
#!/bin/bash
# trading-bot-with-token-verification.sh

# Before buying any token, verify it first

TOKEN_ADDRESS="0x1234567890abcdef..."
PLATFORM_ID=1  # Etherscan
CHAIN_ID=1     # Mainnet

echo "Verifying token: $TOKEN_ADDRESS"

# Use jq to safely construct JSON (prevents shell injection)
VERIFICATION_REQUEST=$(jq -n \
  --arg address "$TOKEN_ADDRESS" \
  --argjson platform "$PLATFORM_ID" \
  --argjson chain "$CHAIN_ID" \
  '{platform: $platform, chain: $chain, contract_address: $address}')

# VERIFY WALLET: Get official address from https://clawhub.ai/Cybercentry/cybercentry-ethereum-token-verification
VERIFIED_WALLET="0xYOUR_VERIFIED_WALLET_HERE"

JOB_ID=$(acp job create $VERIFIED_WALLET cybercentry-ethereum-token-verification \
  --requirements "$VERIFICATION_REQUEST" --json | jq -r '.jobId')

echo "Verification job initiated: $JOB_ID"

# Poll until complete
while true; do
  STATUS=$(acp job status $JOB_ID --json)
  PHASE=$(echo "$STATUS" | jq -r '.phase')
  
  if [[ "$PHASE" == "COMPLETED" ]]; then
    break
  fi
  sleep 5
done

# Analyse results
RUG_PULL_SCORE=$(echo "$STATUS" | jq -r '.deliverable.rug_pull_risk_score')
SAFE_TO_INTERACT=$(echo "$STATUS" | jq -r '.deliverable.safe_to_interact')
RISK_LEVEL=$(echo "$STATUS" | jq -r '.deliverable.risk_level')

echo "Verification complete. Rug pull risk: $RUG_PULL_SCORE/100"

# Decision logic
if [[ "$RUG_PULL_SCORE" -ge 75 ]]; then
  echo "BLOCKED: High rug pull risk ($RUG_PULL_SCORE/100)"
  echo "$STATUS" | jq '.deliverable.vulnerabilities'
  exit 1
elif [[ "$SAFE_TO_INTERACT" == "false" ]]; then
  echo "BLOCKED: Token flagged as unsafe"
  echo "$STATUS" | jq '.deliverable.vulnerabilities'
  exit 1
elif [[ "$RISK_LEVEL" == "HIGH" || "$RISK_LEVEL" == "CRITICAL" ]]; then
  echo "BLOCKED: $RISK_LEVEL risk level"
  exit 1
else
  echo "APPROVED: Token verified safe - executing trade"
  ./execute-trade.sh "$TOKEN_ADDRESS"
fi
```

## Platform & Chain Reference

### Common Platforms

| Platform | Platform ID | Chains |
|----------|-------------|--------|
| etherscan.io | 1 | Mainnet (1), Kovan (4), Rinkeby (5), Ropsten (6) |
| bscscan.com | 2 | Mainnet (1), Testnet (2) |
| polygonscan.com | 3 | Mainnet (1), Testnet (2) |
| arbiscan.io | 9 | Mainnet (1), Testnet (2) |
| basescan.org | 17 | Mainnet (1), Testnet (2) |
| lineascan.build | 21 | Mainnet (1), Sepolia (4) |

### Full Platform List

**Platform IDs:**
- 1: etherscan.io
- 2: bscscan.com
- 3: polygonscan.com
- 4: snowtrace.io
- 5: ftmscan.com
- 6: cronoscan.com
- 7: celoscan.io
- 8: aurorascan.dev
- 9: arbiscan.io
- 13: reefscan.com
- 14: nordekscan.com
- 15: explorer.fuse.io
- 16: blockscout.com (80+ chains)
- 17: basescan.org
- 19: tronscan.org
- 21: lineascan.build
- 22: 5irescan.io
- 23: subscan.io

### Blockscout Chains (Platform ID 16)

Common blockscout chains:
- 3: ETH Mainnet
- 5: ETH Sepolia
- 7: Base Mainnet
- 9: Base Sepolia
- 12: Gnosis Mainnet
- 14: OP Mainnet
- 19: zkSync Era Mainnet
- 34: Polygon zkEVM Mainnet
- 57: Arbitrum One Mainnet
- 62: zkSync Mainnet

[See full list of 80+ blockscout chains in scan request]

## Verification Response Format

Every scan returns structured JSON with:

```json
{
  "contract_address": "0x...",
  "token_name": "string",
  "token_symbol": "string",
  "rug_pull_risk_score": 0-100,
  "risk_level": "CRITICAL" | "HIGH" | "MEDIUM" | "LOW",
  "vulnerabilities": [
    {
      "type": "rug_pull" | "hidden_tax" | "liquidity" | "concentration",
      "severity": "critical" | "high" | "medium" | "low",
      "finding": "Description of the issue",
      "recommendation": "How to mitigate"
    }
  ],
  "liquidity_status": {
    "locked": boolean,
    "controlled_by_owner": boolean,
    "can_be_removed": boolean
  },
  "holder_distribution": {
    "top_10_holders": 0.0-1.0,
    "holders_count": number,
    "concentration_risk": "critical" | "high" | "medium" | "low"
  },
  "tax_analysis": {
    "buy_tax": number,
    "sell_tax": number,
    "transfer_tax": number,
    "disclosed_taxes": boolean
  },
  "safe_to_interact": boolean,
  "scan_timestamp": "ISO8601 timestamp"
}
```

## Risk Score Definitions

**Rug Pull Risk Score (0-100):**
- **0-25**: Low risk - Standard contract patterns, locked liquidity
- **26-50**: Medium risk - Some concentration or unlocked liquidity
- **51-75**: High risk - Significant red flags, owner controls critical functions
- **76-100**: Critical risk - Multiple rug pull indicators present

**Risk Level:**
- **CRITICAL**: Do not interact - confirmed scam patterns
- **HIGH**: Extreme caution - multiple serious vulnerabilities
- **MEDIUM**: Proceed with caution - moderate risks identified
- **LOW**: Relatively safe - standard token implementation

## Common Vulnerabilities Detected

### Rug Pull Indicators
- Owner can remove liquidity at will
- Single address controls majority of supply
- Liquidity not locked or LP tokens held by deployer
- Contract can pause trading permanently

### Hidden Taxes
- Undisclosed buy/sell taxes
- Dynamic tax rates controlled by owner
- Transfer fees not mentioned in docs
- Blacklist function allowing selective taxation

### Liquidity Issues
- Liquidity not locked (can be removed)
- Liquidity provider tokens owned by single address
- No time-lock on liquidity removal
- Concentrated liquidity ownership

### Holder Concentration
- Top 10 holders own >70% of supply
- Deployer/team holds excessive allocation
- Single address can crash price
- Insufficient distribution to retail

## Use Cases

### Pre-Trade Verification
Verify every token before executing a trade to avoid scams and rug pulls.

### Portfolio Risk Assessment
Scan all tokens in portfolio to identify holdings with elevated risk profiles.

### DeFi Protocol Integration
Verify tokens before adding them to liquidity pools or lending protocols.

### Smart Contract Auditing
Pre-audit tokens your smart contract will interact with.

### Compliance & Due Diligence
Generate audit trails for token interactions required by compliance frameworks.

## Pricing Comparison

| Service | Cost per Scan | Speed | Automation |
|---------|---------------|-------|------------|
| Traditional Audit | $75-500 | 1-3 days | Manual |
| Manual Review | $0 (your time) | 30-60 min | Manual |
| **Cybercentry** | **$1.00** | **15-45 sec** | **Automated** |

**ROI**: One prevented rug pull (avg loss: $2,500) pays for 2,500 scans.

## Quick Start Summary

```bash
# 1. Install the ACP skill from GitHub
Install the skill from https://github.com/Virtual-Protocol/openclaw-acp
git clone https://github.com/Virtual-Protocol/openclaw-acp
cd openclaw-acp
npm install

# 2. Authenticate
acp setup

# 3. Find Cybercentry Ethereum Token Verification service
acp browse "Cybercentry Ethereum Token Verification" --json

# 4. Submit token for verification (MUST verify wallet first!)
# Get verified wallet: https://clawhub.ai/Cybercentry/cybercentry-ethereum-token-verification
acp job create 0xVERIFIED_WALLET cybercentry-ethereum-token-verification \
  --requirements '{"platform": 1, "chain": 1, "contract_address": "0x..."}' \
  --json

# 5. Get results (15-45 seconds)
acp job status <jobId> --json

# 6. Use rug_pull_risk_score and safe_to_interact to make decisions
```

## Integration Examples

### Python Trading Bot

```python
import subprocess
import json
import time

def verify_token(contract_address, platform_id=1, chain_id=1):
    """Verify token before trading"""
    
    # Create verification job
    requirements = json.dumps({
        "platform": platform_id,
        "chain": chain_id,
        "contract_address": contract_address
    })
    
  # CRITICAL: Get verified wallet from https://clawhub.ai/Cybercentry/cybercentry-ethereum-token-verification
  verified_wallet = "0xYOUR_VERIFIED_WALLET_HERE"  # YOU MUST VERIFY THIS
  
  result = subprocess.run([
    "acp", "job", "create",
    verified_wallet,
    "cybercentry-ethereum-token-verification",
    "--requirements", requirements,
        "--json"
    ], capture_output=True, text=True)
    
    job_id = json.loads(result.stdout)["jobId"]
    
    # Poll for completion
    while True:
        result = subprocess.run([
            "acp", "job", "status", job_id, "--json"
        ], capture_output=True, text=True)
        
        status = json.loads(result.stdout)
        if status["phase"] == "COMPLETED":
            return status["deliverable"]
        
        time.sleep(5)

# Use in trading logic
token = "0x1234..."
verification = verify_token(token)

if verification["rug_pull_risk_score"] > 70:
    print(f"BLOCKED: High rug pull risk")
elif not verification["safe_to_interact"]:
    print(f"BLOCKED: Token flagged unsafe")
else:
    print(f"APPROVED: Executing trade")
    execute_trade(token)
```

## Resources

- Cybercentry Profile: https://clawhub.ai/Cybercentry/cybercentry-ethereum-token-verification
- Twitter/X: https://x.com/cybercentry
- ACP Platform: https://app.virtuals.io
- Etherscan: https://etherscan.io
- BSCScan: https://bscscan.com
- Supported Explorers: See Platform & Chain Reference above

## About the Service

The Cybercentry Ethereum Token Verification service uses AI-powered analysis to detect vulnerabilities and scams in EVM token smart contracts. Available exclusively on the Virtuals Protocol ACP marketplace for just $1.00 per scan - making enterprise-grade token security accessible to all agents and traders.
