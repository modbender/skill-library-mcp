---
name: yc-new-way
description: Apply Y Combinator’s “New Way to Build a Startup” playbook to ship fast, validate with real distribution, and iterate using data. Use when the user asks to follow “New Way”, design a 7-day startup sprint, pick a narrow wedge, build a lightweight MVP/SEO site/newsletter, set up experiments, or turn a vague idea into a testable plan with metrics, launch checklist, and weekly iteration loop.
---

# YC “New Way” (ship → distribute → learn)

## Goal
Turn an idea into **a running distribution loop** fast (days, not weeks), using the smallest product that can **measure real demand**.

## Workflow (default)
### 0) Clarify the bet (2 minutes)
Fill this sentence:
- **For [who]** with **[pain]**, we offer **[promise]** via **[channel]**, and we’ll know it works when **[metric]** hits **[threshold]**.

If missing, use `references/experiment-brief.md`.

### 1) Pick a narrow wedge
Prefer wedges that are:
- High intent (people already searching/buying)
- Clear objects (SKUs, listings, templates)
- Easy to prove with evidence (links, screenshots, timestamps)

Output:
- 1 primary wedge + 1 backup wedge
- 3 user stories

### 2) Choose one distribution channel first
Pick exactly one:
- **SEO** (content library + internal links)
- **Newsletter** (weekly digest)
- **Community** (Reddit/Discord/forums) where posting is allowed

Do **not** build more channels until one shows signal.

### 3) Ship the smallest MVP that measures
Default MVPs:
- SEO site: 10 pages (2 money pages + 8 support pages)
- Newsletter: 1 issue + signup + archive
- Tool page: 1 calculator/checklist with email capture

Include:
- Clear CTA
- Analytics
- Evidence links (avoid “AI says”)

Use `references/landing-page-checklist.md` and `references/seo-10-page-plan.md`.

### 4) Instrumentation & decision rules
Track only the fewest metrics:
- **Traffic → CTA CTR → Outbound clicks → (optional) purchases**
- Time to publish / pages per week (throughput)

Define stop/iterate rules:
- If CTR is low → fix promise/copy
- If CTR is high but no conversions → fix offer/price/trust
- If no traffic after 7 days → distribution problem (not product)

Use `references/weekly-loop.md`.

### 5) Weekly iteration loop
Every week:
1) Double down on 1 thing that worked
2) Kill 1 thing that didn’t
3) Add 1 new experiment

Keep a changelog; avoid rebuilding.

## Output templates (use these verbatim)
- Experiment brief: `references/experiment-brief.md`
- Landing page checklist: `references/landing-page-checklist.md`
- SEO 10-page plan: `references/seo-10-page-plan.md`
- Weekly loop: `references/weekly-loop.md`

## Guardrails
- **Distribution before system**: don’t over-automate until there’s signal.
- **Evidence-first**: recommendations must cite sources.
- **Narrow first**: one wedge, one channel, one metric.
- **Legal/ToS**: prefer public sources / allowed APIs; avoid bypassing logins or CAPTCHAs.
