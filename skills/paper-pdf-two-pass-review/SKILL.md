---
name: cvpr-pdf-two-pass-review
description: Analyze uploaded CVPR paper PDFs with a strict two-pass workflow. First pass extracts verifiable facts with page/section/figure/table evidence only. Second pass produces a 2000-3000 Chinese research critique grounded in those facts. Use when the user uploads a paper PDF and asks for deep interpretation, critical review, reproducibility assessment, or PhD-level reading notes.
---

# CVPR PDF Two-Pass Review

## Overview

Run a deterministic two-pass paper analysis workflow on an uploaded PDF.
Prioritize evidence-grounded outputs and reduce hallucinations by separating fact extraction from interpretation.

## Workflow

1. Confirm the user has uploaded the PDF in the current chat. If not, ask them to upload it first.
2. Load and execute prompt in `references/round1.md` to produce a structured fact sheet.
3. Load and execute prompt in `references/round2.md` using only round-1 facts plus PDF evidence.
4. Enforce evidence tags for core claims: `[Evidence: p.X, Sec.Y, Fig/Table Z]`.
5. If any required information is missing, explicitly state `Not provided in paper` or `Insufficient evidence`.

## Output Rules

- Keep analysis strictly based on uploaded PDF content.
- Do not introduce external papers, benchmarks, or assumptions unless user explicitly asks.
- Keep language concise and technical.
- Preserve required length in pass 2: 2000-3000 words or characters as requested by the prompt.

## References

- Round 1 prompt: `references/round1.md`
- Round 2 prompt: `references/round2.md`
