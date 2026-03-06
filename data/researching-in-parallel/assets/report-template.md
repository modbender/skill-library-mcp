# Research Report: {{TOPIC}}

*{{DATE}}*

---

## About This Report

**Workflow:** Parallel AI research synthesis (researching-in-parallel skill v1.4)

**What the AI did:** Three AI sub-agents independently researched this topic with
distinct analytical briefs (breadth survey, critical analysis, evidence assessment).
A dedicated synthesis sub-agent read all three outputs and produced this report.

**What the human did:** {{HUMAN_CONTRIBUTION — e.g. "Provided the research topic and
angle. Reviewed the final output."}}

**Models used:**
- Breadth pass: {{MODEL_BREADTH — copied from first line of research-breadth-*.md}}
- Critical pass: {{MODEL_CRITICAL — copied from first line of research-critical-*.md}}
- Evidence pass: {{MODEL_EVIDENCE — copied from first line of research-evidence-*.md}}
- Synthesis: {{MODEL_SYNTHESIS — this agent's own model ID}}

**Important caveats:** AI-generated research may contain errors, gaps, and hallucinated
citations. Sources in the bibliography should be independently verified before use in
decisions or published work. Sub-agent outputs are saved to your workspace for review.

---

## Report Body

---

## Research Methodology

**Passes conducted:** 3 (breadth survey, critical analysis, evidence assessment) + synthesis  
**Sources collected:** {{N}} across all passes; {{N}} unique after deduplication  
**Single-pass-only sources (verify before citing):** {{N}}  
**Bibliography:** `bibliography-{{TOPIC_SLUG}}-{{DATE}}.md`  
**Sub-agent outputs:**
- `research-breadth-{{TOPIC_SLUG}}-{{DATE}}.md`
- `research-critical-{{TOPIC_SLUG}}-{{DATE}}.md`
- `research-evidence-{{TOPIC_SLUG}}-{{DATE}}.md`

**Synthesis approach:** Cross-pass consensus weighted more heavily than single-pass
findings. Contradictions preserved rather than resolved. Evidence pass ratings used
to weight claims from the breadth and critical passes.

*This report was produced by AI and has not been independently fact-checked.
Verify critical claims before use.*
