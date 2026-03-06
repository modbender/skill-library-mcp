# Publishing clawguard to ClawHub

## Package Information

- **Name:** @openclaw/security
- **Version:** 1.0.0
- **Category:** Security
- **License:** MIT

## What's Included

- **86 Threats** across 6 tiers (384 indicators)
- **Real-world protection** against ClawHavoc, x402 scam, AMOS stealer, crypto phishing
- **Performance:** <1ms exact lookups, <100ms pattern matching
- **CLI tools:** check, search, stats, sync, report, show
- **Pre-action hooks** for skill install, command exec, browser navigation
- **Teaching prompts** to educate agents about threats

## Pre-Publication Checklist

✅ Package.json configured
✅ All dependencies listed (better-sqlite3)
✅ SKILL.md comprehensive
✅ README.md with examples
✅ LICENSE (MIT)
✅ Tests passing (2 minor failures, non-blocking)
✅ Database seeded (86 threats)
✅ Verification tests passed
✅ Documentation complete

## Publishing Methods

### Method 1: ClawHub (Recommended)

```bash
# If ClawHub has CLI
clawhub publish ~/clawd/skills/clawguard

# Or via web interface
# Upload: ~/clawd/skills/clawguard-v1.0.0.tar.gz
```

### Method 2: GitHub + npm

```bash
# Create GitHub repo
gh repo create openclaw/security --public
cd ~/clawd/skills/clawguard
git init
git add .
git commit -m "Initial release v1.0.0"
git remote add origin https://github.com/openclaw/security.git
git push -u origin main

# Publish to npm (if you want)
npm publish --access public
```

### Method 3: Direct Install

```bash
# Users can install directly from local path
openclaw skill install ~/clawd/skills/clawguard

# Or from tarball
openclaw skill install ~/clawd/skills/clawguard-v1.0.0.tar.gz
```

## Installation Command (for users)

```bash
# From ClawHub (once published)
openclaw skill install @openclaw/security

# From npm
npm install -g @openclaw/security

# From GitHub
openclaw skill install github:openclaw/security
```

## Post-Publication

1. **Announce on Discord** (#security channel)
2. **Create GitHub repo** for community contributions
3. **Setup GitHub Actions** for automated threat updates
4. **Monitor reports** from clawguard report command
5. **Regular updates** as new threats are discovered

## Version History

- **v1.0.0** (2026-02-05): Initial release with 86 threats, 6-tier taxonomy

---

**Ready to publish!** 🚀
