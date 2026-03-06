# AGENTS.md

Guidelines for AI agents working in this repository.

## Repository Overview

This repository contains an **Agent Skill** for AI agents following the [Agent Skills specification](https://agentskills.io/specification.md).

- **Name**: Helpcenter Skill
- **GitHub**: [microdotcompany/helpcenter-skill](https://github.com/microdotcompany/helpcenter-skill)
- **Creator**: Microdot Company
- **License**: MIT

## Repository Structure

```
helpcenter-skill/
├── .claude-plugin/
│   └── marketplace.json   # Claude Code plugin manifest
├── SKILL.md               # Skill definition and API reference
├── AGENTS.md
├── LICENSE
└── README.md
```

## Agent Skills Specification

Skills follow the [Agent Skills spec](https://agentskills.io/specification.md).

### Required Frontmatter

```yaml
---
name: skill-name
description: What this skill does and when to use it. Include trigger phrases.
metadata:
  version: 1.0.0
---
```

### Frontmatter Field Constraints

| Field         | Required | Constraints                                                     |
|---------------|----------|-----------------------------------------------------------------|
| `name`        | Yes      | 1-64 chars, lowercase `a-z`, numbers, hyphens. Must match dir. |
| `description` | Yes      | 1-1024 chars. Describe what it does and when to use it.         |
| `metadata`    | No       | Key-value pairs (author, version, etc.)                         |

## Writing Style Guidelines

- Keep `SKILL.md` under 500 lines (move details to `references/` if needed)
- Use H2 (`##`) for main sections, H3 (`###`) for subsections
- Direct and instructional tone
- Bold (`**text**`) for key terms
- Code blocks for examples and templates
- Tables for reference data

## Git Workflow

### Commit Messages

- `feat: add new endpoint support`
- `fix: improve error handling guidance`
- `docs: update README`
