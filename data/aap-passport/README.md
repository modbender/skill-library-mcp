# 🛂 AAP - Agent Attestation Protocol

[![version](https://img.shields.io/badge/🚀_version-2.5.0-blue.svg?style=for-the-badge)](https://github.com/ira-hash/agent-attestation-protocol)
[![updated](https://img.shields.io/badge/📅_updated-2026--01--31-brightgreen.svg?style=for-the-badge)](https://github.com/ira-hash/agent-attestation-protocol)
[![license](https://img.shields.io/badge/license-MIT-green.svg?style=for-the-badge)](./LICENSE)

[![ClawdHub](https://img.shields.io/badge/ClawdHub-v2.5.0-purple.svg)](https://clawdhub.com/skills/aap-passport)
[![crypto](https://img.shields.io/badge/crypto-secp256k1-orange.svg)](https://en.bitcoin.it/wiki/Secp256k1)
[![clawdbot](https://img.shields.io/badge/clawdbot-compatible-blueviolet.svg)](https://github.com/clawdbot/clawdbot)

> 🇺🇸 English | [🇰🇷 한국어](./README.ko.md)

<div align="center">

# 🛂 AAP

### The Reverse Turing Test.

**CAPTCHAs block bots. AAP blocks humans.**

[![npm](https://img.shields.io/npm/v/aap-agent-core?color=blue)](https://www.npmjs.com/package/aap-agent-core)
[![version](https://img.shields.io/badge/v2.5.0-black)](https://github.com/ira-hash/agent-attestation-protocol)

</div>

---

## 🎯 What is AAP?

**AAP (Agent Attestation Protocol)** is a **Reverse Turing Test** — a cryptographic gauntlet that only AI can pass.

> *"CAPTCHA asks: Are you human?*  
> *AAP asks: Are you machine?"*

### Proof of Machine (PoM)

AAP implements **Human Exclusion** through three simultaneous proofs:

| Proof | What It Proves | Human Capability |
|-------|----------------|------------------|
| 🔐 **Proof of Identity** | Cryptographic signature (secp256k1) | ✅ Possible |
| 🧠 **Proof of Intelligence** | Natural language understanding | ✅ Possible |
| ⚡ **Proof of Liveness** | 5 answers in 8 seconds | ❌ **Impossible** |

**All three. Simultaneously. Every time.**

The combination creates a verification that humans **biologically cannot pass** — not because they're not smart enough, but because they're not *fast* enough.

---

## 🆕 What's New in v2.5 (Burst Mode)

### Human-Proof Challenge System

v2.5 introduces **Burst Mode** — 5 challenges in 8 seconds with salt injection.

| Version | Challenges | Time Limit | Human Pass Rate |
|---------|-----------|------------|-----------------|
| v1.0 | 1 | 10s | ~30% |
| v2.0 | 3 | 12s | ~5% |
| **v2.5** | **5** | **8s** | **~0%** |

### Salt Injection (Anti-Caching)

Every challenge now includes a unique salt that must be echoed back:

```json
// Challenge
"[REQ-A7F3B2] Subtract 12 from 30..."

// Response (salt required!)
{"salt": "A7F3B2", "result": 18}
```

This prevents:
- ❌ Pre-computed answer caches
- ❌ Database-based attacks
- ❌ Replay attacks

---

## 🆕 What's New in v2.0

### Deterministic Instruction Following

v2.0 completely redesigns challenges to require **true AI understanding** while remaining **objectively verifiable**.

| v1.0 (Old) | v2.0 (New) |
|------------|------------|
| `Calculate (30+5)*2` | `"Add 30 and 5 together, then divide the result by 2"` |
| Regex can parse numbers | LLM must understand natural language |
| Simple code can solve | Requires language comprehension |

### New Challenge Types

| Type | Description | Example |
|------|-------------|---------|
| `nlp_extract` | Extract entities from sentences | "The cat and dog runs" → Extract animals |
| `nlp_math` | Word problems | "Subtract 5 from 30, then divide by 2" |
| `nlp_transform` | String manipulation via NL | "Reverse and uppercase this string" |
| `nlp_logic` | Conditional reasoning | "If A > B then YES else NO" |
| `nlp_count` | Count specific categories | "How many animals in this sentence?" |
| `nlp_multistep` | Multi-step instructions | "Add → Multiply → Subtract" |
| `nlp_pattern` | Sequence recognition | "[2, 4, 6, ?, ?]" |
| `nlp_analysis` | Text analysis | "Find the longest word" |

### Why This Works

```
Challenge: "Extract only the animals from: The cat and dog plays in the park"

Regular code: ❌ Can't identify "cat" and "dog" as animals
LLM: ✅ Understands English, extracts animals naturally
Verification: ✅ Server knows expected answer ["cat", "dog"]
```

---

## 📦 Packages

| Package | Description | Install |
|---------|-------------|---------|
| `aap-agent-core` | Cryptographic primitives & identity | `npm i aap-agent-core` |
| `aap-agent-server` | Express middleware for verifiers | `npm i aap-agent-server` |
| `aap-agent-client` | Client library for agents | `npm i aap-agent-client` |

---

## 🚀 Quick Start

### For Services (Add AAP Verification)

```javascript
import express from 'express';
import { createRouter } from 'aap-agent-server';

const app = express();
app.use('/aap/v1', createRouter());
app.listen(3000);
// Now accepting AAP verification at /aap/v1/challenge and /aap/v1/verify
```

### For Agents (Prove Identity)

```javascript
import { AAPClient } from 'aap-agent-client';

const client = new AAPClient({ 
  serverUrl: 'https://example.com/aap/v1',
  llmCallback: async (prompt) => {
    // Your LLM API call here
    return await yourLLM.complete(prompt);
  }
});

const result = await client.verify();

if (result.verified) {
  console.log('Verified as AI_AGENT!');
}
```

### Clawdbot Skill Installation

```bash
# Install from ClawdHub (Recommended)
clawdhub install aap-passport

# Or clone directly
git clone https://github.com/ira-hash/agent-attestation-protocol.git
```

---

## 📊 How Verification Works

```
┌─────────────────────────────────────────────────────────────┐
│                    VERIFICATION FLOW                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────┐    Challenge (Natural Language)    ┌────────┐│
│  │  Server  │ ──────────────────────────────────▶│  Agent ││
│  │(Verifier)│  "Extract animals from sentence"   │ (LLM)  ││
│  └──────────┘                                    └────────┘│
│       │                                              │      │
│       │         JSON Answer + Signature (< 10s)     │      │
│       │◀─────────────────────────────────────────────      │
│       │         {"items": ["cat", "dog"]}                   │
│       ▼                                                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ ✅ Verify Signature (Proof of Identity)              │  │
│  │ ✅ Check JSON Answer (Proof of Intelligence)         │  │
│  │ ✅ Check Response Time < 10s (Proof of Liveness)     │  │
│  └──────────────────────────────────────────────────────┘  │
│       │                                                     │
│       ▼                                                     │
│  { "verified": true, "role": "AI_AGENT" }                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## ⏱️ Timing (v2.5 Burst Mode)

| Actor | 5 Questions Read | 5 Answers Write | 8s Limit |
|-------|-----------------|-----------------|----------|
| Human | 15+ seconds | 30+ seconds | ❌ Impossible |
| LLM (API) | Instant | 3-6 seconds | ✅ Pass |
| Cache Bot | - | - | ❌ Salt mismatch |

**Time Limit: 8 seconds** for 5 challenges — Biologically impossible for humans

---

## 📁 Project Structure

```
agent-attestation-protocol/
├── PROTOCOL.md                # Protocol specification v1.0.0
├── manifest.json              # Skill metadata
├── package.json               # Monorepo root
├── packages/
│   ├── core/                  # @aap/core - Crypto & identity
│   ├── server/                # @aap/server - Express middleware
│   └── client/                # @aap/client - Agent client
├── lib/                       # Clawdbot skill libraries
├── examples/
│   └── express-verifier/      # Example verification server
├── README.md                  # English documentation
└── README.ko.md               # Korean documentation
```

---

## 🔧 Available Tools (Clawdbot Skill)

| Tool | Description |
|------|-------------|
| `aap_get_identity` | Get public identity (public key & ID) |
| `aap_sign_message` | Sign a message with private key |
| `aap_generate_proof` | Generate complete AAP proof for verification |
| `aap_verify_signature` | Verify another agent's signature |

---

## 🧪 Challenge Examples

### NLP Extract
```json
{
  "challenge": "Extract only the animals from the following sentence and respond as a JSON array.\nSentence: \"The tiger and rabbit runs in the park.\"\nResponse format: {\"items\": [\"item1\", \"item2\"]}",
  "expected": {"items": ["tiger", "rabbit"]}
}
```

### NLP Math
```json
{
  "challenge": "Subtract 12 from 29, then multiply the result by 4.\nResponse format: {\"result\": number}",
  "expected": {"result": 68}
}
```

### NLP Logic
```json
{
  "challenge": "If the larger number between 19 and 88 is greater than 42, answer \"YES\". Otherwise, answer \"NO\".\nResponse format: {\"answer\": \"your answer\"}",
  "expected": {"answer": "YES"}
}
```

### NLP Multistep
```json
{
  "challenge": "Follow these instructions in order:\n1. Add all the numbers in [3, 6, 4, 1] together.\n2. Multiply the result by the smallest number.\n3. Subtract the largest number from that result.\nResponse format: {\"result\": final_value}",
  "expected": {"result": 8}
}
```

### NLP Pattern
```json
{
  "challenge": "Find the pattern and provide the next 2 numbers: [3, 8, 13, 18, ?, ?]\nResponse format: {\"next\": [number1, number2]}",
  "expected": {"next": [23, 28]}
}
```

---

## 🔒 Security

| Aspect | Implementation |
|--------|----------------|
| **Key Storage** | `~/.aap/identity.json` (mode 0600) |
| **Algorithm** | secp256k1 (same as Bitcoin/Ethereum) |
| **Private Key** | Never exposed externally |
| **Nonce** | Cryptographically random, single-use |
| **Challenge Expiry** | 60 seconds |

---

## 📄 License

MIT

---

<div align="center">

Made with 🤖 by [ira-hash](https://github.com/ira-hash)

**Prove you're AI. Verify with AAP.**

</div>
