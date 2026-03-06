# Summary Format Reference

Write `<paper_dir>/summary.md` with this exact section layout:

1. `## 1. Paper Snapshot`
2. `## 2. Research Objective`
3. `## 3. Method Overview`
4. `## 4. Data and Evaluation`
5. `## 5. Key Results`
6. `## 6. Strengths`
7. `## 7. Limitations and Risks`
8. `## 8. Reproducibility Notes`
9. `## 9. Practical Takeaways`
10. `## 10. Brief Conclusion`

## Mandatory Notes

- Write the whole `summary.md` in the workflow-selected language.
- Keep section numbering (`## 1.` ... `## 10.`) but localize section titles and body text to the selected language.
- Section 10 should be a fuller mini-conclusion (3-4 sentences, similar information density to an abstract-style wrap-up).
- Section 10 must include what the paper does, the main method, how evaluation is conducted, and what results are reported.
- Section 10 should include paper-specific detail rather than generic wording (for example, if the paper builds a pipeline, mention its key pipeline components).
- Base the write-up on full-text reading from source/PDF plus metadata.
- Keep claims grounded in paper content; avoid generic statements.
- Do not use scripts, regex, or snippet extraction to auto-compose section text.
- Match the length and specificity shown in `references/summary-example-en.md` and `references/summary-example-zh.md`.

## Minimal Snapshot Fields

In section 1 include:

- Use these exact field names (same spelling and capitalization):
  - `ArXiv ID`
  - `Title`
  - `Authors`
  - `Publish date`
  - `Primary category`
  - `Reading basis`
- `Reading basis` value must be `source` or `pdf` (you may append a short path/detail note in parentheses).

Example snapshot block:

```markdown
- ArXiv ID: 2602.00528
- Title: Example Paper Title
- Authors: Alice A., Bob B.
- Publish date: 2026-02-01
- Primary category: cs.AI
- Reading basis: source (source/source_extract/main.tex)
```
