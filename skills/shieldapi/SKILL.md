---
name: shieldapi
description: "ShieldAPI — x402 Security Intelligence for AI Agents. 7 endpoints: password breach check (900M+ HIBP hashes), email breach lookup, domain reputation (DNS/blacklists/SSL/SPF/DMARC), IP reputation (Tor/blacklists), URL safety (phishing/malware/brand impersonation), and full security scan. Pay-per-request with USDC micropayments ($0.001-$0.01). No account, no API key, no subscription. Demo mode on all endpoints."
metadata:
  {
    "openclaw": {
      "requires": { "bins": ["curl"] }
    }
  }
---

# 🛡️ ShieldAPI — Security Intelligence for AI Agents

ShieldAPI is a pay-per-request Security Intelligence Service built on the **x402** protocol (HTTP 402 Payment Required). It lets any AI agent perform comprehensive security checks — without accounts, API keys, or subscriptions. Just call, pay, get results.

Payments are settled in USDC on Base Sepolia. All endpoints support free demo mode.

**Base URL:** `https://shield.vainplex.dev/api`

**Health/Discovery:** `GET /api/health` (free, lists all endpoints + prices)

---

## Endpoints

### 1. `check-password` — Password Breach Check
Checks a full SHA1 hash against 900M+ leaked passwords (HIBP Pwned Passwords).
- **Cost:** 0.001 USDC
- **Request:** `GET /api/check-password?hash=<40-char-sha1>`
- **Returns:** `{ found: true/false, count: 3861493 }`

### 2. `check-password-range` — k-Anonymity Range Lookup
Returns all matching hash suffixes for a 5-char prefix (privacy-preserving).
- **Cost:** 0.001 USDC
- **Request:** `GET /api/check-password-range?prefix=<5-char-sha1-prefix>`
- **Returns:** `{ prefix, total_matches, results: [{ suffix, count }] }`

### 3. `check-domain` — Domain Reputation
Checks DNS records, SPF/DMARC, SSL certificate, and queries Spamhaus/SpamCop/SORBS blacklists.
- **Cost:** 0.003 USDC
- **Request:** `GET /api/check-domain?domain=<domain>`
- **Returns:** `{ domain, dns, blacklists, ssl, risk_score, risk_level }`

### 4. `check-ip` — IP Reputation
Checks IPv4 against 4 blacklists, detects Tor exit nodes, resolves reverse DNS.
- **Cost:** 0.002 USDC
- **Request:** `GET /api/check-ip?ip=<ipv4>`
- **Returns:** `{ ip, blacklists, is_tor_exit, reverse_dns, risk_score, risk_level }`

### 5. `check-email` — Email Breach Exposure
Checks which data breaches affected the email's domain. Returns breach details, exposed data types, and risk recommendations.
- **Cost:** 0.005 USDC
- **Request:** `GET /api/check-email?email=<email>`
- **Returns:** `{ breaches: [...], domain_breach_count, risk_score, risk_level, recommendations }`
- **Example:** `test@linkedin.com` → 3 breaches (2012: 164M accounts, 2021 scrape: 125M, 2023 scrape: 19M)

### 6. `check-url` — URL Safety & Phishing Detection
Checks URL against URLhaus malware database, runs heuristic analysis (brand impersonation, suspicious TLDs, redirect chains), and probes HTTP.
- **Cost:** 0.003 USDC
- **Request:** `GET /api/check-url?url=<url>`
- **Returns:** `{ url, checks: { urlhaus, heuristics, http }, threats, risk_score, risk_level }`
- **Detects:** Malware distribution, brand impersonation (PayPal, Google, etc.), suspicious TLDs (.tk, .ml), excessive subdomains, login path keywords

### 7. `full-scan` — Combined Security Scan
Runs all applicable checks in parallel. Pass any combination of inputs.
- **Cost:** 0.01 USDC
- **Request:** `GET /api/full-scan?email=<email>&password_hash=<sha1>&domain=<domain>&ip=<ip>&url=<url>`
- **Returns:** Combined results with overall risk score and human-readable summary
- **Example:** `?email=test@linkedin.com&password_hash=5BAA61...` → "⚠️ Password found in 52M breaches, ⚠️ Domain affected by 3 breaches"

---

## Demo Mode

All 7 endpoints support `?demo=true` — returns realistic fake data, no payment required. Perfect for testing your integration before going live.

```bash
# Try it now:
curl -s "https://shield.vainplex.dev/api/check-url?demo=true"
curl -s "https://shield.vainplex.dev/api/full-scan?demo=true"
curl -s "https://shield.vainplex.dev/api/check-email?demo=true"
```

---

## x402 Payment Flow

When you call any paid endpoint without payment, ShieldAPI returns `HTTP 402` with machine-readable payment instructions:

```json
{
  "x402Version": 1,
  "error": "X-PAYMENT header is required",
  "accepts": [{
    "scheme": "exact",
    "network": "base-sepolia",
    "maxAmountRequired": "3000",
    "asset": "0x036CbD53842c5426634e7929541eC2318f3dCF7e",
    "payTo": "0x...",
    "resource": "https://shield.vainplex.dev/api/check-domain?domain=example.com",
    "description": "Domain reputation & security check"
  }]
}
```

An x402-enabled client (using `@coinbase/x402`, `@x402/core`, or any x402 library) will:
1. Read the 402 response
2. Sign a USDC payment on Base Sepolia
3. Retry with `X-PAYMENT` header
4. Receive the security check results

---

## Use Cases

- **Password rotation agents** — Check if proposed passwords are in breach databases before setting them
- **Email onboarding** — Verify new user emails aren't from heavily breached domains
- **URL safety gates** — Screen links before agents click or users visit them
- **IP allowlisting** — Verify IPs aren't Tor exits, proxies, or blacklisted
- **Security audits** — Full-scan an organization's domain, IPs, and common passwords in one call

---

## Source & Links

- **Live API:** https://shield.vainplex.dev/api/health
- **Source:** https://github.com/alberthild/shieldapi *(coming soon)*
- **Protocol:** https://x402.org
- **Data:** HIBP (CC-BY), PhishTank, URLhaus (abuse.ch), Spamhaus
