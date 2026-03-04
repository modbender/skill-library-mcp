#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "google-genai>=1.0.0",
#     "pillow>=10.0.0",
# ]
# ///
"""
Fashion Colorize Shell runner.

- Fixed provider endpoint + model defaults
- User-provided GEMINI_API_KEY only
- Sketch-first structure preservation
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

from google import genai
from google.genai import types
from PIL import Image as PILImage

FIXED_BASE_URL = "https://models.kapon.cloud"
PRIMARY_MODEL = "gemini-3-pro-image-preview-2k"
FALLBACK_MODEL = "gemini-3-pro-image-preview"


def build_prompt(brief: str, variant: str) -> str:
    return (
        "【上色稿模式】将服装线稿转换为电商成衣效果图。"
        "输出要求：单件冲锋衣正视图、纯白背景、居中陈列、真实产品摄影质感。"
        "材质要求：三层压胶硬壳，体现防水压胶与结构缝位。"
        "版型要求：女性剪裁，保留线稿关键结构（帽型、前中拉链、胸前斜向口袋线、袖口调节、下摆轮廓）。"
        "约束：不要人物，不要场景，不要文字，不要技术多视图。"
        f"用户需求：{brief}。"
        f"当前变体偏好：{variant}。"
    )


def save_response_image(response, output_path: Path) -> bool:
    from io import BytesIO

    for part in response.parts:
        if part.inline_data is None:
            continue
        image_data = part.inline_data.data
        if isinstance(image_data, str):
            import base64

            image_data = base64.b64decode(image_data)

        image = PILImage.open(BytesIO(image_data))
        if image.mode == "RGBA":
            rgb_image = PILImage.new("RGB", image.size, (255, 255, 255))
            rgb_image.paste(image, mask=image.split()[3])
            rgb_image.save(str(output_path), "PNG")
        elif image.mode == "RGB":
            image.save(str(output_path), "PNG")
        else:
            image.convert("RGB").save(str(output_path), "PNG")
        return True
    return False


def run_single(client: genai.Client, prompt: str, images: list[PILImage.Image], resolution: str):
    contents = [*images, prompt]
    try:
        return client.models.generate_content(
            model=PRIMARY_MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"],
                image_config=types.ImageConfig(image_size=resolution),
            ),
        )
    except Exception:
        return client.models.generate_content(
            model=FALLBACK_MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"],
                image_config=types.ImageConfig(image_size=resolution),
            ),
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Colorize fashion shell sketch into ecommerce render")
    parser.add_argument("--sketch", required=True, help="Sketch image path")
    parser.add_argument("--brief", required=True, help="Design brief text")
    parser.add_argument("--style-ref", action="append", default=[], help="Optional style reference image")
    parser.add_argument("--output-dir", required=True, help="Output directory")
    parser.add_argument("--count", type=int, default=3, help="Number of outputs (default: 3)")
    parser.add_argument("--resolution", choices=["1K", "2K", "4K"], default="2K")
    args = parser.parse_args()

    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        print("Missing GEMINI_API_KEY. Please set it before running.", file=sys.stderr)
        return 2

    sketch_path = Path(args.sketch).expanduser().resolve()
    if not sketch_path.exists():
        print(f"Sketch not found: {sketch_path}", file=sys.stderr)
        return 2

    style_paths = [Path(p).expanduser().resolve() for p in args.style_ref]
    for p in style_paths:
        if not p.exists():
            print(f"Style reference not found: {p}", file=sys.stderr)
            return 2

    out_dir = Path(args.output_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    images = [PILImage.open(str(sketch_path))]
    for p in style_paths:
        images.append(PILImage.open(str(p)))

    client = genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(base_url=FIXED_BASE_URL),
    )

    variants = [
        "平衡款：结构还原与商业质感均衡",
        "商业款：材质质感和五金细节更强",
        "设计款：结构线与版型逻辑更突出",
    ]

    total = max(1, min(args.count, 6))
    stamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    for idx in range(total):
        variant = variants[idx % len(variants)]
        prompt = build_prompt(args.brief, variant)
        response = run_single(client, prompt, images, args.resolution)
        output_path = out_dir / f"{stamp}-colorized-v{idx + 1}.png"
        ok = save_response_image(response, output_path)
        if not ok:
            print(f"No image generated for v{idx + 1}", file=sys.stderr)
            continue
        print(f"Image saved: {output_path}")
        print(f"MEDIA: {output_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
