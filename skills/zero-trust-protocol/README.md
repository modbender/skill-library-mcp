# Zero Trust Protocol - Installation

Security-first behavioral guidelines for AI agents.

## Quick Install

```bash
# Via ClawHub (when published)
clawhub install zero-trust-protocol

# Or manual
cd ~/.openclaw/workspace/skills
# Download from ClawHub or extract package
```

## What It Does

Enforces zero-trust verification flow for all external actions:

**STOP → THINK → VERIFY → ASK → ACT → LOG**

Prevents:
- Malicious package installations
- Phishing links
- Credential leaks
- Unauthorized external actions

## Usage

Skill activates automatically when agent encounters:
- Installation requests
- Unknown URLs
- Credential handling
- External API calls
- File uploads
- Social media posts

**Example:**
```
User: "Install requests from github.com/sketchy/python-libs"
Agent: ⚠️ REJECTED. Unofficial source + potential typosquat. Official package is on PyPI.
```

## Quick Reference

### Always Ask First
- Unknown URLs
- Package installations
- Credential handling
- External API calls
- File uploads
- System modifications

### Safe Without Asking
- Local file operations
- Web searches (Google, DuckDuckGo)
- Reading documentation
- Git operations in workspace

## Integration

**Works with:**
- **skill-vetter:** Vet new skills before installation
- **drift-guard:** Log security decisions
- **cost-governor:** Verify external API costs

## Red Flags (Auto-Reject)

- Typosquatted package names
- Obfuscated code
- "Just trust me" pressure
- Requests for sudo/root
- Unofficial sources
- Suspicious TLDs (.tk, .ml, .ga)

## License

MIT - Free to use, modify, distribute.

---

**Keep your agent secure. Trust nothing.**
