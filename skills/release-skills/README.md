# Release Skills

Universal release workflow with auto-detection, multi-language changelogs, semantic versioning, and git tagging. Supports Node.js, Python, Rust, Claude Plugin, and generic projects.

## What's Inside

- Auto-detection of project type and version files
- Change analysis with conventional commit categorization
- Semantic version determination (major/minor/patch)
- Multi-language changelog generation (English, Chinese, Japanese, and more)
- Monorepo module grouping
- User confirmation flow before pushing
- Git tagging and release creation
- Configuration via `.releaserc.yml`
- Scripts for release preparation, notes generation, and roadmap changelogs

## When to Use

- User wants to create a release or bump a version
- Updating changelogs before a deploy
- Preparing for deployment with proper tagging
- Triggered by: "release", "new version", "bump version", "update version", "push", "create release", "prepare release", "tag version"

## Installation

```bash
npx add https://github.com/wpank/ai/tree/main/skills/tools/release-skills
```

### Manual Installation

#### Cursor (per-project)

From your project root:

```bash
mkdir -p .cursor/skills
cp -r ~/.ai-skills/skills/tools/release-skills .cursor/skills/release-skills
```

#### Cursor (global)

```bash
mkdir -p ~/.cursor/skills
cp -r ~/.ai-skills/skills/tools/release-skills ~/.cursor/skills/release-skills
```

#### Claude Code (per-project)

From your project root:

```bash
mkdir -p .claude/skills
cp -r ~/.ai-skills/skills/tools/release-skills .claude/skills/release-skills
```

#### Claude Code (global)

```bash
mkdir -p ~/.claude/skills
cp -r ~/.ai-skills/skills/tools/release-skills ~/.claude/skills/release-skills
```

---

Part of the [Tools](..) skill category.
