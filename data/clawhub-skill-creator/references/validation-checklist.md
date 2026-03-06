# Validation Checklist

Before publishing skill to clawhub:

## Structure

- [ ] `SKILL.md` exists in root
- [ ] `_meta.json` exists in root
- [ ] `LICENSE.txt` exists in root
- [ ] Directory name matches `name` in frontmatter
- [ ] No extraneous files (README.md, CHANGELOG.md, etc.)

## Metadata

- [ ] `_meta.json` has valid JSON
- [ ] `name` matches directory name
- [ ] `version` follows semver (X.Y.Z)
- [ ] `description` is concise (<100 words)
- [ ] `requires.env` lists all needed env vars
- [ ] `requires.credentials` lists all needed credentials
- [ ] `tags` includes "latest"

## SKILL.md

- [ ] Valid YAML frontmatter
- [ ] `name` field present
- [ ] `description` field present with "Use when:" triggers
- [ ] Body < 300 lines
- [ ] Imperative voice throughout
- [ ] No duplicate content with references
- [ ] Every resource file referenced
- [ ] Platform-aware commands (if applicable)

## References

- [ ] Files referenced from SKILL.md actually exist
- [ ] No deeply nested references (max 1 level)
- [ ] Each reference < 5K words
- [ ] No duplicate content between files

## Scripts (if any)

- [ ] Cross-platform or platform-aware
- [ ] No interactive prompts
- [ ] No external dependencies (or documented)
- [ ] Tested and working

## Token Budget

- [ ] Metadata: <100 words
- [ ] SKILL.md: <300 lines
- [ ] References: <5K words each
- [ ] Total: <10K tokens

## Agent Testing

- [ ] Skill triggers for intended queries
- [ ] Agent can follow workflow without clarification
- [ ] References loaded at appropriate time
- [ ] Edge cases handled

## Version Check

- [ ] Checked current version: `clawhub inspect skill-name`
- [ ] New version follows semver
- [ ] Not downgrading (1.1.0 → 1.0.2 is wrong)
- [ ] Changelog describes changes

## Pre-Publish Commands

```bash
# Validate JSON
jq . _meta.json

# Check line count
wc -l SKILL.md

# Check word counts
wc -w references/*.md

# Test with agent (manual)
# ...

# Publish
clawhub publish . --version X.Y.Z --changelog "Description"
```