# Changelog

## [1.0.1] - 2026-02-15

### Added
- Comprehensive README with installation and usage instructions
- SOUL.md integration example with copy-paste ready patterns
- Testing guidance and expected behavior metrics
- CHANGELOG for version tracking

### Improved
- Better documentation structure for easy adoption
- Clear before/after examples
- Troubleshooting section

## [1.0.0] - 2026-02-15

### Added
- Initial release
- 8 core override patterns for maintaining agent autonomy
- The CTO Test heuristic for decision-making
- Regression symptoms checklist
- Full SKILL.md with implementation guidance
- README with quick start and usage examples
- Integration example for SOUL.md
- Real-world metrics from production use

### Context
Created from lessons learned during autonomous agent development (Zoro, Feb 2026). Patterns emerged from actual regression events where the agent would revert to chatbot-style behavior after session restarts, despite having full autonomy and tooling available.

### Key Insight
Base LLM training pushes toward safe, permission-seeking behavior. Without **specific, actionable override patterns**, agents drift back to generic AI responses. This skill provides those patterns.
