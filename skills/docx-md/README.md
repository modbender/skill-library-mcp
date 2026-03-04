# docx-md

Low-level DOCX format tool for AI document review. Converts Word documents to compact Markdown or JSON, applies AI edits back to DOCX with tracked revisions and comments, and finalizes documents.

**License**: [GPL-3.0](LICENSE) — See [License](#license) below.

---

## Overview

| Operation | Description |
|-----------|-------------|
| **Read** | Parse DOCX → output Markdown (default, token-efficient) or JSON |
| **Modify** | Apply AI-returned edit JSON → DOCX with track changes and comments |
| **Finalize** | Accept all revisions, remove comments → clean DOCX |

---

## docx-md vs Raw XML Modification

| Aspect | **Raw XML (OOXML) modification** | **docx-md** |
|--------|----------------------------------|-------------|
| **AI input** | Raw `word/document.xml`, namespaces, `w:p`/`w:r`/`w:t` structure | Structured Markdown or JSON with `blockIndex` |
| **AI output** | Python/XML snippets, `w:ins`/`w:del` tags, RSID, run splitting | Edit JSON: `{ blockIndex, originalContent, content, basis }` |
| **AI knowledge required** | OOXML schema, RSID, run boundaries, comment anchors | Only compare original vs new text; script infers op |
| **Token cost** | High (XML markup, long code) | Lower (compact Markdown, small JSON) |
| **Error surface** | High (XML structure, RSID, namespaces) | Lower (schema-driven, script validates) |
| **Format preservation** | Manual (must preserve pPr, rPr when editing) | Automatic (apply script preserves pPr, rPr) |
| **Workflow** | Unpack → edit XML/Python → pack | Read → AI edits JSON → apply |

**Summary**: Raw XML requires the AI to understand OOXML internals. docx-md hides OOXML complexity: the AI reads structured content, outputs simple edit JSON, and the apply script handles OOXML generation and format preservation (pPr, rPr).

---

## AI Output Format (Apply / 回填 Input)

The AI outputs **only** `blockIndex`, `originalContent`, `content`, `basis`. The apply script infers the operation (replace / delete / add_comment) from these fields — the AI does **not** choose `op`.

### JSON Shape

```json
{
  "modifications": [
    { "blockIndex": 5, "originalContent": "原文本", "content": "修改后文本", "basis": "修改依据" }
  ]
}
```

| Field | Required | Meaning |
|-------|----------|---------|
| `blockIndex` | ✅ | Paragraph index (from `<!-- b:N -->` or `body[].blockIndex`) |
| `originalContent` | — | Original text for diff / delete. Empty or omit for pure comment. |
| `content` | — | New text. Empty = delete or pure comment. |
| `basis` | — | Reason / legal basis → Word comment |

### Op Inference (Script Logic)

The script infers the operation:

| Condition | Operation |
|-----------|-----------|
| `content` non-empty, `originalContent` non-empty | **replace** — diff 段内替换 (w:ins/w:del) |
| `content` non-empty, `originalContent` empty | **insert_paragraph_after** — 在 block 后新增段落 (w:ins) |
| `content` empty, `originalContent` non-empty | **delete** — mark block as w:del |
| Both empty, `basis` non-empty | **add_comment** — add Word comment |

### Rules

- `blockIndex` must match the `<!-- b:N -->` or `body[].blockIndex` from the read output.
- Only `w:p` (paragraph) blocks are editable; table blocks are skipped.
- The apply script preserves paragraph (`pPr`) and run (`rPr`) formatting automatically.

---

## Usage

```bash
# Read → Markdown (default)
python3 scripts/read_docx.py document.docx -o output.md

# Read → JSON
python3 scripts/read_docx.py document.docx -f json -o output.json

# Apply edits
python3 scripts/apply_edits_docx.py document.docx edits.json -o reviewed.docx

# Finalize
python3 scripts/finalize_docx.py reviewed.docx -o final.docx
```

---

## Markdown Format (Read Output)

Each block is prefixed with `<!-- b:N -->` (N = blockIndex):

- **Insertion**: `{+text+}`
- **Deletion**: `{-text-}`
- **Comment**: `[comment: text]`

Example:

```markdown
<!-- b:0 --># Chapter 1
<!-- b:1 -->Payment in {-30-}{+60+} days. [comment: Confirm period]
```

---

## Requirements

- Python 3.10+
- `lxml`: `pip install lxml`

---

## License

This skill is licensed under **GNU General Public License v3.0 (GPL-3.0)**.

- Copyright (c) 2025 yanweiliang
- You may use, modify, and distribute this code under the terms of GPL-3.0.
- Using this skill and all derivative works (modifications, forks, integrations) must comply with GPL-3.0.
- See [LICENSE](LICENSE) for the full text.

**Note**: OpenClaw core is MIT-licensed. Using OpenClaw itself does not require GPL. However, **using this skill** and **all derivative works of this skill** (modifications, forks, integrations that include or build upon this skill) must comply with GPL-3.0.
