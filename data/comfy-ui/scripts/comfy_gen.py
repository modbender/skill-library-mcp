import json
import urllib.request
import urllib.parse
import sys
import os
import time
import argparse

def generate_image(prompt, server_address, workflow_path=None, checkpoint="SDXL/juggernautXL_ragnarokBy.safetensors"):
    if workflow_path and os.path.exists(workflow_path):
        with open(workflow_path, 'r') as f:
            workflow = json.load(f)
        
        # Smart Injection: Try to find prompt and seed nodes
        found_prompt = False
        for node_id, node in workflow.items():
            # Inject prompt into CLIPTextEncode (usually the first one or one with specific inputs)
            if node.get("class_type") == "CLIPTextEncode" and not found_prompt:
                node["inputs"]["text"] = prompt
                found_prompt = True
            
            # Inject seed into KSampler or similar
            if "seed" in node.get("inputs", {}):
                node["inputs"]["seed"] = int(time.time())
    else:
        # Default Simple SDXL API Workflow
        workflow = {
            "3": {
                "inputs": {
                    "seed": int(time.time()),
                    "steps": 25,
                    "cfg": 7,
                    "sampler_name": "dpmpp_2m",
                    "scheduler": "karras",
                    "denoise": 1,
                    "model": ["4", 0],
                    "positive": ["6", 0],
                    "negative": ["7", 0],
                    "latent_image": ["5", 0]
                },
                "class_type": "KSampler"
            },
            "4": {
                "inputs": {
                    "ckpt_name": checkpoint
                },
                "class_type": "CheckpointLoaderSimple"
            },
            "5": {
                "inputs": {
                    "width": 1024,
                    "height": 1024,
                    "batch_size": 1
                },
                "class_type": "EmptyLatentImage"
            },
            "6": {
                "inputs": {
                    "text": prompt,
                    "clip": ["4", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "7": {
                "inputs": {
                    "text": "text, watermark, low quality, blurry, distorted",
                    "clip": ["4", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "8": {
                "inputs": {
                    "samples": ["3", 0],
                    "vae": ["4", 2]
                },
                "class_type": "VAEDecode"
            },
            "9": {
                "inputs": {
                    "filename_prefix": "OpenClaw",
                    "images": ["8", 0]
                },
                "class_type": "SaveImage"
            }
        }

    p = {"prompt": workflow}
    data = json.dumps(p).encode('utf-8')
    req = urllib.request.Request(f"{server_address}/prompt", data=data)
    
    try:
        with urllib.request.urlopen(req) as f:
            response = json.loads(f.read().decode('utf-8'))
            prompt_id = response['prompt_id']
    except Exception as e:
        print(f"Error connecting to ComfyUI: {e}")
        sys.exit(1)

    # Wait for completion
    while True:
        with urllib.request.urlopen(f"{server_address}/history/{prompt_id}") as f:
            history = json.loads(f.read().decode('utf-8'))
            if prompt_id in history:
                outputs = history[prompt_id]['outputs']
                for node_id in outputs:
                    if 'images' in outputs[node_id]:
                        image_data = outputs[node_id]['images'][0]
                        filename = image_data['filename']
                        subfolder = image_data['subfolder']
                        folder_type = image_data['type']
                        
                        # Download image
                        image_url = f"{server_address}/view?filename={filename}&subfolder={subfolder}&type={folder_type}"
                        image_path = f"image-gens/{filename}"
                        os.makedirs("image-gens", exist_ok=True)
                        urllib.request.urlretrieve(image_url, image_path)
                        return image_path
        time.sleep(2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("prompt", help="The image generation prompt")
    parser.add_argument("server", help="ComfyUI server address")
    parser.add_argument("--workflow", help="Path to workflow JSON file", default=None)
    args = parser.parse_args()
    
    path = generate_image(args.prompt, args.server, args.workflow)
    print(f"MEDIA:{path}")
    print(f"Generated image saved to {path}")
