---
name: viral-video-analysis
description: Analyze video ad performance and provide actionable feedback to creators. Use when asked to analyze why videos underperform, give creator coaching feedback, compare high vs low ROI content, or identify video structure issues. Combines audio transcripts, visual analysis, and performance metrics. Supports YouTube, TikTok, Instagram Reels, and Twitter.
metadata: {"openclaw": {"requires": {"env": ["MEMORIES_API_KEY"]}, "primaryEnv": "MEMORIES_API_KEY", "homepage": "https://api-tools.memories.ai"}}
---

## Requirements

- **API Key**: Requires `MEMORIES_API_KEY` from [Memories.ai](https://api-tools.memories.ai)
- **External API**: Sends video URLs to `https://mavi-backend.memories.ai` for transcription
- **Python packages**: `generate_report.py` will auto-install `fpdf2`, `pandas`, `openpyxl` if missing

### Privacy Note
- Video URLs are sent to Memories.ai for transcription
- Batch analysis reads Excel files with creator/ROI data
- Review [Memories.ai privacy policy](https://memories.ai/privacy) before use

# Viral Video Analysis

Analyze videos and provide **actionable feedback for creators**.

## Core Insight

**High ROI videos**: <100 words, ~5s per product, visual-first + background music
**Low ROI videos**: >150 words, >15s per product, too much explaining

The core problem: Creators spend too much time "selling" instead of "showing".
Remember: **Ads reach non-followers who need to be hooked in 3 seconds.**

## Quantitative Thresholds

| Metric | ✅ GOOD (High ROI) | ❌ BAD (Low ROI) |
|--------|-------------------|------------------|
| Word Count | <100 words | >150 words |
| Time per Product | ~5 seconds | >15 seconds |
| Shows All Products Upfront | YES | NO |
| Format | Visual + Music | Talking/Explaining |

## Analysis Workflow

## Setup

Requires Memories.ai API key. Get one at https://api-tools.memories.ai

Set environment variable:
```bash
export MEMORIES_API_KEY="sk-mavi-your-key-here"
```

### 1. Get Audio Transcript (Word Count)
```python
import os
import requests

BASE_URL = "https://mavi-backend.memories.ai/serve/api/v2"
API_KEY = os.environ.get("MEMORIES_API_KEY")
HEADERS = {"Authorization": API_KEY}

def get_transcript(url: str, platform: str = "instagram"):
    resp = requests.post(
        f"{BASE_URL}/{platform}/video/transcript",
        headers=HEADERS,
        json={"video_url": url, "channel": "rapid"},
        timeout=60
    )
    data = resp.json()
    if data.get("success"):
        text = data["data"]["transcripts"][0]["text"]
        return {"text": text, "word_count": len(text.split())}
    return {"error": data.get("msg")}

# Platform detection
def detect_platform(url):
    url = url.lower()
    if "tiktok" in url: return "tiktok"
    if "instagram" in url: return "instagram"
    if "twitter" in url or "x.com" in url: return "twitter"
    return "youtube"
```

### 2. Analyze Against Thresholds
```python
def analyze_video(url):
    platform = detect_platform(url)
    result = get_transcript(url, platform)
    
    if "error" in result:
        return result
    
    word_count = result["word_count"]
    
    return {
        "url": url,
        "word_count": word_count,
        "word_count_status": "GOOD" if word_count < 100 else "OK" if word_count < 150 else "BAD",
        "issues": [],
        "transcript_preview": result["text"][:200]
    }
```

### 3. Generate Creator Feedback

Based on analysis, provide specific feedback:

**If word_count > 150:**
> "Your video has {X} words. Top performers use <100 words. Try replacing verbal explanations with visual demonstrations - stretch the fabric, spin around, show the fit."

**If pace is slow (>15s per product):**
> "You're spending ~{X} seconds per product. High-performers show each item in ~5 seconds. Try quick cuts - one outfit = one scene transition."

**If no upfront overview:**
> "Show ALL products in the first 2-3 seconds. Let viewers see the full haul immediately - it sets expectations and keeps them watching."

**Always remind:**
> "Remember: Ads reach people who DON'T follow you. You have 3 seconds to grab a stranger's attention - don't waste it on intros."

## The Exception: Kirstin Approach

Detailed verbal reviews CAN work if:
1. Show all products FIRST before explaining
2. Use low-pressure language: "if it doesn't fit, just return it"
3. Focus on introducing products, not "selling" them

Word count: 373 words can still perform if structure is right.

## Reference Videos

### GOOD Examples (share with creators)
- `instagram.com/reel/Cy1zs4gLGFG` - 46 words, 15s for 3 outfits, pure visual
- `instagram.com/reel/DEybxPbNeOl` - 56 words, quick showcase, background music
- `instagram.com/reel/DHHr5o2s1LG` - 91 words, fast cuts, shows product features
- `instagram.com/reel/DBd6NxbOeBb` - 91 words, demonstrates fit visually

### EXCEPTION Example (detailed review done RIGHT)
- `instagram.com/reel/DCQJ355RWSE` - 373 words but works: shows all upfront, low-pressure

### BAD Example (avoid)
- `instagram.com/reel/DRCdjLlDcla` - 168 words, 30s per outfit, too much explaining

## Feedback Template

```
Hi [Creator],

Thanks for your video! Here's some feedback to help improve performance:

**What's Working:**
- [Specific positive]

**Opportunities:**
1. **Pacing**: Currently ~{X}s per product. Try ~5s per item with quick cuts.
2. **Word Count**: {X} words detected. Top performers use <100. Show more, tell less.
3. **Opening**: Consider showing all products in first 2-3 seconds.

**Key Reminder:**
Ads reach people who don't follow you yet. They need to be hooked in 3 seconds!

**Reference Videos:**
[Link to good example]

Best,
[Team]
```

## Batch Analysis

```python
def analyze_batch(excel_path, sample_size=20):
    import pandas as pd
    df = pd.read_excel(excel_path)
    df.columns = [c.lower().replace('sum of ', '').replace(' ', '_') for c in df.columns]
    
    # Get top and bottom performers
    top = df.nlargest(sample_size // 2, 'roi')
    bottom = df.nsmallest(sample_size // 2, 'roi')
    
    results = []
    for _, row in pd.concat([top, bottom]).iterrows():
        url = row.get('video_url') or row.get('row_labels')
        analysis = analyze_video(url)
        analysis['roi'] = row['roi']
        analysis['tier'] = 'TOP' if row['roi'] > 1.0 else 'BOTTOM'
        results.append(analysis)
    
    return results
```

## Quick Commands

- "Analyze this video: [url]" → Word count + feedback
- "Why is this video underperforming?" → Detailed analysis
- "Give me feedback for [creator]" → Coaching template
- "Compare these videos" → Side-by-side analysis
- "Analyze my performance data" → Batch analysis from Excel
