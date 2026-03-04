# book-reader

Read books (epub, pdf, txt) from various sources with progress tracking.

## Purpose

Enable AI agents to read full-length books for learning, summarization, and knowledge extraction.

## Features

- **Multiple sources**: Anna's Archive, Project Gutenberg, local files
- **Format support**: EPUB, PDF, TXT
- **Progress tracking**: Remember where you left off
- **Smart chunking**: Read books in digestible sections
- **Summary generation**: Extract key insights as you read

## Tools Required

- `curl` or `wget` - Download books
- `pandoc` - Convert EPUB to text (optional, fallback to python)
- `pdftotext` (poppler-utils) - Extract PDF text
- Python 3 with `ebooklib` and `beautifulsoup4` (for EPUB parsing)

## Usage

### Search for a book

```bash
./book-reader.sh search "Thinking Fast and Slow"
```

### Download a book

```bash
./book-reader.sh download <book-id> [output-file]
```

### Read a book (with progress tracking)

```bash
./book-reader.sh read <file> [--from-page N] [--pages N]
```

### Show reading progress

```bash
./book-reader.sh status
```

## Installation

```bash
# Install dependencies
sudo apt-get install poppler-utils pandoc  # Linux
# brew install poppler pandoc  # macOS

pip3 install ebooklib beautifulsoup4 lxml

# Make executable
chmod +x book-reader.sh
```

## Book Sources

1. **Project Gutenberg** (70k+ public domain books)
   - API: https://gutendex.com
   - Free, legal, no DRM

2. **Anna's Archive** (shadow library)
   - Millions of books, papers, comics
   - Legal gray area depending on jurisdiction
   - Use responsibly

3. **Local files** (your own epub/pdf collection)

## Reading State

Progress tracked in `~/.openclaw/workspace/memory/reading-state.json`:

```json
{
  "currentBook": "Thinking, Fast and Slow",
  "file": "/path/to/book.epub",
  "totalPages": 499,
  "pagesRead": 127,
  "lastRead": 1770957900,
  "bookmarks": [50, 200],
  "notes": "Interesting insight about System 1 vs System 2..."
}
```

## Example Workflow

```bash
# Find the book
./book-reader.sh search "Daniel Kahneman Thinking"

# Download it
./book-reader.sh download 12345 ~/books/thinking-fast-slow.epub

# Start reading
./book-reader.sh read ~/books/thinking-fast-slow.epub --pages 50

# Continue later
./book-reader.sh read ~/books/thinking-fast-slow.epub --pages 50

# Check progress
./book-reader.sh status
```

## Privacy & Ethics

- Public domain books (Gutenberg): Fully legal
- Copyrighted books: Check your local laws
- Consider buying books you find valuable to support authors
- Use for personal learning, not redistribution

## Limitations

- PDF OCR quality varies
- DRM-protected books not supported (by design)
- Large PDFs may be slow to parse
- EPUB formatting may be imperfect in plain text

---

**Use responsibly. Support authors when possible.**
