# Sci-Hub-Search

> **AI-Powered Academic Paper Search Tool** - Search and download academic papers through Sci-Hub

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

**Sci-Hub-Search** is a Claude Code Skill designed to help researchers search and download academic papers through Sci-Hub. It provides multiple search methods (DOI, title, keyword) and direct PDF download capabilities.

### Key Features

- **🔍 Multiple Search Modes**: Search by DOI (most accurate), title, or keywords
- **📊 Metadata Extraction**: Get paper information (title, author, year, download URL)
- **📥 PDF Download**: Download papers directly from Sci-Hub with a single command
- **🔄 Automatic Mirror Detection**: Automatically finds working Sci-Hub mirrors
- **📄 Multiple Output Formats**: Console and JSON output options
- **⚙️ Crossref Integration**: Uses CrossRef API for title and keyword searches

## Installation

### Method 1: One-Click Installation via npx (Recommended)

```bash
npx skills add https://github.com/JackKuo666/sci-hub-search-skill.git
```

### Method 2: Git Clone

```bash
# Clone to Claude Code skills directory
git clone https://github.com/JackKuo666/sci-hub-search-skill.git ~/.claude/skills/sci-hub-search-skill
```

### Method 3: Manual Installation

1. Download the project ZIP or clone to local
2. Copy the `sci-hub-search-skill` folder to Claude Code skills directory:
   - **macOS/Linux**: `~/.claude/skills/`
   - **Windows**: `%USERPROFILE%\.claude\skills\`
3. Ensure the folder structure is:

```
~/.claude/skills/sci-hub-search-skill/
├── SKILL.md            # Skill definition file
├── sci_hub_search.py   # Core search script
├── README.md           # Documentation
├── requirements.txt    # Python dependencies
└── .env.example        # Environment variable examples
```

### Install Python Dependencies

**Option 1: Using uv (Recommended - Fastest)**

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
cd ~/.claude/skills/sci-hub-search-skill
uv venv
source .venv/bin/activate  # Linux/macOS
# or .venv\Scripts\activate  # Windows
uv pip install -r requirements.txt
```

**Option 2: Using conda (Best for scientific/research users)**

```bash
cd ~/.claude/skills/sci-hub-search-skill
conda create -n sci-hub-search python=3.11 -y
conda activate sci-hub-search
pip install -r requirements.txt
```

**Option 3: Using venv (Built-in)**

```bash
cd ~/.claude/skills/sci-hub-search-skill
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or .venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Verify Installation

Restart Claude Code or reload skills, then enter in conversation:

```
/sci-hub-search
```

If installed successfully, the skill will be activated.

## Configuration

### Environment Variables (Optional)

The skill works without any configuration - the Sci-Hub library automatically detects available mirrors. You can optionally configure:

Create a `.env` file or set the following environment variables:

```bash
# Optional: Specific Sci-Hub mirror (auto-detected if empty)
export SCIHub_BASE_URL=""

# Optional: Download timeout in seconds
export DOWNLOAD_TIMEOUT="30"
```

## Usage

### Using in Claude Code

#### 1. Search by DOI (Most Accurate)

```
/sci-hub-search Find the paper with DOI 10.1038/nature09492
```

#### 2. Search by Title

```
/sci-hub-search Search for "CRISPR gene editing in mammalian cells"
```

#### 3. Search by Keyword

```
/sci-hub-search Find papers about artificial intelligence in medicine
```

#### 4. Download Paper

```
/sci-hub-search Download the paper with DOI 10.1002/jcad.12075
```

### Direct Command Line Usage

#### Search by DOI

```bash
# Search for a paper using its DOI
python sci_hub_search.py search --doi "10.1002/jcad.12075"
```

#### Search by Title

```bash
# Search for a paper using its title
python sci_hub_search.py search --title "CRISPR gene editing"
```

#### Search by Keyword

```bash
# Search for papers by keyword
python sci_hub_search.py search --keyword "artificial intelligence medicine" --results 10
```

#### Get Metadata

```bash
# Get metadata for a paper
python sci_hub_search.py metadata --doi "10.1002/jcad.12075"
```

#### Download PDF

```bash
# Download using DOI
python sci_hub_search.py download --doi "10.1002/jcad.12075" --output paper.pdf

# Download using direct URL
python sci_hub_search.py download --url "https://sci-hub.se/xxxxx" --output paper.pdf
```

#### Different Output Formats

```bash
# Output as JSON
python sci_hub_search.py search --doi "10.1002/jcad.12075" --format json --output result.json

# Hide PDF URL from output
python sci_hub_search.py search --doi "10.1002/jcad.12075" --hide-url
```

## Command Reference

### search
Search for papers on Sci-Hub.

| Option | Description |
|--------|-------------|
| `--doi` | Search by DOI (Digital Object Identifier) |
| `--title` | Search by paper title |
| `--keyword` | Search by keyword |
| `--results` | Number of results for keyword search (default: 10) |
| `--output` | Output file path |
| `--format` | Output format: console, json |
| `--hide-url` | Hide PDF URL from output |

### metadata
Get metadata for a paper.

| Option | Description |
|--------|-------------|
| `--doi` | DOI (required) |
| `--output` | Output file path |
| `--format` | Output format: console, json |

### download
Download a paper PDF.

| Option | Description |
|--------|-------------|
| `--doi` | DOI to search and download |
| `--url` | Direct PDF URL |
| `--output` | Output PDF file path (required) |

## Output Formats

### Console Output
```
标题: Choosing Assessment Instruments for Posttraumatic Stress Disorder Screening and Outcome Research
作者: Weathers, F. W., et al.
年份: 2023
DOI: 10.1002/jcad.12075
PDF URL: https://sci-hub.se/10.1002/jcad.12075
```

### JSON Format
```json
{
  "doi": "10.1002/jcad.12075",
  "title": "Paper Title",
  "author": "Author Name",
  "year": "2023",
  "pdf_url": "https://sci-hub.se/xxxxx",
  "status": "success"
}
```

## Use Cases

### Case 1: Download Known Paper

```bash
# You have the DOI from a reference list
python sci_hub_search.py download --doi "10.1038/nature09492" --output nature_paper.pdf
```

### Case 2: Find Paper by Title

```bash
# You remember the title but not the DOI
python sci_hub_search.py search --title "Deep learning for genomics"
```

### Case 3: Explore Research Area

```bash
# Discover papers in a specific field
python sci_hub_search.py search --keyword "single cell RNA sequencing" --results 20 --format json --output papers.json
```

### Case 4: Batch Download

```bash
# Download multiple papers from a list
for doi in $(cat doi_list.txt); do
    python sci_hub_search.py download --doi "$doi" --output "papers/${doi}.pdf"
done
```

## Project Structure

```
sci-hub-search-skill/
├── SKILL.md              # Claude Code skill definition
├── sci_hub_search.py     # Core search script
├── README.md             # Documentation
├── requirements.txt      # Python dependencies
└── .env.example          # Environment variable examples
```

## Dependencies

- **Python 3.8+**
- **scihub**: Sci-Hub API wrapper
- **requests**: HTTP requests
- **python-dotenv**: Environment variable management (optional)

## FAQ

### Q: Is this tool legal?

**A:** The legality of using Sci-Hub varies by jurisdiction. This tool is for research and educational purposes. Please respect copyright laws in your region.

### Q: Why does DOI search fail sometimes?

**A:** Some papers may not be available on Sci-Hub, or the Sci-Hub mirrors may be temporarily down. The tool will report "not_found" in these cases.

### Q: How does title search work?

**A:** Title search uses the CrossRef API to find the DOI first, then searches Sci-Hub using that DOI. This ensures more accurate results.

### Q: Can I specify a particular Sci-Hub mirror?

**A:** Yes, set the `SCIHUB_BASE_URL` environment variable to a specific mirror (e.g., `https://sci-hub.se`).

### Q: What's the download timeout?

**A:** Default is 30 seconds. You can adjust this by setting the `DOWNLOAD_TIMEOUT` environment variable.

## Troubleshooting

### Issue: "No papers found in CrossRef"

**Solution:** The title might not match exactly. Try using a shorter, more distinctive portion of the title, or use keyword search instead.

### Issue: Download fails or times out

**Solution:** This could be due to:
- Sci-Hub mirror is down (try again later or specify a different mirror)
- Slow internet connection (increase DOWNLOAD_TIMEOUT)
- Paper not available on Sci-Hub

### Issue: SSL/HTTPS errors

**Solution:** The tool automatically disables SSL warnings for Sci-Hub downloads. If you still have issues, make sure you have `urllib3` installed.

## Related Projects

- [Sci-Hub-MCP-Server](https://github.com/JackKuo666/Sci-Hub-MCP-Server): MCP server for Sci-Hub integration
- [PubMed-Search-Skill](https://github.com/JackKuo666/pubmed-search-skill): Search PubMed biomedical literature
- [Sci-Data-Extractor](https://github.com/JackKuo666/sci-data-extractor): Extract data from scientific paper PDFs

## Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

## Contact

- GitHub: [JackKuo666/sci-hub-search-skill](https://github.com/JackKuo666/sci-hub-search-skill)
- GitHub Issues: [Submit Issues](https://github.com/JackKuo666/sci-hub-search-skill/issues)

## License

This project is licensed under the **MIT License**.

## Disclaimer

**This tool is for research and educational purposes only.** Please respect copyright laws and use this tool responsibly. The authors do not endorse or encourage any copyright infringement. Users are responsible for ensuring their use of this tool complies with local laws and regulations.

## Acknowledgments

- [Sci-Hub](https://sci-hub.se) for providing access to scientific knowledge
- [scihub PyPI package](https://pypi.org/project/scihub/) for the Python library
- Built based on the [sci-data-extractor](https://github.com/JackKuo666/sci-data-extractor) skill template

---

**Note**: This tool accesses academic papers through Sci-Hub. Always verify the legality of accessing papers in your jurisdiction and respect copyright.
