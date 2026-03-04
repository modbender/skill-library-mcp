---
name: clawhub-skill-guide
description: >
  Create, structure, and publish OpenClaw skills to ClawHub that pass the
  security scanner with clean ratings. Covers frontmatter schema, env var
  declarations, script safety, config change patterns, and the full
  publish workflow. Use when: creating a new skill, publishing to ClawHub,
  fixing security scan warnings, structuring skill files, writing
  SKILL.md frontmatter, declaring environment variables, understanding
  scanner categories, preparing scripts for publication.
---

# ClawHub Skill Guide

Publish OpenClaw skills to ClawHub with clean security scanner ratings.
This guide supplements the built-in `skill-creator` skill with ClawHub-specific
publishing knowledge — especially frontmatter schema and scanner compliance.

> **Note:** The built-in `skill-creator` says "Do not include any other fields
> in YAML frontmatter." That guidance is outdated. ClawHub supports and the
> scanner **requires** additional fields like `env`, `metadata`, `requires`, etc.
> This guide documents the complete frontmatter schema.

---

## Quick Reference

### Skill Anatomy

```
my-skill/
├── SKILL.md              # Core instructions (required, under 500 lines)
├── scripts/              # Executable code (optional)
├── references/           # Docs loaded on demand (optional)
└── assets/               # Templates, images, non-context files (optional)
```

### Frontmatter Fields

| Field | Required | Purpose |
|-------|----------|---------|
| `name` | ✅ | Lowercase, hyphens, under 64 chars |
| `description` | ✅ | Trigger text with keywords |
| `env` | When credentials needed | Array of env var declarations |
| `metadata` | Alternative env format | OpenClaw-specific metadata |
| `requires` | When dependencies exist | Human-readable requirement list |
| `homepage` | Optional | Source/docs URL |
| `category` | Optional | Skill category |
| `emoji` | Optional | Display emoji |
| `version` | Optional | Semver (can also set via CLI) |

→ Full schema: [references/frontmatter-schema.md](references/frontmatter-schema.md)

### Scanner Categories

| # | Category | Key Requirement |
|---|----------|-----------------|
| 1 | PURPOSE & CAPABILITY | Description matches functionality; credentials declared |
| 2 | INSTRUCTION SCOPE | Instructions on-topic; no auto-config language |
| 3 | INSTALL MECHANISM | No external downloads; scripts write within workspace |
| 4 | CREDENTIALS | All env vars declared in frontmatter; sensitive marked |
| 5 | PERSISTENCE & PRIVILEGE | No always:true; config as templates for manual review |

→ Deep dive: [references/scanner-compliance.md](references/scanner-compliance.md)

---

## Creating a Skill

### Step 1: Plan Structure

Decide what goes where:

| Content Type | Location |
|-------------|----------|
| Core workflow, key instructions | SKILL.md body |
| Detailed reference material | `references/` |
| Executable automation | `scripts/` |
| Templates, images, boilerplate | `assets/` |

Keep SKILL.md under 500 lines. Move detailed docs to references.

### Step 2: Write Frontmatter

This is where most scanner issues originate. Get frontmatter right first.

**Important:** The local packager (`package_skill.py`) only allows these top-level
frontmatter keys: `name`, `description`, `license`, `metadata`, `allowed-tools`.
The `env:` key works on ClawHub's registry but fails local validation. Use the
`metadata.openclaw` format for compatibility with both.

**Minimal frontmatter (no credentials needed):**

```yaml
---
name: my-skill
description: >
  What this skill does. Include trigger keywords so the agent
  knows when to activate it. Use when: scenario1, scenario2.
---
```

**With credentials (packager-compatible format):**

```yaml
---
name: my-api-skill
description: >
  Integrates with Example API for data retrieval and analysis.
  Use when: querying example data, generating reports from Example API.
metadata:
  openclaw:
    requires:
      env:
        - EXAMPLE_API_KEY
      bins:
        - curl
    primaryEnv: EXAMPLE_API_KEY
    env:
      - name: EXAMPLE_API_KEY
        description: "API key for Example service"
        required: true
      - name: EXAMPLE_BASE_URL
        description: "Base URL for Example API (default: https://api.example.com)"
        required: false
---
```

**Note:** If you skip the local packager and publish directly with `npx clawhub publish`,
the direct `env:` top-level array also works (some published skills use this). But
the `metadata.openclaw` format works everywhere.

→ All supported fields and formats: [references/frontmatter-schema.md](references/frontmatter-schema.md)

### Step 3: Write Body

Structure the body for progressive disclosure:

1. **Quick Start** — Minimal steps to use the skill
2. **Prerequisites** — Table of requirements (if any)
3. **Security Notes** — Script safety, credential handling (if applicable)
4. **How It Works** — Core instructions
5. **File Reference** — List bundled resources with descriptions

Keep instructions imperative. Challenge every paragraph: "Does the agent
really need this?"

### Step 4: Add Scripts (If Needed)

Follow safe patterns to pass the scanner:

- Only write within the skill workspace
- No network calls unless explicitly declared and justified
- No obfuscated code
- Document line count and purpose in SKILL.md
- Include "inspect before running" warning

→ Full patterns: [references/script-safety.md](references/script-safety.md)

### Step 5: Validate and Package

```bash
# Validate structure
python3 ~/.npm-global/lib/node_modules/openclaw/skills/skill-creator/scripts/package_skill.py ./my-skill

# Check manually:
# - Frontmatter has name + description
# - env declarations match actual credential usage
# - No personal data or test artifacts
# - SKILL.md under 500 lines
```

### Step 6: Publish and Check Scanner

```bash
# Verify auth
npx clawhub whoami

# Publish
npx clawhub publish ./my-skill \
  --slug my-skill \
  --name "My Skill" \
  --version 1.0.0 \
  --changelog "Initial release" \
  --tags latest

# Check scanner results
npx clawhub inspect my-skill
```

→ Full workflow: [references/publish-workflow.md](references/publish-workflow.md)

---

## Frontmatter Quick Guide

### The Three Env Declaration Formats

ClawHub supports three ways to declare environment variables. All are valid;
the `metadata.openclaw` format is recommended for compatibility with both
the local packager and the ClawHub scanner.

**Format 1 — Direct `env:` array (richest data, but fails local packager):**

```yaml
env:
  - name: MY_API_KEY
    description: "API key for the service"
    required: true
    sensitive: true
```

Works with `npx clawhub publish` but NOT with `package_skill.py` validation.

**Format 2 — `metadata.openclaw.env` (recommended — works everywhere):**

```yaml
metadata:
  openclaw:
    env:
      - name: MY_API_KEY
        description: "API key for the service"
        required: false
```

**Format 3 — `metadata.openclaw.requires`:**

```yaml
metadata:
  openclaw:
    requires:
      env:
        - MY_API_KEY
      bins:
        - curl
    primaryEnv: MY_API_KEY
```

Format 1 gives the scanner the most information (including `sensitive` flag)
and produces the cleanest scan results.

### Description Best Practices

The description is the primary trigger mechanism. Include:

- What the skill does (concrete actions)
- Keywords matching user queries
- "Use when:" clause listing activation scenarios

**Bad:** `"Helps with APIs."`

**Good:**
```yaml
description: >
  Query and manage Example API resources including users, projects,
  and billing data. Generates reports, monitors usage, and handles
  authentication. Use when: querying Example API, generating usage
  reports, managing API resources, checking billing status.
```

---

## Scanner Compliance Quick Guide

### 1. PURPOSE & CAPABILITY ✓

- Description accurately reflects what the skill does
- All credentials declared in frontmatter `env` or `metadata`
- No undeclared external service dependencies

### 2. INSTRUCTION SCOPE ✓

- Instructions stay on-topic for the skill's stated purpose
- No language about automatically applying config changes
- Privileged operations marked as "requires manual review"
- If using `requireMention:false`, document data exposure implications

### 3. INSTALL MECHANISM ✓

- No `curl`, `wget`, or network downloads in scripts
- Scripts only write within the skill workspace directory
- Include "inspect before running" notes for all scripts
- No obfuscated or minified executable code

### 4. CREDENTIALS ✓

- Every env var the skill uses is declared in frontmatter
- Sensitive credentials marked `sensitive: true`
- No requests for credentials unrelated to the skill's purpose
- Prerequisites table lists all required accounts/keys

### 5. PERSISTENCE & PRIVILEGE ✓

- No `always:true` in config recommendations
- Config changes presented as templates for manual review
- Multi-user skills recommend agent isolation (separate OpenClaw agent)
- No persistent background processes or daemons

→ Deep dive with case study: [references/scanner-compliance.md](references/scanner-compliance.md)

---

## Publishing

### Command Reference

```bash
# Publish a skill
npx clawhub publish ./skill-dir \
  --slug my-skill \
  --name "Display Name" \
  --version 1.0.0 \
  --changelog "What changed" \
  --tags latest

# Inspect published skill
npx clawhub inspect my-skill
npx clawhub inspect my-skill --files
npx clawhub inspect my-skill --file SKILL.md

# Browse and search
npx clawhub explore
npx clawhub search "keyword"

# Auth
npx clawhub whoami
```

### Version Bumping

When fixing scanner warnings, bump the version and republish:

```bash
npx clawhub publish ./skill-dir \
  --slug my-skill \
  --version 1.1.0 \
  --changelog "Fix: declared env vars in frontmatter for clean scan" \
  --tags latest
```

---

## Common Pitfalls

| Mistake | Scanner Impact | Fix |
|---------|---------------|-----|
| No env declarations when skill uses credentials | ! CREDENTIALS | Add env vars via `metadata.openclaw.env` in frontmatter |
| "Agent automatically applies config" language | ! INSTRUCTION SCOPE | Change to "manual review required" |
| Scripts without inspection warning | ℹ INSTALL MECHANISM | Add "inspect before running" note |
| No agent isolation for multi-user skills | ℹ PERSISTENCE | Add security model section |
| `requireMention:false` without data exposure docs | ℹ INSTRUCTION SCOPE | Document what data the skill sees |
| Description too short / missing keywords | Poor discoverability | Expand with trigger scenarios |
| Shipping test DBs or generated files | Bloat | Clean before publishing |
| Personal data in examples | Privacy risk | Use generic examples |

---

## Templates

Ready-to-use SKILL.md templates:

- [Basic skill](assets/templates/basic-skill.md) — Minimal SKILL.md
- [Skill with scripts](assets/templates/skill-with-scripts.md) — Scripts + env vars
- [Skill with config](assets/templates/skill-with-config.md) — Gateway config changes

Copy, fill in the placeholders, publish.

---

## File Reference

| File | Purpose |
|------|---------|
| `references/frontmatter-schema.md` | Complete YAML frontmatter field documentation |
| `references/scanner-compliance.md` | Scanner categories deep dive with case study |
| `references/script-safety.md` | Safe script patterns for publication |
| `references/publish-workflow.md` | Step-by-step publish and iterate workflow |
| `assets/templates/basic-skill.md` | Minimal SKILL.md template |
| `assets/templates/skill-with-scripts.md` | Template with scripts and env vars |
| `assets/templates/skill-with-config.md` | Template for config-changing skills |
