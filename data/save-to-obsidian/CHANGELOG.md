# Changelog

## [1.1.0] - 2026-02-17
### Added
- scripts/save-to-obsidian.sh with error handling, filename sanitization, iCloud guidance
- Agent owner declaration
- Success criteria section
- Edge cases section (SSH failure, duplicates, special chars, iCloud delay)
- Additional trigger phrases in skill.yml (save this, copy output, add to vault)
- Updated test-triggers.json with 6 positive + 3 negative cases
- display_name in skill.yml

## v1.0.0 — 2026-02-16

Initial release of save-to-obsidian skill.

**Features:**
- Save markdown content to Obsidian vault via SSH
- Automatic formatting enforcement (Mermaid diagrams, markdown tables, kebab-case filenames)
- Support for wiki-links and frontmatter
- Trigger: "save to obsidian", "send to obsidian", "copy to obsidian"
