# QA Defect Loop

For each plan step:
1. Run the mapped check command from verification matrix.
2. If check fails:
   - mark step BLOCKED in mid-summary,
   - capture defect details (step, command, error, probable cause),
   - fix implementation,
   - re-run the same check.
3. Move to next step only after PASS.

Rules:
- No verification evidence -> no done.
- If preferred test runner is unavailable, use fallback (e.g., unittest) and record it explicitly.