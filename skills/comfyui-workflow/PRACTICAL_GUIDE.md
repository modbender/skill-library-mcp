# ComfyUI Qwen - Practical Guide (Condensed)

This is the operational quick guide for agent usage. Covers all 24 workflows across 8 model families.

---

## Requirements

| Requirement | Details |
|-------------|---------|
| **Python** | 3.10 or higher |
| **pip packages** | `websocket-client`, `requests` |
| **ComfyUI server** | Running locally or remotely |
| **Token** | Required if ComfyUI has authentication enabled |

Install dependencies:
```bash
pip install websocket-client requests
```

---

## Prerequisites

```bash
# Start ComfyUI manually before running any workflow
# Verify it's running at http://127.0.0.1:8188

TOKEN="your_comfy_token_here"  # Get from ComfyUI settings
```

Required assets live in:

- `scripts/comfy_api.py`
- workflow JSON files in `workflows/`
- `WORKFLOWS_SUMMARY.md` for full node-level details

## Recommended execution pattern

Use the Python wrapper rather than embedding giant inline workflow payloads.

```python
import sys, os
sys.path.insert(0, '/path/to/comfyui-workflow-skill/scripts')
from comfy_api import run_workflow, load_workflow

token = "your_comfy_token_here"
workflow = load_workflow("image_qwen_image_2512_with_2steps_lora.json")
workflow["108"]["inputs"]["text"] = "A futuristic cityscape at night"
files = run_workflow("127.0.0.1:8188", token, workflow, output_prefix="/tmp/gen")
print(files)  # list of saved image/video/audio file paths
```

## Task map — Image Generation

| Task | Workflow | Notes |
|------|----------|-------|
| Fast text-to-image | `image_qwen_image_2512_with_2steps_lora.json` | 2 steps, rapid drafts |
| High-quality text-to-image | `image_qwen_Image_2512.json` | 50 steps, best detail |
| Text-to-image (good text rendering) | `image_kandinsky5_t2i.json` | 50 steps, DualCLIP, good at rendering text in images |
| Image editing (fast) | `image_flux2_klein_image_edit_9b_distilled.json` | 4 steps, CFG=1 |
| Image editing (quality) | `image_qwen_image_edit_2511.json` | 40 steps, CFG=4 |
| Image editing (2509 + LoRA) | `image_qwen_image_edit_2509.json` | 4 steps with Lightning LoRA |
| Layered control | `image_qwen_image_layered_control.json` | Structured layer composition |
| Flux image gen/edit | `image_flux2_fp8.json` | Mistral 3 CLIP, BasicGuider pipeline |
| Flux Klein 4B edit | `image_flux2_klein_image_edit_4b_base.json` | Qwen 3 4B CLIP, lighter model |
| Flux Klein 9B edit | `image_flux2_klein_image_edit_9b_base.json` | Qwen 3 8B CLIP, higher quality |
| Image to realistic photo | `templates-image_to_real.json` | 8 steps, Anything2Real LoRA |
| Lighting transfer | `templates-portrait_light_migration.json` | 8 steps, Light-Migration LoRA |
| 8 camera angles (character) | `templates-1_click_multiple_character_angles-v1.0.json` | 8 parallel KSamplers |
| 8 camera angles (scene) | `templates-1_click_multiple_scene_angles-v1.0.json` | 8 parallel KSamplers |

## Task map — Video Generation

| Task | Workflow | Notes |
|------|----------|-------|
| Image to video (1080p quality) | `video_hunyuan_video_1.5_720p_i2v.json` | 8 steps + latent upscale + SR |
| Text to video (1080p quality) | `video_hunyuan_video_1.5_720p_t2v.json` | 8 steps + latent upscale + SR |
| Image to video (Wan 640px) | `video_wan2_2_14B_i2v.json` | 20 steps, CFG=3.5, LightX2V |
| Text to video (Wan 640px) | `video_wan2_2_14B_t2v.json` | 20 steps, CFG=3.5, LightX2V |
| Image to video (Kandinsky 5s) | `video_kandinsky5_i2v.json` | 50 steps, euler_ancestral+beta |
| 6-keyframe interpolation | `templates-6-key-frames.json` | Wan dual-UNET, 5 chained segments |
| Image to video + audio (LTX) | `video_ltx2_i2v.json` | 2-pass + audio, Gemma 3 12B |
| Text to video + audio (LTX) | `video_ltx2_t2v.json` | 2-pass + audio, Gemma 3 12B |
| Canny-guided video | `video_ltx2_canny_to_video.json` | Edge-guided structural video |
| Depth-guided video | `video_ltx2_depth_to_video.json` | Depth-guided structural video |

## Baseline settings

- Fast draft: steps `2-4`, CFG `~1.0`
- Balanced quality: steps `12-20`
- High quality: steps `40-50`, CFG `3-5`
- Typical image output sizes:
  - `1:1` → `1328×1328` (Qwen) / `1024×1024` (Kandinsky)
  - `16:9` → `1664×928`
  - `9:16` → `928×1664`
- Typical video output sizes:
  - `1280×720` → `1920×1080` (HunyuanVideo with upscaler)
  - `768×512` (LTX-2 initial, upscaled in 2nd pass)
  - `640×640` (Wan 2.2)

## Troubleshooting

- Empty output: verify token and endpoint reachability.
- Slow or OOM: reduce resolution/steps, one image per batch.
- Missing nodes/model files: validate names in workflow JSON against ComfyUI model directories.
- Upload failures: confirm image exists and use multipart upload endpoint.
- Video not saving: check that workflow uses `SaveVideo` or `VHS_VideoCombine` output nodes.
- No audio in LTX output: ensure LTXVAudioVAELoader node is connected.

## References

- Full workflow coverage: `WORKFLOWS_SUMMARY.md`
- Skill entry point: `SKILL.md`
