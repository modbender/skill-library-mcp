---
name: erc8004-identity
version: 1.0.0
description: Maintain your agent on-chain identity (ERC-8004) on BNB Chain. Register, check status, and manage your agent metadata securely using the BNBAgent SDK.
---

# ERC-8004 Agent Identity

This skill enables your agent to register and manage its own on-chain identity on BNB Chain using the ERC-8004 standard.

## Features

- **Self-Registration:** Register yourself as an agent (ERC-8004).
- **Gasless:** Uses MegaFuel Paymaster (BSC Testnet only) for zero-cost registration.
- **Identity Management:** Update your metadata (URI), endpoints, and description.
- **Verification:** Users can verify your agent status on [8004scan.io](https://testnet.8004scan.io).

## Installation

This skill requires the `bnbagent` Python SDK.

```bash
# Install bnbagent SDK (from test.pypi.org as per release)
pip install --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple \
  bnbagent==0.1.6

# Or using uv (recommended for speed)
uv pip install --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple \
  bnbagent==0.1.6
```

## Security Note

This skill manages a wallet specifically for your agent's identity.
- **Password:** The wallet is encrypted. Set `WALLET_PASSWORD` env var or provide it when prompted.
- **Private Key:** Stored locally in `.bnbagent_state` (encrypted). Do not share this file.

## Usage

Create a script (or ask me to create one) to manage your identity.

### 1. Register (First Time)

If you haven't registered on-chain yet:

```python
import os
from bnbagent import ERC8004Agent, EVMWalletProvider, AgentEndpoint

# 1. Setup Wallet & SDK
password = os.getenv("WALLET_PASSWORD", "default-secure-password")
wallet = EVMWalletProvider(password=password)
sdk = ERC8004Agent(wallet_provider=wallet, network="bsc-testnet")

# 2. Define Your Identity
agent_uri = sdk.generate_agent_uri(
    name="My Agent Name",
    description="I am an autonomous agent running on OpenClaw.",
    endpoints=[
        AgentEndpoint(
            name="activity",
            endpoint="https://moltbook.com/u/MyAgentName", # Example: Link to your social profile
            version="1.0.0"
        )
    ]
)

# 3. Register on BNB Chain (Gasless via Paymaster)
print("Registering...")
result = sdk.register_agent(agent_uri=agent_uri)
print(f"Success! Agent ID: {result['agentId']}")
print(f"View registered agents: https://testnet.8004scan.io/agents?chain=97")
```

### 2. Check Status

```python
# Check if you are already registered locally
info = sdk.get_local_agent_info("My Agent Name")
if info:
    print(f"I am registered! Agent ID: {info['agent_id']}")
    # Get on-chain details
    chain_info = sdk.get_agent_info(info['agent_id'])
    print(f"On-chain Address: {chain_info['agentAddress']}")
```

### 3. Update Identity

If your endpoints or description change:

```python
local_info = sdk.get_local_agent_info("My Agent Name")
if local_info:
    agent_id = local_info['agent_id']
    
    # Generate new URI
    new_uri = sdk.generate_agent_uri(
        name="My Agent Name",
        description="Updated description.",
        endpoints=[...],
        agent_id=agent_id
    )
    
    # Update on-chain
    sdk.set_agent_uri(agent_id=agent_id, agent_uri=new_uri)
    print("Identity updated successfully.")
```

## Explorers

- **BSC Testnet:** https://testnet.8004scan.io/agents?chain=97
- **BSC Mainnet:** https://www.8004scan.io/agents?chain=56 (Coming Soon)
