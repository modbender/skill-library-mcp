---
name: comfyui
description: Generate high-quality images using a local ComfyUI instance. Use when the user wants private, powerful image generation via their own hardware and custom workflows. Requires a running ComfyUI server accessible on the local network.
metadata:
  {
    "openclaw":
      {
        "emoji": "🎨",
        "requires": { "env": ["COMFYUI_SERVER_ADDRESS"] },
      },
  }
---

# ComfyUI Local Skill

This skill allows OpenClaw to generate images by connecting to a ComfyUI instance running on the local network.

## Setup

1. **Server Address:** Set the `COMFYUI_SERVER_ADDRESS` environment variable to your PC's IP and port (e.g., `http://192.168.1.119:8189`).
2. **API Mode:** Ensure **"Enable Dev mode"** is turned on in your ComfyUI settings to allow API interactions.
  
## Usage

### Generate an Image
Run the internal generation script with a prompt:
```bash
python3 {skillDir}/scripts/comfy_gen.py "your image prompt" $COMFYUI_SERVER_ADDRESS
```

### Use a Custom Workflow
Place your API JSON workflows in the `workflows/` folder, then specify the path:
```bash
python3 {skillDir}/scripts/comfy_gen.py "your prompt" $COMFYUI_SERVER_ADDRESS --workflow {skillDir}/workflows/my_workflow.json
```

## Features
- **SDXL Default:** Uses a high-quality SDXL workflow (Juggernaut XL) by default.
- **Auto-Backup:** Designed to save images to `image-gens/` and can be configured to sync to local document folders.
- **Custom Workflows:** Supports external API JSON workflows saved in the `workflows/` folder. The script will automatically try to inject your prompt and a random seed into the workflow nodes.

## Implementation Details
The skill uses a Python helper (`scripts/comfy_gen.py`) to handle the WebSocket/HTTP handshake with the ComfyUI API, queue the prompt, and download the resulting image.

## ComfyUI Image Generation Notes:

1.  **Server Address:**
    *   The ComfyUI server address needs to be passed as a direct argument to the `comfy_gen.py` script after the prompt, not just as an environment variable.
    *   Example: `python3 ... "Your prompt" http://192.168.1.119:8189 ...`

2.  **Workflow Paths:**
    *   When specifying a workflow file path that contains spaces or special characters, it must be enclosed in single quotes to be parsed correctly by the script.
    *   Example: `--workflow '/path/to/your/workflow file name.json'`

3.  **Lora Weight Control:**
    *   The current `comfy_gen.py` script does not appear to have a direct parameter for controlling Lora weights (e.g., setting 'l1lly' Lora to 0.90). This might need to be configured within the workflow JSON itself, or require modifications to the script or workflow.

4.  **Output Filenames:**
    *   Generated images might be saved with temporary names (e.g., `ComfyUI_temp_...png`) rather than more descriptive ones by default.

5.  **ComfyUI Setup:**
    *   Ensure "Enable Dev mode" is turned on in ComfyUI settings for API interactions.
