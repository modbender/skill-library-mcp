# Patterns — Skill Builder / Creator

Common patterns for different skill types.

## Pattern 1: Memory-Based Skills

Skills that learn and adapt to user preferences.

```
skill/
├── SKILL.md           # Instructions + memory reference
├── setup.md           # Integration process
├── memory-template.md # Memory structure
└── [domain].md        # Domain details
```

**Key elements:**
- Memory structure with status tracking
- Rules for when to update memory
- Integration with user's main memory

## Pattern 2: Tool Integration Skills

Skills wrapping external tools or APIs.

```
skill/
├── SKILL.md           # Workflow + commands
├── setup.md           # Installation verification
├── reference.md       # Command reference
└── scripts/           # Helper scripts
    └── [tool].sh
```

**Key elements:**
- External Endpoints table (required)
- Security & Privacy section
- Script manifests
- Error handling guidance

## Pattern 3: Domain Expert Skills

Skills providing specialized knowledge.

```
skill/
├── SKILL.md           # Overview + rules
├── setup.md           # Minimal
├── memory-template.md # Minimal config
└── references/
    ├── [topic1].md
    └── [topic2].md
```

**Key elements:**
- Progressive loading of references
- Clear triggers in description
- Core Rules capture expert judgment

## Pattern 4: Workflow Skills

Skills guiding multi-step processes.

```
skill/
├── SKILL.md           # Process overview
├── setup.md           # Prerequisites
├── memory-template.md # Progress tracking
├── phases/
│   ├── phase1.md
│   └── phase2.md
└── templates/         # Output templates
```

**Key elements:**
- Clear phase boundaries
- Progress tracking in memory
- Templates for outputs

## Description Examples

### Good Descriptions (copy these patterns)

| Domain | Description |
|--------|-------------|
| PDF | "Process, merge, and extract PDF content with page manipulation and text extraction." |
| Git | "Manage branches, resolve conflicts, and automate Git workflows with best practices." |
| Docker | "Build, deploy, and debug Docker containers with compose patterns and troubleshooting." |
| API | "Design, document, and test REST APIs with OpenAPI specs and mock servers." |
| Database | "Query, optimize, and migrate databases with schema design and performance tuning." |

### Bad Descriptions (avoid these)

| ❌ Bad | Why |
|--------|-----|
| "Use when you need to work with PDFs" | Starts with "Use when" |
| "PDF helper. Triggers: pdf, document, merge" | Multiple sentences, keyword list |
| "A comprehensive guide to Docker—including containers, images, and more" | Em-dash, vague "more" |
| "Helper for Git stuff" | Too vague, "stuff" |

### Formula

```
[Verb], [verb], and [verb] [technology] with [feature], [feature], and [feature].
```

15-25 words. One sentence. No em-dashes (—). No "Use when".

## Frontmatter Checklist

```yaml
---
name: Clear Name           # What it is
slug: clear-name           # Lowercase, hyphens
version: 1.0.0             # Semver
description: One sentence. # Action verbs. 15-25 words.
---
```

## Quality Checklist

Before publishing:
- [ ] SKILL.md under 80 lines?
- [ ] Description is one sentence, 15-25 words?
- [ ] All required sections present?
- [ ] No redundancy between files?
- [ ] Core Rules are actionable?
- [ ] Traps are real failure modes?

## Security Checklist

Avoid getting flagged as suspicious:
- [ ] No vague words: "silently", "secretly", "automatically"
- [ ] If creating files, add `## Data Storage` section
- [ ] If using APIs, add `## External Endpoints` table
- [ ] If using env vars, declare in metadata requires
- [ ] No "observe", "monitor", "track" without specifying WHAT exactly
- [ ] Always mention "ask user first" for file operations
