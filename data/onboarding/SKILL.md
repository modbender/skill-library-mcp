---
name: Onboarding
description: Design user onboarding flows that maximize activation and time-to-value.
metadata: {"clawdbot":{"emoji":"🚀","os":["linux","darwin","win32"]}}
---

## Define Activation First

Answer before designing anything:
- What specific action = user got value?
- What % of signups currently reach it?
- What's the minimum path to get there?

If you can't answer these, onboarding will optimize the wrong thing.

## Measure the Funnel

Create this table for current state:
| Step | Users | Drop-off |
|------|-------|----------|
| Signed up | 100% | - |
| Step 2 | ?% | ?% |
| Step 3 | ?% | ?% |
| Activated | ?% | ?% |

Biggest drop-off = focus there first. Everything else is distraction.

## Signup Form

At signup, require ONLY: email + password.
Everything else: defer until after first value delivered.

For each additional field, calculate: how many users lost × LTV = cost of that field.

## Segmentation Question

One question only, immediately after signup:
"What's your main goal?" with 3-4 options.

Route to different:
- First action to complete
- Empty state messaging
- Email sequence

More than 4 paths = complexity without benefit.

## Checklist Pattern

Structure:
- 4-6 items maximum
- First item already complete when shown (quick win psychology)
- Items ordered by value delivered, not logical sequence
- Persists across sessions
- Completion reward visible

Format: action verb + outcome
✓ "Create your first project" 
✗ "Projects"

## Empty State Formula

Every empty screen needs:
1. What will appear here (1 sentence)
2. Visual of populated state or example
3. ONE action button (primary style)

Pre-populated templates > blank slate.

## Email Sequence

| Day | Trigger | Content |
|-----|---------|---------|
| 0 | Signup | Welcome + single quick win CTA |
| 1 | Not activated | Reminder + "here's how" |
| 3 | Not activated | Social proof / success story |
| 7 | Not activated | Feature highlight |
| 14 | Inactive | "We miss you" + incentive |

Stop sequence immediately when user activates.

## Tooltips vs Modals

- **Tooltip**: single UI element explanation, non-blocking
- **Modal**: requires decision, blocks everything
- **Tour**: max 3-5 steps or users skip

Never repeat to returning users.
Trigger contextually, not on every login.

## Metrics

Track weekly:
- Signup → Activation rate
- Time to activate (median)
- Drop-off by step
- Day 1, Day 7 retention: activated vs non-activated

Activated users should retain 2-3x better. If not, activation definition is wrong.

## Common Failures

- Asking for info before showing value—user hasn't bought in
- Tour showing everything—overwhelms, skip rate high
- Same onboarding for all segments—relevance drives completion
- No follow-up emails—user closes tab and forgets
- Blocking features behind upgrade before value demonstrated
