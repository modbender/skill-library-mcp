# Skill Design Best Practices

Based on skill-creator SKILL.md and OpenClaw conventions.

## Core Principles

### Concise is Key
The context window is a public good. Skills share the context window with everything else.

**Default assumption:** Codex is already very smart. Only add context Codex doesn't already have.

Challenge each piece of information:
- "Does Codex really need this explanation?"
- "Does this paragraph justify its token cost?"

Prefer concise examples over verbose explanations.

### Set Appropriate Degrees of Freedom

Match the level of specificity to the task's fragility and variability:

**High freedom (text-based instructions):**
- Multiple approaches are valid
- Decisions depend on context
- Heuristics guide the approach

**Medium freedom (pseudocode or scripts with parameters):**
- Preferred pattern exists
- Some variation is acceptable
- Configuration affects behavior

**Low freedom (specific scripts, few parameters):**
- Operations are fragile and error-prone
- Consistency is critical
- Specific sequence must be followed

## Progressive Disclosure Design

Skills use a three-level loading system:

1. **Metadata (name + description)** - Always in context (~100 words)
2. **SKILL.md body** - When skill triggers (<5k words)
3. **Bundled resources** - As needed by Codex (Unlimited)

### Progressive Disclosure Patterns

**Pattern 1: High-level guide with references**
Keep SKILL.md body to essentials, link to detailed references:

```markdown
# PDF Processing

## Quick start
Extract text with pdfplumber: [code example]

## Advanced features
- **Form filling**: See [FORMS.md](FORMS.md)
- **API reference**: See [REFERENCE.md](REFERENCE.md)
```

**Pattern 2: Domain-specific organization**
Organize by domain to avoid loading irrelevant context:

```
bigquery-skill/
├── SKILL.md (overview and navigation)
└── reference/
    ├── finance.md
    ├── sales.md
    ├── product.md
    └── marketing.md
```

**Pattern 3: Conditional details**
Show basic content, link to advanced:

```markdown
# DOCX Processing

## Creating documents
Use docx-js. See [DOCX-JS.md](DOCX-JS.md).

## Editing documents
For simple edits, modify XML directly.
**For tracked changes**: See [REDLINING.md](REDLINING.md)
```

### Guidelines

- **Avoid deeply nested references** - Keep references one level deep from SKILL.md
- **Structure longer reference files** - Include table of contents for files >100 lines
- **Keep SKILL.md under 500 lines** - Split content when approaching this limit

## SKILL.md Structure

### Frontmatter (YAML)

Required fields:
- `name`: The skill name
- `description`: Primary triggering mechanism
  - Include both what the skill does AND when to use it
  - Include all "when to use" information here (NOT in body)
  - Example: "Comprehensive document creation, editing, and analysis. Use when Codex needs to work with .docx files for: (1) Creating new documents, (2) Modifying content, (3) Working with tracked changes"

**Do NOT include any other fields in YAML frontmatter.**

### Body

**Writing Guidelines:**
- Always use imperative/infinitive form
- Be concise and focused
- Include concrete examples
- Reference bundled resources clearly

## Resource Organization

### scripts/
Executable code (Python/Bash/etc.) for tasks requiring deterministic reliability.

**When to include:**
- Same code is being rewritten repeatedly
- Deterministic reliability is needed

**Benefits:**
- Token efficient
- Deterministic execution
- May execute without loading into context

### references/
Documentation intended to be loaded as needed into context.

**When to include:**
- Documentation Codex should reference while working
- Database schemas, API documentation, domain knowledge, company policies

**Best practice:**
- If files are large (>10k words), include grep search patterns in SKILL.md
- **Avoid duplication**: Information should live in either SKILL.md OR references, not both

### assets/
Files used in output, not loaded into context.

**When to include:**
- Templates, images, icons, boilerplate code, fonts, sample documents

**Benefits:**
- Separates output resources from documentation
- Enables Codex to use files without loading into context

## What NOT to Include

A skill should only contain essential files. Do NOT create:

- README.md
- INSTALLATION_GUIDE.md
- QUICK_REFERENCE.md
- CHANGELOG.md
- etc.

The skill should only contain information needed for an AI agent to do the job at hand.

## Skill Naming

- Use lowercase letters, digits, and hyphens only
- Normalize titles to hyphen-case (e.g., "Plan Mode" -> `plan-mode`)
- Generate names under 64 characters
- Prefer short, verb-led phrases
- Namespace by tool when it improves clarity (e.g., `gh-address-comments`)
- Name skill folder exactly after the skill name

## Common Anti-Patterns

### "When to Use This Skill" in Body
❌ Wrong: Body contains "When to Use This Skill" section
✅ Right: All "when to use" information in description field

### Duplication
❌ Wrong: Same information in both SKILL.md and references
✅ Right: Information lives in one place only

### Verbose SKILL.md
❌ Wrong: SKILL.md body is long and detailed
✅ Right: SKILL.md is concise, details in references

### Extraneous Files
❌ Wrong: README.md, CHANGELOG.md, etc. in skill directory
✅ Right: Only SKILL.md and necessary resources

### Missing Links
❌ Wrong: References exist but not linked from SKILL.md
✅ Right: SKILL.md clearly describes when to read each reference