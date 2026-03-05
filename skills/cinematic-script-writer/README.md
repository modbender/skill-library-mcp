# Cinematic Script Writer Skill

[![CI](https://github.com/yourusername/openclawskills/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/openclawskills/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue.svg)](https://www.typescriptlang.org/)

> Professional cinematic script generation for AI video creation with character consistency, comprehensive cinematography knowledge, and Google Drive integration.

## Features

| Feature | Description |
|---------|-------------|
| **175+ Cinematography Techniques** | Camera angles, movements, shots, lighting, composition |
| **Character Consistency** | Reference sheets ensuring same appearance across all shots |
| **Voice Consistency** | Speech profiles for consistent dialogue |
| **Environment Consistency** | Era-appropriate architecture, clothing, props |
| **Anachronism Detection** | Validates no modern elements in historical settings |
| **Google Drive Integration** | Auto-save all content to organized folders |
| **YouTube Metadata** | Titles, descriptions, tags for upload |
| **CLI Tool** | `cinematic-script` command for all operations |

## Quick Start

```bash
# Install globally
npm install -g cinematic-script-writer

# Create a story context
cinematic-script create-context --name "My Story" --genre comedy --era "Modern"

# Browse cinematography techniques
cinematic-script list-angles
cinematic-script suggest-lighting --scene-type interior-day --mood comedy
```

See [SKILL.md](SKILL.md) for full CLI documentation.

## Repository Structure

```
openclawskills/
├── SKILL.md                         # Skill definition (ClawHub auto-detects this)
├── bin/
│   └── cinematic-script.ts          # CLI entry point
├── skills/
│   └── cinematic-script-writer/     # Main skill implementation
│       ├── index.ts                 # Main class
│       ├── skill.json               # Tool definitions (55 methods)
│       ├── cinematography-*.ts      # Camera techniques database
│       ├── consistency-*.ts         # Consistency system
│       ├── storage-*.ts             # Storage system
│       └── EXAMPLE-*.md             # Usage examples
├── examples/                        # Reference skill examples
├── skill-template/                  # Template for new skills
├── README.md                        # This file
└── SETUP-GUIDE.md                   # Complete setup guide
```

## Publishing to ClawHub

1. **Push to GitHub** (make repo public):
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/openclawskills.git
   git push -u origin main
   ```

2. **Import to ClawHub**:
   - Go to https://clawhub.ai/import
   - Enter your GitHub URL
   - Click **Detect** - it will find `SKILL.md` automatically
   - Fill in details and click **Publish**

ClawHub auto-updates when you push new commits.

## Development

```bash
# Install dependencies
npm install

# Build
npm run build

# Test
npm test

# Lint
npm run lint
```

## Documentation

- [SKILL.md](SKILL.md) - Full skill definition and CLI reference
- [SETUP-GUIDE.md](SETUP-GUIDE.md) - Complete setup and testing guide
- [skills/cinematic-script-writer/EXAMPLE-KUTIL.md](skills/cinematic-script-writer/EXAMPLE-KUTIL.md) - Complete Kutil example
- [skills/cinematic-script-writer/EXAMPLE-CONSISTENCY.md](skills/cinematic-script-writer/EXAMPLE-CONSISTENCY.md) - Consistency guide
- [skills/cinematic-script-writer/EXAMPLE-STORAGE.md](skills/cinematic-script-writer/EXAMPLE-STORAGE.md) - Storage guide

## Requirements

- Node.js 18+
- TypeScript 5.0+
- OpenClaw Agent with memory permissions

## License

MIT License - see [LICENSE](LICENSE)

---

**Made for OpenClaw**
