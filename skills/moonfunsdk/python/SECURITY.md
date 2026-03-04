# Security Policy

## Overview

This document explains how MoonfunSDK handles sensitive data, particularly private keys, and how users can verify the security of the SDK.

## Private Key Security

### How Private Keys Are Used

Private keys are used for **two purposes only**:

1. **Transaction Signing** (local only)
   - Creating tokens on BSC blockchain
   - Approving token spending
   - Buying and selling tokens

2. **Message Signing** (for authentication)
   - Signing login messages for platform access
   - Signing image generation requests (anti-spam)

### What Is Transmitted

The SDK transmits **only these items** over the network:

| Transmitted | Location | Purpose |
|------------|----------|---------|
| Wallet address | `image_api.py:66`, `platform.py:62` | Identify user |
| Message signature | `image_api.py:67`, `platform.py:64` | Authenticate user |
| Timestamp | `image_api.py:66` | Prevent replay attacks |
| Signed transactions | `blockchain.py:*` | Submit to BSC network |

**⚠️ Private keys are NEVER included in network requests.**

### Code Audit Guide

Users can verify private key handling by reviewing these files:

#### 1. `auth.py` - Private Key Management

```python
# Lines 15-30: Private key is stored in Account object
self.account = Account.from_key(private_key)

# Lines 45-60: Message signing (private key stays local)
signed_message = self.account.sign_message(...)
# Only signed_message.signature is used, not the private key
```

**Verification:**
- Private key is converted to `eth_account.Account` object
- `Account.sign_message()` operates locally
- Only signature output is exposed

#### 2. `image_api.py` - Image API Client

```python
# Lines 59-68: Request payload
payload = {
    "prompt": prompt,
    "address": self.auth.address,      # ✅ Address only
    "timestamp": timestamp,
    "signature": signature             # ✅ Signature only
}
# ❌ Private key is NOT in payload
```

**Verification:**
- Only `address` and `signature` are sent
- Private key never appears in payload
- Network traffic can be inspected with proxy tools

#### 3. `platform.py` - Platform Client

```python
# Lines 59-65: Login request
response = self.session.post(
    f"{self.base_url}/{self.chain}/api/v1/user/login",
    data={
        "address": self.auth.address,  # ✅ Address only
        "message": message,
        "signature": signature         # ✅ Signature only
    }
)
# ❌ Private key is NOT sent
```

**Verification:**
- Authentication uses challenge-response pattern
- Server never receives private key
- Session maintained with cookies after login

#### 4. `blockchain.py` - Blockchain Client

```python
# Lines 80-95: Transaction signing
tx = {
    'from': self.auth.address,
    'to': contract_address,
    # ... transaction details
}
signed_tx = self.web3.eth.account.sign_transaction(tx, self.auth.account.key)
# Signing happens locally via web3.py
```

**Verification:**
- `web3.eth.account.sign_transaction()` operates locally
- Only signed transaction bytes are broadcast
- Standard web3.py transaction flow

### Inspecting Network Traffic

Users can verify network requests using tools:

```bash
# Using mitmproxy to inspect HTTP/HTTPS traffic
pip install mitmproxy
mitmproxy --mode regular

# Set proxy in your script
import os
os.environ['HTTP_PROXY'] = 'http://localhost:8080'
os.environ['HTTPS_PROXY'] = 'http://localhost:8080'

# Run SDK - you can inspect all requests
from moonfun_sdk import MoonfunSDK
sdk = MoonfunSDK(private_key="0x...")
```

**What you'll see:**
- Requests to image API contain: `address`, `signature`, `timestamp`
- Requests to platform contain: `address`, `message`, `signature`
- No private key in any request body

## Cryptographic Security

### Message Signing

The SDK uses Ethereum's standard message signing:

```python
# auth.py
message = encode_defunct(text=message_text)
signed = self.account.sign_message(message)
signature = signed.signature.hex()
```

**Properties:**
- Uses secp256k1 elliptic curve (same as Ethereum)
- Signature proves ownership without revealing private key
- Timestamp prevents replay attacks
- Cannot be forged without private key

### Balance Verification

Image API requests require minimum balance (0.011 BNB):

```python
# Server-side verification (not in SDK)
balance = web3.eth.get_balance(address)
if balance < Web3.to_wei(0.011, 'ether'):
    raise InsufficientBalanceError
```

**Purpose:**
- Prevent spam/abuse of image generation service
- Ensures user can actually create tokens
- No payment is collected (just balance check)

## Hosted Services Security

### Image Generation API

**Endpoint**: `http://moonfun.site`

**Security Measures:**
1. Signature verification (proves wallet ownership)
2. Timestamp validation (5-minute window)
3. Balance checking (minimum BNB requirement)
4. Rate limiting per address

**Risks:**
- Service logs requests (address + timestamp, not private key)
- Generated images are stored on platform
- Service availability depends on hosting

**Mitigation:**
- Deploy your own instance (FastAPI source available on request)
- Use different wallet addresses for different projects
- Review `image_api.py` for exact request format

### MoonnFun Platform

**Endpoint**: `https://moonn.fun`

**Security Measures:**
1. Session-based authentication with signed login
2. HTTPS encryption for all requests
3. CSRF protection
4. Public platform with open APIs

**What is stored:**
- Token metadata (name, symbol, description)
- Uploaded images
- Creator address (public)

**Not stored:**
- Private keys (never sent)
- Transaction details (on blockchain only)

## Best Practices

### 1. Use Dedicated Wallets

```python
# Create new wallet for SDK operations
from eth_account import Account
wallet = Account.create()
print(f"Address: {wallet.address}")
print(f"Private Key: {wallet.key.hex()}")

# Fund this wallet with minimal BNB (0.02-0.05)
# Use only for SDK operations
sdk = MoonfunSDK(private_key=wallet.key.hex())
```

### 2. Environment Variables

```bash
# Store in environment, not in code
export PRIVATE_KEY="0x..."

# Load in script
import os
sdk = MoonfunSDK(private_key=os.getenv('PRIVATE_KEY'))
```

### 3. Never Commit Private Keys

```bash
# .gitignore
.env
*.key
private_keys.txt
secrets/
```

### 4. Test with Small Amounts

```python
# Start with minimum amounts
result = sdk.create_meme("Test meme")  # 0.011 BNB

# Test trading with small amounts
sdk.buy_token(token_address, bnb_amount=0.001)
```

### 5. Review Transactions Before Broadcast

```python
# Add verification step in blockchain.py if needed
print(f"About to send transaction:")
print(f"  From: {tx['from']}")
print(f"  To: {tx['to']}")
print(f"  Value: {tx['value']}")
input("Press Enter to continue...")
```

## Dependency Security

### Core Dependencies

```
web3>=6.0.0         # Ethereum interaction
eth-account>=0.8.0  # Private key management
requests>=2.28.0    # HTTP client
httpx>=0.24.0       # Async HTTP client
```

**Security Notes:**
- All dependencies are widely used and audited
- `eth-account` handles private keys (50M+ downloads)
- `web3.py` is official Ethereum library

### Installing from Source

```bash
# Verify package integrity
git clone <repository>
cd moonfun-sdk/python

# Review requirements.txt
cat requirements.txt

# Check for malicious dependencies
pip install safety
safety check -r requirements.txt

# Install from reviewed source
pip install -e .
```

## Vulnerability Reporting

If you discover a security vulnerability:

1. **DO NOT** open a public GitHub issue
2. Contact: (Provide security contact email)
3. Include:
   - Description of vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

**Responsible Disclosure:**
- We will acknowledge receipt within 48 hours
- We will provide status updates every 7 days
- We will credit reporters (unless anonymous requested)

## Security Checklist for Users

Before using the SDK:

- [ ] Review source code in `auth.py`, `image_api.py`, `platform.py`
- [ ] Verify no hardcoded private keys in examples
- [ ] Check dependencies with `pip list` or `safety check`
- [ ] Test with minimal BNB amount first
- [ ] Use dedicated wallet, not your main wallet
- [ ] Enable 2FA on systems with private key access
- [ ] Store private keys encrypted if persisting to disk
- [ ] Monitor wallet activity on BSCScan

## Known Limitations

1. **Trading Functions (Experimental)**
   - Price estimation may fail on new tokens
   - Slippage protection uses fallback (min_received=0)
   - Risk of frontrunning on large trades

2. **Image API Centralization**
   - Depends on hosted service availability
   - Service operator can log request metadata
   - Mitigation: Deploy your own instance

3. **Session Security**
   - Platform sessions use cookies
   - Sessions expire after inactivity
   - No sensitive data in cookies

## Security Updates

Check `CHANGELOG.md` for security-related updates:

```bash
# Check for updates
pip install --upgrade moonfun-sdk

# Review changelog
pip show moonfun-sdk
```

## Auditing Tools

### Recommended Tools

1. **mitmproxy** - Inspect HTTP/HTTPS traffic
2. **Wireshark** - Packet-level network analysis
3. **safety** - Check dependency vulnerabilities
4. **bandit** - Python code security scanner

```bash
# Run security scan
pip install bandit
bandit -r moonfun_sdk/
```

## Conclusion

**Summary:**
- ✅ Private keys never leave your machine
- ✅ Only signatures are transmitted
- ✅ Standard Ethereum cryptography (secp256k1)
- ✅ Source code is auditable
- ✅ Uses trusted dependencies (web3.py, eth-account)

**User Responsibility:**
- Secure your private key storage
- Use dedicated wallets for SDK
- Review code before production use
- Monitor blockchain transactions
- Keep SDK updated

For questions or concerns, please review the source code or contact security team.
