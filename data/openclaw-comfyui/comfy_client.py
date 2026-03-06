import json
import requests
import sys
import os
import time
import re

# --- DYNAMIC CONFIG ---
# Default values
COMFY_HOST = "127.0.0.1"
COMFY_PORT = "8188"

# Path logic
SKILL_ROOT = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_ROOT = os.path.abspath(os.path.join(SKILL_ROOT, "..", ".."))
TOOLS_PATH = os.path.join(WORKSPACE_ROOT, "TOOLS.md")
OUTPUT_DIR = os.path.join(WORKSPACE_ROOT, "outputs", "comfy")
WORKFLOW_DIR = os.path.join(SKILL_ROOT, "workflows")

# Attempt to read from TOOLS.md to avoid hardcoding (Security Compliance)
if os.path.exists(TOOLS_PATH):
    with open(TOOLS_PATH, 'r') as f:
        content = f.read()
        host_match = re.search(r'Host:\s*([\d\.]+)', content)
        port_match = re.search(r'Port:\s*(\d+)', content)
        if host_match: COMFY_HOST = host_match.group(1)
        if port_match: COMFY_PORT = port_match.group(1)

COMFY_URL = f"http://{COMFY_HOST}:{COMFY_PORT}"

# ALLOWED EXTENSIONS (Security Check)
ALLOWED_EXT = {'.jpg', '.jpeg', '.png', '.webp', '.mp4', '.mov', '.wav', '.mp3'}

WORKFLOW_MAP = {
    "gen_z": os.path.join(WORKFLOW_DIR, "image_z_image_turbo.json"),
    "qwen_edit": os.path.join(WORKFLOW_DIR, "qwen_image_edit_2511.json")
}

os.makedirs(OUTPUT_DIR, exist_ok=True)

def upload_file(input_path):
    ext = os.path.splitext(input_path)[1].lower()
    if ext not in ALLOWED_EXT:
        raise ValueError(f"Security Error: File type {ext} is not allowed.")
    
    with open(input_path, 'rb') as f:
        files = {'image': f} # ComfyUI uses 'image' key for all uploads usually
        res = requests.post(f"{COMFY_URL}/upload/image", files=files)
        return res.json()

def send_prompt(workflow_data):
    p = {"prompt": workflow_data}
    data = json.dumps(p).encode('utf-8')
    res = requests.post(f"{COMFY_URL}/prompt", data=data)
    return res.json()

def check_history(prompt_id):
    res = requests.get(f"{COMFY_URL}/history/{prompt_id}")
    return res.json()

def download_file(filename, subfolder, folder_type):
    url = f"{COMFY_URL}/view?filename={filename}&subfolder={subfolder}&type={folder_type}"
    res = requests.get(url)
    file_path = os.path.join(OUTPUT_DIR, filename)
    with open(file_path, "wb") as f:
        f.write(res.content)
    return file_path

def main():
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Usage: python3 comfy_client.py <template_id> <prompt_text> [input_path/orientation] [orientation]"}))
        return

    template_id = sys.argv[1]
    prompt_text = sys.argv[2]
    
    input_path = None
    orientation = "portrait" 

    for arg in sys.argv[3:]:
        if arg.lower() in ["portrait", "landscape"]:
            orientation = arg.lower()
        elif os.path.exists(arg):
            input_path = arg

    width, height = (720, 1280) if orientation == "portrait" else (1280, 720)

    if template_id not in WORKFLOW_MAP:
        print(json.dumps({"error": f"Unknown template: {template_id}"}))
        return

    with open(WORKFLOW_MAP[template_id], 'r') as f:
        workflow = json.load(f)

    uploaded_filename = None
    if input_path:
        try:
            upload_res = upload_file(input_path)
            uploaded_filename = upload_res.get("name")
        except Exception as e:
            print(json.dumps({"error": str(e)}))
            return

    for node_id in workflow:
        node = workflow[node_id]
        if node.get("class_type") in ["CLIPTextEncode", "TextEncodeQwenImageEditPlus"]:
            if "inputs" in node:
                if "prompt" in node["inputs"]: node["inputs"]["prompt"] = prompt_text
                elif "text" in node["inputs"]: node["inputs"]["text"] = prompt_text
        
        if uploaded_filename and node.get("class_type") == "LoadImage":
            node["inputs"]["image"] = uploaded_filename

        if node.get("class_type") in ["EmptyLatentImage", "LatentImage", "EmptyImage", "EmptySD3LatentImage"]:
            if "inputs" in node:
                node["inputs"]["width"] = width
                node["inputs"]["height"] = height

    prompt_res = send_prompt(workflow)
    prompt_id = prompt_res.get("prompt_id")
    
    if not prompt_id:
        print(json.dumps({"error": "Failed to get prompt_id", "response": prompt_res}))
        return

    print(f"Connected to {COMFY_HOST}:{COMFY_PORT}. Job: {prompt_id}. Waiting...", file=sys.stderr)
    while True:
        history = check_history(prompt_id)
        if prompt_id in history:
            outputs = history[prompt_id].get("outputs", {})
            results = []
            for node_id in outputs:
                if "images" in outputs[node_id]:
                    for img in outputs[node_id]["images"]:
                        local = download_file(img["filename"], img["subfolder"], img["type"])
                        results.append(local)
            
            print(json.dumps({"status": "success", "files": results, "resolution": f"{width}x{height}"}))
            return
        time.sleep(2)

if __name__ == "__main__":
    main()
