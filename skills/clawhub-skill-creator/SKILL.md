---
name: clawhub-skill-creator
description: Create effective skills for clawhub registry. Use when: (1) Creating new skill for publication, (2) Updating existing skill metadata, (3) Optimizing skill structure for AI agents, (4) Validating skill before publish, (5) Understanding clawhub-specific requirements.
---

# Clawhub Skill Creator

Complete guide for creating skills compatible with clawhub registry and optimized for AI agent usage.

## Language Rule

**Skill description must be in English**, unless context requires otherwise (examples, comments, etc. may use other languages when appropriate).

- `description` in frontmatter: English only
- SKILL.md body: English preferred
- Examples, code comments: Any language as needed
- References: Any language as appropriate for domain

## Quick Start

### Create New Skill

```bash
# Run initializer
./scripts/init-skill.sh my-skill

# Or manually create structure
mkdir -p my-skill/{references,scripts,assets}
touch my-skill/SKILL.md my-skill/_meta.json my-skill/LICENSE.txt
```

## Skill Creation Workflow

### Phase 1: Understand Requirements

**Before writing any code, clarify:**

1. **What problem does this skill solve?**
   - Concrete use cases (2-3 examples)
   - Target queries that should trigger skill

2. **Who will use this skill?**
   - AI agents (primary audience for clawhub)
   - Expected context (tools available, environment)

3. **What resources are needed?**
   - References for detailed docs?
   - Assets for templates?
   - Scripts for automation?

**Output:** Clear understanding of skill scope and triggers.

### Phase 2: Plan Structure

**Choose pattern based on complexity:**

| Complexity | Structure | When to Use |
|------------|-----------|-------------|
| Simple | SKILL.md only | <100 lines, single purpose |
| Medium | + references/ | 100-300 lines, some details |
| Complex | + references/ + assets/ | >300 lines, multi-domain |

**Decide on resources:**
- Which references needed? (docs, examples, patterns)
- Which assets needed? (templates, configs)
- Which scripts needed? (validation, packaging)

**Output:** Directory structure and resource list.

### Phase 3: Initialize Structure

```bash
# Create directory
mkdir -p my-skill/{references,scripts,assets}

# Create required files
touch my-skill/SKILL.md
touch my-skill/_meta.json
touch my-skill/LICENSE.txt
```

**Required files for clawhub:**
```
my-skill/
├── SKILL.md              # Instructions and metadata (required)
├── _meta.json            # Registry metadata (required)
├── LICENSE.txt           # License file (required)
├── references/           # Optional: detailed documentation
├── scripts/              # Optional: automation scripts
└── assets/               # Optional: templates, resources
```

### Phase 4: Write SKILL.md

#### Frontmatter (YAML)

```yaml
---
name: skill-name
description: What it does. Use when: (1) trigger-1, (2) trigger-2, (3) trigger-3.
---
```

**Critical rules:**
- `name` must match directory name
- `description` is ONLY trigger mechanism — include all "when to use" here
- `description` must be in **English**
- Only `name` and `description` are required in frontmatter

#### Body Structure

```markdown
# Skill Title

Brief purpose (1-2 sentences).

## Quick Start

**Linux/Mac:**
```bash
command --option
```

**Windows CMD:**
```cmd
command --option
```

**PowerShell:**
```powershell
command --option
```

## When to Use

- Situation 1: What to do
- Situation 2: What to do
- Situation 3: What to do

## Workflow

1. **Step one**: Description
2. **Step two**: Description
3. **Step three**: Description

## Resources

- `references/advanced.md` - For complex cases
- `references/examples.md` - Usage examples
- `assets/template.txt` - Starting template
```

**Writing guidelines:**
- Imperative voice ("Open file", not "You should open file")
- Concrete examples over abstract explanations
- Platform-aware commands
- Navigation to references
- English preferred for body text

### Phase 5: Create _meta.json

```json
{
  "name": "skill-name",
  "version": "1.0.0",
  "description": "Short description for registry listing",
  "requires": {
    "env": ["ENV_VAR_1", "ENV_VAR_2"],
    "credentials": ["credential_name"]
  },
  "tags": ["tag1", "tag2", "latest"]
}
```

**Fields explained:**
- `name`: Must match directory and SKILL.md frontmatter
- `version`: Semver (X.Y.Z), check registry before setting
- `description`: For registry listing, must be in **English**
- `requires.env`: Environment variables needed
- `requires.credentials`: Credentials needed
- `tags`: Include "latest" for discoverability

### Phase 6: Add LICENSE.txt

Choose license (MIT recommended):

```
MIT License

Copyright (c) 2025 [Author]

Permission is hereby granted...
```

### Phase 7: Write References (if needed)

Create files in `references/`:

```markdown
# Reference Title

Detailed documentation here.

## Section

Content...
```

**Guidelines:**
- One topic per file
- <5K words per file
- Link from SKILL.md with clear context
- No deeply nested references
- Language: English preferred, domain-specific allowed

### Phase 8: Validate Locally

```bash
# Check structure
./scripts/validate.sh my-skill

# Or manual checks:
# - SKILL.md exists and has frontmatter
# - _meta.json is valid JSON
# - LICENSE.txt exists
# - No README.md, CHANGELOG.md
# - Line count < 300
# - References linked correctly
```

**Validation checklist:**
- [ ] Directory name matches `name` in frontmatter and _meta.json
- [ ] `description` in English, includes "Use when:" triggers
- [ ] SKILL.md < 300 lines
- [ ] _meta.json valid JSON
- [ ] No extraneous files (README, CHANGELOG)
- [ ] References exist and linked
- [ ] Token estimate < 10K

### Phase 9: Test with Agent

**Trigger test:**
- Does skill activate for intended queries?
- Does description correctly trigger skill?

**Workflow test:**
- Can agent follow steps without clarification?
- Are commands clear and executable?

**Resource test:**
- Are references loaded at appropriate time?
- Is navigation clear?

**Edge case test:**
- How does skill handle errors?
- Are platform differences handled?

### Phase 10: Iterate (if needed)

If tests reveal issues:

1. **Identify problem**
   - Trigger not working? → Fix description
   - Workflow unclear? → Rewrite steps
   - Missing info? → Add reference

2. **Update files**
   - SKILL.md, _meta.json, or references

3. **Re-validate and re-test**
   - Go back to Phase 8

4. **Repeat until satisfied**

**Iterate cycle:** Phase 8 → Phase 9 → Phase 10 (loop) → Phase 11

### Phase 11: Check Version

**Before publishing, verify current registry version:**

```bash
# Check current registry version
clawhub inspect skill-name --json | grep version

# Ensure new version follows semver:
# 1.0.0 → 1.0.1 (patch: bug fixes)
# 1.0.0 → 1.1.0 (minor: new features)
# 1.0.0 → 2.0.0 (major: breaking changes)

# Never downgrade! (1.1.0 → 1.0.2 is wrong)
```

**Update _meta.json with correct version:**

```json
{
  "version": "1.0.1"
}
```

### Phase 12: Package

```bash
# Create .skill package for distribution
./scripts/package-skill.sh my-skill ./dist

# Output: dist/my-skill.skill
# Validates structure before packaging
```

**Package contains:**
- All skill files
- Validated structure
- Ready for distribution

### Phase 13: Publish

```bash
cd my-skill

# Publish to clawhub
clawhub publish . --version 1.0.1 --changelog "Description of changes"

# Verify publication
clawhub inspect skill-name
```

**After publish:**
- Skill available in registry
- Others can install via `clawhub install skill-name`

## Required Files for Clawhub

### SKILL.md

Instructions and metadata:
- YAML frontmatter (name, description in English)
- Markdown body (workflow, examples)
- Navigation to references

### _meta.json

Registry metadata:
```json
{
  "name": "skill-name",
  "version": "1.0.0",
  "description": "Registry listing description in English",
  "requires": {
    "env": [],
    "credentials": []
  },
  "tags": ["latest"]
}
```

### LICENSE.txt

License file (MIT, Apache-2.0, etc.)

## Resources

- `references/skill-structure.md` - Directory structure patterns
- `references/agent-first-design.md` - Designing for AI vs humans
- `references/token-optimization.md` - Minimizing context usage
- `references/cross-platform.md` - Platform-aware scripts
- `references/validation-checklist.md` - Pre-publish checks
- `references/versioning.md` - Semver best practices

## Key Principles

### 1. Agent-First Design

Skills used by AI agents, not humans:
- ❌ No interactive prompts
- ❌ No platform-specific scripts (use knowledge instead)
- ✅ Command templates for all platforms
- ✅ Clear navigation to references

### 2. Progressive Disclosure

```
Level 1: Metadata (name + description)     → Always loaded
Level 2: SKILL.md body                      → On trigger
Level 3: Resources (references/, assets/)   → On demand
```

### 3. Token Budget

| Component | Target | Max |
|-----------|--------|-----|
| Metadata | 50 words | 100 words |
| SKILL.md | 200 lines | 300 lines |
| References | 3K words | 5K words |
| Total | 5K tokens | 10K tokens |

### 4. Cross-Platform Awareness

**Instead of script:**
```markdown
## Commands

**Linux/Mac:**
```bash
command --option
```

**Windows CMD:**
```cmd
command --option
```

**PowerShell:**
```powershell
command --option
```
```

**Agent chooses** appropriate variant based on detected platform.

### 5. English Language for Descriptions

**Required in English:**
- `description` in SKILL.md frontmatter
- `description` in _meta.json
- Main workflow instructions

**May use other languages:**
- Code examples
- Comments
- Domain-specific references
- User-facing examples

## Scripts

- `scripts/init-skill.sh` - Initialize new skill structure
- `scripts/package-skill.sh` - Package skill for distribution
- `scripts/validate.sh` - Validate skill structure

## Anti-Patterns

❌ **Don't:**
- Put "When to use" only in body (must be in description)
- Use non-English description in frontmatter
- Duplicate info between SKILL.md and references
- Create README.md, CHANGELOG.md (clutter)
- Use platform-specific scripts (sh/bat)
- Write passive voice ("You should")
- Include generic background theory
- Skip validation before publish
- Forget to bump version
- Publish without testing

✅ **Do:**
- Write description in English
- Start with concrete examples
- Move details to references/
- Use imperative voice ("Do X")
- Challenge every sentence's value
- Test with real agent queries
- Validate before publish
- Follow semver strictly
- Iterate based on test results