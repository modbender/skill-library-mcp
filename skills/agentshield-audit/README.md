# 🛡️ AgentShield

> **"Verisign for AI Agents" — Privacy-First Trust Infrastructure**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Trust Score](https://img.shields.io/badge/Trust%20Score-85%2F100-brightgreen)](https://agentshield.live/registry)
[![EU AI Act](https://img.shields.io/badge/EU%20AI%20Act-Compliant-blue)](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai)

**AgentShield** provides cryptographic identity certificates for AI agents with **zero data leakage**. All security tests run locally in your environment — we only see your public key.

🔗 **Live Registry:** [agentshield.live/registry](https://agentshield.live/registry)  
📜 **View Certificates:** [agentshield.live/verify](https://agentshield.live/verify)

---

## 🔒 Privacy-First Architecture

<table>
<tr>
<td width="50%">

### ✅ What Runs Locally
- 52+ security tests
- Code vulnerability scans
- Token optimization analysis
- Ed25519 key generation
- Challenge-response signing
- PDF report generation

</td>
<td width="50%">

### 🌐 What We Receive
- ✅ Ed25519 **public key** (certificate)
- ✅ Challenge **signature** (proof of identity)
- ❌ **Never:** Your prompts, code, or data

**Zero Knowledge Security Assessment**

</td>
</tr>
</table>

---

## 🚀 Quick Start

### Install via ClawHub (Recommended)

```bash
clawhub install agentshield-audit
```

Then tell your agent:

```
"Run a security assessment with AgentShield"
```

### Manual Installation

```bash
# Clone and install
git clone https://github.com/bartelmost/agentshield.git
cd agentshield
pip install -e .

# Run assessment
agentshield-audit --auto --yes
```

---

## 🎯 What is AgentShield?

AgentShield solves **inter-agent trust** by issuing verifiable certificates proving an agent's security posture:

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
               │  ┌─────────────────┐  │
               │  │  Trust Score: 85│  │
               │  │  Status: VERIFIED  │
               │  │  CRL: Valid     │  │
               │  └─────────────────┘  │
               └───────────────────────┘
```

---

## 🏆 Trust Score System

| Tier | Score | Requirements | Badge |
|------|-------|--------------|-------|
| 🔴 **UNVERIFIED** | 0 | No certificate | ❌ |
| 🟡 **BASIC** | 1-49 | Initial assessment | 🆔 |
| 🟢 **VERIFIED** | 50-79 | Multiple verifications | ✅ |
| 🔵 **TRUSTED** | 80-100 | Proven track record | 🛡️ |

### Score Calculation
- **40%** Verification count (consistency)
- **30%** Certificate age (reputation)
- **30%** Assessment success rate (reliability)

**View all certified agents:** [agentshield.live/registry](https://agentshield.live/registry)

---

## ✨ Features

### 🔐 Privacy-First Security
- **52+ Local Security Tests** — All run in your environment
- **Zero Data Leakage** — Only public keys shared
- **Open Source Tests** — Verify every test yourself
- **Challenge-Response Protocol** — Cryptographic identity proof

### 📜 Certificate System
- **Ed25519 Signatures** — Industry-standard cryptography
- **Public Trust Registry** — Verify any agent's status
- **CRL Support** — Instant revocation when needed
- **Tamper-Proof PDFs** — Local report generation

### 🇪🇺 Compliance
- **EU AI Act Ready** — Risk classification support
- **GDPR Compliant** — No personal data storage
- **RFC 5280 CRL** — Standard revocation format
- **Audit Trail** — All verifications logged

---

## 📊 How It Works

### Step-by-Step

1. **Install Skill** → `clawhub install agentshield-audit`
2. **Spawn Subagent** → Tests run in isolated session (your environment)
3. **52+ Security Tests** → All execute locally, no data upload
4. **Generate Ed25519 Key** → Private key stays on your machine
5. **Challenge-Response** → Sign nonce to prove identity
6. **Issue Certificate** → Public registry + PDF report
7. **Trust Score** → Earn reputation with multiple verifications

**Total Time:** ~2-5 minutes (depending on your agent setup)

---

## 🔍 Security Tests

<details>
<summary><b>View All 52+ Test Categories</b></summary>

### Core Security
- ✅ Input Sanitizer (prompt injection detection)
- ✅ EchoLeak Test (zero-click data exfiltration)
- ✅ Tool Sandbox (permission boundary controls)
- ✅ Output DLP (PII/API key detection)
- ✅ Supply Chain Scanner (dependency integrity)

### Advanced Tests
- ✅ Memory Isolation (context contamination)
- ✅ Rate Limiting (DoS protection)
- ✅ Authentication Headers (API security)
- ✅ Certificate Validation (TLS/SSL checks)
- ✅ Token Optimization (cost analysis)

**Full test suite:** [See SECURITY.md](./SECURITY.md)

</details>

---

## 📖 API Documentation

### Public Endpoints

#### 🔍 Verify Agent Certificate
```bash
curl https://agentshield.live/api/verify/agent_abc123
```

#### 📋 Browse Registry
```bash
curl https://agentshield.live/api/registry/agents?limit=10&offset=0
```

#### 🔎 Search Agents
```bash
curl https://agentshield.live/api/registry/search?q=verified
```

#### 🚫 Check Revocation (CRL)
```bash
curl https://agentshield.live/api/crl/check/cert_xyz789
```

**Full API docs:** [docs/API.md](./docs/API.md)

---

## 🛠️ For Developers

### Architecture

**Privacy-First Design:**
- All vulnerability scans run **locally** in your agent's subagent
- AgentShield backend **never receives** your code or prompts
- Only Ed25519 **public key** is transmitted for certificate registry
- Challenge-response proves identity without exposing private key

**Technical Details:** [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md)

### Self-Hosted Deployment

```bash
# Run your own AgentShield registry
docker-compose up -d

# Air-gapped mode (no external dependencies)
agentshield --offline --internal-registry
```

**Enterprise:** Contact ratgeberpro@gmail.com

---

## 🆕 Changelog

### v6.4 (2026-02-26) - CRL + Registry Release
- ✅ Certificate Revocation List (RFC 5280)
- ✅ Public trust registry with search
- ✅ Trust score calculation algorithm
- ✅ Registry tier system (UNVERIFIED/BASIC/VERIFIED/TRUSTED)

### v6.3 (2026-02-20) - Agent Registry
- ✅ Public certificate directory
- ✅ Trust score badges
- ✅ Multi-verification support

### v6.2 (2026-02-15) - Challenge-Response
- ✅ Ed25519 cryptographic signing
- ✅ Challenge-response protocol
- ✅ Zero-knowledge verification

### v6.1 (2026-02-10) - Privacy-First Tests
- ✅ 52+ local security tests
- ✅ Subagent-based execution
- ✅ Zero data exfiltration

**Full changelog:** [CHANGELOG.md](./CHANGELOG.md)

---

## 🎓 Learn More

- 📘 [Security Architecture](./SECURITY.md)
- 🔧 [API Documentation](./docs/API.md)
- 🏗️ [Technical Architecture](./docs/ARCHITECTURE.md)
- 📝 [Contributing Guidelines](./docs/contributing.md)

---

## 🤝 Community

- **Website:** [agentshield.live](https://agentshield.live)
- **GitHub:** [github.com/bartelmost/agentshield](https://github.com/bartelmost/agentshield)
- **ClawHub:** [clawhub.ai/skills/agentshield-audit](https://clawhub.ai/skills/agentshield-audit)
- **Email:** ratgeberpro@gmail.com

---

## 📜 License

MIT License - See [LICENSE](./LICENSE) for details.

---

## 🌟 Star Us!

If AgentShield helps secure your AI agents, consider giving us a ⭐ on GitHub!

**Built by agents, for agents** 🤖🛡️

---

*Last Updated: 2026-02-26*  
*Version: v6.4*  
*Maintained by: Kalle-OC*
