---
name: IMA Studio
version: 1.0.3
category: file-generation
author: IMA Studio (imastudio.com)
keywords: imastudio, ai creation, multimodal
argument-hint: "[text prompt, image URL, or music description]"
description: >
  Use for any IMA AI content generation: images, videos, and music via IMA Open API.
  IMPORTANT — Default model selection rule: always recommend the NEWEST and most POPULAR model,
  NOT the cheapest. Defaults: image → SeeDream 4.5 (doubao-seedream-4.5, 5pts);
  image budget → Nano Banana2 (gemini-3.1-flash-image, 4pts for 512px);
  video text_to_video → Wan 2.6 (wan2.6-t2v, 25pts) — most popular, balanced cost;
  video image_to_video → Wan 2.6 (wan2.6-i2v, 25pts);
  music → Suno sonic (25pts).
  Production models (2026-02-27) — Image text_to_image (3): SeeDream 4.5, Nano Banana2, Nano Banana Pro.
  Image image_to_image (3): SeeDream 4.5, Nano Banana2, Nano Banana Pro.
  Video text_to_video (14): Wan 2.6, Hailuo 2.0/2.3, Vidu Q2, SeeDance 1.5 Pro, Sora 2 Pro,
  Kling O1/2.6, Google Veo 3.1, Pixverse V3.5-V5.5.
  Video image_to_video (14): Wan 2.6, Hailuo 2.0/2.3, Vidu Q2 Pro, SeeDance 1.5 Pro, Sora 2 Pro,
  Kling O1/2.6, Google Veo 3.1, Pixverse V3.5-V5.5.
  Video first_last_frame_to_video (10): Hailuo 2.0, Vidu Q2 Pro, Kling O1/2.6,
  Google Veo 3.1, Pixverse V3.5-V5.5.
  Video reference_image_to_video (9): Vidu Q2, Kling O1, Google Veo 3.1, Pixverse (all versions).
  Music text_to_music (3): Suno sonic/sonic-v5, DouBao BGM, DouBao Song.
  Use this all-in-one skill when a task spans multiple media types; use the focused
  ima-image-ai / ima-video-ai / ima-voice-ai skills for single-media workflows.
  Requires an ima_* API key.
---

# IMA AI Creation

## ⚙️ How This Skill Works

**For transparency:** This skill uses a bundled Python script (`scripts/ima_create.py`) to call the IMA Open API. The script:
- Sends your prompt to **two IMA-owned domains** (see "Network Endpoints" below)
- Uses `--user-id` **only locally** as a key for storing your model preferences
- Returns image/video/music URLs when generation is complete

**What gets sent to IMA servers:**
- ✅ Your prompt/description (image/video/music)
- ✅ Model selection (SeeDream/Wan/Suno/etc.)
- ✅ Generation parameters (size, duration, style, etc.)
- ❌ NO API key in prompts (key is used for authentication only)
- ❌ NO user_id (it's only used locally)

**What's stored locally:**
- `~/.openclaw/memory/ima_prefs.json` - Your model preferences (< 1 KB)
- `~/.openclaw/logs/ima_skills/` - Generation logs (auto-deleted after 7 days)
- See [SECURITY.md](SECURITY.md) for complete privacy policy

---

## 🌐 Network Endpoints Used

| Domain | Owner | Purpose | Data Sent | Privacy |
|--------|-------|---------|-----------|---------|
| `api.imastudio.com` | IMA Studio | Main API (product list, task creation, task polling) | Prompts, model IDs, generation params, **your API key** | Standard HTTPS, data processed for AI generation |
| `imapi.liveme.com` | IMA Studio | Image/Video upload service (presigned URL generation) | **Your API key**, file metadata (MIME type, extension) | Standard HTTPS, used for image/video tasks only |
| `*.aliyuncs.com`, `*.esxscloud.com` | Alibaba Cloud (OSS) | Image/video storage (file upload, CDN delivery) | Raw image/video bytes (via presigned URL, **NO API key**) | IMA-managed OSS buckets, presigned URLs expire after 7 days |

**Key Points:**
- **Music tasks** (`text_to_music`) only use `api.imastudio.com`.
- **Image/video tasks** require `imapi.liveme.com` to obtain presigned URLs for uploading input images.
- Your API key is sent to **both `api.imastudio.com` and `imapi.liveme.com`** (both owned by IMA Studio).
- Verify network calls: `tcpdump -i any -n 'host api.imastudio.com or host imapi.liveme.com'` (see [SECURITY.md](SECURITY.md)).

---

## ⚠️ Credential Security Notice

**Your API key is sent to both IMA-owned domains:**
1. `Authorization: Bearer ima_xxx...` → `api.imastudio.com` (main API)
2. Query param `appUid=ima_xxx...` → `imapi.liveme.com` (upload service)

**Security best practices:**
- 🧪 **Use test keys for experiments:** Generate a separate API key for testing.
- 🔍 **Monitor usage:** Check `https://imastudio.com/dashboard` for unauthorized activity.
- ⏱️ **Rotate keys:** Regenerate your API key periodically (monthly recommended).
- 📊 **Review logs:** Check `~/.openclaw/logs/ima_skills/` for unexpected API calls.

**Why two domains?** IMA Studio uses a microservices architecture:
- **`api.imastudio.com`**: Core AI generation API
- **`imapi.liveme.com`**: Specialized image/video upload service (shared infrastructure)

Both domains are operated by IMA Studio. The same API key grants access to both services.

### Agent Execution (Internal Reference)

> **Note for users:** You can review the script source at `scripts/ima_create.py` anytime.  
> The agent uses this script to simplify API calls. **Music tasks** use only `api.imastudio.com`, while **image/video tasks** also call `imapi.liveme.com` for file uploads (see "Network Endpoints" above).

Use the bundled script internally for all task types — it ensures correct parameter construction:

```bash
# ─── Image Generation ──────────────────────────────────────────────────────────

# Basic text-to-image (default model)
python3 {baseDir}/scripts/ima_create.py \
  --api-key $IMA_API_KEY --task-type text_to_image \
  --model-id doubao-seedream-4.5 --prompt "a cute puppy on grass, photorealistic" \
  --user-id {user_id} --output-json

# Text-to-image with size override (Nano Banana2)
python3 {baseDir}/scripts/ima_create.py \
  --api-key $IMA_API_KEY --task-type text_to_image \
  --model-id gemini-3.1-flash-image --prompt "city skyline at sunset, 4K" \
  --size 2k --user-id {user_id} --output-json

# Image-to-image with input URL
python3 {baseDir}/scripts/ima_create.py \
  --api-key $IMA_API_KEY --task-type image_to_image \
  --model-id doubao-seedream-4.5 --prompt "turn into oil painting style" \
  --input-images https://example.com/photo.jpg --user-id {user_id} --output-json

# ─── Video Generation ──────────────────────────────────────────────────────────

# Basic text-to-video (default model, 5s 720P)
python3 {baseDir}/scripts/ima_create.py \
  --api-key $IMA_API_KEY --task-type text_to_video \
  --model-id wan2.6-t2v --prompt "a puppy dancing happily, cinematic" \
  --user-id {user_id} --output-json

# Text-to-video with extra params (10s 1080P)
python3 {baseDir}/scripts/ima_create.py \
  --api-key $IMA_API_KEY --task-type text_to_video \
  --model-id wan2.6-t2v --prompt "dramatic ocean waves, sunset" \
  --extra-params '{"duration":10,"resolution":"1080P","aspect_ratio":"16:9"}' \
  --user-id {user_id} --output-json

# Image-to-video (animate static image)
python3 {baseDir}/scripts/ima_create.py \
  --api-key $IMA_API_KEY --task-type image_to_video \
  --model-id wan2.6-i2v --prompt "camera slowly zooms in, gentle movement" \
  --input-images https://example.com/photo.jpg --user-id {user_id} --output-json

# First-last frame video (two images)
python3 {baseDir}/scripts/ima_create.py \
  --api-key $IMA_API_KEY --task-type first_last_frame_to_video \
  --model-id kling-video-o1 --prompt "smooth transition between frames" \
  --input-images https://example.com/frame1.jpg https://example.com/frame2.jpg \
  --user-id {user_id} --output-json

# ─── Music Generation ──────────────────────────────────────────────────────────

# Basic text-to-music (Suno default)
python3 {baseDir}/scripts/ima_create.py \
  --api-key $IMA_API_KEY --task-type text_to_music \
  --model-id sonic --prompt "upbeat electronic music, 120 BPM, no vocals" \
  --user-id {user_id} --output-json

# Music with custom lyrics (Suno custom mode)
python3 {baseDir}/scripts/ima_create.py \
  --api-key $IMA_API_KEY --task-type text_to_music \
  --model-id sonic --prompt "pop ballad, emotional" \
  --extra-params '{"custom_mode":true,"lyrics":"Your custom lyrics here...","vocal_gender":"female"}' \
  --user-id {user_id} --output-json

# Background music (DouBao BGM)
python3 {baseDir}/scripts/ima_create.py \
  --api-key $IMA_API_KEY --task-type text_to_music \
  --model-id GenBGM --prompt "relaxing ambient music for meditation" \
  --user-id {user_id} --output-json
```

The script outputs JSON with `url`, `model_name`, `credit` — use these values in the UX protocol messages below. The script internals (product list query, parameter construction, polling) are invisible to users.

---

## Overview

Call IMA Open API to create AI-generated content. All endpoints require an `ima_*` API key. The core flow is: **query products → create task → poll until done**.

---

## 🔒 Security & Transparency Policy

> **This skill is community-maintained and open for inspection.**

### ✅ What Users CAN Do

**Full transparency:**
- ✅ **Review all source code**: Check `scripts/ima_create.py` and `ima_logger.py` anytime
- ✅ **Verify network calls**: Music tasks use `api.imastudio.com` only; image/video tasks also use `imapi.liveme.com` (see "Network Endpoints" section)
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
| Prompts (image/video/music) | ✅ Yes (required for generation) | ❌ No | None (required) |
| API key | ✅ Yes (authentication header) | ❌ No | Set via env var |
| user_id (optional CLI arg) | ❌ **Never** (local preference key only) | ✅ Yes (as prefs file key) | Change `--user-id` value |
| Model preferences | ❌ No | ✅ Yes (~/.openclaw) | Delete anytime |
| Generation logs | ❌ No | ✅ Yes (~/.openclaw) | Auto-cleanup 7 days |

**Privacy recommendations:**
1. **Use test/scoped API keys** for initial testing
2. **Note**: `--user-id` is **never sent to IMA servers** - it's only used locally as a key for storing preferences in `~/.openclaw/memory/ima_prefs.json`
3. **Review source code** at `scripts/ima_create.py` to verify network calls (search for `create_task` function)
4. **Rotate API keys** after testing or if compromised

**Get your IMA API key:** Visit https://imastudio.com to register and get started.

### 🔧 For Skill Maintainers Only

**Version control:**
- All changes must go through Git with proper version bumps (semver)
- CHANGELOG.md must document all changes
- Production deployments require code review

如果你需要定制功能，请：
1. Fork 这个 Skill 创建私有版本（不保证兼容性）
2. 或者联系 IMA 技术支持申请企业定制
```

### 🔧 For Skill Maintainers Only

**Version control:**
- All changes must go through Git with proper version bumps (semver)
- CHANGELOG.md must document all changes
- Production deployments require code review

**File checksums (optional):**
```bash
# Verify skill integrity
sha256sum SKILL.md scripts/ima_create.py
```

If users report issues, verify file integrity first.

---

## 🧠 User Preference Memory

> User preferences **override** recommended defaults across ALL task types.  
> If a user has generated before, use their preferred model — not the system default.

### Storage: `~/.openclaw/memory/ima_prefs.json`

Single file, shared across all IMA skills:

```json
{
  "user_{user_id}": {
    "text_to_image":             { "model_id": "doubao-seedream-4.5", "model_name": "SeeDream 4.5",    "credit": 5,  "last_used": "2026-02-27T03:07:27Z" },
    "image_to_image":            { "model_id": "doubao-seedream-4.5", "model_name": "SeeDream 4.5",    "credit": 5,  "last_used": "2026-02-27T03:07:27Z" },
    "text_to_video":             { "model_id": "wan2.6-t2v",           "model_name": "Wan 2.6",         "credit": 25, "last_used": "2026-02-27T10:00:00Z" },
    "image_to_video":            { "model_id": "wan2.6-i2v",          "model_name": "Wan 2.6",         "credit": 25, "last_used": "2026-02-27T10:00:00Z" },
    "first_last_frame_to_video": { "model_id": "kling-video-o1",      "model_name": "Kling O1",        "credit": 48, "last_used": "2026-02-26T08:00:00Z" },
    "reference_image_to_video":  { "model_id": "kling-video-o1",      "model_name": "Kling O1",        "credit": 48, "last_used": "2026-02-26T08:00:00Z" },
    "text_to_music":             { "model_id": "sonic",               "model_name": "Suno",            "credit": 25, "last_used": "2026-02-26T06:00:00Z" }
  }
}
```

If the file or key doesn't exist, fall back to the ⭐ Recommended Defaults below.

---

### Model Selection Priority (Strict Order)

```
1. User explicitly specifies a model in this message
      → use it, save as new preference, confirm if different from old preference
2. User has a saved preference for this task type
      → use it, mention "根据你的使用习惯"
3. No preference exists
      → use ⭐ Recommended Default, save after success
```

---

### When to Read (Before Every Generation)

```python
import json, os

prefs_path = os.path.expanduser("~/.openclaw/memory/ima_prefs.json")
try:
    with open(prefs_path) as f:
        prefs = json.load(f)
    user_pref = prefs.get(f"user_{user_id}", {}).get(task_type)
except (FileNotFoundError, json.JSONDecodeError):
    user_pref = None

if user_pref:
    model_id   = user_pref["model_id"]
    model_name = user_pref["model_name"]
    credit     = user_pref["credit"]
    source     = "preference"   # pre-generation message: "根据你的使用习惯"
else:
    model_id, model_name, credit = RECOMMENDED_DEFAULTS[task_type]
    source = "default"
```

### When to Write (After Every Successful Generation)

```python
os.makedirs(os.path.dirname(prefs_path), exist_ok=True)
try:
    with open(prefs_path) as f:
        prefs = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    prefs = {}

from datetime import datetime, timezone
prefs.setdefault(f"user_{user_id}", {})[task_type] = {
    "model_id":   model_id,
    "model_name": model_name,
    "credit":     credit,
    "last_used":  datetime.now(timezone.utc).isoformat(),
}
with open(prefs_path, "w") as f:
    json.dump(prefs, f, ensure_ascii=False, indent=2)
```

### When to Update (User Explicitly Changes Model)

| User Says | Action |
|-----------|--------|
| `用XXX` / `换成XXX` / `改用XXX` / `use XXX` | Use that model this time AND save as new preference |
| `以后都用XXX` / `默认用XXX` / `always use XXX` | Save preference + confirm: `✅ 已记住！以后 [类型] 生成默认用 [XXX]` |
| `换个模型` / `try another model` | Show top 3 alternatives, let user pick; save chosen |
| `用最好的` / `best quality` | Use highest-quality model for this type; save preference |
| `用便宜的` / `cheapest` | Use lowest-cost model; only save if user adds "以后都用" |
| `清除我的偏好` / `reset preference` | Delete `user_{user_id}.{task_type}` from prefs file; confirm |

### Pre-Generation Notification (with preference)

When using a saved preference, mention it naturally:

```
🎨 根据你的使用习惯，将用 [Model Name] 帮你生成…
• 模型：[Model Name]（你的常用模型）
• 预计耗时：[X ~ Y 秒]
• 消耗积分：[N pts]
```

### Preference Change Confirmation

When user switches to a different model than their saved preference:

```
💡 你之前喜欢用 [Old Model]，这次换成了 [New Model]。
要把 [New Model] 设为以后的默认吗？
回复「是」保存 / 回复「否」仅本次使用
```

---

## ⭐ Recommended Defaults

> **These are fallback defaults — only used when no user preference exists.**  
> **Always default to the newest and most popular model. Do NOT default to the cheapest.**

| Task Type | Default Model | model_id | Cost | Why |
|-----------|--------------|----------|------|-----|
| text_to_image | **SeeDream 4.5** | `doubao-seedream-4.5` | 5 pts | Latest doubao flagship, photorealistic 4K |
| image_to_image | **SeeDream 4.5** | `doubao-seedream-4.5` | 5 pts | Latest, best i2i quality |
| text_to_video | **Wan 2.6** | `wan2.6-t2v` | 25 pts | 🔥 Most popular t2v, balanced cost. Premium → Hailuo 2.3 (38 pts) |
| image_to_video | **Wan 2.6** | `wan2.6-i2v` | 25 pts | 🔥 Most popular i2v, 1080P |
| first_last_frame_to_video | **Kling O1** | `kling-video-o1` | 48 pts | Newest Kling reasoning model |
| reference_image_to_video | **Kling O1** | `kling-video-o1` | 48 pts | Best reference fidelity |
| text_to_music | **Suno (sonic-v4)** | `sonic` | 25 pts | Latest Suno engine, best quality |

**Quick selection guide (production as of 2026-02-27, sorted by popularity):**
- **Image (3 models available)** → **SeeDream 4.5** (5, default); budget → Nano Banana2 (4, 512px); premium → Nano Banana Pro (10-18)
- **🔥 Video from text (most popular)** → **Wan 2.6** (25, balanced); premium → Hailuo 2.3 (38); budget → Vidu Q2 (5)
- **🔥 Video from image (most popular)** → **Wan 2.6** (25)
- Music → **Suno** (25); DouBao BGM/Song (30 each)
- Cheapest → Nano Banana2 512px (4) for image; Vidu Q2 (5) for video

**⚠️ Production Image Models (3 available):**
- SeeDream 4.5 (`doubao-seedream-4.5`) — 5 pts, default
- Nano Banana Pro (`gemini-3-pro-image`) — 10/10/18 pts for 1K/2K/4K

**All other image models mentioned in older documentation are no longer available in production.**

**🌟 Parameter Support Notes (All Task Types):**

### Image Models (text_to_image / image_to_image)
- ❌ **aspect_ratio**: NOT supported by any production image model (all produce 1:1 or fixed aspect ratio only)
- ✅ **size**: 
  - **Nano Banana2**: 512px, 1K, 2K, 4K (via different `attribute_id`s, 4-13 pts)
  - **Nano Banana Pro**: 1K, 2K, 4K (via different `attribute_id`s, 10-18 pts)
  - **SeeDream 4.5**: Adaptive default only (no size control, 5 pts)
- ❌ **8K**: No model supports 8K (max is 4K via Nano Banana Pro)
- ❌ **Custom aspect ratios** (7:3, 4:5, etc.): Not supported. Use video models as workaround.
- ✅ **n**: Multiple outputs supported (1-4), credit × n

### Video Models (text_to_video / image_to_video / first_last_frame / reference_image)
- ✅ **resolution**: 540P, 720P, 1080P, 2K, 4K (model-dependent, higher res = higher cost)
- ✅ **aspect_ratio**: 16:9, 9:16, 1:1, 4:3 (model-dependent, check `form_config`)
- ✅ **duration**: 4s, 5s, 10s, 15s (model-dependent, longer = higher cost)
- ⚠️ **generate_audio**: Supported by Veo 3.1, Kling O1, Hailuo (check `form_config`)
- ✅ **prompt_extend**: AI-powered prompt enhancement (most models support)
- ✅ **negative_prompt**: Content exclusion (most models support)
- ✅ **shot_type**: Single/multi-shot control (model-dependent)
- ✅ **seed**: Reproducibility control (most models support, -1 = random)
- ✅ **n**: Multiple outputs (1-4), credit × n

### Music Models (text_to_music)
- ✅ **custom_mode**: Suno only (enables vocal_gender, lyrics support)
- ✅ **vocal_gender**: Suno only (male/female/mixed, requires custom_mode=True)
- ✅ **lyrics**: Suno only (custom lyrics support, requires custom_mode=True)
- ❌ **duration**: Fixed-length output (DouBao ~30s, Suno ~2min, not user-controllable)
- ✅ **n**: Multiple outputs supported (1-2), credit × n

### Common Parameter Patterns
- **n (batch generation)**: Supported by ALL models. Cost = base_credit × n. Creates n independent resources.
- **seed**: Supported by most models (-1 = random, >0 = reproducible results)
- **prompt_extend**: AI-powered prompt enhancement (video models only)

### Decision Tree: When User Requests Unsupported Features

```
User asks for custom aspect ratio image (e.g. "7:3 landscape")
  → ❌ Image models don't support custom ratios
  → ✅ Solution: "图片模型不支持自定义比例。建议用视频模型(Wan 2.6 t2v)生成16:9视频，然后截取首帧作为图片。"

User asks for 8K image
  → ❌ No model supports 8K
  → ✅ Solution: "当前最高支持4K分辨率(Nano Banana Pro，18积分)。要使用吗？"

User asks for video with audio
  → Check model: Veo 3.1 / Kling O1 / Hailuo have generate_audio
  → ✅ Solution: "Veo 3.1 和 Kling O1 支持音频生成(需在参数中设置 generate_audio=True)。要用哪个？"

User asks for long music (e.g. "5 minute track")
  → ❌ Duration not user-controllable
  → ✅ Solution: "Suno 生成约2分钟音乐。需要更长时长可以生成多段后拼接。"

User asks for 30s video
  → Check model: Most models max 15s
  → ✅ Solution: "当前最长15秒。可选模型：Wan 2.6(15s, 75积分), Kling O1(10s, 96积分)。"
```

**When user requests unsupported combinations:**
- Any image model + custom aspect_ratio → "不支持自定义比例,建议用视频模型(Wan 2.6)生成后截取首帧"
- Any model + 8K → "最高支持4K (Nano Banana Pro, 18 pts)"
- Image model + 7:3 → "图片模型不支持,建议用 Wan 2.6 视频模型(支持16:9/9:16)生成后截帧"
- Video + audio (unsupported model) → "该模型不支持音频。建议用 Veo 3.1 或 Kling O1 (支持 generate_audio 参数)"
- Music + custom duration → "音乐时长由模型固定(Suno约2分钟,DouBao约30秒),无法自定义"


---

## 💬 User Experience Protocol (IM / Feishu / Discord)

> This skill runs inside IM platforms (Feishu, Discord via OpenClaw).  
> Generation takes 10 seconds (music) up to 6 minutes (video). **Never let users wait in silence.**  
> Always follow all 4 steps below, every single time.

### 🚫 Never Say to Users

The following are **internal implementation details**. Never mention them in any user-facing message, under any circumstances:

| ❌ Never say | ✅ What users care about |
|-------------|--------------------------|
| `ima_create.py` / 脚本 / script | — |
| 自动化脚本 / automation script | — |
| 自动处理产品列表查询 | — |
| 自动解析参数和配置 | — |
| 智能轮询 / polling / 轮询 | — |
| product list / 商品列表接口 | — |
| attribute_id / model_version / form_config | — |
| API 调用 / HTTP 请求 | — |
| 任何技术参数名 | 模型名称、积分、生成时间 |

User messages must only contain: **model name, estimated/actual time, credits consumed, result URL, and natural language status updates.**

---

### Estimated Generation Time (All Task Types)

| Task Type | Model | Estimated Time | Poll Every | Send Progress Every |
|-----------|-------|---------------|------------|---------------------|
| **text_to_image** | SeeDream 4.5 | 25~60s | 5s | 20s |
| | Nano Banana2 💚 | 20~40s | 5s | 15s |
| | Nano Banana Pro | 60~120s | 5s | 30s |
| **image_to_image** | SeeDream 4.5 | 25~60s | 5s | 20s |
| | Nano Banana2 💚 | 20~40s | 5s | 15s |
| | Nano Banana Pro | 60~120s | 5s | 30s |
| **text_to_video** | Wan 2.6, Hailuo 2.0/2.3, Vidu Q2, Pixverse | 60~120s | 8s | 30s |
| | SeeDance 1.5 Pro, Kling 2.6, Veo 3.1 | 90~180s | 8s | 40s |
| | Kling O1, Sora 2 Pro | 180~360s | 8s | 60s |
| **image_to_video** | Same ranges as text_to_video | — | 8s | 40s |
| **first_last_frame / reference** | Kling O1, Veo 3.1 | 180~360s | 8s | 60s |
| **text_to_music** | DouBao BGM / Song | 10~25s | 5s | 10s |
| | Suno (sonic-v5) | 20~45s | 5s | 15s |

`estimated_max_seconds` = upper bound of the range (e.g. 60 for SeeDream 4.5, 40 for Nano Banana2, 120 for Nano Banana Pro, 180 for Kling 2.6, 360 for Kling O1).

---

### Step 1 — Pre-Generation Notification

**Before calling the create API**, immediately send:

```
[Emoji] 开始生成 [内容类型]，请稍候…
• 模型：[Model Name]
• 预计耗时：[X ~ Y 秒]
• 消耗积分：[N pts]
```

**Emoji by content type:**
- 图片 → `🎨`  
- 视频 → `🎬`（加注:视频生成需要较长时间，我会定时汇报进度）  
- 音乐 → `🎵`

**Cost transparency (new requirement):**
- Always show credit cost with model tier context
- For expensive models (>50 pts), offer cheaper alternative proactively
- Examples:
  - Balanced (default): "使用 Wan 2.6（25 积分，最新 Wan）"
  - Premium (user explicit): "使用高端模型 Kling O1（48-120 积分），质量最佳"
  - Premium (auto-selected): "使用 Wan 2.6（25 积分）。若需更高质量可选 Kling O1（48 积分起）"
  - Budget (user asked): "使用 Vidu Q2（5 积分，最省钱）"

> Adapt language to match the user (Chinese / English). For video, always add a note that it takes longer. For expensive models, always mention cheaper alternatives unless user explicitly requested premium.

---

### Step 2 — Progress Updates

Poll the task detail API every `[Poll Every]` seconds per the table.  
Send a progress update every `[Send Progress Every]` seconds.

```
⏳ 正在生成中… [P]%
已等待 [elapsed]s，预计最长 [max]s
```

**Progress formula:**
```
P = min(95, floor(elapsed_seconds / estimated_max_seconds * 100))
```

- **Cap at 95%** — never reach 100% until the API confirms `success`
- If `elapsed > estimated_max`: freeze at 95%, append `「快了，稍等一下…」`
- For video with max=360s: at 120s → 33%, at 250s → 69%, at 400s → 95% (frozen)

---

### Step 3 — Success Notification

When task status = `success`, send:

```
✅ [内容类型]生成成功！
• 模型：[Model Name]
• 耗时：预计 [X~Y]s，实际 [actual]s
• 消耗积分：[N pts]

[结果链接]
```

---

### Step 4 — Failure Notification

When task status = `failed` or any API/network error, send:

```
❌ [内容类型]生成失败
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
| `error 400` (bad request) | error 400 / Bad request | 请求参数有误，请稍后重试 | Invalid request parameters, please try again |
| `resource_status == 2` | Resource status 2 / Failed | 生成过程遇到问题，建议换个模型试试 | Generation failed, please try another model |
| `status == "failed"` (no details) | Task failed | 这次生成没成功，要不换个模型试试？ | Generation unsuccessful, try a different model? |
| `timeout` | Task timed out / Timeout error | 生成时间过长已超时，建议用更快的模型 | Generation took too long, try a faster model |
| Network error / Connection refused | Connection refused / Network error | 网络连接不稳定，请检查网络后重试 | Network connection unstable, check network and retry |
| API key invalid | Invalid API key / 401 Unauthorized | API 密钥无效，请联系管理员 | API key invalid, contact administrator |
| Rate limit exceeded | 429 Too Many Requests / Rate limit | 请求过于频繁，请稍等片刻再试 | Too many requests, please wait a moment |
| Prompt moderation (Sora only) | Content policy violation | 提示词包含敏感内容，请修改后重试 | Prompt contains restricted content, please modify |
| Model unavailable | Model not available / 503 Service Unavailable | 当前模型暂时不可用，建议换个模型 | Model temporarily unavailable, try another model |

**Generic fallback (when error is unknown):**
- Chinese: `生成过程遇到问题，请稍后重试或换个模型试试`
- English: `Generation encountered an issue, please try again or use another model`

**Best Practices:**
1. **Focus on user action**: Tell users what to do next, not what went wrong technically
2. **Be reassuring**: Use phrases like "建议换个模型试试" instead of "失败了"
3. **Avoid blame**: Never say "你的提示词有问题" → say "提示词需要调整一下"
4. **Provide alternatives**: Always suggest 1-2 alternative models in the failure message

**Failure fallback by task type:**

| Task Type | Failed Model | First Alt | Second Alt |
|-----------|-------------|-----------|------------|
| text_to_image | SeeDream 4.5 | Nano Banana2 (4pts, fast) | Nano Banana Pro (10-18pts, premium) |
| text_to_image | Nano Banana2 | SeeDream 4.5 (5pts, better quality) | Nano Banana Pro (10-18pts) |
| text_to_image | Nano Banana Pro | SeeDream 4.5 (5pts) | Nano Banana2 (4pts, budget) |
| image_to_image | SeeDream 4.5 | Nano Banana2 (4pts, fast) | Nano Banana Pro (10pts) |
| image_to_image | Nano Banana2 | SeeDream 4.5 (5pts) | Nano Banana Pro (10pts) |
| image_to_image | Nano Banana Pro | SeeDream 4.5 (5pts) | Nano Banana2 (4pts) |
| text_to_video | Kling O1 | Wan 2.6 (25pts) | Vidu Q2 (5pts) |
| text_to_video | Google Veo 3.1 | Kling O1 (48pts) | Sora 2 Pro (122pts) |
| text_to_video | Any | Wan 2.6 (25pts, most popular) | Hailuo 2.0 (5pts) |
| image_to_video | Wan 2.6 | Kling O1 (48pts) | Hailuo 2.0 i2v (25pts) |
| image_to_video | Any | Wan 2.6 (25pts, most popular) | Vidu Q2 Pro (20pts) |
| first_last / reference | Kling O1 | Kling 2.6 (80pts) | Veo 3.1 (70pts+) |
| text_to_music | Suno | DouBao BGM (6pts) | DouBao Song (6pts) |
| text_to_music | DouBao | Suno (21pts) | DouBao BGM/Song (互换) |

---

## Supported Models at a Glance

> **Source: production `GET /open/v1/product/list` (2026-02-27).** Model count reduced significantly. Always query product list API at runtime.

### Image Generation (3 models each)

| Category | Name | model_id | Cost |
|----------|------|----------|------|
| **text_to_image** | SeeDream 4.5 🌟 | `doubao-seedream-4.5` | 5 pts |
| text_to_image | Nano Banana2 💚 | `gemini-3.1-flash-image` | 4/6/10/13 pts |
| text_to_image | Nano Banana Pro | `gemini-3-pro-image` | 10/10/18 pts |
| **image_to_image** | SeeDream 4.5 🌟 | `doubao-seedream-4.5` | 5 pts |
| image_to_image | Nano Banana2 💚 | `gemini-3.1-flash-image` | 4/6/10/13 pts |
| image_to_image | Nano Banana Pro | `gemini-3-pro-image` | 10 pts |

**Nano Banana2 size options**: 512px (4pts), 1K (6pts), 2K (10pts), 4K (13pts)  
**Nano Banana Pro size options**: 1K (10pts), 2K (10pts), 4K (18pts for t2i / 10pts for i2i)

❌ **Removed**: SeeDream 3.0/4.0, Nano Banana (gemini-2.5), GPT Image 1.0/1.5, Wan 2.6 t2i/i2i, Midjourney, Imagen 4, SeedEdit 3.0

### Video Generation

| Category | Name | model_id | Cost Range |
|----------|------|----------|-----------|
| **text_to_video (14)** | Wan 2.6 🔥 | `wan2.6-t2v` | 25-120 pts |
| | Hailuo 2.3 | `MiniMax-Hailuo-2.3` | 32+ pts |
| | Hailuo 2.0 | `MiniMax-Hailuo-02` | 5+ pts |
| | Vidu Q2 | `viduq2` | 5-70 pts |
| | SeeDance 1.5 Pro | `doubao-seedance-1.5-pro` | 20+ pts |
| | Sora 2 Pro | `sora-2-pro` | 122+ pts |
| | Kling O1 | `kling-video-o1` | 48-120 pts |
| | Kling 2.6 | `kling-v2-6` | 80+ pts |
| | Google Veo 3.1 | `veo-3.1-generate-preview` | 70-330 pts |
| | Pixverse V5.5 / V5 / V4.5 / V4 / V3.5 | `pixverse` | 12-48 pts |
| **image_to_video (14)** | Wan 2.6 🔥 | `wan2.6-i2v` | 25-120 pts |
| | Hailuo 2.3 / 2.0 | `MiniMax-Hailuo-2.3/02` | 25-32 pts |
| | Vidu Q2 Pro | `viduq2-pro` | 20-70 pts |
| | SeeDance 1.5 Pro | `doubao-seedance-1.5-pro` | 47+ pts |
| | Sora 2 Pro | `sora-2-pro` | 122+ pts |
| | Kling O1 / 2.6 | `kling-video-o1/v2-6` | 48-120 pts |
| | Google Veo 3.1 | `veo-3.1-generate-preview` | 70-330 pts |
| | Pixverse V5.5-V3.5 | `pixverse` | 12-48 pts |
| **first_last_frame (11)** | Kling O1 🌟 | `kling-video-o1` | 48-120 pts |
| | Kling 2.6 | `kling-v2-6` | 80+ pts |
| | Others (9) | Hailuo 2.0, Vidu Q2 Pro, SeeDance 1.5 Pro, Veo 3.1, Pixverse V5.5-V3.5 | — |
| **reference_image (6)** | Kling O1 🌟 | `kling-video-o1` | 48-120 pts |
| | Google Veo 3.1 | `veo-3.1-generate-preview` | 70-330 pts |
| | Others (4) | Vidu Q2, Pixverse V5.5/V5/V4.5 | — |

❌ **Removed video models**: Vidu Q2 Turbo (viduq2-turbo), Wan 2.5/2.2 Plus, Kling 1.6/2.1/2.5, Sora 2 (non-Pro), Veo 3.0/3.1 Fast, SeeDance 1.0, Vidu Q1, Hailuo 2.3 Fast
| text_to_video | SeeDance 1.5 Pro / 1.0 Pro | `doubao-seedance-1.5-pro` / `doubao-seedance-1.0-pro` | 16 / 15 pts |
| text_to_video | Sora 2 Pro / Sora 2 | `sora-2-pro` / `sora-2` | 120 / 35 pts |
| text_to_video | Kling O1 / 2.6 / 2.5 Turbo / 1.6 | `kling-video-o1` / `kling-v2-6` / `kling-v2-5-turbo` / `kling-v1-6` | 48 / 80 / 24 / 32 pts |
| text_to_video | Google Veo 3.1 Fast / 3.1 / 3.0 | `veo-3.1-fast-generate-preview` / `veo-3.1-generate-preview` / `veo-3.0-generate-preview` | 55 / 140 / 280 pts |
| text_to_video | Pixverse V3.5–V5.5 | `pixverse` | 12 pts |
| image_to_video | Wan 2.6 / 2.6 Flash / 2.5 / 2.2 Plus | `wan2.6-i2v` / `wan2.6-i2v-flash` / `wan2.5-i2v-preview` / `wan2.2-i2v-plus` | 25 / 12 / 12 / 10 pts |
| image_to_video | Kling 2.1 Master | `kling-v2-1-master` | 150 pts |
| first_last_frame_to_video | Kling O1 | `kling-video-o1` | 70 pts |
| reference_image_to_video | Kling O1 / Vidu Q2 / Q1 | `kling-video-o1` / `viduq2` / `viduq1` | 48 / 10 / 25 pts |

### Music Generation

| Category | Name | model_id | Cost | Notes |
|----------|------|----------|------|-------|
| text_to_music | Suno | `sonic` | 25 pts | sonic-v5; custom_mode, lyrics, vocal_gender |
| text_to_music | DouBao BGM | `GenBGM` | 30 pts | Background music |
| text_to_music | DouBao Song | `GenSong` | 30 pts | Song generation |

> Always call `GET /open/v1/product/list?category=<type>` first to get the live `attribute_id` and `form_config` defaults required for task creation.

There are two equivalent route systems serving the same backend logic:

| Route | Auth | Use Case |
|-------|------|----------|
| `/open/v1/` | `Authorization: Bearer ima_*` only | Third-party / agent access |
| `/api/v3/` | Token + API Key (dual auth) | Frontend App |

**This skill documents the `/open/v1/` Open API.** All business logic (credit validation, N-flattening, risk control) runs identically on both paths.

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

## 📤 When to Upload Images (Quick Reference)

**The IMA Open API does NOT accept raw bytes or base64 images. All image inputs must be public HTTPS URLs.**

| Task Type | Input Required? | Upload Before Create? | Notes |
|-----------|----------------|----------------------|-------|
| **text_to_image** | ❌ No | — | Prompt only |
| **image_to_image** | ✅ Yes (1 image) | ✅ Upload first | Single input image |
| **text_to_video** | ❌ No | — | Prompt only |
| **image_to_video** | ✅ Yes (1 image) | ✅ Upload first | Single input image |
| **first_last_frame_to_video** | ✅ Yes (2 images) | ✅ Upload first | First + last frame |
| **reference_image_to_video** | ✅ Yes (1+ images) | ✅ Upload first | Reference image(s) |
| **text_to_music** | ❌ No | — | Prompt only |

**Upload flow:**
1. User provides local file path or bytes → call `prepare_image_url()` (see section below)
2. User provides HTTPS URL → use directly, no upload needed
3. Use the returned CDN URL (`fdl`) as the value for `input_images` / `src_img_url`

**Example workflow (image_to_image):**
```python
# User provides local file
image_url = prepare_image_url("/path/to/photo.jpg", api_key)
# → Returns: https://ima-ga.esxscloud.com/webAgent/privite/2026/02/27/..._uuid.jpeg

# Then create task with this URL
create_task(
    task_type="image_to_image",
    input_images=[image_url],  # Use uploaded URL
    prompt="turn into oil painting"
)
```

---

## ⚠️ MANDATORY: Always Query Product List First

> **CRITICAL**: You MUST call `/open/v1/product/list` BEFORE creating any task.  
> The `attribute_id` field is REQUIRED in the create request. If it is `0` or missing, you get:  
> `"Invalid product attribute"` → `"Insufficient points"` → task fails completely.  
> **NEVER construct a create request from the model table alone. Always fetch the product first.**

### How to get attribute_id (all task types)

```python
# Query product list with the correct category
GET /open/v1/product/list?app=ima&platform=web&category=<task_type>
# task_type: text_to_image | image_to_image | text_to_video | image_to_video |
#            first_last_frame_to_video | reference_image_to_video | text_to_music

# Walk the V2 tree to find your target model (type=3 leaf nodes only)
for group in response["data"]:
    for version in group.get("children", []):
        if version["type"] == "3" and version["model_id"] == target_model_id:
            attribute_id  = version["credit_rules"][0]["attribute_id"]
            credit        = version["credit_rules"][0]["points"]
            model_version = version["id"]    # = version_id / model_version
            model_name    = version["name"]
            form_defaults = {f["field"]: f["value"] for f in version["form_config"]}
            break
```

### Quick Reference: Known attribute_ids

> Pre-queried values for convenience. **Always call the product list at runtime for accuracy.**

| Model | Task Type | model_id | attribute_id | credit | Notes |
|-------|-----------|----------|-------------|--------|-------|
| **text_to_image** |||||| |
| SeeDream 4.5 | text_to_image | `doubao-seedream-4.5` | **2341** | 5 pts | Default, balanced |
| Nano Banana Pro (1K) | text_to_image | `gemini-3-pro-image` | **2399** | 10 pts | 1024×1024 |
| Nano Banana Pro (2K) | text_to_image | `gemini-3-pro-image` | **2400** | 10 pts | 2048×2048 |
| Nano Banana Pro (4K) | text_to_image | `gemini-3-pro-image` | **2401** | 18 pts | 4096×4096 |
| **text_to_video** |||||| |
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
| **text_to_music** |||||| |
| Suno (sonic-v4) | text_to_music | `sonic` | **2370** | 25 pts | Default |
| DouBao BGM | text_to_music | `GenBGM` | **4399** | 30 pts | — |
| DouBao Song | text_to_music | `GenSong` | **4398** | 30 pts | — |
| **All others** | any | — | → query `/open/v1/product/list` | — | Always runtime query |

⚠️ **Production warning**: `attribute_id` and `credit` values change frequently in production. Always call `/open/v1/product/list` at runtime; above table is pre-queried reference only (2026-02-27).

### Common Mistakes (and resulting errors)

| Mistake | Error |
|---------|-------|
| `attribute_id` is `0` or missing | `"Invalid product attribute"` + `"Insufficient points"` |
| `attribute_id` outdated (production changed) | Same errors; always query product list first |
| **`attribute_id` doesn't match parameter combination** | **Error 6010: "Attribute ID does not match the calculated rule"** |
| `prompt` at outer `parameters[]` level | Prompt ignored; wrong routing |
| `cast` missing from inner `parameters.parameters` | Billing validation failure |
| `credit` value wrong or missing | Error 6006 |
| `model_name` / `model_version` missing | Wrong backend routing |
| Skipped product list, used table values directly | All of the above |

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
   → REQUIRED: Get attribute_id, credit, model_version, model_name, form_config defaults

[If input image required]
2. Upload image → get public HTTPS URL
   → See "Image Upload" section below

3. POST /open/v1/tasks/create
   → Must include: attribute_id, model_name, model_version, credit, cast, prompt (nested!)

4. POST /open/v1/tasks/detail  {"task_id": "..."}
   → Poll until medias[].resource_status == 1
   → Extract url from completed media
```

---

## Image Upload (Required Before Image Tasks)

**The IMA Open API does NOT accept raw bytes or base64 images. All image inputs must be public HTTPS URLs.**

When a user provides an image (local file, bytes, base64), you must upload it first and get a URL. This is exactly what the IMA frontend does before every image task.

### Real Upload Flow (from IMA Frontend Source)

The frontend uses a **two-step presigned URL flow** via the IM platform:

```
Step 1: GET /api/rest/oss/getuploadtoken   → returns { ful, fdl }
          ful = presigned PUT URL (upload destination, expires ~7 days)
          fdl = final CDN download URL (use this as input_images value)

Step 2: PUT {ful}  with raw image bytes + Content-Type header
          → image is stored in Aliyun OSS: zhubite-imagent-bot.oss-us-east-1.aliyuncs.com
          → accessible via CDN: https://ima-ga.esxscloud.com/...
```

### Step 1: Get Upload Token

```
GET https://imapi-qa.liveme.com/api/rest/oss/getuploadtoken
```

Required query parameters (11 total — sourced directly from frontend `generateUploadInfo`):

| Parameter | Example | Description |
|-----------|---------|-------------|
| `appUid` | `ima_xxx...` | **Use IMA API key directly** — no separate login needed |
| `appId` | `webAgent` | App identifier (fixed) |
| `appKey` | `32jdskjdk320eew` | App secret (fixed, used for `sign` generation) |
| `cmimToken` | `ima_xxx...` | **Use IMA API key directly** — same as appUid |
| `sign` | `117CF6CF...` | IM auth HMAC: `SHA1("webAgent\|32jdskjdk320eew\|{timestamp}\|{nonce}").upper()` |
| `timestamp` | `1772042430` | Unix timestamp (seconds), generated per request |
| `nonce` | `CxI1FLI5ajLJZ1jlxZmeg` | Random nonce string, generated per request |
| `fService` | `privite` | Fixed: storage service type |
| `fType` | `picture` | `picture` for images, `video`, `audio` |
| `fSuffix` | `jpeg` | File extension: `jpeg`, `png`, `mp4`, `mp3` |
| `fContentType` | `image/jpeg` | MIME type of the file |

> **简化认证**：直接使用 IMA API key 填充 `appUid` 和 `cmimToken` 参数，无需单独获取凭证。

Response:
```json
{
  "ful": "https://zhubite-imagent-bot.oss-us-east-1.aliyuncs.com/webAgent/privite/2026/02/26/..._uuid.jpeg?Expires=...&OSSAccessKeyId=...&Signature=...",
  "fdl": "https://ima-ga.esxscloud.com/webAgent/privite/2026/02/26/..._uuid.jpeg",
  "ful_expire": "...",
  "fdl_expire": "...",
  "fdl_key": "..."
}
```

### Step 2: Upload Image via Presigned URL

```
PUT {ful}
Content-Type: image/jpeg
Body: [raw image bytes]
```

No auth headers needed — the presigned URL already encodes the credentials.

### Step 3: Use `fdl` as the Image URL

After the PUT succeeds, use `fdl` (the CDN URL) as the value for `input_images` / `src_img_url`.

### Python Implementation

```python
import hashlib, time, uuid, requests, mimetypes

# ── 🌐 IMA Upload Service Endpoint (IMA-owned, for image/video uploads) ──────
IMA_IM_BASE = "https://imapi-qa.liveme.com"   # prod: https://imapi.liveme.com

# ── 🔑 Hardcoded APP_KEY (Public, Shared Across All Users) ──────────────────
# This APP_KEY is a PUBLIC identifier used by IMA Studio's image/video upload 
# service. It is NOT a secret—it's intentionally shared across all users and 
# embedded in the IMA web frontend. This key is used to generate HMAC signatures 
# for upload token requests, but your IMA API key (ima_xxx...) is the ACTUAL 
# authentication credential. Think of APP_KEY as a "client ID" rather than a 
# "client secret."
#
# ⚠️ Security Note: Your ima_xxx... API key is the sensitive credential. It is 
# sent to imapi.liveme.com as query parameters (appUid, cmimToken). Always use 
# test keys for experiments and rotate your API key regularly.
#
# 📖 See SECURITY.md for complete disclosure and network verification guide.
APP_ID    = "webAgent"
APP_KEY   = "32jdskjdk320eew"   # Public shared key (used for HMAC sign generation)
APP_UID   = "<your_app_uid>"    # POST /api/v3/login/app → data.user_id
APP_TOKEN = "<your_app_token>"  # POST /api/v3/login/app → data.token


def _gen_sign() -> tuple[str, str, str]:
    """Generate per-request (sign, timestamp, nonce)."""
    nonce = uuid.uuid4().hex[:21]
    ts    = str(int(time.time()))
    raw   = f"{APP_ID}|{APP_KEY}|{ts}|{nonce}"
    sign  = hashlib.sha1(raw.encode()).hexdigest().upper()
    return sign, ts, nonce


def get_upload_token(app_uid: str, app_token: str,
                     suffix: str, content_type: str) -> dict:
    """Step 1: Get presigned upload URL from IMA's upload service.
    
    Calls GET imapi.liveme.com/api/rest/oss/getuploadtoken with exactly 11 params.
    Returns: { "ful": "<presigned PUT URL>", "fdl": "<CDN download URL>" }
    
    Args:
        app_uid: Your IMA API key (ima_xxx...), used as appUid parameter
        app_token: Your IMA API key (ima_xxx...), used as cmimToken parameter
        suffix: File extension (jpeg, png, mp4, mp3)
        content_type: MIME type (image/jpeg, video/mp4, etc.)
    
    Security Note:
        Your IMA API key (ima_xxx...) is sent to imapi.liveme.com as query 
        parameters (appUid, cmimToken). This is IMA Studio's image/video upload 
        service, separate from the main api.imastudio.com API. Both domains are 
        owned by IMA Studio—this is part of IMA's microservices architecture.
        
        Why two domains?
        - api.imastudio.com: Core AI generation API (product list, task creation)
        - imapi.liveme.com: Specialized upload service (presigned URL generation)
        
        Your API key grants access to both services. For security verification, 
        see SECURITY.md section "Network Traffic Verification."
    """
    sign, ts, nonce = _gen_sign()
    r = requests.get(
        f"{IMA_IM_BASE}/api/rest/oss/getuploadtoken",
        params={
            # App Key params
            "appUid":       app_uid,       # APP_UID
            "appId":        APP_ID,
            "appKey":       APP_KEY,
            "cmimToken":    app_token,     # APP_TOKEN
            "sign":         sign,
            "timestamp":    ts,
            "nonce":        nonce,
            # File params
            "fService":     "privite",     # fixed
            "fType":        "picture",     # picture / video / audio
            "fSuffix":      suffix,        # jpeg / png / mp4 / mp3
            "fContentType": content_type,
        },
    )
    r.raise_for_status()
    return r.json()["data"]


def upload_image_to_oss(image_bytes: bytes, content_type: str, ful: str) -> None:
    """Step 2: PUT image bytes to the presigned OSS URL. No auth needed."""
    resp = requests.put(ful, data=image_bytes, headers={"Content-Type": content_type})
    resp.raise_for_status()


def prepare_image_url(source, api_key: str) -> str:
    """
    Full workflow: upload any image and return the CDN URL (fdl).
    
    Args:
        source: file path (str), raw bytes, or already-public HTTPS URL
        api_key: IMA API key for upload authentication
    
    Returns: public HTTPS CDN URL ready to use as input_images value
    """
    # Already a public URL → use directly, no upload needed
    if isinstance(source, str) and source.startswith("https://"):
        return source
    
    # Read file bytes
    if isinstance(source, str):
        ext = source.rsplit(".", 1)[-1].lower() if "." in source else "jpeg"
        with open(source, "rb") as f:
            image_bytes = f.read()
        content_type = mimetypes.guess_type(source)[0] or "image/jpeg"
    else:
        image_bytes = source
        ext = "jpeg"
        content_type = "image/jpeg"

    # Step 1: Get presigned URL using API key directly
    token_data = get_upload_token(api_key, ext, content_type)
    ful = token_data["ful"]
    fdl = token_data["fdl"]

    # Step 2: Upload to OSS
    upload_image_to_oss(image_bytes, content_type, ful)

    # Step 3: Return CDN URL
    return fdl   # use this as input_images / src_img_url value
```

> **OSS path format**: `webAgent/privite/{YYYY}/{MM}/{DD}/{timestamp}_{uid}_{uuid}.{ext}`
> **CDN base**: `https://ima-ga.esxscloud.com/`
> **OSS bucket**: `zhubite-imagent-bot.oss-us-east-1.aliyuncs.com`

---

## Quick Reference

### Task Types (category values)

| category | Capability | Input |
|----------|------------|-------|
| `text_to_image` | Text → Image | prompt |
| `image_to_image` | Image → Image | prompt + input_images |
| `text_to_video` | Text → Video | prompt |
| `image_to_video` | Image → Video | prompt + input_images |
| `first_last_frame_to_video` | First+Last Frame → Video | prompt + src_img_url[2] |
| `reference_image_to_video` | Reference Image → Video | prompt + src_img_url[1+] |
| `text_to_music` | Text → Music | prompt |

### Detail API status values

Each media in `medias[]` has two fields:

| Field | Type | Values | Description |
|-------|------|--------|-------------|
| **`resource_status`** | int (or `null`) | `0`, `1`, `2`, `3` | 0=处理中, 1=可用, 2=失败, 3=已删除。API 可能返回 `null`，需当作 0。 |
| **`status`** | string | `"pending"`, `"processing"`, `"success"`, `"failed"` | 任务状态文案。轮询时以 `resource_status` 为准；`status == "failed"` 表示失败。 |

Poll on `resource_status` first, then ensure `status` is not `"failed"`:

| `resource_status` | `status` | Meaning | Action |
|-------------------|----------|---------|--------|
| `0` or **`null`** | `pending` / `processing` | 处理中 | Keep polling; do not stop (null = 0) |
| `1` | `success` (or `completed`) | **完成** | Read `url`; stop only when **all** medias are 1 |
| `1` | `failed` | 失败 (status 优先) | Stop, handle error |
| `2` | any | 失败 | Stop, handle error |
| `3` | any | 已删除 | Stop |

> **Important**: (1) Treat `resource_status: null` as 0. (2) Stop only when **all** medias have `resource_status == 1`. (3) When `resource_status=1`, still check `status != "failed"`.

---

## API 1: Product List

```
GET /open/v1/product/list?app=ima&platform=web&category=text_to_image
```

Internally calls downstream `/v1/products/listv2`. Returns a **V2 tree structure**: `type=2` nodes are model groups, `type=3` nodes are versions (leaves). Only `type=3` nodes contain `credit_rules` and `form_config`.

> `webAgent` is auto-converted to `ima` by the gateway — you can use either value for `app`.

```json
[
  {
    "id": "SeeDream",
    "type": "2",
    "name": "SeeDream",
    "model_id": "",
    "children": [
      {
        "id": "doubao-seedream-4-0-250828",
        "type": "3",
        "name": "SeeDream 4.0",
        "model_id": "doubao-seedream-4.0",
        "credit_rules": [
          { "attribute_id": 332, "points": 5, "attributes": { "default": "enabled" } }
        ],
        "form_config": [
          { "field": "size", "type": "tags", "value": "1K",
            "options": [{"label":"1K","value":"1K"}, {"label":"2K","value":"2K"}] }
        ]
      }
    ]
  }
]
```

**How to pick a version for task creation:**
1. Traverse nodes to find `type=3` leaves (versions)
2. Use `model_id` and `id` (= `model_version`) from the leaf
3. Pick `credit_rules[].attribute_id` matching your desired quality/size (`attributes` field shows the config)
4. Use `form_config[].value` as default `parameters` values

> `credit_rules[].attribute_id` → required for task creation as `attribute_id`.
> `credit_rules[].points` → required for task creation as `credit` and `cast.points`.

---

## API 2: Create Task

```
POST /open/v1/tasks/create
```

### Request Structure

```json
{
  "task_type": "text_to_image",
  "enable_multi_model": false,
  "src_img_url": [],
  "upload_img_src": "",
  "parameters": [
    {
      "attribute_id": 8538,
      "model_id":      "doubao-seedream-4.5",
      "model_name":    "SeeDream 4.5",
      "model_version": "doubao-seedream-4-5-251128",
      "app":           "ima",
      "platform":      "web",
      "category":      "text_to_image",
      "credit":        5,
      "parameters": {
        "prompt":       "a beautiful mountain sunset, photorealistic",
        "size":         "4k",
        "n":            1,
        "input_images": [],
        "cast":         {"points": 5, "attribute_id": 8538}
      }
    }
  ]
}
```

### Field Reference

| Field | Required | Description |
|-------|----------|-------------|
| `task_type` | ✅ | Must match `parameters[].category` |
| `parameters[].attribute_id` | ✅ | From `credit_rules[].attribute_id` in product list |
| `parameters[].model_id` | ✅ | From `type=3` leaf node `model_id` |
| `parameters[].model_version` | ✅ | From `type=3` leaf node `id` |
| `parameters[].app` | ✅ | Use `ima` (or `webAgent`, auto-converted) |
| `parameters[].platform` | ✅ | Use `web` |
| `parameters[].category` | ✅ | Must match top-level `task_type` |
| `parameters[].credit` | ✅ | Must equal `credit_rules[].points`. Error 6006 if wrong. |
| `parameters[].parameters.prompt` | ✅ | The actual prompt text used by downstream service |
| `parameters[].parameters.cast` | ✅ | `{"points": N, "attribute_id": N}` — mirrors credit |
| `parameters[].parameters.n` | ✅ | Number of outputs (usually `1`). Gateway flattens N>1 into separate resources. |
| `parameters[].parameters.input_images` | image tasks | Array of input image URLs |
| top-level `src_img_url` | multi-image | Array for first_last_frame / reference tasks |

### N-Field Flattening (Gateway Internal Logic)

When `n > 1`, the gateway automatically:
1. Generates `n` independent `resourceBizId` values
2. Deducts credits `n` times (one per resource)
3. Creates `n` separate tasks in the downstream service

Response `medias[]` will contain `n` items. Poll until **all** have `resource_status == 1`.

### Response

```json
{
  "code": 0,
  "data": {
    "id": "task_abc123",
    "biz_id": "biz_xxx",
    "task_type": "text_to_image",
    "medias": [],
    "generate_count": 1,
    "created_at": 1700000000000,
    "timeout_at": 1700000300000
  }
}
```

`data.id` = task ID for polling. `timeout_at` = Unix ms deadline.

---

## API 3: Task Detail (Poll)

```
POST /open/v1/tasks/detail
{"task_id": "<id from create response>"}
```

Poll every 2–5s (8s+ for video). Completed response:

```json
{
  "id": "task_abc",
  "medias": [{
    "resource_status": 1,
    "status": "success",
    "url": "https://cdn.../output.jpg",
    "cover": "https://cdn.../cover.jpg",
    "format": "jpg",
    "width": 1024,
    "height": 1024
  }]
}
```

**Polling stop condition (must implement exactly):**
- Treat `resource_status: null` (or missing) as **0** (processing). Do **not** stop when you see null; backend may serialize Go `*int` as null.
- Stop **only when ALL** `medias[].resource_status == 1` and no `status == "failed"`. If you return on the first media with `resource_status == 1` while others are still 0, the task is not fully done and you will keep polling or get inconsistent state.
- Stop immediately if any `status == "failed"` or `resource_status == 2` or `resource_status == 3`.

---

## Task Type Examples

### text_to_image ✅ Verified
No image input. `src_img_url: []`, `input_images: []`. See API 2 for full example.

### text_to_video ✅ Verified
Extra fields vs text_to_image — all from `form_config` defaults:

```json
{
  "task_type": "text_to_video",
  "src_img_url": [],
  "parameters": [{
    "attribute_id":  4838,
    "model_id":      "wan2.6-t2v",
    "model_name":    "Wan 2.6",
    "model_version": "wan2.6-t2v",
    "category":      "text_to_video",
    "credit":        3,
    "app": "ima", "platform": "web",
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
> Poll every 8s (video generation is slower). Response `medias[].cover` = first-frame thumbnail.

### text_to_music
No image input. `src_img_url: []`, `input_images: []`.

### image_to_image ✅ Verified
```json
{
  "task_type": "image_to_image",
  "src_img_url": ["https://...input.jpg"],
  "parameters": [{
    "attribute_id":  8560,
    "model_id":      "doubao-seedream-4.5",
    "model_version": "doubao-seedream-4-5-251128",
    "category":      "image_to_image",
    "credit":        5,
    "app": "ima", "platform": "web",
    "parameters": {
      "prompt":       "turn into oil painting style",
      "size":         "4k",
      "n":            1,
      "input_images": ["https://...input.jpg"],
      "cast":         {"points": 5, "attribute_id": 8560}
    }
  }]
}
```
> ⚠️ `size` must be from `form_config` options (e.g. `"2k"`, `"4k"`, `"2048x2048"`). `"adaptive"` is NOT valid for SeeDream 4.5 i2i — causes error 400.
> Top-level `src_img_url` **and** `parameters.input_images` must both contain the input image URL.
> Some i2i models (e.g. `doubao-seededit-3.0-i2i`) may not be available in test environments — fall back to SeeDream 4.5.

### image_to_video / first_last_frame_to_video / reference_image_to_video
```json
"src_img_url": ["https://first-frame.jpg", "https://last-frame.jpg"]
```
Index 0 = first frame (or reference), index 1 = last frame (first_last_frame only).

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| `attribute_id` not from `credit_rules` | Always fetch product list first |
| `credit` value wrong | Must exactly match `credit_rules[].points` — error 6006 |
| `prompt` at wrong location | Put prompt in `parameters[].parameters.prompt` (nested), not only at top level |
| Polling `biz_id` instead of `id` | Use `id` (task ID) for `/tasks/detail` |
| Single-poll instead of loop | Poll until `resource_status == 1` for ALL medias |
| Missing `app` / `platform` in parameters | Required fields — use `ima` / `web` |
| `category` mismatch | `parameters[].category` must match top-level `task_type` |
| `resource_status == 2` not handled | Check for failure, don't loop forever |
| `status == "failed"` ignored | `resource_status=1` + `status="failed"` means actual failure |
| `n > 1` and only checking first media | All `n` media items must reach `resource_status == 1` |

---

## Complete Python Example

See [examples.md](examples.md) for a full Python implementation covering all 7 task types.
