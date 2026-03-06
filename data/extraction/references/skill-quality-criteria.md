# Skill Quality Criteria

Condensed quality checklist for generating high-quality skills. Based on the 8-dimension evaluation framework.

---

## The Core Formula

> **Good Skill = Expert-only Knowledge − What Claude Already Knows**

A skill's value is measured by its **knowledge delta** — the gap between what it provides and what Claude already knows.

---

## Quick Quality Checklist

Before finalizing any extracted skill, verify:

### Knowledge Delta (Most Important)
- [ ] No "What is X" explanations for basic concepts
- [ ] No step-by-step tutorials for standard operations
- [ ] Has decision trees for non-obvious choices
- [ ] Has trade-offs only experts would know
- [ ] Has edge cases from real-world experience

### Description Quality (Critical for Activation)
- [ ] Answers WHAT: What does this skill do?
- [ ] Answers WHEN: In what situations should it be used?
- [ ] Contains KEYWORDS: Searchable trigger terms
- [ ] Specific enough that agent knows exactly when to use it

### Anti-Patterns
- [ ] Has explicit NEVER list
- [ ] Anti-patterns are specific, not vague
- [ ] Includes WHY (non-obvious reasons)

### Structure
- [ ] SKILL.md < 500 lines (ideal < 300)
- [ ] Heavy content in references/ if needed
- [ ] Loading triggers embedded in workflow (if references exist)

### Usability
- [ ] Decision trees for multi-path scenarios
- [ ] Working code examples (not pseudocode)
- [ ] Error handling and fallbacks
- [ ] Edge cases covered

---

## Three Types of Knowledge

When writing skill content, categorize each section:

| Type | Definition | Treatment |
|------|------------|-----------|
| **Expert** | Claude genuinely doesn't know this | Must keep — this is the skill's value |
| **Activation** | Claude knows but may not think of | Keep if brief — serves as reminder |
| **Redundant** | Claude definitely knows this | Should delete — wastes tokens |

Target ratio: >70% Expert, <20% Activation, <10% Redundant

---

## Description Template

The description is THE MOST IMPORTANT field — determines if skill gets activated.

```yaml
---
name: [lowercase-hyphenated-name]
description: [WHAT it does]. Use when [WHEN scenarios]. Triggers on [KEYWORDS].
---
```

**Good example:**
```yaml
description: Design system patterns for retro-futuristic UI with CRT effects, 
  scan lines, and analog-digital fusion. Use when building video game-style 
  interfaces, sci-fi terminals, or applications needing a distinct nostalgic-future 
  aesthetic. Triggers on retro, futuristic, CRT, synthwave, cyberpunk.
```

**Bad example:**
```yaml
description: Helps with design.
```

---

## Anti-Pattern Quality

Expert anti-patterns are specific with non-obvious reasons:

**Good:**
```markdown
NEVER:
- Use Inter, Roboto, or system-ui for distinctive aesthetics (too generic)
- Apply purple gradients on white (screams "AI-generated")
- Use default Tailwind spacing (looks like every other site)
```

**Bad:**
```markdown
NEVER:
- Make mistakes
- Be inconsistent
- Forget edge cases
```

---

## Skill Patterns

Choose the appropriate pattern based on task type:

| Pattern | ~Lines | When to Use |
|---------|--------|-------------|
| **Mindset** | ~50 | Creative tasks requiring taste |
| **Navigation** | ~30 | Multiple distinct sub-scenarios |
| **Philosophy** | ~150 | Art/creation requiring originality |
| **Process** | ~200 | Complex multi-step projects |
| **Tool** | ~300 | Precise operations on specific formats |

---

## Common Failure Patterns to Avoid

1. **The Tutorial** — Explains basics Claude already knows
2. **The Dump** — Everything in SKILL.md (>500 lines, no structure)
3. **The Orphan References** — References exist but never loaded
4. **The Checkbox Procedure** — Generic Step 1, 2, 3 without thinking frameworks
5. **The Vague Warning** — "Be careful" without specifics
6. **The Invisible Skill** — Great content, poor description
7. **The Over-Engineered** — README, CHANGELOG, INSTALLATION_GUIDE, etc.

---

## The Meta-Question

Before finalizing any skill, ask:

> **"Would an expert in this domain say: 'Yes, this captures knowledge that took me years to learn'?"**

If yes → the skill has genuine value.
If no → it's compressing what Claude already knows.
