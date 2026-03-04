---
name: demo-slap
description: Generate CS2 highlights and fragmovies from demos using the Demo-Slap API. Includes optional Leetify integration for auto-fetching demo URLs. Use when a user asks to "record a highlight", "make a fragmovie", "clip that round", etc.
metadata:
  {
    "openclaw": {
      "requires": {
        "env": ["DEMOSLAP_API_KEY"],
        "bins": ["ffmpeg", "python3"]
      }
    }
  }
---

# Demo-Slap Highlight Skill

Generate beautiful MP4 highlights and fragmovies straight from CS2 demos.

## 🔗 APIs & Prerequisites
- **Demo-Slap API:** [https://api-doc.demo-slap.net/](https://api-doc.demo-slap.net/)
- **Leetify API (Optional but recommended):** [https://api-public-docs.cs-prod.leetify.com/](https://api-public-docs.cs-prod.leetify.com/)

**Using Leetify:** 
Leetify integration is optional but highly recommended to automatically fetch demo URLs from recent matches. 
- **API Key:** Free to get at [leetify.com/app/developer](https://leetify.com/app/developer).
- **Steam64 ID:** Users can find their 17-digit Steam64 ID using sites like [steamid.io](https://steamid.io/) or by checking their Steam profile URL.

## 🛠 Identity & Setup

### 1. Set API Keys (One-time setup)
You need to save the API keys to `data/config.json`. You can do this via the CLI:
```bash
python3 scripts/demo_slap_cli.py set-key demoslap <DEMOSLAP_API_KEY>
python3 scripts/demo_slap_cli.py set-key leetify <LEETIFY_API_KEY>
```
*Note: The keys can also be provided via `DEMOSLAP_API_KEY` and `LEETIFY_API_KEY` environment variables.*

### 2. Map User to Steam ID
To map a user's chat username (Telegram, Discord, Slack, etc.) or nickname to their Steam64 ID (required for Leetify match fetching and filtering their specific highlights):

```bash
python3 scripts/demo_slap_cli.py save-id <USERNAME> <STEAM_64_ID>
```
*If a user asks for their highlights but their Steam ID is unknown, explain how to find it (e.g., via steamid.io), then run this command.*

## 📋 Step 1: Find the Match (Optional)

If the user wants a highlight from a recent match and the Leetify API key is available, you can list their recent matches:

```bash
python3 scripts/demo_slap_cli.py matches <USERNAME>
```
*This lists their recent matches (index 0 is the most recent). Note the index they want.*

If the Leetify API key is NOT available or the user wants to use a specific match not tracked, **ask them to provide a direct download link (.dem.gz or similar) to the demo.**

## 🔍 Step 2: Analyze the Demo (Async)

**CRITICAL: DO NOT BLOCK THE MAIN SESSION.** Analysis on Demo-Slap servers takes 2-4 minutes. You MUST use `sessions_spawn` to run this step asynchronously. When using relative paths, ensure your `cwd` points to this skill's folder or run the command relative to it.

**Subagent Prompt Template:**
```text
Task: Analyze a demo for highlights.
1. Run the analysis command:
   # If using Leetify match index (e.g. index 0):
   exec(command="python3 -u scripts/demo_slap_cli.py analyze --username <USERNAME> --match-index <N>")
   
   # OR if using a direct URL:
   exec(command="python3 -u scripts/demo_slap_cli.py analyze --url '<URL>' --username <USERNAME>")

2. Loop `process(action="poll", sessionId="...", timeout=30000)` until the script finishes.
3. Extract the printed table of highlights (with JobID and Highlight IDs).
4. Send the table to the user in their channel using the `message` tool (`action="send"`). Ask them: "Which Highlight ID(s) do you want to render?"
5. Reply NO_REPLY.
```

## 🎥 Step 3: Render Highlight or Fragmovie (Async)

Once the user replies with the Highlight ID(s) they want, render the final video.
**CRITICAL: DO NOT BLOCK THE MAIN SESSION.** Rendering and downloading the MP4 takes 2-5 minutes. You MUST use `sessions_spawn` to run this step asynchronously.

**Subagent Prompt Template:**
```text
Task: Render a CS2 clip.
1. Run the render command:
   # For a SINGLE highlight:
   exec(command="python3 -u scripts/demo_slap_cli.py render <JOB_ID> <HIGHLIGHT_ID>")
   
   # For a FRAGMOVIE (multiple highlights stitched together):
   exec(command="python3 -u scripts/demo_slap_cli.py render-fragmovie <JOB_ID> <ID_1> <ID_2> ...")

2. Loop `process(action="poll", sessionId="...", timeout=30000)` until the script finishes and prints the downloaded file path (e.g., `/tmp/render_...mp4`).
3. Check the file size using `du -m <file_path>`.
4. If the file is > 48MB (Telegram limit), compress it:
   `ffmpeg -i <file_path> -c:v libx264 -crf 28 -preset fast -c:a aac -b:a 128k /tmp/compressed_clip.mp4`
   Then use the compressed file path for the next step.
5. Send the video to the user using the `message` tool (`action="send"`, `media="<final_file_path>"`).
   ⚠️ CRITICAL: Set `timeoutMs: 120000` (2 minutes) on the `message` tool call because uploading large videos takes time!
6. Remove the MP4 files from `/tmp/`.
7. Reply NO_REPLY.
```
