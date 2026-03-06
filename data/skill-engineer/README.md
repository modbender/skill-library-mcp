# skill-engineer

Design, test, review, and maintain agent skills for OpenClaw systems. Provides comprehensive lifecycle management for agent skills, including validation, quality assurance, and integration testing.

## Overview

This skill enables systematic development and maintenance of agent skills following Anthropic's best practices. It includes:

- **Progressive disclosure** design patterns (YAML frontmatter → SKILL.md → references/)
- **Quality scoring system** for skill evaluation (completeness, clarity, balance, integration)
- **Tool selection validation** to prevent common execution errors
- **Self-play testing** protocols for skill validation
- **Agent kit audit** procedures for maintaining skill ecosystem health

## Requirements

This skill uses a **multi-agent architecture** with three roles: Designer, Reviewer, and Tester. The orchestrating agent must be able to **spawn subagents** (e.g., via `sessions_spawn` in OpenClaw). Each role runs as a separate subagent session to enforce separation of concerns — builders do not evaluate their own work.

**Minimum setup:**
- An OpenClaw agent with subagent spawning capability (main session or top-level agent)
- At least 3 subagent sessions available per skill design cycle
- Subagents cannot be the orchestrator — the orchestrator must be a session that can spawn others

**Single-agent fallback:** If subagent spawning is unavailable, the skill can run in role-based mode where one agent switches between Designer/Reviewer/Tester phases sequentially. This provides less rigorous separation but is functional.

## Installation

Copy the skill into your OpenClaw skills directory:

```bash
cp -r skill-engineer ~/.openclaw/skills/
```

Or install from ClawhHub (when available).

## Usage

See [SKILL.md](SKILL.md) for detailed documentation on:
- Multi-agent architecture and orchestration loop
- Skill design principles and patterns
- Quality standards and scoring rubric (33 checks)
- Testing protocols (trigger, functional, edge case)

## Structure

- **SKILL.md** - Main skill documentation with comprehensive workflows
- **skill.yml** - Skill metadata and trigger configuration
- **tests/** - Test trigger configurations for validation
- **scripts/** - Automation scripts (if any)
- **CHANGELOG.md** - Version history and updates

## Quality Scorecard

| Category | Score | Details |
|----------|-------|---------|
| Completeness (SQ-A) | 8/8 | Full lifecycle coverage, clear workflows, all templates provided |
| Clarity (SQ-B) | 5/5 | Unambiguous instructions, examples, edge cases addressed |
| Balance (SQ-C) | 5/5 | Appropriate workload distribution, scripts + AI balanced |
| Integration (SQ-D) | 5/5 | Standard formats, compatible with OpenClaw agent kit |
| Scope (SCOPE) | 3/3 | Clean boundaries, no scope creep into adjacent systems |
| OPSEC | 2/2 | No violations (test file has intentional negative examples) |
| References (REF) | 3/3 | Anthropic guide cited with URLs, all claims traceable |
| Architecture (ARCH) | 2/2 | Designer/Reviewer/Tester separation enforced |
| **Total** | **33/33** | |

*Scored by skill-engineer Reviewer (iteration 3, multi-agent self-review pipeline)*

## License

MIT
