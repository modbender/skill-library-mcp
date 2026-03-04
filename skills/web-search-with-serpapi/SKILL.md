---
name: serpapi-search
description: "Search the web using SerpAPI with customizable engines (Google, Google AI Mode, Bing, etc.). Use when user needs web search results via SerpAPI."
metadata:
  { "openclaw": { "requires": { "python": true, "pip": ["serpapi"] }, "entrypoint": "serpapi_search.py" } }
---

# SerpAPI Search Skill

## Description
Use SerpAPI to fetch search results with support for multiple engines (Google, Google AI Mode, Bing, Yahoo, etc.). Requires a SerpAPI key.

## Parameters
- `query` (required): Search query string.
- `engine` (optional): Search engine (default: `google`). Options: `google`, `google_ai_mode`, `google_images`, `google_maps`, `youtube`

## Example Usage
```python
# Search with Google
serpapi_search(query="2026年2月24日A股市场表现", engine="google")

# Use Google AI Mode
serpapi_search(query="AI最新进展", engine="google_ai_mode")

# Use Google Image for image search
serpapi_search(query="Sunflowers", engine="google_images")
```

## Setup
1. Replace the API key in `serpapi_search.py` with your SerpAPI key.
2. Install dependencies: `pip install serpapi`

## Notes
- Results are returned as text blocks from SerpAPI response.
- API key can be set via environment variable `SERPAPI_API_KEY` for security.