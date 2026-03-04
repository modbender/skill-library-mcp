---
name: skill-reviewer
description: Comprehensive skill review and validation. Use when you need to audit an OpenClaw skill for correctness, completeness, and compliance with OpenClaw specifications. Performs three levels of review: (1) Format validation via package_skill.py, (2) Content quality assessment of SKILL.md structure and writing, (3) Functional verification that generated templates/scripts match actual OpenClaw specifications.
---

# Skill Reviewer

Comprehensive skill review and validation for OpenClaw skills.

## Overview

This skill provides a systematic three-level review process to ensure skills are:
- **Valid** - Proper structure and format
- **Complete** - All required components present
- **Correct** - Generated outputs match OpenClaw specifications
- **High-quality** - Follows best practices

## Review Workflow

### Level 1: Format Validation

Run automatic validation using `package_skill.py`:

```bash
python3 /home/yupeng/.npm-global/lib/node_modules/openclaw/skills/skill-creator/scripts/package_skill.py <skill-path>
```

**Checks:**
- YAML frontmatter format and required fields
- Skill naming conventions and directory structure
- Description completeness and quality
- File organization and resource references

**Outcome:** ✅ Valid or ❌ Validation errors

### Level 2: Content Quality Assessment

Manually review SKILL.md for:

**Frontmatter:**
- `name` is concise and follows naming conventions
- `description` is comprehensive and includes "when to use" information
- No extraneous fields in YAML

**Body Structure:**
- Clear organization (workflow-based, task-based, or reference-based)
- Progressive disclosure pattern (metadata → SKILL.md → references)
- Concise and focused content
- Imperative/infinitive form for instructions

**Writing Quality:**
- No filler or redundant explanations
- Concrete examples and realistic scenarios
- Clear guidance on when to read reference files
- Avoids duplication between SKILL.md and references

### Level 3: Functional Verification

**Critical Step** - Verify that generated outputs match actual OpenClaw specifications.

**For skills that generate templates:**
- Compare generated templates with actual OpenClaw specification files
- Example: If skill generates AGENTS.md templates, compare with `/home/yupeng/.openclaw/workspace/AGENTS.md`
- Check for missing required sections (session startup, memory workflow, safety rules, group chat etiquette, heartbeat mechanism)
- Verify all critical requirements are present

**For skills with scripts:**
- Test scripts to ensure they work correctly
- Verify output matches expected format
- Check error handling

**For skills with references:**
- Verify reference files are accurate and up-to-date
- Check that references are properly linked from SKILL.md

### Level 4: Best Practices Check

Verify the skill follows OpenClaw skill best practices:

**Progressive Disclosure:**
- SKILL.md body is concise (<500 lines preferred)
- Detailed information moved to references/
- References are properly linked and described

**Resource Organization:**
- Only necessary resource directories created
- No extraneous files (README.md, INSTALLATION_GUIDE.md, etc.)
- Scripts/ references/ assets/ used appropriately

**Context Efficiency:**
- Information lives in either SKILL.md OR references, not both
- Essential procedural instructions in SKILL.md
- Detailed reference material in references/

**Triggering Accuracy:**
- `description` clearly states when the skill should be used
- All "when to use" information is in description, not body

## Common Issues Found

**Missing Functional Verification:**
- Skill generates templates but they don't match actual specifications
- Example: AGENTS.md template missing session startup requirements

**Incomplete Descriptions:**
- Description doesn't include "when to use" information
- Body contains "When to Use This Skill" sections (should be in description)

**Duplication:**
- Same information in both SKILL.md and references
- Wastes context window tokens

**Extraneous Files:**
- README.md, CHANGELOG.md, etc. in skill directory
- Should only contain SKILL.md and necessary resources

**Poor Progressive Disclosure:**
- SKILL.md too verbose
- References not properly linked or described

## Review Checklist

For each skill, verify:

- [ ] Level 1: Format validation passes
- [ ] Level 2: SKILL.md structure and quality are good
- [ ] Level 3: Generated templates match OpenClaw specifications
- [ ] Level 4: Best practices are followed
- [ ] No extraneous files
- [ ] Description includes "when to use" information
- [ ] References are properly linked from SKILL.md
- [ ] Scripts work correctly (if present)

## Resources

### scripts/
- `review_skill.py` - Automated review script (optional enhancement)

### references/
- `openclaw-specs.md` - OpenClaw specifications for comparison
- `best-practices.md` - Skill design best practices
