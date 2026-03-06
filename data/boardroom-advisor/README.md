# Boardroom Advisor Council

**Category:** Productivity  
**Price:** $9  
**Author:** Carson Jarvis ([@CarsonJarvisAI](https://twitter.com/CarsonJarvisAI))

---

## What It Does

Boardroom Advisor gives your AI agent a virtual board of four world-class strategic advisors. When you face a major business decision, the board deliberates for you — two full rounds of argument and rebuttal — then produces a decision brief, interactive dashboard, and a clear recommendation.

**The four advisors:**
- **Donald Miller** (StoryBrand) — narrative clarity, messaging, customer story
- **Seth Godin** — smallest viable market, permission, long-term brand
- **Alex Hormozi** — offer math, cash flow, value stacking, action
- **Daniel Priestley** — personal brand, ecosystem, oversubscribed demand

---

## What's Different

Most "advisor" prompts give you one perspective. Boardroom Advisor runs a real deliberation:

- **Round 1:** Each advisor argues their full position with projections
- **Round 2:** Each advisor rebuts the others — votes can change
- **Result:** A decision brief, interactive HTML dashboard, and a definite recommendation

You don't get four answers. You get one — after they've fought it out.

---

## What's Included

| File | Purpose |
|------|---------|
| `SKILL.md` | Full agent instructions for running the board |
| `references/openrouter-board-model.md` | Config for running the board on Claude Opus (optional) |

---

## Quick Start

### 1. Load the skill

Add `SKILL.md` to your agent's skills directory. Your OpenClaw agent will load it when triggered.

### 2. Trigger the board

```
"Consult the board on whether to raise prices by 30%."
"Run a quick boardroom on: should we add a free tier?"
"Get the board's view on hiring a head of growth now vs. in 6 months."
```

### 3. (Optional) Run on a stronger model

Add `OPENROUTER_API_KEY` to your `.env` for Claude Opus 4.6 quality reasoning. See `references/openrouter-board-model.md` for config snippets.

---

## Example Output

```
FINAL VOTES
Miller: YES → YES (unchanged)
Godin: NO → CONDITIONAL (changed — if you keep the free tier)
Hormozi: YES → YES (unchanged)
Priestley: CONDITIONAL → YES (changed — liked Miller's narrative point)

WHO CHANGED: Godin softened after Hormozi's margin math. Priestley moved after Miller argued identity.
BIGGEST FIGHT: Godin vs. Hormozi on whether margins matter more than tribe trust.
SHARPEST INSIGHT: "You don't have a pricing problem. You have a positioning problem." — Miller

MY RECOMMENDATION: Raise prices. Run a 30-day parallel test on a new customer segment first.
The math supports it, the brand supports it, and Godin's concern dissolves if you keep a genuine free entry point.
```

---

## Deliverables Per Session

1. `decision-brief.md` — Full written brief with all arguments, rebuttals, and synthesis
2. `dashboard.html` — Interactive HTML with sliders for key assumptions
3. `decision-brief-print.html` — Print → PDF ready version (optional)

---

## Requirements

- OpenClaw agent with any model
- `OPENROUTER_API_KEY` (optional, for Claude Opus quality)

---

## Built By

Carson Jarvis — AI operator, builder of systems that ship.  
Follow the build: [@CarsonJarvisAI](https://twitter.com/CarsonJarvisAI)  
More skills: [larrybrain.com](https://larrybrain.com)
