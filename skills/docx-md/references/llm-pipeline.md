# LLM-Oriented DOCX Pipeline

For long documents (e.g. contracts) sent to an LLM for edits, use **compact read → structured representation → LLM → edit JSON → write-back**. Markdown output is token-efficient compared to full JSON.

---

## 1. Overall flow

```
docx → [read] → Markdown (or JSON)
                    ↓
         + prompt → LLM
                    ↓
         edit JSON (blockIndex, originalContent, content, basis)
                    ↓
         [apply_edits_docx] → OOXML → write back to docx
```

- **Read**: Output Markdown (default) or JSON. Markdown uses `<!-- b:N -->` blockIndex markers; revisions: `{+inserted+}` `{-deleted-}`; comments: `[comment: text]`.
- **LLM output**: The model outputs only **edit JSON** with `blockIndex`, `originalContent`, `content`, `basis`. No `op` — the script infers replace/delete/add_comment from these fields.
- **Apply**: Convert JSON to OOXML (`w:ins` / `w:del` / comment anchors) and write back.

---

## 2. Markdown format (default, token-efficient)

Each block is prefixed with `<!-- b:N -->` where N is the blockIndex. The LLM uses this to reference blocks when producing edits.

### Block types

- **Headings**: `<!-- b:0 --># Chapter 1` (level 1–6)
- **Paragraphs**: `<!-- b:1 -->Plain text content.`
- **Tables**: `<!-- b:3 -->| A | B |\n| C | D |`

### Revisions and comments

- **Insertion**: `{+inserted text+}`
- **Deletion**: `{-deleted text-}`
- **Comment**: `[comment: Comment text here]` (inline) or comment ID reference

### Example

```markdown
<!-- b:0 --># Chapter 1 General
<!-- b:1 -->This contract is entered into by the {+following+} parties.
<!-- b:2 -->## Article 2
<!-- b:3 -->| Party A | Party B |
| Company A | Company B |
<!-- b:4 -->Payment terms: 30 days. [comment: Please confirm 30 or 60 days]
```

Use `blockIndex` from the `<!-- b:N -->` markers when outputting edits.

---

## 3. JSON format (full structure)

Use `-f json` when you need the full structure. Schema: `{ body, comments, path }`. Each block: `type`, `blockIndex`, `segments`.

**Segment types**:
- `{"type": "text", "value": "..."}`
- `{"type": "insert", "text": "...", "author", "date"}`
- `{"type": "delete", "text": "...", "author", "date"}`
- `{"type": "comment", "id": "..."}` (full content in top-level `comments`)

---

## 4. Edit JSON (LLM output)

The model outputs **only** this JSON shape. No `op` field — the apply script infers the operation from the fields.

```json
{
  "modifications": [
    { "blockIndex": 5, "originalContent": "原文本", "content": "修改后文本", "basis": "修改依据" }
  ]
}
```

| Field | Meaning |
|-------|---------|
| `blockIndex` | Paragraph index (from `<!-- b:N -->`) |
| `originalContent` | Original text for diff or delete |
| `content` | New text; empty = delete or pure comment |
| `basis` | Reason / legal basis → Word comment |

**Op inference** (script logic):  
`content` non-empty → replace (diff 段内替换); `content` empty + `originalContent` → delete; both empty + `basis` → add_comment.

---

## 5. Scripts

| Script | Purpose |
|--------|---------|
| `read_docx.py` | Read docx → Markdown (default) or JSON |
| `apply_edits_docx.py` | Apply edits JSON → docx with track changes and comments |
| `finalize_docx.py` | Accept all revisions, remove comments → clean docx |
