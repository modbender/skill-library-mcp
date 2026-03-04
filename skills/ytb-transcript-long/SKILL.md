---
name: youtube-transcript
description: YouTube long video (>1 hour) full verbatim transcription and translation workflow. Use when user needs to (1) Extract subtitles from YouTube videos, (2) Translate English transcripts to Chinese, (3) Handle long videos that exceed session limits, (4) Process DownSub API responses and generate formatted documents.
---

# YouTube Long Video Transcript & Translation

Full verbatim transcription and translation workflow for long YouTube videos (>1 hour).

## Prerequisites

- DownSub API key (Bearer token starting with `AIza...`)
- `zhiyan` tool (optional, for online doc generation)
- Sub-agent spawn capability (for long videos)

## DownSub API Configuration

**Endpoint**: `https://api.downsub.com/download`
**Method**: `POST`
**Headers**:
```
Authorization: Bearer AIzaM9ifctIOxusNAldvGeajHqq4rH6e7MJNfN
Content-Type: application/json
```
**Body**:
```json
{"url": "https://www.youtube.com/watch?v=VIDEO_ID"}
```

**⚠️ CRITICAL**: Always check the `lang` field in response. **Use ONLY `en` or `en-auto`**. Do NOT use random languages (e.g., `lt` for Lithuanian).

## Pre-flight Check (Run First)

1. **Check DownSub API Access**
   - Verify `Authorization` header is configured
   - Common error: "401 Unauthorized" = missing/invalid API key

2. **Check Output Capabilities**
   - Has `zhiyan` tool? → Can generate online docs
   - No `zhiyan`? → Output local `.md` file

3. **Check Session Budget**
   - Ensure sub-agent spawn capability for long context processing

## Workflow

### Step 1: Preparation (Main Session)

1. **Environment Check**: Confirm DownSub API key present
2. **Get video link**
3. **Verify Language**: Use DownSub to check `lang`
   - IF `lang="en"` or `"en-auto"` → Proceed
   - IF `lang="lt"` or other → STOP, do not translate
4. **Check Length**: If >1000 lines, DO NOT process in main session
5. **Spawn Sub-Agent**:
   ```
   Task: Translate transcript.txt to Chinese verbatim.
   Process in 500-line chunks to separate files (part1.md, etc.).
   Merge to full_transcript.md.
   Add Executive Summary and Key Metrics Table (Chinese) at top.
   Do NOT use zhiyan.
   Budget: 30 minutes or $2 cost limit.
   ```

### Step 2: Execution (Sub-Agent)

1. **Read & Slice**: Read in chunks (limit=500). Do NOT read full file at once.
2. **Translate & Format**: Translate verbatim to Chinese. Add headers (e.g., `## 开场`).
3. **Stream Write**: Write each chunk to separate files or use `cat >>` to append.
4. **Enhance**:
   - Read first 500 lines to extract Key Metrics (Revenue, Growth, etc.)
   - Generate Executive Summary (3-5 bullets, Chinese)
   - Create Key Metrics Table (Markdown)
   - Prepend to final file
5. **Report**: Return path to `full_transcript.md`

### Step 3: Delivery (Main Session)

1. Receive file path from sub-agent
2. **Upload**: Run `zhiyan` MCP (`parse_markdown`) if available
3. Send doc link/file to user

## Troubleshooting

**Q: "What is the DownSub API Key?"**
→ API key missing. Provide Bearer token or configure in secrets.

**Q: "Tool `zhiyan` not found"**
→ `zhiyan` MCP not installed. **Solution**: Skip upload, send `.md` file directly.

**Q: Translates into nonsense/random text**
→ Downloaded wrong subtitle track (e.g., Lithuanian). **Solution**: Check `lang` field, use only `en`.

**Q: Task times out or stops responding**
→ Video too long for single session. **Solution**: Spawn sub-agent to process in background.
