# Google Scholar Search

> **AI-Powered Academic Literature Search Tool** - Search academic papers through Google Scholar

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

**Google Scholar Search** is a Claude Code Skill designed to help researchers search and explore academic literature through Google Scholar. It provides powerful search capabilities with advanced filtering options including author-specific searches and year-based filtering.

### Key Features

- **Keyword Search**: Search papers by keywords, titles, or topics
- **Advanced Search**: Filter results by author and publication year range
- **Author Profiles**: Retrieve detailed author information including interests and citation counts
- **Rich Metadata**: Access titles, authors, abstracts, and direct links
- **JSON Export**: Export results in JSON format for further processing
- **Web Scraping**: Uses web scraping to access Google Scholar (no official API available)

## Installation

### Method 1: One-Click Installation via npx (Recommended)

```bash
npx skills add https://github.com/JackKuo666/google-scholar-search-skill.git
```

### Method 2: Git Clone

```bash
# Clone to Claude Code skills directory
git clone https://github.com/JackKuo666/google-scholar-search-skill.git ~/.claude/skills/google-scholar-search-skill
```

### Method 3: Manual Installation

1. Download the project ZIP or clone to local
2. Copy the `google-scholar-search-skill` folder to Claude Code skills directory:
   - **macOS/Linux**: `~/.claude/skills/`
   - **Windows**: `%USERPROFILE%\.claude\skills\`
3. Ensure the folder structure is:

```
~/.claude/skills/google-scholar-search-skill/
├── SKILL.md               # Skill definition file
├── google_scholar_search.py  # Core search script
├── README.md              # Documentation
└── requirements.txt       # Python dependencies
```

### Install Python Dependencies

**Option 1: Using uv (Recommended - Fastest)**

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
cd ~/.claude/skills/google-scholar-search-skill
uv venv
source .venv/bin/activate  # Linux/macOS
# or .venv\Scripts\activate  # Windows
uv pip install -r requirements.txt
```

**Option 2: Using conda (Best for scientific/research users)**

```bash
cd ~/.claude/skills/google-scholar-search-skill
conda create -n google-scholar python=3.11 -y
conda activate google-scholar
pip install -r requirements.txt
```

**Option 3: Using venv (Built-in)**

```bash
cd ~/.claude/skills/google-scholar-search-skill
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or .venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Verify Installation

Restart Claude Code or reload skills, then enter in conversation:

```
/google-scholar-search
```

If installed successfully, the skill will be activated.

## Usage

### Using in Claude Code

#### 1. Basic Search

```
/google-scholar-search Find papers about "transformer architecture"
```

#### 2. Advanced Search with Author

```
/google-scholar-search Search for "deep learning" by author "Yann LeCun"
```

#### 3. Search with Year Range

```
/google-scholar-search Find papers about "GANs" from 2018 to 2023
```

#### 4. Get Author Information

```
/google-scholar-search Get author profile for "Yoshua Bengio"
```

### Direct Command Line Usage

#### Basic Search

```bash
# Search for papers
python google_scholar_search.py search --query "machine learning in healthcare"

# Get more results
python google_scholar_search.py search --query "CRISPR" --results 20

# Output as JSON
python google_scholar_search.py search --query "neural networks" --format json --output results.json
```

#### Advanced Search

```bash
# Search with author filter
python google_scholar_search.py advanced --query "deep learning" --author "Ian Goodfellow"

# Search with year range
python google_scholar_search.py advanced --query "transformer" --year-start 2018 --year-end 2022

# Combine filters
python google_scholar_search.py advanced --query "GANs" --author "Ian Goodfellow" --year-start 2015 --year-end 2023 --results 15
```

#### Author Information

```bash
# Get author profile
python google_scholar_search.py author --name "Geoffrey Hinton"

# Get author details as JSON
python google_scholar_search.py author --name "Andrew Ng" --format json --output author.json
```

## Command Reference

### search
Search papers by keywords.

| Option | Description |
|--------|-------------|
| `--query` | Search query string (required) |
| `--results` | Number of results (default: 10) |
| `--format` | Output format: console, json |
| `--output` | Output file path |

### advanced
Advanced search with filters.

| Option | Description |
|--------|-------------|
| `--query` | Search query string (required) |
| `--author` | Filter by author name |
| `--year-start` | Start year for year range filter |
| `--year-end` | End year for year range filter |
| `--results` | Number of results (default: 10) |
| `--format` | Output format: console, json |
| `--output` | Output file path |

### author
Get author profile and publications.

| Option | Description |
|--------|-------------|
| `--name` | Author name (required) |
| `--format` | Output format: console, json |
| `--output` | Output file path |

## Output Formats

### Console Output

```
--- 结果 1 ---
标题: Attention Is All You Need
作者: Vaswani, A., Shazeer, N., Parmar, N., et al.
摘要: The dominant sequence transduction models are based on complex recurrent or convolutional neural networks...
链接: https://arxiv.org/abs/1706.03762
```

### Author Output

```
姓名: Geoffrey Hinton
机构: University of Toronto
研究领域: Machine Learning, Deep Learning, Neural Networks, Artificial Intelligence
总引用数: 150000+

近期论文 (前10篇):
  1. Forward-Forward: A new learning algorithm for neural networks
     年份: 2022
     引用数: 150

  2. Deep Learning
     年份: 2015
     引用数: 50000+
```

### JSON Format

```json
[
  {
    "title": "Attention Is All You Need",
    "authors": "Vaswani, A., Shazeer, N., Parmar, N., et al.",
    "abstract": "The dominant sequence transduction models...",
    "url": "https://arxiv.org/abs/1706.03762"
  }
]
```

## Use Cases

### Case 1: Literature Review

```bash
# Find papers on a specific topic
python google_scholar_search.py search --query "transformer architecture" --results 30 --format json --output papers.json
```

### Case 2: Track Specific Author

```bash
# Find papers by a specific author
python google_scholar_search.py advanced --query "machine learning" --author "Yann LeCun" --results 20
```

### Case 3: Recent Research

```bash
# Find recent papers in a field
python google_scholar_search.py advanced --query "large language models" --year-start 2022 --year-end 2024
```

### Case 4: Author Analysis

```bash
# Get author's research profile
python google_scholar_search.py author --name "Yoshua Bengio"
```

## Project Structure

```
google-scholar-search-skill/
├── SKILL.md                    # Claude Code skill definition
├── google_scholar_search.py    # Core search script
├── README.md                   # Documentation
└── requirements.txt            # Python dependencies
```

## Dependencies

- **Python 3.8+**
- **requests**: HTTP requests
- **beautifulsoup4**: HTML parsing
- **scholarly**: Google Scholar author information

## FAQ

### Q: Is this tool official?

**A:** No, Google Scholar doesn't provide an official API. This tool uses web scraping and may be affected by Google's anti-bot measures.

### Q: Why do searches fail sometimes?

**A:** Google Scholar may block automated requests. If you encounter issues, try:
- Waiting a few minutes between requests
- Using Semantic Scholar or PubMed as alternatives
- Checking your internet connection

### Q: Can I download PDFs?

**A:** This tool only provides links to papers. Use the [sci-hub-search-skill](https://github.com/JackKuo666/sci-hub-search-skill) to download PDFs.

### Q: What's the difference between basic and advanced search?

**A:** Basic search only uses keywords. Advanced search allows you to filter by author and/or year range.

### Q: How accurate is the author information?

**A:** Author information is retrieved from Google Scholar profiles. It's generally accurate but depends on the author maintaining their profile.

## Troubleshooting

### Issue: "Failed to fetch data"

**Solution:** Google Scholar may be blocking requests. Try:
- Wait a few minutes and try again
- Use a different network or VPN
- Consider using Semantic Scholar or PubMed instead

### Issue: "scholarly library not installed"

**Solution:** Install the scholarly library:
```bash
pip install scholarly
```

### Issue: "Author not found"

**Solution:** The author name may not match exactly. Try variations of the name or search for their papers instead.

## Limitations

- Google Scholar doesn't provide an official API
- Web scraping may be unstable or blocked
- Rate limiting may apply
- Results may vary based on location and time
- For stable access, consider using Semantic Scholar or PubMed APIs

## Related Projects

- [Google-Scholar-MCP-Server](https://github.com/JackKuo666/Google-Scholar-MCP-Server): MCP server for Google Scholar integration
- [SemanticScholar-Search-Skill](https://github.com/JackKuo666/semanticScholar-search-skill): Search Semantic Scholar database
- [PubMed-Search-Skill](https://github.com/JackKuo666/pubmed-search-skill): Search biomedical literature
- [Sci-Hub-Search-Skill](https://github.com/JackKuo666/sci-hub-search-skill): Download papers from Sci-Hub

## Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

## Contact

- GitHub: [JackKuo666/google-scholar-search-skill](https://github.com/JackKuo666/google-scholar-search-skill)
- GitHub Issues: [Submit Issues](https://github.com/JackKuo666/google-scholar-search-skill/issues)

## License

This project is licensed under the **MIT License**.

## Disclaimer

This tool uses web scraping to access Google Scholar, which doesn't provide an official API. Use responsibly and be aware that Google may block automated requests. For stable access to academic literature, consider using official APIs like Semantic Scholar or PubMed.

## Acknowledgments

- [Google Scholar](https://scholar.google.com/) for the academic search engine
- [scholarly](https://pypi.org/project/scholarly/) for the Python library
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) for HTML parsing
- Built based on the [sci-data-extractor](https://github.com/JackKuo666/sci-data-extractor) skill template
