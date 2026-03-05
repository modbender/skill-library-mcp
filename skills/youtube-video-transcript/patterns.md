# Advanced Patterns — YouTube Video Transcript

## Research Workflows

### Academic Citation

When user needs citable quotes:

```markdown
"{Exact quote from transcript}" 
— {Speaker}, "{Video Title}", {Channel}, {timestamp}, 
accessed {date}. https://youtube.com/watch?v={id}&t={seconds}
```

### Literature Review

For processing multiple videos on a topic:

1. Create topic folder: `~/youtube-video-transcript/research/{topic}/`
2. Extract all relevant videos
3. Generate index with key quotes per video
4. Cross-reference mentions across videos

### Timestamp Links

Generate deep links for sharing:
- Standard: `https://youtube.com/watch?v=ID&t=323`
- Short: `https://youtu.be/ID?t=5m23s`
- Embed: `https://youtube.com/embed/ID?start=323`

## Content Creator Workflows

### Repurposing Content

Extract transcript → Generate:
- Blog post outline from chapters
- Social media quotes (under 280 chars with timestamp)
- Newsletter summary
- Podcast show notes

### Competitor Analysis

For analyzing competitor videos:
1. Extract transcripts from their top videos
2. Identify topic coverage patterns
3. Find gaps they haven't covered
4. Note their key phrases and terminology

## Language Workflows

### Multi-Language Extraction

```bash
# Get all available languages
yt-dlp --list-subs "VIDEO_URL"

# Extract specific languages
yt-dlp --write-sub --sub-lang en,es,fr --skip-download "VIDEO_URL"
```

### Translation Comparison

Extract same video in multiple languages to:
- Compare auto-translations
- Verify translation accuracy
- Learn vocabulary in context

## Summarization Patterns

### Chapter-Based Summary

For each chapter:
```markdown
### {Chapter Title} [{timestamp}]
**Key points:**
- Point 1
- Point 2

**Notable quote:** "{quote}" [{timestamp}]
```

### Executive Summary

For busy users:
```markdown
## TL;DR (30 seconds)
{2-3 sentence summary}

## Key Takeaways
1. {takeaway with timestamp}
2. {takeaway with timestamp}
3. {takeaway with timestamp}

## Worth Watching?
{recommendation based on content density}
```

### Progressive Detail

```markdown
## One Sentence
{summary}

## One Paragraph
{expanded summary}

## Full Summary
{detailed chapter-by-chapter}

## Complete Transcript
{link to cached file}
```

## Search Patterns

### Semantic Search

User: "Find where they talk about pricing strategies"

Don't just grep for "pricing" — look for:
- Direct mentions: "pricing", "price", "cost"
- Related concepts: "monetization", "revenue", "charge"
- Context: "how much", "pay", "subscription"

### Quote Mining

For extracting quotable moments:

1. Identify strong statements (definitive language)
2. Look for numbered lists spoken aloud
3. Find contrasts ("not X, but Y")
4. Catch memorable phrases (unusual combinations)

Return with full context:
```markdown
**[12:34] Strong Quote**
> "{The exact quote}"

**Context:** {What came before/after}
**Why notable:** {Why this stands out}
```

## Batch Patterns

### Channel Archive

Download all transcripts from a channel:

```bash
# Get channel video list
yt-dlp --flat-playlist -j "CHANNEL_URL" | jq -r '.id'

# Process each
for id in $(cat video_ids.txt); do
  yt-dlp --write-auto-sub --sub-lang en --skip-download "https://youtube.com/watch?v=$id"
done
```

### Playlist Processing

```bash
# Full playlist with metadata
yt-dlp --write-auto-sub --sub-lang en --skip-download \
  --write-info-json \
  -o "%(playlist_index)s-%(title)s" \
  "PLAYLIST_URL"
```

### Rate Limiting

For large batches, be respectful:

```bash
# Add delay between requests
yt-dlp --sleep-interval 2 --max-sleep-interval 5 ...
```

## Quality Assessment

### Auto vs Manual Subtitles

Quick quality check:
- Manual: Usually sentence-cased, proper punctuation
- Auto: Often ALL CAPS or no caps, missing punctuation

```bash
# Check what's available
yt-dlp --list-subs "VIDEO_URL"

# Look for "manual" vs "automatic" in output
```

### Confidence Indicators

When reporting auto-generated transcripts:
- Note it's auto-generated
- Flag sections with obvious errors
- Suggest timestamps for verification

## Error Recovery

### Missing Subtitles

If no subtitles available:
1. Check other languages: `--sub-lang en,es,de,fr,pt,ja,ko`
2. Try auto-generated: `--write-auto-sub`
3. Report to user with alternatives

### Geo-Restricted

If video is region-locked:
- This skill does NOT use proxies
- Inform user of restriction
- Suggest they use VPN if they have one

### Age-Restricted

Some videos require authentication:
- yt-dlp supports cookies: `--cookies cookies.txt`
- User must provide their own browser cookies
- Never ask for or store credentials
