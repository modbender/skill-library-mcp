# arXiv Research Assistant

> **Search, download, and summarize academic papers from arXiv.org — directly from your AI assistant.**

<p align="center">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/ClawHub-skill-purple.svg" alt="ClawHub">
  <img src="https://img.shields.io/badge/version-1.0.1-orange.svg" alt="Version">
</p>

---

## What It Does

Your AI gains the power to explore academic research. Ask naturally, get papers instantly.

| Feature | Description |
|---------|-------------|
| **Smart Search** | Natural language queries across all arXiv categories |
| **Paper Details** | Full abstracts, authors, dates, and metadata |
| **PDF Download** | Save papers locally for offline reading |
| **Categories** | Browse by field (cs.AI, cs.CR, stat.ML, etc.) |
| **Recent Papers** | Stay updated with latest research |

---

## Quick Start

### Installation
```bash
clawhub install Ractorrr/arxiv
```

### Just Ask Your AI
```
"Search arXiv for prompt injection attacks"
"Find papers by Goodfellow on adversarial examples"
"Get details for arXiv 2403.04957"
"Download the latest LLM security papers"
"What's new in cs.CR this week?"
```

---

## Command Line Usage

```bash
# Search papers by query
python arxiv_tool.py search "LLM jailbreaking" --max 10

# Get paper details by ID
python arxiv_tool.py get 2403.04957

# Download PDF to local folder
python arxiv_tool.py download 2403.04957

# List recent papers in a category
python arxiv_tool.py recent cs.CR --days 7

# Search by author
python arxiv_tool.py search --author "Hinton" --max 5
```

---

## Example Output

```
Found 5 papers for: "prompt injection attack LLM"

┌─────────────────────────────────────────────────────────────────┐
│ Automatic and Universal Prompt Injection Attacks               │
├─────────────────────────────────────────────────────────────────┤
│ ID:        2403.04957v1                                         │
│ Authors:   Xiaogeng Liu, Zhiyuan Yu, Yizhe Zhang (+2)          │
│ Published: 2024-03-07                                           │
│ Category:  cs.AI, cs.CR                                         │
│ PDF:       https://arxiv.org/pdf/2403.04957v1                  │
└─────────────────────────────────────────────────────────────────┘

Abstract: We present a novel approach to automatic prompt 
injection that achieves universal transfer across multiple 
LLM architectures...
```

---

## Use Cases

| Who | How They Use It |
|-----|-----------------|
| **Researchers** | Literature review, finding related work |
| **Job Seekers** | Interview prep with cutting-edge papers |
| **Content Creators** | Source material for technical articles |
| **Learners** | Deep dive into any ML/AI topic |
| **Security Pros** | Track latest adversarial ML research |

---

## Configuration

### Environment Variables (Optional)
```bash
# MongoDB for paper tracking (optional)
export MONGODB_URI="mongodb+srv://..."
export MONGODB_DB_NAME="research_papers"

# Custom download directory
export ARXIV_PAPERS_DIR="./papers"
```

---

## Files

| File | Purpose |
|------|---------|
| `arxiv_tool.py` | Main CLI tool |
| `SKILL.md` | AI instructions |
| `requirements.txt` | Python dependencies |

---

## Links

- **GitHub**: [Ractorrr/arxiv-mcp](https://github.com/Ractorrr/arxiv-mcp)
- **arXiv API**: [arxiv.org/help/api](https://arxiv.org/help/api)

---

## License

MIT License — Free to use, modify, and distribute.

---

<p align="center">
  <b>Built by <a href="https://github.com/Ractorrr">Ractor</a></b>
  <br>
  <i>AI Security Researcher</i>
</p>
