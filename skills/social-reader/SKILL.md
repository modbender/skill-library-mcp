---
name: social-reader
description: Social media content scraping and automation skill. Supports real-time single post reading, as well as scheduled batch patrol, LLM distillation, and review notifications.
---

# Social Reader Skill

This skill provides a social media content scraping and monitoring workflow. It offers two usage modes:
- **Interactive Mode**: Agent fetches a single post in real-time for reading, discussion, or reply generation within a conversation.
- **Pipeline Mode**: Background batch patrol of sources, with LLM distillation and review notifications.

## Dependencies

```bash
pip install requests
```

## Configuration Files

| File | Purpose |
|------|---------|
| `prompt.txt` | LLM system prompt for the Processor node |
| `sources.json` | List of monitored accounts and fetch intervals (pipeline mode) |
| `input_urls.txt` | Manually entered post URLs (one per line, `#` for comments) |
| `seen_ids.json` | Deduplication cache for seen post IDs (pipeline mode only) |
| `pending_tweets.json` | Queue of unprocessed posts from the Watcher |
| `drafts.json` | LLM-distilled drafts from the Processor |
| `archive.json` | Archived history records |

### Environment Variables (required only for Pipeline Mode Processor)

| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_API_KEY` | LLM API key (required) | None |
| `LLM_BASE_URL` | API endpoint | `https://api.openai.com/v1` |
| `LLM_MODEL` | Model name | `gpt-4o-mini` |

---

## Mode 1: Agent Interactive Call (Recommended)

When a user sends a social media post link and asks you to "read and discuss" or "generate a quality reply", **call `fetcher.py` directly — do NOT use `run_pipeline.py`**.

`run_pipeline.py` triggers deduplication cache, fixed LLM distillation, and browser popups, which are unsuitable for interactive scenarios.

### Usage Example

```python
import sys

skill_dir = r"d:\AIWareTop\Agent\openclaw-skills\social-reader"
if skill_dir not in sys.path:
    sys.path.append(skill_dir)

from fetcher import get_tweet

result = get_tweet("https://x.com/user/status/123456")

if result.get("success"):
    content = result["content"]
    # Now you can discuss the content with the user or generate a reply
```

### `get_tweet()` Return Structure

```json
{
  "source": "fxtwitter",
  "success": true,
  "type": "tweet",
  "content": {
    "text": "Post body text",
    "author": "Display name",
    "username": "Username handle",
    "created_at": "Publish time",
    "likes": 123,
    "retweets": 45,
    "views": 6789,
    "replies": 10,
    "media": ["image_url_1", "image_url_2"]
  }
}
```

When `type` is `"article"` (long-form post), `content` additionally contains:
- `title`: Article title
- `preview`: Preview text
- `full_text`: Full article body (Markdown format)
- `cover_image`: Cover image URL

This call is completely stateless — it writes no cache files and triggers no notification services.

---

## Mode 2: Background Pipeline Batch Processing

Use `run_pipeline.py` to chain Watcher → Processor → Action nodes. Suitable for scheduled tasks or batch processing.

### Three Core Nodes

1. **Watcher** (`watcher.py`)
   - Reads `input_urls.txt` or `sources.json`, deduplicates via `seen_ids.json`, writes new posts to `pending_tweets.json`.

2. **Processor** (`processor.py`)
   - Reads `pending_tweets.json`, calls LLM to generate commentary, outputs to `drafts.json`.
   - Requires `LLM_API_KEY` environment variable.

3. **Action** (`notifier.py`)
   - Starts a local HTTP review server (port 18923), opens a browser review page with approve/reject/rewrite/archive controls.

### CLI Examples

```bash
# Full pipeline
python run_pipeline.py

# Specific URL
python run_pipeline.py https://x.com/elonmusk/status/123456

# Single node execution
python run_pipeline.py --watch-only
python run_pipeline.py --process-only
python run_pipeline.py --notify-only
```
