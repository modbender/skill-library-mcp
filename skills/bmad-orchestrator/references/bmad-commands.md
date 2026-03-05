# BMAD Claude Code Commands

All commands are available as `/bmad-*` slash commands in Claude Code when the `_bmad/` framework is installed.

## Phase 1: Analysis
| Command | Purpose | Produces |
|---------|---------|----------|
| `/bmad-brainstorming` | Guided brainstorming session | brainstorming-report.md |
| `/bmad-bmm-domain-research` | Domain research | Research findings |
| `/bmad-bmm-market-research` | Market research | Research findings |
| `/bmad-bmm-technical-research` | Technical research | Research findings |
| `/bmad-bmm-create-product-brief` | Capture strategic vision | product-brief.md |

## Phase 2: Planning
| Command | Purpose | Produces |
|---------|---------|----------|
| `/bmad-bmm-create-prd` | Define requirements (FRs/NFRs) | prd.md |
| `/bmad-bmm-validate-prd` | Validate PRD quality | Validation report |
| `/bmad-bmm-edit-prd` | Edit existing PRD | Updated prd.md |
| `/bmad-bmm-create-ux-design` | Design UX (if applicable) | ux-spec.md |

## Phase 3: Solutioning
| Command | Purpose | Produces |
|---------|---------|----------|
| `/bmad-bmm-create-architecture` | Technical architecture + ADRs | architecture.md |
| `/bmad-bmm-create-epics-and-stories` | Break work into epics/stories | epics.md |
| `/bmad-bmm-check-implementation-readiness` | Gate check | PASS/CONCERNS/FAIL |
| `/bmad-bmm-generate-project-context` | Generate project context | project-context.md |

## Phase 4: Implementation
| Command | Purpose | Produces |
|---------|---------|----------|
| `/bmad-bmm-sprint-planning` | Initialize sprint tracking | sprint-status.yaml |
| `/bmad-bmm-create-story` | Prepare next story | story-[slug].md |
| `/bmad-bmm-dev-story` | Implement a story | Working code + tests |
| `/bmad-bmm-code-review` | Review implementation | Approved/changes requested |
| `/bmad-bmm-correct-course` | Handle mid-sprint changes | Updated plan |
| `/bmad-bmm-automate` | Generate E2E tests (after epic) | Test suite |
| `/bmad-bmm-retrospective` | Epic retrospective | Lessons learned |
| `/bmad-bmm-sprint-status` | Check sprint status | Status report |

## Multi-Agent
| Command | Purpose |
|---------|---------|
| `/bmad-party-mode` | Multi-agent discussion (all BMAD agents debate a topic) |
| `/bmad-help` | Interactive help — what to do next |

## Quick Flow
| Command | Purpose | Produces |
|---------|---------|----------|
| `/bmad-bmm-quick-spec` | Quick tech spec | tech-spec.md |
| `/bmad-bmm-quick-dev` | Quick implementation | Working code |

## Agent-Specific Commands
Load a specific agent persona for manual interaction:
| Command | Agent Role |
|---------|-----------|
| `/bmad-agent-bmm-analyst` | Business/market analyst |
| `/bmad-agent-bmm-architect` | Technical architect |
| `/bmad-agent-bmm-dev` | Developer |
| `/bmad-agent-bmm-pm` | Product manager |
| `/bmad-agent-bmm-qa` | QA engineer |
| `/bmad-agent-bmm-sm` | Scrum master |
| `/bmad-agent-bmm-tech-writer` | Technical writer |
| `/bmad-agent-bmm-ux-designer` | UX designer |
