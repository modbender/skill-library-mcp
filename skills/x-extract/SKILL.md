---
name: x-extract
description: Extract tweet content from x.com URLs without credentials using browser automation. Use when user asks to "extract tweet", "download x.com link", "get tweet content", or provides x.com/twitter.com URLs for content extraction. Works without Twitter API credentials.
---

# X.com Tweet Extraction

Extract tweet content (text, media, author, metadata) from x.com URLs without requiring Twitter/X credentials.

## How It Works

Uses OpenClaw's browser tool to load the tweet page, then extracts content from the rendered HTML.

## Workflow

### 1. Validate URL

Check that the URL is a valid x.com/twitter.com tweet:
- Must contain `x.com/*/status/` or `twitter.com/*/status/`
- Extract tweet ID from URL pattern: `/status/(\d+)`

### 2. Open in Browser

```javascript
browser action=open profile=openclaw targetUrl=<x.com-url>
```

Wait for page load (targetId returned).

### 3. Capture Snapshot

```javascript
browser action=snapshot targetId=<TARGET_ID> snapshotFormat=aria
```

### 4. Extract Content

From the snapshot, extract:

**Required fields:**
- **Tweet text**: Look for role=article containing the main tweet content
- **Author**: role=link with author name/handle (usually @username format)
- **Timestamp**: role=time element

**Optional fields:**
- **Media**: role=img or role=link containing /photo/, /video/
- **Engagement**: Like count, retweet count, reply count (in role=group or role=button)
- **Thread context**: If tweet is part of thread, note previous/next tweet references

### 5. Format Output

Output as structured markdown:

```markdown
# Tweet by @username

**Author:** Full Name (@handle)  
**Posted:** YYYY-MM-DD HH:MM  
**Source:** <original-url>

---

<Tweet text content here>

---

**Media:**
- ![Image 1](<media-url-1>)
- ![Image 2](<media-url-2>)

**Engagement:**
- 👍 Likes: 1,234
- 🔄 Retweets: 567
- 💬 Replies: 89

**Thread:** [Part 2/5] | [View full thread](<thread-url>)
```

### 6. Download Media (Optional)

If user requests `--download-media` or "download images":

1. Extract all media URLs from snapshot
2. Use `exec` with `curl` or `wget` to download:
   ```bash
   curl -L -o "tweet-{tweetId}-image-{n}.jpg" "<media-url>"
   ```
3. Report downloaded files with paths

## Error Handling

**If page fails to load:**
- Check if URL is valid
- Try alternative: replace `x.com` with `twitter.com` (still works)
- Some tweets may require login (controversial, age-restricted) - report to user

**If content extraction fails:**
- X.com layout may have changed - check references/selectors.md
- Provide raw snapshot to user for manual review
- Report which fields were successfully extracted

## Common Selectors

See [references/selectors.md](references/selectors.md) for detailed CSS/ARIA selectors used by x.com (updated as layout changes).

## Limitations

- **No credentials**: Cannot access protected tweets, DMs, or login-required content
- **Rate limiting**: X.com may block excessive automated requests
- **Layout changes**: Selectors may break if X updates their HTML structure
- **Dynamic content**: Some content (comments, threads) may load lazily

## Examples

**Extract single tweet:**
```
User: "Extract this tweet: https://x.com/vista8/status/2019651804062241077"
Agent: [Opens browser, captures snapshot, formats markdown output]
```

**Extract with media download:**
```
User: "Get the tweet text and download all images from https://x.com/user/status/123"
Agent: [Extracts content, downloads images to ./downloads/, reports paths]
```

**Thread extraction:**
```
User: "Extract this thread: https://x.com/user/status/456"
Agent: [Detects thread, extracts all tweets in sequence, formats as numbered list]
```
