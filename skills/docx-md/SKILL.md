---
name: docx-md
description: |
  Low-level docx format tool for AI document review. Three operations: (1) read docx → output compact Markdown or JSON; (2) apply edits JSON back to docx (tracked revisions and comments); (3) finalize (accept revisions, remove comments). Markdown output saves tokens vs full JSON. Use when raw .docx read/write is needed. For full contract review workflow, use contract-review-workflow which invokes this tool.
---

# Word DOCX (OOXML) – docx-md

## Overview

Three entry points: **Read** – output compact Markdown (default, token-efficient) or full JSON; **Modify** – apply AI-returned edits to the docx; **Finalize** – accept all revisions and remove all comments. Implemented via OOXML (ZIP + XML). No commercial Word libraries required.

## Workflow

| Goal | Action |
|------|--------|
| **Get document for AI** | **Read**: run read script → Markdown (default) or JSON. Markdown includes `<!-- b:N -->` blockIndex markers for edit targeting. |
| **Apply AI edits to docx** | **Modify**: run apply script with docx + edits JSON → new docx with track changes and comments. |
| **Deliver final version** | **Finalize**: run finalize script → new docx with no revisions/comments. |

## LLM-oriented pipeline

1. **Read** – Parse docx; output **Markdown** (default) or JSON. Markdown uses `<!-- b:N -->` prefix per block; revisions: `{+inserted+}` `{-deleted-}`; comments: `[comment: text]`.
2. Send the output + task prompt to the model; **require the model to output only the edit JSON**: `blockIndex`, `originalContent`, `content`, `basis` .
3. **Modify** – Script infers op from `blockIndex`, `originalContent`, `content`, `basis`; converts to OOXML (`w:ins` / `w:del` / comment anchors), then write back to Word.
4. **Finalize** – When the user confirms, run finalize to accept all revisions and remove all comments.

See [references/llm-pipeline.md](references/llm-pipeline.md) for the Markdown format, JSON schema, and edit format.

## 1. Read

- Parse `word/document.xml` (`w:body` only) and `word/comments.xml`.
- Output **Markdown** (default) or **JSON**. Markdown is compact and token-efficient.

**Script**: `scripts/read_docx.py`

```bash
# Default: Markdown output (token-efficient)
python3 skills/docx-md/scripts/read_docx.py document.docx
python3 skills/docx-md/scripts/read_docx.py document.docx -o result.md

# JSON output (full structure)
python3 skills/docx-md/scripts/read_docx.py document.docx -f json -o result.json
```

**Options**:
- `-o`, `--output` – Output path (default: stdout)
- `-f`, `--format` – `md` (default) or `json`

## 2. Modify

- **Input**: docx path + edit JSON `{ modifications: [{ blockIndex, originalContent, content, basis }] }` (same `blockIndex` as read output).
- **Flow**: Convert JSON to OOXML (`w:ins` / `w:del` / comments), then write back to Word.

**Script**: `scripts/apply_edits_docx.py`. Use `-` as edits file to read JSON from stdin.

```bash
python3 skills/docx-md/scripts/apply_edits_docx.py document.docx edits.json -o output.docx
python3 skills/docx-md/scripts/apply_edits_docx.py document.docx - -o output.docx  # stdin
```

**Options**: `--author` (default: "Review")

## 3. Finalize

- Accept all revisions (flatten to final text), remove all comments. Save as new docx.
- Uses `docx-revisions` to accept revisions (preserves encoding), then removes comment markup via regex on raw bytes.

**Script**: `scripts/finalize_docx.py`

**Requires**: `pip install docx-revisions` (see `requirements.txt`)

```bash
python3 skills/docx-md/scripts/finalize_docx.py input.docx -o output.docx
```

## Resources

### scripts/

- **read_docx.py** – Read: `python3 scripts/read_docx.py document.docx [-o out.md] [-f md|json]`
- **apply_edits_docx.py** – Modify: `python3 scripts/apply_edits_docx.py document.docx edits.json -o output.docx`
- **finalize_docx.py** – Finalize: `python3 scripts/finalize_docx.py input.docx -o output.docx`

### references/

- **ooxml.md** – OOXML layout (document.xml, comments.xml, revisions, comments)
- **llm-pipeline.md** – Pipeline: read → Markdown/JSON → model edits → modify; defines Markdown format, JSON shape (blockIndex, originalContent, content, basis)
