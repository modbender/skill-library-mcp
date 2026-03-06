# MoonfunSDK - Professional Meme Token Creation SDK

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Professional Python SDK for creating and trading Meme tokens on BSC (Binance Smart Chain) with AI-powered image generation.

## Features

- ✅ **Stable**: Create tokens with AI-generated images
- ⚠️ **Experimental**: Buy/sell tokens (slippage handling on new tokens)
- 🔒 **Secure**: Private keys never leave your machine
- 🎨 **AI-Powered**: Automatic meme image and title generation

## Installation

```bash
pip install moonfun-sdk
```

**Requirements:**
- Python 3.8 or higher
- BNB balance ≥ 0.011 (0.01 creation fee + gas)

## Quick Start

```python
from moonfun_sdk import MoonfunSDK

# Initialize with your private key
sdk = MoonfunSDK(private_key="0x...")

# Create a Meme token
result = sdk.create_meme(prompt="A happy cat celebrating")

print(f"Token Address: {result['token_address']}")
print(f"View: https://moonn.fun/detail?address={result['token_address']}")
```

## Configuration

### Default Configuration

The SDK comes pre-configured with a hosted image generation service. No additional configuration needed for basic usage.

### Custom Configuration (Optional)

You can override default settings:

```python
sdk = MoonfunSDK(
    private_key="0x...",
    image_api_url="https://your-custom-api.com",  # Optional: custom image API
    platform_url="https://moonn.fun",              # Default platform
    rpc_url="https://bsc-dataseed.bnbchain.org"    # Default BSC RPC
)
```

### Environment Variables (Optional)

For environment-based configuration:

```bash
export PRIVATE_KEY="0x..."
export MOONFUN_IMAGE_API_URL="https://your-custom-api.com"  # Optional
```

```python
import os
from moonfun_sdk import MoonfunSDK

sdk = MoonfunSDK(
    private_key=os.getenv('PRIVATE_KEY'),
    image_api_url=os.getenv('MOONFUN_IMAGE_API_URL')  # Falls back to default if not set
)
```

## API Reference

### Initialization

```python
MoonfunSDK(
    private_key: str,
    image_api_url: str = "http://moonfun.site",      # Hosted service
    platform_url: str = "https://moonn.fun",
    chain: str = "bsc",
    rpc_url: str = "https://bsc-dataseed.bnbchain.org"
)
```

**Parameters:**
- `private_key` (required): Ethereum private key with 0x prefix
- `image_api_url` (optional): Custom image generation API endpoint
- `platform_url` (optional): MoonnFun platform URL
- `chain` (optional): Blockchain identifier
- `rpc_url` (optional): Custom BSC RPC endpoint

**Raises:**
- `ValueError`: Invalid private key format
- `RPCConnectionError`: Cannot connect to blockchain RPC

### create_meme()

Create a Meme token with AI-generated image.

```python
sdk.create_meme(
    prompt: str,
    symbol: str = None,       # Auto-generated from title
    description: str = None   # Auto-generated from prompt
) -> dict
```

**Returns:**
```python
{
    'success': True,
    'token_id': 12345,
    'token_address': '0x...',
    'tx_hash': '0x...',
    'name': 'Meme Name',
    'symbol': 'MEME',
    'image_url': 'https://...',
    'meme_title': 'AI-generated Title'
}
```

**Process Flow:**
1. Generate image and title using AI (20-30s)
2. Login to platform with signed message
3. Upload image to platform storage
4. Create token metadata
5. Deploy token contract on BSC
6. Confirm creation for fast indexing

### buy_token() ⚠️ Experimental

```python
sdk.buy_token(
    token_address: str,
    bnb_amount: float,
    slippage: float = 0.1  # 10%
) -> dict
```

**Note**: Price estimation may fail on new tokens (holders=0). SDK automatically handles this with fallback logic.

### sell_token() ⚠️ Experimental

```python
sdk.sell_token(
    token_address: str,
    amount: int,           # Token amount in wei
    slippage: float = 0.1
) -> dict
```

**Note**: Automatically approves router before selling. Use with caution on low-liquidity tokens.

### Balance Queries

```python
# Get BNB balance
balance = sdk.get_balance()  # Returns float

# Get token balance
token_balance = sdk.get_token_balance(token_address)  # Returns int (wei)
```

## Security

### Private Key Handling

**⚠️ CRITICAL: Your private key never leaves your machine.**

The SDK uses your private key **only** for:
1. **Local transaction signing** via `eth_account` library
2. **Message signing** for platform authentication

**What is NOT sent:**
- ❌ Private key is NEVER transmitted over network
- ❌ Private key is NEVER stored to disk
- ❌ Private key is NEVER logged

**Verification:**
You can audit the source code to verify private key usage:
- `auth.py`: Uses `eth_account.Account` for local signing only
- `image_api.py`: Sends only signature + address (line 66-67)
- `platform.py`: Sends only signature + address (line 62-64)
- `blockchain.py`: Uses web3.py for local transaction signing

### Best Practices

```python
# ✅ RECOMMENDED: Use environment variables
import os
sdk = MoonfunSDK(private_key=os.getenv('PRIVATE_KEY'))

# ✅ RECOMMENDED: Use dedicated wallet for trading
# Create a new wallet specifically for SDK operations

# ❌ AVOID: Hardcoding private keys
sdk = MoonfunSDK(private_key="0x123...")  # Never do this!

# ❌ AVOID: Committing .env files
# Always add .env to .gitignore
```

### Hosted Services

The SDK uses the following services:

1. **Image Generation API** (`http://moonfun.site`):
   - Secured with cryptographic signatures
   - Requires minimum BNB balance (anti-spam)
   - Timestamp-bound requests (anti-replay)
   - You can deploy your own instance

2. **MoonnFun Platform** (`https://moonn.fun`):
   - Public token launchpad
   - Handles metadata storage
   - Open source smart contracts

3. **BSC Network**:
   - Public blockchain
   - Decentralized and permissionless

## Error Handling

```python
from moonfun_sdk import (
    MoonfunSDK,
    InsufficientBalanceError,
    AuthenticationError,
    TransactionFailedError,
    LoginError,
    UploadError
)

try:
    sdk = MoonfunSDK(private_key=os.getenv('PRIVATE_KEY'))
    result = sdk.create_meme(prompt="A funny cat")
    
except InsufficientBalanceError as e:
    print(f"Need more BNB: {e}")
    
except AuthenticationError as e:
    print(f"Signature verification failed: {e}")
    
except TransactionFailedError as e:
    print(f"Blockchain transaction failed: {e}")
```

## Complete Example

```python
import os
from moonfun_sdk import MoonfunSDK

# Initialize SDK
sdk = MoonfunSDK(private_key=os.getenv('PRIVATE_KEY'))

print(f"Wallet Address: {sdk.address}")
print(f"BNB Balance: {sdk.get_balance():.6f}")

# Create Meme token
result = sdk.create_meme(
    prompt="A shocked cat looking at crypto charts"
)

token_address = result['token_address']
print(f"\n✅ Token Created: {token_address}")
print(f"View: https://moonn.fun/detail?address={token_address}")

# Buy tokens (experimental)
sdk.buy_token(
    token_address=token_address,
    bnb_amount=0.01,
    slippage=0.1
)

# Check balance
balance = sdk.get_token_balance(token_address)
print(f"Token Balance: {balance / 10**18:.2f}")

# Sell half (experimental)
sdk.sell_token(
    token_address=token_address,
    amount=balance // 2,
    slippage=0.1
)
```

## Network Information

### BSC Mainnet

- **Chain ID**: 56
- **Native Token**: BNB
- **Explorer**: https://bscscan.com
- **RPC**: https://bsc-dataseed.bnbchain.org (public)

### Gas Fees

- **Token Creation**: ~0.011 BNB (0.01 fee + 0.001 gas)
- **Buy/Sell**: ~0.0005-0.001 BNB per transaction
- Gas is automatically estimated with safety buffer

### Smart Contracts

- **Router**: `0x953C65358a8666617C66327cb18AD02126b2AAA5`
- **WBNB**: `0xBB4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c`
- All contract addresses are public and verifiable on BSCScan

## Testing

### Basic Test

```bash
export PRIVATE_KEY="0x..."

python -c "
from moonfun_sdk import MoonfunSDK
import os

sdk = MoonfunSDK(private_key=os.getenv('PRIVATE_KEY'))
print(f'SDK initialized for: {sdk.address}')
print(f'Balance: {sdk.get_balance():.6f} BNB')
"
```

### Running Examples

```bash
cd examples/
python create_meme.py
```

## Building from Source

If you want to audit the code before using:

```bash
# Clone repository
git clone https://github.com/your-org/moonfun-sdk
cd moonfun-sdk/python

# Review source code
# Pay attention to: auth.py, image_api.py, platform.py

# Install from source
pip install -e .

# Or build package
python setup.py sdist bdist_wheel
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `InsufficientBalanceError` | Add BNB to wallet (minimum 0.011) |
| `AuthenticationError` | Check private key format (needs 0x prefix) |
| `TransactionFailedError` | Increase slippage or check gas |
| `RPCConnectionError` | Try different RPC endpoint |
| `getAmountOut failed` | Normal for new tokens - SDK auto-handles |

## Architecture

```
MoonfunSDK
├── auth.py           # Private key management & signing
├── image_api.py      # AI image generation client
├── platform.py       # MoonnFun platform client
├── blockchain.py     # BSC interaction (web3.py)
├── trading.py        # Buy/sell logic
├── constants.py      # Contract addresses & ABIs
└── exceptions.py     # Custom error types
```

## Changelog

### v1.0.6 (Current)
- Token tag set to "Ai Agent"
- Improved categorization

### v1.0.5
- Enhanced authentication mechanism
- Optimized login flow

### v1.0.4
- Support selling low-liquidity tokens
- Trading marked as experimental

### v1.0.3
- Support buying new tokens (holders=0)

### v1.0.2
- Simplified initialization
- Dynamic gas estimation

## Resources

- **Platform**: https://moonn.fun
- **BSC Explorer**: https://bscscan.com
- **Documentation**: See `/examples` directory
- **Security**: See `SECURITY.md`

## License

MIT License - See LICENSE file for details.

## Disclaimer

**⚠️ Important:**
- This SDK interacts with blockchain and requires real BNB
- Always test with small amounts first
- Trading features are experimental
- Use dedicated wallets for SDK operations
- Review source code before production use
- The authors are not responsible for financial losses

## Support

For issues or questions:
1. Check error messages and exceptions
2. Verify BNB balance ≥ 0.011
3. Confirm private key format (with 0x prefix)
4. Review source code for security verification
5. Test on BSC Testnet first (if available)
