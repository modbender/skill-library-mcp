---
name: arxiv-batch-reporter
description: "Build the final collection report in two steps: model writes a report template, then script injects each paper's Brief Conclusion and abs URL from summary.md by arXiv-id placeholders."
---

# ArXiv Batch Reporter

Use this skill after per-paper `summary.md` files exist.

## Core Principle

The model writes report structure; scripts inject per-paper conclusion text.

## Constraint

- Per-paper text in final report must come directly from each paper's `summary.md` section `## 10. Brief Conclusion`.
- Do not paraphrase or manually rewrite this per-paper conclusion text in final report.

## Commands

Step 1: build model context bundle.

```bash
python3 scripts/collect_summaries_bundle.py \
  --base-dir /path/to/run-dir \
  --language English
```

Step 2: model writes `collection_report_template.md` under `base-dir` using placeholder lines for papers.

Step 3: render final report from template.

```bash
python3 scripts/render_collection_report.py \
  --base-dir /path/to/run-dir \
  --template-file collection_report_template.md \
  --output-file collection_report.md \
  --language English
```

## Language Parameter

- `--language` controls scaffold/inserted-label language.
- Set this parameter manually for each run.
- Default is `English` when omitted.
- Chinese aliases supported: `Chinese`, `zh`, `zh-cn`, `中文`.
- When non-English is selected (for example Chinese), generated labels/prompts are localized.

## Placeholder Syntax in Template

In each paper leaf entry, add one placeholder line containing arXiv id.

Only supported syntax (standalone line):

```text
{{ARXIV_BRIEF:2602.12276}}
```

`render_collection_report.py` replaces that one placeholder line with:

- brief conclusion text extracted from summary section 10
- generated abs URL: `https://arxiv.org/abs/<arxiv_id>`

Fallback rule: if section 10 heading is missing, use content under the last `##` heading.

## Output

- `<base-dir>/summaries_bundle.md`
- `<base-dir>/collection_report_template.md` (model-authored)
- `<base-dir>/collection_report.md` (rendered final output)

Use `references/report-format.md` for the expected report structure.
Use `references/report-example-lean4-en.md`, `references/report-example-llm-math-en.md`, and `references/report-example-multimodal-en.md` for tree-structure examples with lint-friendly spacing.

## Related Skills

This skill is a sub-skill of `arxiv-summarizer-orchestrator`.

It is intended to run after:

1. `arxiv-search-collector` (selected paper directories + metadata)
2. `arxiv-paper-processor` (per-paper `summary.md`)

This skill consumes the summary outputs from Step 2 and should be used together with Steps 1 and 2 to produce the final collection report.
