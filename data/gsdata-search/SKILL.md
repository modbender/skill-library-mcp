---
name: GS Data Search
description: A skill that provides a simple interface to search data from
  projects-databus.gsdata.cn API.
---

# GS Data Search

## Description

A skill that provides a simple interface to search data from projects-databus.gsdata.cn API.

## Installation

This skill is automatically available when installed in the Claude Code plugins directory.

## Usage

To use this skill, you need to provide the following parameters:
- project_id: Your project ID
- sign: Your API signature
- keywords: Search keywords
- posttime_start: Start time for post (format: 2026-03-01 00:00:00)
- posttime_end: End time for post (format: 2026-03-01 23:59:59)
- limit: Number of results to return (default: 10)

## Example

```python
from gsdata_search import search

result = search(
    project_id="your_project_id",
    sign="your_signature",
    keywords="your_search_keywords",
    posttime_start="2026-03-01 00:00:00",
    posttime_end="2026-03-01 23:59:59",
    limit=20
)

print(result)
```

## API Reference

### search(project_id, sign, keywords, posttime_start, posttime_end, limit=10)

Searches the GS Data API for data matching the keywords.

#### Parameters:
- project_id (str): The project ID
- sign (str): The API signature
- keywords (str): Keywords to search for
- posttime_start (str): Start time for post (format: 2026-03-01 00:00:00)
- posttime_end (str): End time for post (format: 2026-03-01 23:59:59)
- limit (int): Number of results to return (default: 10)

#### Returns:
- list: The search results as a Python list of dictionaries, each containing only the following fields:
  - news_title: News title
  - news_uuid: News UUID
  - media_name: Media name
  - news_posttime: Posting time
  - news_emotion: News emotion (positive/negative/neutral)
  - news_url: News URL
  - news_digest: News digest

#### Response Structure:
```python
[
    {
        "news_title": "News title",
        "news_uuid": "123456789",
        "media_name": "Media name",
        "news_posttime": "2026-03-01 10:30:00",
        "news_emotion": "positive",
        "news_url": "https://example.com/news/123",
        "news_digest": "News digest..."
    }
]
```

## Notes

- Make sure you have valid project_id and sign credentials
- The API has a timeout of 30 seconds
- Results are returned as JSON data
