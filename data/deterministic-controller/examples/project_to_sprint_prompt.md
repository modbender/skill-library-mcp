# Prompt Template — Convert a loose project spec into a sprint plan + queue it

Copy/paste this into your OpenClaw main session. Replace the placeholders.

---

TRIGGER=MANUAL_RECONCILE

You will take the loose project spec below and produce a deterministic sprint plan file AND queue it.

Constraints:
- Use `SPRINT_TEMPLATE.md` as the structure.
- Make every step have an objective completion condition and an Evidence/Output path.
- Do not include secrets.
- Keep steps sized to complete in one worker run.

Actions:
1) Create a sprint plan markdown at: `projects/<project-slug>/sprint-plan.md`.
2) Add a new row to `ACTIVITIES.md` → `## Project Queue (portfolio)` with:
   - `Queue State=BACKLOG`
   - `Plan Path=projects/<project-slug>/sprint-plan.md`
3) Do not arm automation.

Loose project spec:
<PASTE YOUR SPEC HERE>
