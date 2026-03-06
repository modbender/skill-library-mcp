---
name: Home Renovation
slug: home-renovation
version: 1.0.1
changelog: Added clearer budget safety guidance for change orders and contingency planning.
homepage: https://clawic.com/skills/home-renovation
description: Plan, budget, and manage home renovation projects including contractor coordination, timeline tracking, and cost estimation.
metadata: {"clawdbot":{"emoji":"🏠","requires":{"bins":[]},"os":["linux","darwin","win32"],"configPaths":["~/home-renovation/"]}}
---

## Setup

On first use, read `setup.md` for integration guidelines. Create `~/home-renovation/` if it doesn't exist.

## When to Use

User plans a home renovation or remodel. Agent tracks budgets, timelines, and contractor coordination. User needs help evaluating quotes, planning phases, or managing multiple trades.

## Architecture

Memory lives in `~/home-renovation/`. See `memory-template.md` for structure.

```
~/home-renovation/
├── memory.md          # Status + active projects overview
├── projects/          # Per-project details and tracking
│   └── {project}.md   # Budget, timeline, contractors, notes
└── archive/           # Completed projects
```

## Quick Reference

| Topic | File |
|-------|------|
| Setup guide | `setup.md` |
| Memory template | `memory-template.md` |
| Project types | `projects.md` |
| Contractor evaluation | `contractors.md` |
| Renovation phases | `phases.md` |

## Core Rules

### 1. Project-Centric Memory
Each renovation gets its own file in `projects/`. Track:
- Budget: original estimate vs actual spend
- Timeline: planned vs actual dates
- Contractors: who, contact, status, notes
- Decisions: what was decided and why

### 2. Budget Reality Check
When user shares a quote or estimate:
- Ask square footage and scope details
- Compare to typical ranges (see `projects.md`)
- Flag if significantly above/below normal
- Never guarantee prices — always "typically ranges from..."

### 3. Phase-Based Planning
Renovations follow a sequence. See `phases.md` for details:
1. Planning & permits
2. Demolition
3. Structural/rough-in (electrical, plumbing, HVAC)
4. Insulation & drywall
5. Finishes (paint, flooring, fixtures)
6. Final inspection & punch list

Wrong order = costly rework. Always verify sequence before starting.

### 4. Contractor Coordination
When multiple trades involved:
- Confirm who handles permits
- Establish communication expectations
- Document verbal agreements immediately
- Track payment schedule vs work completed

### 5. Scope Creep Defense
Every change request:
- Get written quote before approving
- Update budget tracker
- Recalculate remaining contingency after each approved change order
- Assess timeline impact
- Document decision and rationale

### 6. Decision Documentation
For every major decision, record:
- What options were considered
- Why this option was chosen
- Cost and timeline impact
- Date decided

This prevents revisiting decisions and provides context for future projects.

### 7. Progress Updates
When user mentions progress:
- Update project timeline
- Check if on budget
- Note any issues or delays
- Celebrate completed milestones

## Common Traps

- **Paying too much upfront** → Never more than 30% deposit. Balance tied to milestones.
- **Verbal agreements** → Get everything in writing. "They said" has no legal weight.
- **Skipping permits** → Insurance won't cover unpermitted work. Resale problems.
- **Cheapest bid** → Often means corners cut or change orders coming. Middle bid often safest.
- **No contingency** → Budget 15-20% extra. Something always comes up.
- **Scope creep silence** → Every "while we're at it..." adds cost. Track it.
- **Wrong sequence** → Painting before electrical = repaint. Plan phases correctly.

## Cost Estimation Guidelines

**These are rough ranges only. Always get local quotes.**

| Project Type | Low | Mid | High | Notes |
|-------------|-----|-----|------|-------|
| Kitchen remodel | $15K | $40K | $80K+ | Cabinets drive cost |
| Bathroom remodel | $8K | $20K | $40K+ | Tile and fixtures vary |
| Flooring (per sqft) | $3 | $8 | $15+ | Material + labor |
| Roof replacement | $8K | $15K | $30K+ | Size and material |
| Window replacement (each) | $300 | $700 | $1,500+ | Standard vs custom |
| Deck/patio | $5K | $15K | $40K+ | Material matters |
| Painting interior | $2K | $5K | $10K+ | Size and prep work |

**Cost multipliers:**
- HCOL area (SF, NYC, LA): 1.5-2x
- Historic home: 1.3-1.5x
- Expedited timeline: 1.2-1.5x
- Custom/high-end materials: 2-3x

## Red Flags to Watch

**Contractor warning signs:**
- Won't provide references
- Demands large deposit (>30%)
- No written contract
- Can start "tomorrow" (why are they free?)
- Much lower than other bids
- Pressures quick decision
- No insurance/license proof
- Won't pull permits

**Project warning signs:**
- Budget already maxed before starting
- No contingency fund
- Timeline too aggressive
- Too many simultaneous projects
- Unclear scope document

## Security & Privacy

**Data that stays local:**
- Project details in `~/home-renovation/`
- Contractor contact info you provide
- Budget and timeline tracking

**This skill does NOT:**
- Access financial accounts
- Contact contractors directly
- Make purchases or payments
- Access files outside `~/home-renovation/`

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `money` — Personal finance and budgeting
- `projects` — General project tracking
- `plan` — Planning and goal setting

## Feedback

- If useful: `clawhub star home-renovation`
- Stay updated: `clawhub sync`
