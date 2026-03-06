# PubMed-Search

> **AI-Powered Biomedical Literature Search Tool** - Search, access, and analyze PubMed articles

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

**PubMed-Search** is a Claude Code Skill designed to help researchers search and analyze biomedical literature from PubMed. It provides powerful search capabilities, metadata extraction, deep paper analysis, and full-text PDF downloads for open access articles.

### Key Features

- **🔍 Multiple Search Modes**: Simple keyword search or advanced multi-filter search
- **📊 Metadata Extraction**: Fetch comprehensive article information (title, authors, abstract, journal, DOI)
- **🤖 Deep Paper Analysis**: AI-powered comprehensive analysis of research papers
- **📥 PDF Download**: Automatic download of open access articles from PubMed Central
- **📄 Multiple Output Formats**: Console, JSON, and Markdown output options
- **⚙️ No API Key Required**: Works with free PubMed E-utilities API

## Installation

### Method 1: One-Click Installation via npx (Recommended)

```bash
npx skills add https://github.com/JackKuo666/pubmed-search-skill.git
```

### Method 2: Git Clone

```bash
# Clone to Claude Code skills directory
git clone https://github.com/JackKuo666/pubmed-search-skill.git ~/.claude/skills/pubmed-search-skill
```

### Method 3: Manual Installation

1. Download the project ZIP or clone to local
2. Copy the `pubmed-search-skill` folder to Claude Code skills directory:
   - **macOS/Linux**: `~/.claude/skills/`
   - **Windows**: `%USERPROFILE%\.claude\skills\`
3. Ensure the folder structure is:

```
~/.claude/skills/pubmed-search-skill/
├── SKILL.md           # Skill definition file
├── pubmed_search.py   # Core search script
├── README.md          # Documentation
├── requirements.txt   # Python dependencies
└── .env.example       # Environment variable examples
```

### Install Python Dependencies

**Option 1: Using uv (Recommended - Fastest)**

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
cd ~/.claude/skills/pubmed-search-skill
uv venv
source .venv/bin/activate  # Linux/macOS
# or .venv\Scripts\activate  # Windows
uv pip install -r requirements.txt
```

**Option 2: Using conda (Best for scientific/research users)**

```bash
cd ~/.claude/skills/pubmed-search-skill
conda create -n pubmed-search python=3.11 -y
conda activate pubmed-search
pip install -r requirements.txt
```

**Option 3: Using venv (Built-in, no extra installation)**

```bash
cd ~/.claude/skills/pubmed-search-skill
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or .venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Verify Installation

Restart Claude Code or reload skills, then enter in conversation:

```
/pubmed-search
```

If installed successfully, the skill will be activated.

## Configuration

### Environment Variables (Optional)

The skill works without any configuration using the free PubMed E-utilities API. However, you can configure these optional settings for higher rate limits:

Create a `.env` file or set the following environment variables:

```bash
# Optional: PubMed API Key for higher rate limits
# Get your free API key at: https://www.ncbi.nlm.nih.gov/account/
export PUBMED_API_KEY="your-api-key-here"

# Your email address (required when using API key)
export PUBMED_EMAIL="your-email@example.com"

# Tool name for API identification (optional)
export PUBMED_TOOL="pubmed-search-skill"
```

### Rate Limits

- **Without API key**: 3 requests per second
- **With API key**: Up to 10 requests per second

Get your free API key at: https://www.ncbi.nlm.nih.gov/account/

See the [E-utilities documentation](https://www.ncbi.nlm.nih.gov/books/NBK25501/) for more information.

## Usage

### Using in Claude Code

#### 1. Quick Search by Keywords

```
/pubmed-search Search for recent papers about CRISPR gene editing
```

#### 2. Advanced Search with Filters

```
/pubmed-search Find papers by Smith in Nature journal about cancer from 2020-2023
```

#### 3. Get Paper Metadata

```
/pubmed-search Get metadata for PMID 12345678
```

#### 4. Deep Paper Analysis

```
/pubmed-search Analyze the paper with PMID 12345678
```

#### 5. Download Open Access PDF

```
/pubmed-search Download PDF for PMID 12345678
```

### Direct Command Line Usage

#### Basic Keyword Search

```bash
# Search for articles by keywords
python pubmed_search.py search --keywords "COVID-19 vaccine efficacy" --results 10
```

#### Advanced Search

```bash
# Search with multiple filters
python pubmed_search.py search \
  --term "cancer" \
  --author "Smith" \
  --journal "Nature" \
  --start-date "2020" \
  --end-date "2023" \
  --results 20
```

#### Get Article Metadata

```bash
# Fetch detailed metadata for a specific paper
python pubmed_search.py metadata --pmid "12345678"
```

#### Deep Paper Analysis

```bash
# Perform comprehensive analysis and save to file
python pubmed_search.py analyze --pmid "12345678" --output analysis.md
```

#### Download Full-Text PDF

```bash
# Attempt to download open access PDF
python pubmed_search.py download --pmid "12345678" --output-dir ./papers/
```

#### Different Output Formats

```bash
# Output as JSON
python pubmed_search.py search --keywords "Alzheimer" --format json --output results.json

# Output as Markdown
python pubmed_search.py search --keywords "Alzheimer" --format markdown --output results.md

# Show abstracts in console
python pubmed_search.py search --keywords "Alzheimer" --show-abstract
```

## Command Reference

### search
Search for articles on PubMed.

| Option | Description |
|--------|-------------|
| `--keywords` | Search keywords |
| `--term` | General search term |
| `--title` | Search in title |
| `--author` | Author name |
| `--journal` | Journal name |
| `--start-date` | Start date (YYYY/MM/DD) |
| `--end-date` | End date (YYYY/MM/DD) |
| `--results` | Number of results (default: 10) |
| `--output` | Output file path |
| `--format` | Output format: console, json, markdown |
| `--show-abstract` | Show abstract in output |

### metadata
Get metadata for a specific article.

| Option | Description |
|--------|-------------|
| `--pmid` | PubMed ID (required) |
| `--output` | Output file path |
| `--format` | Output format: console, json, markdown |

### analyze
Perform deep analysis of a paper.

| Option | Description |
|--------|-------------|
| `--pmid` | PubMed ID (required) |
| `--output` | Output file path |

### download
Download open access PDF.

| Option | Description |
|--------|-------------|
| `--pmid` | PubMed ID (required) |
| `--output-dir` | Output directory (default: current directory) |

## Output Formats

### Console Output
Human-readable format with article information:
```
================================================================================
[1] CRISPR-Cas9 gene editing for sickle cell disease and beta-thalassemia
作者: Frangoul H, Altshuler D,... 期刊: N Engl J Med (2021)
PMID: 33303479
DOI: 10.1056/NEJMoa2026738

摘要:
This article reports the results of a...
```

### JSON Format
Machine-readable format:
```json
[
  {
    "PMID": "12345678",
    "Title": "Article Title",
    "Authors": "Author1, Author2",
    "Journal": "Journal Name",
    "Publication Date": "2023",
    "Abstract": "Abstract text...",
    "DOI": "10.xxxx/xxxxx"
  }
]
```

### Markdown Format
Formatted output for documentation:
```markdown
# PubMed 搜索结果

共找到 10 篇文章

## 1. Article Title
- **作者**: Author1, Author2
- **期刊**: Journal Name (2023)
- **PMID**: 12345678
- **DOI**: 10.xxxx/xxxxx

**摘要**:
Abstract text...
```

## Use Cases

### Case 1: Literature Review

```bash
# Search for recent papers on a topic
python pubmed_search.py search --keywords "machine learning drug discovery" --results 50 --format markdown --output review.md
```

### Case 2: Track Specific Author's Work

```bash
# Find all papers by an author
python pubmed_search.py search --author "Smith J" --results 100 --output smith_papers.json
```

### Case 3: Journal-Specific Research

```bash
# Search in a specific journal
python pubmed_search.py search --term "CRISPR" --journal "Nature" --start-date "2023" --end-date "2024" --results 20
```

### Case 4: Build Reference Database

```bash
# Batch search and compile references
for keyword in "keyword1" "keyword2" "keyword3"; do
    python pubmed_search.py search --keywords "$keyword" --results 100 --format json --output "refs_${keyword}.json"
done
```

## Project Structure

```
pubmed-search-skill/
├── SKILL.md              # Claude Code skill definition
├── pubmed_search.py      # Core search script
├── README.md             # Documentation
├── requirements.txt      # Python dependencies
└── .env.example          # Environment variable examples
```

## Dependencies

- **Python 3.8+**
- **requests**: HTTP requests to PubMed API
- **python-dotenv**: Environment variable management (optional)

## FAQ

### Q: Do I need an API key?

**A:** No, most features work without an API key using the free PubMed E-utilities API. However, rate limits apply (3 requests/second without key, 10 requests/second with key). Get a free API key at https://www.ncbi.nlm.nih.gov/account/ for heavy usage.

### Q: Can I download any paper as PDF?

**A:** Only open access articles can be downloaded automatically. For other articles, the tool will provide links to the PubMed page where you can check access options.

### Q: What's the difference between --term and --keywords?

**A:** They function the same way. Use --keywords for simple searches and --term when combining with other filters (--author, --journal, etc.) in advanced searches.

### Q: How accurate is the deep paper analysis?

**A:** The analysis is generated based on the article's metadata and abstract. For a complete understanding, we recommend reading the full paper.

### Q: Can I use this skill for commercial purposes?

**A:** Yes, but please comply with PubMed's terms of service and cite original sources appropriately.

## Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

1. Fork this project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Related Projects

- [PubMed-MCP-Server](https://github.com/JackKuo666/PubMed-MCP-Server): MCP server for PubMed integration
- [Sci-Data-Extractor](https://github.com/JackKuo666/sci-data-extractor): Extract data from scientific paper PDFs
- [Claude Code Skills Documentation](https://docs.anthropic.com/en/docs/claude-code/skills)

## Contact

- GitHub: [JackKuo666/pubmed-search-skill](https://github.com/JackKuo666/pubmed-search-skill)
- GitHub Issues: [Submit Issues](https://github.com/JackKuo666/pubmed-search-skill/issues)

## License

This project is licensed under the **MIT License**.

## Acknowledgments

- PubMed and the E-utilities API: https://www.ncbi.nlm.nih.gov/
- Built based on the [sci-data-extractor](https://github.com/JackKuo666/sci-data-extractor) skill template

---

**Note**: This tool is for academic research use only. Please comply with copyright regulations and cite original literature when using retrieved information.
