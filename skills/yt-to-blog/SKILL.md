---
name: yt-to-blog
description: >
  Full content pipeline: YouTube URL → transcript → blog post → Substack draft → X/Twitter thread →
  vertical video clips via HeyGen AI avatar. One URL in, entire content suite out. Use when asked to:
  "turn this video into content", "create a content suite from this YouTube video", "write a blog from
  this video", "repurpose this video", or any video-to-multi-platform content request.
  Can run the full pipeline or individual steps.
---

# YT-to-Blog Content Engine

YouTube URL → blog post + Substack + tweets + vertical video clips. The whole content machine.

## Pipeline Overview

```
YouTube URL
  ↓
① Transcript (summarize CLI)
  ↓
② Blog Draft (AI-written in your voice)
  ↓
③ Substack Publish (browser automation)
  ↓
④ X/Twitter Post (bird CLI)
  ↓
④b Facebook Group (optional reminder)
  ↓
⑤ Script Splitter (extract hook moments)
  ↓
⑥ HeyGen Videos (AI avatar vertical clips)
  ↓
⑦ Post-Processing (ffmpeg crop/scale)
  ↓
📁 Output Folder (blog.md, videos, tweet.txt, URLs)
```

**One URL in → Five platforms out.** Run the whole thing or any step individually.

---

## First-Time Setup Wizard

Walk the user through this on first use. It takes ~10 minutes once, then never again.

### Step 1: Check Dependencies

Run the setup script to check what's installed:

```bash
bash skills/yt-content-engine/setup.sh
```

Required CLIs:
| Tool | Purpose | Install |
|------|---------|---------|
| `summarize` | YouTube transcript extraction | `brew install steipete/tap/summarize` |
| `bird` | X/Twitter posting | `brew install steipete/tap/bird` |
| `ffmpeg` | Video post-processing | `brew install ffmpeg` |
| `curl` | API calls to HeyGen | Usually pre-installed on macOS |
| `python3` | Helper scripts | Usually pre-installed on macOS |

If anything is missing, tell the user what to install and wait for confirmation.

### Step 2: HeyGen API Key

1. Tell the user: "Go to https://app.heygen.com/settings — grab your API key from the API section."
2. If they don't have a HeyGen account: "Sign up at https://heygen.com — the free tier gives you a few credits to test with."
3. Save the key to `config.json` (see config schema below).
4. Test it:

```bash
curl -s -H "X-Api-Key: API_KEY_HERE" https://api.heygen.com/v2/avatars | python3 -c "import sys,json; d=json.load(sys.stdin); print('✅ API key works!' if 'data' in d else '❌ Invalid key')"
```

### Step 3: HeyGen Avatar Setup

Tell the user:

> "For vertical video clips, you need a HeyGen avatar. Here's what matters:
>
> **Record in PORTRAIT mode** (hold your phone vertically). This is critical — if you record landscape, the avatar will be a small strip in the center of a 9:16 frame and we'll need to crop/scale it (which works but loses quality).
>
> Go to https://app.heygen.com/avatars → Create Instant Avatar → follow their recording guide. Stand in good lighting, look at camera, speak naturally for 2+ minutes.
>
> Once created, grab your Avatar ID from the avatar details page."

List their existing avatars to help them pick. Note: the avatars endpoint returns both custom and stock avatars — filter for the user's custom ones (they typically appear first and have personal names):

```bash
curl -s -H "X-Api-Key: API_KEY" https://api.heygen.com/v2/avatars | python3 -c "
import sys, json
data = json.load(sys.stdin)
for a in data.get('data', {}).get('avatars', []):
    print(f\"  {a['avatar_id']} — {a.get('avatar_name', 'unnamed')}\")
"
```

### Step 4: HeyGen Voice Clone

Tell the user:

> "Go to https://app.heygen.com/voice-clone → Clone your voice. Upload a clean audio sample (1-2 min of you speaking naturally). HeyGen will create a voice ID.
>
> Once done, grab your Voice ID from the voice settings."

List their voices. User's cloned voices typically appear first; stock voices come after:

```bash
curl -s -H "X-Api-Key: API_KEY" https://api.heygen.com/v2/voices | python3 -c "
import sys, json
data = json.load(sys.stdin)
for v in data.get('data', {}).get('voices', []):
    print(f\"  {v['voice_id']} — {v.get('name', 'unnamed')} ({v.get('language', '?')})\")
"
```

⚠️ **IMPORTANT:** Use the FULL voice_id (e.g., `69da9c9bca78499b98fdac698d2a20cd`), not a truncated version. The API will return "Voice validation failed" if you use a shortened ID.

### Step 5: Substack Login

Substack has no API — posting requires browser automation.

1. Open the OpenClaw managed browser: use browser tool with `profile="openclaw"`
2. Navigate to `https://substack.com/sign-in`
3. Help the user log in with their credentials
4. Verify access by navigating to their publication dashboard
5. Save the publication URL to `config.json`

The browser session persists across restarts. One-time setup.

### Step 6: Save Config

Create `skills/yt-content-engine/config.json` (relative to your workspace):

```json
{
  "heygen": {
    "apiKey": "YOUR_API_KEY",
    "avatarId": "YOUR_AVATAR_ID",
    "voiceId": "YOUR_VOICE_ID"
  },
  "substack": {
    "publication": "yourblog.substack.com"
  },
  "twitter": {
    "handle": "@yourhandle"
  },
  "author": {
    "voice": "Description of your writing voice and style",
    "name": "Your Name"
  },
  "video": {
    "clipCount": 5,
    "maxClipSeconds": 60,
    "cropMode": "auto"
  }
}
```

**Tip:** If the user already has a voice guide from the `yt-to-blog` skill, read it from `skills/yt-to-blog/references/voice-guide.md` and use it for the `author.voice` field.

### Step 7: Verify Everything

Run the setup script with the config in place:

```bash
bash skills/yt-content-engine/setup.sh
```

It will test each component and report status.

---

## How to Invoke

### Full Pipeline
```
"Turn this into a full content suite: https://youtu.be/XXXXX"
"Content engine this video: [URL]"
"Run the full pipeline on [URL]"
```

### Individual Steps
```
"Just get me the transcript from [URL]"
"Write a blog post from [URL]" (steps 1-2)
"Post this to Substack" (step 3, after blog exists)
"Tweet about this blog post" (step 4)
"Generate video clips from this blog" (steps 5-7)
"Just split this into scripts" (step 5 only)
```

---

## Pipeline Steps

### Step ①: Transcript

Create the output directory for this run, then fetch the YouTube transcript:

```bash
mkdir -p /tmp/yt-content-engine/output-$(date +%Y-%m-%d)/scripts
mkdir -p /tmp/yt-content-engine/output-$(date +%Y-%m-%d)/videos
```

```bash
summarize "YOUTUBE_URL" --extract > /tmp/yt-content-engine/transcript.txt
```

The `--extract` flag prints the raw transcript without LLM summarization. Read the output. If it fails (no captions available), try with `--youtube yt-dlp` for auto-generated captions, or tell the user and suggest they provide a manual transcript.

### Step ②: Blog Draft

Transform the transcript into a polished long-form blog post.

**Load the author voice** from `config.json` → `author.voice`. If a more detailed voice guide exists at `skills/yt-to-blog/references/voice-guide.md`, read and use that too.

**Analysis phase** — before writing, extract from the transcript:
- Core thesis — the single strongest argument or revelation
- Key data points — statistics, quotes, dates, names
- Narrative moments — anecdotes, examples, scenes
- Source links — URLs, studies, references mentioned
- Missing context — what does the reader need that the video assumed?

**Writing structure:**
1. **Cold open (1-3 paragraphs):** Scene-setting. Specific, sensory, emotional hook before data.
2. **Thesis pivot (1 paragraph):** Connect scene to the bigger story.
3. **Data body (5-15 paragraphs):** Alternate data and editorial. Each stat gets a punch line. Subheadings for major breaks only.
4. **Callback (1-2 paragraphs):** Return to opening scene/metaphor.
5. **Closing (3-6 short paragraphs):** Escalating fragments. Final hammer line.

**Writing rules:**
- Vary sentence length dramatically — long data sentences, then short punches
- Em dashes for asides, not parentheses
- Sentence fragments for emphasis
- No bullet lists in the body — narrative flow
- Inline source links, no footnotes
- No "in conclusion" or "to summarize"
- Credit video source naturally: "As [Name] put it..." with link
- Target: 1,500-3,000 words

**Generate 3-5 headline options** with distinct strategies (contrast/irony, revelation, moral framing, callback). Each with a subtitle. Let the user pick.

Save the final draft to the output folder as `blog.md`.

### Step ③: Substack Publish

Post the blog to Substack via browser automation.

1. Read `config.json` → `substack.publication`
2. Open managed browser (`profile="openclaw"`)
3. Navigate to `https://PUBLICATION.substack.com/publish/post`
4. Click the title field, type the title
5. Click the subtitle area, type the subtitle
6. Click the body area
7. Write markdown to a temp file, copy to clipboard (`pbcopy < /tmp/post.md`), paste into editor (Meta+v)
8. Substack auto-saves as draft

**Known issues:**
- Em dashes (`—`) may garble as `,Äî` during clipboard paste → find/replace after paste
- Large posts: pause briefly between paste and verification
- Verify draft at `https://PUBLICATION.substack.com/publish`

**Default: save as draft.** Only publish if the user explicitly says "publish it" — always confirm first.

Save the Substack URL to `output/substack-url.txt`.

### Step ④: X/Twitter Post

Compose and post using the `bird` CLI.

**Compose the tweet/thread:**
- If the blog has a single killer hook → single tweet with link
- If there are multiple strong points → thread (3-5 tweets)
- Include the Substack URL
- Match the author's voice but punchier — tweets are hooks, not summaries
- Use the handle from `config.json` → `twitter.handle`

**Post with bird:**
```bash
# Single tweet
bird tweet "Your tweet text here"

# Thread (post first tweet, then reply to it)
bird tweet "Tweet 1 text here"
# Note the returned tweet ID, then:
bird reply TWEET_ID "Tweet 2 text here"
# And chain:
bird reply TWEET_2_ID "Tweet 3 text here"
```

**Always show the user the tweet text before posting and get confirmation.**

Save tweet text to `output/tweet.txt`.

### Step ④b: Facebook Group (Optional)

If `config.json` includes a `facebook.group` URL, remind the user to post to their Facebook Group.

**Note:** Facebook Group API posting is heavily restricted. Browser automation is unreliable due to Facebook's anti-bot measures. Best approach:

1. Draft a Facebook post version of the content (shorter, more casual than tweet)
2. Save to `output/facebook-post.txt`
3. Remind the user: "Don't forget to post to [Group Name] — here's your draft"
4. User posts manually

This keeps Facebook distribution in the workflow without fighting their API restrictions.

### Step ⑤: Script Splitter

Extract 3-5 "hook moments" from the blog post and rewrite each as a spoken-word script for vertical video.

**What to look for** (scan the blog for these patterns):
1. **Hook/Controversy** — the most provocative claim, the thing that makes people stop scrolling
2. **Data Bomb** — a surprising statistic or fact that reframes understanding
3. **Counterintuitive Take** — something that contradicts conventional wisdom
4. **Emotional Moment** — a story, anecdote, or human element that creates connection
5. **Call-to-Action Closer** — a rallying cry, challenge, or "what you should do now"

Not every blog will have all five. Extract what's there. Minimum 3 clips.

**Rewrite rules for spoken delivery:**
- **Hook first** — open with the most attention-grabbing line. No preamble.
- **Conversational** — write for speaking, not reading. Contractions, natural rhythm.
- **30-60 seconds each** — roughly 75-150 words per clip
- **Self-contained** — each clip must work on its own, no "as I mentioned earlier"
- **End with punch** — close on the strongest line, not a trailing thought
- **No stage directions** — just the words to speak, nothing else

**Format each script:**
```
CLIP 1: [descriptive title]
---
[Script text here, 75-150 words]
```

Use `config.json` → `video.clipCount` for the target number of clips (default: 5).
Use `config.json` → `video.maxClipSeconds` for max duration (default: 60).

Save scripts to `output/scripts/clip-1.txt`, `clip-2.txt`, etc.

### Step ⑥: HeyGen Video Generation

Submit each script to HeyGen API v2 to generate AI avatar videos.

**Read config:**
```bash
# Parse config.json
API_KEY=$(python3 -c "import json; c=json.load(open('config.json')); print(c['heygen']['apiKey'])")
AVATAR_ID=$(python3 -c "import json; c=json.load(open('config.json')); print(c['heygen']['avatarId'])")
VOICE_ID=$(python3 -c "import json; c=json.load(open('config.json')); print(c['heygen']['voiceId'])")
```

**For each script, submit a video generation request:**

```bash
curl -s -X POST "https://api.heygen.com/v2/video/generate" \
  -H "X-Api-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "video_inputs": [{
      "character": {
        "type": "avatar",
        "avatar_id": "'"$AVATAR_ID"'",
        "avatar_style": "normal"
      },
      "voice": {
        "type": "text",
        "input_text": "'"$(cat output/scripts/clip-1.txt)"'",
        "voice_id": "'"$VOICE_ID"'"
      }
    }],
    "dimension": {
      "width": 1080,
      "height": 1920
    }
  }'
```

**Parse the response** to get `video_id`:
```python
import json
response = json.loads(response_text)
video_id = response["data"]["video_id"]
```

**Submit ALL clips before polling.** HeyGen renders in parallel — submit all scripts first, collect all video_ids, then poll them all. This cuts total render time from N×3min to ~3min.

**Poll for completion** (every 15 seconds, timeout after 10 minutes):

```bash
curl -s -H "X-Api-Key: $API_KEY" \
  "https://api.heygen.com/v1/video_status.get?video_id=$VIDEO_ID" \
  | python3 -c "import sys,json; d=json.load(sys.stdin)['data']; print(d['status'], d.get('video_url',''))"
```

Statuses: `pending` → `processing` → `completed` (with `video_url`) or `failed` (with `error`).

**Download completed videos:**
```bash
curl -L -o "output/videos/clip-1-raw.mp4" "$VIDEO_URL"
```

**Credit note:** ~1 credit per 1 minute of video. A typical 5-clip run uses ~3 credits. Warn the user about credit usage before submitting.

### Step ⑦: Video Post-Processing

If the avatar was recorded in landscape (common), the 9:16 video will show a small avatar strip centered in a large frame with background fill. Fix this with ffmpeg.

**Check `config.json` → `video.cropMode`:**
- `"auto"` — detect and crop automatically
- `"portrait"` — skip cropping (avatar was recorded in portrait)
- `"manual"` — ask user for crop coordinates

**Auto-crop pipeline:**

```bash
# 1. Detect content bounds by scanning center column for non-background pixels
# Extract a single frame
ffmpeg -i input.mp4 -vframes 1 -y /tmp/frame.png

# 2. Use ffmpeg cropdetect to find content bounds
ffmpeg -i input.mp4 -vf "cropdetect=24:16:0" -frames:v 30 -f null - 2>&1 | grep cropdetect

# Parse the crop values from output: crop=W:H:X:Y

# 3. Crop content strip, scale up, center-crop to 1080x1920
ffmpeg -i input.mp4 \
  -vf "crop=DETECTED_W:DETECTED_H:DETECTED_X:DETECTED_Y,scale=1080:-1,crop=1080:1920:0:(ih-1920)/2" \
  -c:a copy \
  -y output.mp4
```

**Alternative manual detection** (preferred — cropdetect often fails when background is white/light):

HeyGen typically renders landscape avatars centered on a white/light background in the 9:16 frame.
Scan the center column for non-white pixels to find the actual content strip:

```bash
# Extract a frame, then scan center column for content bounds
ffmpeg -y -ss 5 -i input.mp4 -frames:v 1 /tmp/frame.png 2>/dev/null

ffmpeg -y -i /tmp/frame.png -vf "crop=1:ih:iw/2:0,format=gray" -f rawvideo -pix_fmt gray - 2>/dev/null | \
  python3 -c "
import sys
data = sys.stdin.buffer.read()
first = last = None
for i, b in enumerate(data):
    if b < 240:  # Non-white pixel = actual content
        if first is None: first = i
        last = i
if first is not None:
    print(f'CONTENT_Y={first}')
    print(f'CONTENT_HEIGHT={last - first}')
    print(f'CENTER={( first + last) // 2}')
else:
    print('No content bounds detected — avatar may already fill the frame')
"
```

Then crop the content strip, scale proportionally to fill width, and center-crop to 9:16:
```bash
ffmpeg -y -i input.mp4 \
  -vf "crop=iw:CONTENT_HEIGHT:0:CONTENT_Y,scale=-1:1920,crop=1080:1920:(ow-1080)/2:0" \
  -c:v libx264 -crf 23 -preset fast -c:a aac \
  output.mp4
```

**Proven crop values for common HeyGen landscape avatars** (1080x1920 canvas):
- Content strip typically at y≈656, height≈607px
- Example: `crop=1080:607:0:656,scale=3413:1920,crop=1080:1920:1166:0`
- Always detect per-video — avatar placement can shift

**Save processed videos** to `output/videos/clip-1.mp4`, `clip-2.mp4`, etc.

If crop mode is `portrait`, just copy the raw files:
```bash
cp output/videos/clip-1-raw.mp4 output/videos/clip-1.mp4
```

### Step ⑧: Output

Organize everything in a dated output folder:

```
output-YYYY-MM-DD/
├── blog.md              # Final blog post
├── tweet.txt            # Tweet text (posted or ready to post)
├── substack-url.txt     # URL of Substack draft/post
├── scripts/
│   ├── clip-1.txt       # Spoken word scripts
│   ├── clip-2.txt
│   └── ...
├── videos/
│   ├── clip-1.mp4       # Final processed vertical videos
│   ├── clip-2.mp4
│   └── ...
└── manifest.json        # Run metadata
```

**manifest.json:**
```json
{
  "source": "https://youtu.be/XXXXX",
  "date": "2026-02-03",
  "blog": "blog.md",
  "substackUrl": "https://...",
  "tweetUrl": "https://...",
  "clips": ["clip-1.mp4", "clip-2.mp4", "..."],
  "heygenCreditsUsed": 3
}
```

Report the summary to the user:
- ✅ Blog post: X words
- ✅ Substack: [URL] (draft/published)
- ✅ Tweet: posted / ready to post
- ✅ X video clips generated and processed
- 💰 HeyGen credits used: ~X

---

## Config Reference

Config file: `skills/yt-content-engine/config.json` (relative to workspace root)

| Key | Description | Default |
|-----|-------------|---------|
| `heygen.apiKey` | HeyGen API key | Required |
| `heygen.avatarId` | Your HeyGen avatar ID | Required |
| `heygen.voiceId` | Your cloned voice ID | Required |
| `substack.publication` | Substack subdomain | Required |
| `twitter.handle` | X/Twitter handle | Required |
| `author.voice` | Writing style description | Recommended |
| `author.name` | Author name for attribution | Recommended |
| `video.clipCount` | Number of clips to generate | `5` |
| `video.maxClipSeconds` | Max seconds per clip | `60` |
| `video.cropMode` | `auto`, `portrait`, or `manual` | `auto` |

---

## Tips & Troubleshooting

- **HeyGen rendering takes 2-3 min per clip.** Set expectations — a 5-clip run takes 10-15 minutes of render time.
- **Portrait avatars save time.** No cropping needed. Worth re-recording if you use this regularly.
- **Substack session expires?** Re-run the browser login step (Step 5 of setup).
- **bird CLI not posting?** Run `bird auth` to re-authenticate.
- **Bad crop detection?** Switch `cropMode` to `manual` and eyeball the content bounds from a frame export.
- **HeyGen quota errors?** Check credits at https://app.heygen.com/settings — upgrade plan or reduce clip count.
- **Transcript unavailable?** Some videos don't have captions. Try `summarize "URL" --extract --youtube yt-dlp` for auto-generated captions, or ask the user for a manual transcript.
