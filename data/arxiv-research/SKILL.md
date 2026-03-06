---
name: arxiv-research
version: 1.0.0
description: Search and download research papers from arXiv.org - Research skill for OpenClaw agents
metadata: {"openclaw": {"emoji": "📚", "requires": {"bins": ["python"], "pip": ["arxiv"]}, "homepage": "https://arxiv.org"}}
---

# ArXiv Research Skill

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
python arxiv_search.py search "quantum computing"

# With max results
python arxiv_search.py search "machine learning" --max 10

# With category filter (physics, cs, math, q-bio, etc.)
python arxiv_search.py search "neural networks" --cats cs,stat
```

### Download a paper

```powershell
# By arXiv ID
python arxiv_search.py download "2310.12345"
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

- Search for consciousness papers: `python arxiv_search.py search "consciousness" --max 5`
- Find physics papers: `python arxiv_search.py search "quantum" --cats physics --max 10`
- Download paper: `python arxiv_search.py download "1706.03762"` (Attention is All You Need)

## Notes

- arXiv is free and open
- Papers are preprints - may not be peer-reviewed
- Great for staying current with research
