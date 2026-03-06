# Styling Presets — Video Captions

## Quick Style Reference (ffmpeg force_style)

```bash
ffmpeg -i video.mp4 -vf "subtitles=video.srt:force_style='STYLE_STRING'" output.mp4
```

---

## Netflix Standard

Clean, professional, bottom-aligned.

```
FontName=Netflix Sans,FontSize=48,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,Outline=2,Shadow=1,Alignment=2,MarginV=50
```

**Fallback fonts:** Arial, Helvetica Neue, sans-serif

**Rules:**
- Max 42 characters per line
- Max 2 lines
- White text, black outline
- Centered bottom

---

## YouTube Standard

Default YouTube auto-caption style.

```
FontName=Roboto,FontSize=36,PrimaryColour=&HFFFFFF,BackColour=&H80000000,Outline=0,Shadow=0,Alignment=2,BorderStyle=4
```

**Features:**
- Semi-transparent black background
- No outline/shadow
- Clean readability

---

## TikTok Bold

Eye-catching, centered, bold text for short-form.

```
FontName=Montserrat-Bold,FontSize=42,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,Outline=4,Shadow=0,Alignment=10,MarginV=200
```

**Alignment 10** = center horizontally, top-center vertically

Alternative with color:
```
FontName=Impact,FontSize=48,PrimaryColour=&H00FFFF,OutlineColour=&H000000,Outline=4,Shadow=2,Alignment=10
```

---

## Instagram Reels

Similar to TikTok but slightly smaller.

```
FontName=Helvetica-Bold,FontSize=36,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,Outline=3,Shadow=0,Alignment=2,MarginV=150
```

---

## Cinematic

Elegant, minimal, for films and documentaries.

```
FontName=Georgia,FontSize=42,PrimaryColour=&HFFFFFF,OutlineColour=&H40000000,Outline=1,Shadow=2,Alignment=2,MarginV=80,Italic=1
```

---

## Gaming/Streaming

High contrast, readable over busy backgrounds.

```
FontName=Arial Black,FontSize=40,PrimaryColour=&H00FF00,OutlineColour=&H000000,Outline=3,Shadow=2,Alignment=2
```

---

## Karaoke Style

Word-by-word highlighting (requires ASS with `\k` tags).

```ass
Style: Karaoke,Arial,48,&H00FFFFFF,&H000000FF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,2,1,2,10,10,50,1

Dialogue: 0,0:00:01.00,0:00:05.00,Karaoke,,0,0,0,karaoke,{\k50}Hel{\k30}lo {\k40}world
```

---

## Color Reference (ASS &HAABBGGRR format)

| Color | Code |
|-------|------|
| White | &HFFFFFF |
| Black | &H000000 |
| Yellow | &H00FFFF |
| Cyan | &HFFFF00 |
| Red | &H0000FF |
| Green | &H00FF00 |
| Blue | &HFF0000 |
| Orange | &H0080FF |
| Purple | &HFF00FF |

**With transparency (AA = alpha, 00=opaque, FF=transparent):**
- Semi-transparent black: &H80000000

---

## Position Reference

**Alignment values (numpad layout):**
```
7  8  9   ← top
4  5  6   ← middle  
1  2  3   ← bottom
↑  ↑  ↑
L  C  R
```

| Position | Alignment |
|----------|-----------|
| Bottom center | 2 |
| Top center | 8 |
| Center middle | 5 |
| Bottom left | 1 |
| Bottom right | 3 |
| Top-center (TikTok) | 10 (special) |

---

## Custom Positioning (ASS)

Exact pixel position:
```
{\pos(960,900)}This text at exact position
```

Animated movement:
```
{\move(100,500,1800,500,0,2000)}Moving text left to right
```

---

## Font Recommendations

| Style | Primary | Fallback |
|-------|---------|----------|
| Professional | Netflix Sans, Gotham | Arial, Helvetica |
| Bold/Social | Montserrat Bold, Impact | Arial Black |
| Cinematic | Georgia, Garamond | Times New Roman |
| Gaming | Arial Black, Bebas Neue | Impact |
| Clean | Roboto, Open Sans | Arial |
| Retro | VCR OSD Mono | Courier |

---

## Complete ffmpeg Examples

**Netflix-style burn-in:**
```bash
ffmpeg -i video.mp4 -vf "subtitles=video.srt:force_style='FontName=Arial,FontSize=48,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,Outline=2,Shadow=1,Alignment=2,MarginV=50'" -c:a copy output.mp4
```

**TikTok-style with high quality:**
```bash
ffmpeg -i video.mp4 -vf "subtitles=video.ass" -c:v libx264 -preset slow -crf 18 -c:a copy output.mp4
```

**Vertical video (9:16) positioning:**
```bash
ffmpeg -i video.mp4 -vf "subtitles=video.srt:force_style='Alignment=10,MarginV=400,FontSize=28'" -c:a copy output.mp4
```
