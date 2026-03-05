# TikTok Clipper — Video → Viral Clips with Subtitles

## What it does
Takes a long-form video, transcribes it, identifies the most engaging segments for TikTok/Reels, clips them with ffmpeg, and adds TikTok-style animated subtitles.

## When to use
- User sends a video and wants TikTok/Reels clips
- User asks to "clip this", "find viral moments", "cut for TikTok"
- User wants subtitles added to video clips

## Pipeline

### Step 1: Transcribe
```bash
# Transcribe with Whisper (word-level timestamps)
python3 SKILL_DIR/transcribe.py --input VIDEO_PATH --output TRANSCRIPT.json
```
Uses OpenAI Whisper API with `timestamp_granularities=["word","segment"]` for precise subtitle timing.

### Step 2: Analyze & Suggest Clips
Read the transcript and identify segments that would perform well on TikTok:
- **Hooks**: Strong opening lines, provocative statements, questions
- **Value bombs**: Key insights, surprising facts, actionable tips
- **Emotional peaks**: Enthusiasm, humor, strong opinions
- **Story arcs**: Complete mini-stories with beginning/middle/end
- **Controversy/debate**: Polarizing takes that drive comments

Present clips as numbered options with:
- Time range (start → end)
- Duration
- Hook line (first sentence)
- Why it could be viral
- Suggested caption

User picks which ones to cut.

### Step 3: Cut clips
```bash
python3 SKILL_DIR/clip.py --input VIDEO_PATH --start MM:SS --end MM:SS --output CLIP.mp4
```
- Uses ffmpeg with re-encoding for clean cuts
- Converts to 9:16 vertical if needed (crop or pad)
- Ensures TikTok-compatible format (h264, aac, mp4)

### Step 4: Add TikTok-style subtitles
```bash
python3 SKILL_DIR/subtitles.py --input CLIP.mp4 --transcript TRANSCRIPT.json --start SS --end SS --style STYLE --output FINAL.mp4
```

#### Subtitle Styles Available:
1. **bold-center**: White bold text, black outline, centered bottom third (classic TikTok)
2. **word-highlight**: Word-by-word highlight in yellow/green (like CapCut auto-captions)
3. **karaoke**: Current word scales up + color change (Alex Hormozi style)
4. **box**: Text with colored background box (MrBeast style)

All styles use ASS (Advanced SubStation Alpha) for rich formatting via ffmpeg.

### Step 5: Vertical format
If source is horizontal (16:9), auto-crop to 9:16:
- Center crop for talking head
- Or blur-background padding (video small in center, blurred fill)

## File outputs
All outputs go to `/home/ubuntu/clawd/clips/` with naming: `{source}-clip{N}-{style}.mp4`

## Requirements
- `ffmpeg` (installed)
- OpenAI API key for Whisper (in .env)
- Source video file

## Notes
- Max TikTok length: 90 seconds for best performance
- Sweet spot: 30-60 seconds
- Always start with a hook (first 3 seconds matter most)
- Subtitles should be max 2 lines, ~5-7 words per line
