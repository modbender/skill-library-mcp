# Changelog

## [1.0.0] - 2026-02-06

### Added
- Initial release
- SKILL.md with comprehensive documentation
- Templates for CHECKS and ANSWERS files
- init.sh script for workspace setup
- add-check.sh script for interactive check creation
- Real-world example (Prometheus, 23 checks)
- README for quick start
- package.json for ClawHub compatibility

### Philosophy
- Test behavior, not just memory recall
- Catch "silent degradation" early
- Inspired by aviation pre-flight checklists
- Self-diagnostic capability for agents

### Files Included
- Templates: Blank CHECKS and ANSWERS templates
- Scripts: init.sh, add-check.sh
- Examples: Working 23-check system from Prometheus
- Documentation: SKILL.md, README.md

### Integration
- Works with OpenClaw workspace structure
- Integrates with AGENTS.md
- Compatible with memory system (MEMORY.md, daily notes)

### Use Cases
- Agent behavioral verification after session start
- Post-update consistency checks
- Memory vs behavior drift detection
- Self-diagnostic on demand

### Future Plans
- Automated test runner (run-checks.sh)
- CI/CD integration examples
- Additional check templates
- Multi-profile support
- Community check library
