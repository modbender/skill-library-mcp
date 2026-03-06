#!/usr/bin/env python3
"""
AI content generation for Xiaohongshu — generates copywriting via OpenClaw Gateway
(Claude Sonnet 4.5) and images via NanoBanana Pro (Gemini 3 Pro Image).

Usage:
    uv run --project $XHS_TOOLKIT_DIR xhs_generate_content.py \
        --topic "AI学习入门" --style "干货分享" --image-count 4

    uv run --project $XHS_TOOLKIT_DIR xhs_generate_content.py \
        --trending-file data/trending/2025-01-01_综合.json
"""

import argparse
import base64
import json
import os
import sys
import time
from datetime import datetime
from io import BytesIO
from pathlib import Path


STYLE_PROMPTS = {
    "干货分享": "专业知识分享风格，条理清晰，用数据和事实说话，适当使用 emoji 增加可读性",
    "种草推荐": "真诚推荐风格，从个人使用体验出发，突出产品/服务的亮点和实际效果",
    "经验分享": "过来人的口吻，分享踩坑经历和实用技巧，亲切自然",
    "教程攻略": "手把手教学风格，步骤清晰，图文并茂，新手友好",
    "生活记录": "记录生活的美好瞬间，文字温暖有感染力，配图精致",
}

XHS_COPYWRITING_PROMPT = """你是一个专业的小红书内容创作者。请根据以下要求生成一篇小红书笔记。

主题：{topic}
风格：{style_desc}
{trending_context}

要求：
1. 标题：吸引眼球，10-25字，可以用 emoji，要有关键词
2. 正文：300-800字，分段清晰，适当使用 emoji，符合小红书的阅读习惯
3. 话题标签：5-8个相关话题，每个2-6字
4. 图片描述：为每张配图写一段英文描述（用于 AI 图片生成），要具体、有画面感、适合小红书风格

请严格按以下 JSON 格式输出（不要包含 markdown 代码块标记）：
{{
    "title": "标题",
    "content": "正文内容（包含 emoji 和换行）",
    "topics": ["话题1", "话题2", "话题3", "话题4", "话题5"],
    "image_prompts": [
        "English description for image 1, detailed and specific",
        "English description for image 2, detailed and specific"
    ]
}}

注意：
- image_prompts 数量要求：{image_count} 张
- 标题不超过 50 字
- 正文不超过 1000 字
- 每个话题不超过 20 字
- 图片描述要用英文，要具体到颜色、构图、风格
"""


def extract_json(text: str) -> dict:
    """Robustly extract a JSON object from LLM output."""
    import re

    text = text.strip()

    # Strip markdown code fences
    if text.startswith("```"):
        lines = text.split("\n")
        # Remove first line (```json or ```) and last ``` line
        end = len(lines)
        for i in range(len(lines) - 1, 0, -1):
            if lines[i].strip() == "```":
                end = i
                break
        text = "\n".join(lines[1:end]).strip()

    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try fixing common LLM JSON issues (unescaped quotes, trailing commas, etc.)
    try:
        return json.loads(_fix_json(text))
    except (json.JSONDecodeError, Exception):
        pass

    # Try to find a JSON object with regex (first { to last })
    match = re.search(r'\{', text)
    if match:
        start = match.start()
        # Find the matching closing brace
        depth = 0
        for i in range(start, len(text)):
            if text[i] == '{':
                depth += 1
            elif text[i] == '}':
                depth -= 1
                if depth == 0:
                    candidate = text[start:i + 1]
                    try:
                        return json.loads(candidate)
                    except json.JSONDecodeError:
                        # Try fixing common issues
                        fixed = _fix_json(candidate)
                        try:
                            return json.loads(fixed)
                        except json.JSONDecodeError:
                            pass
                    break

    raise ValueError(f"无法从 LLM 输出中解析 JSON（长度 {len(text)}）")


def _fix_json(text: str) -> str:
    """Attempt to fix common JSON issues from LLM output."""
    import re
    # Remove trailing commas before } or ]
    text = re.sub(r',\s*([}\]])', r'\1', text)

    # Fix unescaped double quotes inside JSON string values.
    # Strategy: a structural quote is followed by : , } ] or preceded by { [ , :
    # A non-structural quote inside a value should be escaped.
    # We walk char-by-char tracking whether we're inside a JSON string.
    result = []
    i = 0
    in_string = False
    while i < len(text):
        ch = text[i]

        if not in_string:
            result.append(ch)
            if ch == '"':
                in_string = True
            i += 1
            continue

        # We are inside a string
        if ch == '\\':
            # Escape sequence — consume next char too
            result.append(ch)
            if i + 1 < len(text):
                i += 1
                result.append(text[i])
            i += 1
            continue

        if ch == '\n':
            result.append('\\n')
            i += 1
            continue

        if ch == '"':
            # Is this a closing structural quote or an unescaped quote in content?
            # Look ahead: structural close is followed by optional whitespace then , : } ]
            rest = text[i + 1:].lstrip()
            if not rest or rest[0] in (',', ':', '}', ']'):
                # Structural closing quote
                result.append(ch)
                in_string = False
            else:
                # Unescaped quote inside string value — escape it
                result.append('\\"')
            i += 1
            continue

        result.append(ch)
        i += 1

    return ''.join(result)


def generate_copywriting(topic: str, style: str, image_count: int,
                         trending_context: str = "") -> dict:
    """Generate copywriting via OpenClaw Gateway API (Claude Sonnet 4.5)."""
    import requests as req

    gateway_token = os.environ.get("OPENCLAW_GATEWAY_TOKEN", "")
    gateway_port = 18789
    gateway_url = f"http://127.0.0.1:{gateway_port}/v1/chat/completions"

    style_desc = STYLE_PROMPTS.get(style, STYLE_PROMPTS["干货分享"])

    prompt = XHS_COPYWRITING_PROMPT.format(
        topic=topic,
        style_desc=style_desc,
        trending_context=trending_context,
        image_count=image_count,
    )

    payload = {
        "model": "anthropic/claude-sonnet-4.5",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.8,
        "max_tokens": 2000,
    }

    headers = {
        "Content-Type": "application/json",
    }
    if gateway_token:
        headers["Authorization"] = f"Bearer {gateway_token}"

    print(json.dumps({"step": "copywriting", "status": "generating", "message": "正在生成文案..."}))
    sys.stdout.flush()

    resp = req.post(gateway_url, headers=headers, json=payload, timeout=120)

    if resp.status_code != 200:
        raise RuntimeError(f"Gateway API error {resp.status_code}: {resp.text[:500]}")

    data = resp.json()
    content = data["choices"][0]["message"]["content"]

    result = extract_json(content)

    # Validate
    if len(result.get("title", "")) > 50:
        result["title"] = result["title"][:50]
    if len(result.get("content", "")) > 1000:
        result["content"] = result["content"][:1000]
    result["topics"] = result.get("topics", [])[:10]
    result["image_prompts"] = result.get("image_prompts", [])[:image_count]

    return result


def generate_images(image_prompts: list[str], output_dir: Path) -> list[str]:
    """Generate images via configurable API (any OpenAI-compatible image generation endpoint)."""
    import requests as req

    api_key = os.environ.get("IMAGE_API_KEY", "")
    base_url = os.environ.get("IMAGE_BASE_URL", "")
    model = os.environ.get("IMAGE_MODEL", "")

    if not api_key or not base_url or not model:
        missing = [v for v, val in [("IMAGE_API_KEY", api_key), ("IMAGE_BASE_URL", base_url), ("IMAGE_MODEL", model)] if not val]
        raise RuntimeError(f"Missing required env vars for image generation: {', '.join(missing)}. "
                           f"Set them in your OpenClaw skill config.")

    # Normalize base_url: ensure it ends with /chat/completions
    if not base_url.endswith("/chat/completions"):
        base_url = base_url.rstrip("/")
        if base_url.endswith("/v1"):
            base_url += "/chat/completions"
        else:
            base_url = base_url + "/v1/chat/completions"

    url = base_url

    output_dir.mkdir(parents=True, exist_ok=True)
    image_paths = []

    for i, prompt in enumerate(image_prompts):
        print(json.dumps({
            "step": "image_generation",
            "status": "generating",
            "message": f"正在生成第 {i + 1}/{len(image_prompts)} 张图片...",
            "prompt": prompt[:100],
        }))
        sys.stdout.flush()

        enhanced_prompt = (
            f"Create a beautiful, high-quality image suitable for Xiaohongshu (Little Red Book) social media post. "
            f"Style: clean, aesthetic, Instagram-worthy. {prompt}"
        )

        payload = {
            "model": model,
            "messages": [{"role": "user", "content": enhanced_prompt}],
            "max_tokens": 4096,
        }

        # Gemini models on OpenRouter require modalities param for image output
        if "gemini" in model.lower():
            payload["modalities"] = ["image", "text"]

        max_retries = 2
        for attempt in range(max_retries + 1):
            try:
                resp = req.post(
                    url,
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                    timeout=180,
                )

                if resp.status_code != 200:
                    print(json.dumps({
                        "step": "image_generation",
                        "status": "warning",
                        "message": f"第 {i + 1} 张图片 HTTP {resp.status_code}，{'重试' if attempt < max_retries else '跳过'}。",
                    }), file=sys.stderr)
                    if attempt < max_retries:
                        time.sleep(3)
                        continue
                    break

                # Parse raw bytes to avoid any library-level truncation
                data = json.loads(resp.content)
                message = data["choices"][0]["message"]
                image_saved = False
                output_path = output_dir / f"image_{i + 1}.png"

                # Method 1: OpenRouter style — images in message.images array
                images_list = message.get("images", [])
                for img_obj in images_list:
                    url_str = ""
                    if isinstance(img_obj, dict):
                        url_str = img_obj.get("image_url", {}).get("url", "")
                    if url_str.startswith("data:"):
                        b64 = url_str.split(",", 1)[1]
                        save_image(base64.b64decode(b64), output_path)
                        image_saved = True
                        break

                # Method 2: content is a list of parts (NanoBanana / Gemini style)
                if not image_saved:
                    content = message.get("content", "")
                    if isinstance(content, list):
                        for part in content:
                            if isinstance(part, dict):
                                b64 = None
                                if part.get("type") == "image":
                                    img_data = part.get("image", {})
                                    b64 = img_data.get("data") or img_data.get("b64_json", "")
                                elif part.get("type") == "image_url":
                                    u = part.get("image_url", {}).get("url", "")
                                    if u.startswith("data:"):
                                        b64 = u.split(",", 1)[1]
                                elif part.get("inline_data"):
                                    b64 = part["inline_data"].get("data", "")
                                if b64:
                                    save_image(base64.b64decode(b64), output_path)
                                    image_saved = True
                                    break
                    # Method 3: content is a string with an image URL
                    elif isinstance(content, str) and content:
                        import re
                        md_match = re.search(r'!\[.*?\]\((https?://[^\s)]+)\)', content)
                        url_match = md_match or re.search(r'(https?://\S+\.(?:png|jpg|jpeg|webp|gif))', content)
                        if url_match:
                            img_url = md_match.group(1) if md_match else url_match.group(1)
                            img_resp = req.get(img_url, timeout=60, allow_redirects=True)
                            if img_resp.status_code == 200:
                                save_image(img_resp.content, output_path)
                                image_saved = True

                if image_saved:
                    image_paths.append(str(output_path))
                    break  # success, exit retry loop
                elif attempt < max_retries:
                    print(json.dumps({
                        "step": "image_generation",
                        "status": "warning",
                        "message": f"第 {i + 1} 张图片响应无图像数据（keys: {list(message.keys())}），重试...",
                    }), file=sys.stderr)
                    time.sleep(3)
                    continue
                else:
                    print(json.dumps({
                        "step": "image_generation",
                        "status": "warning",
                        "message": f"第 {i + 1} 张图片 {max_retries + 1} 次尝试均未获取到图像。",
                    }), file=sys.stderr)

            except Exception as e:
                if attempt < max_retries:
                    time.sleep(3)
                    continue
                print(json.dumps({
                    "step": "image_generation",
                    "status": "warning",
                    "message": f"第 {i + 1} 张图片生成异常: {str(e)}",
                }), file=sys.stderr)
                break

        # Rate limiting between image generations
        if i < len(image_prompts) - 1:
            time.sleep(2)

    return image_paths


def save_image(image_data: bytes, output_path: Path):
    """Save image data to PNG file."""
    from PIL import Image as PILImage

    image = PILImage.open(BytesIO(image_data))
    if image.mode == "RGBA":
        rgb = PILImage.new("RGB", image.size, (255, 255, 255))
        rgb.paste(image, mask=image.split()[3])
        rgb.save(str(output_path), "PNG")
    elif image.mode == "RGB":
        image.save(str(output_path), "PNG")
    else:
        image.convert("RGB").save(str(output_path), "PNG")


def load_trending_context(trending_file: str) -> str:
    """Load trending data and format as context for LLM."""
    data = json.loads(Path(trending_file).read_text())
    notes = data.get("notes", [])[:10]
    analysis = data.get("analysis", {})

    parts = ["以下是当前小红书热门内容供参考：\n"]

    if analysis.get("top_keywords"):
        keywords = [kw["word"] for kw in analysis["top_keywords"][:10]]
        parts.append(f"热门关键词：{', '.join(keywords)}\n")

    for i, note in enumerate(notes[:5], 1):
        parts.append(f"{i}. {note.get('title', '')} (点赞: {note.get('likes', 0)})")

    return "\n".join(parts)


def main():
    parser = argparse.ArgumentParser(description="AI content generation for Xiaohongshu")
    parser.add_argument("--topic", default="", help="Content topic")
    parser.add_argument("--style", default="干货分享",
                        choices=list(STYLE_PROMPTS.keys()),
                        help="Content style")
    parser.add_argument("--image-count", type=int, default=4, help="Number of images (1-9, default 4)")
    parser.add_argument("--trending-file", default="", help="Trending data file for context")
    parser.add_argument("--preview-only", action="store_true", help="Only generate preview, don't save")
    args = parser.parse_args()

    if not args.topic and not args.trending_file:
        print(json.dumps({
            "status": "error",
            "message": "请提供 --topic 或 --trending-file 参数。",
        }))
        sys.exit(1)

    image_count = max(1, min(9, args.image_count))

    # Load trending context if provided
    trending_context = ""
    if args.trending_file and Path(args.trending_file).exists():
        trending_context = load_trending_context(args.trending_file)
        if not args.topic:
            # Extract topic from trending data
            data = json.loads(Path(args.trending_file).read_text())
            analysis = data.get("analysis", {})
            if analysis.get("top_keywords"):
                args.topic = analysis["top_keywords"][0]["word"]
            else:
                notes = data.get("notes", [])
                if notes:
                    args.topic = notes[0].get("title", "热门话题")[:20]

    try:
        # Step 1: Generate copywriting
        copywriting = generate_copywriting(args.topic, args.style, image_count, trending_context)
        print(json.dumps({
            "step": "copywriting", "status": "done",
            "title": copywriting["title"],
            "image_prompts_count": len(copywriting["image_prompts"]),
        }))
        sys.stdout.flush()

        # Step 2: Generate images
        data_dir = os.environ.get(
            "XHS_DATA_DIR",
            os.path.expanduser("~/.openclaw/skills/xhs/data"),
        )
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path(data_dir) / "generated" / ts
        output_dir.mkdir(parents=True, exist_ok=True)

        image_paths = generate_images(copywriting["image_prompts"], output_dir)

        # Step 3: Save package
        package = {
            "title": copywriting["title"],
            "content": copywriting["content"],
            "topics": copywriting["topics"],
            "image_prompts": copywriting["image_prompts"],
            "images": image_paths,
            "topic": args.topic,
            "style": args.style,
            "generated_at": datetime.now().isoformat(),
        }

        if not args.preview_only:
            package_file = output_dir / "package.json"
            package_file.write_text(json.dumps(package, ensure_ascii=False, indent=2))

        # Output compact result (full data is in package.json)
        result = {
            "status": "success",
            "message": f"内容生成完成！标题: {copywriting['title']}",
            "title": copywriting["title"],
            "content_preview": copywriting["content"][:200],
            "topics": copywriting["topics"],
            "image_count": len(image_paths),
            "output_dir": str(output_dir),
            "package_file": str(output_dir / "package.json") if not args.preview_only else None,
        }
        print(json.dumps(result, ensure_ascii=False))

        # Print MEDIA lines for OpenClaw to auto-attach images
        for img_path in image_paths:
            print(f"MEDIA: {img_path}")

    except Exception as e:
        print(json.dumps({
            "status": "error",
            "message": f"内容生成失败: {str(e)}",
            "error": str(e),
        }))
        sys.exit(1)


if __name__ == "__main__":
    main()
