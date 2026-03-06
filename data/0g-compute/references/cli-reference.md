# 0G Compute CLI Reference

Complete command reference for `0g-compute-cli`. Organized by category.

## Table of Contents

- [Account Management](#account-management)
- [Inference Operations](#inference-operations)
- [Network & Auth](#network--auth)
- [Helper Scripts](#helper-scripts)

---

## Account Management

### get-account

Show account balance overview.

```bash
0g-compute-cli get-account
```

**Output:**
```
Total Balance: 100.0 0G
Locked Balance: 0.0 0G
Available Balance: 100.0 0G
```

### get-sub-account

Check balance for a specific provider sub-account.

```bash
0g-compute-cli get-sub-account --provider <address> --service inference
```

| Flag | Description |
|------|-------------|
| `--provider` | Provider wallet address |
| `--service` | Service type (typically `inference`) |

**Output:**
```
Sub-account balance: 10.0 0G
```

### deposit

Deposit 0G tokens to your main account from wallet.

```bash
0g-compute-cli deposit --amount <0G>
```

| Flag | Description |
|------|-------------|
| `--amount` | Amount in 0G tokens |

**Example:**
```bash
0g-compute-cli deposit --amount 50
```

### transfer-fund

Transfer funds from main account to a provider sub-account.

```bash
0g-compute-cli transfer-fund --provider <address> --amount <0G> --service inference
```

| Flag | Description |
|------|-------------|
| `--provider` | Provider wallet address |
| `--amount` | Amount in 0G tokens |
| `--service` | Service type (typically `inference`) |

**Example:**
```bash
0g-compute-cli transfer-fund --provider 0x1234... --amount 10 --service inference
```

### retrieve-fund

Retrieve funds from sub-accounts back to main account.

```bash
0g-compute-cli retrieve-fund --service inference
```

| Flag | Description |
|------|-------------|
| `--service` | Service type (typically `inference`) |

### refund

Withdraw from main account back to wallet.

```bash
0g-compute-cli refund --amount <0G>
```

| Flag | Description |
|------|-------------|
| `--amount` | Amount in 0G tokens |

---

## Inference Operations

### list-providers

List all available providers with models, prices, and verifiability status.

```bash
0g-compute-cli inference list-providers [options]
```

| Flag | Description |
|------|-------------|
| `--include-invalid` | Include providers without valid TEE signer |

**Output:**
```
Provider: 0x1234...
  Model: llama-3-70b
  Price: 0.001 0G/token
  Verifiable: Yes
  TEE Signer: 0x5678...
```

### list-providers-detail

List providers with additional health and uptime metrics.

```bash
0g-compute-cli inference list-providers-detail [options]
```

| Flag | Description |
|------|-------------|
| `--include-invalid` | Include providers without valid TEE signer |

**Output:**
```
Provider: 0x1234...
  Model: llama-3-70b
  Price: 0.001 0G/token
  Health: Healthy
  Uptime: 99.5%
  Verifiable: Yes
```

### verify

Perform full TEE attestation verification on a provider.

```bash
0g-compute-cli inference verify --provider <address>
```

| Flag | Description |
|------|-------------|
| `--provider` | Provider wallet address |

**Output:**
```
Verifying provider 0x1234...
✓ TEE signer address matches contract
✓ Docker Compose hash verified
✓ DStack TEE attestation passed
Provider verified successfully
```

**Verification checks:**
1. TEE signer address matches on-chain registration
2. Docker Compose hash integrity
3. DStack TEE (Intel TDX) hardware attestation

### download-report

Download raw attestation data from a provider.

```bash
0g-compute-cli inference download-report --provider <address> --output <file>
```

| Flag | Description |
|------|-------------|
| `--provider` | Provider wallet address |
| `--output` | Output file path (JSON format) |

**Example:**
```bash
0g-compute-cli inference download-report --provider 0x1234... --output report.json
```

### get-secret

Retrieve API key/secret for a provider.

```bash
0g-compute-cli inference get-secret --provider <address>
```

| Flag | Description |
|------|-------------|
| `--provider` | Provider wallet address |

**Output:**
```
API Secret: sk-abc123...
```

Use this secret as the `apiKey` when configuring OpenClaw providers.

---

## Network & Auth

### login

Authenticate with a private key.

```bash
0g-compute-cli login --private-key <key>
```

| Flag | Description |
|------|-------------|
| `--private-key` | Wallet private key |

**Important:** The private key is stored in `~/.0g-compute-cli/config.json`. Never expose this file.

### status

Show login status and wallet address.

```bash
0g-compute-cli status
```

**Output:**
```
Logged in: Yes
Wallet Address: 0xabcd...
```

### setup-network

Configure network connection (mainnet or testnet).

```bash
0g-compute-cli setup-network
```

Interactive prompt to select network and RPC endpoint.

### show-network

Display current network configuration.

```bash
0g-compute-cli show-network
```

**Output:**
```
Network: mainnet
RPC Endpoint: https://rpc.0g.ai
```

---

## Scripts

### 0g-price-compare.sh

Compare 0G pricing vs OpenRouter. Requires `python3` and internet access. No API keys needed.

```bash
scripts/0g-price-compare.sh
```

Set `OG_TOKEN_PRICE_USD` env var to override CoinGecko if rate-limited.

---

## Notes

- All monetary values are in 0G tokens
- Provider addresses are Ethereum-style addresses (0x...)
- Sub-account balances are provider-specific; funds must be transferred before use
- TEE verification is critical for ensuring model integrity — always verify new providers
