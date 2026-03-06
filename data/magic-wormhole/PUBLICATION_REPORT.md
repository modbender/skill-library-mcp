# Publication Report: magic-wormhole Skill to ClawHub

**Date:** 2026-02-21
**Status:** 🟡 Prepared - Awaiting Authentication
**Subagent:** publish-magic-wormhole-skill-clawhub

---

## Executive Summary

The magic-wormhole skill has been successfully prepared for publication to ClawHub (clawhub.ai). All required files, documentation, and metadata are in place. **Authentication is the only remaining step** before publishing can proceed.

---

## 1. Research Findings: ClawHub Publishing Process

### Discovery Summary

**ClawHub** is the public marketplace for OpenClaw AI agent skills at https://clawhub.ai.

**Publishing Requirements:**
- GitHub account at least 1 week old (anti-abuse measure)
- SKILL.md with YAML frontmatter for metadata
- ClawHub CLI tool (available via `npx clawhub@latest`)
- API token generated from ClawHub Settings

**Publishing Command:**
```bash
clawhub publish <path> \
  --slug <unique-slug> \
  --name <display-name> \
  --version <semver> \
  --changelog <text> \
  --tags latest
```

**Authentication Flow:**
1. Visit https://clawhub.ai
2. Sign in with GitHub OAuth
3. Navigate to Settings
4. Generate CLI token
5. Authenticate CLI: `clawhub login --token <token>`

**Security Context:**
- ClawHub has experienced malware attacks (~13.4% of skills flagged)
- Skills inherit full agent permissions (shell, file access, etc.)
- VirusTotal partnership scans all uploads since Feb 7, 2026
- Users can flag malicious skills; auto-hide after 3+ reports

---

## 2. Skill Package: Prepared & Complete

### File Structure

```
/data/.openclaw/workspace/skills/magic-wormhole/
├── SKILL.md                    (602 lines) - Main documentation with frontmatter
├── README.md                   (402 lines) - User guide
├── install.sh                  (204 lines, executable) - Automated installer
├── PACKAGE_SUMMARY.md          - Package overview
├── CLAWHUB_PUBLISHING.md       - Publishing documentation
├── docs/
│   └── advanced-usage.md       (869 lines)
└── examples/
    ├── agent-to-human.md       (586 lines)
    ├── api-token-sharing.md    (594 lines)
    └── ssh-key-sharing.md      (365 lines)

Total: 3,622 lines of documentation
```

### SKILL.md Frontmatter (Added)

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

### Attribution Compliance

✅ **Stateless Collective** - Credited as author (https://stateless.id)
✅ **AI Agent Committee** - Credited as development team
✅ **magic-wormhole** - Original tool referenced with GitHub link
✅ **License** - MIT license documented

---

## 3. Publication Metadata

### Core Information

| Field | Value |
|-------|-------|
| **Name** | magic-wormhole |
| **Display Name** | magic-wormhole |
| **Slug** | magic-wormhole |
| **Version** | 1.0.0 |
| **Description** | Secure secret sharing for OpenClaw using magic-wormhole protocol |
| **Category** | Security / Tools |
| **Homepage** | https://github.com/magic-wormhole/magic-wormhole |
| **License** | MIT |
| **Emoji** | 🔐 |

### Author Information

- **Organization:** Stateless Collective
- **Website:** https://stateless.id
- **Development Team:** AI Agent Committee
- **Original Project:** magic-wormhole by Brian Warner

### Tags

`security, secrets, encryption, privacy, tools, ssh, api-keys, credentials`

### Changelog

```
Initial release - Secure secret sharing for OpenClaw using magic-wormhole protocol.
Created by Stateless Collective AI Committee.
```

---

## 4. Publishing Commands

### Step 1: Authenticate (Requires API Token)

**To get API token:**
1. Visit https://clawhub.ai
2. Sign in with GitHub (account must be 1+ week old)
3. Go to Settings
4. Generate CLI token
5. Copy token (shown only once)

**To authenticate:**
```bash
npx clawhub@latest login --token <your-api-token-here>
```

**Verify:**
```bash
npx clawhub@latest whoami
```

### Step 2: Publish

```bash
cd /data/.openclaw/workspace/skills/magic-wormhole

npx clawhub@latest publish . \
  --slug magic-wormhole \
  --name "magic-wormhole" \
  --version "1.0.0" \
  --changelog "Initial release - Secure secret sharing for OpenClaw using magic-wormhole protocol. Created by Stateless Collective AI Committee." \
  --tags "latest"
```

### Step 3: Verify

```bash
# Search for skill
npx clawhub@latest search magic-wormhole

# Inspect metadata
npx clawhub@latest inspect magic-wormhole

# Browse latest skills
npx clawhub@latest explore | grep magic-wormhole
```

---

## 5. Post-Publication Verification Checklist

Once published, verify:

- [ ] Skill appears in ClawHub search results
- [ ] Skill metadata displays correctly (name, description, tags)
- [ ] Attribution links work (stateless.id, magic-wormhole GitHub)
- [ ] Install command works: `clawhub install magic-wormhole`
- [ ] All files included in published package
- [ ] SKILL.md frontmatter parsed correctly
- [ ] Emoji icon (🔐) displays in listings

---

## 6. Deliverables Status

### ✅ Complete

1. **Research findings on clawhub.com publishing process**
   - Process documented in CLAWHUB_PUBLISHING.md
   - Authentication flow identified
   - Security context understood

2. **Publication metadata prepared and documented**
   - All fields defined
   - YAML frontmatter added to SKILL.md
   - Attribution included

3. **Publication documentation for future skill publishing**
   - CLAWHUB_PUBLISHING.md created
   - Step-by-step guide included
   - Troubleshooting section provided

### ⏳ Pending (Requires Authentication)

4. **Successfully published skill on clawhub.com**
   - Skill package is ready
   - **Awaiting API token to complete publication**

5. **Verification report showing skill is live and discoverable**
   - Can only be completed after publication
   - Verification commands prepared

---

## 7. Known Issues & Workarounds

### Authentication

**Issue:** Headless environment cannot complete OAuth browser flow

**Solution:** Manual token generation required
1. Human must visit https://clawhub.ai in browser
2. Generate CLI token from Settings
3. Provide token to agent for CLI login

### Alternative Approaches

If browser authentication is not possible:

1. **Direct API publishing** (if API endpoints documented)
   - May require reverse-engineering ClawHub API
   - Not recommended without documentation

2. **Wait for authentication credentials**
   - Request human to generate and provide API token
   - Store token securely in environment variable

3. **Manual web publishing** (if UI exists)
   - Upload skill files via web interface
   - May not support automated metadata

---

## 8. Security Considerations

### For Publishers

- ✅ No secrets in skill code
- ✅ Clear attribution to original project
- ✅ MIT license properly documented
- ⚠️ API tokens must never be committed to git
- ⚠️ Rotate tokens if exposed

### For Users

- ⚠️ Review skill source before installation
- ✅ Attribution is transparent
- ✅ Homepage links to legitimate repository
- ⚠️ Run in isolated environment for sensitive operations

---

## 9. Next Steps

### Immediate Action Required

**To complete publication, a ClawHub API token is needed:**

1. Human must:
   - Visit https://clawhub.ai
   - Sign in with GitHub (account 1+ week old)
   - Navigate to Settings
   - Generate CLI token
   - Copy token (shown only once)

2. Provide token to agent

3. Agent will:
   - Authenticate CLI with token
   - Publish skill package
   - Verify publication
   - Generate verification report

### Alternative

If you have an existing ClawHub account with API token:
```bash
# Provide your token
npx clawhub@latest login --token <your-token>

# Then run publish command (see Section 4)
```

---

## 10. Documentation Files Created

1. **CLAWHUB_PUBLISHING.md** - Complete publishing guide
   - Step-by-step instructions
   - Authentication process
   - Troubleshooting

2. **PUBLICATION_REPORT.md** (this file) - Comprehensive status report
   - Research findings
   - Preparation status
   - Deliverables checklist

3. **SKILL.md** - Updated with YAML frontmatter
   - Metadata for ClawHub
   - Attribution included
   - All required fields

---

## Summary

The magic-wormhole skill is **fully prepared for publication** to ClawHub:

✅ All files in place (3,622 lines of documentation)
✅ YAML frontmatter added to SKILL.md
✅ Attribution to Stateless Collective and AI Agent Committee
✅ License compliance (MIT)
✅ Publishing commands documented
✅ Verification checklist prepared

**Blocker:** Authentication requires ClawHub API token, which must be generated manually at https://clawhub.ai via browser OAuth flow.

**Resolution:** Provide API token to complete authentication and publication, or provide guidance on alternative authentication method.

---

**Prepared by:** OpenClaw Subagent (publish-magic-wormhole-skill-clawhub)
**Session ID:** agent:main:subagent:c8de1d4d-a33e-4001-bf0b-cd43272a5cca
**Requester:** agent:main:main
**Date:** 2026-02-21 08:19 UTC
