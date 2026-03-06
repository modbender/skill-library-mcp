import urllib.request
import json
import ssl
import sys
import os

def call_nim(model_alias, prompt):
    # 模型映射表
    MODEL_MAP = {
        "glm5": "z-ai/glm5",
        "kimi": "moonshotai/kimi-k2.5",
        "minimax": "minimaxai/minimax-m2.1",
        "llama": "meta/llama-3.1-405b-instruct",
        "phi": "microsoft/phi-4-mini-instruct",
        "r1": "deepseek-ai/deepseek-r1-distill-llama-8b"
    }
    
    model_id = MODEL_MAP.get(model_alias.lower(), model_alias)
    
    # 从环境变量读取 API Key
    api_key = os.getenv("NVIDIA_API_KEY")
    if not api_key:
        return "Error: NVIDIA_API_KEY not found in environment variables."
        
    url = "https://integrate.api.nvidia.com/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model_id,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 2048
    }
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    try:
        req = urllib.request.Request(url, data=json.dumps(data).encode(), headers=headers)
        with urllib.request.urlopen(req, context=ctx) as response:
            result = json.loads(response.read().decode())
            return result['choices'][0]['message']['content']
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 nim_call.py <model_alias> <prompt>")
    else:
        alias = sys.argv[1]
        task = " ".join(sys.argv[2:])
        print(call_nim(alias, task))
