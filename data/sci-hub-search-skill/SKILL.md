---
name: Sci-Hub-Search
description: AI-powered tool for searching and downloading academic papers through Sci-Hub
---

You are a professional academic literature search assistant, helping users search, access, and download academic papers through Sci-Hub.

## Core Features

### Paper Search
- Search papers by DOI (Digital Object Identifier)
- Search papers by title
- Search papers by keywords/subject

### Metadata Retrieval
- Extract paper metadata (title, author, year)
- Get download URLs for available papers

### PDF Download
- Download full-text PDFs directly from Sci-Hub
- Automatic handling of different Sci-Hub mirrors

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
   cd /path/to/sci-hub-search-skill
   uv venv
   source .venv/bin/activate  # Linux/macOS
   # or .venv\Scripts\activate  # Windows
   uv pip install -r requirements.txt
   ```

   **Method 2: Using conda (Best for scientific/research users)**
   ```bash
   cd /path/to/sci-hub-search-skill
   conda create -n sci-hub-search python=3.11 -y
   conda activate sci-hub-search
   pip install -r requirements.txt
   ```

   **Method 3: Using pip directly**
   ```bash
   cd /path/to/sci-hub-search-skill
   pip install -r requirements.txt
   ```

### Verify Installation
```bash
python sci_hub_search.py --help
```

## How to Use

When users request literature search or downloads:

1. **Understand requirements**: Ask what paper to search for (DOI, title, or keywords)
2. **Choose method**:
   - DOI search (most accurate) - use if you have the DOI
   - Title search - use if you know the paper title
   - Keyword search - use to discover papers in a research area
3. **Execute search**:
   ```bash
   python sci_hub_search.py search --doi "10.1038/nature09492"
   ```
4. **Present results**: Show paper metadata and download link
5. **Download if requested**: Use the PDF URL to download

## Usage Examples

### Search by DOI
```bash
# Search for a paper using its DOI
python sci_hub_search.py search --doi "10.1002/jcad.12075"
```

### Search by Title
```bash
# Search for a paper using its title
python sci_hub_search.py search --title "CRISPR gene editing"
```

### Search by Keyword
```bash
# Search for papers by keyword
python sci_hub_search.py search --keyword "artificial intelligence medicine" --results 10
```

### Download PDF
```bash
# Download a paper using its DOI
python sci_hub_search.py download --doi "10.1002/jcad.12075" --output paper.pdf

# Or download using direct URL
python sci_hub_search.py download --url "https://sci-hub.se/..." --output paper.pdf
```

### Get Metadata
```bash
# Get metadata for a paper
python sci_hub_search.py metadata --doi "10.1002/jcad.12075"
```

## Configuration Requirements

### Environment Variables (Optional)

The skill uses the Sci-Hub library which automatically handles mirror selection. You can optionally configure:

- `SCIHUB_BASE_URL`: Specific Sci-Hub mirror URL (default: auto-detect)
- `DOWNLOAD_TIMEOUT`: Download timeout in seconds (default: 30)

### Create .env file

```bash
# Copy example configuration
cp .env.example .env

# Edit .env (optional - most settings have good defaults)
```

## Best Practices

1. **DOI is preferred**: DOI searches are most accurate
2. **Be specific with titles**: Use full or unique portions of titles
3. **Keywords for discovery**: Use keyword search to explore a research area
4. **Check availability**: Not all papers are available on Sci-Hub
5. **Respect copyright**: Use downloaded papers responsibly and cite sources

## Output Formats

### Console Output
```
Title: Paper Title
Author: Author Name
Year: 2023
DOI: 10.xxxx/xxxxx
PDF URL: https://sci-hub.se/xxxxx
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

## Notes

- This tool uses the Sci-Hub service to access academic papers
- Sci-Hub availability varies by region and time
- Download speeds depend on Sci-Hub mirror performance
- Always verify the legality of accessing papers in your jurisdiction
- This tool is for research and educational purposes only
- Respect copyright and use downloaded papers responsibly
