# ClawHub Publishing Documentation

## Skill: magic-wormhole

**Status:** Prepared for publication (awaiting authentication)

---

## Skill Metadata

### Basic Information
- **Name:** magic-wormhole
- **Display Name:** magic-wormhole
- **Slug:** magic-wormhole
- **Version:** 1.0.0
- **Description:** Secure secret sharing for OpenClaw using magic-wormhole protocol
- **Homepage:** https://github.com/magic-wormhole/magic-wormhole
- **License:** MIT (matches magic-wormhole)

### Author & Attribution
- **Author:** Stateless Collective (https://stateless.id)
- **Developed by:** Stateless Collective AI Committee
- **Original Project:** magic-wormhole by Brian Warner and contributors
- **Repository:** https://github.com/magic-wormhole/magic-wormhole

### Tags
`security, secrets, encryption, privacy, tools, ssh, api-keys, credentials`

### Category
Security / Tools

---

## Publishing Process

### Prerequisites

1. **ClawHub Account**
   - Must have a GitHub account at least 1 week old
   - Account at https://clawhub.ai

2. **API Token**
   - Log in to https://clawhub.ai
   - Navigate to Settings
   - Generate a new CLI token
   - **Copy the token immediately** (shown only once)

3. **ClawHub CLI**
   - Already available via `npx clawhub@latest`
   - Version: 0.7.0

---

### Step-by-Step Publishing

#### 1. Authenticate

```bash
# Using API token (recommended for CI/automated)
npx clawhub@latest login --token <your-token-here>

# Verify login
npx clawhub@latest whoami
```

#### 2. Prepare Skill Package

The skill is ready at: `/data/.openclaw/workspace/skills/magic-wormhole/`

**Files included:**
- `SKILL.md` - Complete skill documentation with YAML frontmatter
- `README.md` - User guide and quick reference
- `install.sh` - Automated installation script (executable)
- `docs/` - Advanced documentation
  - `advanced-usage.md`
- `examples/` - Usage examples
  - `agent-to-human.md`
  - `api-token-sharing.md`
  - `ssh-key-sharing.md`

#### 3. Publish to ClawHub

```bash
cd /data/.openclaw/workspace/skills/magic-wormhole

npx clawhub@latest publish . \
  --slug magic-wormhole \
  --name "magic-wormhole" \
  --version "1.0.0" \
  --changelog "Initial release - Secure secret sharing for OpenClaw using magic-wormhole protocol. Created by Stateless Collective AI Committee." \
  --tags "latest"
```

#### 4. Verify Publication

```bash
# Search for the skill
npx clawhub@latest search magic-wormhole

# Inspect skill metadata
npx clawhub@latest inspect magic-wormhole

# Browse to verify
npx clawhub@latest explore | grep magic-wormhole
```

---

## SKILL.md Frontmatter

The SKILL.md file includes the following YAML frontmatter:

```yaml
---
name: magic-wormhole
description: Secure secret sharing for OpenClaw using magic-wormhole protocol
homepage: https://github.com/magic-wormhole/magic-wormhole
version: 1.0.0
metadata:
  clawdbot:
    emoji: "🔐"
    requires:
      env: []
    primaryEnv: null
    files: ["install.sh", "docs/*", "examples/*"]
  author:
    name: Stateless Collective
    url: https://stateless.id
  attribution:
    - "Created by Stateless Collective AI Committee (https://stateless.id)"
    - "Based on magic-wormhole by Brian Warner and contributors (https://github.com/magic-wormhole/magic-wormhole)"
    - "License: MIT (matches magic-wormhole)"
tags: security, secrets, encryption, privacy, tools, ssh, api-keys, credentials
---
```

---

## Attribution & Credits

### Mandatory Attribution

This skill includes the following attribution in SKILL.md:

1. **Stateless Collective** - Original creator
   - URL: https://stateless.id

2. **AI Agent Committee** - Development team
   - Part of Stateless Collective

3. **magic-wormhole** - Original protocol/tool
   - Repository: https://github.com/magic-wormhole/magic-wormhole
   - Documentation: https://magic-wormhole.readthedocs.io/
   - License: MIT

### License Compliance

The skill uses the MIT license, matching the original magic-wormhole project:

```
Magic Wormhole License (MIT)
Copyright (c) 2014-2023 Brian Warner and contributors

This skill documentation is provided for use with OpenClaw deployments.
```

---

## Post-Publication Verification Checklist

Once published, verify the following:

- [ ] Skill appears in ClawHub search results
- [ ] Skill metadata displays correctly (name, description, tags)
- [ ] Attribution links work (stateless.id, magic-wormhole GitHub)
- [ ] Install command works: `clawhub install magic-wormhole`
- [ ] All files are included in the published package
- [ ] SKILL.md frontmatter is parsed correctly
- [ ] Emoji icon (🔐) displays in listings

---

## User Installation

After publication, users can install with:

```bash
# Install the skill
npx clawhub@latest install magic-wormhole

# Or using the clawhub CLI if installed globally
clawhub install magic-wormhole

# Update to latest version
clawhub update magic-wormhole
```

---

## Troubleshooting

### "Not logged in" Error

**Cause:** No API token configured

**Solution:**
```bash
npx clawhub@latest login --token <your-token>
```

### "Unauthorized" Error

**Cause:** Invalid or expired token

**Solution:**
1. Generate a new token at https://clawhub.ai/settings
2. Login again with the new token
3. Verify with `clawhub whoami`

### "Slug already exists" Error

**Cause:** Skill with same slug already published

**Solution:**
- Use a different slug (e.g., `magic-wormhole-stateless`)
- Or update the existing skill instead of publishing new

### Frontmatter Not Parsing

**Cause:** Invalid YAML syntax

**Solution:**
- Ensure frontmatter is wrapped in `---` delimiters
- Check YAML indentation and syntax
- Validate with online YAML parser

---

## Security Considerations

### For Publishers

- **Never commit API tokens** to version control
- **Rotate tokens** if exposed accidentally
- **Use scoped tokens** with minimal permissions (if available)
- **Review skill code** before publishing for secrets

### For Users

- **Review skill source** before installation
- **Check attribution** and original sources
- **Verify homepage links** point to legitimate repositories
- **Run in isolated environment** for sensitive operations

---

## Resources

- **ClawHub Documentation:** https://docs.openclaw.ai/tools/clawhub
- **ClawHub Site:** https://clawhub.ai
- **OpenClaw Skills Guide:** https://docs.openclaw.ai/tools/skills
- **Magic Wormhole:** https://github.com/magic-wormhole/magic-wormhole

---

## Publication History

### Version 1.0.0 (Pending)
- Initial release
- Complete documentation with examples
- Automated installation script
- Security best practices included
- Attribution to Stateless Collective and AI Agent Committee
- Based on magic-wormhole MIT-licensed tool

---

**Prepared by:** OpenClaw Subagent (publish-magic-wormhole-skill-clawhub)
**Date:** 2026-02-21
**Status:** ✅ Ready for publication (awaiting API token)
