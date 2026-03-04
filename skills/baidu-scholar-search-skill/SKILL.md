---
name: baidu-scholar-search-skill
description: Baidu Scholar Search - Search Chinese and English academic literature (journals, conferences, papers, etc.)
homepage: https://xueshu.baidu.com/
metadata: { "openclaw": { "emoji": "🔬", "requires": { "bins": ["curl"] ,"env":["BAIDU_API_KEY"]},"primaryEnv":"BAIDU_API_KEY" }  }
---

# Baidu Scholar Search Skill

## Features
Search Chinese and English academic literature by keyword, including journal papers, conference papers, dissertations, etc.

## LLM Usage Guide

### Basic Usage
```bash
bash baidu_scholar_search.sh "keyword"
bash baidu_scholar_search.sh "keyword" page_number
bash baidu_scholar_search.sh "keyword" page_number include_abstract
```

### Parameter Description
| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| keyword | ✅ | - | Search term, e.g., "machine learning" or "cancer immunotherapy" |
| page_number | ❌ | 0 | Starts from 0, 0=first page, 1=second page |
| include_abstract | ❌ | false | true=return detailed abstract, false=return only title and basic info |

### Default Behavior
- **No abstract returned** - Fast response, suitable for quickly browsing literature lists
- Start from page 1

### When to Return Abstract
- User explicitly requests "abstract", "include abstract", "detailed content"
- User says "I need to understand the paper content", "give me detailed explanation"

### When NOT to Return Abstract
- User only says "search", "retrieve", "check"
- User says "see what's available", "help me find"
- No explicit request for abstract information

## API Specification

### Endpoint
`GET https://qianfan.baidubce.com/v2/tools/baidu_scholar/search`

### Request Parameters
- `wd` - Search keyword (required)
- `pageNum` - Page number (optional, default 0)
- `enable_abstract` - Whether to return abstract (optional, default false)

### Response Fields
- `title` - Paper title
- `abstract` - Abstract (only returned when enable_abstract=true)
- `keyword` - Keywords
- `paperId` - Paper ID
- `publishYear` - Publication year
- `url` - Baidu Scholar link

## Examples

### Quick Search (No Abstract)
```bash
bash baidu_scholar_search.sh "cancer immunotherapy"
# Returns title, year, keywords and other basic information
```

### Detailed Search (With Abstract)
```bash
bash baidu_scholar_search.sh "cancer immunotherapy" 0 true
# Returns detailed information including abstract
```

### Pagination Search
```bash
bash baidu_scholar_search.sh "machine learning" 1
# Search page 2 (no abstract)
```

## Notes
- Need to set `BAIDU_API_KEY` environment variable
- Keywords must be wrapped in quotes
- Returning abstract significantly increases response time
- Both Chinese and English keywords are supported
