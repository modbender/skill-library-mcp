---
name: abstract-searcher
description: Add abstracts to .bib file entries by searching academic databases (arXiv, Semantic Scholar, CrossRef) with browser fallback.
---

# Abstract Searcher

Automatically fetch and add abstracts to BibTeX entries.

## Usage

Given a .bib file, this skill will:
1. Parse each BibTeX entry
2. Search for the abstract using multiple sources:
   - arXiv API (for arXiv papers)
   - Semantic Scholar API
   - CrossRef API
   - OpenAlex API
3. **If APIs fail**: Use browser automation to search Google Scholar
4. Add `abstract={...}` to each entry
5. Return the complete modified .bib file

## Quick Start

```bash
# Process a bib file (API-based)
python3 {baseDir}/scripts/add_abstracts.py input.bib > output.bib
```

## API Sources (No keys required)

1. **arXiv API**: `http://export.arxiv.org/api/query?search_query=...`
2. **Semantic Scholar**: `https://api.semanticscholar.org/graph/v1/paper/search?query=...`
3. **CrossRef**: `https://api.crossref.org/works?query.title=...`
4. **OpenAlex**: `https://api.openalex.org/works?search=...`

## Browser Fallback (IMPORTANT!)

When APIs fail to find an abstract, **use Chrome browser relay like a real person**:

### Step 1: Attach Chrome tab
```
# Check if tab is attached
browser action=tabs profile=chrome

# If no tabs, ask user to click the Clawdbot Browser Relay toolbar icon
# Or use mac-control skill to auto-click it
```

### Step 2: Open Google Scholar and search
```
browser action=open profile=chrome targetUrl="https://scholar.google.com"
browser action=snapshot profile=chrome

# Type the paper title in search box
browser action=act profile=chrome request={"kind":"type","ref":"search box ref","text":"paper title here"}
browser action=act profile=chrome request={"kind":"press","key":"Enter"}
browser action=snapshot profile=chrome
```

### Step 3: Click the result
```
# Find the paper in results, click to open
browser action=act profile=chrome request={"kind":"click","ref":"paper title link ref"}
browser action=snapshot profile=chrome
```

### Step 4: Extract abstract from the page
- **ScienceDirect**: Look for "Abstract" section in snapshot
- **ACL Anthology**: Abstract is directly visible at top
- **Springer/Wiley**: May need to click "Abstract" to expand
- **PubMed**: Abstract is usually visible

### Step 5: Copy and format for BibTeX
```
# Get the abstract text from snapshot
# Clean it: remove newlines, escape special chars
# Add to bib entry: abstract={...},
```

### Tips:
- Use `profile=chrome` to use real Chrome with your login sessions
- Google Scholar rarely blocks real Chrome browsers
- ScienceDirect/IEEE may need institutional login (your Chrome has it)
- Always verify the paper title matches before copying abstract!

## Notes

- Rate limiting: 2 seconds between API requests
- Browser fallback should find almost all papers
- Abstracts are cleaned (newlines removed, escaped for BibTeX)
- Always verify the abstract matches the correct paper!
