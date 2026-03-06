---
name: babblebrush
description: Generate and iteratively edit images. Supports storage, UI for manual editing, history, version branching, time travel, reference images, and multiple AI models and providers with your own API keys.
version: "1.4.1"
metadata:
  openclaw:
    requires:
      env:
        - BABBLEBRUSH_API_KEY
---

# babbleBrush

babbleBrush is a voice-first image editor. Humans can use it directly to edit, view, manage images and agents can use it alongside their human or on behalf of the user to do the same programatically.

The units of work are canvases and versions, you create or use an existing canvas and edit the image inside of it as a canvas version, ie, the image edit. You can also upload images in the canvas to edit them, to use as a reference, or mixing them in the edit.

Website - https://babblebrush.com

API index - https://babblebrush.com/api

- Users start with trial credits
- After trial credits are exhausted, platform access must be unlocked(one time payment) to manage API keys
- Check `platform_access_unlocked` in `GET /api/v1/me` to see if unlocked

**Important:**
- If you haven't added a key for a provider, edits with that provider will use credits
- Your API usage is billed directly by the provider (Google, xAI, etc.)
- Keys are encrypted and stored securely

## Skill URL

| File | URL |
|------|-----|
| `claude/SKILL.md` | `https://babblebrush.com/babblebrush/claude/SKILL.md` |
| `openclaw/SKILL.md` | `https://babblebrush.com/babblebrush/openclaw/SKILL.md` |


## Core Concepts

### Canvas

A **Canvas** is a workspace for image generation & editing.
A canvas contains multiple **Canvas versions** representing the edit history.
The latest completed canvas version is the current image of any given canvas. 


### Canvas version

A **canvas version** represents an image edit inside a canvas, it's the main unit of work. 
It contains information all the information about the eidt, like the prompt, image references uploaded(the limit depends on the model), the source canvas version the edit branched from, the status, etc




## Authentication

All requests require an API key sent in the Authorization header.

```bash
Authorization: Bearer bb_...
```

You can create API tokens from the settings page at `https://babblebrush.com/app/settings`.

Once you have the API key, store it locally and securely.


---

## API Reference

- https://babblebrush.com/api

---

## Endpoint Details

### Get current user

```bash
curl -H "Authorization: Bearer $BABBLEBRUSH_API_KEY" \
  "https://babblebrush.com/api/v1/me"
```

Response:

```json
{
  "email": "user@example.com",
  "credits": 5,
  "platform_access_unlocked": false,
  "platform_access_unlocked_at": null,
  "canvases_count": 1,
  "created_at": "2026-02-27T14:27:41.281Z"
}
```

Info:

- `platform_access_unlocked` - Whether user has unlocked platform access (required for BYOK after trial)


### List provider models

```bash
curl -H "Authorization: Bearer $BABBLEBRUSH_API_KEY" \
  "https://babblebrush.com/api/v1/provider-models"
```

Response:

```json
{
  "providers": [
    {
      "id": "gemini",
      "label": "Gemini",
      "models": [
        {
          "id": "gemini-2.5-flash-image",
          "name": "Flash 2.5 - Nano Banana",
          "description": "Quick image generation",
          "max_imgs_per_prompt": 3
        }
      ]
    }
  ]
}
```

Info:

  - `max_imgs_per_prompt` - Maximum images accepted in a single prompt

### List provider credentials

See which providers have API keys configured.

```bash
curl -H "Authorization: Bearer $BABBLEBRUSH_API_KEY" \
  "https://babblebrush.com/api/v1/provider-credentials"
```

Response:

```json
{
  "credentials": [
    {
      "provider": "gemini",
      "created_at": "2025-10-11T10:00:00.000Z",
      "updated_at": "2025-10-11T10:00:00.000Z"
    }
  ]
}
```

### Add/update provider API key

```bash
curl -X POST \
  -H "Authorization: Bearer $BABBLEBRUSH_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"provider": "gemini", "api_key": "AIza..."}' \
  "https://babblebrush.com/api/v1/provider-credentials"
```

Valid providers: `gemini`, `xai`

Response:

```json
{
  "credential": {
    "provider": "gemini",
    "created_at": "2025-10-11T10:00:00.000Z",
    "updated_at": "2025-10-11T10:00:00.000Z"
  },
  "message": "API key saved for gemini"
}
```

### Remove provider API key

```bash
curl -X DELETE \
  -H "Authorization: Bearer $BABBLEBRUSH_API_KEY" \
  "https://babblebrush.com/api/v1/provider-credentials/gemini"
```

Response:

```json
{
  "message": "API key removed for gemini"
}
```

### List canvases

```bash
curl -H "Authorization: Bearer $BABBLEBRUSH_API_KEY" \
  "https://babblebrush.com/api/v1/canvases"
```

Response:

```json
{
  "canvases": [
    {
      "public_token": "01234567-89ab-cdef-0123-456789abcdef",
      "title": "My Logo Design",
      "default_model": "gemini/gemini-2.5-flash-image",
      "current_version_id": 105,
      "latest_version_number": 5,
      "current_version_image_url": "https://babblebrush.com/rails/active_storage/...",
      "is_latest_version_pending": false,
      "created_at": "2025-10-11T10:00:00.000Z",
      "updated_at": "2025-10-11T12:30:00.000Z"
    }
  ]
}
```

### Create canvas with image

```bash
# With file upload
curl -X POST \
  -H "Authorization: Bearer $BABBLEBRUSH_API_KEY" \
  -F "title=My New Canvas" \
  -F "image=@/path/to/image.png" \
  "https://babblebrush.com/api/v1/canvases"

# With base64 image
curl -X POST \
  -H "Authorization: Bearer $BABBLEBRUSH_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My New Canvas",
    "default_model": "gemini/gemini-2.5-flash-image",
    "image": "data:image/png;base64,iVBORw0KGgo..."
  }' \
  "https://babblebrush.com/api/v1/canvases"
```

Response:

```json
{
  "public_token": "01234567-89ab-cdef-0123-456789abcdef",
  "title": "My New Canvas",
  "default_model": "gemini/gemini-2.5-flash-image",
  "current_version_id": 201,
  "latest_version_number": 1,
  "current_version_image_url": "https://babblebrush.com/rails/active_storage/...",
  "is_latest_version_pending": false,
  "created_at": "2025-10-11T10:00:00.000Z",
  "updated_at": "2025-10-11T10:00:00.000Z",
  "versions": [
    {
      "id": 201,
      "canvas_id": 42,
      "version_number": 1,
      "status": "completed",
      "prompt": null,
      "model_identifier": "gemini/gemini-2.5-flash-image",
      "fail_reason": null,
      "source_version_id": null,
      "job_identifier": null,
      "metadata": {},
      "image_url": "https://babblebrush.com/rails/active_storage/...",
      "created_at": "2025-10-11T10:00:00.000Z",
      "updated_at": "2025-10-11T10:00:00.000Z"
    }
  ]
}
```

### Create blank canvas

```bash
curl -X POST \
  -H "Authorization: Bearer $BABBLEBRUSH_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"title": "Blank Canvas"}' \
  "https://babblebrush.com/api/v1/canvases/blank"
```

### Get canvas details

```bash
curl -H "Authorization: Bearer $BABBLEBRUSH_API_KEY" \
  "https://babblebrush.com/api/v1/canvases/01234567-89ab-cdef-0123-456789abcdef"
```

`/api/v1/canvases/:id` expects the canvas `public_token`.

Response includes full canvas details with all versions.

### Update canvas

```bash
# Update title
curl -X PATCH \
  -H "Authorization: Bearer $BABBLEBRUSH_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"title": "New Title"}' \
  "https://babblebrush.com/api/v1/canvases/01234567-89ab-cdef-0123-456789abcdef"

# Change default model
curl -X PATCH \
  -H "Authorization: Bearer $BABBLEBRUSH_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"default_model": "gemini/gemini-3-pro-image-preview"}' \
  "https://babblebrush.com/api/v1/canvases/01234567-89ab-cdef-0123-456789abcdef"
```

### Delete canvas

```bash
curl -X DELETE \
  -H "Authorization: Bearer $BABBLEBRUSH_API_KEY" \
  "https://babblebrush.com/api/v1/canvases/01234567-89ab-cdef-0123-456789abcdef"
```

Response:

```json
{"ok": true}
```

### List versions of a canvas

```bash
curl -H "Authorization: Bearer $BABBLEBRUSH_API_KEY" \
  "https://babblebrush.com/api/v1/canvases/01234567-89ab-cdef-0123-456789abcdef/versions"
```

Response:

```json
{
  "versions": [
    {
      "id": 5,
      "version_number": 5,
      "status": "completed",
      "prompt": "add a sunset background",
      "model": "gemini/gemini-2.5-flash-image",
      "fail_reason": null,
      "source_version_id": 4,
      "is_current": true,
      "image_url": "https://babblebrush.com/rails/active_storage/...",
      "reference_images_count": 0,
      "reference_images": [],
      "created_at": "2025-10-11T12:30:00.000Z"
    },
    {
      "id": 4,
      "version_number": 4,
      "status": "completed",
      "prompt": "make it larger",
      "model": "gemini/gemini-2.5-flash-image",
      "fail_reason": null,
      "source_version_id": 3,
      "is_current": false,
      "image_url": "https://babblebrush.com/rails/active_storage/...",
      "reference_images_count": 0,
      "reference_images": [],
      "created_at": "2025-10-11T12:00:00.000Z"
    }
  ]
}
```

### Create new edit in a canvas (enqueue)

This is the main editing endpoint. It creates a new version and starts AI processing.

```bash
curl -X POST \
  -H "Authorization: Bearer $BABBLEBRUSH_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "add a red ball in the center"}' \
  "https://babblebrush.com/api/v1/canvases/01234567-89ab-cdef-0123-456789abcdef/versions"
```

Optional parameters:
- `source_version_id` - Edit from a specific version instead of the current version
- `model` - Override the model for this specific edit (e.g., `gemini/gemini-3-pro-image-preview`)

**How image inputs are chosen for this edit:**
- The new pending edit version points to a `source_version`.
- `source_version` is `source_version_id` if provided, otherwise the canvas current version.
- Image inputs for the provider come from that `source_version`.
- If you want extra context images for the next edit, upload them as **reference images** to that `source_version` before enqueueing.
- Max images are model-specific. Use `GET /api/v1/provider-models` and read `max_imgs_per_prompt` (total images = source image + reference images).

**Reference images workflow:**
1. Upload reference image(s) to the version you want to use as source.
2. Enqueue a new edit with that version as `source_version_id`.

```bash
# 1) Upload image to version 5 (source for next edit)
curl -X POST \
  -H "Authorization: Bearer $BABBLEBRUSH_API_KEY" \
  -F "image=@/path/to/reference.png" \
  "https://babblebrush.com/api/v1/canvases/01234567-89ab-cdef-0123-456789abcdef/versions/5/images"

# 2) Enqueue edit from version 5 so uploaded image is used
curl -X POST \
  -H "Authorization: Bearer $BABBLEBRUSH_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"make it cinematic", "source_version_id": 5}' \
  "https://babblebrush.com/api/v1/canvases/01234567-89ab-cdef-0123-456789abcdef/versions"
```

**Example: add 3 reference images (extra context)**

```bash
# Check model limits first (max_imgs_per_prompt)
curl -H "Authorization: Bearer $BABBLEBRUSH_API_KEY" \
  "https://babblebrush.com/api/v1/provider-models"

# Upload 3 extra reference images to source version 5
curl -X POST -H "Authorization: Bearer $BABBLEBRUSH_API_KEY" \
  -F "image=@/path/to/ref-1.png" \
  "https://babblebrush.com/api/v1/canvases/01234567-89ab-cdef-0123-456789abcdef/versions/5/images"

curl -X POST -H "Authorization: Bearer $BABBLEBRUSH_API_KEY" \
  -F "image=@/path/to/ref-2.png" \
  "https://babblebrush.com/api/v1/canvases/01234567-89ab-cdef-0123-456789abcdef/versions/5/images"

curl -X POST -H "Authorization: Bearer $BABBLEBRUSH_API_KEY" \
  -F "image=@/path/to/ref-3.png" \
  "https://babblebrush.com/api/v1/canvases/01234567-89ab-cdef-0123-456789abcdef/versions/5/images"

# Enqueue edit from that source version
curl -X POST -H "Authorization: Bearer $BABBLEBRUSH_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"blend these references into one cohesive scene", "source_version_id": 5}' \
  "https://babblebrush.com/api/v1/canvases/01234567-89ab-cdef-0123-456789abcdef/versions"
```

Note: this 3-reference example needs a model that supports at least 4 total images (1 source + 3 references).

**Model Override Example:**

```bash
curl -X POST \
  -H "Authorization: Bearer $BABBLEBRUSH_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "add a red ball", "model": "xai/grok-imagine-image"}' \
  "https://babblebrush.com/api/v1/canvases/01234567-89ab-cdef-0123-456789abcdef/versions"
```

**Model Resolution Order:**
1. Per-edit `model` parameter (if provided)
2. Canvas `default_model` (if set)
3. Default model for the provider

Response (202 Accepted):

```json
{
  "version": {
    "id": 6,
    "version_number": 6,
    "status": "pending",
    "prompt": "add a red ball in the center",
    "model": "gemini/gemini-2.5-flash-image",
    "fail_reason": null,
    "source_version_id": 5,
    "is_current": false,
    "image_url": null,
    "reference_images_count": 0,
    "created_at": "2025-10-11T13:00:00.000Z"
  },
  "remaining_credits": 9
}
```

**Important**: The edit is processed asynchronously. Poll the version endpoint or canvas to check when it completes.

### Get canvas version details

```bash
curl -H "Authorization: Bearer $BABBLEBRUSH_API_KEY" \
  "https://babblebrush.com/api/v1/canvases/01234567-89ab-cdef-0123-456789abcdef/versions/6"
```

Use this to poll for completion after creating an edit.

### Promote canvas version (make current)

"Time travel" to a previous version by promoting it to current.

```bash
curl -X POST \
  -H "Authorization: Bearer $BABBLEBRUSH_API_KEY" \
  "https://babblebrush.com/api/v1/canvases/01234567-89ab-cdef-0123-456789abcdef/versions/3/promote"
```

Response:

```json
{
  "ok": true,
  "current_version": {
    "id": 3,
    "version_number": 3,
    "status": "completed",
    "is_current": true,
    ...
  }
}
```

### Cancel pending edit

Cancel an edit that is still pending or processing. Credits are refunded.

```bash
curl -X POST \
  -H "Authorization: Bearer $BABBLEBRUSH_API_KEY" \
  "https://babblebrush.com/api/v1/canvases/01234567-89ab-cdef-0123-456789abcdef/versions/6/cancel"
```

Response:

```json
{
  "ok": true,
  "version": {
    "id": 6,
    "status": "cancelled",
    ...
  },
  "remaining_credits": 10
}
```

**Important**: Cancel is best-effort. If provider request already started, provider-side compute may continue.


---

## Common Workflows

### 1. Create canvas, enqueue edit, poll to completion

```bash
# 1) Create a blank canvas
curl -X POST \
  -H "Authorization: Bearer $BABBLEBRUSH_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"title": "My Project"}' \
  "https://babblebrush.com/api/v1/canvases/blank"

# 2) Copy `public_token` from response and set it
CANVAS_PUBLIC_TOKEN="<paste_public_token_here>"

# 3) Enqueue first edit
curl -X POST \
  -H "Authorization: Bearer $BABBLEBRUSH_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "draw a mountain landscape with snow"}' \
  "https://babblebrush.com/api/v1/canvases/$CANVAS_PUBLIC_TOKEN/versions"

# 4) Copy `version.id` from response and set it
VERSION_ID="<paste_version_id_here>"

# 5) Poll this version (repeat until status is completed/failed/cancelled)
curl -H "Authorization: Bearer $BABBLEBRUSH_API_KEY" \
  "https://babblebrush.com/api/v1/canvases/$CANVAS_PUBLIC_TOKEN/versions/$VERSION_ID"

# 6) Read latest canvas state
curl -H "Authorization: Bearer $BABBLEBRUSH_API_KEY" \
  "https://babblebrush.com/api/v1/canvases/$CANVAS_PUBLIC_TOKEN"
```

### 2. Add reference images, then edit from that source version

```bash
# 1) Read canvas details
curl -H "Authorization: Bearer $BABBLEBRUSH_API_KEY" \
  "https://babblebrush.com/api/v1/canvases/$CANVAS_PUBLIC_TOKEN"

# 2) Copy `current_version_id` from response and set it
SOURCE_VERSION_ID="<paste_current_version_id_here>"

# 3) Upload extra context images to that source version
curl -X POST \
  -H "Authorization: Bearer $BABBLEBRUSH_API_KEY" \
  -F "image=@/path/to/ref-1.png" \
  "https://babblebrush.com/api/v1/canvases/$CANVAS_PUBLIC_TOKEN/versions/$SOURCE_VERSION_ID/images"

curl -X POST \
  -H "Authorization: Bearer $BABBLEBRUSH_API_KEY" \
  -F "image=@/path/to/ref-2.png" \
  "https://babblebrush.com/api/v1/canvases/$CANVAS_PUBLIC_TOKEN/versions/$SOURCE_VERSION_ID/images"

# 4) Enqueue edit from the same source version
curl -X POST \
  -H "Authorization: Bearer $BABBLEBRUSH_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"prompt\":\"blend the scene using the references\", \"source_version_id\": \"$SOURCE_VERSION_ID\"}" \
  "https://babblebrush.com/api/v1/canvases/$CANVAS_PUBLIC_TOKEN/versions"
```

### 3. Branch from an older version (with optional model override)

```bash
# Branch A from version 2 using default canvas model
curl -X POST \
  -H "Authorization: Bearer $BABBLEBRUSH_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "try watercolor style", "source_version_id": 2}' \
  "https://babblebrush.com/api/v1/canvases/$CANVAS_PUBLIC_TOKEN/versions"

# Branch B from same source with explicit model override
curl -X POST \
  -H "Authorization: Bearer $BABBLEBRUSH_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "try watercolor style", "source_version_id": 2, "model": "gemini/gemini-3-pro-image-preview"}' \
  "https://babblebrush.com/api/v1/canvases/$CANVAS_PUBLIC_TOKEN/versions"
```

### 4. Promote or cancel an edit

```bash
# Promote version 3 to current ("time travel")
curl -X POST \
  -H "Authorization: Bearer $BABBLEBRUSH_API_KEY" \
  "https://babblebrush.com/api/v1/canvases/$CANVAS_PUBLIC_TOKEN/versions/3/promote"

# Cancel version 8 if still pending/processing (best-effort)
curl -X POST \
  -H "Authorization: Bearer $BABBLEBRUSH_API_KEY" \
  "https://babblebrush.com/api/v1/canvases/$CANVAS_PUBLIC_TOKEN/versions/8/cancel"
```

### 5. Start multiple edits from the same source (different models)

```bash
# 1) Read canvas details
curl -H "Authorization: Bearer $BABBLEBRUSH_API_KEY" \
  "https://babblebrush.com/api/v1/canvases/$CANVAS_PUBLIC_TOKEN"

# 2) Copy `current_version_id` from response and set it
SOURCE_VERSION_ID="<paste_current_version_id_here>"

# 3) Create edit A from the same source using Gemini Pro
curl -X POST \
  -H "Authorization: Bearer $BABBLEBRUSH_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"prompt\":\"cinematic dramatic lighting\", \"source_version_id\": \"$SOURCE_VERSION_ID\", \"model\": \"gemini/gemini-3-pro-image-preview\"}" \
  "https://babblebrush.com/api/v1/canvases/$CANVAS_PUBLIC_TOKEN/versions"

# 4) Copy `version.id` from edit A response and set it
VERSION_A="<paste_version_a_id_here>"

# 5) Create edit B from the same source using xAI
curl -X POST \
  -H "Authorization: Bearer $BABBLEBRUSH_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"prompt\":\"cinematic dramatic lighting\", \"source_version_id\": \"$SOURCE_VERSION_ID\", \"model\": \"xai/grok-imagine-image\"}" \
  "https://babblebrush.com/api/v1/canvases/$CANVAS_PUBLIC_TOKEN/versions"

# 6) Copy `version.id` from edit B response and set it
VERSION_B="<paste_version_b_id_here>"

# 7) Poll each edit (repeat each request until terminal status)
curl -H "Authorization: Bearer $BABBLEBRUSH_API_KEY" \
  "https://babblebrush.com/api/v1/canvases/$CANVAS_PUBLIC_TOKEN/versions/$VERSION_A"

curl -H "Authorization: Bearer $BABBLEBRUSH_API_KEY" \
  "https://babblebrush.com/api/v1/canvases/$CANVAS_PUBLIC_TOKEN/versions/$VERSION_B"
```

---

## Error Behavior

| Status | Meaning |
|--------|---------|
| 401 | Missing or invalid API key |
| 402 | Insufficient credits |
| 403 | Forbidden |
| 404 | Resource not found |
| 422 | Invalid request (validation error) |
| 500 | Server error |

Error response format:

```json
{
  "error": "Human-readable error message"
}
```


---

## Rate Limits

Currently no rate limits are enforced, but please be respectful of the service.

---

## Tips for Agents

1. **Check access first** - Before starting a workflow, verify the user has sufficient credits or `platform_access_unlocked` with provider keys configured
2. **Poll for completion** - Edits are async; poll `GET /api/v1/canvases/:canvas_id/versions/:id` until status is terminal (`completed`, `failed`, `cancelled`)
3. **Use descriptive prompts** - The AI responds better to detailed, clear prompts
4. **Branch experiments** - Use `source_version_id` to try different approaches without losing progress
5. **Promote to revert** - If an edit doesn't work out, promote an earlier version to go back

6. **Inline Images in the chat** - If the chat interface you're using allows(eg: Telegram), let's display the images inline instead of just posting the image link, unless the user asks for it.
