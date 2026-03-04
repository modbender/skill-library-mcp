# Semantic Scholar Search

> **AI-Powered Academic Paper Search Tool** - Search academic papers through Semantic Scholar

## Description

Search for academic papers, get detailed paper information, author profiles, and citation data through Semantic Scholar API. This skill provides comprehensive academic literature search capabilities with rich metadata extraction.

## Features

- **Paper Search**: Search papers by keywords, titles, or authors
- **Paper Details**: Get detailed information including abstract, authors, citations
- **Author Profiles**: Retrieve author information, publication count, h-index
- **Citation Analysis**: Get citations and references for any paper
- **Rich Metadata**: Access venue, publication type, citation counts
- **JSON Output**: Export results in JSON format for further processing

## Usage

```
/semantic-scholar-search Search for papers about "deep learning in computer vision"
/semantic-scholar-search Get details for paper ID "10.1038/nature12373"
/semantic-scholar-search Find author information for author ID "1741101"
/semantic-scholar-search Get citations and references for paper "10.1038/nature12373"
```

## Examples

### Search Papers

```
/semantic-scholar-search Find papers about "transformer architecture in natural language processing"
```

### Get Paper Details

```
/semantic-scholar-search Get detailed information for paper with ID "10.1038/nature12373"
```

### Get Author Profile

```
/semantic-scholar-search Get author profile for author ID "1741101"
```

### Citation Analysis

```
/semantic-scholar-search Show citations and references for paper "10.1038/nature12373"
```

## Command Reference

### search

Search for papers on Semantic Scholar.

| Option | Description |
|--------|-------------|
| `--query` | Search query string |
| `--results` | Number of results (default: 10) |
| `--output` | Output file path |
| `--format` | Output format: console, json |

### paper

Get detailed information about a specific paper.

| Option | Description |
|--------|-------------|
| `--paper-id` | Paper ID or DOI (required) |
| `--output` | Output file path |
| `--format` | Output format: console, json |

### author

Get author details and statistics.

| Option | Description |
|--------|-------------|
| `--author-id` | Author ID (required) |
| `--output` | Output file path |
| `--format` | Output format: console, json |

### citations

Get citations and references for a paper.

| Option | Description |
|--------|-------------|
| `--paper-id` | Paper ID or DOI (required) |
| `--limit` | Number of citations/references to return (default: 10) |
| `--output` | Output file path |
| `--format` | Output format: console, json |

## Output Format

### Console Output

```
标题: Attention Is All You Need
作者: Vaswani, A., et al.
年份: 2017
引用数: 50000+
会议: NeurIPS
摘要: This paper proposes the Transformer architecture...
```

### JSON Format

```json
{
  "paperId": "10.1038/nature12373",
  "title": "Paper Title",
  "abstract": "Paper abstract...",
  "year": "2020",
  "authors": [{"name": "Author Name", "authorId": "12345"}],
  "citationCount": 150,
  "venue": "Nature",
  "url": "https://www.semanticscholar.org/paper/..."
}
```

## Notes

- Semantic Scholar API is free and doesn't require authentication
- You can use DOI as paper ID (e.g., "10.1038/nature12373")
- Search results are ranked by relevance
- Citation counts are updated regularly
- Some papers may not have abstracts available

## Related Skills

- [sci-data-extractor](../sci-data-extractor/) - Extract data from scientific paper PDFs
- [pubmed-search-skill](../pubmed-search-skill/) - Search biomedical literature on PubMed
- [sci-hub-search-skill](../sci-hub-search-skill/) - Download papers from Sci-Hub
