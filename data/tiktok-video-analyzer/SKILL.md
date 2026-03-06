---
name: Video Analyzer Skill
description: Analyze any video by dropping a URL. Works with TikTok, YouTube,
  Instagram, Twitter/X, and 1000+ other sites. Transcribes the audio locally and
  answers any question about the content.
---

# Video Analyzer Skill

Analyze any video by dropping a URL. Works with TikTok, YouTube, Instagram, Twitter/X, and 1000+ other sites. Transcribes the audio locally and answers any question about the content.

---

## When to Use This Skill

Activate when the user:
- Shares a video URL (tiktok.com, youtube.com, instagram.com, twitter.com, x.com, etc.)
- Asks "what is this video about", "summarize this", "what are they teaching", "what's the hook", etc.
- Asks a question about a previously saved video

---

## ⚠️ CRITICAL RULES — READ BEFORE ANYTHING ELSE

**Rule 1 — FIRST MESSAGE IS ALWAYS THIS, NO EXCEPTIONS:**

Use the `message` tool to send this BEFORE running any exec command:
> 📡 Video received, analyzing...

This must be a `message` tool call, not your final reply text. Using the message tool sends it immediately to the user while you continue processing. If you put it in your reply text instead, the user won't see it until everything is done — which defeats the purpose entirely.

Do NOT reference conversation history, prior testing, or anything from the current session. Every URL is treated fresh.

**Rule 2 — NEVER GO SILENT**
The user MUST receive a message every 30-60 seconds while processing. Silence = broken.
- After download step: send "📥 Downloaded! Transcribing now..."
- If anything takes more than 30 seconds: send "⏳ Still working..."

**Rule 3 — NO PERSONAL COMMENTARY. EVER.**
Do NOT add ANY of the following:
- "This appears to be the video we already tested"
- "I recognize this URL" / "you've sent this before"
- "Heads up — this is the same link"
- Any footnote, parenthetical, or aside about the URL or prior usage

Just run the skill and give the answer. End with the save prompt. Nothing else.
If the transcript is cached: say "📚 Found in your library!" then answer. That's it.

**Rule 4 — First-run warning**
If the transcripts folder is empty (first ever run), warn upfront:
> ⚠️ First time running — downloading the AI model (~150MB). Takes 2-4 minutes once, never again.

---

## Prerequisites Check

Before the first run, check if dependencies are installed:

```bash
which ffmpeg && python3 -c "import faster_whisper; print('ok')" && python3 -c "import yt_dlp; print('ok')"
```

**If anything is missing, guide the user:**

Mac/local:
```bash
brew install ffmpeg
pip3 install faster-whisper yt-dlp --break-system-packages
```

Linux/VPS:
```bash
apt install -y ffmpeg
pip install faster-whisper yt-dlp --break-system-packages
```

---

## Flow

### Step 1 — Acknowledge IMMEDIATELY (before anything else)
Send: `📡 Video received, analyzing...`

### Step 1b — First run warning
If this looks like the first time (no cached transcripts exist), warn the user:
> ⚠️ First time running — the AI transcription model needs to download (~150MB). This takes 2-4 minutes once and never again. Grab a coffee ☕

### Step 2 — Download (step 1 of 2)

```bash
python3 ~/.openclaw/skills/tiktok-analyzer/transcribe.py --download-only "URL_HERE"
```

Returns JSON with `status: "downloaded"` and `video_id`. If `from_cache: true` + `skip_transcribe: true` → go straight to Step 3, skip Step 2b.

### Step 2b — Send progress message (via message tool), then transcribe

Use the `message` tool to send: `📥 Downloaded! Transcribing now...`

Then immediately run:
```bash
python3 ~/.openclaw/skills/tiktok-analyzer/transcribe.py --transcribe-only "VIDEO_ID"
```

Replace `VIDEO_ID` with the `video_id` from the previous step.

Returns JSON:
```json
{
  "transcript": "full text here...",
  "language": "en",
  "video_id": "abc123",
  "from_cache": false
}
```

If `from_cache: true` (from Step 2) → say "📚 Found this in your library — instant answer!" and skip the wait messages.

If there's an `"error"` key → relay it cleanly (never show a Python stacktrace to the user).

### Step 3 — Answer the question
Use the transcript to answer whatever they asked. If no specific question, provide:
- **What it's about** (1-2 sentences)
- **Key points / what's being taught** (bullet list)
- **Tone / style** (educational, entertainment, story, etc.)

### Step 4 — Offer to save (MANDATORY if from_cache: false)
After giving the answer, ALWAYS ask this — do not skip it:
> 💾 Want to save this transcript so you can ask follow-up questions later without re-downloading? (yes/no)

Only skip this if `from_cache: true` (already saved).

If yes:
```bash
python3 ~/.openclaw/skills/tiktok-analyzer/save_transcript.py "VIDEO_ID" 'JSON_DATA'
```

Confirm: `✅ Saved to your video library!`

---

## Searching Saved Transcripts

When the user asks about something they've analyzed before:
1. List files in `~/.openclaw/skills/tiktok-analyzer/transcripts/`
2. Read the relevant `.json` file(s)
3. Answer from the saved transcript

---

## Error Handling

| Error | Response |
|-------|----------|
| Private/removed video | "This video is private or has been removed. Try a different URL." |
| No ffmpeg | "You need ffmpeg. Run: `brew install ffmpeg` (Mac) or `apt install ffmpeg` (Linux)" |
| No faster-whisper | "Run: `pip install faster-whisper yt-dlp` then try again." |
| Timeout / very long video | "That one's taking a while — try a shorter clip or check your connection." |

---

## Demo Tips

- **For demos:** Use a video you've already analyzed (cache hit = instant response, looks great)
- **First run:** Always warn upfront about the 150MB model download
- **Works on any platform** yt-dlp supports — TikTok, YouTube, Instagram, Twitter, Reddit, Vimeo, and 1000+ more
