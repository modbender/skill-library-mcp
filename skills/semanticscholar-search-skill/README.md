# Semantic Scholar Search

> **AI-Powered Academic Paper Search Tool** - Search academic papers through Semantic Scholar

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

**Semantic Scholar Search** is a Claude Code Skill designed to help researchers search and explore academic papers through Semantic Scholar API. It provides comprehensive search capabilities, detailed paper information, author profiles, and citation analysis.

### Key Features

- **Paper Search**: Search papers by keywords, titles, or authors
- **Paper Details**: Get detailed information including abstract, authors, citations, venue
- **Author Profiles**: Retrieve author information, publication count, h-index
- **Citation Analysis**: Get citations and references for any paper
- **Rich Metadata**: Access venue, publication type, citation counts
- **JSON Output**: Export results in JSON format for further processing
- **DOI Support**: Use DOI directly as paper ID

## Installation

### Method 1: One-Click Installation via npx (Recommended)

```bash
npx skills add https://github.com/JackKuo666/semanticscholar-search-skill.git
```

### Method 2: Git Clone

```bash
# Clone to Claude Code skills directory
git clone https://github.com/JackKuo666/semanticscholar-search-skill.git ~/.claude/skills/semanticscholar-search-skill
```

### Method 3: Manual Installation

1. Download the project ZIP or clone to local
2. Copy the `semanticscholar-search-skill` folder to Claude Code skills directory:
   - **macOS/Linux**: `~/.claude/skills/`
   - **Windows**: `%USERPROFILE%\.claude\skills\`
3. Ensure the folder structure is:

```
~/.claude/skills/semanticscholar-search-skill/
├── SKILL.md                 # Skill definition file
├── semantic_scholar_search.py  # Core search script
├── README.md                # Documentation
├── requirements.txt         # Python dependencies
└── .env.example             # Environment variable examples
```

### Install Python Dependencies

**Option 1: Using uv (Recommended - Fastest)**

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
cd ~/.claude/skills/semanticscholar-search-skill
uv venv
source .venv/bin/activate  # Linux/macOS
# or .venv\Scripts\activate  # Windows
uv pip install -r requirements.txt
```

**Option 2: Using conda (Best for scientific/research users)**

```bash
cd ~/.claude/skills/semanticscholar-search-skill
conda create -n semantic-scholar python=3.11 -y
conda activate semantic-scholar
pip install -r requirements.txt
```

**Option 3: Using venv (Built-in)**

```bash
cd ~/.claude/skills/semanticscholar-search-skill
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or .venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Verify Installation

Restart Claude Code or reload skills, then enter in conversation:

```
/semantic-scholar-search
```

If installed successfully, the skill will be activated.

## Configuration

### Environment Variables (Optional)

The skill works without any configuration - Semantic Scholar API is free to use. You can optionally configure an API key for higher rate limits.

Create a `.env` file or set the following environment variables:

```bash
# Optional: Semantic Scholar API Key (higher rate limits)
# Get your API key from: https://www.semanticscholar.org/product/api#api-key
export SEMANTIC_SCHOLAR_API_KEY=""
```

## Usage

### Using in Claude Code

#### 1. Search Papers

```
/semantic-scholar-search Find papers about "transformer architecture in natural language processing"
```

#### 2. Get Paper Details

```
/semantic-scholar-search Get details for paper ID "10.1038/nature12373"
```

#### 3. Get Author Profile

```
/semantic-scholar-search Get author profile for author ID "1741101"
```

#### 4. Citation Analysis

```
/semantic-scholar-search Get citations and references for paper "10.1038/nature12373"
```

### Direct Command Line Usage

#### Search Papers

```bash
# Search for papers
python semantic_scholar_search.py search --query "deep learning in computer vision"

# Get more results
python semantic_scholar_search.py search --query "machine learning" --results 20

# Output as JSON
python semantic_scholar_search.py search --query "CRISPR" --format json --output results.json
```

#### Get Paper Details

```bash
# Get paper details using DOI
python semantic_scholar_search.py paper --paper-id "10.1038/nature12373"

# Get paper details using Semantic Scholar ID
python semantic_scholar_search.py paper --paper-id "10.1038/nature12373" --format json --output paper.json
```

#### Get Author Details

```bash
# Get author information
python semantic_scholar_search.py author --author-id "1741101"

# Get author details as JSON
python semantic_scholar_search.py author --author-id "1741101" --format json --output author.json
```

#### Get Citations and References

```bash
# Get citations and references for a paper
python semantic_scholar_search.py citations --paper-id "10.1038/nature12373"

# Get more citations and references
python semantic_scholar_search.py citations --paper-id "10.1038/nature12373" --limit 20

# Export to JSON
python semantic_scholar_search.py citations --paper-id "10.1038/nature12373" --format json --output citations.json
```

## Command Reference

### search
Search for papers on Semantic Scholar.

| Option | Description |
|--------|-------------|
| `--query` | Search query string (required) |
| `--results` | Number of results (default: 10) |
| `--format` | Output format: console, json |
| `--output` | Output file path |

### paper
Get detailed information about a specific paper.

| Option | Description |
|--------|-------------|
| `--paper-id` | Paper ID or DOI (required) |
| `--format` | Output format: console, json |
| `--output` | Output file path |

### author
Get author details and statistics.

| Option | Description |
|--------|-------------|
| `--author-id` | Author ID (required) |
| `--format` | Output format: console, json |
| `--output` | Output file path |

### citations
Get citations and references for a paper.

| Option | Description |
|--------|-------------|
| `--paper-id` | Paper ID or DOI (required) |
| `--limit` | Number of citations/references to return (default: 10) |
| `--format` | Output format: console, json |
| `--output` | Output file path |

## Output Formats

### Console Output

```
标题: Attention Is All You Need
作者: Vaswani, A., et al.
年份: 2017
发表: NeurIPS
引用数: 50000+
摘要: This paper proposes the Transformer architecture...
链接: https://www.semanticscholar.org/paper/...
```

### Author Output

```
作者ID: 1741101
姓名: Geoffrey Hinton
机构: University of Toronto
论文数: 450+
引用数: 150000+
H指数: 200+
```

### JSON Format

```json
{
  "paperId": "10.1038/nature12373",
  "title": "Paper Title",
  "abstract": "Paper abstract...",
  "year": "2020",
  "authors": [
    {"name": "Author Name", "authorId": "12345"}
  ],
  "citationCount": 150,
  "influentialCitationCount": 75,
  "venue": "Nature",
  "publicationTypes": ["JournalArticle"],
  "url": "https://www.semanticscholar.org/paper/..."
}
```

## Use Cases

### Case 1: Literature Review

```bash
# Find papers on a specific topic
python semantic_scholar_search.py search --query "transformer architecture" --results 30 --format json --output papers.json
```

### Case 2: Track Citations

```bash
# See who cited a paper
python semantic_scholar_search.py citations --paper-id "10.1038/nature12373" --limit 50
```

### Case 3: Author Analysis

```bash
# Get author's publication statistics
python semantic_scholar_search.py author --author-id "1741101"
```

### Case 4: Quick Paper Lookup

```bash
# Get paper details using DOI
python semantic_scholar_search.py paper --paper-id "10.1038/nature12373"
```

## Project Structure

```
semanticscholar-search-skill/
├── SKILL.md                    # Claude Code skill definition
├── semantic_scholar_search.py  # Core search script
├── README.md                   # Documentation
├── requirements.txt            # Python dependencies
└── .env.example                # Environment variable examples
```

## Dependencies

- **Python 3.8+**
- **semanticscholar**: Semantic Scholar API wrapper
- **requests**: HTTP requests

## FAQ

### Q: Do I need an API key?

**A:** No, the Semantic Scholar API is free to use without authentication. However, getting an API key provides higher rate limits.

### Q: How do I find a paper ID?

**A:** You can use the DOI of the paper as the paper ID. For example, "10.1038/nature12373". You can also search for papers first and get the Semantic Scholar paper ID from the search results.

### Q: How do I find an author ID?

**A:** Search for papers by the author, then use the authorId from the search results. Alternatively, visit the author's page on Semantic Scholar and extract the ID from the URL.

### Q: What's the rate limit?

**A:** Without an API key, the rate limit is 100 requests per 5 minutes. With an API key, you get significantly higher limits.

### Q: Can I download PDFs?

**A:** Some papers have open access PDFs available. Check the `openAccessPdf` field in the paper details.

## Troubleshooting

### Issue: "Paper not found"

**Solution:** The paper may not be indexed by Semantic Scholar, or the paper ID/DOI is incorrect. Try searching by title or keywords first.

### Issue: "Rate limit exceeded"

**Solution:** You've made too many requests. Wait a few minutes before trying again, or get an API key from Semantic Scholar for higher limits.

### Issue: "Author not found"

**Solution:** The author ID may be incorrect. Search for papers by the author name and get the author ID from the results.

## Related Projects

- [SemanticScholar-MCP-Server](https://github.com/JackKuo666/SemanticScholar-MCP-Server): MCP server for Semantic Scholar integration
- [PubMed-Search-Skill](https://github.com/JackKuo666/pubmed-search-skill): Search PubMed biomedical literature
- [Sci-Hub-Search-Skill](https://github.com/JackKuo666/sci-hub-search-skill): Search and download papers from Sci-Hub
- [Sci-Data-Extractor](https://github.com/JackKuo666/sci-data-extractor): Extract data from scientific paper PDFs

## Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

## Contact

- GitHub: [JackKuo666/semanticscholar-search-skill](https://github.com/JackKuo666/semanticscholar-search-skill)
- GitHub Issues: [Submit Issues](https://github.com/JackKuo666/semanticscholar-search-skill/issues)

## License

This project is licensed under the **MIT License**.

## Acknowledgments

- [Semantic Scholar](https://www.semanticscholar.org/) for providing the API and academic database
- [semanticscholar PyPI package](https://pypi.org/project/semanticscholar/) for the Python library
- Built based on the [sci-data-extractor](https://github.com/JackKuo666/sci-data-extractor) skill template
