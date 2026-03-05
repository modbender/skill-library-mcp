# Twitter/X Reader Skill

A comprehensive skill for reading and extracting data from X (formerly Twitter) tweets using multiple reliable data sources.

## Overview

This skill extracts complete tweet information including text content, author details, engagement statistics, media attachments, and quoted tweets from X/Twitter URLs. It uses a multi-tier approach for maximum reliability and data completeness.

## When to Use

**Primary Triggers:**
- User shares a tweet URL (x.com/*/status/* or twitter.com/*/status/*)
- User asks to "read this tweet" with a URL
- User requests tweet analysis, summary, or data extraction
- User mentions getting information from a specific tweet

**Example User Requests:**
- "What does this tweet say? https://x.com/elonmusk/status/123456789"
- "Can you read this tweet for me?"
- "Summarize this Twitter thread"
- "What are the engagement stats on this tweet?"
- "Extract the media from this tweet"

## Capabilities

### Data Extracted
- **Tweet Content:** Full text with proper formatting
- **Author Information:** Display name and handle (@username)
- **Timestamps:** Both human-readable and original format
- **Engagement Stats:** Likes, retweets, replies, quote tweets
- **Media Attachments:** Photos and videos with direct URLs
- **Quote Tweets:** Full quoted tweet content and author info
- **Thread Context:** When available

### Supported URL Formats
- `https://x.com/username/status/1234567890`
- `https://twitter.com/username/status/1234567890`
- URLs with query parameters (e.g., `?s=20`, `?t=abc123`)
- Mobile URLs (m.twitter.com automatically handled)

## Usage Examples

### Basic Usage
```bash
# Read a single tweet
./scripts/read_tweet.sh "https://x.com/username/status/1234567890"

# Read a full thread (follows reply chain from the same author)
./scripts/read_thread.sh "https://x.com/username/status/1234567890"

# Fallback method using Nitter
./scripts/read_tweet_nitter.sh "https://x.com/username/status/1234567890"
```

### Agent Instructions

When a user provides a tweet URL:

1. **Validate the URL format** - ensure it's a valid X/Twitter status URL
2. **Use the primary script** - `scripts/read_tweet.sh` first
3. **Handle failures gracefully** - if primary fails, try `scripts/read_tweet_nitter.sh`
4. **Present data clearly** - format the output for human consumption
5. **Preserve context** - include engagement stats and media references

### Sample Response Format

The scripts return structured JSON with this format:

```json
{
  "success": true,
  "tweet": {
    "text": "Tweet content here...",
    "author": {
      "name": "Display Name",
      "handle": "username"
    },
    "timestamp": {
      "formatted": "2024-01-15 14:30:25 UTC",
      "original": "Mon Jan 15 14:30:25 +0000 2024"
    },
    "url": "https://x.com/username/status/1234567890",
    "engagement": {
      "likes": 1250,
      "retweets": 340,
      "replies": 89,
      "quotes": 45
    },
    "media": {
      "photos": ["https://pbs.twimg.com/media/..."],
      "video": "https://video.twimg.com/..."
    },
    "quoted_tweet": {
      "text": "Quoted tweet text...",
      "author": {
        "name": "Quoted Author",
        "handle": "quoted_user"
      },
      "url": "https://x.com/quoted_user/status/987654321"
    }
  },
  "source": "fxtwitter",
  "fetched_at": 1705327825
}
```

### Agent Response Example

```markdown
**Tweet from @elonmusk:**
> "Just had a great meeting about sustainable transport. The future is electric! ⚡🚗"

**Posted:** January 15, 2024 at 2:30 PM UTC
**Engagement:** 1,250 likes • 340 retweets • 89 replies • 45 quotes

**Media:** 1 photo attached
- Photo: https://pbs.twimg.com/media/example.jpg

**Quote Tweet from @teslaofficial:**
> "Our latest Model S update includes new charging optimizations..."
```

## Technical Implementation

### Primary Method: FxTwitter API
- **Endpoint:** `https://api.fxtwitter.com/{username}/status/{tweet_id}`
- **Advantages:** No authentication, comprehensive data, reliable
- **Rate Limits:** Generous for personal use
- **Response:** Complete JSON with all tweet metadata

### Fallback Method: Nitter Scraping (Best-Effort)
- **Instances:** Multiple public Nitter instances as backup
- **Advantages:** Works when FxTwitter is unavailable
- **Limitations:** Basic data extraction, no engagement stats
- **Usage:** Automatic fallback when primary method fails
- **⚠️ Note:** Most public Nitter instances have shut down or become unreliable since 2024. This fallback is best-effort and may not return results. The FxTwitter API should be considered the only reliable method.

### Error Handling
- Invalid URL format detection
- Network timeout handling
- API error response parsing
- Graceful fallback between methods
- Clear error messages for users

## Dependencies

**Required System Tools:**
- `curl` - HTTP requests to APIs
- `jq` - JSON parsing and formatting
- `bash` - Script execution environment
- `grep/sed` - Text processing (Nitter fallback only)

**Optional Enhancements:**
- `gdate` (GNU date via Homebrew on macOS) - Better timestamp formatting

## Security & Privacy

### Security Features
- ✅ **No external data collection** - Data stays on your system
- ✅ **No analytics or telemetry** - No tracking or usage reporting
- ✅ **Fully auditable code** - Open source, readable shell scripts
- ✅ **Minimal network calls** - Only to FxTwitter API and Nitter instances
- ✅ **No sensitive data exposure** - Scripts don't store or log personal info
- ✅ **Safe URL handling** - Proper URL validation and sanitization

### Network Connections
**Approved External Hosts:**
- `api.fxtwitter.com` - Primary data source (FxTwitter API)
- `nitter.net` and other Nitter instances - Fallback scraping
- No other external connections made

**Data Flow:**
1. User provides tweet URL
2. Script extracts username/ID from URL
3. Makes API request to FxTwitter or Nitter
4. Parses response locally
5. Returns formatted JSON (never stored permanently)

### Audit Trail
All network requests include:
- Clear user-agent identification
- Minimal necessary headers only
- No authentication tokens or personal identifiers
- Requests only to extract public tweet data

## Error Scenarios & Handling

### Common Errors

**Invalid URL Format:**
```json
{
  "error": "Invalid Twitter/X URL format",
  "expected": "x.com/user/status/123456789 or twitter.com/user/status/123456789"
}
```

**Tweet Not Found:**
```json
{
  "error": "API Error",
  "code": 404,
  "message": "NOT_FOUND"
}
```

**Network Failure:**
```json
{
  "error": "Failed to fetch tweet data",
  "details": "Network request failed"
}
```

**Fallback Needed:**
```json
{
  "error": "All Nitter instances failed",
  "suggestion": "Try the main script with FxTwitter API, or wait for Nitter instances to recover"
}
```

### Agent Error Handling

When errors occur:
1. **Parse the error JSON** to understand the issue
2. **Try the fallback method** if primary fails
3. **Explain to the user** what went wrong in plain language
4. **Suggest alternatives** (try again later, check URL format, etc.)

## Advanced Features

### Thread Reading
Full thread unrolling is supported via `read_thread.sh`:
- Given any tweet URL in a thread, walks UP the reply chain via `replying_to` fields
- Only collects tweets from the same author (self-reply threads)
- Returns tweets in chronological order as a JSON array
- Safety limit of 50 tweets per thread (configurable via second argument)
- Usage: `./scripts/read_thread.sh "https://x.com/user/status/123" [max_depth]`

### Media Handling
- **Photos:** Direct URLs via `media.photos` array (full-resolution)
- **Videos:** Links to MP4 files via `media.videos` with thumbnails and duration
- **All media:** Combined `media.all` array with type annotations for complete coverage
- **Article covers:** Long-form X posts ("articles") have `media.article_cover` extracted
- **GIFs:** Handled as video content
- **External Links:** Preserved in tweet text

### Quote Tweet Recursion
The skill can extract nested quote tweets up to reasonable depth to avoid infinite loops.

## Performance Notes

### Response Times
- **FxTwitter API:** Typically 200-500ms
- **Nitter Scraping:** 1-3 seconds per instance
- **Network Dependent:** May vary based on connection quality

### Caching Considerations
- No persistent caching implemented by default
- Consider temporary caching for repeated requests
- Respect rate limits of external services

## Troubleshooting

### Common Issues

**"No tweet data in API response"**
- Tweet may be deleted or protected
- Check URL format and tweet ID
- Try fallback method

**"Network request failed"**
- Check internet connection
- FxTwitter API may be temporarily down
- Fallback to Nitter method

**"All Nitter instances failed"**
- Nitter instances may be blocked or down
- Wait and retry with FxTwitter API
- Check firewall/proxy settings

### Debug Mode
For debugging, run with verbose output:
```bash
bash -x scripts/read_tweet.sh "https://x.com/username/status/123"
```

## Development & Customization

### Adding New Data Sources
To add additional fallback methods:
1. Create new script in `scripts/` directory
2. Follow same JSON output format
3. Update main skill logic to include new method
4. Test thoroughly and update documentation

### Modifying Output Format
The JSON structure can be customized by modifying the final `jq` command in each script. Maintain consistency across all methods.

### Adding Features
Consider these enhancement areas:
- Sentiment analysis of tweet content
- Hashtag and mention extraction
- Link expansion and preview
- Image OCR for text in media
- Translation support for non-English tweets

## Version History

- **v1.1** - Thread following (`read_thread.sh`), comprehensive media extraction (photos, videos, all media, article covers)
- **v1.0** - Initial release with FxTwitter API and Nitter fallback
- Multi-source reliability with comprehensive data extraction
- Full security audit compliance
- Production-ready for ClawHub distribution