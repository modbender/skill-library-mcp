---
name: google-search
slug: google-search-grounding
description: >
  Google web search via Gemini Search Grounding (primary) and Custom Search JSON API (fallback).
  Use for: (1) Synthesized answers with citations (grounded search), (2) Raw link results with snippets,
  (3) Image search. Excellent Hebrew support. Preferred over built-in web_search (Perplexity).
version: 2.1.0
author: Leo 🦁
tags: [search, google, web, grounding, gemini, news, hebrew, images, citations]
metadata: {"clawdbot":{"emoji":"🔍","requires":{"env":["GOOGLE_API_KEY"]},"primaryEnv":"GOOGLE_API_KEY","secondaryEnv":["GOOGLE_CSE_CX","GOOGLE_SEARCH_LANG","GOOGLE_SEARCH_COUNTRY"],"install":[{"id":"pip","kind":"pip","package":"google-genai","label":"Install google-genai library"}],"notes":"GOOGLE_CSE_CX is required only for raw/image modes (Custom Search API). The default search mode (Gemini grounding) needs only GOOGLE_API_KEY. No hardcoded CSE IDs — users must supply their own."}}
allowed-tools: [exec]
---

# Google Search 🔍

Google web search powered by Gemini 2.5 Flash with Search Grounding + Custom Search API.

**⭐ This is the PRIMARY web search tool. Prefer over built-in `web_search` (Perplexity).**

## Requirements

- `GOOGLE_API_KEY` environment variable
- Enable in Google Cloud Console: Gemini API, Custom Search JSON API

## Configuration

| Env Variable | Default | Description |
|---|---|---|
| `GOOGLE_API_KEY` | — | **Required.** Google API key |
| `GOOGLE_CSE_CX` | — | Custom Search Engine ID (required for raw/image modes) |
| `GOOGLE_SEARCH_LANG` | `he` | Default language code (he, en, ar, ja, etc.) |
| `GOOGLE_SEARCH_COUNTRY` | `IL` | Default country code (IL, US, DE, etc.) |

Set in OpenClaw config:
```json
{
  "env": {
    "GOOGLE_API_KEY": "AIza...",
    "GOOGLE_SEARCH_LANG": "he",
    "GOOGLE_SEARCH_COUNTRY": "IL"
  }
}
```

## Script Location

```bash
python3 skills/google-search/lib/google_search.py <mode> "query" [options]
```

---

## Output Modes

- **Text mode** (default): Best for most use cases. Clean readable output with answer, sources, and search queries.
- **JSON mode** (`--json`): For programmatic processing. Includes confidence scores, grounding supports, and search queries.

---

## Modes

### search — Grounded Search (Default, Recommended)

Gemini 2.0 Flash + Google Search tool → **synthesized answer with numbered citations**.

```bash
python3 lib/google_search.py search "query" [--lang he] [--country IL] [--json]
```

**When to use:** Questions, current events, "what is X", Hebrew queries, anything needing a direct answer.

**Examples:**
```bash
# Hebrew (default)
python3 lib/google_search.py search "מזג אוויר תל אביב"

# English override
python3 lib/google_search.py search "latest AI news" --lang en --country US

# JSON output
python3 lib/google_search.py search "OpenAI GPT-5 release date" --json
```

**Output format:**
```
<Synthesized answer text>

Sources:
  1. Source Title
     https://example.com/article
  2. Another Source
     https://example.com/other
```

---

### raw — Raw Search Results

Custom Search JSON API → **links with titles and snippets**.

```bash
python3 lib/google_search.py raw "query" [-n 5] [--lang he] [--country IL] [--json]
```

**When to use:** Need actual URLs, research, building reference lists, when you want links not answers.

**Examples:**
```bash
python3 lib/google_search.py raw "python asyncio tutorial" -n 5
python3 lib/google_search.py raw "best restaurants tel aviv" --json
python3 lib/google_search.py raw "rust vs go performance" -n 3 --lang en
```

**Output format:**
```
1. Page Title
   https://example.com/page
   Brief snippet from the page...

2. Another Page
   https://example.com/other
   Another snippet...
```

---

### image — Image Search

Custom Search image search → **image URLs with titles**.

```bash
python3 lib/google_search.py image "query" [-n 5] [--lang he] [--country IL] [--json]
```

**When to use:** Finding images, visual references, thumbnails.

**Examples:**
```bash
python3 lib/google_search.py image "aurora borealis" -n 5
python3 lib/google_search.py image "תל אביב חוף" --json
```

---

## Options Reference

| Option | Applies To | Description | Default |
|---|---|---|---|
| `--lang CODE` | all | Language code (he, en, ar, ja…) | env `GOOGLE_SEARCH_LANG` (he) |
| `--country CODE` | all | Country code (IL, US, DE…) | env `GOOGLE_SEARCH_COUNTRY` (IL) |
| `-n NUM` | raw, image | Number of results (1–10) | 10 |
| `--json` | all | Structured JSON output | off |

**Language resolution order:** `--lang` flag → `GOOGLE_SEARCH_LANG` env → None (auto)
**Country resolution order:** `--country` flag → `GOOGLE_SEARCH_COUNTRY` env → None (auto)

---

## Error Handling

- **Missing API key:** Clear error message with setup instructions.
- **429 Rate Limit:** Automatic retry once after 5-second wait.
- **Network errors:** Descriptive error with cause.
- **No results:** Clean "No results found." message.
- **Timeout:** 30-second timeout on all HTTP requests.

---

## Quota & Rate Limits

| API | Free Tier | Rate Limit |
|---|---|---|
| Gemini API (grounded search) | Generous free tier | ~15 RPM (free), higher on paid |
| Custom Search JSON API (raw/image) | 100 queries/day | 10K queries/day (paid) |

**On 429 errors:** Script retries once automatically. If quota exhausted, fall back to built-in `web_search` (Perplexity).

---

## Multilingual Support

Works with queries in any language. Hebrew is the default:

```bash
# Hebrew (default, no flags needed)
python3 lib/google_search.py search "חדשות טכנולוגיה"

# English
python3 lib/google_search.py search "technology news" --lang en

# Arabic
python3 lib/google_search.py search "أخبار التكنولوجيا" --lang ar
```

---

## Install

```bash
bash skills/google-search/install.sh
```
