---
name: office-document-editor
description: Professional DOCX/PPTX document editing with tracked changes, formatting preservation, highlights, strikethrough, and Git version control.
license: MIT
metadata:
  openclaw:
    requires:
      bins:
        - uv
        - curl
    install:
      - id: uv-env
        kind: uv
        path: .
        bins: [docx_editor.py, pptx_editor.py, generate_diff.py]
---
# Universal Office Document Editor

Professional document editing for **any** DOCX/PPTX file from **any source**.

## Quick Reference

| Task | Approach |
|------|----------|
| Fetch file from upload | `bash scripts/fetch_file.sh upload` |
| Fetch file from URL | `bash scripts/fetch_file.sh https://example.com/file.docx` |
| Fetch file from SFTP | `bash scripts/fetch_file.sh sftp://user@host:/path/file.docx` |
| Edit DOCX | `uv run python scripts/docx_editor.py input.docx output.docx edits.json` |
| Edit PPTX | `uv run python scripts/pptx_editor.py input.pptx output.pptx edits.json` |
| Generate diff | `uv run python scripts/generate_diff.py old.docx new.docx diff.md` |
| Interactive mode | `bash scripts/interactive_edit.sh` |

---

## File Sources

### Uploaded Files (Chat Attachments)

```bash
# Get latest uploaded DOCX
bash scripts/fetch_file.sh upload output.docx

# Get latest uploaded PPTX
bash scripts/fetch_file.sh upload output.pptx
```

Location: `~/.openclaw/workspace/media/inbound/file_*.docx`

### Local Filesystem Paths

```bash
# Copy from local path
bash scripts/fetch_file.sh ~/Documents/report.docx output.docx

# Or direct path
bash scripts/fetch_file.sh /absolute/path/file.pptx output.pptx
```

### Public URLs

```bash
# Download from URL
bash scripts/fetch_file.sh https://example.com/document.docx output.docx
```

### SFTP/SSH Remote Files

```bash
# Fetch via SFTP
bash scripts/fetch_file.sh sftp://user@host:/path/file.docx output.docx
```

---

## Creating Edit Rules

Create `edits.json` with your editing instructions:

```json
{
  "description": "Edit description",
  "replacements": [
    {
      "search": "old text",
      "replace": "new text",
      "style": "highlight"
    }
  ],
  "additions": [
    {
      "after": "after this text",
      "text": "add this text",
      "style": "highlight"
    }
  ],
  "slides": [
    {
      "action": "rearrange",
      "order": [0, 2, 1, 3]
    }
  ]
}
```

### Supported Styles

- `replace` - Direct replacement
- `highlight` - Yellow highlight
- `delete` - Strikethrough
- `bold` - Bold text
- `underline` - Underline

### Slide Actions (PPTX only)

- `rearrange` - Change slide order
- `add` - Add new slide
- `remove` - Delete slide

---

## Editing Documents

### Edit DOCX

```bash
uv run python scripts/docx_editor.py input.docx output.docx edits.json
```

Features:
- Paragraph text editing
- Table cell editing
- Format preservation
- Multiple replacements
- Text additions

### Edit PPTX

```bash
uv run python scripts/pptx_editor.py input.pptx output.pptx edits.json
```

Features:
- Slide text replacement
- Slide rearrangement
- Add/remove slides
- Format preservation

### Generate Diff Report

```bash
uv run python scripts/generate_diff.py input.docx output.docx diff-report.md
```

Output: Standard Unified Diff format in Markdown.

---

## Complete Workflow

### Step 1: Fetch File

```bash
# From upload
bash scripts/fetch_file.sh upload input.docx

# From URL
bash scripts/fetch_file.sh https://example.com/file.docx input.docx

# From local path
bash scripts/fetch_file.sh ~/Documents/file.docx input.docx
```

### Step 2: Create Edit Rules

```json
{
  "description": "IRB Review Response",
  "replacements": [
    {
      "search": "2026 年 2 月 28 日",
      "replace": "2026 年 8 月 31 日",
      "style": "highlight"
    }
  ]
}
```

### Step 3: Execute Edit

```bash
uv run python scripts/docx_editor.py input.docx output.docx edits.json
```

### Step 4: Generate Reports

```bash
# Unified Diff
uv run python scripts/generate_diff.py input.docx output.docx diff.md

# Convert to Markdown
uv run markitdown output.docx > output.md
```

### Step 5: Version Control

```bash
git add *.docx *.md diff.md
git commit -m "Edit: Description of changes"
```

---

## Interactive Mode

For guided editing:

```bash
bash scripts/interactive_edit.sh
```

This will prompt you through:
1. File source selection
2. Edit type selection
3. Details collection
4. Output location

---

## Examples

### Example 1: Text Replacement with Highlight

```json
{
  "replacements": [
    {
      "search": "February 28, 2026",
      "replace": "August 31, 2026",
      "style": "highlight"
    }
  ]
}
```

### Example 2: Add Text After Question

```json
{
  "additions": [
    {
      "after": "What is the research topic?",
      "text": "[ANSWER] Data Structures and Algorithms",
      "style": "highlight"
    }
  ]
}
```

### Example 3: Rearrange Slides

```json
{
  "slides": [
    {
      "action": "rearrange",
      "order": [0, 2, 1, 3, 4]
    }
  ]
}
```

---

## Notes

### Format Preservation

- ✅ Text, paragraphs, tables: Fully preserved
- ✅ Highlights, strikethrough, bold: Supported
- ⚠️ Complex styles (custom themes): May be lost
- ❌ Images, charts: Manual handling required

### Table Text Replacement

python-docx requires **exact match** (including spaces, punctuation, newlines) for table text.

**Solutions:**
1. Use shorter search strings
2. Use `markitdown` to preview table content first
3. Use exact match in JSON

### Git Best Practices

- Use local Git repo (do not upload to GitHub)
- Add sensitive files to `.gitignore`
- Backup to secure location regularly

---

## Dependencies

- **uv**: Package management and virtual environment
- **python-docx**: DOCX editing
- **python-pptx**: PPTX editing
- **mammoth**: DOCX to Markdown conversion
- **markitdown**: Universal document conversion
- **curl**: URL downloads
- **sftp**: SFTP file transfers (optional)

### Installation

```bash
cd ~/.openclaw/workspace/skills/office-document-editor
uv sync
```

---

## Troubleshooting

### "No replacements made"

**Cause:** Text doesn't match exactly

**Solution:**
```bash
# Preview content
uv run markitdown input.docx

# Use exact text from preview
```

### "Virtual environment not found"

**Solution:**
```bash
cd ~/.openclaw/workspace/skills/office-document-editor
uv sync
```

### "File not found"

**Solutions:**
- Check file path is correct
- Try uploading the file again
- Verify URL is accessible
- Check SFTP credentials

---

## Scripts Reference

### fetch_file.sh

Universal file fetcher for all source types.

```bash
bash scripts/fetch_file.sh <source> [output_filename]
```

Sources:
- `upload` - Latest uploaded file
- `/path/to/file` - Local path
- `https://...` - Public URL
- `sftp://...` - SFTP remote

### docx_editor.py

Edit Word documents with formatting.

```bash
uv run python scripts/docx_editor.py input.docx output.docx edits.json
```

### pptx_editor.py

Edit PowerPoint presentations.

```bash
uv run python scripts/pptx_editor.py input.pptx output.pptx edits.json
```

### generate_diff.py

Generate Unified Diff reports.

```bash
uv run python scripts/generate_diff.py old.docx new.docx diff.md
```

### interactive_edit.sh

Interactive guided editing.

```bash
bash scripts/interactive_edit.sh
```

### workflow_complete.sh

Complete automated workflow.

```bash
bash scripts/workflow_complete.sh input.docx edits.json
```
