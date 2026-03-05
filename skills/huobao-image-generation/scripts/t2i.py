#!/usr/bin/env python3
"""
火山引擎 AI 文生图脚本
用法: python3 t2i.py "提示词" [选项]
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error


API_URL = "https://api.chatfire.site/v1/images/generations"

# 支持的模型
MODELS = [
    "gemini-2.5-flash-image",
    "gemini-2.5-flash-image-preview",
    "nano-banana",
    "nano-banana-pro",
    "nano-banana-pro_4k",
    "doubao-seedream-4-5-251128"
]

# 支持的尺寸
SIZES = ["1x1", "16x9", "9x16", "3x4", "4x3"]


def get_api_key():
    """获取 API Key"""
    api_key = os.environ.get("HUOBAO_API_KEY")
    if not api_key:
        # 尝试从参数获取
        for i, arg in enumerate(sys.argv):
            if arg == "--api-key" and i + 1 < len(sys.argv):
                return sys.argv[i + 1]
        print("Error: 请设置环境变量 HUOBAO_API_KEY 或使用 --api-key 参数", file=sys.stderr)
        sys.exit(1)
    return api_key


def text2image(prompt, model="nano-banana-pro", size="1x1", count=1, watermark=True, api_key=None, debug=False):
    """文生图"""
    if api_key is None:
        api_key = get_api_key()
    
    # 验证模型
    if model not in MODELS:
        print(f"Warning: 模型 {model} 不在已知列表中，继续尝试...", file=sys.stderr)
    
    # 构建请求体
    body = {
        "model": model,
        "prompt": prompt,
        "response_format": "url",
        "size": size,
        "stream": False,
        "watermark": watermark
    }
    
    if count > 1:
        body["sequential_image_generation"] = "auto"
        body["sequential_image_generation_options"] = {"max_images": count}
    
    if debug:
        print(f"提示词: {prompt}", file=sys.stderr)
        print(f"模型: {model}", file=sys.stderr)
        print(f"尺寸: {size}", file=sys.stderr)
        print(f"数量: {count}", file=sys.stderr)
        print(f"请求体: {json.dumps(body, ensure_ascii=False)}", file=sys.stderr)
    
    # 发送请求
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        },
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"HTTP Error {e.code}: {error_body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Network Error: {e.reason}", file=sys.stderr)
        sys.exit(1)
    
    # 解析结果
    if "data" in result and len(result["data"]) > 0:
        images = []
        for img in result["data"]:
            images.append({
                "url": img.get("url", "")
            })
        
        output = {
            "success": True,
            "prompt": prompt,
            "model": model,
            "size": size,
            "count": len(images),
            "images": images,
            "usage": result.get("usage", {})
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print(json.dumps({"success": False, "error": "No images returned"}, ensure_ascii=False, indent=2))
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="火山引擎 AI 文生图")
    parser.add_argument("prompt", help="图片描述提示词")
    parser.add_argument("--model", "-m", default="nano-banana-pro", help=f"模型名称 (默认: nano-banana-pro)")
    parser.add_argument("--size", "-s", default="1x1", choices=SIZES, help=f"尺寸 (默认: 1x1)")
    parser.add_argument("--count", "-c", type=int, default=1, help="生成数量 1-4 (默认: 1)")
    parser.add_argument("--watermark", "-w", type=bool, default=True, help="是否添加水印 (默认: True)")
    parser.add_argument("--api-key", "-k", help="API Key")
    parser.add_argument("--debug", "-d", action="store_true", help="调试模式")
    
    args = parser.parse_args()
    
    text2image(
        prompt=args.prompt,
        model=args.model,
        size=args.size,
        count=args.count,
        watermark=args.watermark,
        api_key=args.api_key,
        debug=args.debug
    )


if __name__ == "__main__":
    main()
