# Output Formats — Video Captions

## SRT (SubRip)

**Use for:** Universal compatibility, editing, YouTube upload

```srt
1
00:00:01,000 --> 00:00:04,500
This is the first subtitle line.

2
00:00:05,000 --> 00:00:08,500
This is the second subtitle.
```

**Features:**
- Most widely supported
- Simple text format
- Easy to edit manually
- No styling (plain text only)

**Supported by:** VLC, YouTube, Vimeo, Premiere, DaVinci, all players

---

## VTT (WebVTT)

**Use for:** Web/HTML5, YouTube (preferred), modern platforms

```vtt
WEBVTT

00:00:01.000 --> 00:00:04.500
This is the first subtitle line.

00:00:05.000 --> 00:00:08.500
This is the second subtitle.
```

**Features:**
- HTML5 native
- Supports basic styling (bold, italic, color)
- Positioning cues
- Chapter markers

**Styling example:**
```vtt
WEBVTT

STYLE
::cue {
  color: white;
  background-color: rgba(0,0,0,0.8);
}

00:00:01.000 --> 00:00:04.500
<v Speaker1>Hello there!</v>

00:00:05.000 --> 00:00:08.500 position:10%,line-left
Positioned subtitle.
```

---

## ASS/SSA (Advanced SubStation Alpha)

**Use for:** Styled captions, karaoke, anime, TikTok effects, burn-in

```ass
[Script Info]
Title: Video Captions
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,48,&H00FFFFFF,&H000000FF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,2,1,2,10,10,50,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:01.00,0:00:04.50,Default,,0,0,0,,This is a styled subtitle.
```

**Style Parameters:**
- `PrimaryColour` - Text color (&HAABBGGRR format)
- `OutlineColour` - Border color
- `Outline` - Border thickness (pixels)
- `Shadow` - Shadow distance
- `Alignment` - Position (1-9 numpad layout)
- `MarginV` - Vertical margin from edge

**Alignment positions:**
```
7 8 9  (top)
4 5 6  (middle)
1 2 3  (bottom)
```

**Effects available:**
- `\blur` - Gaussian blur
- `\bord` - Border size
- `\shad` - Shadow
- `\fad(in,out)` - Fade timing
- `\k` - Karaoke timing
- `\pos(x,y)` - Exact position
- `\move(x1,y1,x2,y2)` - Animation

---

## TTML (Timed Text Markup Language)

**Use for:** Netflix, broadcast, professional delivery

```xml
<?xml version="1.0" encoding="UTF-8"?>
<tt xmlns="http://www.w3.org/ns/ttml">
  <body>
    <div>
      <p begin="00:00:01.000" end="00:00:04.500">
        This is the first subtitle.
      </p>
      <p begin="00:00:05.000" end="00:00:08.500">
        This is the second subtitle.
      </p>
    </div>
  </body>
</tt>
```

**Netflix requirements:**
- Use percentage values (not pixels)
- fontSize: 100%
- Only NETFLIX Glyph List characters

---

## JSON (Structured Data)

**Use for:** Custom processing, word-level data, APIs

```json
{
  "text": "Hello, this is a transcription.",
  "segments": [
    {
      "id": 0,
      "start": 0.0,
      "end": 2.5,
      "text": "Hello, this is",
      "words": [
        {"word": "Hello,", "start": 0.0, "end": 0.5},
        {"word": "this", "start": 0.6, "end": 0.8},
        {"word": "is", "start": 0.9, "end": 1.0}
      ]
    }
  ],
  "language": "en"
}
```

**Use cases:**
- Custom caption rendering
- Word-level highlighting
- Data analysis
- Integration with video editors

---

## Format Conversion

```bash
# SRT to VTT
ffmpeg -i input.srt output.vtt

# SRT to ASS
ffmpeg -i input.srt output.ass

# VTT to SRT
ffmpeg -i input.vtt output.srt

# Extract embedded subtitles from video
ffmpeg -i video.mkv -map 0:s:0 output.srt
```

---

## Platform Format Matrix

| Platform | Primary | Alternative | Notes |
|----------|---------|-------------|-------|
| YouTube | VTT | SRT | VTT has more features |
| Netflix | TTML | - | Strict compliance required |
| Vimeo | VTT | SRT | - |
| TikTok | Burn-in (ASS) | - | No external subtitle support |
| Instagram | Burn-in (ASS) | - | Reels need embedded |
| Premiere Pro | SRT | - | Native import |
| DaVinci | SRT | VTT | - |
| Final Cut | SRT | - | - |
| Web/HTML5 | VTT | - | Native `<track>` element |
