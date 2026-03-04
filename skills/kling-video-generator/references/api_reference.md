# Kling 3.0 Omni Video API — Complete Parameter Reference

> Source: [KlingAI Series 3.0 Model API Specification](https://docs.qingque.cn/d/home/eZQDkLsWj1-DlmBV0EQIOm9vu)  
> Last updated: 2026-02-10

---

## Endpoint

```
POST https://api-singapore.klingai.com/v1/videos/omni-video
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

### Query Single Task
```
GET /v1/videos/omni-video/{task_id}
```

### Query Task List
```
GET /v1/videos/omni-video?pageNum=1&pageSize=30
```

---

## Authentication

JWT token generated from `access_key` + `secret_key`:

```python
import jwt, time

def generate_token(access_key: str, secret_key: str) -> str:
    payload = {
        "iss": access_key,
        "exp": int(time.time()) + 1800,  # 30 minutes
        "nbf": int(time.time()) - 5
    }
    return jwt.encode(payload, secret_key, algorithm="HS256")
```

---

## Request Body Parameters

### Core Parameters

| Field | Type | Required | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `model_name` | string | Optional | `kling-video-o1` | Model name. **Must explicitly pass `kling-v3-omni`** to use the 3.0 Omni model. Enum: `kling-video-o1`, `kling-v3-omni` |
| `prompt` | string | Conditional | None | Text prompt. Max 2500 chars. **Required when `multi_shot=false`**. Supports Omni template syntax (see below). |
| `aspect_ratio` | string | Conditional | None | Output aspect ratio. Enum: `16:9`, `9:16`, `1:1`. **Required when no first_frame image and not in video editing (base) mode.** Not supported in `base` editing mode or when first_frame image is provided. |
| `duration` | string | Optional | `"5"` | Video duration in seconds. Range: `"3"` to `"15"` (string). **Capped at `"10"` when `video_list` is provided.** **Ignored in `base` editing mode** (output duration = input video duration). |
| `mode` | string | Optional | `"pro"` | Quality mode. Enum: `std` (720P), `pro` (high quality). |
| `sound` | string | Optional | `"off"` | Native audio generation. Enum: `on`, `off`. **Automatically overridden to `"off"` when `video_list` is provided** (mutual exclusion rule). |

### Multi-Shot Parameters

| Field | Type | Required | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `multi_shot` | boolean | Optional | `false` | Enable multi-shot video generation. When `true`: `prompt` parameter is **invalid**. When `false`: `shot_type` and `multi_prompt` are **invalid**. |
| `shot_type` | string | Conditional | None | Storyboard method. Enum: `customize`. **Required when `multi_shot=true`**. Note: `intelligence` is only supported on legacy `/v1/videos/text2video` endpoint, NOT on `/v1/videos/omni-video`. |
| `multi_prompt` | array | Conditional | None | Per-shot storyboard details. **Required when `multi_shot=true` and `shot_type=customize`**. See structure below. |

#### `multi_prompt` Structure

```json
"multi_prompt": [
  {
    "index": 1,          // int, starts from 1, must be consecutive
    "prompt": "string",  // max 512 chars per shot
    "duration": "5"      // string, min 1s per shot
  },
  {
    "index": 2,
    "prompt": "string",
    "duration": "5"
  }
]
```

**Constraints:**
- Supports 1 to 6 shots maximum
- Each shot `duration` must be ≥ 1 second
- Sum of all shot `duration` values **must equal** the total `duration` of the task
- `index` must start from 1 and be consecutive (1, 2, 3...)

### Image Input Parameters

| Field | Type | Required | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `image_list` | array | Optional | None | Reference image list. Can include reference images (style, scene, element) and/or first/last frame images. |

#### `image_list` Structure

```json
"image_list": [
  {
    "image_url": "https://...",  // or base64 encoded string
    "type": "first_frame"        // optional: "first_frame" or "end_frame"
  },
  {
    "image_url": "https://...",
    "type": "end_frame"
  }
]
```

**Constraints:**
- Supported formats: `.jpg`, `.jpeg`, `.png`
- Max file size: 10MB per image
- Min dimensions: 300px × 300px
- Aspect ratio: between 1:2.5 and 2.5:1
- **Quantity limit depends on whether `video_list` is provided:**
  - With reference video: `len(image_list) + len(element_list)` ≤ **4**
  - Without reference video: `len(image_list) + len(element_list)` ≤ **7**
- `end_frame` is NOT supported when there are more than 2 images total
- `end_frame` requires a `first_frame` to also be present (cannot use end_frame alone)
- When using first_frame or first+end frame: **video editing (`base` mode) is disabled**

### Video Input Parameters (Reference to Video)

| Field | Type | Required | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `video_list` | array | Optional | None | Reference video list. Maximum 1 video. Only supported for `kling-v3-omni` in duration range 3s–10s. |

#### `video_list` Structure

```json
"video_list": [
  {
    "video_url": "https://...",          // Required, must be accessible URL
    "refer_type": "base",                // Optional, default: "base"
    "keep_original_sound": "no"          // Optional, default: "no"
  }
]
```

**`refer_type` values:**
| Value | Mode | Description |
| :--- | :--- | :--- |
| `"base"` | Video Editing | Edit/transform the content of the input video. Output duration = input video duration (ignores `duration` param). Does NOT support `aspect_ratio` or `first_frame`. |
| `"feature"` | Video Reference | Use the input video as a motion/style reference to generate new content. Requires `aspect_ratio`. |

**`keep_original_sound` values:**
| Value | Description |
| :--- | :--- |
| `"yes"` | Preserve original audio from the input video in the output |
| `"no"` | Discard original audio (default) |

**Video input constraints:**
- Format: MP4 or MOV
- Duration: 3–10 seconds
- Resolution: 720px–2160px
- Frame rate: 24–60fps
- `sound: "on"` is **mutually exclusive** with `video_list` — API will return an error if both are provided

### Element Input Parameters

| Field | Type | Required | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `element_list` | array | Optional | None | Custom element references (video character elements or multi-image elements). Created via `/v1/elements` endpoint. |

#### `element_list` Structure

```json
"element_list": [
  {
    "element_id": "element_id_string",  // ID from /v1/elements
    "refer_type": "subject"             // How to use this element
  }
]
```

**Note:** Element count contributes to the `image_list` quantity limit (combined total ≤ 4 with video, ≤ 7 without).

---

## Omni Model Template Syntax (Critical)

The `kling-v3-omni` model supports **template references** in `prompt` to precisely bind inputs to specific roles:

```
<<<element_1>>>  →  element_list[0]
<<<element_2>>>  →  element_list[1]
<<<image_1>>>    →  image_list[0]
<<<image_2>>>    →  image_list[1]
<<<video_1>>>    →  video_list[0]
```

**Example:**
```json
{
  "prompt": "<<<element_1>>> is walking through a futuristic city at night, cinematic lighting",
  "element_list": [{"element_id": "char_001", "refer_type": "subject"}]
}
```

This is the **core differentiator** of the Omni model — without template references, the model may not correctly associate inputs with their intended roles in the scene.

---

## Response Body

```json
{
  "code": 0,
  "message": "SUCCEED",
  "request_id": "string",
  "data": {
    "task_id": "string",
    "task_status": "submitted | processing | succeed | failed",
    "task_status_msg": "string",
    "created_at": 1234567890,
    "updated_at": 1234567890,
    "task_result": {
      "videos": [
        {
          "id": "string",
          "url": "string",       // Video download URL
          "duration": "5.041"    // Actual output duration (string)
        }
      ]
    }
  }
}
```

**Task status flow:** `submitted` → `processing` → `succeed` / `failed`

---

## Parameter Constraint Rules (from Testing)

The following rules were validated through systematic API testing:

| Rule | Description |
| :--- | :--- |
| **R1** | `sound: "on"` + `video_list` non-empty → API error: `sound on is not supported with video input` |
| **R2** | `refer_type: "feature"` requires `aspect_ratio` → API error if missing |
| **R3** | `refer_type: "base"` ignores `duration` → output duration = input video duration |
| **R4** | `multi_prompt[].index` must start from 1 and be consecutive → API error if starts from 0 |
| **R5** | Sum of `multi_prompt[].duration` must equal total `duration` → API error if mismatch |
| **R6** | `refer_type` is optional (default: `base`), but **cannot be controlled via prompt** — must be explicitly set |
| **R7** | `shot_type: "intelligence"` is NOT supported on `/v1/videos/omni-video` endpoint |
| **R8** | `multi_shot: true` + `shot_type: "customize"` is the **only** reliable multi-shot method on omni-video |
| **R9** | With `video_list`: `image_list + element_list` count ≤ 4; without: ≤ 7 |
| **R10** | `model_name` defaults to `kling-video-o1`; must explicitly pass `kling-v3-omni` for 3.0 Omni model |

---

## Capability Matrix (kling-v3-omni)

| Capability | std | pro |
| :--- | :--- | :--- |
| Text-to-video (single shot) | ✅ | ✅ |
| Text-to-video (multi-shot) | ✅ | ✅ |
| Image-to-video (single shot) | ✅ | ✅ |
| Image-to-video (multi-shot) | ✅ | ✅ |
| Start & end frame | ✅ | ✅ |
| Element control | ✅ | ✅ |
| Reference video (3s–10s only) | ✅ | ✅ |
| Voice control (`sound: "on"`) | ❌ | ❌ |

---

## Invocation Example: Reference to Video (feature mode)

```python
import jwt, time, requests

def generate_token(access_key, secret_key):
    payload = {"iss": access_key, "exp": int(time.time()) + 1800, "nbf": int(time.time()) - 5}
    return jwt.encode(payload, secret_key, algorithm="HS256")

token = generate_token("YOUR_ACCESS_KEY", "YOUR_SECRET_KEY")

payload = {
    "model_name": "kling-v3-omni",
    "prompt": "<<<video_1>>> A golden retriever runs on a sunny beach, cinematic slow motion",
    "video_list": [
        {
            "video_url": "https://example.com/input_video.mp4",
            "refer_type": "feature",
            "keep_original_sound": "no"
        }
    ],
    "aspect_ratio": "16:9",
    "duration": "5",
    "mode": "std"
}

response = requests.post(
    "https://api-singapore.klingai.com/v1/videos/omni-video",
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    json=payload
)
task_id = response.json()["data"]["task_id"]
```

## Invocation Example: Multi-Shot (customize mode)

```python
payload = {
    "model_name": "kling-v3-omni",
    "multi_shot": True,
    "shot_type": "customize",
    "multi_prompt": [
        {"index": 1, "prompt": "Wide aerial shot of a sunny beach at golden hour", "duration": "5"},
        {"index": 2, "prompt": "Close-up of a golden retriever running toward the ocean", "duration": "5"}
    ],
    "duration": "10",
    "aspect_ratio": "16:9",
    "mode": "std"
}
```
