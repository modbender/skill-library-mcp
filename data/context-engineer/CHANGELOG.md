# Changelog

## [1.0.0] - 2026-02-19

### Added
- `analyze` command — scan workspace context files, count tokens, identify bloat, score efficiency
- `audit-tools` command — parse tool definitions, identify redundant/overlapping tools, measure overhead
- `report` command — comprehensive terminal-rendered context engineering report
- `compare` command — before/after snapshot comparison with projected token savings
- Redundancy detection for duplicate lines, repeated phrases, excessive whitespace
- Efficiency scoring with letter grades (A+ through F)
- Context budget visualization showing static vs available token allocation
- Per-file and per-category token breakdown with bar charts
- Snapshot save/load for tracking optimization progress over time
- Unicode box-drawing terminal output with ANSI colours
- Approximate token estimation (~4 chars/token, stdlib-only)
