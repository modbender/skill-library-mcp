# Pre-Publish Quality Checklist

Validate each item before publishing a skill. Report results to the user as a checklist.

## Structure

- [ ] Folder name is lowercase, hyphens only, max 64 chars
- [ ] Folder name matches `name` field in frontmatter
- [ ] `SKILL.md` exists in the skill root
- [ ] `README.md` exists (required for published skills)
- [ ] `scripts/` directory present only if the skill uses external scripts

## Frontmatter

- [ ] `name` field is present and valid
- [ ] `description` field is present
- [ ] Description includes "Use when..." trigger phrases
- [ ] Description is specific enough to avoid overlap with other skills
- [ ] `metadata` declares all runtime dependencies via `requires.bins` and/or `requires.env`
- [ ] `metadata` uses inline JSON format (not nested YAML)

## Body

- [ ] Opening line explains what the skill does (one sentence)
- [ ] `## Workflow` section with numbered H3 steps
- [ ] Steps are written in imperative form ("Extract the URL", not "The URL is extracted")
- [ ] Tables used for structured data (fields, flags, mappings)
- [ ] Code blocks use `exec` tool JSON format for shell commands
- [ ] `{baseDir}` used for all paths within the skill directory
- [ ] No hardcoded secrets, API keys, or tokens
- [ ] Confirmation step before any state-changing operation (DB write, message send, file delete)
- [ ] Error handling section is present and covers common failures
- [ ] Examples section with at least 3 realistic input/output rows
- [ ] Total SKILL.md line count is under 500

## README.md

- [ ] Describes what the skill does (1-2 lines)
- [ ] Lists requirements (binaries, services, env vars)
- [ ] Includes setup instructions
- [ ] Shows 2-3 natural language usage examples
- [ ] Contains install command (`clawhub install <slug>`)

## Final

- [ ] Skill can be understood by reading SKILL.md alone (self-contained workflow)
- [ ] No dead references to files that don't exist
- [ ] Large reference docs moved to `references/` and loaded on-demand via `{baseDir}`
