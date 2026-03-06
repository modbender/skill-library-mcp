# Submitting god-mode to ClawHub

## Quick Start

**Repository:** https://github.com/InfantLab/god-mode-skill  
**ClawHub:** https://www.clawhub.ai/  
**Version:** v0.1.0  

## Submission Methods

### Method 1: ClawHub Web Interface (Preferred)

1. Visit https://www.clawhub.ai/
2. Look for "Submit Skill" / "Contribute" / "Add Skill" button
3. Provide:
   - Repository URL: `https://github.com/InfantLab/god-mode-skill`
   - Branch/Tag: `v0.1.0` or `main`
   - Skill name: `god-mode`

**Note:** Site may show browser security warnings - this is a known issue with the platform. Proceed anyway or use Method 2.

### Method 2: Discord Manual Submission

If the web interface isn't clear or you prefer human review:

1. Join OpenClaw Discord: https://discord.com/invite/clawd
2. Post in **#skills** channel:

```
🔭 New Skill Submission: god-mode v0.1.0

Multi-project oversight and AI agent coaching for developers.

📦 Repository: https://github.com/InfantLab/god-mode-skill
🏷️ Version: v0.1.0
📖 Docs: SKILL.md included with proper frontmatter

✨ Features:
- Status overview (GitHub + Azure DevOps)
- LLM-powered AGENTS.md analysis
- Monthly activity reviews
- Conversational OpenClaw interface

Ready for review! Let me know if you need any changes. 🙏
```

## What ClawHub Needs

Your skill already has everything required:

✅ **SKILL.md with frontmatter:**
```yaml
---
name: god-mode
description: Developer project oversight via conversation...
metadata: {"openclaw": {"requires": {"bins": ["gh", "sqlite3", "jq"]}}}
user-invocable: true
---
```

✅ **Proper structure:**
- Scripts in `scripts/` directory
- Main entry point: `scripts/god`
- Dependencies declared in metadata

✅ **Documentation:**
- README.md (user-facing)
- SKILL.md (OpenClaw integration)
- CHANGELOG.md (version history)
- LICENSE (MIT)

✅ **GitHub Release:**
- Tagged v0.1.0
- Release notes published

## Validation

ClawHub will automatically check:
- ✅ SKILL.md exists and has valid frontmatter
- ✅ Required binaries (`gh`, `sqlite3`, `jq`) are documented
- ✅ Scripts are executable
- ✅ Repository is public

## After Submission

Once approved, users can install via:

```bash
# Via ClawHub CLI (when available)
npx clawhub install god-mode

# Or via OpenClaw skills command
openclaw skills install god-mode

# Or direct from GitHub (works now)
curl -fsSL https://raw.githubusercontent.com/InfantLab/god-mode-skill/main/install.sh | bash
```

## Troubleshooting

**If submission fails:**
1. Check SKILL.md frontmatter is valid YAML
2. Ensure repository is public
3. Verify scripts/god is executable
4. Ask in Discord #skills for help

**Security Warnings:**
- ClawHub site may show SSL/certificate warnings
- This is a known platform issue
- Your skill code is on GitHub (publicly auditable)
- Safe to proceed with submission

## Updates

For future versions, update ClawHub listing:

```bash
# Create new release
git tag -a v0.2.0 -m "Release v0.2.0"
git push origin v0.2.0
gh release create v0.2.0

# Then either:
# 1. Update via ClawHub web interface
# 2. Post update notice in Discord #skills
```

## Support

- Discord: https://discord.com/invite/clawd (#skills channel)
- GitHub Issues: https://github.com/InfantLab/god-mode-skill/issues
- ClawHub: https://www.clawhub.ai/
