---
name: creative-ops-copilot
description: Turn messy client briefs into a production-ready plan for motion design/VFX projects: scope, assumptions/exclusions, deliverables matrix, schedule/milestones, review rounds, and estimate/quote. Also generate an invoice draft payload for Chris's local invoicing system (invoicing_system_2025) or export quote/invoice JSON/CSV/Markdown. Use when Chris asks to go from brief/email notes/chat logs into a clear plan + quote/invoice, or to create a repeatable project folder + docs.
---

# Creative Ops Copilot

## What to do

1) Ask for (or infer) the input brief:
- Paste text directly, or
- Provide a file path to a brief/email/thread export.

2) Produce these outputs (always):
- `docs/creative-ops/plan.md` (client-ready)
- `docs/creative-ops/estimate.json` (structured line items)
- `docs/creative-ops/invoice-draft.json` (ready for API import later)

3) If Chris wants it, also:
- Create a project folder skeleton (AE/C4D/Octane-friendly) with a `docs/README.md`.
- POST the invoice draft to the local invoicing API (only if base URL is configured and Chris says “push it”).

## Canonical output structure (plan.md)

- Project summary (one paragraph)
- Goals / Success criteria
- Deliverables (matrix)
  - Format, duration, aspect ratios, versions, audio deliverables
- Workflow assumptions
  - what’s included, what’s not, number of review rounds
- Open questions (what you still need answered)
- Production plan
  - phases + milestones + review windows
- Risks / dependencies
- Estimate
  - line items + hours + rate + subtotal + contingency
- Next actions

## How to generate reliably

Prefer generating structured data first, then render it:

1) Extract entities
- Client name
- Project name
- Deadline/date constraints
- Deliverables list
- Constraints (brand, legal, footage supply, approvals)

2) Decide the production approach
- Template-driven vs bespoke
- 2D AE vs 3D C4D vs mixed

3) Estimate with motion/VFX realism
- Prepro (briefing, styleframes, boards)
- Production (anim, 3D, comp)
- Audio/music/licensing (if applicable)
- Renders, exports, versioning
- PM/admin buffer

## Scripts (recommended)

Use the bundled script to create consistent outputs:

```powershell
python skills/creative-ops-copilot/scripts/creative_ops_copilot.py --brief "<paste brief>" --out .
```

If the brief is a file:

```powershell
python skills/creative-ops-copilot/scripts/creative_ops_copilot.py --brief-file "C:\path\to\brief.txt" --out .
```

To also create a project skeleton:

```powershell
python skills/creative-ops-copilot/scripts/creative_ops_copilot.py --brief "..." --out . --skeleton
```

To attempt pushing the invoice draft to your local invoicing API (only if configured):

```powershell
python skills/creative-ops-copilot/scripts/creative_ops_copilot.py --brief "..." --out . --push-invoice
```

## Configuration

Optional config file:
- `skills/creative-ops-copilot/references/config.example.json`

Copy to:
- `skills/creative-ops-copilot/references/config.json`

Then edit:
- `invoicingApi.baseUrl`
- `invoicingApi.apiKey` (if needed)
- `rateCard` defaults

## Notes

- Keep outputs concise, clean, and client-ready.
- When anything is missing/ambiguous, surface it under **Open questions** instead of guessing.
