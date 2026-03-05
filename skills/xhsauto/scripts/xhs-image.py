#!/usr/bin/env python3
"""
小红书图片生成工具 - 跨平台 Python 版本
支持文生图和图编辑，兼容 Google Gemini 和 ByteDance Seed
"""

import argparse
import base64
import json
import os
import sys
from pathlib import Path
from typing import Optional

try:
    import requests
except ImportError:
    print("Error: requests library not found. Install with: pip install requests", file=sys.stderr)
    sys.exit(1)


def log_info(msg: str):
    print(f"[xhs-image] {msg}", file=sys.stderr)


def log_error(msg: str):
    print(f"[xhs-image] ERROR: {msg}", file=sys.stderr)


class ImageGenerator:
    RATIO_TO_SIZE = {
        "1:1": "1024x1024",
        "3:4": "1024x1365",
        "4:3": "1365x1024",
        "9:16": "1024x1820",
        "16:9": "1820x1024",
    }

    def __init__(self, provider: str, mode: str, ratio: str):
        self.provider = provider
        self.mode = mode
        self.ratio = ratio
        self.size = self.RATIO_TO_SIZE.get(ratio)
        
        if not self.size:
            raise ValueError(f"Unsupported ratio: {ratio}")
        
        self._setup_api_config()

    def _setup_api_config(self):
        """根据 provider 设置 API 配置"""
        if self.provider == "google":
            self.api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
            self.api_base = os.getenv("GOOGLE_API_BASE") or os.getenv("GEMINI_API_BASE") or \
                           "https://generativelanguage.googleapis.com/openai"
            self.model = os.getenv("GOOGLE_IMAGE_MODEL") or os.getenv("GEMINI_IMAGE_MODEL") or \
                        "gemini-3.1-flash-image-preview"
        elif self.provider == "seed":
            self.api_key = os.getenv("SEED_API_KEY")
            self.api_base = os.getenv("SEED_API_BASE") or "https://seed.bytedanceapi.com"
            self.model = os.getenv("SEED_IMAGE_MODEL") or "bytedance/seed-v1"
        else:
            raise ValueError(f"Unknown provider: {self.provider}")
        
        if not self.api_key:
            raise ValueError(f"API key not set for provider {self.provider}")

    def generate(self, prompt: str, seed: Optional[int] = None) -> bytes:
        """文生图"""
        url = f"{self.api_base.rstrip('/')}/v1/images/generations"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "size": self.size,
            "n": 1,
            "response_format": "b64_json"
        }
        
        if seed is not None:
            payload["seed"] = seed
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        log_info(f"Generating image via {self.provider} ({self.model}) size {self.size}")
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=120)
            response.raise_for_status()
            
            result = response.json()
            b64_data = result["data"][0]["b64_json"]
            return base64.b64decode(b64_data)
        
        except requests.exceptions.RequestException as e:
            log_error(f"API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                log_error(f"Response: {e.response.text}")
            raise

    def edit(self, prompt: str, base_image_path: str, seed: Optional[int] = None) -> bytes:
        """图编辑"""
        url = f"{self.api_base.rstrip('/')}/v1/images/edits"
        
        base_path = Path(base_image_path)
        if not base_path.exists():
            raise FileNotFoundError(f"Base image not found: {base_image_path}")
        
        with open(base_path, "rb") as f:
            image_data = f.read()
        
        files = {
            "image": (base_path.name, image_data, "image/png")
        }
        
        data = {
            "model": self.model,
            "prompt": prompt,
            "size": self.size,
            "n": 1,
            "response_format": "b64_json"
        }
        
        if seed is not None:
            data["seed"] = seed
        
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        log_info(f"Editing image via {self.provider} ({self.model}) size {self.size}")
        
        try:
            response = requests.post(url, data=data, files=files, headers=headers, timeout=120)
            response.raise_for_status()
            
            result = response.json()
            b64_data = result["data"][0]["b64_json"]
            return base64.b64decode(b64_data)
        
        except requests.exceptions.RequestException as e:
            log_error(f"API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                log_error(f"Response: {e.response.text}")
            raise


def main():
    parser = argparse.ArgumentParser(
        description="小红书图片生成工具 - 文生图/图编辑",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
环境变量:
  Google/Gemini:
    GOOGLE_API_KEY 或 GEMINI_API_KEY       (必需)
    GOOGLE_API_BASE 或 GEMINI_API_BASE     (可选, 默认: https://generativelanguage.googleapis.com/openai)
    GOOGLE_IMAGE_MODEL 或 GEMINI_IMAGE_MODEL (可选, 默认: gemini-3.1-flash-image-preview)
  
  ByteDance Seed:
    SEED_API_KEY        (必需)
    SEED_API_BASE       (可选, 默认: https://seed.bytedanceapi.com)
    SEED_IMAGE_MODEL    (可选, 默认: bytedance/seed-v1)

示例:
  # 文生图
  python xhs-image.py --mode generate --prompt "一只可爱的猫" --output cat.png
  
  # 图编辑
  python xhs-image.py --mode edit --prompt "添加温暖的光线" --base-image input.png --output output.png
"""
    )
    
    parser.add_argument("--mode", required=True, choices=["generate", "edit"],
                       help="模式: generate (文生图) 或 edit (图编辑)")
    parser.add_argument("--prompt", required=True,
                       help="图像生成/编辑提示词")
    parser.add_argument("--base-image",
                       help="底图路径 (edit 模式必需)")
    parser.add_argument("--provider", default="google", choices=["google", "seed"],
                       help="图像提供方 (默认: google)")
    parser.add_argument("--ratio", default="1:1",
                       choices=["1:1", "3:4", "4:3", "9:16", "16:9"],
                       help="图片比例 (默认: 1:1)")
    parser.add_argument("--seed", type=int,
                       help="随机种子 (可选)")
    parser.add_argument("--output", required=True,
                       help="输出图片路径")
    
    args = parser.parse_args()
    
    # 验证参数
    if args.mode == "edit" and not args.base_image:
        parser.error("--base-image is required for edit mode")
    
    try:
        # 创建生成器
        generator = ImageGenerator(args.provider, args.mode, args.ratio)
        
        # 生成图片
        if args.mode == "generate":
            image_data = generator.generate(args.prompt, args.seed)
        else:
            image_data = generator.edit(args.prompt, args.base_image, args.seed)
        
        # 保存图片
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "wb") as f:
            f.write(image_data)
        
        log_info(f"Image saved to {output_path.absolute()}")
        
        # 输出 JSON 结果（供脚本解析）
        result = {
            "success": True,
            "output": str(output_path.absolute()),
            "mode": args.mode,
            "provider": args.provider,
            "size": generator.size
        }
        print(json.dumps(result, ensure_ascii=False))
        
        return 0
    
    except Exception as e:
        log_error(str(e))
        result = {
            "success": False,
            "error": str(e)
        }
        print(json.dumps(result, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    sys.exit(main())
