# MoonfunSDK - Open Source Release

This package contains the complete source code for MoonfunSDK, a professional Python SDK for creating and trading Meme tokens on Binance Smart Chain.

## What's Included

```
new_hub_skill/
├── SKILL.md                  # Quick reference guide
├── README.md                 # This file
├── PROJECT_STRUCTURE.txt     # Directory structure
└── python/                   # Python SDK source code
    ├── README.md             # Full documentation
    ├── SECURITY.md           # Security and audit guide
    ├── CHANGELOG.md          # Version history
    ├── LICENSE               # MIT License
    ├── requirements.txt      # Dependencies
    ├── setup.py              # Installation script
    ├── env.example           # Configuration template
    ├── moonfun_sdk/          # Source code
    │   ├── auth.py           # Private key & signing
    │   ├── blockchain.py     # BSC interaction
    │   ├── client.py         # Main SDK class
    │   ├── constants.py      # Contract addresses & ABIs
    │   ├── exceptions.py     # Error definitions
    │   ├── image_api.py      # AI image generation
    │   ├── platform.py       # Platform integration
    │   └── trading.py        # Buy/sell operations
    ├── examples/             # Example scripts
    │   ├── README.md         # Example documentation
    │   ├── example_create_meme.py
    │   ├── example_trading.py
    │   ├── debug_api_request.py
    │   └── debug_login.py
    └── tests/                # Test suite
```

## Key Features

### ✅ Complete Source Code
- All SDK source files included
- No obfuscation or minification
- Auditable and verifiable

### ✅ Security Focused
- Private keys never leave your machine
- Local transaction signing only
- Detailed security documentation
- Code audit guide included

### ✅ Well Documented
- Comprehensive README with examples
- API reference documentation
- Security best practices guide
- Example scripts with comments

### ✅ Production Ready
- MIT License
- Stable token creation API
- Experimental trading features
- Proper error handling

## Quick Start

### Installation

```bash
cd python/
pip install -e .
```

### Basic Usage

```python
import os
from moonfun_sdk import MoonfunSDK

# Initialize SDK
sdk = MoonfunSDK(private_key=os.getenv('PRIVATE_KEY'))

# Create Meme token
result = sdk.create_meme(prompt="A happy cat")

print(f"Token: {result['token_address']}")
```

## Documentation

1. **Quick Reference**: Read `SKILL.md` for API overview
2. **Full Documentation**: Read `python/README.md` for complete guide
3. **Security Guide**: Read `python/SECURITY.md` for audit information
4. **Examples**: Check `python/examples/` for usage examples

## Security Verification

### Private Key Handling

Users can verify private key security by reviewing:

1. **`python/moonfun_sdk/auth.py`**
   - Lines 15-30: Private key stored in eth_account.Account object
   - Lines 45-60: Local message signing (key never transmitted)

2. **`python/moonfun_sdk/image_api.py`**
   - Lines 59-68: Only address and signature sent to API
   - Private key NOT in request payload

3. **`python/moonfun_sdk/platform.py`**
   - Lines 59-65: Authentication sends signature only
   - Private key NOT transmitted

4. **`python/moonfun_sdk/blockchain.py`**
   - Lines 80-95: Local transaction signing via web3.py
   - Standard Ethereum signing flow

### Network Inspection

Users can inspect network traffic to verify no private key transmission:

```bash
# Use mitmproxy or similar tool
pip install mitmproxy
mitmproxy

# All requests will show only: address, signature, timestamp
# No private key in any request
```

## Configuration

### Default Configuration (Works Out of Box)

The SDK uses these defaults:
- Image API: `http://moonfun.site` (hosted service)
- Platform: `https://moonn.fun`
- BSC RPC: `https://bsc-dataseed.bnbchain.org`

### Custom Configuration

Users can override defaults:

```python
sdk = MoonfunSDK(
    private_key="0x...",
    image_api_url="https://your-api.com",  # Custom image API
    platform_url="https://moonn.fun",      # Default platform
    rpc_url="https://your-rpc.com"         # Custom RPC
)
```

Or use environment variables:

```bash
export MOONFUN_IMAGE_API_URL="https://your-api.com"
export PRIVATE_KEY="0x..."
```

## Hosted Services

The SDK integrates with these services:

### 1. Image Generation API (`http://moonfun.site`)

**Purpose**: AI-powered meme image generation

**Security**:
- Requests authenticated with cryptographic signatures
- Requires minimum BNB balance (anti-spam)
- Timestamp-bound to prevent replay attacks

**What is sent**:
- Wallet address (public)
- Request signature (proves ownership)
- Timestamp (prevents replay)
- Prompt text

**What is NOT sent**:
- Private key (never transmitted)
- Transaction data
- Personal information

**Self-hosting**: Users can deploy their own image API instance

### 2. MoonnFun Platform (`https://moonn.fun`)

**Purpose**: Token metadata storage and indexing

**What is sent**:
- Token metadata (name, symbol, description)
- Uploaded images
- Creator address (public)

**What is NOT sent**:
- Private keys
- Wallet balances
- Transaction history

### 3. BSC Network

**Purpose**: Blockchain for token deployment

**Interaction**:
- Public RPC nodes
- Signed transactions only
- Standard web3.py library

## Dependencies

All dependencies are open source and widely used:

```
web3>=6.0.0         # 50M+ downloads, official Ethereum library
eth-account>=0.8.0  # 50M+ downloads, cryptographic signing
requests>=2.28.0    # 500M+ downloads, HTTP client
httpx>=0.24.0       # 10M+ downloads, async HTTP
```

Check vulnerabilities:
```bash
pip install safety
safety check -r python/requirements.txt
```

## Building from Source

```bash
# Review source code first
cd python/
cat moonfun_sdk/auth.py      # Check private key handling
cat moonfun_sdk/image_api.py # Check API requests
cat moonfun_sdk/platform.py  # Check platform integration

# Install dependencies
pip install -r requirements.txt

# Install SDK
pip install -e .

# Run tests
python -m pytest tests/

# Build distribution
python setup.py sdist bdist_wheel
```

## Testing

```bash
# Set environment
export PRIVATE_KEY="0x..."

# Run examples
cd python/examples/
python example_create_meme.py
```

## Comparison with Previous Concerns

### Before (Closed Source)

❌ No source code available  
❌ Cannot verify private key handling  
❌ Hardcoded API URLs  
❌ Cannot audit security  
❌ "Black box" installation  

### After (Open Source)

✅ Complete source code included  
✅ Private key handling verifiable in auth.py  
✅ All API endpoints documented  
✅ Full security audit guide provided  
✅ Transparent and auditable  

## License

MIT License - See `python/LICENSE` for details

## Support and Resources

- **Platform**: https://moonn.fun
- **BSC Explorer**: https://bscscan.com
- **Documentation**: `python/README.md`
- **Security**: `python/SECURITY.md`
- **Examples**: `python/examples/`

## Changelog

See `python/CHANGELOG.md` for version history.

Current version: 1.0.6

## Contributing

This SDK is open source under MIT License. Users can:
- Review and audit the code
- Submit bug reports
- Propose improvements
- Fork and modify
- Self-host components

## Disclaimer

**Important Notes:**

1. **Blockchain Risks**: This SDK interacts with real blockchain and requires real BNB
2. **Private Keys**: Users are responsible for securing their private keys
3. **Testing**: Always test with small amounts first
4. **Experimental Features**: Trading functions are experimental
5. **No Warranty**: Provided "as-is" without warranty (see LICENSE)

## Security Contact

For security vulnerabilities, please:
1. Do NOT open public issues
2. Contact maintainers directly
3. Allow reasonable time for fixes

## Summary

This package provides complete, auditable source code for MoonfunSDK with:
- Full documentation
- Security audit guide
- Working examples
- MIT License
- No hidden code

Users can verify all security claims by reviewing the source code themselves.
