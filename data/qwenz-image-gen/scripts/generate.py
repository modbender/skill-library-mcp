#!/usr/bin/env python3
"""
Qwen-Image / Z-Image 生图脚本
自动判断场景选择模型，人像用 z-image，其他用 qwen-image
"""

import argparse
import os
import sys
import json
import re
from pathlib import Path
import http.client
from urllib.parse import urlparse
from datetime import datetime


def get_api_key() -> str:
    """从环境变量或 TOOLS.md 获取 API Key"""
    # 1. 环境变量
    key = os.environ.get("DASHSCOPE_API_KEY")
    if key:
        return key
    
    # 2. 从 TOOLS.md 读取
    possible_paths = [
        Path(__file__).parent.parent.parent.parent / "TOOLS.md",
        Path.cwd() / "TOOLS.md",
        Path("/home/admin/clawd/TOOLS.md"),
    ]
    
    for path in possible_paths:
        try:
            if path.exists():
                content = path.read_text(encoding="utf-8")
                match = re.search(r'DASHSCOPE_API_KEY:\s*(\S+)', content)
                if match:
                    key = match.group(1)
                    if key and not key.startswith('请在这里'):
                        return key
        except Exception:
            continue
    
    return None


# 人像/照片关键词
PORTRAIT_KEYWORDS = [
    "人", "女", "男", "少女", "帅哥", "美女", "肖像", "portrait", "woman", "man", "girl", "boy",
    "人物", "face", " facial", "selfie", "photo", "photograph", "film grain", "analog",
    "Kodak", "胶片", "portra", "cinematic", "photorealistic", "真实", "写真人像"
]

def is_portrait_prompt(prompt: str) -> bool:
    """判断提示词是否涉及人像/照片场景"""
    prompt_lower = prompt.lower()
    return any(kw in prompt or kw.lower() in prompt_lower for kw in PORTRAIT_KEYWORDS)


# 模型配置
MODELS = {
    "qwen": {
        "name": "qwen-image-max",
        "sizes": {
            "1664*928": (1664, 928),   # 16:9
            "1472*1104": (1472, 1104), # 4:3
            "1328*1328": (1328, 1328), # 1:1
            "1104*1472": (1104, 1472), # 3:4
            "928*1664": (928, 1664),   # 9:16
        },
        "default_size": "1328*1328"
    },
    "z": {
        "name": "z-image-turbo",
        "sizes": {
            "1120*1440": (1120, 1440), # 人像推荐
            "1664*928": (1664, 928),
            "1328*1328": (1328, 1328),
        },
        "default_size": "1120*1440"
    }
}


def parse_size(size_str: str) -> tuple:
    """解析尺寸字符串，返回 (width, height)"""
    parts = size_str.split("*")
    if len(parts) == 2:
        return int(parts[0]), int(parts[1])
    return 1328, 1328


def generate_image(
    prompt: str,
    model_type: str = "auto",
    size: str = None,
    prompt_extend: int = 0,
    watermark: bool = False,
    output: str = None
) -> str:
    """
    生成图片
    
    Args:
        prompt: 提示词
        model_type: auto/qwen/z | auto 自动判断
        size: 尺寸
        prompt_extend: 是否扩展提示词 (0/1)
        watermark: 是否添加水印
        output: 输出路径
    """
    api_key = get_api_key()
    if not api_key:
        print("❌ 错误: 未设置 DASHSCOPE_API_KEY 环境变量")
        print("请设置: export DASHSCOPE_API_KEY='your-api-key'")
        sys.exit(1)
    
    # 判断模型
    if model_type == "auto":
        if is_portrait_prompt(prompt):
            model_config = MODELS["z"]
            model_type = "z"
            print("🔍 检测到人像/照片场景，自动使用 z-image 模型")
        else:
            model_config = MODELS["qwen"]
            model_type = "qwen"
    else:
        model_config = MODELS.get(model_type, MODELS["qwen"])
    
    # 确定尺寸
    if size and size in model_config["sizes"]:
        size_str = size
    else:
        size_str = model_config["default_size"]
    width, height = model_config["sizes"][size_str]
    
    # 构建请求体 (messages 格式)
    payload = {
        "model": model_config["name"],
        "input": {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ]
        },
        "parameters": {
            "size": size_str,
            "prompt_extend": bool(prompt_extend),
            "watermark": watermark
        }
    }
    
    # 人像类添加额外参数
    if model_type == "z" and "film grain" not in prompt.lower():
        # 自动添加胶片效果，除非用户已指定
        pass  # 可选：可以自动增强提示词
    
    print(f"🎨 正在生成图片...")
    print(f"   模型: {model_config['name']}")
    print(f"   尺寸: {size_str} ({width}x{height})")
    print(f"   提示词: {prompt[:60]}{'...' if len(prompt) > 60 else ''}")
    
    # 发送请求
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        conn = http.client.HTTPSConnection("dashscope.aliyuncs.com", timeout=120)
        conn.request(
            "POST",
            "/api/v1/services/aigc/multimodal-generation/generation",
            body=json.dumps(payload),
            headers=headers
        )
        
        response = conn.getresponse()
        data = response.read().decode("utf-8")
        
        if response.status != 200:
            print(f"❌ HTTP 错误 {response.status}: {data}")
            sys.exit(1)
        
        result = json.loads(data)
        
        # 解析响应: output.choices[0].message.content[0].image
        if "output" in result and "choices" in result["output"]:
            choice = result["output"]["choices"][0]
            content = choice["message"]["content"]
            
            # 找到 image
            image_url = None
            for item in content:
                if "image" in item:
                    image_url = item["image"]
                    break
            
            if not image_url:
                print(f"❌ 未找到图片 URL: {result}")
                sys.exit(1)
            
            # 确定输出文件名
            if not output:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output = f"{model_type}_image_{timestamp}.png"
            
            # 下载图片
            print(f"⬇️  下载图片...")
            parsed = urlparse(image_url)
            img_conn = http.client.HTTPSConnection(parsed.netloc, timeout=60)
            img_conn.request("GET", parsed.path + (f"?{parsed.query}" if parsed.query else ""))
            img_resp = img_conn.getresponse()
            
            with open(output, "wb") as f:
                f.write(img_resp.read())
            img_conn.close()
            
            print(f"✅ 图片已保存: {os.path.abspath(output)}")
            conn.close()
            return output
        
        print(f"❌ API 返回异常: {result}")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="使用 Qwen-Image / Z-Image 模型生成图片",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 自动判断模型
  python generate.py "一只可爱的橘猫"
  
  # 指定人像模式 (z-image)
  python generate.py "短发少女" --model z --size 1120*1440
  
  # 通用模式 (qwen-image)
  python generate.py "赛博朋克城市" --model qwen --size 1664*928
        """
    )
    
    parser.add_argument("prompt", help="图片生成提示词（支持中文）")
    parser.add_argument("--model", default="auto", choices=["auto", "qwen", "z"],
                        help="模型选择 (auto/qwen/z, 默认 auto)")
    parser.add_argument("--size", help="图片尺寸 (如: 1664*928, 1120*1440)")
    parser.add_argument("--extend", action="store_true",
                        help="开启提示词扩展")
    parser.add_argument("--watermark", action="store_true",
                        help="添加水印")
    parser.add_argument("--output", "-o", help="输出文件路径")
    
    args = parser.parse_args()
    
    generate_image(
        prompt=args.prompt,
        model_type=args.model,
        size=args.size,
        prompt_extend=args.extend,
        watermark=args.watermark,
        output=args.output
    )


if __name__ == "__main__":
    main()
