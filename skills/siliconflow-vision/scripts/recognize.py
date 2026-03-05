#!/usr/bin/env python3
"""
SiliconFlow 图片识别脚本
被 sub-agent 调用，识别图片内容并输出结果
"""

import argparse
import base64
import json
import os
import sys
from pathlib import Path

import requests


def load_config():
    """加载配置文件"""
    config_path = Path(__file__).parent.parent / "config" / "default.json"
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def encode_image(image_path: str) -> str:
    """将图片编码为 Base64"""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def recognize_image(
    api_key: str,
    image_path: str,
    question: str = "请描述这张图片的内容",
    model: str = "deepseek-ai/deepseek-vl2",
    api_base: str = "https://api.siliconflow.cn/v1",
) -> str:
    """
    调用 SiliconFlow API 识别图片

    Returns:
        识别结果（描述/文字等）
    """
    # 处理图片 URL 或本地路径
    if image_path.startswith(("http://", "https://")):
        image_url = image_path
    else:
        # 本地图片转 Base64
        if not os.path.exists(image_path):
            return f"错误: 图片文件不存在: {image_path}"
        
        image_data = encode_image(image_path)
        mime_type = f"image/{Path(image_path).suffix[1:]}" if Path(image_path).suffix else "image/jpeg"
        image_url = f"data:{mime_type};base64,{image_data}"

    # 构建请求
    messages = [{
        "role": "user",
        "content": [
            {"type": "image_url", "image_url": {"url": image_url}},
            {"type": "text", "text": question}
        ]
    }]

    url = f"{api_base}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": 2048,
        "temperature": 0.7
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=180)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"识别错误: {e}"


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description="SiliconFlow 图片识别")
    parser.add_argument("image", help="图片路径或 URL")
    parser.add_argument("-q", "--question", default="请描述这张图片的内容",
                        help="要识别的问题")
    parser.add_argument("-m", "--model", default="fast",
                        help="模型选择: fast/smart")
    parser.add_argument("--api-key", help="API Key")

    args = parser.parse_args()

    # 获取 API Key
    config = load_config()
    api_key = args.api_key or config.get("api_key") or os.environ.get("SILICONFLOW_API_KEY")

    if not api_key:
        print("错误: 未提供 API Key", file=sys.stderr)
        sys.exit(1)

    # 解析模型
    models = {
        "fast": "deepseek-ai/deepseek-vl2",
        "smart": "Qwen/Qwen2.5-VL-72B-Instruct",
    }
    actual_model = models.get(args.model, args.model)

    # 识别图片
    result = recognize_image(
        api_key=api_key,
        image_path=args.image,
        question=args.question,
        model=actual_model
    )
    print(result)


if __name__ == "__main__":
    main()
