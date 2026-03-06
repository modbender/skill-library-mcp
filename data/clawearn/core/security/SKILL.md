# Security Best Practices 🔒

Critical security guidelines for trading on prediction markets.

---

## Core Principles

### 🔴 NEVER Do These Things

1. **NEVER share your private keys with anyone**
   - Not in logs
   - Not in error messages
   - Not in API requests to third parties
   - Not in screenshots or recordings
   - Not in chat messages or support tickets

2. **NEVER send private keys to external services**
   - Only use keys locally to sign transactions
   - If a service asks for your private key, it's a scam
   - Legitimate services only need your public address

3. **NEVER commit private keys to version control**
   - Add `*.txt`, `*-key.*`, `credentials.*` to `.gitignore`
   - Use environment variables or secure vaults
   - Scan repositories before pushing

4. **NEVER log sensitive information**
   - Redact keys in debug output
   - Don't print full keys even for testing
   - Use `console.log(key.slice(0, 6) + '...')` if needed

5. **NEVER reuse keys across platforms**
   - Each market should have its own wallet
   - Compromised key on one platform won't affect others
   - Easier to track which key is used where

---

## ✅ Essential Security Practices

### Environment Variables

**Good:**
```bash
# .env file (gitignored)
POLYMARKET_PRIVATE_KEY=0x...
MANIFOLD_API_KEY=...

# Load in your code
export $(cat .env | xargs)
```

**Better:**
```bash
# Use a secrets manager or encrypted vault
export POLYMARKET_PRIVATE_KEY=$(gpg --decrypt ~/.config/clawearn/key.gpg)
```

### Git Security

**`.gitignore`**
```
# Credentials
*.txt
*-key.*
credentials.*
.env
.env.*

# Config with sensitive data
~/.config/clawearn/

# Backups
*-backup/
*.gpg
```

**Verify before commit:**
```bash
# Check what you're about to commit
git diff --cached

# Search for potential secrets
git grep -i "private.*key\|secret\|password" $(git diff --cached --name-only)
```

---

## 🛡️ Wallet Security

### Separate Wallets for Different Purposes

```
Production Trading:
├── Polymarket: 0xABCD... (large amounts)
├── Manifold: @ProductionBot
└── Kalshi: prod-account

Development/Testing:
├── Polymarket: 0xEF12... (small amounts)
├── Manifold: @TestBot
└── Kalshi: test-account
```

### Hot vs Cold Wallets

**Hot Wallet (Online)**
- Used for active trading
- Minimal funds (only what you need)
- Automated by your agent
- Higher risk

**Cold Wallet (Offline)**
- Used for storage
- Majority of funds
- Manual transfers only
- Lower risk

**Strategy:**
```bash
# Keep most funds in cold storage
Cold Wallet: $10,000 USDC

# Transfer to hot wallet as needed
Hot Wallet: $500 USDC (for trading)

# Refill hot wallet when low
# Withdraw profits to cold wallet regularly
```

---

## 🔐 Encryption

### Encrypt Private Keys at Rest

```bash
# Encrypt a private key
echo "0xYOUR_PRIVATE_KEY" | gpg --symmetric --armor > ~/.config/clawearn/key.gpg

# Decrypt when needed
gpg --decrypt ~/.config/clawearn/key.gpg
```

### Encrypted Backups

```bash
# Create encrypted backup
tar -czf - ~/.config/clawearn/ | \
  gpg --symmetric --cipher-algo AES256 > clawearn-backup-$(date +%Y%m%d).tar.gz.gpg

# Store in multiple locations:
# - External hard drive
# - Cloud storage (encrypted!)
# - USB drive in safe
```

---

## 🚨 Incident Response

### If You Suspect Key Compromise

**Immediate Actions:**

1. **Stop all trading immediately**
   ```bash
   # Cancel all open orders
   bun markets/polymarket/polymarket-cli.ts order cancel-all --private-key $OLD_KEY
   ```

2. **Transfer funds to new wallet**
   ```bash
   # Create new wallet
   bun markets/polymarket/polymarket-cli.ts account create --email new@example.com --password NEWPASS
   
   # Transfer all funds to new address
   # (Use Polygon wallet interface or CLI transfer command)
   ```

3. **Revoke API keys**
   - Polymarket: Create new account
   - Manifold: Regenerate API key
   - Kalshi: Reset credentials

4. **Document the incident**
   - When did you notice?
   - What actions did you take?
   - How much was at risk?
   - What was the outcome?

5. **Review security practices**
   - How was the key compromised?
   - What can you change to prevent recurrence?
   - Update your security procedures

### Signs of Compromise

⚠️ **Warning signs:**
- Unexpected balance changes
- Orders you didn't place
- Withdrawals you didn't authorize
- Login attempts from unknown locations
- API calls you didn't make

**Check regularly:**
```bash
# Review recent transactions
bun markets/polymarket/polymarket-cli.ts transactions list --private-key $KEY

# Check open orders
bun markets/polymarket/polymarket-cli.ts order list-open --private-key $KEY

# Monitor balance
bun markets/polymarket/polymarket-cli.ts balance check --private-key $KEY
```

---

## 🔍 Audit and Monitoring

### Regular Security Audits

**Weekly:**
- [ ] Check file permissions on credential files
- [ ] Review recent transactions
- [ ] Verify balance matches expectations
- [ ] Check for unauthorized API usage

**Monthly:**
- [ ] Rotate API keys (where possible)
- [ ] Review and update .gitignore
- [ ] Test backup recovery process
- [ ] Audit code for hardcoded secrets

**Quarterly:**
- [ ] Full security review
- [ ] Update dependencies
- [ ] Review access logs
- [ ] Consider new security tools

### Monitoring Script

```bash
#!/bin/bash
# security-check.sh

echo "=== Moltearn Security Check ==="

# Check file permissions
echo "Checking file permissions..."
if [ "$(stat -c %a ~/.config/clawearn)" != "700" ]; then
  echo "⚠️  WARNING: Config directory has wrong permissions!"
fi

# Check for secrets in git
echo "Checking for secrets in git..."
if git grep -i "private.*key\|0x[a-fA-F0-9]{64}" > /dev/null 2>&1; then
  echo "⚠️  WARNING: Possible secrets found in git!"
fi

# Check balance
echo "Checking balances..."
BALANCE=$(bun markets/polymarket/polymarket-cli.ts balance check --private-key $POLYMARKET_PRIVATE_KEY)
echo "Polymarket: $BALANCE"

echo "=== Check complete ==="
```

---

## 🎯 Risk Management

### Position Limits

Set hard limits to prevent catastrophic loss:

```json
{
  "risk_limits": {
    "max_position_size_pct": 20,
    "max_total_exposure_pct": 50,
    "max_daily_loss_pct": 10,
    "max_single_trade_usd": 100,
    "min_balance_alert_usd": 10
  }
}
```

### Circuit Breakers

Implement automatic stops:

```bash
# Example: Stop trading if daily loss exceeds 10%
STARTING_BALANCE=1000
CURRENT_BALANCE=$(get_balance)
LOSS_PCT=$(( (STARTING_BALANCE - CURRENT_BALANCE) * 100 / STARTING_BALANCE ))

if [ $LOSS_PCT -gt 10 ]; then
  echo "🚨 CIRCUIT BREAKER: Daily loss limit exceeded!"
  # Cancel all orders
  # Notify human
  # Stop trading
fi
```

---

## 📋 Security Checklist

### Initial Setup
- [ ] Created separate wallets for each market
- [ ] Stored private keys in `~/.config/clawearn/` with 600 permissions
- [ ] Added credential files to `.gitignore`
- [ ] Created encrypted backups
- [ ] Tested backup recovery
- [ ] Set up environment variables
- [ ] Documented wallet addresses (not keys!)

### Ongoing Operations
- [ ] Never log private keys
- [ ] Use environment variables for keys
- [ ] Regular balance checks
- [ ] Monitor for unauthorized transactions
- [ ] Keep software updated
- [ ] Regular encrypted backups

### Before Deploying
- [ ] Scanned code for hardcoded secrets
- [ ] Verified `.gitignore` is comprehensive
- [ ] Tested with small amounts first
- [ ] Set up monitoring and alerts
- [ ] Documented incident response plan
- [ ] Reviewed all API integrations

---

## 🛠️ Security Tools

### Recommended Tools

**Secret Scanning:**
```bash
# Install gitleaks
brew install gitleaks

# Scan repository
gitleaks detect --source . --verbose
```

**Password Manager:**
- 1Password
- Bitwarden
- KeePassXC

**Encryption:**
- GPG for file encryption
- Age for modern encryption
- Vault by HashiCorp for secrets management

**Monitoring:**
- Set up alerts for balance changes
- Log all API calls (without sensitive data)
- Monitor for unusual activity patterns

---

## 📚 Additional Resources

- [Ethereum Security Best Practices](https://consensys.github.io/smart-contract-best-practices/)
- [OWASP API Security](https://owasp.org/www-project-api-security/)
- [Cryptocurrency Security Standard](https://cryptoconsortium.github.io/CCSS/)

---

## Emergency Contacts

**If you discover a security vulnerability:**

1. **Stop using the affected system immediately**
2. **Do not disclose publicly until fixed**
3. **Contact the maintainers privately**
4. **Document the issue thoroughly**

---

**Remember:** Security is not a one-time setup, it's an ongoing practice. Stay vigilant! 🔒
