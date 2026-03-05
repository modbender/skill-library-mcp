---
name: youtube-transcript
description: Extract and analyze YouTube video transcripts without watching the video. Use when users request video summaries, ask to "analyze this YouTube video", want transcripts extracted, or need to understand video content quickly. Handles any YouTube URL and provides cleaned transcripts plus AI analysis.
---

# YouTube Transcript Analysis

Extract, clean, and analyze YouTube video transcripts to understand content without watching.

## Overview

This skill enables rapid analysis of YouTube videos by extracting transcripts and providing comprehensive summaries. Perfect for research, content review, or understanding video material without time investment.

## Quick Workflow

1. **Extract**: Use `scripts/extract_transcript.sh` to get clean text from YouTube URL
2. **Read**: Load the extracted transcript file 
3. **Analyze**: Provide structured summary based on content type
4. **Format**: Present findings in scannable, organized format

## Extraction Process

Use the bundled script for any YouTube video:

```bash
scripts/extract_transcript.sh "https://www.youtube.com/watch?v=VIDEO_ID" output.txt
```

The script automatically:
- Downloads yt-dlp if not present
- Extracts captions (auto-generated or manual)
- Cleans VTT formatting to plain text
- Provides character count and preview

## Analysis Approach

### Content Type Recognition

Identify video type first, then tailor analysis:

**Educational/Tutorial**: Step-by-step breakdown, key concepts, prerequisites
**Product Review**: Comparisons, pros/cons, recommendations, specifications  
**News/Commentary**: Main topics, key arguments, sources cited
**Entertainment**: Highlights, key moments, recurring themes

### Structure Your Analysis

**For any video type:**
- **Title/Topic**: Clear description of video content
- **Duration insight**: Brief/detailed based on transcript length
- **Key points**: 3-7 main takeaways in bullet format
- **Notable quotes**: Important statements (if applicable)
- **Action items**: Next steps or recommendations (if present)

**For technical content:**
- Include specific terminology, version numbers, tools mentioned
- Note any code examples or configurations discussed
- Identify prerequisites or dependencies

### Quality Considerations

**Auto-generated transcripts may have:**
- Repetitive phrases
- Transcription errors for technical terms
- Missing punctuation
- Filler words ("um", "uh", "you know")

Filter and interpret accordingly - focus on clear, coherent content.

## Advanced Analysis

For detailed analysis patterns and content-specific approaches, see [analysis-patterns.md](references/analysis-patterns.md).

## Error Handling

**If extraction fails:**
- Video may lack captions
- May be private/restricted  
- Network connectivity issues
- Age-restricted content

**Fallback approach:** Use web_fetch on the YouTube URL to get basic video information, then inform user about transcript limitations.