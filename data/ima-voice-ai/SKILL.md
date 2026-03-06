---
name: IMA Studio Music Generation
version: 1.0.1
category: file-generation
author: IMA Studio (imastudio.com)
keywords: imastudio, music generation, ai music
argument-hint: "[music description or lyrics]"
description: >
  Use for AI music generation via IMA Open API. Supports text_to_music with 3 models.
  IMPORTANT — Default model selection rule: always recommend the NEWEST and most POPULAR model,
  NOT the cheapest. Default: Suno (model_id=sonic, model_version=sonic-v5, 25pts) — latest
  engine, full-featured with custom mode, lyrics, vocal gender, style tags. Alternative:
  DouBao BGM (model=GenBGM, 30pts) for background music; DouBao Song (model=GenSong, 30pts)
  for songs. Use Suno sonic by default unless user asks for BGM/song only.
  Output is MP3/WAV. Requires an ima_* API key.
---

# IMA Voice AI Creation

## ⚙️ How This Skill Works

**For transparency:** This skill uses a bundled Python script (`scripts/ima_voice_create.py`) to call the IMA Open API. The script:
- Sends your prompt to `https://api.imastudio.com` (IMA's servers)
- Uses `--user-id` **only locally** as a key for storing your model preferences
- Returns a music URL when generation is complete

**What gets sent to IMA servers:**
- ✅ Your music prompt/description
- ✅ Model selection (Suno/DouBao)
- ❌ NO API key in prompts (key is used for authentication only)
- ❌ NO user_id (it's only used locally)

**What's stored locally:**
- `~/.openclaw/memory/ima_prefs.json` - Your model preferences (< 1 KB)
- `~/.openclaw/logs/ima_skills/` - Generation logs (auto-deleted after 7 days)
- See [SECURITY.md](SECURITY.md) for complete privacy policy

### Agent Execution (Internal Reference)

> **Note for users:** You can review the script source at `scripts/ima_voice_create.py` anytime.  
> **This skill uses only `api.imastudio.com`** (no image upload needed for music generation, unlike image/video skills which also use `imapi.liveme.com`).

Use the bundled script internally:

```bash
# Generate music — Suno sonic-v5
python3 {baseDir}/scripts/ima_voice_create.py \
  --api-key  $IMA_API_KEY \
  --task-type text_to_music \
  --model-id  sonic \
  --prompt   "upbeat lo-fi hip hop, 90 BPM, no vocals" \
  --user-id  {user_id} \
  --output-json

# DouBao BGM
python3 {baseDir}/scripts/ima_voice_create.py \
  --api-key  $IMA_API_KEY \
  --model-id  GenBGM \
  --prompt   "calm ambient piano background" \
  --user-id  {user_id} \
  --output-json
```

The script outputs JSON — parse it to get the result URL and pass it to the user via the UX protocol messages below.

---

## Overview

Call IMA Open API to create AI-generated music/audio. All endpoints require an `ima_*` API key. The core flow is: **query products → create task → poll until done**.

---

## 🔒 Security & Transparency Policy

> **This skill is community-maintained and open for inspection.**

### 🌐 Network Architecture

**This skill uses a simpler network architecture than image/video skills:**

| Skill Type | Domains Used | Why |
|------------|--------------|-----|
| **ima-voice-ai** (this skill) | ✅ `api.imastudio.com` only | Music generation doesn't require image uploads |
| ima-image-ai, ima-video-ai | `api.imastudio.com` + `imapi.liveme.com` | Image/video tasks need image upload service |

**Why the difference?**
- **Music generation** (text_to_music) only needs text prompts → single API endpoint
- **Image/video generation** (i2i, i2v tasks) needs image file uploads → requires separate upload service

**Security verification:**
```bash
# Verify this skill only uses api.imastudio.com:
grep -n "https://" scripts/ima_voice_create.py

# Expected output:
# Only https://api.imastudio.com (no imapi.liveme.com)
```

---

### ✅ What Users CAN Do

**Full transparency:**
- ✅ **Review all source code**: Check `scripts/ima_voice_create.py` and `ima_logger.py` anytime
- ✅ **Verify network calls**: **This skill uses only `api.imastudio.com`** (music generation doesn't require image uploads). Verify by running: `grep -n "https://" scripts/ima_voice_create.py`
- ✅ **Inspect local data**: View `~/.openclaw/memory/ima_prefs.json` and log files
- ✅ **Control privacy**: Delete preferences/logs anytime, or disable file writes (see below)

**Configuration allowed:**
- ✅ **Set API key** in environment or agent config:
  - Environment variable: `export IMA_API_KEY=ima_your_key_here`
  - OpenClaw/MCP config: Add `IMA_API_KEY` to agent's environment configuration
  - Get your key at: https://imastudio.com
- ✅ **Use scoped/test keys**: Test with limited API keys, rotate after testing
- ✅ **Disable file writes**: Make prefs/logs read-only or symlink to `/dev/null`

**Data control:**
- ✅ **View stored data**: `cat ~/.openclaw/memory/ima_prefs.json`
- ✅ **Delete preferences**: `rm ~/.openclaw/memory/ima_prefs.json` (resets to defaults)
- ✅ **Delete logs**: `rm -rf ~/.openclaw/logs/ima_skills/` (auto-cleanup after 7 days anyway)
- ✅ **Review security**: See [SECURITY.md](SECURITY.md) for complete privacy policy

### ⚠️ Advanced Users: Fork & Modify

If you need to modify this skill for your use case:
1. **Fork the repository** (don't modify the original)
2. **Update your fork** with your changes
3. **Test thoroughly** with limited API keys
4. **Document your changes** for troubleshooting

**Note:** Modified skills may break API compatibility or introduce security issues. Official support only covers the unmodified version.

### ❌ What to AVOID (Security Risks)

**Actions that could compromise security:**
- ❌ Sharing API keys publicly or in skill files
- ❌ Modifying API endpoints to unknown servers
- ❌ Disabling SSL/TLS certificate verification
- ❌ Logging sensitive user data (prompts, IDs, etc.)
- ❌ Bypassing authentication or billing mechanisms

**Why this matters:**
1. **API Compatibility**: Skill logic aligns with IMA Open API schema
2. **Security**: Malicious modifications could leak credentials or bypass billing
3. **Support**: Modified skills may not be supported
4. **Community**: Breaking changes affect all users

### 📁 File System Access (Declared)

This skill reads/writes the following files:

| Path | Purpose | Size | Auto-cleanup | User Control |
|------|---------|------|--------------|--------------|
| `~/.openclaw/memory/ima_prefs.json` | User model preferences | < 1 KB | No | Delete anytime |
| `~/.openclaw/logs/ima_skills/` | Generation logs | ~10-50 KB/day | 7 days | Delete anytime |

**What's stored:**
- ✅ Model preferences (e.g., "last used: Suno sonic-v5")
- ✅ Timestamps (e.g., "2026-02-27 12:34:56")
- ✅ Task IDs and HTTP status codes
- ❌ NO API keys
- ❌ NO personal data
- ❌ NO prompts or generated content

**Full transparency:** See [SECURITY.md](SECURITY.md) for data flow diagram and privacy policy.

### 📋 Privacy & Data Handling Summary

**What this skill does with your data:**

| Data Type | Sent to IMA? | Stored Locally? | User Control |
|-----------|-------------|-----------------|--------------|
| Music prompts | ✅ Yes (required for generation) | ❌ No | None (required) |
| API key | ✅ Yes (authentication header) | ❌ No | Set via env var |
| user_id (optional CLI arg) | ❌ **Never** (local preference key only) | ✅ Yes (as prefs file key) | Change `--user-id` value |
| Model preferences | ❌ No | ✅ Yes (~/.openclaw) | Delete anytime |
| Generation logs | ❌ No | ✅ Yes (~/.openclaw) | Auto-cleanup 7 days |

**Privacy recommendations:**
1. **Use test/scoped API keys** for initial testing
2. **Note**: `--user-id` is **never sent to IMA servers** - it's only used locally as a key for storing preferences in `~/.openclaw/memory/ima_prefs.json`
3. **Review source code** at `scripts/ima_voice_create.py` to verify network calls (search for `create_task` function)
4. **Rotate API keys** after testing or if compromised

**Get your IMA API key:** Visit https://imastudio.com to register and get started.

### 🔧 For Skill Maintainers Only

**Version control:**
- All changes must go through Git with proper version bumps (semver)
- CHANGELOG.md must document all changes
- Production deployments require code review

**File checksums (optional):**
```bash
# Verify skill integrity
sha256sum SKILL.md scripts/ima_voice_create.py
```

If users report issues, verify file integrity first.

---

## 🧠 User Preference Memory

> User preferences **override** recommended defaults. If a user has generated before, use their preferred model — not the system default.

### Storage: `~/.openclaw/memory/ima_prefs.json`

```json
{
  "user_{user_id}": {
    "text_to_music": { "model_id": "sonic", "model_name": "Suno", "credit": 25, "last_used": "..." }
  }
}
```

If the file or key doesn't exist, fall back to the ⭐ Recommended Defaults below.

### When to Read (Before Every Generation)

1. Load `~/.openclaw/memory/ima_prefs.json` (silently, no error if missing)
2. Look up `user_{user_id}.text_to_music`
3. **If found** → use that model; mention it:
   ```
   🎵 根据你的使用习惯，将用 [Model Name] 帮你生成音乐…
   • 模型：[Model Name]（你的常用模型）
   • 预计耗时：[X ~ Y 秒]
   • 消耗积分：[N pts]
   ```
4. **If not found** → use the ⭐ Recommended Default (Suno sonic-v5)

### When to Write (After Every Successful Generation)

Save the used model to `~/.openclaw/memory/ima_prefs.json` under `user_{user_id}.text_to_music`.  
See `ima-image-ai/SKILL.md` → "User Preference Memory" for the full Python write snippet.

### When to Update (User Explicitly Changes Model)

| Trigger | Action |
|---------|--------|
| `用XXX` / `换成XXX` | Switch + save as new preference |
| `以后都用XXX` / `always use XXX` | Save + confirm: `✅ 已记住！以后音乐生成默认用 [XXX]` |
| `用便宜的` / `cheapest` | Use DouBao BGM/Song; do NOT save unless user says "以后都用" |

---

## ⭐ Recommended Defaults

> **These are fallback defaults — only used when no user preference exists.**  
> **Always default to the newest and most popular model. Do NOT default to the cheapest.**

| Task | Default Model | model_id | model_version | Cost | Why |
|------|--------------|----------|---------------|------|-----|
| text_to_music | **Suno (sonic-v5)** | `sonic` | `sonic` | 25 pts | Latest Suno engine, best quality |
| text_to_music (BGM only) | **DouBao BGM** | `GenBGM` | `GenBGM` | 30 pts | Background music |
| text_to_music (song) | **DouBao Song** | `GenSong` | `GenSong` | 30 pts | Song generation |

**Selection guide by use case:**
- Custom song with lyrics, vocals, style → **Suno sonic-v5** (default)
- Background music / ambient loop → **DouBao BGM**
- Simple song generation → **DouBao Song**
- User explicitly asks for cheapest → DouBao BGM/Song (6pts each) — only if explicitly requested

> ⚠️ For Suno: `model_version` inside `parameters` (e.g. `sonic-v5`) is different from the outer `model_version` field (which is `sonic`). Always set both.

---

## 💬 User Experience Protocol (IM / Feishu / Discord) v1.1 🆕

> **v1.1 Update:** Added Step 0 to ensure correct message ordering in group chats (learned from ima-image-ai v1.2).
>
> Music generation completes in 10~45 seconds. **Never let users wait in silence.**  
> Always follow all 5 steps below, every single time.

### 🚫 Never Say to Users

| ❌ Never say | ✅ What users care about |
|-------------|--------------------------|
| `ima_voice_create.py` / 脚本 / script | — |
| 自动化脚本 / automation | — |
| 自动处理产品列表 / 查询接口 | — |
| 自动解析参数 / 智能轮询 | — |
| attribute_id / model_version / form_config | — |
| API 调用 / HTTP 请求 / 任何技术参数名 | — |

Only tell users: **model name · estimated time · credits · result (audio file/player) · plain-language status**.

---

### Estimated Generation Time per Model

| Model | Estimated Time | Poll Every | Send Progress Every |
|-------|---------------|------------|---------------------|
| DouBao BGM | 10~25s | 5s | 10s |
| DouBao Song | 10~25s | 5s | 10s |
| Suno (sonic-v5) | 20~45s | 5s | 15s |

`estimated_max_seconds` = upper bound (e.g. 45 for Suno, 25 for DouBao BGM/Song).

---

### Step 0 — Initial Acknowledgment Reply (Normal Reply) 🆕

**⚠️ CRITICAL:** This step ensures correct message ordering in group chats.

**Before doing anything else**, reply to the user with a friendly acknowledgment message using your **normal reply** (not `message` tool). This reply will automatically appear FIRST in the conversation.

**Example acknowledgment messages:**
```
好的！马上帮你生成轻松的背景音乐 🎵
```
```
收到！用 Suno 为你创作一首歌 🎶
```
```
OK! Starting music generation with DouBao BGM 🎵
```

**Rules:**
- Keep it short and warm (< 15 words)
- Match the user's language (Chinese/English)
- Include relevant emoji (🎵/🎶/🎸/🎹)
- This is your ONLY normal reply — all subsequent updates use `message` tool

**Why this matters:**
- Normal replies automatically appear FIRST in the conversation thread
- `message` tool pushes appear in chronological order AFTER your initial reply
- This ensures users see: "好的！" → "🎵 开始生成..." → "✅ 成功!" (correct order)

---

### Step 1 — Pre-Generation Notification (Push via message tool)

**After Step 0 reply**, use the `message` tool to push a notification immediately to the group/channel:

```python
# Agent implementation
message(
    action="send",
    target=group_id,  # or channel_id for Discord
    message="""🎵 开始生成音乐，请稍候…
• 模型：[Model Name]
• 预计耗时：[X ~ Y 秒]
• 消耗积分：[N pts]"""
)
```

**User-facing message template:**
```
🎵 开始生成音乐，请稍候…
• 模型：[Model Name]
• 预计耗时：[X ~ Y 秒]
• 消耗积分：[N pts]
```

**Cost transparency:**
- Balanced (Suno 25 pts): "使用 Suno（25 积分，功能最全）"
- DouBao alternatives (30 pts each): "使用 DouBao BGM（30 积分）" — only if user explicitly requests DouBao or background music type

> Adapt language to match the user. English → `🎵 Starting music generation, please wait [X~Y] seconds…`

---

### Step 2 — Progress Updates

Poll the task detail API every **5s**.  
Send a progress update every `[Send Progress Every]` seconds per the table above.

```
⏳ 音乐生成中… [P]%
已等待 [elapsed]s，预计最长 [max]s
```

**Progress formula:**
```
P = min(95, floor(elapsed_seconds / estimated_max_seconds * 100))
```

- **Cap at 95%** — never show 100% until the API returns `success`
- If `elapsed > estimated_max`: keep P at 95% and append `「快好了，稍等…」`

---

### Step 3 — Success Notification (Push audio via message tool)

When task status = `success`, use the `message` tool to **send the generated audio directly** (not as a text URL):

**Agent implementation:**
```python
# Get result URL from script output or task detail API
result = get_task_result(task_id)
audio_url = result["medias"][0]["url"]

# Push audio + caption to group/channel
message(
    action="send",
    target=group_id,
    media=audio_url,  # Feishu/Discord will render the audio
    caption=f"""✅ 音乐生成成功！
• 模型：[Model Name]
• 耗时：预计 [X~Y]s，实际 [actual]s
• 消耗积分：[N pts]

🔗 原始链接：{audio_url}"""
)
```

**User-facing message:**
```
✅ 音乐生成成功！
• 模型：[Model Name]
• 耗时：预计 [X~Y]s，实际 [actual]s
• 消耗积分：[N pts]

🔗 原始链接：https://ws.esxscloud.com/.../audio.wav

[音频直接显示为文件卡片，可点击播放]
```

**Platform-specific notes:**
- **Feishu**: `message(action=send, media=url, caption="...")` — caption appears with audio file card
- **Discord**: Audio embeds automatically from URL; caption can be in message text
- **Telegram**: Use `message(action=send, media=url, caption="...")`

**⚠️ Important**: 
- Always send audio via `media` parameter (file card/player) + include URL in caption text
- Do NOT use local file paths like `/tmp/audio.wav` — use HTTP URL from API
- Users expect: (1) clickable audio file card + (2) raw URL link for sharing/downloading
- Format: `media=audio_url` + `caption="...🔗 原始链接：{audio_url}"`

---

### Step 4 — Failure Notification (Push via message tool)

When task status = `failed` or any API/network error, push a failure message with alternative suggestions:

**Agent implementation:**
```python
message(
    action="send",
    target=group_id,
    message="""❌ 音乐生成失败
• 原因：[natural_language_error_message]
• 建议改用：
  - [Alt Model 1]（[特点]，[N pts]）
  - [Alt Model 2]（[特点]，[N pts]）

需要我帮你用其他模型重试吗？"""
)
```

**⚠️ CRITICAL: Error Message Translation**

**NEVER show technical error messages to users.** Always translate API errors into natural language:

| Technical Error | ❌ Never Say | ✅ Say Instead (Chinese) | ✅ Say Instead (English) |
|----------------|-------------|------------------------|------------------------|
| `"Invalid product attribute"` / `"Insufficient points"` | Invalid product attribute | 生成参数配置异常，请稍后重试 | Configuration error, please try again later |
| `Error 6006` (credit mismatch) | Error 6006 | 积分计算异常，系统正在修复 | Points calculation error, system is fixing |
| `Error 6010` (attribute_id mismatch) | Attribute ID does not match | 模型参数不匹配，请尝试其他模型 | Model parameters incompatible, try another model |
| `error 400` (bad request) | error 400 / Bad request | 音乐参数设置有误，请调整描述后重试 | Music parameter error, adjust description and retry |
| `resource_status == 2` | Resource status 2 / Failed | 音乐生成遇到问题，建议换个模型试试 | Music generation failed, try another model |
| `status == "failed"` (no details) | Task failed | 这次生成没成功，要不换个模型试试？ | Generation unsuccessful, try a different model? |
| `timeout` | Task timed out / Timeout error | 音乐生成时间过长已超时，建议用更快的模型 | Music generation took too long, try a faster model |
| Network error / Connection refused | Connection refused / Network error | 网络连接不稳定，请检查网络后重试 | Network connection unstable, check network and retry |
| API key invalid | Invalid API key / 401 Unauthorized | API 密钥无效，请联系管理员 | API key invalid, contact administrator |
| Rate limit exceeded | 429 Too Many Requests / Rate limit | 请求过于频繁，请稍等片刻再试 | Too many requests, please wait a moment |
| Model unavailable | Model not available / 503 Service Unavailable | 当前模型暂时不可用，建议换个模型 | Model temporarily unavailable, try another model |
| Lyrics format error (Suno only) | Invalid lyrics format | 歌词格式有误，请调整后重试 | Lyrics format error, adjust and retry |
| Prompt too short/long | Prompt length invalid | 音乐描述过短或过长，请调整到合适长度 | Music description too short or long, adjust length |

**Generic fallback (when error is unknown):**
- Chinese: `音乐生成遇到问题，请稍后重试或换个模型试试`
- English: `Music generation encountered an issue, please try again or use another model`

**Best Practices:**
1. **Focus on user action**: Tell users what to do next, not what went wrong technically
2. **Be reassuring**: Use phrases like "建议换个模型试试" instead of "生成失败了"
3. **Avoid blame**: Never say "你的描述有问题" → say "描述需要调整一下"
4. **Provide alternatives**: Always suggest 1-2 alternative models in the failure message
5. **Music-specific**: 
   - For Suno lyrics errors, suggest simplifying lyrics or using auto-generated lyrics
   - For prompt length errors, give example length (e.g., "建议20-100字")
   - For BGM requests, recommend DouBao BGM over Suno

**Failure fallback table:**

| Failed Model | First Alt | Second Alt |
|-------------|-----------|------------|
| Suno | DouBao BGM（30pts，背景音乐） | DouBao Song（30pts，歌曲生成） |
| DouBao BGM | DouBao Song（30pts） | Suno（25pts，功能最强） |
| DouBao Song | DouBao BGM（30pts） | Suno（25pts，功能最强） |

---

### Step 5 — Done (No Further Action Needed) 🆕

**v1.1 Note:** After completing Steps 0-4:
- ✅ **Step 0** already sent your normal reply (appears FIRST in chat)
- ✅ **Steps 1-4** pushed all updates via `message` tool (appear in order)
- ✅ **No further action needed** — conversation is complete

**Do NOT:**
- ❌ Reply again with `NO_REPLY` (you already replied in Step 0)
- ❌ Send duplicate confirmation messages
- ❌ Use `message` tool to send the same content twice

**Why this works:**
```
User: "帮我生成一段轻松的背景音乐"
  ↓
[Step 0] Your normal reply:  "好的！马上帮你生成轻松的背景音乐 🎵"  ← Appears FIRST
  ↓
[Step 1] message tool push:  "🎵 开始生成音乐..."  ← Appears SECOND
  ↓
[Step 2] message tool push:  "⏳ 正在生成中… 45%"  ← (if task takes >15s)
  ↓
[Step 3] message tool push:  "✅ 音乐生成成功! [Audio File]"  ← Appears LAST
  ↓
[Step 5] Done. No further replies.
```

---

## Supported Models

### text_to_music (3 models)

| Name | model_id | version_id | Cost | Key form_config |
|------|----------|------------|------|-----------------|
| **Suno** | `sonic` | `sonic` | 25 pts | `model_version=sonic-v5` (latest), `custom_mode=true`, `make_instrumental`, `auto_lyrics`, `tags`, `negative_tags`, `vocal_gender`, `title` |
| DouBao BGM | `GenBGM` | `GenBGM` | 30 pts | — |
| DouBao Song | `GenSong` | `GenSong` | 30 pts | — |

**Model guidance:**
- **Suno**: Most powerful option. Supports full custom mode with genre tags, explicit instrumental toggle, vocal gender selection, and negative tags to exclude unwanted styles.
- **DouBao BGM**: Lightweight background music generation. Ideal for ambient / background tracks.
- **DouBao Song**: Song generation. Good for structured vocal compositions.

**What you can generate:**
- Background music (lo-fi, ambient, cinematic, electronic, jazz, classical…)
- Custom jingles or theme songs with specific BPM and key
- Vocal or instrumental tracks with mood direction
- Short loops or full-length compositions

**Prompt writing tips (for Suno `gpt_description_prompt`):**
- Genre: `"lo-fi hip hop"`, `"orchestral cinematic"`, `"upbeat pop"`, `"dark ambient"`
- Tempo: `"80 BPM"`, `"fast tempo"`, `"slow ballad"`
- Vocals: `"no vocals"` → set `make_instrumental=true`; `"female vocals"` → `vocal_gender="female"`
- Mood: `"happy and energetic"`, `"melancholic"`, `"tense and dramatic"`
- Negative: `negative_tags="heavy metal, distortion"` to exclude styles
- Duration hint: `"60 seconds"`, `"30 second loop"`

## Environment

Base URL: `https://api.imastudio.com`

Required/recommended headers for all `/open/v1/` endpoints:

| Header | Required | Value | Notes |
|--------|----------|-------|-------|
| `Authorization` | ✅ | `Bearer ima_your_api_key_here` | API key authentication |
| `x-app-source` | ✅ | `ima_skills` | Fixed value — identifies skill-originated requests |
| `x_app_language` | recommended | `en` / `zh` | Product label language; defaults to `en` if omitted |

```
Authorization: Bearer ima_your_api_key_here
x-app-source: ima_skills
x_app_language: en
```

---

## ⚠️ MANDATORY: Always Query Product List First

> **CRITICAL**: You MUST call `/open/v1/product/list` BEFORE creating any task.  
> The `attribute_id` field is REQUIRED in the create request. If it is `0` or missing, you get:  
> `"Invalid product attribute"` → `"Insufficient points"` → task fails completely.  
> **NEVER construct a create request from the model table alone. Always fetch the product first.**

### How to get attribute_id

```python
# Step 1: Query product list
GET /open/v1/product/list?app=ima&platform=web&category=text_to_music

# Step 2: Walk the tree to find your model
for group in response["data"]:
    for version in group.get("children", []):
        if version["type"] == "3" and version["model_id"] == target_model_id:
            attribute_id  = version["credit_rules"][0]["attribute_id"]
            credit        = version["credit_rules"][0]["points"]
            model_version = version["id"]
            model_name    = version["name"]
```

### Quick Reference: Known attribute_ids

⚠️ **Production warning**: `attribute_id` and `credit` values change frequently. Always call `/open/v1/product/list` at runtime; table below is pre-queried reference (2026-02-27).

| Model | model_id | attribute_id | credit | Notes |
|-------|----------|-------------|--------|-------|
| Suno (sonic-v4) | `sonic` | **2370** | 25 pts | Default |
| DouBao BGM | `GenBGM` | **4399** | 30 pts | BGM专用 |
| DouBao Song | `GenSong` | **4398** | 30 pts | 歌曲专用 |
| All others | — | → query `/open/v1/product/list` | — | Always runtime query |

### Common Mistakes (and resulting errors)

| Mistake | Error |
|---------|-------|
| `attribute_id` is 0 or missing | `"Invalid product attribute"` → Insufficient points |
| `attribute_id` outdated (production changed) | Same errors; always query product list first |
| `prompt` at outer level | Prompt ignored |
| `cast` missing from inner `parameters` | Billing failure |
| Suno: `model_version` in `parameters` not set to `sonic-v5` | Wrong engine used |

---

## Core Flow

```
1. GET /open/v1/product/list?app=ima&platform=web&category=text_to_music
   → REQUIRED: Get attribute_id, credit, model_version, form_config defaults

2. POST /open/v1/tasks/create
   → Must include: attribute_id, model_name, model_version, credit, cast, prompt (nested!)

3. POST /open/v1/tasks/detail  {task_id: "..."}
   → Poll every 3–5s until medias[].resource_status == 1
   → Extract url from completed media (mp3)
```

---

## Supported Task Types

| category | Capability | Input |
|----------|------------|-------|
| `text_to_music` | Text → Music | prompt |

---

## Detail API status values

| Field | Type | Values |
|-------|------|--------|
| **`resource_status`** | int or `null` | `0`=处理中, `1`=可用, `2`=失败, `3`=已删除；`null` 当作 0 |
| **`status`** | string | `"pending"`, `"processing"`, `"success"`, `"failed"` |

| `resource_status` | `status` | Action |
|-------------------|----------|--------|
| `0` or `null` | `pending` / `processing` | Keep polling |
| `1` | `success` (or `completed`) | Stop when **all** medias are 1; read `url` |
| `1` | `failed` | Stop, handle error |
| `2` / `3` | any | Stop, handle error |

> **Important**: Treat `resource_status: null` as 0. Stop only when **all** medias have `resource_status == 1`. Check `status != "failed"` when rs=1.

---

## API 1: Product List

```
GET /open/v1/product/list?app=ima&platform=web&category=text_to_music
```

Returns a **V2 tree structure**: `type=2` nodes are model groups, `type=3` nodes are versions (leaves). Only `type=3` nodes contain `credit_rules` and `form_config`.

**How to pick a version:**
1. Traverse nodes to find `type=3` leaves
2. Use `model_id` and `id` (= `model_version`) from the leaf
3. Pick `credit_rules[].attribute_id`
4. Use `form_config[].value` as default `parameters` values

---

## API 2: Create Task

```
POST /open/v1/tasks/create
```

### text_to_music

No image input. `src_img_url: []`, `input_images: []`.

```json
{
  "task_type": "text_to_music",
  "enable_multi_model": false,
  "src_img_url": [],
  "parameters": [{
    "attribute_id":  "<from credit_rules>",
    "model_id":      "<model_id>",
    "model_name":    "<model_name>",
    "model_version": "<version_id>",
    "app":           "ima",
    "platform":      "web",
    "category":      "text_to_music",
    "credit":        "<points>",
    "parameters": {
      "prompt":       "upbeat electronic, 120 BPM, no vocals",
      "n":            1,
      "input_images": [],
      "cast":         {"points": "<points>", "attribute_id": "<attribute_id>"}
    }
  }]
}
```

**Prompt tips for music generation:**
- Genre: `"upbeat electronic"`, `"classical piano"`, `"ambient chill"`
- Tempo: `"120 BPM"`, `"slow tempo"`
- Vocals: `"no vocals"`, `"male vocals"`, `"female vocals"`
- Mood: `"happy"`, `"melancholic"`, `"energetic"`
- Duration hint: `"60 seconds"`, `"short loop"`

**Key fields**:

| Field | Required | Description |
|-------|----------|-------------|
| `parameters[].credit` | ✅ | Must equal `credit_rules[].points`. Error 6006 if wrong. |
| `parameters[].parameters.prompt` | ✅ | Prompt must be nested here, NOT at top level. |
| `parameters[].parameters.cast` | ✅ | `{"points": N, "attribute_id": N}` — mirror of credit. |
| `parameters[].parameters.n` | ✅ | Number of outputs (usually `1`). |

Response: `data.id` = task ID for polling.

---

## API 3: Task Detail (Poll)

```
POST /open/v1/tasks/detail
{"task_id": "<id from create response>"}
```

Poll every 3–5s. Completed response:

```json
{
  "id": "task_abc",
  "medias": [{
    "resource_status": 1,
    "url":          "https://cdn.../output.mp3",
    "duration_str": "60s",
    "format":       "mp3"
  }]
}
```

Output fields: `url` (mp3), `duration_str`, `format`.

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Placing `prompt` at param top-level | `prompt` must be inside `parameters[].parameters` |
| Wrong `credit` value | Must exactly match `credit_rules[].points` (error 6006) |
| Missing `app` / `platform` in parameters | Required — use `ima` / `web` |
| Single-poll instead of loop | Poll until `resource_status == 1` for ALL medias |
| Not checking `status != "failed"` | `resource_status=1` + `status="failed"` = actual failure |

---

## Python Example

```python
import time
import requests

BASE_URL = "https://api.imastudio.com"
API_KEY  = "ima_your_key_here"
HEADERS  = {
    "Authorization":  f"Bearer {API_KEY}",
    "Content-Type":   "application/json",
    "x-app-source":   "ima_skills",
    "x_app_language": "en",
}


def get_products(category: str) -> list:
    """Returns flat list of type=3 version nodes from V2 tree."""
    r = requests.get(
        f"{BASE_URL}/open/v1/product/list",
        headers=HEADERS,
        params={"app": "ima", "platform": "web", "category": category},
    )
    r.raise_for_status()
    nodes = r.json()["data"]
    versions = []
    for node in nodes:
        for child in node.get("children") or []:
            if child.get("type") == "3":
                versions.append(child)
            for gc in child.get("children") or []:
                if gc.get("type") == "3":
                    versions.append(gc)
    return versions


def create_music_task(prompt: str, product: dict) -> str:
    """Returns task_id."""
    rule = product["credit_rules"][0]
    form_defaults = {f["field"]: f["value"] for f in product.get("form_config", []) if f.get("value") is not None}

    nested_params = {
        "prompt": prompt,
        "n":      1,
        "input_images": [],
        "cast":   {"points": rule["points"], "attribute_id": rule["attribute_id"]},
        **form_defaults,
    }

    body = {
        "task_type":          "text_to_music",
        "enable_multi_model": False,
        "src_img_url":        [],
        "parameters": [{
            "attribute_id":  rule["attribute_id"],
            "model_id":      product["model_id"],
            "model_name":    product["name"],
            "model_version": product["id"],
            "app":           "ima",
            "platform":      "web",
            "category":      "text_to_music",
            "credit":        rule["points"],
            "parameters":    nested_params,
        }],
    }
    r = requests.post(f"{BASE_URL}/open/v1/tasks/create", headers=HEADERS, json=body)
    r.raise_for_status()
    return r.json()["data"]["id"]


def poll(task_id: str, interval: int = 3, timeout: int = 300) -> dict:
    deadline = time.time() + timeout
    while time.time() < deadline:
        r = requests.post(f"{BASE_URL}/open/v1/tasks/detail", headers=HEADERS, json={"task_id": task_id})
        r.raise_for_status()
        task   = r.json()["data"]
        medias = task.get("medias", [])
        if medias:
            if any(m.get("status") == "failed" for m in medias):
                raise RuntimeError(f"Task failed: {task_id}")
            rs = lambda m: m.get("resource_status") if m.get("resource_status") is not None else 0
            if any(rs(m) == 2 for m in medias):
                raise RuntimeError(f"Task failed: {task_id}")
            if all(rs(m) == 1 for m in medias):
                return task
        time.sleep(interval)
    raise TimeoutError(f"Task timed out: {task_id}")


# text_to_music
products = get_products("text_to_music")
task_id  = create_music_task("upbeat electronic, 120 BPM, no vocals", products[0])
result   = poll(task_id)
print(result["medias"][0]["url"])          # mp3 URL
print(result["medias"][0]["duration_str"]) # e.g. "60s"
```
