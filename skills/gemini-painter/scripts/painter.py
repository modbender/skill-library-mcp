import base64
import json
import os
import sys
import requests
import time
from datetime import datetime
from pathlib import Path

# Configuration
BASE_URL = "http://127.0.0.1:8317/v1"
API_KEY = "OpenClaw"
MODEL = "gemini-3-pro-image"

def generate_image(prompt, output_path=None):
    """
    使用 Gemini Imagen 3 接口生成图片
    """
    url = f"{BASE_URL}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": f"Generate an image: {prompt}"
            }
        ]
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=120)
        if response.status_code != 200:
            return {"status": "error", "message": f"API returned status {response.status_code}"}
        
        data = response.json()
        
        # 提取图片数据 (Gemini 响应格式)
        if "choices" in data and len(data["choices"]) > 0:
            message = data["choices"][0].get("message", {})
            images = message.get("images", [])
            
            if images and len(images) > 0:
                img_url_data = images[0].get("image_url", {}).get("url", "")
                if img_url_data.startswith("data:image"):
                    b64_data = img_url_data.split(",", 1)[1]
                    image_bytes = base64.b64decode(b64_data)
                    
                    # 确定保存路径
                    if not output_path:
                        home_dir = os.environ.get("USERPROFILE", "C:\\Users\\10784")
                        filename = f"gen_{int(time.time())}.jpg"
                        output_path = os.path.join(home_dir, ".openclaw", "workspace", "archives", "images", filename)
                    
                    # 确保目录存在
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    
                    with open(output_path, "wb") as f:
                        f.write(image_bytes)
                    
                    return {
                        "status": "success", 
                        "path": output_path, 
                        "prompt": prompt,
                        "timestamp": datetime.now().isoformat()
                    }
        
        return {"status": "error", "message": "No image found in API response"}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    if len(sys.argv) > 1:
        prompt = sys.argv[1]
        result = generate_image(prompt)
        print(json.dumps(result, ensure_ascii=False))
