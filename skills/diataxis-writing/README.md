# Diataxis Writing Skill

A comprehensive skill for creating high-quality documentation using the Diataxis framework.

## Overview

This skill provides complete guidance for creating documentation based on the [Diataxis framework](https://diataxis.fr), including:

- **Four documentation types**: Tutorial, How-to Guide, Reference, Explanation
- **Decision tools**: Diataxis Compass for type selection
- **Templates**: 8 scenario-based templates
- **Checklists**: Quality checklists for each type
- **Diagnosis tools**: Automatic document type detection

## Installation

### For OpenClaw Users

Copy this skill to your workspace:

```bash
cp -r diataxis-writing /root/.openclaw/workspace/skills/
```

### Requirements

- Python 3.8+
- Node.js 18+ (for MCPorter integration)

## Usage

The skill automatically triggers when you mention:

- Documentation creation or writing tasks
- Diataxis framework
- Document type selection
- Troubleshooting records
- Experience summaries
- Learning notes
- Best practices
- Technical sharing

### Example Triggers

- "Help me write a tutorial"
- "What type of documentation should this be?"
- "Create a how-to guide for..."
- "Check my documentation structure"

## Project Structure

```
diataxis-writing/
├── SKILL.md              # Core skill guide
├── CHANGELOG.md          # Version history
├── .gitignore           # Git ignore rules
│
├── checklist/           # Quality checklists (4 files)
├── references/          # Theoretical references (7 files)
├── templates/           # Documentation templates (8 files)
└── scripts/             # Helper scripts (2 files)
```

## Features

### 1. Type Diagnosis

Automatically identifies the appropriate documentation type using the Diataxis Compass.

### 2. Templates

8 scenario-based templates:
- Tutorial
- How-to Guide
- Reference
- Explanation
- Troubleshooting
- Best Practices
- Learning Notes
- Exploratory Sharing

### 3. Checklists

Quality checklists for each documentation type to ensure consistency and completeness.

### 4. Output Management

Support for multiple output methods:
- Chat response
- Feishu documents (via MCP)
- Local Markdown files
- GitHub repositories

## Development

### Version History

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

### Contributing

This skill follows the [Diataxis framework](https://diataxis.fr) strictly. Any contributions should:

1. Respect the official Diataxis terminology
2. Maintain the four-type structure
3. Include proper citations to diataxis.fr

## License

This skill is based on the official Diataxis framework from https://diataxis.fr.

## Acknowledgments

- **Diataxis Framework**: [Daniele Procida](https://vurt.eu) and contributors
- **Official Documentation**: https://diataxis.fr
- **Skill Creator Pattern**: Based on Anthropic's skill-creator guidelines

## Resources

- [Diataxis Official Documentation](https://diataxis.fr)
- [Diataxis GitHub Repository](https://github.com/evildmp/diataxis-documentation-framework)
- [OpenClaw Documentation](https://docs.openclaw.ai)

---

**Version**: 1.2.1  
**Last Updated**: 2026-02-25  
**Maintainer**: Zhua Zhua
