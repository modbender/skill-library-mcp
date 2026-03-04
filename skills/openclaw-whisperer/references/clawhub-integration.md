# ClawHub Integration

Complete guide to using ClawHub - the OpenClaw skill registry with 5,700+ skills.

## Overview

ClawHub is the central registry for OpenClaw skills. It provides:
- **5,700+ skills** across categories (AI, automation, utilities, integrations)
- **Skill discovery** via search and recommendations
- **Version management** and automatic updates
- **Publishing platform** for custom skills
- **Quality ratings** and community reviews

## Basic Commands

### Search Skills

```bash
# Search by keyword
openclaw skills search "image generation"
openclaw skills search "pdf"
openclaw skills search "automation"

# Search by category
openclaw skills search --category ai
openclaw skills search --category utilities

# Filter by rating
openclaw skills search "image" --min-rating 4.0

# Show details
openclaw skills search "image" --detailed
```

**Example Output:**
```
Found 15 skills matching "image":

1. image-generator-pro (⭐ 4.8, 2.3K installs)
   Generate images with DALL-E, Stable Diffusion, Midjourney
   openclaw skills install image-generator-pro

2. image-optimizer (⭐ 4.5, 1.5K installs)
   Compress and optimize images (PNG, JPG, WebP)
   openclaw skills install image-optimizer

3. image-to-text (⭐ 4.3, 890 installs)
   OCR and text extraction from images
   openclaw skills install image-to-text
```

### Install Skills

```bash
# Install by name
openclaw skills install image-generator-pro

# Install specific version
openclaw skills install image-generator-pro@2.1.0

# Install multiple skills
openclaw skills install image-gen pdf-tools automation-helper

# Install from URL (private/custom)
openclaw skills install https://github.com/user/custom-skill.git

# Install with dependencies
openclaw skills install skill-name --with-deps
```

### List Installed Skills

```bash
# List all installed
openclaw skills list

# Show details
openclaw skills list --detailed

# Filter by category
openclaw skills list --category ai

# Show outdated skills
openclaw skills list --outdated
```

**Example Output:**
```
Installed Skills (12):

✓ image-generator-pro (v2.1.0)  - AI
✓ pdf-tools (v1.5.2)            - Utilities
✓ automation-helper (v3.0.1)    - Automation
⚠ web-scraper (v1.2.0 → v1.3.0) - Utilities [UPDATE AVAILABLE]
✗ broken-skill (v0.5.0)         - Error: missing dependency
```

### Update Skills

```bash
# Update all skills
openclaw skills update

# Update specific skill
openclaw skills update image-generator-pro

# Check for updates only
openclaw skills check-updates

# Update with changelog
openclaw skills update --show-changelog
```

### Uninstall Skills

```bash
# Uninstall skill
openclaw skills uninstall image-generator-pro

# Uninstall with cleanup
openclaw skills uninstall skill-name --clean

# Uninstall multiple
openclaw skills uninstall skill1 skill2 skill3
```

## Skill Information

### View Skill Details

```bash
# Show full details
openclaw skills info image-generator-pro

# Show README
openclaw skills readme image-generator-pro

# Show changelog
openclaw skills changelog image-generator-pro

# Show dependencies
openclaw skills deps image-generator-pro
```

**Example Output:**
```
Skill: image-generator-pro
Version: 2.1.0
Author: ClawHub Community
Rating: ⭐⭐⭐⭐⭐ (4.8/5.0, 2,340 installs)
Category: AI
License: MIT

Description:
Generate images using DALL-E 3, Stable Diffusion XL, or Midjourney.
Supports batch generation, style presets, and custom parameters.

Features:
- Multiple AI providers (DALL-E, SD, Midjourney)
- Style presets (realistic, anime, sketch, etc.)
- Batch generation
- Image editing and variations
- Custom resolution up to 4K

Requirements:
- OpenAI API key (for DALL-E)
- Stability API key (for SD)
- Midjourney API key (for MJ)

Installation:
openclaw skills install image-generator-pro
```

### Check Skill Health

```bash
# Validate installed skills
openclaw skills check

# Validate specific skill
openclaw skills check image-generator-pro

# Fix broken skills
openclaw skills doctor --fix
```

## Skill Discovery

### Browse by Category

```bash
# List categories
openclaw skills categories

# Browse category
openclaw skills browse --category ai
openclaw skills browse --category automation
openclaw skills browse --category utilities
openclaw skills browse --category integrations
```

**Categories:**
- **AI**: Language models, image generation, embeddings
- **Automation**: Workflows, schedulers, triggers
- **Utilities**: File tools, converters, formatters
- **Integrations**: Third-party APIs, webhooks
- **Communication**: Email, SMS, notifications
- **Data**: Databases, analytics, visualization
- **Security**: Encryption, auth, scanning
- **Developer**: Code tools, testing, deployment

### Popular Skills

```bash
# Most popular
openclaw skills popular --top 20

# Trending this week
openclaw skills trending

# Recently updated
openclaw skills recent
```

### Recommended Skills

```bash
# Auto-detect and recommend
openclaw skills recommend

# Recommend for specific channel
openclaw skills recommend --channel whatsapp

# Recommend for use case
openclaw skills recommend --use-case "customer support"
```

**Example Recommendations:**
```
Recommended Skills for WhatsApp:

Essential:
- whatsapp-media-handler - Handle images, videos, docs
- message-formatter - Rich formatting for messages
- qr-code-generator - Generate QR codes

Suggested:
- auto-responder - Automated responses
- translation-tool - Multi-language support
- analytics-tracker - Message analytics

Install all: openclaw skills install whatsapp-media-handler message-formatter qr-code-generator
```

## Publishing Skills

### Create Skill

```bash
# Generate skill template
openclaw skills create my-awesome-skill

# Interactive wizard
openclaw skills create --interactive
```

**Template Structure:**
```
my-awesome-skill/
├── SKILL.md           # Manifest
├── README.md          # Documentation
├── script.py          # Main script
├── config.yaml        # Configuration
├── requirements.txt   # Dependencies
└── tests/            # Tests
```

### Validate Skill

```bash
# Validate before publishing
openclaw skills validate my-awesome-skill/

# Test locally
openclaw skills test-local my-awesome-skill/
```

### Publish to ClawHub

```bash
# Login to ClawHub
openclaw skills login

# Publish skill
openclaw skills publish my-awesome-skill/

# Publish with version
openclaw skills publish my-awesome-skill/ --version 1.0.0

# Publish with changelog
openclaw skills publish my-awesome-skill/ --changelog "Initial release"
```

### Update Published Skill

```bash
# Publish update
openclaw skills publish my-awesome-skill/ --version 1.1.0

# Deprecate old version
openclaw skills deprecate my-awesome-skill@1.0.0

# Unpublish (use with caution)
openclaw skills unpublish my-awesome-skill
```

## Skill Management

### Sync with ClawHub

```bash
# Sync skill catalog
openclaw skills sync

# Force refresh cache
openclaw skills sync --force

# Sync specific category
openclaw skills sync --category ai
```

### Skill Configuration

```bash
# Configure skill
openclaw skills config image-gen set provider "dall-e"

# View skill config
openclaw skills config image-gen show

# Reset skill config
openclaw skills config image-gen reset
```

### Skill Execution

```bash
# Run skill manually
openclaw skills run image-gen --prompt "a cat"

# Run with parameters
openclaw skills run pdf-tools --input doc.pdf --output out.pdf

# Run in background
openclaw skills run long-task --async
```

## Advanced Usage

### Private Skill Registry

```bash
# Add private registry
openclaw skills registry add my-company https://skills.company.com

# Set default registry
openclaw skills registry use my-company

# Install from specific registry
openclaw skills install skill-name --registry my-company

# List registries
openclaw skills registry list
```

### Skill Dependencies

```bash
# Show dependency tree
openclaw skills deps image-gen --tree

# Install missing dependencies
openclaw skills install-deps image-gen

# Check for conflicts
openclaw skills check-conflicts
```

### Skill Versioning

```bash
# List versions
openclaw skills versions image-gen

# Install specific version
openclaw skills install image-gen@2.0.0

# Rollback to previous
openclaw skills rollback image-gen

# Pin version (prevent updates)
openclaw skills pin image-gen@2.0.0
```

## ClawHub API Integration

### Search API

```bash
# Search with filters
openclaw skills search "image" \
  --category ai \
  --min-rating 4.0 \
  --min-installs 100 \
  --sort-by popularity
```

### Automation

```bash
# Auto-install recommended skills
openclaw skills recommend --auto-install

# Schedule updates
openclaw skills update --schedule "0 2 * * *"  # 2 AM daily

# Backup skill list
openclaw skills list --json > skills-backup.json

# Restore from backup
openclaw skills install-from-list skills-backup.json
```

## Skill Quality Guidelines

### Rating System
- ⭐⭐⭐⭐⭐ (5.0) - Exceptional quality, well-maintained
- ⭐⭐⭐⭐ (4.0) - Good quality, recommended
- ⭐⭐⭐ (3.0) - Average, usable with minor issues
- ⭐⭐ (2.0) - Below average, use with caution
- ⭐ (1.0) - Poor quality, not recommended

### Quality Indicators
```bash
# Check skill quality
openclaw skills quality-check image-gen

Quality Report:
✓ Active maintenance (updated 2 weeks ago)
✓ High rating (4.8/5.0)
✓ Well documented
✓ Has tests
✓ Good community support (50+ reviews)
⚠ Large dependency tree (15 deps)
✗ No CI/CD configured
```

## Troubleshooting

### Installation Issues

```bash
# Clear cache
openclaw skills cache clear

# Reinstall skill
openclaw skills uninstall skill-name
openclaw skills install skill-name

# Install with verbose output
openclaw skills install skill-name --verbose
```

### Broken Skills

```bash
# Diagnose issues
openclaw skills doctor

# Fix broken dependencies
openclaw skills doctor --fix-deps

# Rebuild skill
openclaw skills rebuild skill-name
```

### Network Issues

```bash
# Use mirror registry
openclaw skills registry use mirror

# Offline mode (use cache)
openclaw skills list --offline

# Export/import for airgapped systems
openclaw skills export skill-name > skill.tar.gz
openclaw skills import skill.tar.gz
```

## Best Practices

1. **Regular Updates**: Run `openclaw skills update` weekly
2. **Pin Critical Skills**: Use `openclaw skills pin` for production
3. **Review Ratings**: Check ratings before installing
4. **Read Documentation**: Use `openclaw skills readme` before use
5. **Test Before Production**: Use `openclaw skills test-local`
6. **Monitor Dependencies**: Run `openclaw skills check-conflicts` regularly
7. **Backup Skill List**: Export installed skills periodically
8. **Use Recommendations**: Let system recommend relevant skills

## Popular Skills by Category

### AI & Machine Learning
- `image-generator-pro` - Multi-provider image generation
- `text-embeddings` - Generate text embeddings
- `sentiment-analyzer` - Sentiment analysis
- `translation-ai` - Neural machine translation

### Automation
- `workflow-builder` - Visual workflow automation
- `scheduler-pro` - Advanced task scheduling
- `auto-responder` - Smart auto-responses
- `batch-processor` - Batch operations

### Utilities
- `pdf-toolkit` - PDF manipulation
- `image-optimizer` - Image compression
- `file-converter` - Format conversion
- `qr-code-tools` - QR code generation/scanning

### Integrations
- `google-workspace` - Google Workspace integration
- `slack-connector` - Slack integration
- `github-integration` - GitHub automation
- `zapier-bridge` - Zapier compatibility

## Related Files

- [Error Catalog](error-catalog.md) - Skill-related errors
- [Diagnostic Commands](diagnostic-commands.md) - Skill commands
- [Auto-Fix Capabilities](auto-fix-capabilities.md) - Skill auto-fixes
