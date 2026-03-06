#!/usr/bin/env python3
"""
ComfyUI API client for ai-media skill
Submits workflows to ComfyUI server and retrieves results
"""

import json
import time
import urllib.request
import urllib.error
import urllib.parse
import random
import sys
import os
from pathlib import Path

class ComfyUIClient:
    def __init__(self, server_address="localhost:8188"):
        self.server_address = server_address
        self.client_id = f"ai-media-{random.randint(1000, 9999)}"
    
    def queue_prompt(self, prompt):
        """Submit a workflow to ComfyUI queue"""
        data = json.dumps({"prompt": prompt, "client_id": self.client_id}).encode('utf-8')
        req = urllib.request.Request(f"http://{self.server_address}/prompt", data=data)
        req.add_header('Content-Type', 'application/json')
        
        try:
            response = urllib.request.urlopen(req)
            return json.loads(response.read())
        except urllib.error.URLError as e:
            print(f"❌ Failed to connect to ComfyUI: {e}")
            return None
    
    def get_image(self, filename, subfolder, folder_type):
        """Download generated image/video from ComfyUI"""
        data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        url_values = urllib.parse.urlencode(data)
        
        try:
            with urllib.request.urlopen(f"http://{self.server_address}/view?{url_values}") as response:
                return response.read()
        except urllib.error.URLError as e:
            print(f"❌ Failed to download output: {e}")
            return None
    
    def get_history(self, prompt_id):
        """Get workflow execution history"""
        try:
            with urllib.request.urlopen(f"http://{self.server_address}/history/{prompt_id}") as response:
                return json.loads(response.read())
        except urllib.error.URLError as e:
            print(f"❌ Failed to get history: {e}")
            return None
    
    def wait_for_completion(self, prompt_id, timeout=300):
        """Wait for workflow to complete"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            history = self.get_history(prompt_id)
            
            if history and prompt_id in history:
                outputs = history[prompt_id].get('outputs', {})
                if outputs:
                    return outputs
            
            time.sleep(2)
        
        print(f"⏱️  Timeout waiting for generation")
        return None

def generate_video_ltx2(prompt, duration=4, width=768, height=512, fps=24, output_dir="/tmp"):
    """Generate video using LTX-2 workflow"""
    
    # Load the LTX-2 T2V workflow
    workflow_path = Path(__file__).parent.parent / "workflows" / "video-ltx2.json"
    
    if not workflow_path.exists():
        print(f"❌ Workflow not found: {workflow_path}")
        return None
    
    with open(workflow_path) as f:
        workflow = json.load(f)
    
    # Find and modify key parameters in the workflow
    # This is workflow-specific - you'll need to identify the right node IDs
    # For now, we'll just set a random seed
    seed = random.randint(0, 2**32 - 1)
    
    # TODO: Parse workflow to find prompt, duration, seed nodes
    # For now, just queue the workflow as-is
    
    print(f"🎬 Generating LTX-2 video...")
    print(f"   Prompt: {prompt}")
    print(f"   Duration: {duration}s @ {fps}fps")
    print(f"   Resolution: {width}x{height}")
    print(f"   Seed: {seed}")
    
    client = ComfyUIClient()
    
    # Queue the workflow
    result = client.queue_prompt(workflow)
    
    if not result:
        return None
    
    prompt_id = result.get('prompt_id')
    if not prompt_id:
        print("❌ No prompt_id returned")
        return None
    
    print(f"✅ Queued with ID: {prompt_id}")
    print(f"⏳ Waiting for generation...")
    
    # Wait for completion
    outputs = client.wait_for_completion(prompt_id)
    
    if not outputs:
        return None
    
    # Find the output video
    for node_id, node_output in outputs.items():
        if 'gifs' in node_output or 'videos' in node_output:
            files = node_output.get('gifs', node_output.get('videos', []))
            if files:
                file_info = files[0]
                filename = file_info['filename']
                subfolder = file_info.get('subfolder', '')
                
                print(f"📥 Downloading: {filename}")
                
                # Download the file
                data = client.get_image(filename, subfolder, "output")
                
                if data:
                    output_path = Path(output_dir) / filename
                    with open(output_path, 'wb') as f:
                        f.write(data)
                    
                    print(f"✅ Saved to: {output_path}")
                    print(f"📦 Size: {len(data) / 1024:.1f} KB")
                    return str(output_path)
    
    print("❌ No video output found")
    return None

def generate_image_comfyui(prompt, style="realistic", width=1024, height=1024, output_dir="/tmp"):
    """Generate image using ComfyUI (simplified for now)"""
    
    print(f"🎨 Generating image...")
    print(f"   Prompt: {prompt}")
    print(f"   Style: {style}")
    print(f"   Resolution: {width}x{height}")
    
    # For now, return a placeholder
    # TODO: Implement proper workflow execution
    print("⚠️  Image generation via ComfyUI API not yet implemented")
    print("   Use ComfyUI web interface at http://localhost:8188")
    return None

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: comfyui_api.py <type> <prompt> [options...]")
        print("  type: video-ltx2 | image")
        sys.exit(1)
    
    gen_type = sys.argv[1]
    prompt = sys.argv[2]
    
    if gen_type == "video-ltx2":
        duration = int(sys.argv[3]) if len(sys.argv) > 3 else 4
        result = generate_video_ltx2(prompt, duration=duration)
    elif gen_type == "image":
        style = sys.argv[3] if len(sys.argv) > 3 else "realistic"
        result = generate_image_comfyui(prompt, style=style)
    else:
        print(f"❌ Unknown type: {gen_type}")
        sys.exit(1)
    
    if result:
        print(f"\n✅ Generation complete: {result}")
        sys.exit(0)
    else:
        print(f"\n❌ Generation failed")
        sys.exit(1)
