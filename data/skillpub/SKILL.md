---
name: skill-publisher
description: >
  Create, validate, security-scan, and publish skills to ClawHub. Use when asked to
  "make a skill", "publish a skill", "create a new skill", "scaffold a skill",
  "package this as a skill", or any request to build and distribute agent capabilities.
---

# Skill Publisher

Build and publish skills to ClawHub in one flow.

## Quick Start

### 1. Scaffold a new skill

```bash
bash {baseDir}/scripts/scaffold.sh <skill-name> [--dir <output-dir>]
```

Creates a new skill folder with SKILL.md template and scripts/ directory.
Default output: `./skills/<skill-name>`

### 2. Fill in the skill

Edit the generated SKILL.md:
- Set `name` and `description` in frontmatter (description is critical for triggering)
- Write clear instructions in the body
- Add scripts/ for executable code, references/ for docs, assets/ for templates

### 3. Validate

```bash
bash {baseDir}/scripts/validate.sh <skill-folder>
```

Checks:
- Required files exist (SKILL.md)
- Frontmatter has `name` and `description`
- Naming conventions (lowercase, hyphens)
- No forbidden files (README.md, CHANGELOG.md, etc.)

### 4. Security scan

```bash
bash {baseDir}/scripts/security-scan.sh <skill-folder>
```

Scans for red flags:
- Remote code execution / eval patterns
- Data exfiltration (curl to unknown hosts)
- Environment variable harvesting
- Prompt injection in markdown files
- Suspicious file permissions

### 5. Publish

```bash
bash {baseDir}/scripts/publish.sh <skill-folder> --slug <name> --version <x.y.z>
```

Pushes to ClawHub. Requires `clawhub login` first.

## One-liner (for simple skills)

```bash
bash {baseDir}/scripts/scaffold.sh my-skill && \
  # edit skills/my-skill/SKILL.md ... && \
  bash {baseDir}/scripts/validate.sh skills/my-skill && \
  bash {baseDir}/scripts/security-scan.sh skills/my-skill && \
  bash {baseDir}/scripts/publish.sh skills/my-skill --slug my-skill --version 1.0.0
```

## Skill Anatomy Reminder

```
my-skill/
├── SKILL.md          ← Required. Frontmatter (name, description) + instructions.
├── scripts/          ← Optional. Executable code (bash, python, etc.)
├── references/       ← Optional. Docs loaded on-demand into context.
└── assets/           ← Optional. Templates, images, files used in output.
```

**Key principles:**
- Be concise. Context window is shared real estate.
- Description in frontmatter is the trigger — make it comprehensive.
- Progressive disclosure: SKILL.md body only loads when triggered.
- Scripts > inline code for deterministic, repeated operations.
