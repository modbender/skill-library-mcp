# Token Optimization

## The 100-300-5000 Rule

| Component | Soft Limit | Hard Limit |
|-----------|------------|------------|
| Metadata (name+description) | 50 words | 100 words |
| SKILL.md body | 200 lines | 300 lines |
| Single reference | 3K words | 5K words |
| Total footprint | 5K tokens | 10K tokens |

## Core Principle

**Context window is a public good.**

Every token in your skill competes with:
- System prompt (~2K tokens)
- Conversation history
- Other skills' metadata
- User's actual request

**Challenge every sentence:** "Does Claude really need this?"

## Technique 1: Ruthless Editing

### Before (verbose, ~500 tokens)
```markdown
## PDF Rotation

PDF rotation is the process of changing the orientation of pages in a PDF document. This is useful when pages are scanned in the wrong orientation or when you need to adjust the layout for presentation purposes. The rotation can be 90, 180, or 270 degrees.

To rotate a PDF, you need to use a PDF manipulation library. There are several libraries available including PyPDF2, pdfplumber, and pikepdf. Each has its own advantages and disadvantages.

### Using pdfplumber

pdfplumber is a Python library that provides a high-level interface for working with PDF files. It is built on top of pdfminer.six and provides additional functionality for extracting text and tables.

To install pdfplumber:
```bash
pip install pdfplumber
```

To rotate a PDF using pdfplumber:
```python
import pdfplumber
# ... 20 lines of code
```
```

### After (concise, ~50 tokens)
```markdown
## Rotate PDF

```bash
python scripts/rotate.py input.pdf 90  # 90, 180, or 270
```

See [ROTATION.md](references/ROTATION.md) for batch processing.
```

**10x reduction.** Same functionality.

## Technique 2: Command Templates

Replace explanations with copy-paste commands:

```markdown
## Common Operations

```bash
# Extract text from single PDF
python scripts/extract.py document.pdf

# Extract from multiple PDFs
python scripts/extract.py *.pdf --output ./texts/

# Extract specific pages
python scripts/extract.py doc.pdf --pages 1,5-10
```
```

No need to explain what extraction is — examples show it.

## Technique 3: Progressive Detail

Start minimal, link to details:

```markdown
## Quick Start

```bash
python scripts/process.py input.pdf
```

## Options

| Task | Command | Details |
|------|---------|---------|
| Extract text | `--extract` | [EXTRACT.md](references/EXTRACT.md) |
| Rotate | `--rotate 90` | [ROTATE.md](references/ROTATE.md) |
```

## Technique 4: Table Over List

Tables compress information:

### List (verbose)
```markdown
## Supported Formats

- PDF: Portable Document Format, good for documents
- PNG: Portable Network Graphics, good for images with transparency
- JPEG: Joint Photographic Experts Group, good for photos
```

### Table (concise)
```markdown
## Supported Formats

| Format | Use For |
|--------|---------|
| PDF | Documents |
| PNG | Transparent images |
| JPEG | Photos |
```

## Technique 5: Remove Boilerplate

❌ **Don't include:**
- "Introduction" sections
- "Overview" that restates description
- "Prerequisites" that are obvious
- "Conclusion" or "Summary"

✅ **Start immediately:**
```markdown
---
description: "X processing. Use when..."
---

# X Processing

## Quick Command
...
```

## Technique 6: Imperative Voice

Active voice saves tokens:

| Passive | Imperative | Savings |
|---------|------------|---------|
| "You should open the file" | "Open the file" | 2 words |
| "The script can be executed" | "Run the script" | 3 words |
| "It is important to note" | (delete) | 5 words |

## Measuring Token Count

Approximate formulas:
```
Words to tokens: ~1.5 tokens/word
Lines to tokens: ~5-10 tokens/line
```

Quick check:
```bash
# Count words in SKILL.md
wc -w .qwen/skills/my-skill/SKILL.md

# Target: <500 words for metadata + body
```

## Red Flags (Token Bloat)

Watch for these patterns:

1. **"In order to"** → "To" (3→1 words)
2. **"It is important to note that"** → Delete
3. **"As mentioned previously"** → Delete
4. **Long code comments** → Remove or shorten
5. **Multiple examples for same concept** → Keep best one

## Checklist

Before publishing:

- [ ] Every paragraph justifies its tokens
- [ ] Examples replace explanations
- [ ] Tables used for structured data
- [ ] No boilerplate sections
- [ ] Imperative voice throughout
- [ ] SKILL.md < 300 lines
- [ ] References < 5K words each