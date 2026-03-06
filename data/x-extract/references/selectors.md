# X.com Content Selectors

Reference for extracting content from x.com pages using ARIA roles and CSS selectors.

**Last updated:** 2026-02-15  
**X.com layout version:** Current as of Feb 2026

## ARIA Snapshot Selectors (Preferred)

When using `browser action=snapshot snapshotFormat=aria`:

### Tweet Content

- **Main tweet article**: `role=article` (primary tweet container)
- **Tweet text**: Text content within `role=article`, usually in a `<div>` with `lang` attribute
- **Author name**: `role=link` containing author's display name (e.g., "John Doe")
- **Author handle**: `role=link` containing `@username` format
- **Timestamp**: `role=time` with `datetime` attribute
- **Media images**: `role=img` within the tweet article
- **Media links**: `role=link` with `href` containing `/photo/` or `/video/`

### Engagement Metrics

- **Like button**: `role=button` with label containing "Like" or heart emoji
- **Retweet button**: `role=button` with label containing "Retweet" or retweet icon
- **Reply button**: `role=button` with label containing "Reply" or comment icon
- **Share button**: `role=button` with label containing "Share"

Counts appear as text within or adjacent to these buttons.

### Thread Context

- **Thread indicator**: Text like "Show this thread" or numbered indicators "1/5"
- **Previous tweet**: `role=link` with "Show previous tweets" or similar
- **Next tweet**: Following `role=article` elements in snapshot

## CSS Selectors (Fallback)

If ARIA snapshot is not available or incomplete:

### Tweet Content

```css
/* Main tweet container */
article[data-testid="tweet"]

/* Tweet text */
div[data-testid="tweetText"]

/* Author name */
div[data-testid="User-Name"] a

/* Author handle */
div[data-testid="User-Name"] span:contains("@")

/* Timestamp */
time

/* Images */
div[data-testid="tweetPhoto"] img

/* Videos */
div[data-testid="videoPlayer"]
```

### Engagement Metrics

```css
/* Like count */
button[data-testid="like"] span

/* Retweet count */
button[data-testid="retweet"] span

/* Reply count */
button[data-testid="reply"] span

/* View count */
a[href$="/analytics"] span
```

## Content Extraction Patterns

### Text Extraction

Tweet text often includes:
- **Line breaks**: Preserved as `\n` in text content
- **Links**: May appear as shortened t.co URLs or full URLs
- **Mentions**: @username format (clickable links)
- **Hashtags**: #hashtag format (clickable links)
- **Emojis**: Unicode characters

**Pattern:**
```javascript
const tweetText = articleElement.querySelector('[data-testid="tweetText"]').innerText;
```

### Media URL Extraction

**Images:**
```javascript
// Pattern: https://pbs.twimg.com/media/{id}?format=jpg&name=large
const images = Array.from(articleElement.querySelectorAll('img[src*="pbs.twimg.com/media"]'))
  .map(img => img.src.replace(/&name=\w+/, '&name=large')); // Get highest quality
```

**Videos:**
```javascript
// Video preview images
const videoThumbs = Array.from(articleElement.querySelectorAll('img[src*="ext_tw_video_thumb"]'));

// Note: Actual video URLs require additional extraction from video player data
```

### Engagement Numbers

Numbers may be formatted as:
- Raw numbers: `1234`
- Shortened: `1.2K`, `45.6M`
- Localized: `1,234` (with commas)

**Parsing pattern:**
```javascript
function parseEngagementCount(text) {
  if (!text) return 0;
  text = text.trim().toUpperCase();
  
  if (text.endsWith('K')) return parseFloat(text) * 1000;
  if (text.endsWith('M')) return parseFloat(text) * 1000000;
  
  return parseInt(text.replace(/,/g, ''), 10) || 0;
}
```

## Layout Changes & Maintenance

X.com frequently updates their HTML structure. If selectors break:

1. **Check data-testid attributes**: These are most stable
2. **Verify ARIA roles**: Usually preserved for accessibility
3. **Inspect network requests**: XHR responses may contain structured data
4. **Use browser DevTools**: Inspect live page to identify new selectors

**Known changes:**
- 2023-07: Migration from twitter.com to x.com domains
- 2024-03: Updated engagement button layouts
- 2025-11: Redesigned tweet card structure

Update this document when selectors change. Include date and description of changes.

## Alternative Data Sources

If browser extraction fails, consider:

**1. Twitter/X API** (requires credentials - not used by this skill)
**2. Third-party services:**
   - Nitter instances (open-source Twitter frontend)
   - Tweet archival services
   - Social media data providers

**3. Browser extensions:**
   - Some extensions provide structured data extraction
   - Requires user installation

## Debug Tips

When extraction fails:

1. **Capture full snapshot**: Save entire browser snapshot for manual inspection
2. **Check role hierarchy**: ARIA tree may have nested structures
3. **Look for lazy-loaded content**: Some elements load after initial render
4. **Try alternative URLs**: twitter.com vs x.com, mobile.twitter.com
5. **Check for error messages**: "This tweet is unavailable" etc.
