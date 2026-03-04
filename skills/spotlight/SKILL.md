---
name: spotlight
description: Search files and content using macOS Spotlight indexing (mdfind). Use when the user asks to search local files, documents, or directories on macOS. Supports text content search inside PDFs, Word documents, text files, and more. Much faster than grep for large document collections. Only works on macOS systems with Spotlight enabled.
---

# Spotlight Search

Search local files using macOS Spotlight indexing system.

## When to Use

Use this skill when:
- User asks to search files or directories on macOS
- Need to find documents containing specific text
- Searching large document collections (faster than grep)
- Need to search inside PDFs, Word docs, or other indexed formats

## Quick Start

```bash
scripts/spotlight-search.sh <directory> <query> [--limit N]
```

**Examples:**

```bash
scripts/spotlight-search.sh ~/Documents "machine learning"
scripts/spotlight-search.sh ~/research "neural networks" --limit 10
scripts/spotlight-search.sh ~/Downloads "meeting notes" --limit 5
```

## Search Features

- **Fast**: Uses system-level Spotlight index (no file scanning)
- **Content-aware**: Searches inside PDF, docx, txt, md, etc.
- **Multilingual**: Supports Chinese, Japanese, and all languages
- **Metadata**: Returns file path, type, and size

## Output Format

```
🔍 Searching in /path/to/directory for: query

✅ Found N results (showing up to M):

📄 /full/path/to/file.pdf [pdf, 2.3M]
📄 /full/path/to/document.txt [txt, 45K]
📁 /full/path/to/folder/
```

## Supported File Types

Spotlight automatically indexes:
- Text files (txt, md, csv, json, xml, etc.)
- Documents (pdf, docx, pages, rtf, etc.)
- Code files (py, js, java, c, etc.)
- Emails and contacts
- Images (with embedded metadata/OCR)

## Limitations

- **macOS only**: Requires Spotlight indexing
- **Indexed directories only**: External drives may not be indexed
- **Keyword search**: Not semantic (use embedding-based search for semantic queries)
- **Privacy**: Respects Spotlight privacy settings (excluded directories won't appear)

## Check Indexing Status

```bash
# Check if a volume is indexed
mdutil -s /path/to/volume

# Enable indexing (requires admin)
sudo mdutil -i on /path/to/volume
```

## Integration with LLM Workflows

**Pattern: Search + Extract + Summarize**

1. Use `spotlight-search.sh` to find relevant files
2. Use `read` tool to extract content from top results
3. Summarize or answer user's question based on extracted content

**Example workflow:**

```
User: "Find all documents about machine learning in my research folder"

1. Run: spotlight-search.sh ~/research "machine learning" --limit 10
2. Read top 3-5 results with read tool
3. Summarize findings for user
```

## Advanced Query Syntax

Spotlight supports advanced query operators:

```bash
# Exact phrase
spotlight-search.sh ~/Documents "\"machine learning\""

# AND operator
spotlight-search.sh ~/Documents "neural AND networks"

# OR operator
spotlight-search.sh ~/Documents "AI OR artificial intelligence"

# Metadata queries
spotlight-search.sh ~/Documents "kMDItemContentType == 'com.adobe.pdf'"
```

## Troubleshooting

**No results found:**
- Check if directory is indexed: `mdutil -s /path`
- Wait for indexing to complete (new files may take minutes)
- Verify Spotlight is enabled in System Preferences

**Incorrect results:**
- Spotlight uses fuzzy matching and synonyms
- Use exact phrase search: `"exact phrase"`
- Check privacy settings (some folders may be excluded)

## Performance

- **Instant**: Pre-indexed, no file scanning needed
- **Scales well**: Handles millions of files
- **Low CPU**: No processing overhead (vs grep/ripgrep)

**Comparison:**

| Tool | Speed | Content Search | Multilingual |
|------|-------|----------------|--------------|
| Spotlight | ⚡ Instant | ✅ Yes | ✅ Yes |
| grep/ripgrep | 🐢 Slow | ✅ Yes | ✅ Yes |
| find | ⚡ Fast | ❌ No | N/A |

## Platform Notes

- **macOS only**: This skill requires macOS Spotlight
- **Linux alternative**: Use `grep -r` or `ripgrep`
- **Windows alternative**: Use Windows Search or Everything search
