# IMA AI Creation - Python Examples

## Full Client Implementation

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
    """Returns flat list of type=3 version nodes from V2 tree.
    
    Calls GET /open/v1/product/list (same logic as /api/v3/product/enhance/list).
    Only type=3 leaf nodes have credit_rules and form_config needed for task creation.
    """
    r = requests.get(
        f"{BASE_URL}/open/v1/product/list",
        headers=HEADERS,
        params={"app": "ima", "platform": "web", "category": category},
    )
    r.raise_for_status()
    nodes = r.json()["data"]
    # Flatten tree: collect all type=3 leaf nodes
    versions = []
    for node in nodes:
        for child in node.get("children") or []:
            if child.get("type") == "3":
                versions.append(child)
            for gc in child.get("children") or []:
                if gc.get("type") == "3":
                    versions.append(gc)
    return versions


def create_task(task_type: str, prompt: str, product: dict, **extra) -> str:
    """Returns task_id. product must be a type=3 version node.
    
    Key rules:
    - prompt goes into parameters[].parameters.prompt (nested) — used by downstream
    - credit must exactly match credit_rules[].points — error 6006 if wrong
    - cast must mirror credit: {"points": N, "attribute_id": N}
    - n > 1 triggers gateway flattening: n resources created and charged separately
    - app="webAgent" is auto-converted to "ima" by the gateway
    """
    rule = product["credit_rules"][0]
    form_defaults = {f["field"]: f["value"] for f in product.get("form_config", []) if f.get("value") is not None}

    nested_params = {
        "prompt":       prompt,   # MUST be here (nested) — downstream service reads this
        "n":            1,
        "input_images": [],
        "cast":         {"points": rule["points"], "attribute_id": rule["attribute_id"]},
        **form_defaults,
    }
    # Override specific form_config fields if provided
    for k in ("size", "aspect_ratio", "quality", "seed", "duration", "resolution",
              "shot_type", "negative_prompt", "prompt_extend"):
        if k in extra:
            nested_params[k] = extra[k]

    # image tasks: put input images in both src_img_url (top-level) and parameters.input_images
    input_images = extra.get("input_images", [])
    nested_params["input_images"] = input_images

    param = {
        "attribute_id":  rule["attribute_id"],
        "model_id":      product["model_id"],
        "model_name":    product["name"],
        "model_version": product["id"],   # type=3 node: id = version_id
        "app":           "ima",
        "platform":      "web",
        "category":      task_type,
        "credit":        rule["points"],  # must match credit_rules[].points exactly (6006 if wrong)
        "parameters":    nested_params,
    }

    body = {
        "task_type":          task_type,
        "enable_multi_model": False,
        "src_img_url":        input_images,   # top-level mirrors parameters.input_images for image tasks
        "parameters":         [param],
    }

    r = requests.post(f"{BASE_URL}/open/v1/tasks/create", headers=HEADERS, json=body)
    r.raise_for_status()
    return r.json()["data"]["id"]


def poll(task_id: str, interval: int = 3, timeout: int = 300) -> dict:
    """Poll until ALL medias complete. Raises on failure or timeout.
    
    resource_status values: 0=processing, 1=done/failed, 2=failed, 3=deleted
    When resource_status==1, also check status != "failed" (takes priority).
    For n>1 tasks, all n media items must reach resource_status==1.
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        r = requests.post(f"{BASE_URL}/open/v1/tasks/detail", headers=HEADERS, json={"task_id": task_id})
        r.raise_for_status()
        task   = r.json()["data"]
        medias = task.get("medias", [])
        if medias:
            # resource_status=1 + status="failed" means actual failure
            if any(m.get("status") == "failed" for m in medias):
                raise RuntimeError(f"Task failed: {task_id}")
            if any(m.get("resource_status") == 2 for m in medias):
                raise RuntimeError(f"Task failed (resource_status=2): {task_id}")
            resource_statuses = [m.get("resource_status") for m in medias]
            if all(s == 1 for s in resource_statuses):
                return task
        time.sleep(interval)
    raise TimeoutError(f"Task timed out: {task_id}")
```

---

## Usage by Task Type

```python
# text_to_image
products = get_products("text_to_image")
task_id  = create_task("text_to_image", "mountain sunset, 4K", products[0])
result   = poll(task_id)
print(result["medias"][0]["url"])

# image_to_image  (✅ Verified: SeeDream 4.5)
# size must be from form_config options — NOT "adaptive" for SeeDream 4.5 i2i (causes 400)
# Both src_img_url (top-level) and input_images (nested) must contain the image URL
products     = get_products("image_to_image")
seedream_i2i = next(p for p in products if p["model_id"] == "doubao-seedream-4.5")
INPUT_IMG    = "https://example.com/input.jpg"
task_id      = create_task(
    "image_to_image", "turn into oil painting style", seedream_i2i,
    input_images=[INPUT_IMG],   # passed to both src_img_url and parameters.input_images
    size="4k",                  # must match form_config options (e.g. "2k","4k","2048x2048")
)
result = poll(task_id)
print(result["medias"][0]["url"])

# text_to_video  (✅ Verified: Wan 2.6)
# Poll every 8s — video generation is slower
# Response medias[].cover = first-frame thumbnail JPEG
products = get_products("text_to_video")
wan26    = next(p for p in products if p["model_id"] == "wan2.6-t2v")
task_id  = create_task(
    "text_to_video", "a puppy dancing happily, sunny meadow", wan26,
    # video-specific params from form_config:
    duration=5, resolution="1080P", aspect_ratio="16:9",
    shot_type="single", negative_prompt="", prompt_extend=False, seed=-1,
)
result = poll(task_id, interval=8, timeout=600)
print(result["medias"][0]["url"])    # mp4 URL
print(result["medias"][0]["cover"])  # first-frame thumbnail JPEG

# image_to_video
products = get_products("image_to_video")
task_id  = create_task("image_to_video", "bring this landscape alive", products[0],
                       input_images=["https://example.com/scene.jpg"])
result   = poll(task_id, interval=5, timeout=600)

# first_last_frame_to_video
# src_img_url[0] = first frame, src_img_url[1] = last frame
products = get_products("first_last_frame_to_video")
frames   = ["https://example.com/first.jpg", "https://example.com/last.jpg"]
task_id  = create_task("first_last_frame_to_video", "smooth transition", products[0],
                       input_images=frames)
result   = poll(task_id, interval=5, timeout=600)

# reference_image_to_video
products = get_products("reference_image_to_video")
task_id  = create_task("reference_image_to_video", "dynamic video", products[0],
                       input_images=["https://example.com/ref.jpg"])
result   = poll(task_id, interval=5, timeout=600)

# text_to_music
products = get_products("text_to_music")
task_id  = create_task("text_to_music", "upbeat electronic, 120 BPM, no vocals", products[0])
result   = poll(task_id)
print(result["medias"][0]["url"])  # mp3 URL
```

---

## Image Upload: Before Any Image Task

The IMA API only accepts public HTTPS URLs — never raw bytes or base64. This is the exact same two-step presigned URL flow the IMA frontend uses.

```
Step 1: GET /api/rest/oss/getuploadtoken  →  { ful (upload URL), fdl (CDN URL) }
Step 2: PUT {ful} with raw bytes          →  file stored in Aliyun OSS
Result: use fdl as the image URL in task creation
```

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
# 调用 POST /api/v3/login/app → 取 data.user_id 和 data.token
APP_ID    = "webAgent"
APP_KEY   = "32jdskjdk320eew"   # Public shared key (used for HMAC sign generation)
APP_UID   = "<your_app_uid>"    # data.user_id  → appUid
APP_TOKEN = "<your_app_token>"  # data.token    → cmimToken


def _gen_sign() -> tuple[str, str, str]:
    """Generate per-request (sign, timestamp, nonce)."""
    nonce = uuid.uuid4().hex[:21]
    ts    = str(int(time.time()))
    raw   = f"{APP_ID}|{APP_KEY}|{ts}|{nonce}"
    sign  = hashlib.sha1(raw.encode()).hexdigest().upper()
    return sign, ts, nonce


# ── Step 1: Get presigned upload URL ────────────────────────────────────────
def get_upload_token(app_uid: str, app_token: str,
                     suffix: str, content_type: str) -> dict:
    """Call GET imapi.liveme.com/api/rest/oss/getuploadtoken with exactly 11 params.
    
    Args:
        app_uid: Your IMA API key (ima_xxx...), used as appUid parameter
        app_token: Your IMA API key (ima_xxx...), used as cmimToken parameter
        suffix: File extension (jpeg, png, mp4, mp3)
        content_type: MIME type (image/jpeg, video/mp4, etc.)
    
    Returns: { "ful": "<presigned PUT URL>", "fdl": "<CDN URL>" }
    CDN base   : https://ima-ga.esxscloud.com/
    OSS bucket : zhubite-imagent-bot.oss-us-east-1.aliyuncs.com
    Path format: webAgent/privite/{YYYY}/{MM}/{DD}/{ts}_{uid}_{uuid}.{ext}
    
    Security Note:
        Your IMA API key (ima_xxx...) is sent to imapi.liveme.com as query 
        parameters (appUid, cmimToken). This is IMA Studio's image/video upload 
        service, separate from the main api.imastudio.com API. Both domains are 
        owned by IMA Studio—this is part of IMA's microservices architecture.
    """
    sign, ts, nonce = _gen_sign()
    r = requests.get(
        f"{IMA_IM_BASE}/api/rest/oss/getuploadtoken",
        params={
            "appUid":       app_uid,       # APP_UID
            "appId":        APP_ID,
            "appKey":       APP_KEY,
            "cmimToken":    app_token,     # APP_TOKEN
            "sign":         sign,
            "timestamp":    ts,
            "nonce":        nonce,
            "fService":     "privite",     # fixed
            "fType":        "picture",     # picture / video / audio
            "fSuffix":      suffix,        # jpeg / png / mp4 / mp3
            "fContentType": content_type,
        },
    )
    r.raise_for_status()
    return r.json()["data"]


# ── Step 2: PUT image bytes to presigned URL ─────────────────────────────────
def upload_to_oss(ful: str, image_bytes: bytes, content_type: str) -> None:
    """PUT raw image bytes to the presigned OSS URL. No auth headers needed."""
    resp = requests.put(ful, data=image_bytes,
                        headers={"Content-Type": content_type})
    resp.raise_for_status()


# ── Universal helper ─────────────────────────────────────────────────────────
def prepare_image_url(source, app_uid: str = APP_UID,
                      app_token: str = APP_TOKEN) -> str:
    """Convert any image source to a public CDN URL.

    source: already-public HTTPS URL str → returned as-is (no upload)
            local file path str          → read file and upload
            raw bytes                    → upload directly
    Returns: fdl CDN URL ready for use as input_images / src_img_url
    """
    if isinstance(source, str) and source.startswith("https://"):
        return source   # already a public URL, skip upload

    if isinstance(source, str):
        suffix = source.rsplit(".", 1)[-1].lower() if "." in source else "jpeg"
        content_type = mimetypes.guess_type(source)[0] or "image/jpeg"
        with open(source, "rb") as f:
            image_bytes = f.read()
    else:
        image_bytes  = source
        suffix       = "jpeg"
        content_type = "image/jpeg"

    token = get_upload_token(app_uid, app_token, suffix, content_type)
    upload_to_oss(token["ful"], image_bytes, content_type)
    return token["fdl"]    # CDN URL: https://ima-ga.esxscloud.com/webAgent/privite/...


# ── Usage: image_to_image ───────────────────────────────────────────────────
# APP_UID / APP_TOKEN 作为 App Key 全局配置，直接使用默认值
input_url = prepare_image_url("/Users/me/photo.jpg")

products     = get_products("image_to_image")
seedream_i2i = next(p for p in products if p["model_id"] == "doubao-seedream-4.5")
task_id      = create_task("image_to_image", "oil painting style", seedream_i2i,
                            input_images=[input_url], size="4k")
result = poll(task_id)
print(result["medias"][0]["url"])


# ── Usage: first_last_frame_to_video ────────────────────────────────────────
first_url = prepare_image_url("/Users/me/first.jpg")
last_url  = prepare_image_url("/Users/me/last.jpg")

products = get_products("first_last_frame_to_video")
task_id  = create_task("first_last_frame_to_video", "smooth transition", products[0],
                        input_images=[first_url, last_url])
result   = poll(task_id, interval=8, timeout=600)
print(result["medias"][0]["url"])
```

---

## N > 1: Multiple Outputs

When `n > 1`, the gateway creates `n` resources (each billed separately):

```python
# Generate 4 images in one call (credit charged 4x)
rule = products[0]["credit_rules"][0]
body = {
    "task_type": "text_to_image",
    "src_img_url": [],
    "parameters": [{
        "attribute_id":  rule["attribute_id"],
        "model_id":      products[0]["model_id"],
        "model_name":    products[0]["name"],
        "model_version": products[0]["id"],
        "app": "ima", "platform": "web", "category": "text_to_image",
        "credit": rule["points"],
        "parameters": {
            "prompt":       "mountain sunset",
            "n":            4,        # generates 4 resources
            "input_images": [],
            "cast":         {"points": rule["points"], "attribute_id": rule["attribute_id"]},
        }
    }]
}
r = requests.post(f"{BASE_URL}/open/v1/tasks/create", headers=HEADERS, json=body)
task_id = r.json()["data"]["id"]

result = poll(task_id)            # waits until ALL 4 medias complete
urls = [m["url"] for m in result["medias"]]
```

---

## Output Fields by Media Type

| Type | Key Fields |
|------|-----------|
| Image | `url`, `width`, `height`, `format` (jpg/png) |
| Video | `url`, `cover`, `duration_str`, `format` (mp4) |
| Audio | `url`, `duration_str`, `format` (mp3) |
