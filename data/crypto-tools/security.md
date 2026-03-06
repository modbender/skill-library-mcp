# Crypto Security & Scam Detection

## Contract Verification

Before interacting with ANY new token/contract:

| Tool | What It Checks | URL |
|------|---------------|-----|
| **TokenSniffer** | Honeypot, ownership, liquidity locks | tokensniffer.com |
| **RugDoc** | Contract risks, dev history | rugdoc.io |
| **CertiK** | Audit status, security score | skynet.certik.com |
| **De.Fi Scanner** | Multiple checks combined | de.fi/scanner |
| **Honeypot.is** | Sell restrictions | honeypot.is |

### Red Flags in Contracts

| Flag | Risk Level | What It Means |
|------|------------|---------------|
| **Can't sell** | 🔴 Critical | Honeypot — you're trapped |
| **Owner can mint** | 🔴 Critical | Unlimited inflation |
| **Hidden fees** | 🔴 Critical | Drains on transfer |
| **No liquidity lock** | 🟠 High | Rug pull ready |
| **Unverified code** | 🟠 High | Can't audit |
| **Single owner** | 🟡 Medium | Centralization risk |

### Quick Contract Check

```
1. Is contract verified on explorer? (No → 🚫)
2. TokenSniffer score > 70? (No → ⚠️)
3. Liquidity locked > 6 months? (No → ⚠️)
4. Ownership renounced or multisig? (No → check carefully)
5. Audit from known firm? (Nice to have)
```

---

## Common Scam Patterns

### Rug Pulls
- Dev creates token → hypes it → removes liquidity → token worthless
- **Defense:** Check liquidity locks, dev wallet history

### Honeypots
- You can buy but can't sell
- **Defense:** Always test with tiny amount first, use Honeypot.is

### Fake Airdrops
- "Claim your free tokens" → connects to malicious contract → drains wallet
- **Defense:** Never interact with random tokens in your wallet

### Phishing Sites
- Lookalike URLs (uniswap.org vs un1swap.org)
- **Defense:** Bookmark official sites, verify URLs character by character

### Social Engineering
- "I'm from support" in DMs
- "Send 1 ETH to verify, get 2 back"
- **Defense:** No legitimate project DMs first. Ever.

### Pump & Dump
- Coordinated buy → price spikes → insiders sell → crashes
- **Defense:** Avoid "guaranteed profit" groups, check holder distribution

---

## Wallet Security Checklist

### Seed Phrase
- [ ] Written on paper, NEVER digital
- [ ] Stored in multiple secure locations
- [ ] NOT in cloud, email, photo, notes app
- [ ] Test recovery before storing funds

### Hot Wallet (MetaMask, etc.)
- [ ] Only keep what you're actively using
- [ ] Revoke unused approvals regularly (revoke.cash)
- [ ] Different wallet for sketchy mints
- [ ] Bookmark official sites, don't Google

### Cold Storage (Ledger, Trezor)
- [ ] Buy ONLY from official store (never Amazon/eBay)
- [ ] Verify firmware before setup
- [ ] Use for long-term holdings
- [ ] Separate device from daily browsing

### Exchange Security
- [ ] 2FA with authenticator app (NOT SMS)
- [ ] Whitelist withdrawal addresses
- [ ] Unique strong password
- [ ] Don't store long-term on exchange

---

## URL Verification

### Official Sites (bookmark these)
- **Uniswap:** app.uniswap.org
- **OpenSea:** opensea.io
- **Aave:** app.aave.com
- **MetaMask:** metamask.io
- **Etherscan:** etherscan.io

### Verification Steps
1. Check for HTTPS (but scams have it too)
2. Look for subtle typos (rn vs m, 1 vs l)
3. Use official links from verified Twitter/GitHub
4. When in doubt, type manually from memory

---

## When User Asks "Is X Safe?"

Response template:

```
I can check several things:

1. Contract verification on [explorer]
2. TokenSniffer score
3. Liquidity lock status
4. Audit history

Let me look... [do checks]

Results: [findings]

⚠️ Reminder: This is technical analysis only. 
No token is "safe" — all crypto carries risk of total loss.
Do your own research before any decision.
```

---

## Approval Hygiene

**Problem:** Connecting to dApps gives them permission to spend your tokens. Old approvals = attack surface.

**Solution:** Regular cleanup via revoke.cash

```
1. Go to revoke.cash
2. Connect wallet
3. Review all approvals
4. Revoke anything you don't actively use
5. Do this monthly or after major interactions
```

---

## Emergency Response

If compromised:
1. **Immediately:** Transfer remaining assets to NEW wallet (not same seed)
2. **Check:** revoke.cash for active approvals
3. **Don't:** Use same seed phrase ever again
4. **Report:** To relevant platform if applicable

If unsure:
- Move assets to cold storage while investigating
- Don't interact with suspicious tokens (even to "check")
