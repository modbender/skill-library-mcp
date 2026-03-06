# Changelog

## 1.0.3 — 2026-02-19

### Fixed
- ✅ **Command naming consistency**: Standardized all references from `pmp-agent` to `pmp-agentclaw`
  - SKILL.md: Updated `npx pmp-agent health-check` → `npx pmp-agentclaw health-check`
  - SKILL.md: Removed references to non-existent CLI commands (`generate-wbs`, `generate-gantt`)
  - CLI index.ts: Updated help text and examples to use `pmp-agentclaw` consistently
  - CLI now shows direct command aliases (`pm-evm`, `pm-risk`, `pm-velocity`, `pm-health`)
- ✅ **Instruction scope clarity**: Confirmed runtime instructions focus on PM tasks and reference templates/configs from skill directory
- ✅ **File access documentation**: CLI reads user-provided files (--file or projectDir) as expected behavior

## 1.0.2 — 2026-02-19

### Security Fix
- 🔒 **Fixed SKILL.md metadata format**: Converted from inline JSON to proper YAML structure
  - Before: `metadata: {"openclaw": {...}}` (JSON string in YAML)
  - After: Proper YAML nested structure with `metadata:\n  openclaw:\n    emoji: ...`
  - This ensures compatibility with OpenClaw's YAML parser

## 1.0.1 — 2026-02-19

### Bug Fixes
- ✅ Added missing templates (wbs.md, gantt-schedule.md, change-request.md, lessons-learned.md, evm-dashboard.md, communications-plan.md)
- ✅ Added missing configs (communications.json, stakeholder-analysis.json)
- ✅ Fixed install metadata mismatch in SKILL.md
- ✅ Synced all files between Desktop and live locations

## 1.0.0 — 2026-02-19

### Copyright Compliance Update
- ✅ Removed all PMBOK/PMI-branded references
- ✅ Rebranded from "PMP-certified" to "AI project management assistant"
- ✅ Added DISCLAIMER.md with clear legal notices
- ✅ Updated package.json description to generic terms
- ✅ Updated README.md to remove copyrighted language
- ✅ Updated skill.json framework description
- ✅ Created independent implementation with academic references

### Features
- **Core Calculations:**
  - Earned Value Management (EVM) — CPI, SPI, EAC, TCPI
  - Risk scoring — 5×5 Probability × Impact matrix
  - Sprint velocity tracking — Rolling average forecasting
  - Project health checks

- **Templates:**
  - Project Charter
  - Work Breakdown Structure (WBS)
  - Risk Register
  - RACI Matrix
  - Status Report
  - Sprint Planning
  - Lessons Learned

- **Multi-Agent:**
  - RACI-based orchestration
  - Hub-and-spoke pattern
  - Supports 26+ agent teams

- **Methodologies:**
  - Predictive (traditional waterfall)
  - Adaptive (Agile/Scrum)
  - Hybrid approaches

### Technical
- TypeScript implementation
- Zero runtime dependencies
- Compiled to JavaScript (dist/)
- CLI + API access

### Legal
- MIT License
- Independent from PMI/PMBOK
- Uses public domain formulas only
