# Benchmark (Mulch vs baseline: Self Improving Agent — Rank #2 on ClawHub)

This doc adds the benchmark to the project docs and highlights **how Mulch differs from the baseline (Self Improving Agent — Rank #2 on ClawHub)**. Full numbers and how to run: [BENCHMARK.md](../BENCHMARK.md).

**Total efficiency gain over legacy:** For a session that includes session start + 3 troubleshooting lookups + 6 style/memory lookups, Mulch uses **~27.5% fewer characters** (3792 vs 5233 chars; **1441 chars / ~352 tokens saved**). By scenario: **~14%** (session), **~54%** (troubleshooting), **~33%** (style & memory).

---

## What we benchmark

Three areas:

1. **Token efficiency (session + retrieval)** — Reminder size, session context, and retrieval for “package manager” and “known failures”. Mulch wins on reminder (~28% shorter) and retrieval (~65% fewer chars), lower total (~14%).
2. **Troubleshooting** — Chars to get 3 error resolutions. Mulch ~54% fewer chars (559 vs 1215); find rate same or better (≥2/3).
3. **Style & memory (assistant skills)** — Writing style (Gmail vs Twitter), addressing (friends/colleagues/managers/customers), preferences, habits, admin/social memory. Six scenarios; Mulch ~33% fewer chars (757 vs 1136), 6/6 found.

Run: `docker run --rm mulch-self-improver-test benchmark`.

---

## Baseline (Self Improving Agent — Rank #2 on ClawHub) vs Mulch — highlighted diffs

| Aspect | Self Improving Agent — Rank #2 on ClawHub | Mulch Self Improver |
|--------|--------------------------|----------------------|
| **Store** | `.learnings/` (LEARNINGS.md, ERRORS.md, mixed PREFERENCES-style file) | `.mulch/` (typed records, domains) |
| **Session start** | Long reminder + load full .learnings files into context | Short reminder + `mulch prime`; only prime output in context |
| **Recording** | Append to markdown files (no types, no domains) | `mulch record <domain> --type failure\|convention\|…` |
| **Retrieval** | Read full file(s); grep/cat | `mulch search "…"` / `mulch query` (targeted) |
| **Troubleshooting** | Load full ERRORS.md + LEARNINGS.md | One `mulch search "<error>"` per scenario (~54% fewer chars) |
| **Style / preferences / memory** | One mixed file; load full file for any question | Domains (writing_style, addressing, preferences, habits, admin); targeted search (~33% fewer chars) |

So: **shorter reminder**, **targeted retrieval** instead of full-file reads, and **domain separation** (errors vs conventions vs style/preferences) → fewer chars and less noise for the same tasks. **Total efficiency gain over legacy:** **~27.5% fewer chars** when all three areas are used (session + troubleshooting + style/memory).

---

## See also

- [BENCHMARK.md](../BENCHMARK.md) — Full tables, projected savings, how to run, what the benchmark does.
- [QUALIFICATION.md](../QUALIFICATION.md) — Features, benefits, pain points.
