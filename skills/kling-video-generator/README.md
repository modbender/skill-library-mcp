# kling-video-generator

> An Agent Skill for generating high-quality videos using the **Kling 3.0 Omni** model via the official Kling API.

[![ClawHub](https://img.shields.io/badge/ClawHub-Skill-blue)](https://www.clawhub.ai)
[![Kling API](https://img.shields.io/badge/Kling-3.0%20Omni-purple)](https://app.klingai.com/global/dev/document-api)

---

## What This Skill Does

This skill enables an AI agent to generate and manipulate videos using the Kling 3.0 Omni model. It provides a structured, tested workflow for constructing correct API requests based on user intent, covering:

- **Text-to-Video**: Generate a video from a text prompt.
- **Image-to-Video**: Animate a static image.
- **Video Editing** (`refer_type: base`): Modify an existing video (e.g., change a subject, alter the scene).
- **Video Reference** (`refer_type: feature`): Use an existing video as a reference for camera movement and style.
- **Multi-shot Generation**: Create a video with multiple distinct scenes using `multi_shot: true` + `shot_type: customize`.
- **Audio Generation**: Generate video with synchronized speech and sound effects.

---

## Key Findings from Testing

This skill is built on **extensive API testing** of the Kling 3.0 Omni model. The following critical, non-obvious rules were discovered through testing and are embedded into the skill's workflow:

| Parameter | Rule |
| :--- | :--- |
| `refer_type` | **Must be explicit.** Omitting it defaults to `base` (editing mode) regardless of prompt intent. Cannot be controlled via prompt alone. |
| `duration` | **Ignored in `base` (editing) mode.** Output duration always equals input video duration. |
| `sound` | **Incompatible with `video_list`.** Setting `sound: on` while providing a reference video causes an API error. |
| `shot_type` | **Must be `customize`** for multi-shot with the Omni model. `intelligence` mode is not supported on `kling-v3-omni`. |
| `multi_prompt` | `index` must start from **1**. Sum of all `duration` values must equal the top-level `duration`. Max **6 shots**. |
| `aspect_ratio` | **Required for `feature` mode.** |
| `image_list` | Max **7 images** without video input, max **4 images** with video input. |

---

## File Structure

```
kling-video-generator/
├── SKILL.md                        # Main skill instructions and workflow
├── README.md                       # This file
├── references/
│   └── prompt_guide.md             # Kling 3.0 Omni prompting guide with few-shot examples
└── scripts/
    └── kling_api.py                # Python helper for authentication and API calls
```

---

## Quick Start

### Prerequisites

- Kling API Access Key and Secret Key (from [Kling AI Developer Console](https://app.klingai.com/global/dev))
- Python 3.8+ with `PyJWT` and `requests` installed

### Setup

```bash
pip install PyJWT requests
export KLING_ACCESS_KEY="your_access_key"
export KLING_SECRET_KEY="your_secret_key"
```

### Example: Text-to-Video

```python
from scripts.kling_api import KlingAPI
import os

api = KlingAPI(os.environ["KLING_ACCESS_KEY"], os.environ["KLING_SECRET_KEY"])

payload = {
    "model_name": "kling-v3-omni",
    "prompt": "A giant panda wearing black-framed glasses is reading a book in a café, medium shot, blurred background, ambient lighting, cinematic color palette.",
    "aspect_ratio": "16:9",
    "duration": "5",
    "sound": "off"
}

task = api.create_omni_video_task(payload)
task_id = task["data"]["task_id"]
result = api.poll_for_completion(task_id)
print("Video URL:", result["videos"][0]["url"])
```

### Example: Multi-shot Video

```python
payload = {
    "model_name": "kling-v3-omni",
    "multi_shot": True,
    "shot_type": "customize",
    "duration": "10",
    "aspect_ratio": "16:9",
    "multi_prompt": [
        {"index": 1, "prompt": "Aerial wide shot of a sunny beach at golden hour, calm waves.", "duration": "3"},
        {"index": 2, "prompt": "A golden retriever runs at full speed toward the ocean, water splashing, dynamic tracking shot.", "duration": "4"},
        {"index": 3, "prompt": "Close-up of the golden retriever face, tongue out, happily swimming.", "duration": "3"}
    ]
}
```

---

## Prompting Guide

The skill includes a comprehensive prompting guide at `references/prompt_guide.md`, covering:

- **Official Prompt Formula**: `Subject + Movement + Scene + [Camera + Lighting + Atmosphere]`
- **Template Syntax**: How to use `<<<image_1>>>`, `<<<element_1>>>`, `<<<video_1>>>` to reference input assets
- **Few-shot Examples**: For single-shot, multi-shot, dialogue, editing, and reference scenarios
- **Common Mistakes**: 7 tested anti-patterns to avoid

---

## License

MIT License — feel free to use, modify, and distribute.

---

*Built and tested against Kling 3.0 Omni API — February 2026*


---

## Publishing to ClawHub

To publish this skill to the [ClawHub registry](https://www.clawhub.ai), use the `clawhub` CLI:

```bash
# First, log in to ClawHub
clawhub login

# Then, publish the skill from its root directory
clawhub publish . --slug kling-video-generator --name "Kling 3.0 Video Generator" --version 1.0.0 --changelog "Initial release based on extensive API testing"
```
