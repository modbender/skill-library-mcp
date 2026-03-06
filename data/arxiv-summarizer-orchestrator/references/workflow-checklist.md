# Workflow Checklist

## A. Collection

- [ ] Run initialization script and confirm run dir created.
- [ ] Set workflow language parameter explicitly and pass it to collector scripts.
- [ ] Draft multiple focused queries from original topic.
- [ ] Fetch one JSON list per query in serial mode (no parallel API calls).
- [ ] Use conservative fetch controls (`--min-interval-sec`, retry args) and avoid `--force` unless needed.
- [ ] Prefer default run-local rate-state (`<run_dir>/.runtime/*`); override `--rate-state-path` only when needed.
- [ ] For each query list, decide keep indexes manually.
- [ ] Merge and dedupe selections.
- [ ] If relevance is weak or count is insufficient, run another Stage-A round and re-merge with `--incremental` (drop weak labels by empty keep list).
- [ ] Confirm per-paper metadata directories exist.

## B. Per-paper Processing

- [ ] Choose paper processing mode: `subagent_parallel` (default) or `serial`.
- [ ] If parallel mode, keep `max_parallel_papers <= 5` by default.
- [ ] Optional for many papers: run `arxiv-paper-processor/scripts/download_papers_batch.py` first.
- [ ] Use one `arxiv-paper-processor` skill run per paper directory.
- [ ] If parallel mode, launch `arxiv-paper-processor` runs in batches and keep concurrent count `<= max_parallel_papers`.
- [ ] If serial mode, run `arxiv-paper-processor` one paper at a time.
- [ ] If `summary.md` already exists and is complete for a paper dir, skip that paper.
- [ ] If source/PDF already exists in a paper dir, skip download and move to reading/summarization.
- [ ] If artifacts are missing, download source for each paper.
- [ ] Fallback to PDF when source is unusable.
- [ ] Read content manually.
- [ ] Write one `summary.md` per paper in required format and selected language.
- [ ] Confirm summaries are manually synthesized from full-text reading, not script-extracted snippets.

## C. Batch Reporting

- [ ] Build `summaries_bundle.md` with target language.
- [ ] Write `collection_report_template.md` (overview + tree + final synthesis) manually.
- [ ] In each paper leaf entry, add one standalone placeholder line: `{{ARXIV_BRIEF:<arxiv_id>}}`.
- [ ] Run `arxiv-batch-reporter/scripts/render_collection_report.py` to generate `collection_report.md`.
- [ ] Verify all placeholders are resolved.

## D. Quality Checks

- [ ] Final paper count matches target intent.
- [ ] Category hierarchy is understandable and not over-complex.
- [ ] Every listed paper has injected brief conclusion text + arXiv abs URL.
- [ ] Final synthesis paragraph is concise and grounded.
- [ ] Intermediate markdown files and final report all match the selected language.
