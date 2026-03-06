---
name: Google Scholar Search
description: Search for academic literature and research papers through Google
  Scholar. This skill provides powerful search capabilities with advanced
  filtering options including author-specific searches and ye...
---

# Google Scholar Search

> **AI-Powered Academic Literature Search Tool** - Search academic papers through Google Scholar

## Description

Search for academic literature and research papers through Google Scholar. This skill provides powerful search capabilities with advanced filtering options including author-specific searches and year-based filtering.

## Features

- **Keyword Search**: Search papers by keywords, titles, or topics
- **Advanced Search**: Filter results by author and publication year range
- **Author Profiles**: Retrieve detailed author information including interests and citation counts
- **Rich Metadata**: Access titles, authors, abstracts, and direct links
- **JSON Export**: Export results in JSON format for further processing

## Usage

```
/google-scholar-search Search for papers about "machine learning in healthcare"
/google-scholar-search Find papers by author "Andrew Ng" about "deep learning"
/google-scholar-search Search for "neural networks" from 2018 to 2022
/google-scholar-search Get author information for "Geoffrey Hinton"
```

## Examples

### Basic Search

```
/google-scholar-search Find papers about "transformer architecture"
```

### Advanced Search with Author

```
/google-scholar-search Search for "deep learning" by author "Yann LeCun"
```

### Search with Year Range

```
/google-scholar-search Find papers about "GANs" from 2018 to 2023
```

### Author Information

```
/google-scholar-search Get author profile for "Yoshua Bengio"
```

## Command Reference

### search

Search papers by keywords.

| Option | Description |
|--------|-------------|
| `--query` | Search query string |
| `--results` | Number of results (default: 10) |
| `--output` | Output file path |
| `--format` | Output format: console, json |

### advanced

Advanced search with filters.

| Option | Description |
|--------|-------------|
| `--query` | Search query string |
| `--author` | Filter by author name |
| `--year-start` | Start year (optional) |
| `--year-end` | End year (optional) |
| `--results` | Number of results (default: 10) |
| `--output` | Output file path |
| `--format` | Output format: console, json |

### author

Get author profile and publications.

| Option | Description |
|--------|-------------|
| `--name` | Author name |
| `--output` | Output file path |
| `--format` | Output format: console, json |

## Output Format

### Console Output

```
标题: Attention Is All You Need
作者: Vaswani, A., et al.
摘要: This paper proposes the Transformer architecture...
链接: https://...
```

### Author Output

```
姓名: Geoffrey Hinton
机构: University of Toronto
研究领域: Machine Learning, Deep Learning, Neural Networks
总引用数: 150000+
近期论文:
  - 1. Forward-Forward (2022) - 引用数: 150
  - 2. Deep Learning (2015) - 引用数: 50000+
```

## Notes

- Google Scholar doesn't provide an official API - this tool uses web scraping
- Search results may vary due to Google's anti-bot measures
- For stable access, consider using Semantic Scholar or PubMed APIs
- Author search returns the first matching author profile

## Related Skills

- [semanticscholar-search-skill](../semanticscholar-search-skill/) - Search Semantic Scholar database
- [pubmed-search-skill](../pubmed-search-skill/) - Search biomedical literature
- [sci-hub-search-skill](../sci-hub-search-skill/) - Download papers from Sci-Hub
