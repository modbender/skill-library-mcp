# MoonfunSDK - BSC Meme Token Creation Tool

Professional Python SDK for creating and trading Meme tokens on Binance Smart Chain with AI-powered image generation.

## Overview

MoonfunSDK enables automated creation of Meme tokens with AI-generated images on BSC. The SDK handles image generation, platform integration, and blockchain transactions through a simple Python interface.

## Installation

```bash
pip install moonfun-sdk
```

**Requirements:**
- Python 3.8+
- BNB balance ≥ 0.011 (0.01 creation fee + gas)

## Quick Start

```python
import os
from moonfun_sdk import MoonfunSDK

# Initialize with private key
sdk = MoonfunSDK(private_key=os.getenv('PRIVATE_KEY'))

# Create Meme token
result = sdk.create_meme(prompt="A happy cat celebrating")

print(f"Token: {result['token_address']}")
print(f"View: https://moonn.fun/detail?address={result['token_address']}")
```

## Core Features

### Token Creation (Stable)

- AI-generated meme images
- Automatic title and symbol generation
- One-function deployment to BSC
- Integrated with MoonnFun platform

### Token Trading (Experimental)

- Buy tokens with BNB
- Sell tokens for BNB
- Automatic slippage handling
- Balance queries

## API Methods

### create_meme()

```python
sdk.create_meme(
    prompt: str,              # Meme description
    symbol: str = None,       # Auto-generated if None
    description: str = None   # Auto-generated if None
) -> dict
```

**Returns:**
- `token_address`: Contract address
- `token_id`: Platform token ID
- `tx_hash`: Creation transaction hash
- `name`: Token name
- `symbol`: Token symbol
- `image_url`: Hosted image URL

### buy_token() / sell_token()

```python
sdk.buy_token(token_address: str, bnb_amount: float, slippage: float = 0.1)
sdk.sell_token(token_address: str, amount: int, slippage: float = 0.1)
```

### Balance Queries

```python
sdk.get_balance()                           # Returns BNB balance
sdk.get_token_balance(token_address: str)   # Returns token balance (wei)
```

## Configuration

### Default Configuration

SDK comes pre-configured with hosted services:
- Image API: Hosted service for AI generation
- Platform: https://moonn.fun
- BSC RPC: Public BSC dataseed node

No additional configuration needed for basic usage.

### Custom Configuration

```python
sdk = MoonfunSDK(
    private_key="0x...",
    image_api_url="https://custom-api.com",     # Optional
    platform_url="https://moonn.fun",           # Default
    rpc_url="https://bsc-dataseed.bnbchain.org" # Default
)
```

### Environment Variables

Supported environment variables:
- `PRIVATE_KEY` (required): Ethereum private key
- `MOONFUN_IMAGE_API_URL` (optional): Custom image API endpoint

## Security

### Private Key Handling

**Private keys are used locally only** for:
1. Transaction signing (via eth_account library)
2. Message signing for authentication

**Private keys are NEVER:**
- Transmitted over network
- Stored to disk
- Logged to console

### Code Verification

Users can audit private key usage in source code:
- `auth.py`: Local signing with eth_account
- `image_api.py`: Sends only signature + address
- `platform.py`: Sends only signature + address
- `blockchain.py`: Local transaction signing via web3.py

### Best Practices

```python
# ✅ Use environment variables
sdk = MoonfunSDK(private_key=os.getenv('PRIVATE_KEY'))

# ✅ Use dedicated wallets
# Create new wallet for SDK operations only

# ❌ Never hardcode keys
sdk = MoonfunSDK(private_key="0x123...")  # Don't do this
```

## Network Details

### BSC Mainnet

- Chain ID: 56
- Native Token: BNB
- Explorer: https://bscscan.com
- RPC: https://bsc-dataseed.bnbchain.org

### Smart Contracts

- Router: `0x953C65358a8666617C66327cb18AD02126b2AAA5`
- WBNB: `0xBB4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c`

All addresses are public and verifiable on BSCScan.

### Gas Costs

- Token creation: ~0.011 BNB (0.01 fee + 0.001 gas)
- Buy/sell: ~0.0005-0.001 BNB per transaction

## Error Handling

```python
from moonfun_sdk import (
    InsufficientBalanceError,
    AuthenticationError,
    TransactionFailedError
)

try:
    result = sdk.create_meme("A funny cat")
except InsufficientBalanceError:
    print("Need more BNB (minimum 0.011)")
except AuthenticationError:
    print("Signature verification failed")
except TransactionFailedError:
    print("Blockchain transaction failed")
```

## Hosted Services

The SDK uses these services:

1. **Image Generation API**
   - Secured with cryptographic signatures
   - Balance-gated (minimum 0.011 BNB)
   - Timestamp-bound requests
   - Default endpoint: `http://moonfun.site`
   - Users can deploy custom instances

2. **MoonnFun Platform**
   - Public token launchpad
   - Metadata and image storage
   - URL: https://moonn.fun

3. **BSC Network**
   - Public blockchain
   - Decentralized infrastructure

## Dependencies

Core dependencies:
- `web3>=6.0.0` - Ethereum interaction
- `eth-account>=0.8.0` - Private key management
- `requests>=2.28.0` - HTTP client
- `httpx>=0.24.0` - Async HTTP client

All dependencies are widely used and audited libraries.

## Building from Source

```bash
# Clone repository
git clone <repository-url>
cd moonfun-sdk/python

# Review source code
cat moonfun_sdk/auth.py        # Private key handling
cat moonfun_sdk/image_api.py   # API requests
cat moonfun_sdk/platform.py    # Platform integration

# Install from source
pip install -e .
```

## Changelog

### v1.0.6 (Current)
- Token tag set to "Ai Agent"
- Improved categorization

### v1.0.5
- Enhanced authentication mechanism
- Optimized login flow

### v1.0.4
- Support for low-liquidity token selling
- Trading marked as experimental

## Troubleshooting

| Issue | Solution |
|-------|----------|
| InsufficientBalanceError | Add BNB (minimum 0.011) |
| AuthenticationError | Check private key format (needs 0x prefix) |
| TransactionFailedError | Increase slippage or check gas |
| RPCConnectionError | Try different RPC endpoint |

## Resources

- Platform: https://moonn.fun
- BSC Explorer: https://bscscan.com
- Documentation: See README.md
- Security Guide: See SECURITY.md

## License

MIT License

## Disclaimer

This SDK interacts with blockchain and requires real BNB. Users should:
- Test with small amounts first
- Use dedicated wallets
- Review source code
- Understand blockchain risks

Trading features are experimental and may have issues with new/low-liquidity tokens.
