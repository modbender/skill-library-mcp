---
name: hxxra
description: A Research Assistant workflow skill with four core commands: search papers, download PDFs, analyze content, and save to Zotero. Entry point is a Python script located at scripts/hxxra.py and invoked via stdin/stdout (OpenClaw integration). The search uses crawlers for Google Scholar and arXiv APIs; download uses Python requests or arXiv API; analyze uses an LLM; save uses Zotero API.
---

# hxxra

This skill is a Research Assistant that helps users search, download, analyze, and save research papers.

## Core Commands

### 1. **hxxra search** - Search for research papers

**Dependencies**: `pip install scholarly`

**Purpose**: Search for papers using Google Scholar and arXiv APIs

**Parameters**:

- `-q, --query <string>` (Required): Search keywords
- `-s, --source <string>` (Optional): Data source: `arxiv` (default), `scholar`
- `-l, --limit <number>` (Optional): Number of results (default: 10)
- `-o, --output <path>` (Optional): JSON output file (default: `search_results.json`)

**Input Examples**:

```json
{"command": "search", "query": "neural radiance fields", "source": "arxiv", "limit": 10, "output": "results.json"} | python scripts/hxxra.py
{"command": "search", "query": "transformer architecture", "source": "scholar", "limit": 15} | python scripts/hxxra.py
```

**Output Structure**:

```json
{
  "ok": true,
  "command": "search",
  "query": "<query>",
  "source": "<source>",
  "results": [
    {
      "id": "1",
      "title": "Paper Title",
      "authors": ["Author1", "Author2"],
      "year": "2023",
      "source": "arxiv",
      "abstract": "Abstract text...",
      "url": "https://arxiv.org/abs/xxxx.xxxxx",
      "pdf_url": "https://arxiv.org/pdf/xxxx.xxxxx.pdf",
      "citations": 123
    }
  ],
  "total": 10,
  "output_file": "/path/to/results.json"
}
```

------

### 2. **hxxra download** - Download PDF files

**Purpose**: Download PDFs for specified papers

**Parameters**:

- `-f, --from-file <path>` (Required): JSON file with search results
- `-i, --ids <list>` (Optional): Paper IDs (comma-separated or range)
- `-d, --dir <path>` (Optional): Download directory (default: `./papers`)

**Input Examples**:

```json
{"command": "download", "from-file": "results.json", "ids": [1, 3, 5], "dir": "./downloads"} | python scripts/hxxra.py
{"command": "download", "from-file": "results.json", "dir": "./downloads"} | python scripts/hxxra.py
```

**Output Structure**:

```json
{
  "ok": true,
  "command": "download",
  "downloaded": [
    {
      "id": "1",
      "title": "Paper Title",
      "status": "success",
      "pdf_path": "/path/to/downloads/Smith_2023_Title.pdf",
      "size_bytes": 1234567,
      "url": "https://arxiv.org/pdf/xxxx.xxxxx.pdf"
    }
  ],
  "failed": [],
  "total": 3,
  "successful": 3,
  "download_dir": "/path/to/downloads"
}
```

------

### 3. **hxxra analyze** - Analyze PDF content

**Dependencies**: `pip install pymupdf pdfplumber openai`

**Purpose**: Analyze paper content using LLM
**Parameters**:

- `-p, --pdf <path>` (Optional*): Single PDF file to analyze
- `-d, --directory <path>` (Optional*): Directory with multiple PDFs
- `-o, --output <path>` (Optional): Output directory (default: `./analysis`)

** Note: Either `--pdf` or `--directory` must be provided, but not both*

**Input Examples**:

```json
{"command": "analyze", "pdf": "paper.pdf", "output": "analysis.json"} | python scripts/hxxra.py
{"command": "analyze", "directory": "./papers/"} | python scripts/hxxra.py
```

**Output Structure**:

```json
{
  "ok": true,
  "command": "analyze",
  "analyzed": [
    {
      "id": "paper_1",
      "original_file": "paper.pdf",
      "analysis_file": "/path/to/analysis/paper_analysis.json",
      "metadata": {
        "title": "Paper Title",
        "authors": ["Author1", "Author2"],
        "year": "2023",
        "abstract": "Abstract text..."
      },
      "analysis": {
        "background": "Problem background...",
        "methodology": "Proposed method...",
        "results": "Experimental results...",
        "conclusions": "Conclusions..."
      },
      "status": "success"
    }
  ],
  "summary": {
    "total": 1,
    "successful": 1,
    "failed": 0
  }
}
```

------

### 4. **hxxra save** - Save to Zotero

**Purpose**: Save papers to Zotero collection

**Parameters**:

- `-f, --from-file <path>` (Required): JSON file with paper data
- `-i, --ids <list>` (Optional): Paper IDs to save
- `-c, --collection <string>` (Required): Zotero collection name

**Input Examples**:

```json
{"command": "save", "from-file": "analysis.json", "ids": [1, 2, 3], "collection": "AI Research"} | python scripts/hxxra.py
{"command": "save", "from-file": "analysis.json", "collection": "My Collection"} | python scripts/hxxra.py
```

**Output Structure**:

```json
{
  "ok": true,
  "command": "save",
  "collection": "AI Research",
  "saved_items": [
    {
      "id": "1",
      "title": "Paper Title",
      "zotero_key": "ABCD1234",
      "url": "https://www.zotero.org/items/ABCD1234",
      "status": "success"
    }
  ],
  "failed_items": [],
  "total": 3,
  "successful": 3,
  "zotero_collection": "ABCD5678"
}
```

------

## Workflow Examples

### Complete Workflow

```bash
# 1. Search for papers
{"command": "search", "query": "graph neural networks", "source": "arxiv", "limit": 10} | python scripts/hxxra.py

# 2. Download first 5 papers
{"command": "download", "from-file": "search_results.json"} | python scripts/hxxra.py

# 3. Analyze downloaded papers
{"command": "analyze", "directory": "./papers/"} | python scripts/hxxra.py

# 4. Save to Zotero
{"command": "save", "from-file": "./analysis/", "collection": "GNN Papers"} | python scripts/hxxra.py
```

### Single Command Examples

```bash
# Search with scholar
{"command": "search", "query": "reinforcement learning", "source": "scholar", "limit": 15} | python scripts/hxxra.py

# Download specific papers
{"command": "download", "from-file": "search_results.json", "ids": [2, 4, 6]} | python scripts/hxxra.py

# Analyze single PDF in detail
{"command": "analyze", "pdf": "important_paper.pdf"} | python scripts/hxxra.py

# Save with custom notes
{"command": "save", "from-file": "search_results.json", "ids": [1], "collection": "To Read"} | python scripts/hxxra.py
```

## Configuration Requirements

### API Credentials(config.json)

1. **arXiv API**: No key required for basic access

2. **Google Scholar**: May require authentication for large queries

3. **Zotero API**: Required credentials:

   ```json
   {
     "api_key": "YOUR_ZOTERO_API_KEY", # Create at https://www.zotero.org/settings/keys/new
     "user_id": "YOUR_ZOTERO_USER_ID", # Found on the same page (numeric, not username)
     "library_type": "user"  # or "group"
   }
   ```

4. **LLM API**: OpenAI or compatible API key for analysis

## Notes

- All commands are executed via stdin/stdout JSON communication
- Error handling returns `{"ok": false, "error": "Error message"}`
- Large operations support progress reporting via intermediate messages
- Configuration is loaded from `config.json` or environment variables
- Concurrent operations have configurable limits to avoid rate limiting

## Error Handling

Each command returns standard error format:

```json
{
  "ok": false,
  "command": "<command>",
  "error": "Error description",
  "error_code": "ERROR_TYPE",
  "suggestion": "How to fix it"
}
```

## Development Status

version: v1
- ✅ Command structure defined
- ✅ Parameter validation implemented
- ✅ arXiv integration in progress
- ✅ Google Scholar integration using scholarly library
- ✅ Zotero API integration
- ✅ LLM analysis pipeline using pymupdf pdfplumber and OpenAI API