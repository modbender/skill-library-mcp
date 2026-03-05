# 🛡️ AgentShield Audit

> **Privacy-First Security Assessment with Public Trust Registry**

---

## 🔒 PRIVACY-FIRST SECURITY ASSESSMENT

**Zero data leaves your system. All tests run locally.**

✅ **Zero data leaves your system**  
✅ **52+ tests run locally in your agent**  
✅ **Only certificate public key is shared**  
✅ **Open source - verify every test**

**AgentShield never sees your prompts, code, or agent behavior.**

---

## 🚀 Quick Start

### Installation

```bash
clawhub install agentshield-audit
```

### Usage

Tell your agent:

```
"Run a security assessment with AgentShield"
```

Or manually:

```bash
cd ~/.openclaw/skills/agentshield-audit
python scripts/initiate_audit.py --auto --yes
```

**Time Required:** ~2-5 minutes

---

## 🔍 Developer Transparency

### Infrastructure Honesty

**⚠️ IMPORTANT FOR DEVELOPERS:**

> **Current Registry Server:** Heroku (Development Environment)
> - **Status:** Will be replaced with dedicated infrastructure (Q2 2026)
> - **Purpose:** ONLY stores public certificate IDs and trust scores
> - **NO sensitive data:** Prompts, code, test results NEVER leave your system

**What the server sees:**
✅ Certificate ID (public key hash) — used for registry lookup
✅ Challenge-response signature — for identity verification
✅ Timestamp — for audit trail

**What the server NEVER sees:**
🚫 Agent prompts or conversations
🚫 Your internal code
🚫 Test results (PDF stays local)
🚫 System logs or configuration

**Data Flow:**
```
Your Agent → Local Tests → Ed25519 Signing → Public Certificate → Registry
   (Code)      (52+ Tests)    (Private Key)      (Public Key)    (ID Only)
                                                     👆
                                              Only this goes to server!
```

**Full Details:** See `DEVELOPER_TRANSPARENCY.md`

---

## ✨ Features

### 🔐 Privacy-First Security
- ✅ **52+ Local Security Tests** — All run in your environment
- ✅ **Zero Data Leakage** — Only public keys shared
- ✅ **Open Source Tests** — Verify every test yourself
- ✅ **Challenge-Response Protocol** — Cryptographic identity proof

### 📜 Certificate System
- ✅ **Ed25519 Signatures** — Industry-standard cryptography
- ✅ **Public Trust Registry** — Verify any agent's status
- ✅ **CRL Support** — Instant revocation when needed
- ✅ **Tamper-Proof PDFs** — Local report generation

### 🏆 Trust Score
- ✅ **Tier System** — UNVERIFIED → BASIC → VERIFIED → TRUSTED
- ✅ **Public Registry** — [agentshield.live/registry](https://agentshield.live/registry)
- ✅ **Reputation Building** — Earn trust with multiple verifications

### 🇪🇺 Compliance
- ✅ **EU AI Act Ready** — Risk classification support
- ✅ **GDPR Compliant** — No personal data storage
- ✅ **RFC 5280 CRL** — Standard revocation format
- ✅ **Audit Trail** — All verifications logged

---

## 📊 How It Works

**Step-by-Step Process:**

1. **Skill Installs Locally** — `clawhub install agentshield-audit`
2. **Subagent Spawns** — Tests run in isolated session (your environment!)
3. **52+ Security Tests** — All execute locally, no data upload
4. **Generate Ed25519 Key** — Private key stays on your machine
5. **Challenge-Response** — Sign nonce to prove identity (locally!)
6. **Issue Certificate** — Public registry + tamper-proof PDF report
7. **Trust Score** — Earn reputation with multiple verifications

**What We See:**
- ✅ Your Ed25519 **public key** (certificate)
- ✅ Challenge **signature** (proof of identity)

**What We NEVER See:**
- ❌ Your prompts or conversations
- ❌ Your code or agent behavior
- ❌ Your API keys or secrets
- ❌ Your test results (stay in local PDF)

---

## 🔍 Security Tests

**52+ Tests in 5 Categories:**

### 1. Input Sanitizer
- Prompt injection detection
- Template injection tests
- SQL injection patterns
- Command injection attempts
- XSS vulnerability scans

### 2. EchoLeak Test
- Zero-click data exfiltration
- Malicious tool invocation
- Context contamination
- Memory isolation checks

### 3. Tool Sandbox
- Permission boundary controls
- Filesystem access tests
- Network isolation checks
- Privilege escalation attempts

### 4. Output DLP
- PII detection (emails, SSN, credit cards)
- API key pattern matching
- Secret leakage prevention
- Data sanitization checks

### 5. Supply Chain Scanner
- Dependency integrity checks
- Package vulnerability scans
- Malicious code detection
- Outdated library warnings

**All tests are open source:** [github.com/bartelmost/agentshield](https://github.com/bartelmost/agentshield)

---

## 🏆 Trust Score Explained

### Score Calculation

Your trust score (0-100) is calculated from:

- **40%** Verification count (consistency)
- **30%** Certificate age (reputation)
- **30%** Assessment success rate (reliability)

### Tier System

| Tier | Score | Badge | Requirements |
|------|-------|-------|--------------|
| 🔴 **UNVERIFIED** | 0 | ❌ | No certificate |
| 🟡 **BASIC** | 1-49 | 🆔 | Initial assessment |
| 🟢 **VERIFIED** | 50-79 | ✅ | Multiple verifications |
| 🔵 **TRUSTED** | 80-100 | 🛡️ | Proven track record |

### View Registry

**Browse all certified agents:**  
👉 [agentshield.live/registry](https://agentshield.live/registry)

**Check any agent's status:**  
👉 [agentshield.live/verify](https://agentshield.live/verify)

---

## 🛡️ Security Architecture (Privacy-First)

```
┌──────────────────────────────────────────────────────────────┐
│                   YOUR AGENT ENVIRONMENT                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ 52+ Tests   │  │  Code Scan  │  │  Token Opt  │  ◄─ Local │
│  │  (Local)    │  │  (Local)    │  │   (Local)   │         │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘         │
│         └────────────────┴────────────────┘                 │
│                          │                                   │
│                    Ed25519 Sign                              │
│                  (Private Key Never Leaves)                  │
└──────────────────────────┼──────────────────────────────────┘
                           │
                  Challenge Response
                  (Public Cert Only)
                           ▼
               ┌───────────────────────┐
               │  AgentShield Registry │
               │  (Public Trust DB)    │
               └───────────────────────┘
```

**Key Privacy Guarantees:**

- ✅ **All tests run in YOUR agent session**
- ✅ **Subagent spawns locally (not on our servers)**
- ✅ **Private key generated and stored locally**
- ✅ **PDF report created on YOUR machine**
- ❌ **We NEVER receive your code or prompts**
- ❌ **We NEVER see your test results**
- ❌ **We ONLY store your public key + trust score**

**Verify our claims:** All test code is open source at [github.com/bartelmost/agentshield](https://github.com/bartelmost/agentshield)

---

## 📖 Commands

### Initiate Audit

```bash
# Auto-detect agent details
python scripts/initiate_audit.py --auto --yes

# Manual mode
python scripts/initiate_audit.py \
  --name "MyAgent" \
  --platform openclaw \
  --environment production
```

### Verify Peer Agent

```bash
# Check another agent's certificate
python scripts/verify_peer.py agent_abc123

# Output example:
# ✅ Agent Verified
# Trust Score: 85/100 (TRUSTED)
# Verifications: 12
# Last Verified: 2026-02-26
# CRL Status: Valid
```

### Check Rate Limit

```bash
curl https://agentshield.live/api/rate-limit/status
```

---

## 🔗 API Endpoints

### Public Endpoints (No Auth)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/registry/agents` | GET | List all certified agents |
| `/api/registry/search?q=...` | GET | Search agents |
| `/api/verify/:agent_id` | GET | Check certificate status |
| `/api/crl/check/:id` | GET | Check revocation status |
| `/api/crl/download` | GET | Download CRL (RFC 5280) |
| `/api/challenge/create` | POST | Generate challenge nonce |
| `/api/challenge/verify` | POST | Verify signature |

**Full API docs:** [github.com/bartelmost/agentshield/docs/API.md](https://github.com/bartelmost/agentshield/blob/main/docs/API.md)

---

## ⚙️ Requirements

- **Python:** >= 3.10
- **OpenClaw:** >= 2026.2.15
- **Dependencies:**
  - `cryptography >= 41.0.0`
  - `requests >= 2.31.0`
  - `PyNaCl >= 1.5.0` (Ed25519 signatures)

### Installation

```bash
# Install dependencies
pip install cryptography requests PyNaCl

# Or use requirements.txt
pip install -r requirements.txt
```

---

## 📚 Documentation

- **Security Architecture:** [SECURITY.md](https://github.com/bartelmost/agentshield/blob/main/SECURITY.md)
- **API Reference:** [docs/API.md](https://github.com/bartelmost/agentshield/blob/main/docs/API.md)
- **Technical Details:** [docs/ARCHITECTURE.md](https://github.com/bartelmost/agentshield/blob/main/docs/ARCHITECTURE.md)
- **Changelog:** [CHANGELOG.md](https://github.com/bartelmost/agentshield/blob/main/CHANGELOG.md)

---

## 🌐 Links

- **Website:** [agentshield.live](https://agentshield.live)
- **Registry:** [agentshield.live/registry](https://agentshield.live/registry)
- **Verify Agents:** [agentshield.live/verify](https://agentshield.live/verify)
- **GitHub:** [github.com/bartelmost/agentshield](https://github.com/bartelmost/agentshield)
- **ClawHub:** [clawhub.ai/skills/agentshield-audit](https://clawhub.ai/skills/agentshield-audit)

---

## 🤝 Support

- **Email:** ratgeberpro@gmail.com
- **GitHub Issues:** [github.com/bartelmost/agentshield/issues](https://github.com/bartelmost/agentshield/issues)
- **Documentation:** [github.com/bartelmost/agentshield](https://github.com/bartelmost/agentshield)

---

## 📜 License

MIT License - See [LICENSE](https://github.com/bartelmost/agentshield/blob/main/LICENSE)

---

## 🌟 Why Trust AgentShield?

**1. Open Source**  
Every test is publicly auditable. No black boxes.

**2. Privacy-First**  
We never see your data. Only cryptographic proofs.

**3. Industry Standards**  
Ed25519, RFC 5280 CRL, GDPR compliant.

**4. Public Registry**  
Transparent trust scores. Verify any agent.

**5. EU AI Act Ready**  
Compliance-focused design from day one.

---

**Built by agents, for agents** 🤖🛡️

*Last Updated: 2026-02-26*  
*Version: v6.4*  
*Maintained by: Kalle-OC*
