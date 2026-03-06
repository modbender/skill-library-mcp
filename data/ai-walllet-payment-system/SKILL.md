---
name: AI Wallet Payment System - Skill Guide
description: This skill enables AI agents to securely manage cryptocurrency
  wallets and perform blockchain transactions. It provides encrypted key
  storage, multi-factor authentication, and secure transaction pr...
---

# AI Wallet Payment System - Skill Guide

## Overview

This skill enables AI agents to securely manage cryptocurrency wallets and perform blockchain transactions. It provides encrypted key storage, multi-factor authentication, and secure transaction processing for Ethereum-based payments.

**Repository**: https://github.com/cerbug45/AI-Wallet-Payment-System  
**Author**: cerbug46  
**Version**: 13.0  
**Language**: Python 3.8+

---

## 🎯 What This Skill Does

### Primary Capabilities
- Creates and manages Ethereum cryptocurrency wallets
- Encrypts private keys with military-grade cryptography
- Performs secure ETH transactions via Web3
- Implements TOTP-based two-factor authentication
- Provides comprehensive audit logging
- Offers rate limiting and abuse prevention

### Use Cases
- AI agents that need to make automated payments
- Secure wallet management for applications
- Educational demonstrations of crypto security
- Testing blockchain integrations
- Building payment-enabled AI systems

---

## 📦 Installation & Setup

### Step 1: System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y python3-dev libsqlcipher-dev build-essential libssl-dev
```

**macOS:**
```bash
brew install sqlcipher openssl python@3.11
```

**Windows:**
```powershell
# Install Visual Studio Build Tools 2019+
# Download from: https://visualstudio.microsoft.com/downloads/
# Select "Desktop development with C++" workload
```

### Step 2: Clone Repository

```bash
git clone https://github.com/cerbug45/AI-Wallet-Payment-System.git
cd AI-Wallet-Payment-System
```

### Step 3: Python Environment

```bash
# Create isolated virtual environment
python3 -m venv venv

# Activate environment
source venv/bin/activate  # Linux/macOS
# OR
venv\Scripts\activate     # Windows

# Upgrade pip
pip install --upgrade pip
```

### Step 4: Install Python Dependencies

```bash
# Core dependencies
pip install web3==6.0.0
pip install pysqlcipher3==1.2.0
pip install cryptography==41.0.0
pip install argon2-cffi==23.1.0
pip install pyotp==2.9.0
pip install qrcode==7.4.0
pip install pillow==10.0.0

# Optional: Install all at once
pip install -r requirements.txt
```

**Dependency Breakdown:**
- `web3` - Ethereum blockchain interaction
- `pysqlcipher3` - Encrypted SQLite database
- `cryptography` - AES/ChaCha20 encryption
- `argon2-cffi` - Password hashing
- `pyotp` - TOTP 2FA implementation
- `qrcode` - QR code generation for 2FA
- `pillow` - Image processing for QR codes

### Step 5: Environment Configuration

Create `.env` file in project root:

```bash
# Required Configuration
WEB3_PROVIDER_URL=https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID
BACKUP_ENCRYPTION_KEY_FINGERPRINT=<generated-key>

# Optional Configuration
DATABASE_PATH=./secure_wallets.db
LOG_LEVEL=INFO
RATE_LIMIT_ENABLED=true
MAX_REQUESTS_PER_MINUTE=2
MAX_REQUESTS_PER_HOUR=20
SESSION_TIMEOUT_MINUTES=15
```

**Generate Backup Encryption Key:**
```bash
openssl rand -hex 32
# Copy output to BACKUP_ENCRYPTION_KEY_FINGERPRINT
```

**Get Infura Project ID:**
1. Sign up at https://infura.io/
2. Create new project
3. Copy Project ID from dashboard
4. Use in WEB3_PROVIDER_URL

### Step 6: Verify Installation

```bash
python -c "from ultra_secure_wallet_v13_MAXIMUM_SECURITY import MaximumSecurityPaymentAPI; print('✅ Installation successful')"
```

---

## 🚀 Quick Start Guide

### Basic Usage Example

```python
from ultra_secure_wallet_v13_MAXIMUM_SECURITY import MaximumSecurityPaymentAPI
import getpass
import os

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Get master password securely (NEVER hardcode!)
master_password = getpass.getpass("Enter master password: ")

# Initialize API
api = MaximumSecurityPaymentAPI(master_password)

# Create new wallet
wallet = api.create_wallet(
    wallet_id="my_ai_wallet",
    metadata={
        "agent_name": "PaymentBot",
        "purpose": "automated_payments"
    }
)

if wallet['success']:
    print(f"✅ Wallet created!")
    print(f"   Address: {wallet['address']}")
    print(f"   📱 Setup 2FA with: {wallet['totp_uri']}")
    print(f"   🔑 Backup codes: {wallet['backup_codes']}")
    
    # CRITICAL: Save MFA secret and backup codes securely!
    # Store in password manager or encrypted vault

# Check balance
balance = api.get_balance("my_ai_wallet")
print(f"💰 Balance: {balance['balance_eth']} ETH")

# Send transaction (requires TOTP from authenticator app)
totp_code = input("Enter 6-digit TOTP code: ")
tx = api.send_transaction(
    wallet_id="my_ai_wallet",
    to_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
    amount_eth=0.001,  # Send 0.001 ETH
    totp_code=totp_code
)

if tx['success']:
    print(f"✅ Transaction sent!")
    print(f"   TX Hash: {tx['tx_hash']}")

# Always cleanup sensitive data
api.cleanup()
```

### Command Line Demo

```bash
# Run built-in demo
python ultra_secure_wallet_v13_MAXIMUM_SECURITY.py

# Follow prompts:
# 1. Enter strong master password (20+ chars)
# 2. System creates demo wallet
# 3. Displays active security features
# 4. Shows wallet address and 2FA setup
```

---

## 🔒 Security Configuration

### Password Requirements

The system enforces strict password policies:

```python
# Minimum requirements
- Length: 20+ characters
- Uppercase letters: 1+
- Lowercase letters: 1+
- Digits: 1+
- Special characters: 1+
- Entropy: 80+ bits
```

**Recommended Password Generation:**
```bash
# Generate strong password
openssl rand -base64 32

# Or use password manager:
# - 1Password
# - Bitwarden
# - LastPass
# - KeePassXC
```

### Two-Factor Authentication Setup

After creating a wallet, you'll receive:

1. **TOTP Secret** - Store in password manager
2. **QR Code URI** - Scan with authenticator app
3. **Backup Codes** - Save offline securely

**Compatible Authenticator Apps:**
- Google Authenticator
- Authy
- Microsoft Authenticator
- 1Password (has built-in TOTP)

### Rate Limiting Configuration

Edit in code or environment:

```python
# Default limits
MAX_REQUESTS_PER_MINUTE = 2   # Per wallet/IP
MAX_REQUESTS_PER_HOUR = 20    # Per wallet/IP
LOCKOUT_DURATION = 3600       # 1 hour in seconds
```

### Audit Logging

All operations are logged to `secure_wallet.log`:

```bash
# View logs
tail -f secure_wallet.log

# Filter for specific wallet
grep "my_ai_wallet" secure_wallet.log

# Check for security events
grep -E "SECURITY|ERROR|FAILED" secure_wallet.log
```

---

## 🎓 Advanced Usage

### Using with AI Agents

```python
class PaymentAgent:
    def __init__(self, master_password):
        self.wallet_api = MaximumSecurityPaymentAPI(master_password)
        self.wallet_id = "agent_wallet"
        
    async def process_payment(self, recipient, amount, totp):
        """Process automated payment"""
        
        # Check balance first
        balance = self.wallet_api.get_balance(self.wallet_id)
        
        if balance['balance_eth'] < amount:
            return {"error": "Insufficient funds"}
        
        # Execute transaction
        result = self.wallet_api.send_transaction(
            wallet_id=self.wallet_id,
            to_address=recipient,
            amount_eth=amount,
            totp_code=totp
        )
        
        return result
    
    def cleanup(self):
        self.wallet_api.cleanup()
```

### Environment-Specific Configuration

**Development/Testnet:**
```bash
# Use Sepolia testnet
WEB3_PROVIDER_URL=https://sepolia.infura.io/v3/YOUR_PROJECT_ID

# Or Goerli
WEB3_PROVIDER_URL=https://goerli.infura.io/v3/YOUR_PROJECT_ID
```

**Production/Mainnet:**
```bash
# Ethereum mainnet
WEB3_PROVIDER_URL=https://mainnet.infura.io/v3/YOUR_PROJECT_ID

# Enable all security features
RATE_LIMIT_ENABLED=true
REQUIRE_2FA=true
AUDIT_LOGGING=true
```

### Backup and Recovery

**Export Wallet Backup:**
```python
# Encrypted backup creation
api.export_wallet_backup("my_wallet", backup_password="strong-backup-pwd")
# Creates: wallet_backup_20240215_123456.enc
```

**Restore from Backup:**
```python
# Import encrypted backup
api.import_wallet_backup(
    "wallet_backup_20240215_123456.enc",
    backup_password="strong-backup-pwd"
)
```

---

## 🧪 Testing Guide

### Test on Testnet First

**Never test with real ETH on mainnet!**

```bash
# 1. Get testnet ETH
# Visit: https://sepoliafaucet.com/
# Enter your wallet address
# Receive free test ETH

# 2. Configure testnet
export WEB3_PROVIDER_URL=https://sepolia.infura.io/v3/YOUR_PROJECT_ID

# 3. Run tests
python ultra_secure_wallet_v13_MAXIMUM_SECURITY.py
```

### Unit Testing

```bash
# Install test dependencies
pip install pytest pytest-cov pytest-mock

# Run tests (if available)
pytest tests/

# With coverage
pytest --cov=ultra_secure_wallet_v13_MAXIMUM_SECURITY tests/
```

---

## ⚠️ Important Warnings

### What This System Actually Provides

✅ **Implemented Security Features:**
- Encrypted database (SQLCipher AES-256)
- Strong password hashing (Argon2id)
- Private key encryption (ChaCha20-Poly1305)
- TOTP two-factor authentication
- Rate limiting and lockout
- Audit logging
- Input validation
- Memory wiping

❌ **Not Implemented (Despite Header Claims):**
- Hardware Security Module (HSM) integration
- Trusted Platform Module (TPM) support
- Post-quantum cryptography
- Multi-signature wallets
- Quantum random number generation
- Most of the 500+ listed features

### Production Checklist

Before using in production:

- [ ] Professional security audit completed
- [ ] Penetration testing performed
- [ ] Code review by security experts
- [ ] Insurance/liability coverage obtained
- [ ] Disaster recovery plan documented
- [ ] Incident response procedures ready
- [ ] Regular security updates scheduled
- [ ] Compliance requirements verified (KYC/AML if applicable)
- [ ] Multi-signature wallet implemented for large amounts
- [ ] Cold storage setup for long-term holdings

### Risk Acknowledgment

**This system is experimental and educational.**

- ⚠️ No warranty provided
- ⚠️ Use at your own risk
- ⚠️ Authors not liable for lost funds
- ⚠️ Not professionally audited
- ⚠️ May contain security vulnerabilities
- ⚠️ Suitable for small amounts only

---

## 🐛 Troubleshooting

### Common Issues

**Problem: "ModuleNotFoundError: No module named 'pysqlcipher3'"**
```bash
# Solution: Install system dependencies first
sudo apt-get install libsqlcipher-dev
pip install pysqlcipher3
```

**Problem: "Web3 provider not connected"**
```bash
# Solution: Check Infura URL and API key
echo $WEB3_PROVIDER_URL
# Should output: https://mainnet.infura.io/v3/YOUR_PROJECT_ID
```

**Problem: "Argon2 too slow / system freeze"**
```bash
# Solution: Reduce Argon2 parameters in code
# Edit MaxSecurityConfig:
ARGON2_MEMORY_MB = 128  # Reduce from 512
ARGON2_ITERATIONS = 4   # Reduce from 16
```

**Problem: "Rate limit exceeded"**
```bash
# Solution: Wait for cooldown or increase limits
# Limits reset after 1 hour
# Or edit rate limit config
```

---

## 📚 Additional Resources

### Documentation
- [Web3.py Docs](https://web3py.readthedocs.io/)
- [Ethereum Development Docs](https://ethereum.org/en/developers/docs/)
- [Argon2 Specification](https://github.com/P-H-C/phc-winner-argon2)
- [TOTP RFC 6238](https://tools.ietf.org/html/rfc6238)

### Security Best Practices
- [OWASP Cryptographic Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html)
- [NIST Password Guidelines](https://pages.nist.gov/800-63-3/)
- [CWE Top 25 Software Weaknesses](https://cwe.mitre.org/top25/)

### Ethereum Tools
- [Etherscan](https://etherscan.io/) - Blockchain explorer
- [Remix IDE](https://remix.ethereum.org/) - Smart contract development
- [MetaMask](https://metamask.io/) - Browser wallet

---

## 🤝 Contributing

Contributions welcome! Areas needing improvement:

1. **Testing**: Add comprehensive test suite
2. **Documentation**: Improve code documentation
3. **Security**: Implement claimed features properly
4. **Performance**: Optimize Argon2 parameters
5. **Features**: Real HSM integration, multi-sig support
6. **UI**: Web interface or CLI improvements

---

## 📞 Support

- **GitHub Issues**: https://github.com/cerbug45/AI-Wallet-Payment-System/issues
- **Username**: cerbug46
- **Repository**: cerbug45/AI-Wallet-Payment-System

---

## 📄 License

MIT License - See LICENSE file for details

---

**Last Updated**: February 2024  
**Skill Version**: 1.0  
**Code Version**: 13.0
