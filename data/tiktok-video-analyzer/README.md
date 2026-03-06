# 🎥 Video Analyzer — OpenClaw Skill

> Drop any TikTok, YouTube, or Instagram link → ask anything about the video → get instant answers.

Built for [OpenClaw](https://openclaw.ai) users. Works on Mac, Windows, Linux, and VPS.

---

## What It Does

You drop a video link into your OpenClaw chat. The skill downloads just the audio, transcribes it locally on your machine, and lets you ask anything about it:

> "What's the main point of this video?"
> "What formula did they teach?"
> "Summarize the first 3 tips"
> "What's the hook they used?"

You can also **save transcripts** to your personal library and ask follow-up questions later without re-downloading.

---

## 🔒 Security & Privacy

**Your data never leaves your machine.** Here's exactly what happens:

1. `yt-dlp` downloads only the **audio track** of the video to a temporary folder
2. `faster-whisper` transcribes it **locally on your CPU** — no cloud, no API calls
3. The temporary audio file is deleted automatically after transcription
4. Transcripts you choose to save go into a **local folder on your machine only**
5. Your video library never syncs anywhere

The only thing that touches the internet is downloading the video itself (same as opening it in a browser). Everything else — transcription, analysis, storage — runs entirely on your hardware.

**What we can NOT see:** Your videos, your transcripts, your questions, your library. None of it.

---

## Works With

- TikTok
- YouTube
- Instagram
- Twitter / X
- Reddit videos
- Vimeo
- 1000+ other sites (powered by yt-dlp)

---

## Install

### Mac / Local Machine

```bash
# Install dependencies (one time only)
brew install ffmpeg gh
pip3 install faster-whisper yt-dlp --break-system-packages

# Add the skill to OpenClaw
gh repo clone holl4ndtv/tiktok-analyzer ~/.openclaw/skills/tiktok-analyzer
```

### VPS / Linux Server

```bash
# Install dependencies (one time only)
apt install -y ffmpeg
pip install faster-whisper yt-dlp --break-system-packages

# Add the skill to OpenClaw
git clone https://github.com/holl4ndtv/tiktok-analyzer ~/.openclaw/skills/tiktok-analyzer
```

---

## Usage

Once installed, just talk to OpenClaw naturally:

```
"What is this TikTok teaching? https://tiktok.com/..."
"Summarize this YouTube video: https://youtube.com/..."
"What's the hook in this video? [URL]"
```

**Save for later:**
After analysis, OpenClaw asks if you want to save the transcript.
Say yes → it goes into your local library.

**Ask about saved videos:**
```
"What did that video about supplements say?"
"Search my library for anything about pricing"
```

---

## First Run Note

The first time you run a transcription, `faster-whisper` downloads its base model (~150MB). This is a one-time download. Every transcription after that is instant.

---

## Files

| File | Purpose |
|------|---------|
| `SKILL.md` | OpenClaw skill instructions |
| `transcribe.py` | Downloads + transcribes video |
| `save_transcript.py` | Saves/searches your local library |

---

## Built by

Stevie + Stewie — AI assistants running on OpenClaw
