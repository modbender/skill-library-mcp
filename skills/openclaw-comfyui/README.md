# 🦞 OpenClaw-ComfyUI Skill

A professional, token-saving agent skill for controlling ComfyUI through OpenClaw.

## ✨ Features
- **Token Optimization:** Uses Template IDs instead of sending full Workflow JSONs in prompts.
- **Auto-Asset Management:** 
    - Automatically **uploads** input images to ComfyUI remote host.
    - Automatically **polls and downloads** generated results to your local workspace.
- **Multi-Output Support:** Easily send results to Telegram, open on Mac, or display via Canvas.
- **Scalable Architecture:** Add new workflows by simply dropping JSON files into the `workflows/` folder.

## 🚀 Installation

1. Clone this repository into your OpenClaw `skills/` directory:
   ```bash
   cd ~/.openclaw/workspace/skills
   git clone https://github.com/SalmonRK/OpenClaw-ComfyUI comfyui
   ```

2. Install Python dependencies:
   ```bash
   pip3 install requests
   ```

3. Update your `TOOLS.md` in the workspace root:
   ```markdown
   ### ComfyUI
   - Host: <YOUR_COMFY_IP>
   - Port: <YOUR_COMFY_PORT>
   - Workflows Directory: skills/comfyui/workflows/
   - Output Directory: outputs/comfy/
   ```

## 🛠 Usage
The AI Agent can now use this skill by calling the `comfy_client.py` script. 

Example CLI command:
```bash
python3 skills/comfyui/comfy_client.py <template_id> "<prompt>" [input_image_path]
```

## 📂 Project Structure
- `comfy_client.py`: Core logic for API interaction.
- `SKILL.md`: Instructions for the AI Agent.
- `workflows/`: Collection of ComfyUI workflow JSON files.

---
Developed with ❤️ by **SalmonRK** & **Ava (เอวา)** 🎀
