# Publishing god-mode to ClawdHub

## Prerequisites

✅ You already have these:
- [x] SKILL.md with frontmatter metadata
- [x] Scripts in `scripts/` directory
- [x] README.md with installation instructions
- [x] LICENSE file (MIT)
- [x] Working install from GitHub

## Publishing to ClawdHub

### 1. Create GitHub Release

```bash
# Tag the release
git tag -a v0.1.0 -m "Release v0.1.0 - Initial release"
git push origin v0.1.0

# Create release on GitHub
gh release create v0.1.0 \
  --title "v0.1.0 - Multi-project oversight + agent coaching" \
  --notes "See CHANGELOG.md for details"
```

### 2. Submit to ClawHub

**Via Web:**
1. Go to https://www.clawhub.ai/
2. Click "Submit Skill" or "Publish" (look for contribution/submit option)
3. Enter repository URL: `https://github.com/InfantLab/god-mode-skill`
4. ClawHub will validate SKILL.md metadata
5. Approve and publish

**Note:** Site may show security warnings - this is a known issue with the platform.

**If submission UI isn't available:**
- Join Discord: https://discord.com/invite/clawd
- Post in #skills with your GitHub URL
- OpenClaw team can manually add it

### 3. Announce

**Discord:**
Post in #skills channel:
```
🎉 New Skill: god-mode v0.1.0

Multi-project oversight and agent coaching for developers.

✨ Features:
- Status overview (GitHub + Azure DevOps)
- LLM-powered agent.md analysis
- Monthly activity reviews
- Conversational interface

📦 Install: npx clawdhub install god-mode
🔗 GitHub: https://github.com/InfantLab/god-mode-skill
📖 Docs: See SKILL.md

Feedback welcome! 🙏
```

## Alternative: GitHub-Only Distribution

Users can install directly from GitHub without ClawdHub:

### Installation Instructions for Users

Add to README.md:

```bash
# Option 1: Clone and symlink (recommended for development)
git clone https://github.com/InfantLab/god-mode-skill
cd god-mode-skill
chmod +x scripts/god
ln -s $(pwd)/scripts/god ~/.local/bin/god

# Option 2: Direct install
curl -fsSL https://raw.githubusercontent.com/InfantLab/god-mode-skill/main/install.sh | bash
```

## Create Install Script

```bash
cat > install.sh << 'EOF'
#!/bin/bash
# god-mode installation script

set -e

INSTALL_DIR="${HOME}/.local/share/god-mode"
BIN_DIR="${HOME}/.local/bin"

echo "Installing god-mode..."

# Clone or update
if [ -d "$INSTALL_DIR" ]; then
    echo "Updating existing installation..."
    cd "$INSTALL_DIR"
    git pull
else
    echo "Cloning repository..."
    git clone https://github.com/InfantLab/god-mode-skill "$INSTALL_DIR"
fi

# Create bin directory if needed
mkdir -p "$BIN_DIR"

# Symlink executable
ln -sf "$INSTALL_DIR/scripts/god" "$BIN_DIR/god"

# Make executable
chmod +x "$INSTALL_DIR/scripts/god"

echo "✅ god-mode installed!"
echo ""
echo "Run: god setup"
echo ""

# Check PATH
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo "⚠️  Add to your shell profile:"
    echo "   export PATH=\"\$HOME/.local/bin:\$PATH\""
fi
EOF
chmod +x install.sh
git add install.sh
git commit -m "Add install script for GitHub-only distribution"
git push
```

## Skill Metadata Checklist

Your SKILL.md already has correct frontmatter:

```yaml
---
name: god-mode
description: Developer project oversight via conversation...
metadata: {"openclaw": {"requires": {"bins": ["gh", "sqlite3", "jq"]}}}
user-invocable: true
---
```

✅ This tells OpenClaw:
- Skill name: `god-mode`
- Required binaries: gh, sqlite3, jq
- User can invoke directly (not just internal)

## Verification

After publishing, users should be able to:

```bash
# Via ClawdHub (once published)
npx clawdhub install god-mode

# Via GitHub (works now)
curl -fsSL https://raw.githubusercontent.com/InfantLab/god-mode-skill/main/install.sh | bash

# Verify installation
god --version  # Should show: god-mode v0.1.0
god status     # Should work
```

## Post-Release

1. Monitor GitHub Issues for bug reports
2. Update ClawdHub listing if needed
3. Respond to Discord feedback
4. Plan v0.2.0 based on community requests

## Version Updates

For future releases:

```bash
# Update version
vim scripts/god  # Change VERSION="0.1.0" to "0.2.0"

# Update changelog
vim CHANGELOG.md  # Add v0.2.0 section

# Tag and release
git commit -am "Release v0.2.0"
git tag -a v0.2.0 -m "Release v0.2.0"
git push origin v0.2.0
gh release create v0.2.0 --notes "See CHANGELOG.md"

# Update ClawdHub
npx clawdhub update god-mode
```
