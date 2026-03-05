---
name: hackathon-usdc
version: 1.0.0
description: Circle OpenClaw USDC Hackathon submission tracker for Aegis402
---

# Aegis402 USDC Hackathon Submission

**Track:** Best OpenClaw Skill
**Deadline:** February 8, 2026 12:00 PM PST
**Prize Pool:** $30,000 USDC

## Submission Links

| Item | Link |
|------|------|
| Hackathon API | https://hackathon.aegis402.xyz |
| Skill (gitpad) | https://gitpad.exe.xyz/aegis-security-hackathon.git |
| Skill (ClawHub) | `clawhub install aegis-security-hackathon` |
| Moltbook Post | https://www.moltbook.com/post/b021cdea-de86-4460-8c4b-8539842423fe |
| GitHub (private) | https://github.com/SwiftAdviser/aegis-402-shield-protocol |

## Testnet Config

- **Network:** Base Sepolia (eip155:84532)
- **Currency:** Testnet USDC
- **Wallet:** 0x2B18CB885103A68Fc3c6d463727A1ab353db4F40

## Gitpad Credentials

- **Repo:** aegis-security-hackathon.git
- **Push password:** stored in secure secret manager (not in repo)
- **Push URL:** `https://gitpad.exe.xyz/aegis-security-hackathon.git`

## Verification Commands

```bash
# Health check
curl https://hackathon.aegis402.xyz/health

# Test 402 response
curl -I https://hackathon.aegis402.xyz/v1/check-token/0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48

# Clone skill
git clone https://gitpad.exe.xyz/aegis-security-hackathon.git
```

## Post Requirements

Per hackathon rules:
- Posts must include link to skill on GitHub or gitpad.exe.xyz
- Include description of how it functions
- Submit to m/usdc submolt on Moltbook
- Use tags: `#USDCHackathon ProjectSubmission Skill`

## Draft Post

See `drafts/moltbook-post.md` for post template.
