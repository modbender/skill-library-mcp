# Skill Template

Use this template when generating extracted skills from a project.

---

## Template

```markdown
---
name: [project-name]-[category]
description: [WHAT it does]. Use when [WHEN scenarios]. Triggers on [KEYWORDS].
---

# [Skill Title]

[One sentence describing what expert knowledge this skill captures.]

---

## When to Use

- [Specific scenario 1]
- [Specific scenario 2]
- [Specific scenario 3]

---

## Core Patterns

### [Pattern 1 Name]

[Expert knowledge about this pattern - decision trees, trade-offs, edge cases]

### [Pattern 2 Name]

[Expert knowledge about this pattern]

---

## Decision Tree

[For multi-path scenarios, provide clear decision guidance]

| Situation | Approach | Why |
|-----------|----------|-----|
| [When X] | [Do Y] | [Because Z] |
| [When A] | [Do B] | [Because C] |

---

## Code Examples

[Working code examples, not pseudocode]

```[language]
// Example with explanation
```

---

## NEVER Do

- **[Specific anti-pattern]** — [Non-obvious reason why]
- **[Specific anti-pattern]** — [Non-obvious reason why]

---

## Edge Cases

| Case | Solution |
|------|----------|
| [Edge case 1] | [How to handle] |
| [Edge case 2] | [How to handle] |
```

---

## Quality Checklist

Before finalizing, verify:

- [ ] Description has WHAT, WHEN, and KEYWORDS
- [ ] No explanations of things Claude already knows
- [ ] Has specific NEVER list with reasons
- [ ] Working code examples (not pseudocode)
- [ ] Decision trees for multi-path scenarios
- [ ] < 300 lines (ideal), < 500 lines (max)
- [ ] Would an expert say "this captures real knowledge"?

---

## Pattern Guidelines

Choose structure based on skill type:

| Type | Lines | Structure |
|------|-------|-----------|
| Mindset | ~50 | Thinking principles + NEVER list |
| Navigation | ~30 | Routes to sub-files for scenarios |
| Philosophy | ~150 | Philosophy section + expression section |
| Process | ~200 | Phased workflow with checkpoints |
| Tool | ~300 | Decision trees + code examples + edge cases |
