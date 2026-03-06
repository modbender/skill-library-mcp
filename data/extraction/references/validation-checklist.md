# Extraction Validation Checklist

Pre-output validation steps to ensure extraction quality.

---

## Skill Validation

### Required Sections

- [ ] **Frontmatter** with `name` and `description`
- [ ] **When to Use** section with clear triggers
- [ ] **Code examples** (if applicable)
- [ ] **NEVER Do** section with anti-patterns
- [ ] **Related Skills** section (if applicable)

### Description Quality

The description must contain:

| Component | Example | Check |
|-----------|---------|-------|
| WHAT | "Extract design tokens from Tailwind configs" | What does this skill do? |
| WHEN | "Use when analyzing existing design systems" | When should it activate? |
| KEYWORDS | "extract, design tokens, Tailwind, CSS variables" | Trigger words |

**Test:** Read the description aloud. Would you know when to use this skill?

### Expert Knowledge Test

Ask: "Does Claude already know this?"

| Type | Keep | Delete |
|------|------|--------|
| Expert intuition | ✓ | |
| Decision trees | ✓ | |
| Anti-patterns from experience | ✓ | |
| Basic concepts | | ✓ |
| Tutorial content | | ✓ |
| API documentation | | ✓ |

**Rule:** >70% of content should be expert knowledge not in base model.

### Size Check

| Status | Lines | Action |
|--------|-------|--------|
| Ideal | <300 | Proceed |
| Acceptable | 300-500 | Consider splitting |
| Too large | >500 | Must split into references/ |

### Project-Agnostic Check

Search for:
- [ ] Hardcoded project names (remove)
- [ ] Specific file paths (generalize)
- [ ] Unique configurations (abstract to patterns)
- [ ] Team-specific conventions (generalize)

---

## Documentation Validation

### Design System Docs

- [ ] **Color palette** — Actual hex/HSL values extracted
- [ ] **Typography** — Font families and scale captured
- [ ] **Spacing** — Scale documented
- [ ] **Motion** — Animation timings captured
- [ ] **Aesthetic direction** — "The vibe" documented in words

### Project Summary Docs

- [ ] **Tech stack** — Complete and accurate
- [ ] **Folder structure** — Documented with reasoning
- [ ] **Key decisions** — Notable patterns explained
- [ ] **What worked** — Lessons learned
- [ ] **What to improve** — Honest assessment

### Template Completeness

| Issue | Fix |
|-------|-----|
| `[placeholder]` text | Replace with actual values |
| `TODO` comments | Complete or remove |
| Empty sections | Fill or delete section |
| Sample data | Replace with real extracted data |

---

## Common Validation Errors

### Skills

| Error | Fix |
|-------|-----|
| Description too vague | Add specific WHEN and KEYWORDS |
| No When to Use section | Add section with 3-5 triggers |
| No code examples | Add at least one example |
| No NEVER Do section | Add 3-5 anti-patterns |
| Too long (>500 lines) | Move details to references/ |
| Project-specific content | Generalize or remove |

### Documentation

| Error | Fix |
|-------|-----|
| Placeholder text remains | Replace with actual values |
| Missing aesthetic description | Add "The Vibe" section |
| Incomplete token extraction | Re-scan source files |
| No file paths | Add source file references |

---

## Validation Commands

```bash
# Count lines in skill
wc -l SKILL.md

# Search for placeholders
grep -E '\[.*\]|TODO|FIXME' SKILL.md

# Search for project names
grep -i '[project-name]' SKILL.md
```

---

## Pre-Output Checklist

Before writing any output:

### For Skills
- [ ] Description has WHAT, WHEN, KEYWORDS
- [ ] When to Use section exists with triggers
- [ ] Code examples included
- [ ] NEVER Do section with 3+ anti-patterns
- [ ] <300 lines (or justified if larger)
- [ ] No project-specific content
- [ ] No placeholders remaining

### For Docs
- [ ] Template fully filled out
- [ ] Actual values (not examples)
- [ ] Aesthetic documented (for design systems)
- [ ] File paths correct and accessible

---

## Related

- **Quality criteria:** [`skill-quality-criteria.md`](skill-quality-criteria.md)
- **Templates:** [`output-templates/`](output-templates/)
- **Extraction skill:** [`../SKILL.md`](../SKILL.md)
