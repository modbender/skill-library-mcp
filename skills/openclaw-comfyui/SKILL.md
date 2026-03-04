# ComfyUI-OpenClaw Skill 🎨✨

A professional, token-saving agent skill for connecting and controlling ComfyUI via API. Designed for high efficiency, automatic asset handling, and seamless integration with OpenClaw.

## 🏗️ Skill Structure
- **Host Address:** `192.168.1.38:8190` (Configured in `TOOLS.md`)
- **Workflow Directory:** `skills/comfyui/workflows/` (Self-contained within the skill folder)
- **Output Directory:** `outputs/comfy/` (Relative to workspace root)
- **Core Script:** `skills/comfyui/comfy_client.py` (Handles prompt injection, image uploads, and result polling)

## 🛠️ Tools (CLI)
Invoke via the `exec` command:
`python3 skills/comfyui/comfy_client.py <template_id> "<prompt>" [input_image_path/orientation] [orientation]`

### Parameters:
- **template_id:**
    1. `gen_z`: Text-to-Image (uses `image_z_image_turbo.json`)
    2. `qwen_edit`: Image-to-Image / Editing (uses `qwen_image_edit_2511.json`) - *Supports automatic image upload.*
- **prompt:** The description of the image to generate or edits to perform.
- **input_image_path:** (Optional) Local path for image-to-image tasks.
- **orientation:** (Optional) Set to `portrait` (720x1280) or `landscape` (1280x720). Defaults to `portrait`.

## 💡 How to Add New Workflows
You can expand this skill easily:
1. Place your new API-formatted JSON workflow in `skills/comfyui/workflows/`.
2. Update the `WORKFLOW_MAP` dictionary in `skills/comfyui/comfy_client.py` with a new ID and the file path.
3. (Optional) If the workflow uses unique node types, adjust the injection logic in the script's `main()` function.

## 🚀 Token-Saving Strategy
- **Template Mapping:** Never send full workflow JSONs in the chat. Refer to them by `template_id`.
- **Vision-Saving Strategy:** To minimize token usage, the agent should prioritize using the **file path from metadata** instead of analyzing image content via vision capabilities unless explicitly asked to describe or analyze the image.
- **Direct Delivery:** Deliver images directly to users via messaging plugins (e.g., Telegram) or local file openers (`open`) to avoid bloating the LLM's context window with base64 data.
