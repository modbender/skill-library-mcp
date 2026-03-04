# Skill Routing Logic Convention

**Version:** 1.0  
**Date:** 2026-02-12  
**Status:** Deployed across 12 skills  

## Overview

This document defines the standard pattern for skill descriptions and structure, based on OpenAI's research showing that explicit routing logic with negative examples improves skill invocation accuracy by approximately 20%.

## The Pattern

### 1. Description as Routing Logic

Every skill description must include three sections:

```yaml
name: skill-name
description: |
  **USE WHEN:** 
  - Specific condition 1
  - Specific condition 2
  - Specific condition 3
  
  **DON'T USE WHEN:**
  - Exclusion 1 (use [alternative] instead)
  - Exclusion 2 (use [alternative] instead)
  - Exclusion 3 (use [alternative] instead)
  
  **Outputs:**
  - What skill produces (files, text, confirmations)
  - Error states to expect
  
  **Prerequisites (if any):**
  - Required configuration
  - Required setup
```

### 2. Decision Tree / Comparison Table

Include a table showing when to use this skill vs. alternatives:

```markdown
## Quick Decision: This Tool vs. Others

| Task | This Skill | Alternative |
|------|------------|-------------|
| Task A | ✅ Yes | No ❌ |
| Task B | No ❌ | ✅ Better tool |
| Task C | Maybe 🤔 | Depends on X |
```

### 3. Common Workflows (Organized by Use Case)

Organize commands by use case, not alphabetically:

```markdown
## Common Workflows

### Workflow 1: Name (Primary Use Case)
```bash
step one
step two
step three
```

### Workflow 2: Name (Secondary Use Case)
```bash
step one
step two
```
```

### 4. Negative Examples (3-4 minimum)

Each negative example must have three parts:

```markdown
## Negative Examples (Common Mistakes)

❌ **Mistake description:**
```bash
# WRONG - explanation of why this is wrong
command that fails or is inefficient

# CORRECT
command or approach that works
```
```

### 5. Safety Notes (Where Required)

For security-critical skills, include explicit safety sections:

```markdown
## Security/Safety Notes

- **Never do X** - explanation
- **Always verify Y** - explanation
- **Require explicit approval for Z** - explanation
```

## Examples by Category

### Technical/CLI Skills (github, tmux, himalaya)
- Focus on: Command decision trees
- Include: Common flags and options
- Safety: None (unless handling credentials)

### Security-Critical Skills (1password, healthcheck)
- Focus on: Prerequisites and guardrails
- Include: Required confirmations list
- Safety: EXTENSIVE - every risky operation

### Utility Skills (weather, summarize, gemini)
- Focus on: Comparison with alternatives
- Include: When to use simpler tools instead
- Safety: Minimal (standard usage)

### Integration Skills (gog, obsidian, clawhub)
- Focus on: Setup prerequisites
- Include: OAuth/API configuration steps
- Safety: Where credentials involved

## Deployment Checklist

When upgrading or creating a skill:

- [ ] Description has USE WHEN section
- [ ] Description has DON'T USE WHEN section
- [ ] Description specifies outputs
- [ ] Prerequisites noted (if any)
- [ ] Decision tree/table included
- [ ] Workflows organized by use case
- [ ] 3-4 negative examples with corrections
- [ ] Safety notes added (if needed)
- [ ] Homepage metadata included
- [ ] Dependencies/requirements documented

## Measurement

Track effectiveness via:
1. Fewer "Why did you use X instead of Y?" clarifications
2. Faster correct tool selection in logs
3. Reduced skill misfires (wrong tool chosen)
4. User feedback on skill accuracy

## References

- OpenAI Skills/Shell/Compaction blog: https://developers.openai.com/blog/skills-shell-tips
- Glean case study: ~20% misfire reduction after adding negative examples
- Current implementation: 12 skills upgraded (see `memory/skill-improvements-log.md`)

## Future Improvements

Potential additions to convention:
1. **Complexity rating** - Simple/Medium/Complex for resource planning
2. **Cost awareness** - API call costs where applicable
3. **Latency notes** - Expected response times
4. **Error handling** - Common errors and solutions

---

**This convention is living documentation.** Update as patterns evolve. 🧪
