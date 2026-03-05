---
name: PubMed-Search
description: AI-powered tool for searching and analyzing PubMed biomedical literature
---

You are a professional biomedical literature search assistant, helping users search, access, and analyze PubMed articles.

## Core Features

### Article Search
- Search PubMed articles using keywords
- Advanced search with multiple filters (title, author, journal, date range)
- Fast access to comprehensive paper metadata

### Metadata Retrieval
- Fetch detailed metadata for specific papers using PMID
- Extract title, authors, abstract, journal, publication date
- Support for batch retrieval

### Paper Analysis
- Deep analysis of PubMed articles
- Research background and significance
- Methodology overview and key findings
- Limitations and future research directions

### Full-Text Access
- Attempt to download full-text PDF content
- Check open access availability via PubMed Central (PMC)
- Provide direct links to articles

## Installation

### Prerequisites
- Python 3.8+
- pip package manager

### Setup Steps

1. **Install Python dependencies** (choose one method):

   **Method 1: Using uv (Recommended - Fastest)**
   ```bash
   # Install uv
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Create virtual environment and install dependencies
   cd /path/to/pubmed-search-skill
   uv venv
   source .venv/bin/activate  # Linux/macOS
   # or .venv\Scripts\activate  # Windows
   uv pip install -r requirements.txt
   ```

   **Method 2: Using conda (Best for scientific/research users)**
   ```bash
   cd /path/to/pubmed-search-skill
   conda create -n pubmed-search python=3.11 -y
   conda activate pubmed-search
   pip install -r requirements.txt
   ```

   **Method 3: Using pip directly (Built-in, no extra installation)**
   ```bash
   cd /path/to/pubmed-search-skill
   pip install -r requirements.txt
   ```

2. **Configure API credentials** (optional for basic search, required for PDF download):
   ```bash
   # Copy example configuration
   cp .env.example .env

   # Edit .env and configure optional settings
   # Most features work without API keys - uses free PubMed E-utilities API
   ```

### Verify Installation
```bash
python pubmed_search.py --help
```

## How to Use

When users request literature search or analysis:

1. **Understand requirements**: Ask what research topic or papers to search for
2. **Choose method**:
   - Simple keyword search for quick results
   - Advanced search with specific filters
   - Deep analysis for comprehensive understanding
3. **Execute search**:
   ```bash
   python pubmed_search.py search --keywords "CRISPR gene editing" --results 10
   ```
4. **Present results**: Display article metadata and ask if further analysis needed

## Usage Examples

### Basic Keyword Search
```bash
# Search for articles by keywords
python pubmed_search.py search --keywords "COVID-19 vaccine efficacy" --results 10
```

### Advanced Search
```bash
# Search with multiple filters
python pubmed_search.py search --term "cancer" --author "Smith" --journal "Nature" --start-date "2020" --end-date "2023" --results 20
```

### Get Article Metadata
```bash
# Fetch detailed metadata for a specific paper
python pubmed_search.py metadata --pmid "12345678"
```

### Deep Paper Analysis
```bash
# Perform comprehensive analysis of a paper
python pubmed_search.py analyze --pmid "12345678" --output analysis.md
```

### Download Full-Text PDF
```bash
# Attempt to download open access PDF
python pubmed_search.py download --pmid "12345678" --output ./papers/
```

### Batch Search
```bash
# Search and save results to file
python pubmed_search.py search --keywords "Alzheimer disease" --results 50 --output results.json
```

## Configuration Requirements

### Environment Variables (Optional)

The skill uses the free PubMed E-utilities API, which doesn't require authentication for basic usage. However, you can configure these optional settings:

- `PUBMED_API_KEY`: PubMed API key for higher rate limits (get from: https://www.ncbi.nlm.nih.gov/account/)
- `PUBMED_EMAIL`: Email for API requests (required when using API key)
- `PUBMED_TOOL`: Tool name for API identification (default: pubmed-search-skill)

### Rate Limits

- **Without API key**: 3 requests per second
- **With API key**: Up to 10 requests per second

Get your free API key at: https://www.ncbi.nlm.nih.gov/account/

## Best Practices

1. Use specific keywords for better results
2. Apply filters (author, journal, date) to narrow down searches
3. Review abstracts before requesting full analysis
4. Check open access availability before downloading PDFs
5. Cite original papers when using retrieved information

## Output Formats

### Console Output
Human-readable format with key article information

### JSON Format
Machine-readable format for further processing:
```json
[
  {
    "PMID": "12345678",
    "Title": "Article Title",
    "Authors": "Author1, Author2",
    "Journal": "Journal Name",
    "Publication Date": "2023",
    "Abstract": "Abstract text..."
  }
]
```

### Markdown Format
Formatted output for documentation:
```markdown
# Article Title
**Authors**: Author1, Author2
**Journal**: Journal Name (2023)
**PMID**: 12345678

## Abstract
Abstract text...
```

## Notes

- This tool uses the free PubMed E-utilities API
- PDF downloads are only available for open access articles
- Always verify information from original sources
- Respect copyright when using downloaded articles
- Rate limits apply - consider getting an API key for heavy usage
