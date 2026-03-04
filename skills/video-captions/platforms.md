# Platform Requirements — Video Captions

## YouTube

**Format:** VTT (preferred) or SRT

**Upload methods:**
1. Auto-generate: YouTube creates captions automatically
2. Manual upload: Upload .vtt/.srt file in Studio
3. Type manually: Use YouTube caption editor

**Character limits:**
- No strict limit per line (but 42 recommended)
- Auto-wraps based on player size

**Best practices:**
- Include punctuation and capitalization
- Add speaker labels for multi-person content
- Timestamp within 1 frame of speech
- Use VTT for styling control

**Upload path:**
1. YouTube Studio → Video → Subtitles
2. Add language → Upload file
3. Choose "With timing" for SRT/VTT

---

## Netflix

**Format:** TTML (Timed Text Markup Language)

**Strict requirements:**
- Min duration: 5/6 second (0.833s)
- Max duration: 7 seconds
- Max 42 characters per line
- Max 2 lines per subtitle
- 2+ frame gap between subtitles

**Line breaks - DO:**
- After punctuation marks
- Before conjunctions
- Before prepositions

**Line breaks - DON'T:**
- Separate article from noun
- Separate adjective from noun
- Separate first name from last name
- Separate verb from subject pronoun

**Translator credit:**
- Required as last subtitle event
- After copyright disclaimer
- Up to 5 seconds duration

**Technical:**
- Use percentage values (not pixels)
- fontSize: 100%
- Only Netflix Glyph List characters

---

## TikTok

**Format:** Burn-in only (no external subtitle support)

**Specifications:**
- Video resolution: 1080x1920 (9:16)
- Position: Center or upper-center (avoid bottom menu overlap)
- Font size: 28-36pt for mobile readability
- Duration: 2-4 words per segment (fast pacing)

**Style recommendations:**
- Bold fonts (Montserrat Bold, Impact)
- High contrast (white + black outline)
- Consider colored text for emphasis
- Word-by-word animation popular

**Safe zones:**
- Top 150px: Username/sounds
- Bottom 300px: Buttons/description
- Best text area: Center 70% of screen

**ffmpeg for TikTok:**
```bash
ffmpeg -i video.mp4 \
  -vf "subtitles=video.srt:force_style='FontName=Montserrat-Bold,FontSize=32,Alignment=10,MarginV=200,Outline=3'" \
  -c:a copy output.mp4
```

---

## Instagram Reels

**Format:** Burn-in only

**Specifications:**
- Same as TikTok (9:16)
- Slightly more conservative styling
- Consider brand consistency

**Auto-captions:**
- Instagram offers auto-generated captions
- Limited editing options
- Use "Captions" sticker

---

## Vimeo

**Format:** VTT or SRT

**Features:**
- Multiple language tracks supported
- Viewer can toggle on/off
- No burn-in required

**Upload:**
1. Video settings → Distribution → Subtitles
2. Upload file, select language

---

## Facebook/Meta

**Format:** SRT (preferred)

**Specifications:**
- Max 2 lines
- 35 characters per line (recommended)
- Auto-captions available but often inaccurate

**Upload:**
- Creator Studio → Subtitles → Upload SRT

---

## LinkedIn

**Format:** SRT

**Best practices:**
- Auto-captions available (enable in post settings)
- Upload SRT for accuracy
- Keep text concise (mobile viewing)

---

## Twitter/X

**Format:** Burn-in or platform auto-captions

**Notes:**
- Native auto-captions available
- Burn-in recommended for guaranteed visibility
- Short segments work best

---

## Broadcast/TV

**Format:** TTML, STL, or EBU-STL

**Requirements:**
- Very strict timing (frame-accurate)
- Specific font requirements
- Safe area compliance
- Teletext compatibility (some markets)

**Typically handled by:**
- Dedicated subtitling houses
- Broadcast engineers
- Specialized software (EZTitles, WinCAPS)

---

## Accessibility Standards

### FCC (US)
- 99% accuracy for pre-recorded content
- Real-time: Best efforts standard
- Required for broadcast/cable

### WCAG 2.1
- Level A: Captions for all prerecorded audio
- Level AA: Live captions where feasible
- Timing synchronized within 1 second

### SDH (Subtitles for Deaf and Hard-of-hearing)
- Include non-speech audio: [music], [laughter], [door closes]
- Speaker identification: JOHN:
- Sound descriptions in brackets

---

## Platform Comparison

| Platform | Format | Max Lines | Max Chars | Burn-in? |
|----------|--------|-----------|-----------|----------|
| YouTube | VTT/SRT | 2 | ~42 | Optional |
| Netflix | TTML | 2 | 42 | No |
| TikTok | ASS | 2 | 30 | Required |
| Instagram | ASS | 2 | 30 | Required |
| Vimeo | VTT/SRT | 2 | 42 | Optional |
| Facebook | SRT | 2 | 35 | Optional |
| Broadcast | TTML/STL | 2 | 37 | No |
