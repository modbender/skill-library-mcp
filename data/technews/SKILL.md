---
name: technews
description: Fetches top stories from TechMeme, summarizes linked articles, and highlights social media reactions. Use when user wants tech news or says /technews.
metadata: {"openclaw":{"emoji":"📰"}}
---

# TechNews Skill

Fetches top stories from TechMeme, summarizes linked articles, and highlights social media buzz.

## Usage

**Command:** `/technews`

Fetches the top 10 stories from TechMeme, provides summaries from the linked articles, and highlights notable social media reactions.

## Setup

This skill requires:
- Python 3.9+
- `requests` and `beautifulsoup4` packages
- Optional: `tiktoken` for token-aware truncation

Install dependencies:
```bash
pip install requests beautifulsoup4
```

## Architecture

The skill works in three stages:

1. **Scrape TechMeme** — `scripts/techmeme_scraper.py` fetches and parses top stories
2. **Fetch Articles** — `scripts/article_fetcher.py` retrieves article content in parallel
3. **Summarize** — `scripts/summarizer.py` generates summaries and finds social reactions

## Commands

### /technews

Fetches and presents top tech news stories.

**Output includes:**
- Story title and original link
- AI-generated summary
- Social media highlights (Twitter reactions)
- Relevance score based on topic preferences

## How It Works

1. Scrapes TechMeme's homepage for top stories (by default, top 10)
2. For each story, fetches the linked article
3. Generates a concise summary (2-3 sentences)
4. Checks for notable social media reactions
5. Presents results in a clean, readable format

## State

- `<workspace>/memory/technews_history.json` — cache of recently fetched stories to avoid repeats

## Examples

- `/technews` — Get the latest tech news summary

## Future Expansion

This skill is designed to be extended to other sources:
- Hacker News (`/hn`)
- Reddit (`/reddit`)
- Other tech news aggregators

The modular architecture allows adding new source handlers without changing core functionality.
