---
name: idx-cma-report
description: Generate comparative market analysis (CMA) and home valuation reports from IDX listing data and selected comparable properties. Use when a user wants to pick comps, estimate a market value range, produce seller-facing home evaluation reports, or publish an interactive CMA experience via Google Gemini Canvas or Google AI Studio.
---

# IDX CMA Report

Use this skill to turn subject-property data and IDX comparables into a defensible CMA package with:

- Structured valuation calculations
- A written report for agent/client review
- An interactive handoff prompt for Google Gemini Canvas / Google AI Studio

## Workflow

### 1. Gather Data Through IDX MCP/CLI
Use the IDX MCP/CLI skill already available in the environment to pull:

- Subject property details
- Candidate comparable listings (closed/pending/active based on user preference)

Ask the user which comps to include when the choice is ambiguous. Keep 3 to 8 comps unless the user requests otherwise.

Normalize data to JSON using the schema in `references/cma-input-schema.md`.

### 2. Build CMA Outputs
Run:

```bash
python3 scripts/build_cma.py \
  --subject subject.json \
  --comps comps.json \
  --output-dir cma-output
```

The script produces:

- `cma-output/cma_report.md` (summary report)
- `cma-output/cma_data.json` (calculation payload)
- `cma-output/interactive_local.html` (local interactive view)
- `cma-output/gemini_canvas_prompt.md` (prompt for Google tools)

### 3. Review and Explain Adjustments
Before final delivery:

- Show the comp set used
- Show estimated range and central estimate
- Explain assumptions and major adjustments in plain language
- Flag missing/low-quality fields that weaken confidence

Use `references/valuation-guidelines.md` for adjustment defaults and confidence guidance.

### 4. Publish Interactive Version in Gemini
Use `cma-output/gemini_canvas_prompt.md` as the base prompt. Then:

1. Open [Google AI Studio](https://aistudio.google.com/) or Gemini Canvas.
2. Paste the generated prompt and provide `cma_data.json`.
3. Ask for an interactive CMA web app with:
   - Comp table with sorting/filtering
   - Map-ready data fields (if lat/lng present)
   - Value-range visualization
   - Notes panel explaining adjustments
4. Request hosted/shareable output if available in the chosen Google tool.

See `references/gemini-canvas-publish.md` for a copy-ready checklist.

## Safety Rules

- Treat outputs as broker/agent CMA support, not a licensed appraisal.
- Surface data gaps, outliers, or stale comps before presenting a valuation.
- Never invent listing attributes; mark missing values as unknown.
- Keep a clear boundary between factual listing data and model assumptions.

## References

- `references/cma-input-schema.md`
- `references/valuation-guidelines.md`
- `references/gemini-canvas-publish.md`
