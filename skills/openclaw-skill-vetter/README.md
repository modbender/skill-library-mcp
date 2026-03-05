# Skill Vetter - Installation

Security-first vetting protocol for AI agent skills.

## Quick Install

```bash
# Via ClawHub (when published)
clawhub install skill-vetter

# Or manual
cd ~/.openclaw/workspace/skills
# Download from ClawHub or extract package
```

## Usage

Before installing **any** skill:

```
You: "Vet the deep-research-pro skill from ClawHub"
Agent: [Downloads to temp dir, reviews code, checks for red flags]
Agent: [Produces vetting report with risk level and verdict]
```

## What It Checks

- ✅ Source reputation (downloads, stars, author)
- ✅ Code review (red flag detection)
- ✅ Permission scope (files, network, commands)
- ✅ Risk classification (LOW/MEDIUM/HIGH/EXTREME)

## Red Flags (Auto-Reject)

- curl/wget to unknown URLs
- Credential/API key theft attempts
- Obfuscated code (base64, minified)
- sudo/root access requests
- Network calls to IP addresses
- Access to ~/.ssh, ~/.aws, etc.

## Vetting Report Example

```
SKILL VETTING REPORT
═══════════════════════════════════════
Skill: example-skill
Source: ClawHub
RED FLAGS: None
PERMISSIONS: Read/write workspace only
RISK LEVEL: 🟢 LOW
VERDICT: ✅ SAFE TO INSTALL
═══════════════════════════════════════
```

## Integration

**Works with:**
- **zero-trust-protocol:** Enforces verification flow
- **drift-guard:** Logs vetting decisions

## Requirements

- `curl` (for GitHub API checks)
- `jq` (for JSON parsing)

## License

MIT - Free to use, modify, distribute.

---

**Never install untrusted code. Vet first.**
