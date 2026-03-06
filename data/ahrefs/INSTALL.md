# Installation Guide

## Quick Start

### 1. Get Your Ahrefs API Token

1. Log in to your [Ahrefs account](https://ahrefs.com)
2. Navigate to [Account Settings → API](https://ahrefs.com/api)
3. Copy your API token

### 2. Install the Skill

**Option A: Via OpenClaw CLI**
```bash
openclaw skills install ahrefs
```

**Option B: Via ClawHub**
```bash
openclaw skills install https://clawhub.com/skills/ahrefs
```

**Option C: Manual Installation**
```bash
# Clone to your workspace
cd ~/.openclaw/workspace/skills
git clone <repo-url> ahrefs
```

### 3. Configure Credentials

Add your API credentials to `~/.openclaw/workspace/.env`:

```bash
# Linux/Mac
echo "AHREFS_API_TOKEN=your_token_here" >> ~/.openclaw/workspace/.env
echo "AHREFS_API_PLAN=enterprise" >> ~/.openclaw/workspace/.env

# Windows (PowerShell)
Add-Content -Path "$env:USERPROFILE\.openclaw\workspace\.env" -Value "AHREFS_API_TOKEN=your_token_here"
Add-Content -Path "$env:USERPROFILE\.openclaw\workspace\.env" -Value "AHREFS_API_PLAN=enterprise"
```

**Replace `your_token_here` with your actual API token**

**Set your plan tier:**
- `lite` - Basic plan
- `standard` - Standard plan
- `advanced` - Advanced plan
- `enterprise` - Enterprise plan

### 4. Verify Installation

```bash
# Check config
grep AHREFS ~/.openclaw/workspace/.env

# Test the skill
openclaw agent --message "Get domain rating for ahrefs.com"
```

## Plan Configuration

### Why Specify Your Plan?

Different Ahrefs API plans have different capabilities:

| Feature | Lite | Standard | Advanced | Enterprise |
|---------|------|----------|----------|------------|
| Basic metrics | ✓ | ✓ | ✓ | ✓ |
| Keyword lists | Limited | ✓ | ✓ | ✓ |
| Position filtering | ✗ | ✗ | ✓ | ✓ |
| Geographic filtering | ✗ | ✗ | ✓ | ✓ |
| Large datasets (5000+) | ✗ | Limited | ✓ | ✓ |
| Rate limits | Low | Medium | High | Very High |

Specifying your plan helps OpenClaw:
- Use the correct API endpoints
- Provide appropriate error messages
- Optimize queries for your tier
- Avoid unsupported features

### How to Check Your Plan

1. Visit [Ahrefs Pricing](https://ahrefs.com/pricing)
2. Check your current subscription in your account settings
3. Verify API access is included (some plans require API add-on)

## Troubleshooting

### Token Not Working

```bash
# Verify token is set correctly
grep AHREFS_API_TOKEN ~/.openclaw/workspace/.env

# Test manually
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "https://api.ahrefs.com/v3/site-explorer/metrics?date=$(date +%Y-%m-%d)&target=ahrefs.com"
```

### Plan Features Not Working

If advanced features fail:
1. Verify your plan tier in `.env` matches your actual subscription
2. Check if your plan includes API access (some require add-on)
3. Review available features in README.md

### Permission Errors

Ensure `.env` file is readable:
```bash
chmod 600 ~/.openclaw/workspace/.env
```

## Upgrading

To update to a newer version:

```bash
# If installed via CLI/ClawHub
openclaw skills update ahrefs

# If cloned manually
cd ~/.openclaw/workspace/skills/ahrefs
git pull origin main
```

## Uninstallation

```bash
# Remove the skill
openclaw skills remove ahrefs

# Remove credentials (optional)
# Edit ~/.openclaw/workspace/.env and remove AHREFS_* lines
```

## Next Steps

- Read [SKILL.md](SKILL.md) for usage examples
- Check [references/api-endpoints.md](references/api-endpoints.md) for API details
- Review [CHANGELOG.md](CHANGELOG.md) for version history
- Try the example scripts in `scripts/`

## Support

- OpenClaw Docs: https://docs.openclaw.ai
- OpenClaw Discord: https://discord.gg/clawd
- Ahrefs API Docs: https://ahrefs.com/api/documentation
