---
name: arxiv-osiris
version: 1.0.0
description: Search and download research papers from arXiv.org - Research version for OpenClaw agents
metadata: {"openclaw": {"emoji": "📚", "requires": {"bins": ["python"], "pip": ["arxiv"]}, "homepage": "https://arxiv.org"}}
---

# ArXiv Skill

Search and download scientific papers from arXiv.org - the largest free distribution of scientific preprints.

## What it does

- **Search** papers by keywords, titles, abstracts
- **Download** PDFs directly
- **Filter** by category (physics, cs, math, etc.)
- **Get metadata** including authors, dates, categories

## Installation

```powershell
# Install Python dependency
pip install arxiv
```

## Usage

### Search for papers

```powershell
# Basic search
.\arxiv.ps1 -Action search -Query "quantum computing"

# With max results
.\arxiv.ps1 -Action search -Query "machine learning" -MaxResults 10

# With category filter (physics, cs, math, q-bio, etc.)
.\arxiv.ps1 -Action search -Query "neural networks" -Categories "cs,stat"
```

### Download a paper

```powershell
# By arXiv ID
.\arxiv.ps1 -Action download -ArxivId "2310.12345"
```

### Python API

```python
from arxiv import search, download

# Search
results = search("simulation hypothesis", max_results=5)
for paper in results:
    print(f"{paper.title} - {paper.pdf_url}")

# Download
paper.download("/path/to/save")
```

## Categories

Common arXiv categories:
- `cs.*` - Computer Science
- `physics.*` - Physics  
- `math.*` - Mathematics
- `q-bio.*` - Quantitative Biology
- `q-fin.*` - Quantitative Finance
- `stat.*` - Statistics

## Examples

- Search for consciousness papers: `arxiv.ps1 -search "consciousness" -max 5`
- Find physics papers: `arxiv.ps1 -search "quantum" -cats "physics" -max 10`
- Download paper: `arxiv.ps1 -download "1706.03762"` (Attention is All You Need)

## Notes

- arXiv is free and open
- Papers are preprints - may not be peer-reviewed
- Great for staying current with research
