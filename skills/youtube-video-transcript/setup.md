# Setup — YouTube Video Transcript

Read this when `~/youtube-video-transcript/` doesn't exist or is empty.

## Your Attitude

You're offering a powerful way to work with video content. The user might be a researcher, content creator, student, or just someone who prefers reading to watching. Adapt to their needs.

## Verify yt-dlp Installation

Before first use, verify `yt-dlp` is available:

```bash
which yt-dlp
```

If not installed, offer to help:
- "I need yt-dlp to extract transcripts. Want me to help you install it?"
- Options: `brew install yt-dlp` (macOS) or `pip install yt-dlp`

## Priority Order

### 1. First: Help With Their Immediate Request

If they came with a specific video, help with that first. Don't delay with questions before delivering value.

### 2. Then: Ask About Caching Preference

After the first transcript, ask:
- "Want me to save transcripts locally for faster access next time? They'll go in ~/youtube-video-transcript/videos/"
- Respect their choice. If they say no, don't cache.

### 3. Finally: Integration

When appropriate in conversation:
- "Want me to automatically offer to transcribe when you share YouTube links?"
- "Should I remember your format preferences (timestamps, summaries)?"

## What to Save (With User Consent)

If user agrees to caching, save to `~/youtube-video-transcript/memory.md`:
- **Preferred format:** markdown / text / srt
- **Timestamp preference:** always / sometimes / never
- **Summary style:** brief / detailed / chapter-based
- **Export location:** if they have a preference

Tell the user what you're saving: "I'll remember you prefer summaries with timestamps."

## Transparency Rules

1. **Always tell the user** what you're about to save and where
2. **Ask before caching** transcripts for the first time
3. **Confirm preferences** before storing them
4. **Offer to show** saved files if they ask

## When "Ready"

You're ready after:
1. Successfully extracting one transcript
2. Understanding if they want caching (yes/no)

Everything else builds naturally over time.
