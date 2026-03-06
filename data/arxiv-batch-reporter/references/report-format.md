# Collection Report Template Format

Write one template file under run `base-dir`, e.g. `collection_report_template.md`.
Then render final report with:

```bash
python3 scripts/render_collection_report.py \
  --base-dir /path/to/run-dir \
  --template-file collection_report_template.md \
  --output-file collection_report.md \
  --language English
```

## Required Sections

### 1. Unified Overview

Include:

- topic
- selected time range
- target paper count range
- actual paper count

### 2. Hierarchical Classification (Tree-like)

Requirements:

- Use moderate depth (not too flat, not too deep).
- Avoid putting all papers in one bucket.
- Avoid over-fragmenting into many singleton categories without meaning.
- Good default depth: `domain -> subtopic -> paper list`.
- For each paper entry in a leaf category, include:
  - `paper title`
  - one placeholder line with arXiv id
- Do not include local filesystem paths (for example absolute paper directory paths).
- Do not manually write/paraphrase per-paper conclusion text.
- Do not manually write per-paper arXiv URL in template.

Placeholder line format (standalone line):

```text
{{ARXIV_BRIEF:2602.12276}}
```

Render behavior:

- The placeholder line is replaced by:
  - `Brief Conclusion`/`简要结论`: direct text from `summary.md` section `## 10. Brief Conclusion` (or localized equivalent).
  - `arXiv` URL: `https://arxiv.org/abs/<arxiv_id>`.
- Fallback: if section 10 heading is missing, use content under the last `##` heading in `summary.md`.

### 3. Concise Overall Synthesis

Requirements:

- Place this after the full tree.
- Summarize key themes and major differences across categories.
- Keep concise.

## Category Granularity Guidance

- Keep category names semantically meaningful.
- Keep category depth readable for humans.
- If a category has only one weakly related paper, merge or rename categories.

## Markdown Lint Note

- Use blank lines before and after every list block.
- This avoids markdownlint `MD032/blanks-around-lists` violations.

## Examples

- Lean 4 / formalization example: `references/report-example-lean4-en.md`
- LLM for Math example: `references/report-example-llm-math-en.md`
- Multimodal LLM research example: `references/report-example-multimodal-en.md`

## Language

Follow the language requested by workflow parameter (default English).
