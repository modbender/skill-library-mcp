---
name: x402-compute
version: 1.0.7
description: |
  This skill should be used when the user asks to "provision GPU instance",
  "spin up a cloud server", "list compute plans", "browse GPU pricing",
  "extend compute instance", "destroy server instance", "check instance status",
  "list my instances", or manage x402 Singularity Compute / x402Compute
  infrastructure. Handles GPU and VPS provisioning with USDC payment on Base
  or Solana networks via the x402 payment protocol.
homepage: https://studio.x402layer.cc/docs/agentic-access/x402-compute
metadata:
  clawdbot:
    emoji: "🖥️"
    homepage: https://compute.x402layer.cc
    os:
      - linux
      - darwin
    requires:
      bins:
        - python3
      env:
        # Option A — Base/EVM payments (provide these OR Option B, not both)
        - PRIVATE_KEY        # EVM private key for signing payments (0x...)
        - WALLET_ADDRESS     # EVM wallet address (0x...)
        # Option B — Solana payments (alternative to Option A)
        - SOLANA_SECRET_KEY        # Solana signer key (base58 or JSON byte array)
        - SOLANA_WALLET_ADDRESS    # Solana public address
        # Optional — preferred for routine management without exposing private keys
        - COMPUTE_API_KEY   # Reusable API key (create once via create_api_key.py)
    credentials:
      primary: COMPUTE_API_KEY   # Recommended: use API key for management over raw private keys
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - WebFetch
---


# x402 Singularity Compute

Provision and manage GPU/VPS instances paid with USDC via the x402 payment protocol.

**Base URL:** `https://compute.x402layer.cc`
**Networks:** Base (EVM) • Solana
**Currency:** USDC
**Protocol:** HTTP 402 Payment Required

**Access Note:** Preferred access is SSH public key. If no SSH key is provided, a one-time password fallback can be fetched once via API.

---

## Quick Start

### 1. Install Dependencies
```bash
pip install -r {baseDir}/requirements.txt
```

### 2. Set Up Wallet

#### Option A: Base (EVM) Private Key
```bash
export PRIVATE_KEY="0x..."
export WALLET_ADDRESS="0x..."
```

#### Option B: Solana Private Key
```bash
export SOLANA_SECRET_KEY="base58-or-json-array"
export SOLANA_WALLET_ADDRESS="YourSolanaAddress"
export COMPUTE_AUTH_CHAIN="solana"
```

Create `COMPUTE_API_KEY` (optional) for management endpoints:
```bash
python {baseDir}/scripts/create_api_key.py --label "my-agent"
```

---

## ⚠️ Security Notice

> **IMPORTANT**: This skill handles private keys for signing blockchain transactions.
>
> - **Never use your primary custody wallet** - Create a dedicated wallet with limited funds
> - **Private keys are used locally only** - They sign transactions locally and are never transmitted
> - **For testing**: Use a throwaway wallet with minimal USDC

---

## Scripts Overview

| Script | Purpose |
|--------|---------|
| `browse_plans.py` | List available GPU/VPS plans with pricing |
| `browse_regions.py` | List deployment regions |
| `provision.py` | Provision a new instance (x402 payment, `--months` or `--days`) |
| `create_api_key.py` | Create an API key for agent access (optional) |
| `list_instances.py` | List your active instances |
| `instance_details.py` | Get details for a specific instance |
| `get_one_time_password.py` | Retrieve one-time root password fallback |
| `extend_instance.py` | Extend instance lifetime (x402 payment) |
| `destroy_instance.py` | Destroy an instance |
| `solana_signing.py` | Internal helper for Solana x402 payment signing |

---

## Instance Lifecycle

```
Browse Plans → Provision (pay USDC) → Active → Extend / Destroy → Expired
```

Instances expire after their prepaid duration. Extend before expiry to keep them running.

---

## Workflows

### A. Browse and Provision

```bash
# List GPU plans
python {baseDir}/scripts/browse_plans.py

# Filter by type (gpu/vps/high-performance)
python {baseDir}/scripts/browse_plans.py --type vcg

# Check available regions
python {baseDir}/scripts/browse_regions.py

# Generate a dedicated SSH key once (recommended for agents)
ssh-keygen -t ed25519 -N "" -f ~/.ssh/x402_compute

# Provision an instance for 1 month (triggers x402 payment)
python {baseDir}/scripts/provision.py vcg-a100-1c-2g-6gb lax --months 1 --label "my-gpu" --ssh-key-file ~/.ssh/x402_compute.pub

# Provision a daily instance (cheaper, use-and-throw)
python {baseDir}/scripts/provision.py vc2-1c-1gb ewr --days 1 --label "test-daily" --ssh-key-file ~/.ssh/x402_compute.pub

# Provision for 3 days
python {baseDir}/scripts/provision.py vc2-1c-1gb ewr --days 3 --label "short-task" --ssh-key-file ~/.ssh/x402_compute.pub

# Provision on Solana
python {baseDir}/scripts/provision.py vc2-1c-1gb ewr --months 1 --label "my-sol-vps" --network solana --ssh-key-file ~/.ssh/x402_compute.pub

# ⚠️ After provisioning, wait 2-3 minutes for Vultr to complete setup
# Then fetch your instance details (IP, status):
python {baseDir}/scripts/instance_details.py <instance_id>
```

### B. Manage Instances

```bash
# Optional: create a reusable API key (avoids message signing each request)
python {baseDir}/scripts/create_api_key.py --label "my-agent"

# List all your instances
python {baseDir}/scripts/list_instances.py

# Get details for one instance
python {baseDir}/scripts/instance_details.py <instance_id>

# Optional fallback if no SSH key was provided during provisioning
python {baseDir}/scripts/get_one_time_password.py <instance_id>

# Extend by 1 day
python {baseDir}/scripts/extend_instance.py <instance_id> --hours 24

# Extend by 1 month
python {baseDir}/scripts/extend_instance.py <instance_id> --hours 720

# Extend on Solana
python {baseDir}/scripts/extend_instance.py <instance_id> --hours 720 --network solana

# Destroy
python {baseDir}/scripts/destroy_instance.py <instance_id>
```

---

## x402 Payment Flow

1. Request provision/extend → server returns `HTTP 402` with payment requirements
2. Script signs payment locally:
   - Base: USDC `TransferWithAuthorization` (EIP-712)
   - Solana: signed SPL transfer transaction payload
3. Script resends request with `X-Payment` header containing signed payload
4. Server verifies payment, settles on-chain, provisions/extends instance

For Solana, transient facilitator failures can happen. Retry once or twice if you get a temporary 5xx verify error.

---

## Plan Types

| Type | Plan Prefix | Description |
|------|-------------|-------------|
| GPU | `vcg-*` | GPU-accelerated (A100, H100, etc.) |
| VPS | `vc2-*` | Standard cloud compute |
| High-Perf | `vhp-*` | High-performance dedicated |
| Dedicated | `vdc-*` | Dedicated bare-metal |

---

## Environment Reference

| Variable | Required For | Description |
|----------|--------------|-------------|
| `PRIVATE_KEY` | Base payments | EVM private key (0x...) |
| `WALLET_ADDRESS` | Base mode | Base wallet address (0x...) |
| `SOLANA_SECRET_KEY` | Solana mode | Solana signer key (base58 or JSON byte array) |
| `SOLANA_WALLET_ADDRESS` | Solana mode | Solana wallet address (optional if derivable from secret) |
| `COMPUTE_AUTH_CHAIN` | Solana/base auth override | `base` or `solana` |
| `COMPUTE_API_KEY` | Optional | Reusable API key for compute management endpoints |

---

## API Reference

For full endpoint details, see [references/api-reference.md](references/api-reference.md).

---

## Resources

- 📖 **Documentation:** [studio.x402layer.cc/docs/agentic-access/x402-compute](https://studio.x402layer.cc/docs/agentic-access/x402-compute)
- 🖥️ **Compute Dashboard:** [compute.x402layer.cc](https://compute.x402layer.cc)
- 🌐 **x402 Studio:** [studio.x402layer.cc](https://studio.x402layer.cc)
