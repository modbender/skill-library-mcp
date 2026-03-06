---
name: SOP Generator
description: Generate Standard Operating Procedures from plain-language process
  descriptions.
---

# SOP Generator

Generate Standard Operating Procedures from plain-language process descriptions.

## Usage

Describe any business process and this skill creates a structured SOP document with:
- Step-by-step instructions with numbered sections
- Role assignments and responsibilities  
- Decision points and escalation paths
- Quality checkpoints and acceptance criteria
- Time estimates per step
- Common failure modes and troubleshooting

## When to Use

- Documenting team processes for the first time
- Onboarding new hires who need clear procedures
- Standardizing operations across locations or departments
- Preparing for compliance audits (ISO, SOC2, etc.)
- Turning tribal knowledge into repeatable systems

## Instructions

When the user asks to create an SOP or document a process:

1. Ask what process they want documented (if not provided)
2. Ask who performs it and how often
3. Generate a complete SOP in this format:

```markdown
# SOP: [Process Name]
**Version:** 1.0 | **Owner:** [Role] | **Frequency:** [How often]
**Last Updated:** [Date]

## Purpose
[Why this process exists and what it achieves]

## Scope
[Who this applies to, when it applies]

## Prerequisites
- [What's needed before starting]

## Procedure

### Step 1: [Action]
**Responsible:** [Role]  
**Time:** [Estimate]  
- Detail 1
- Detail 2
- **Decision point:** If [condition], go to Step X

### Step 2: [Action]
...

## Quality Checks
- [ ] [Verification item]

## Failure Modes
| Issue | Cause | Resolution |
|-------|-------|------------|

## Revision History
| Date | Version | Changes | Author |
|------|---------|---------|--------|
```

4. Tailor complexity to the process — simple processes get simple SOPs
5. Include specific, actionable details — not generic filler
6. Flag any gaps where the user needs to fill in company-specific details

## Tips

- Start with your most painful/error-prone process
- Have the person who actually does the work review the SOP
- Review SOPs quarterly — stale procedures are worse than none
- For complex operations, consider the [AfrexAI Context Packs](https://afrexai-cto.github.io/context-packs/) which include industry-specific SOP templates and operational frameworks for 10 industries
