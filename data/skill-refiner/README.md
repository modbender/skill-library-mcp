# skill-refiner

Audit and fix [OpenClaw](https://github.com/openclaw/openclaw) agent skills for [skill-creator](https://github.com/openclaw/openclaw/tree/main/skills/skill-creator) compliance.

[中文文档](./README.zh.md)

## Why?

OpenClaw skills need to follow specific conventions to be properly discovered and triggered. Common issues include:

- Missing or malformed YAML frontmatter
- Extra frontmatter fields (only `name` and `description` allowed)
- Extraneous files (README.md, CHANGELOG.md in skill directories)
- Weak descriptions that don't specify trigger conditions

This tool finds all skills in your workspace and reports compliance issues.

## Quick Start

```bash
# Scan your OpenClaw workspace
npx skill-refiner

# Scan a specific directory
npx skill-refiner /path/to/workspace
```

## Installation

### As an OpenClaw Skill

```bash
clawhub install skill-refiner
```

Then ask your agent: "audit my skills" or "check skill compliance"

### Global CLI

```bash
npm install -g skill-refiner
skill-refiner ~/.openclaw/workspace
```

## What It Checks

| Check | Severity | Description |
|-------|----------|-------------|
| SKILL.md exists | 🔴 Issue | Every skill needs a SKILL.md |
| YAML frontmatter | 🔴 Issue | Must start with `---` block |
| Required fields | 🔴 Issue | `name` and `description` required |
| Extra fields | 🔴 Issue | Only `name` + `description` allowed |
| Extraneous files | 🔴 Issue | No README.md, CHANGELOG.md, etc. |
| Naming convention | 🔴 Issue | lowercase-hyphen-case, ≤64 chars |
| Trigger conditions | 🟡 Warning | Description should include "Use when..." |
| SKILL.md length | 🟡 Warning | Recommended max 500 lines |
| Unlinked references | 🟡 Warning | Files in references/ should be linked |

## Output Example

```
🔍 skill-refiner — scanning: /Users/me/.openclaw/workspace

✅ markdown-converter
✅ weather
❌ my-broken-skill
  ✗  Frontmatter has extra fields: metadata, author
  ✗  Extraneous file: README.md
⚠️ another-skill
  ⚠️  Description doesn't clearly state trigger conditions

─────────────────────────────────
Total: 4  ✅ 2  ❌ 1  ⚠️ 1
```

## Programmatic Usage

```bash
# Find all skills
bash scripts/find_skills.sh /path/to/workspace

# Audit a single skill (returns JSON)
python3 scripts/audit_skill.py /path/to/skill-dir
```

## License

MIT
