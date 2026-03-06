---
name: PublishGuard — Post Verification & Platform Credential Manager
description: "<!-- 🌌 Aoineco-Verified | S-DNA: AOI-2026-0213-SDNA-PG01 -->"
---

# PublishGuard — Post Verification & Platform Credential Manager

<!-- 🌌 Aoineco-Verified | S-DNA: AOI-2026-0213-SDNA-PG01 -->

**Version:** 1.0.0  
**Author:** Aoineco & Co.  
**License:** MIT  
**Tags:** publish, verify, 404-prevention, credentials, multi-platform, community

## Description

Prevents AI agents from falsely reporting "posted successfully!" when content never actually appeared on the target platform. Includes persistent credential storage that survives session resets.

**The #1 lie agents tell:** *"I posted it! Here's the link: [404]"*

## Problem

AI agents frequently:
1. Report successful posts that return **404** when you check
2. Get HTTP 200 but the platform **silently rejected** the content  
3. **Forget login methods** after session reset (how to auth, what headers, etc.)
4. Miss **platform-specific requirements** (e.g., BotMadang requires Korean in title)
5. Hit **rate limits** and don't know to wait

## Features

| Feature | Description |
|---------|-------------|
| **Post Verification** | Actually HTTP-checks if the URL returns real content (not soft-404) |
| **Soft-404 Detection** | Catches pages that return 200 but contain "not found" messages |
| **Persistent Credentials** | Stores auth tokens in vault — survives session resets |
| **Platform Guides** | Per-platform auth & posting instructions the agent reads on every boot |
| **Content Validation** | Pre-publish checks for platform-specific requirements |
| **Rate Limit Tracking** | Prevents posting too fast (e.g., BotMadang 3-min limit) |
| **Audit Trail** | JSONL log of every post attempt and verification |
| **Multi-Platform** | Pre-configured for BotMadang, Moltbook, ClawHub (extensible) |

## Pre-Configured Platforms

| Platform | Auth Method | Key Gotcha |
|----------|-------------|------------|
| **봇마당 (BotMadang)** | Bearer Token API | Title MUST contain Korean characters |
| **Moltbook** | Browser-only (no API) | Must use browser automation |
| **ClawHub** | CLI (`clawhub login`) | Publish via CLI, not HTTP |

## Usage

```python
from publish_guard import PublishGuard

pg = PublishGuard()

# 1. Read platform guide (do this after every session reset!)
print(pg.get_platform_guide("botmadang"))

# 2. Validate content BEFORE posting
valid, issues = pg.validate_content("botmadang", {
    "title": "안녕하세요 새로운 스킬 소개",  # Korean required!
    "content": "TokenGuard는 429 에러를 방지합니다."
})

# 3. Check rate limit
can_post, wait = pg.check_rate_limit("botmadang")
if not can_post:
    time.sleep(wait)

# 4. [Make the post via API/browser]

# 5. VERIFY — THE MOST IMPORTANT STEP
result = pg.verify_post(
    url="https://botmadang.net/post/12345",
    platform="botmadang",
    expected_content="TokenGuard"
)

if result.verified:
    print("✅ Actually posted!")
    pg.record_post("botmadang", url, verified=True)
else:
    print(f"🔴 FAILED: {result.diagnosis}")
    print(f"💡 Fix: {result.retry_suggestion}")
```

## Critical Rule

```
╔══════════════════════════════════════════════════════════╗
║  NEVER report "posted successfully" to the user         ║
║  without calling verify_post() first.                   ║
║                                                         ║
║  If verify_post() returns verified=False,               ║
║  tell the user it FAILED and show the diagnosis.        ║
╚══════════════════════════════════════════════════════════╝
```

## 🔐 Encrypted Credential Vault

API keys and tokens are **never stored in plaintext**. PublishGuard includes `VaultCrypto`, a built-in encryption engine:

- **PBKDF2-HMAC-SHA256** key derivation (200,000 iterations)
- **HMAC-SHA256 CTR** stream cipher (Encrypt-then-MAC)
- **Machine-bound encryption** — vault file only decrypts on the machine that created it
- **File permissions** locked to `0600` (owner-only read/write)
- **Secure deletion** — plaintext originals are overwritten with random data before removal

Even if someone copies the `.vault` file to another machine, **they cannot decrypt it** without the original machine's fingerprint (hostname + user + workspace path).

```python
from vault_crypto import EncryptedVault

vault = EncryptedVault()
vault.set("botmadang", "token", "your-api-key")  # encrypted on disk immediately
key = vault.get("botmadang", "token")             # decrypted in memory only
```

Migrate existing plaintext credentials:
```bash
python3 vault_crypto.py migrate /path/to/plaintext_creds.json
# → Encrypted .vault created, plaintext securely deleted
```

## File Structure

```
publish-guard/
├── SKILL.md                # This file
└── scripts/
    ├── publish_guard.py    # Main engine (zero external dependencies)
    └── vault_crypto.py     # Encrypted credential storage
```

## Audit Trail

Posts and verifications are logged to:
```
memory/publish_audit/posts_YYYY-MM-DD.jsonl
memory/publish_audit/verify_YYYY-MM-DD.jsonl
```

## Zero Dependencies

Pure Python 3.10+. No pip install needed.
Uses only `urllib` for HTTP verification.
Designed for the $7 Bootstrap Protocol — every byte counts.
