---
name: IMA Studio Video Generation
version: 1.0.2
category: file-generation
author: IMA Studio (imastudio.com)
keywords: imastudio, video generation, text to video
argument-hint: "[text prompt or image URL]"
description: >
  Use for AI video generation via IMA Open API. Supports 4 modes: text-to-video (14 models),
  image-to-video (14 models), first_last_frame_to_video (10 models), reference_image_to_video
  (9 models).
  IMPORTANT — Default model selection rule: always recommend the NEWEST and most POPULAR model,
  NOT the cheapest. Default text_to_video: Wan 2.6 (wan2.6-t2v, 25pts) — most popular, balanced cost.
  Alternative: Hailuo 2.3 (MiniMax-Hailuo-2.3, 38pts) for higher quality.
  Default image_to_video: Wan 2.6 (wan2.6-i2v, 25pts) — most popular for i2v.
  Default first_last_frame_to_video: Kling O1 (kling-video-o1, 48-120pts).
  Default reference_image_to_video: Kling O1 (kling-video-o1, 48-120pts).
  Production models (2026-02-27) — text_to_video (14): Wan 2.6, Hailuo 2.0/2.3, Vidu Q2,
  SeeDance 1.5 Pro, Sora 2 Pro, Kling O1/2.6, Google Veo 3.1, Pixverse V3.5-V5.5.
  image_to_video (14): Same as text_to_video except Vidu Q2 Pro. first_last_frame_to_video (10):
  Hailuo 2.0, Kling O1/2.6, Vidu Q2 Pro, Google Veo 3.1, Pixverse V3.5-V5.5.
  reference_image_to_video (9): Kling O1, Google Veo 3.1, Vidu Q2, Pixverse (all versions).
  Poll every 8s. Requires an ima_* API key.
---

# IMA Video AI Creation

## ⚙️ How This Skill Works

**For transparency:** This skill uses a bundled Python script (`scripts/ima_video_create.py`) to call the IMA Open API. The script:
- Sends your prompt to IMA's servers (two domains, see below)
- Uses `--user-id` **only locally** as a key for storing your model preferences
- Returns a video URL when generation is complete

### 🌐 Network Endpoints Used

This skill connects to **two domains** owned by IMA Studio for complete functionality:

| Domain | Purpose | What's Sent | Authentication |
|--------|---------|-------------|----------------|
| `api.imastudio.com` | Main API (task creation, status polling) | Prompts, model params, task IDs | Bearer token (IMA API key) |
| `imapi.liveme.com` | Image upload service (OSS token generation) | Image files (for i2v/ref tasks), IMA API key | IMA API key + APP_KEY signature |

**Why two domains?**
- `api.imastudio.com`: IMA's video generation API (handles task orchestration)
- `imapi.liveme.com`: IMA's media storage infrastructure (handles large file uploads)
- Both services are **owned and operated by IMA Studio**

**Privacy implications:**
- Your IMA API key is sent to **both domains** for authentication
- Image files are uploaded to `imapi.liveme.com` to obtain CDN URLs (for image_to_video, first_last_frame_to_video, reference_image_to_video tasks)
- Video generation happens on `api.imastudio.com` using the CDN URLs
- For text_to_video tasks (no image input), only `api.imastudio.com` is contacted

**Security verification:**
```bash
# List all network endpoints in the code:
grep -n "https://" scripts/ima_video_create.py

# Expected output:
# 57: DEFAULT_BASE_URL = "https://api.imastudio.com"
# 58: DEFAULT_IM_BASE_URL = "https://imapi.liveme.com"
```

**If you're concerned about the two-domain architecture:**
1. Review IMA Studio's privacy policy at https://imastudio.com/privacy
2. Contact IMA technical support to confirm domain ownership: support@imastudio.com
3. Use a test/scoped API key first (see security notice below)
4. Monitor network traffic during first run (instructions in SECURITY.md)

### ⚠️ Credential Security Notice

**Your IMA API key is sent to TWO domains:**
1. `api.imastudio.com` — Main video generation API
2. `imapi.liveme.com` — Image upload service (only when using image-to-video tasks)

**Both domains are owned by IMA Studio**, but if you're concerned about credential exposure:

✅ **Best practices:**
- Use a **test/scoped API key** for initial testing (create at https://imastudio.com/api-keys)
- Set a low quota (e.g., 100 credits) for the test key
- Rotate your key after testing if needed
- Monitor network traffic during first run (see SECURITY.md § "Network Traffic Verification")
- Contact IMA support to confirm domain ownership: support@imastudio.com

❌ **Do NOT:**
- Use a production key if you're uncomfortable with the two-domain architecture
- Share your API key with others
- Commit your API key to version control

**What gets sent to IMA servers:**
- ✅ Your video prompt/description
- ✅ Model selection (Wan/Hailuo/Kling/etc.)
- ✅ Video parameters (duration, resolution, etc.)
- ✅ Image files (for image-to-video tasks, uploaded to `imapi.liveme.com`)
- ✅ IMA API key (for authentication to both domains)
- ❌ NO user_id (it's only used locally)

**What's stored locally:**
- `~/.openclaw/memory/ima_prefs.json` - Your model preferences (< 1 KB)
- `~/.openclaw/logs/ima_skills/` - Generation logs (auto-deleted after 7 days)
- See [SECURITY.md](SECURITY.md) for complete privacy policy

### Agent Execution (Internal Reference)

> **Note for users:** You can review the script source at `scripts/ima_video_create.py` anytime.  
> The agent uses this script to simplify API calls. Network requests go to two IMA Studio domains: `api.imastudio.com` (API) and `imapi.liveme.com` (image uploads).

Use the bundled script internally to ensure correct parameter construction:

```bash
# Text to video
python3 {baseDir}/scripts/ima_video_create.py \
  --api-key  $IMA_API_KEY \
  --task-type text_to_video \
  --model-id  wan2.6-t2v \
  --prompt   "a puppy runs across a sunny meadow, cinematic" \
  --user-id  {user_id} \
  --output-json

# Image to video
python3 {baseDir}/scripts/ima_video_create.py \
  --api-key      $IMA_API_KEY \
  --task-type    image_to_video \
  --model-id     wan2.6-i2v \
  --prompt       "camera slowly zooms in" \
  --input-images https://example.com/photo.jpg \
  --user-id      {user_id} \
  --output-json

# First-last frame to video
python3 {baseDir}/scripts/ima_video_create.py \
  --api-key      $IMA_API_KEY \
  --task-type    first_last_frame_to_video \
  --model-id     kling-video-o1 \
  --prompt       "smooth transition" \
  --input-images https://example.com/first.jpg https://example.com/last.jpg \
  --user-id      {user_id} \
  --output-json
```

The script outputs JSON — parse it to get the result URL and pass it to the user via the UX protocol messages below.

**🚨 CRITICAL: How to send the video to user (Feishu/Discord/IM)**

```python
# ✅ CORRECT: Use the remote URL directly
video_url = json_output["url"]
message(
    action="send",
    media=video_url,  # Direct HTTPS URL → renders inline video player
    caption="✅ 视频生成成功！\n• 模型：[Model Name]\n• 耗时：[X]s\n• 消耗积分：[N pts]"
)

# ❌ WRONG: Download to local file first
# curl -o /tmp/video.mp4 {video_url}
# message(media="/tmp/video.mp4")  # Shows as file attachment (📎 path), NOT playable
```

**Why this matters:**
- ✅ Remote URL → Feishu renders inline video player with ▶ button
- ❌ Local file path → Feishu shows file attachment (📎 /tmp/...), not playable

**Always use the remote URL directly. Never download the video to local storage.**

---

## Overview


---

## 🛡️ Model-Specific Notes

### Sora 2 Pro — Content Safety Policy

**⚠️ Important**: Sora 2 Pro has **strict content safety policies** (OpenAI policy).

**Content Restrictions**:
- ❌ Cannot generate: people, celebrities, IP assets (e.g., Mickey Mouse)
- ❌ Strict prompt moderation
- ✅ Safe themes: landscapes, abstract patterns, animals, nature scenes

**Recommended Prompts**:
- ✅ "A sunset over mountains"
- ✅ "Abstract colorful flowing patterns"
- ✅ "A bird flying through clouds"

**Avoid**:
- ❌ "A person walking" (people)
- ❌ "Mickey Mouse dancing" (IP asset)
- ❌ Celebrity names or recognizable figures

If your prompt is rejected, try using more abstract or nature-focused descriptions.

---

Call IMA Open API to create AI-generated videos. All endpoints require an `ima_*` API key. The core flow is: **query products → create task → poll until done**.

---

## 🔒 Security & Transparency Policy

> **This skill is community-maintained and open for inspection.**

### ✅ What Users CAN Do

**Full transparency:**
- ✅ **Review all source code**: Check `scripts/ima_video_create.py` and `ima_logger.py` anytime
- ✅ **Verify network calls**: Network requests go to two IMA Studio domains: `api.imastudio.com` (API) and `imapi.liveme.com` (image uploads). See "🌐 Network Endpoints Used" section above for full details.
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

### 📋 Privacy & Data Handling Summary

**What this skill does with your data:**

| Data Type | Sent to IMA? | Stored Locally? | User Control |
|-----------|-------------|-----------------|--------------|
| Video prompts | ✅ Yes (required for generation) | ❌ No | None (required) |
| API key | ✅ Yes (authentication header) | ❌ No | Set via env var |
| user_id (optional CLI arg) | ❌ **Never** (local preference key only) | ✅ Yes (as prefs file key) | Change `--user-id` value |
| Model preferences | ❌ No | ✅ Yes (~/.openclaw) | Delete anytime |
| Generation logs | ❌ No | ✅ Yes (~/.openclaw) | Auto-cleanup 7 days |

**Privacy recommendations:**
1. **Use test/scoped API keys** for initial testing
2. **Note**: `--user-id` is **never sent to IMA servers** - it's only used locally as a key for storing preferences in `~/.openclaw/memory/ima_prefs.json`
3. **Review source code** at `scripts/ima_video_create.py` to verify network calls (search for `create_task` function)
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
sha256sum SKILL.md scripts/ima_video_create.py
```
# Verify skill integrity
sha256sum SKILL.md scripts/ima_video_create.py
```

If users report issues, verify file integrity first.

---

## 🧠 User Preference Memory

> User preferences **override** recommended defaults. If a user has generated before, use their preferred model — not the system default.

### Storage: `~/.openclaw/memory/ima_prefs.json`

```json
{
  "user_{user_id}": {
    "text_to_video":              { "model_id": "wan2.6-t2v",        "model_name": "Wan 2.6",          "credit": 25, "last_used": "..." },
    "image_to_video":             { "model_id": "wan2.6-i2v",        "model_name": "Wan 2.6",          "credit": 25, "last_used": "..." },
    "first_last_frame_to_video":  { "model_id": "kling-video-o1",    "model_name": "Kling O1",        "credit": 48, "last_used": "..." },
    "reference_image_to_video":   { "model_id": "kling-video-o1",    "model_name": "Kling O1",        "credit": 48, "last_used": "..." }
  }
}
```

If the file or key doesn't exist, fall back to the ⭐ Recommended Defaults below.

### When to Read (Before Every Generation)

1. Load `~/.openclaw/memory/ima_prefs.json` (silently, no error if missing)
2. Look up `user_{user_id}.{task_type}`
3. **If found** → use that model; mention it:
   ```
   🎬 根据你的使用习惯，将用 [Model Name] 帮你生成视频…
   • 模型：[Model Name]（你的常用模型）
   • 预计耗时：[X ~ Y 秒]
   • 消耗积分：[N pts]
   ```
4. **If not found** → use the ⭐ Recommended Default

### When to Write (After Every Successful Generation)

Save the used model to `~/.openclaw/memory/ima_prefs.json` under `user_{user_id}.{task_type}`.  
See `ima-image-ai/SKILL.md` → "User Preference Memory" for the full Python write snippet.

### When to Update (User Explicitly Changes Model)

| Trigger | Action |
|---------|--------|
| `用XXX` / `换成XXX` / `改用XXX` | Switch + save as new preference |
| `以后都用XXX` / `always use XXX` | Save + confirm: `✅ 已记住！以后视频生成默认用 [XXX]` |
| `换个模型` / `try another model` | Ask user to choose; save chosen model |
| `用最好的` / `best quality` | Use highest-quality model; save preference |
| `用便宜的` / `cheapest` | Use lowest-cost model; do NOT save unless user says "以后都用" |

---

## ⭐ Recommended Defaults

> **These are fallback defaults — only used when no user preference exists.**  
> **Always default to the newest and most popular model. Do NOT default to the cheapest.**

| Task | Default Model | model_id | version_id | Cost | Why |
|------|--------------|----------|------------|------|-----|
| text_to_video | **Wan 2.6** | `wan2.6-t2v` | `wan2.6-t2v` | 25 pts | 🔥 Most popular, balanced cost |
| text_to_video (premium) | **Hailuo 2.3** | `MiniMax-Hailuo-2.3` | `MiniMax-Hailuo-2.3` | 38 pts | Higher quality |
| text_to_video (budget) | **Vidu Q2** | `viduq2` | `viduq2` | 5 pts | Lowest cost t2v |
| image_to_video | **Wan 2.6** | `wan2.6-i2v` | `wan2.6-i2v` | 25 pts | 🔥 Most popular i2v, 1080P |
| image_to_video (premium) | **Kling 2.6** | `kling-v2-6` | `kling-v2-6` | 40-160 pts | Premium Kling i2v |
| first_last_frame_to_video | **Kling O1** | `kling-video-o1` | `kling-video-o1` | 48 pts | Newest Kling reasoning model |
| reference_image_to_video | **Kling O1** | `kling-video-o1` | `kling-video-o1` | 48 pts | Best reference fidelity |

**Selection guide (production credits, sorted by popularity):**
- **🔥 Most popular text-to-video** → **Wan 2.6** (25 pts, balanced cost & quality)
- Premium text-to-video → **Hailuo 2.3** (38 pts, higher quality)
- Budget text-to-video → **Vidu Q2** (5 pts) or **Hailuo 2.0** (12 pts)
- **🔥 Most popular image_to_video** → **Wan 2.6** (25 pts)
- first_last_frame / reference → **Kling O1** (48 pts)
- User specifies cheapest → **Vidu Q2** (5 pts) — only if explicitly requested

---

## 💬 User Experience Protocol (IM / Feishu / Discord)

> Video generation takes 1~6 minutes. **Never let users wait in silence.**  
> Always follow all 4 steps below, every single time.

### 🚫 Never Say to Users

| ❌ Never say | ✅ What users care about |
|-------------|--------------------------|
| `ima_video_create.py` / 脚本 / script | — |
| 自动化脚本 / automation | — |
| 自动处理产品列表 / 查询接口 | — |
| 自动解析参数 / 智能轮询 | — |
| attribute_id / model_version / form_config | — |
| API 调用 / HTTP 请求 / 任何技术参数名 | — |

Only tell users: **model name · estimated time · credits · result URL · plain-language status**.

---

### Estimated Generation Time per Model

| Model | Estimated Time | Poll Every | Send Progress Every |
|-------|---------------|------------|---------------------|
| Wan 2.6 (t2v / i2v) | 60~120s | 8s | 30s |
| Hailuo 2.0 | 60~120s | 8s | 30s |
| Hailuo 2.3 | 60~120s | 8s | 30s |
| Vidu Q1 / Q2 | 60~120s | 8s | 30s |
| Pixverse V3.5~V5.5 | 60~120s | 8s | 30s |
| Kling 1.6 | 60~120s | 8s | 30s |
| Kling 2.1 Master | 90~180s | 8s | 40s |
| SeeDance 1.0 / 1.5 Pro | 90~180s | 8s | 40s |
| Google Veo 3.1 Fast | 90~180s | 8s | 40s |
| Kling 2.5 Turbo | 120~240s | 8s | 45s |
| Sora 2 | 120~240s | 8s | 45s |
| Wan 2.5 | 90~180s | 8s | 40s |
| Kling 2.6 | 120~240s | 8s | 45s |
| Kling O1 | 180~360s | 8s | 60s |
| Sora 2 Pro | 180~360s | 8s | 60s |
| Google Veo 3.1 | 120~300s | 8s | 50s |
| Google Veo 3.0 | 180~360s | 8s | 60s |

`estimated_max_seconds` = upper bound of the range (e.g. 180 for Kling 2.1 Master, 360 for Kling O1).

---

### Step 1 — Pre-Generation Notification (with Cost Transparency)

**Before calling the create API**, send this message immediately:

```
🎬 开始生成视频，请稍候…
• 模型：[Model Name]
• 预计耗时：[X ~ Y 秒]（约 [X/60 ~ Y/60] 分钟）
• 消耗积分：[N pts]

视频生成需要一定时间，我会每隔一段时间汇报进度 🙏
```

**Cost transparency (critical for video):**
- For balanced/default models (25 pts): "使用 Wan 2.6（25 积分，最新 Wan）"
- For premium models (>50 pts):
  - If auto-selected: "使用 Wan 2.6（25 积分）。若需更高质量可选 Kling 2.1 Master（150 积分）"
  - If user explicit: "使用高端模型 Kling 2.1 Master（150 积分），质量最佳"
- For budget (user explicit): "使用 Vidu Q2（5 积分，最省钱选项）"

> Adapt language to match the user. For expensive models (>50 pts), always mention cheaper alternatives unless user explicitly requested premium quality.

> Adapt language to match the user. English → `🎬 Starting video generation, this may take [X~Y] seconds. I'll update you on progress…`

---

### Step 2 — Progress Updates

Poll the task detail API every **8s**.  
Send a progress update message every `[Send Progress Every]` seconds per the table above.

```
⏳ 视频生成中… [P]%
已等待 [elapsed]s，预计最长 [max]s
```

**Progress formula:**
```
P = min(95, floor(elapsed_seconds / estimated_max_seconds * 100))
```

- **Cap at 95%** — never show 100% until the API returns `success`
- If `elapsed > estimated_max`: keep P at 95% and append `「快了，稍等一下…」`
- Example: elapsed=120s, max=180s → P = min(95, floor(120/180*100)) = min(95, 66) = **66%**
- Example: elapsed=200s, max=180s → P = **95%**（冻结 + 「快了，稍等一下…」）

---

### Step 3 — Success Notification (Push video via message tool)

When task status = `success`:

**3.1 Send video player first** (Feishu will render inline player):
```python
# Get result URL from script output or task detail API
result = get_task_result(task_id)
video_url = result["medias"][0]["url"]

# Send video with caption
message(
    action="send",
    media=video_url,  # ⚠️ Use HTTPS URL directly, NOT local file path
    caption="""✅ 视频生成成功！
• 模型：[Model Name]
• 耗时：预计 [X~Y]s，实际 [actual]s
• 消耗积分：[N pts]

[视频描述]"""
)
```

**3.2 Then send link as text** (for copying/sharing):
```python
# Send link message immediately after
message(
    action="send",
    message=f"""🔗 视频链接（方便复制分享）：
{video_url}"""
)
```

**Critical:** 
- Use the **remote HTTPS URL** directly as `media` parameter. Do NOT download to local file first.
- Send video first (for inline playback), then send link text (for copying/sharing).

> For Feishu: Direct video URL → inline video player with play button. Local file path → file attachment (📎 path).

---

### Step 4 — Failure Notification

When task status = `failed` or any API/network error, send:

```
❌ 视频生成失败
• 原因：[natural_language_error_message]
• 建议改用：
  - [Alt Model 1]（[特点]，[N pts]）
  - [Alt Model 2]（[特点]，[N pts]）

需要我帮你用其他模型重试吗？
```

**⚠️ CRITICAL: Error Message Translation**

**NEVER show technical error messages to users.** Always translate API errors into natural language:

| Technical Error | ❌ Never Say | ✅ Say Instead (Chinese) | ✅ Say Instead (English) |
|----------------|-------------|------------------------|------------------------|
| `"Invalid product attribute"` / `"Insufficient points"` | Invalid product attribute | 生成参数配置异常，请稍后重试 | Configuration error, please try again later |
| `Error 6006` (credit mismatch) | Error 6006 | 积分计算异常，系统正在修复 | Points calculation error, system is fixing |
| `Error 6010` (attribute_id mismatch) | Attribute ID does not match | 模型参数不匹配，请尝试其他模型 | Model parameters incompatible, try another model |
| `error 400` (bad request) | error 400 / Bad request | 视频参数设置有误，请调整时长或分辨率 | Video parameter error, adjust duration or resolution |
| `resource_status == 2` | Resource status 2 / Failed | 视频生成遇到问题，建议换个模型试试 | Video generation failed, try another model |
| `status == "failed"` (no details) | Task failed | 这次生成没成功，要不换个模型试试？ | Generation unsuccessful, try a different model? |
| `timeout` | Task timed out / Timeout error | 视频生成时间过长已超时，建议用更快的模型 | Video generation took too long, try a faster model |
| Network error / Connection refused | Connection refused / Network error | 网络连接不稳定，请检查网络后重试 | Network connection unstable, check network and retry |
| API key invalid | Invalid API key / 401 Unauthorized | API 密钥无效，请联系管理员 | API key invalid, contact administrator |
| Rate limit exceeded | 429 Too Many Requests / Rate limit | 请求过于频繁，请稍等片刻再试 | Too many requests, please wait a moment |
| Prompt moderation (Sora 2 Pro only) | Content policy violation | 提示词包含敏感内容（如人物），Sora 不支持，请换其他模型 | Prompt contains restricted content (e.g. people), Sora doesn't support it, try another model |
| Model unavailable | Model not available / 503 Service Unavailable | 当前模型暂时不可用，建议换个模型 | Model temporarily unavailable, try another model |
| Image upload failed (image_to_video only) | Image upload error | 输入图片处理失败，请检查图片格式或换张图 | Input image processing failed, check format or try another image |
| Duration/resolution not supported | Parameter not supported | 该模型不支持此时长或分辨率，请调整参数 | Model doesn't support this duration or resolution, adjust parameters |

**Generic fallback (when error is unknown):**
- Chinese: `视频生成遇到问题，请稍后重试或换个模型试试`
- English: `Video generation encountered an issue, please try again or use another model`

**Best Practices:**
1. **Focus on user action**: Tell users what to do next, not what went wrong technically
2. **Be reassuring**: Use phrases like "建议换个模型试试" instead of "生成失败了"
3. **Avoid blame**: Never say "你的提示词有问题" → say "提示词需要调整一下"
4. **Provide alternatives**: Always suggest 1-2 alternative models in the failure message
5. **Video-specific**: 
   - For Sora content policy errors, recommend Wan 2.6 or Kling O1 (more permissive)
   - For timeout errors, recommend faster models (Vidu Q2, Hailuo 2.0)
   - For image input errors, suggest checking image format (HTTPS URL, valid JPEG/PNG)

**Failure fallback table:**

| Failed Model | First Alt | Second Alt |
|-------------|-----------|------------|
| Kling 2.1 Master | Wan 2.6（3pts，速度快） | Hailuo 2.0（5pts） |
| Google Veo 3.1 | Kling 2.1 Master（10pts） | Sora 2（42pts） |
| Kling O1 | Kling 2.1 Master（10pts） | Kling 2.5 Turbo（37pts） |
| Wan 2.6 | Hailuo 2.0（5pts） | Kling 1.6（10pts） |
| Sora 2 / Pro | Kling 2.1 Master（10pts） | Google Veo 3.1（162pts） |
| SeeDance | Kling 2.1 Master（10pts） | Wan 2.6（3pts） |
| Any / Unknown | Wan 2.6（3pts，最稳定） | Hailuo 2.0（5pts） |

---


## Supported Models

⚠️ **Production Environment**: Model availability validated against production API on 2026-02-27.

### text_to_video (14 models)

| Name | model_id | Cost Range | Resolution | Duration | Notes |
|------|----------|-----------|------------|----------|-------|
| **Wan 2.6** 🌟 | `wan2.6-t2v` | 25-120 pts | 720P/1080P | 5-15s | Balanced, most popular |
| **Hailuo 2.3** | `MiniMax-Hailuo-2.3` | 32+ pts | 768P | 6s | Latest Hailuo |
| Hailuo 2.0 | `MiniMax-Hailuo-02` | 5+ pts | 768P | 6s | Budget friendly |
| Vidu Q2 | `viduq2` | 5-70 pts | 540P-1080P | 5-10s | Fast generation |
| SeeDance 1.5 Pro | `doubao-seedance-1.5-pro` | 20+ pts | 720P | 4s | Latest SeeDance |
| Sora 2 Pro | `sora-2-pro` | 122+ pts | 720P+ | 4s+ | Premium OpenAI |
| **Kling O1** | `kling-video-o1` | 48-120 pts | — | 5-10s | Latest Kling, with audio |
| Kling 2.6 | `kling-v2-6` | 80+ pts | — | 5-10s | Previous Kling gen |
| **Google Veo 3.1** | `veo-3.1-generate-preview` | 70-330 pts | 720P-4K | 4-8s | SOTA cinematic |
| Pixverse V5.5 | `pixverse` | 30+ pts | 540P-1080P | 5-8s | Latest Pixverse |
| Pixverse V5 | `pixverse` | 25+ pts | 540P-1080P | 5-8s | — |
| Pixverse V4.5 | `pixverse` | 20+ pts | 540P-1080P | 5-8s | — |
| Pixverse V4 | `pixverse` | 12+ pts | 540P-1080P | 5-8s | — |
| Pixverse V3.5 | `pixverse` | 12+ pts | 540P-1080P | 5-8s | — |

### image_to_video (14 models)

| Name | model_id | Cost Range | Resolution | Duration | Notes |
|------|----------|-----------|------------|----------|-------|
| **Wan 2.6** 🔥 | `wan2.6-i2v` | 25-120 pts | 720P/1080P | 5-15s | Most popular i2v |
| **Hailuo 2.3** | `MiniMax-Hailuo-2.3` | 32+ pts | 768P | 6s | Latest Hailuo |
| Hailuo 2.0 | `MiniMax-Hailuo-02` | 25+ pts | 768P | 6s | — |
| Vidu Q2 Pro | `viduq2-pro` | 20-70 pts | 540P-1080P | 5-10s | Fast i2v |
| SeeDance 1.5 Pro | `doubao-seedance-1.5-pro` | 47+ pts | 720P | 4s | Latest SeeDance |
| Sora 2 Pro | `sora-2-pro` | 122+ pts | 720P+ | 4s+ | Premium OpenAI |
| **Kling O1** | `kling-video-o1` | 48-120 pts | — | 5-10s | Latest Kling, with audio |
| Kling 2.6 | `kling-v2-6` | 80+ pts | — | 5-10s | Previous Kling gen |
| **Google Veo 3.1** | `veo-3.1-generate-preview` | 70-330 pts | 720P-4K | 4-8s | SOTA cinematic |
| Pixverse V5.5 | `pixverse` | 24-48 pts | 540P-1080P | 5-8s | Latest Pixverse |
| Pixverse V5 | `pixverse` | 24-48 pts | 540P-1080P | 5-8s | — |
| Pixverse V4.5 | `pixverse` | 12-48 pts | 540P-1080P | 5-8s | — |
| Pixverse V4 | `pixverse` | 12-48 pts | 540P-1080P | 5-8s | — |
| Pixverse V3.5 | `pixverse` | 12-48 pts | 540P-1080P | 5-8s | — |

### first_last_frame_to_video (10 models)

| Name | model_id | Cost Range | Duration | Notes |
|------|----------|-----------|----------|-------|
| Hailuo 2.0 | `MiniMax-Hailuo-02` | 5+ pts | 6s | Budget option |
| Vidu Q2 Pro | `viduq2-pro` | 20-70 pts | 5-10s | Fast generation |
| **Kling O1** 🌟 | `kling-video-o1` | 48-120 pts | 5-10s | Recommended default |
| Kling 2.6 | `kling-v2-6` | 80+ pts | 5-10s | — |
| **Google Veo 3.1** | `veo-3.1-generate-preview` | 70-330 pts | 4-8s | SOTA quality |
| Pixverse V5.5 | `pixverse` | 24-48 pts | 5-8s | Latest Pixverse |
| Pixverse V5 | `pixverse` | 24-48 pts | 5-8s | — |
| Pixverse V4.5 | `pixverse` | 12-48 pts | 5-8s | — |
| Pixverse V4 | `pixverse` | 12-48 pts | 5-8s | — |
| Pixverse V3.5 | `pixverse` | 12-48 pts | 5-8s | — |

### reference_image_to_video (9 models)

| Name | model_id | Cost Range | Duration | Notes |
|------|----------|-----------|----------|-------|
| Vidu Q2 | `viduq2` | 10-70 pts | 5-10s | Fast, cost-effective |
| **Kling O1** 🌟 | `kling-video-o1` | 48-120 pts | 5-10s | Recommended, strong reference |
| **Google Veo 3.1** | `veo-3.1-generate-preview` | 70-330 pts | 4-8s | SOTA cinematic |
| Pixverse (generic) | `pixverse` | 12-48 pts | 5-8s | Pixverse base |
| Pixverse V5.5 | `pixverse` | 12-48 pts | 5-8s | Latest Pixverse |
| Pixverse V5 | `pixverse` | 12-48 pts | 5-8s | — |
| Pixverse V4.5 | `pixverse` | 12-48 pts | 5-8s | — |
| Pixverse V4 | `pixverse` | 12-48 pts | 5-8s | — |
| Pixverse V3.5 | `pixverse` | 12-48 pts | 5-8s | — |

**Production Notes (2026-02-27)**:
- ❌ **Removed models**: Vidu Q2 Turbo (viduq2-turbo), Wan 2.5, Kling 1.6/2.1/2.5, Sora 2 (non-Pro), Veo 3.0/3.1 Fast, SeeDance 1.0, Vidu Q1
- ✅ **Active models**: 14 t2v, 14 i2v, 10 first_last_frame, 9 reference_image
- 🔥 **Most popular**: Wan 2.6 (both t2v and i2v)
- 🌟 **Recommended defaults**: Wan 2.6 (balanced), Kling O1 (premium with audio)

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
# Step 1: Query product list for the target category
GET /open/v1/product/list?app=ima&platform=web&category=text_to_video
# (or image_to_video / first_last_frame_to_video / reference_image_to_video)

# Step 2: Walk the V2 tree to find your model (type=3 leaf nodes only)
for group in response["data"]:
    for version in group.get("children", []):
        if version["type"] == "3" and version["model_id"] == target_model_id:
            attribute_id  = version["credit_rules"][0]["attribute_id"]
            credit        = version["credit_rules"][0]["points"]
            model_version = version["id"]    # = version_id
            model_name    = version["name"]
            form_defaults = {f["field"]: f["value"] for f in version["form_config"]}
```

### Quick Reference: Known attribute_ids

⚠️ **Production warning**: `attribute_id` and `credit` values change frequently. Always call `/open/v1/product/list` at runtime; table below is pre-queried reference (2026-02-27).

| Model | Task | model_id | attribute_id | credit | Notes |
|-------|------|----------|-------------|--------|-------|
| Wan 2.6 (720P, 5s) | text_to_video | `wan2.6-t2v` | **2057** | 25 pts | Default, balanced |
| Wan 2.6 (1080P, 5s) | text_to_video | `wan2.6-t2v` | **2058** | 40 pts | — |
| Wan 2.6 (720P, 10s) | text_to_video | `wan2.6-t2v` | **2059** | 50 pts | — |
| Wan 2.6 (1080P, 10s) | text_to_video | `wan2.6-t2v` | **2060** | 80 pts | — |
| Wan 2.6 (720P, 15s) | text_to_video | `wan2.6-t2v` | **2061** | 75 pts | — |
| Wan 2.6 (1080P, 15s) | text_to_video | `wan2.6-t2v` | **2062** | 120 pts | — |
| Kling O1 (5s, std) | text_to_video | `kling-video-o1` | **2313** | 48 pts | Latest Kling |
| Kling O1 (5s, pro) | text_to_video | `kling-video-o1` | **2314** | 60 pts | — |
| Kling O1 (10s, std) | text_to_video | `kling-video-o1` | **2315** | 96 pts | — |
| Kling O1 (10s, pro) | text_to_video | `kling-video-o1` | **2316** | 120 pts | — |
| All others | any | — | → query `/open/v1/product/list` | — | Always runtime query |

### Common Mistakes (and resulting errors)

| Mistake | Error |
|---------|-------|
| `attribute_id` is 0 or missing | `"Invalid product attribute"` → Insufficient points |
| `attribute_id` outdated (production changed) | Same errors; always query product list first |
| **`attribute_id` doesn't match parameter combination** | **Error 6010: "Attribute ID does not match the calculated rule"** |
| `prompt` at outer level instead of `parameters.parameters.prompt` | Prompt ignored |
| `cast` missing from inner `parameters` | Billing validation failure |
| `credit` wrong / missing | Error 6006 |
| `model_name` or `model_version` missing | Wrong model routing |

**⚠️ Critical for Google Veo 3.1 and multi-rule models:**

Models like Google Veo 3.1 have **multiple `credit_rules`**, each with a different `attribute_id` for different parameter combinations:
- `720p + 4s + optimized` → attribute_id A
- `720p + 8s + optimized` → attribute_id B  
- `4K + 4s + high` → attribute_id C

The script automatically selects the correct `attribute_id` by matching your parameters (`duration`, `resolution`, `compression_quality`, `generate_audio`) against each rule's `attributes`. If the match fails, you get error 6010.

**Fix**: The bundled script now checks these video-specific parameters for smart credit_rule selection. Always use the script, not manual API construction.

---

## Core Flow

```
1. GET /open/v1/product/list?app=ima&platform=web&category=<type>
   → REQUIRED: Get attribute_id, credit, model_version, form_config defaults

[image_to_video / first_last_frame / reference_image tasks only]
2. Upload input image(s) → get public HTTPS URL(s)
   → See "Image Upload" section below

3. POST /open/v1/tasks/create
   → Must include: attribute_id, model_name, model_version, credit, cast, prompt (nested!)

4. POST /open/v1/tasks/detail  {task_id: "..."}
   → Poll every 8s until medias[].resource_status == 1
   → Extract url (mp4) and cover (thumbnail) from completed media
```

> Video generation is slower than image — poll every **8s** and set timeout to **600s**.

---

## Image Upload (Required for Video Tasks with Image Input)

**The IMA Open API does NOT accept raw bytes or base64 images. All input images must be public HTTPS URLs.**

For `image_to_video`, `first_last_frame_to_video`, `reference_image_to_video`: when a user provides an image (local file, base64, or non-public URL), upload it first to get a URL.

```python
def prepare_image_url(source) -> str:
    """Convert any image source to a public HTTPS URL.
    
    - If source is already a public HTTPS URL: return as-is
    - If source is a local file path or bytes: upload to hosting first
    """
    if isinstance(source, str) and source.startswith("https://"):
        return source  # already public, use directly

    # Option 1: IMA OSS (requires OSS credentials)
    #   objectName = f"aiagent/src/d/{date}/in/{uuid}.jpg"
    #   bucket.put_object(objectName, image_bytes)
    #   return f"https://ima.esxscloud.com/{objectName}"

    # Option 2: Any public image hosting (imgbb example)
    import base64, requests
    if isinstance(source, str):
        with open(source, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
    else:
        b64 = base64.b64encode(source).decode()
    r = requests.post("https://api.imgbb.com/1/upload",
                      data={"key": IMGBB_API_KEY, "image": b64})
    r.raise_for_status()
    return r.json()["data"]["url"]

# For first_last_frame: prepare both frames
first_url = prepare_image_url("/path/to/first.jpg")
last_url  = prepare_image_url("/path/to/last.jpg")
src_img_url = [first_url, last_url]  # index 0 = first, index 1 = last
```

> **Note**: URLs must be publicly accessible — not localhost, private network, or auth-gated endpoints.

---

## Supported Task Types

| category | Capability | Input |
|----------|------------|-------|
| `text_to_video` | Text → Video | prompt |
| `image_to_video` | Image → Video | prompt + upload_img_src |
| `first_last_frame_to_video` | First+Last Frame → Video | prompt + src_img_url[2] |
| `reference_image_to_video` | Reference Image → Video | prompt + src_img_url[1+] |

---

## Detail API status values

| Field | Type | Values |
|-------|------|--------|
| **`resource_status`** | int or `null` | `0`=处理中, `1`=可用, `2`=失败, `3`=已删除；`null` 当作 0 |
| **`status`** | string | `"pending"`, `"processing"`, `"success"`, `"failed"` |

| `resource_status` | `status` | Action |
|-------------------|----------|--------|
| `0` or `null` | `pending` / `processing` | Keep polling |
| `1` | `success` (or `completed`) | Stop when **all** medias are 1; read `url` / `cover` |
| `1` | `failed` | Stop, handle error |
| `2` / `3` | any | Stop, handle error |

> **Important**: Treat `resource_status: null` as 0. Stop only when **all** medias have `resource_status == 1`. Check `status != "failed"` when rs=1.

---

## API 1: Product List

```
GET /open/v1/product/list?app=ima&platform=web&category=text_to_video
```

Returns a **V2 tree structure**: `type=2` nodes are model groups, `type=3` nodes are versions (leaves). Only `type=3` nodes contain `credit_rules` and `form_config`.

**How to pick a version:**
1. Traverse nodes to find `type=3` leaves
2. Use `model_id` and `id` (= `model_version`) from the leaf
3. Pick `credit_rules[].attribute_id` matching desired quality
4. Use `form_config[].value` as default `parameters` values (duration, resolution, aspect_ratio, etc.)

---

## API 2: Create Task

```
POST /open/v1/tasks/create
```

### text_to_video — Verified ✅

No image input. `src_img_url: []`, `input_images: []`.

```json
{
  "task_type": "text_to_video",
  "enable_multi_model": false,
  "src_img_url": [],
  "parameters": [{
    "attribute_id":  4838,
    "model_id":      "wan2.6-t2v",
    "model_name":    "Wan 2.6",
    "model_version": "wan2.6-t2v",
    "app":           "ima",
    "platform":      "web",
    "category":      "text_to_video",
    "credit":        25,
    "parameters": {
      "prompt":          "a puppy dancing happily, sunny meadow",
      "negative_prompt": "",
      "prompt_extend":   false,
      "duration":        5,
      "resolution":      "1080P",
      "aspect_ratio":    "16:9",
      "shot_type":       "single",
      "seed":            -1,
      "n":               1,
      "input_images":    [],
      "cast":            {"points": 3, "attribute_id": 4838}
    }
  }]
}
```

> Video-specific fields from `form_config`: `duration` (seconds), `resolution`, `aspect_ratio`, `shot_type`, `negative_prompt`, `prompt_extend`.
> Response `medias[].cover` = first-frame thumbnail JPEG.

### image_to_video

Input image goes in top-level `src_img_url` and `parameters.input_images`:

```json
{
  "task_type": "image_to_video",
  "enable_multi_model": false,
  "src_img_url": ["https://example.com/scene.jpg"],
  "parameters": [{
    "attribute_id":  "<from credit_rules>",
    "model_id":      "<model_id>",
    "model_name":    "<model_name>",
    "model_version": "<version_id>",
    "app":           "ima",
    "platform":      "web",
    "category":      "image_to_video",
    "credit":        "<points>",
    "parameters": {
      "prompt":       "bring this landscape alive",
      "n":            1,
      "input_images": ["https://example.com/scene.jpg"],
      "cast":         {"points": "<points>", "attribute_id": "<attribute_id>"}
    }
  }]
}
```

### first_last_frame_to_video

Provide exactly 2 images: index 0 = first frame, index 1 = last frame:

```json
{
  "task_type": "first_last_frame_to_video",
  "src_img_url": ["https://example.com/first.jpg", "https://example.com/last.jpg"],
  "parameters": [{
    "category": "first_last_frame_to_video",
    "parameters": {
      "prompt": "smooth transition",
      "n": 1,
      "input_images": ["https://example.com/first.jpg", "https://example.com/last.jpg"],
      "cast": {"points": "<points>", "attribute_id": "<attribute_id>"}
    }
  }]
}
```

### reference_image_to_video

Provide 1 or more reference images in `src_img_url`:

```json
{
  "task_type": "reference_image_to_video",
  "src_img_url": ["https://example.com/ref.jpg"],
  "parameters": [{
    "category": "reference_image_to_video",
    "parameters": {
      "prompt": "dynamic video based on reference",
      "n": 1,
      "input_images": ["https://example.com/ref.jpg"],
      "cast": {"points": "<points>", "attribute_id": "<attribute_id>"}
    }
  }]
}
```

**Key fields**:

| Field | Required | Description |
|-------|----------|-------------|
| `parameters[].credit` | ✅ | Must equal `credit_rules[].points`. Error 6006 if wrong. |
| `parameters[].parameters.prompt` | ✅ | Prompt must be nested here, NOT at top level. |
| `parameters[].parameters.cast` | ✅ | `{"points": N, "attribute_id": N}` — mirror of credit. |
| `parameters[].parameters.n` | ✅ | Number of outputs (usually `1`). |
| top-level `src_img_url` | image tasks | Image URL(s); 2 images for first_last_frame. |
| `parameters[].parameters.input_images` | image tasks | Must mirror `src_img_url`. |
| `parameters[].parameters.duration` | text_to_video | Video duration in seconds (from form_config). |
| `parameters[].parameters.resolution` | text_to_video | e.g. `"1080P"` (from form_config). |
| `parameters[].parameters.aspect_ratio` | text_to_video | e.g. `"16:9"` (from form_config). |

Response: `data.id` = task ID for polling.

---

## API 3: Task Detail (Poll)

```
POST /open/v1/tasks/detail
{"task_id": "<id from create response>"}
```

Poll every **8s** for video tasks. Completed response:

```json
{
  "id": "task_abc",
  "medias": [{
    "resource_status": 1,
    "url":   "https://cdn.../output.mp4",
    "cover": "https://cdn.../cover.jpg",
    "duration_str": "5s",
    "format": "mp4"
  }]
}
```

Output fields: `url` (mp4), `cover` (first-frame thumbnail JPEG), `duration_str`, `format`.

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Polling too fast for video | Use 8s interval, not 2–3s |
| Missing `duration`/`resolution`/`aspect_ratio` | Read defaults from `form_config` |
| Wrong `credit` value | Must exactly match `credit_rules[].points` (error 6006) |
| `src_img_url` and `input_images` mismatch | Both must contain the same image URL(s) |
| Only 1 image for first_last_frame | Requires exactly 2 images (first + last) |
| Placing `prompt` at param top-level | `prompt` must be inside `parameters[].parameters` |

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


def create_video_task(task_type: str, prompt: str, product: dict, src_img_url: list = None, **extra) -> str:
    """Returns task_id. src_img_url: list of image URLs (1+ for image tasks, 2 for first_last_frame)."""
    src_img_url = src_img_url or []
    rule = product["credit_rules"][0]
    form_defaults = {f["field"]: f["value"] for f in product.get("form_config", []) if f.get("value") is not None}

    nested_params = {
        "prompt": prompt,
        "n":      1,
        "input_images": src_img_url,
        "cast":   {"points": rule["points"], "attribute_id": rule["attribute_id"]},
        **form_defaults,
    }
    nested_params.update({k: v for k, v in extra.items()
                          if k in ("duration", "resolution", "aspect_ratio", "shot_type",
                                   "negative_prompt", "prompt_extend", "seed")})

    body = {
        "task_type":          task_type,
        "enable_multi_model": False,
        "src_img_url":        src_img_url,
        "parameters": [{
            "attribute_id":  rule["attribute_id"],
            "model_id":      product["model_id"],
            "model_name":    product["name"],
            "model_version": product["id"],
            "app":           "ima",
            "platform":      "web",
            "category":      task_type,
            "credit":        rule["points"],
            "parameters":    nested_params,
        }],
    }
    r = requests.post(f"{BASE_URL}/open/v1/tasks/create", headers=HEADERS, json=body)
    r.raise_for_status()
    return r.json()["data"]["id"]


def poll(task_id: str, interval: int = 8, timeout: int = 600) -> dict:
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


# text_to_video (Verified: Wan 2.6, response includes cover thumbnail)
products = get_products("text_to_video")
wan26    = next(p for p in products if p["model_id"] == "wan2.6-t2v")
task_id  = create_video_task(
    "text_to_video", "a puppy dancing happily, sunny meadow", wan26,
    duration=5, resolution="1080P", aspect_ratio="16:9",
    shot_type="single", negative_prompt="", prompt_extend=False, seed=-1,
)
result = poll(task_id)
print(result["medias"][0]["url"])    # mp4 URL
print(result["medias"][0]["cover"])  # first-frame thumbnail JPEG

# image_to_video
products = get_products("image_to_video")
task_id  = create_video_task("image_to_video", "bring this landscape alive", products[0],
                             src_img_url=["https://example.com/scene.jpg"])
result   = poll(task_id)
print(result["medias"][0]["url"])

# first_last_frame_to_video (exactly 2 images required)
products = get_products("first_last_frame_to_video")
frames   = ["https://example.com/first.jpg", "https://example.com/last.jpg"]
task_id  = create_video_task("first_last_frame_to_video", "smooth transition", products[0],
                             src_img_url=frames)
result   = poll(task_id)
print(result["medias"][0]["url"])

# reference_image_to_video
products = get_products("reference_image_to_video")
task_id  = create_video_task("reference_image_to_video", "dynamic video", products[0],
                             src_img_url=["https://example.com/ref.jpg"])
result   = poll(task_id)
print(result["medias"][0]["url"])
```
