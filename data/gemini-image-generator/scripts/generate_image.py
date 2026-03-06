#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "httpx>=0.27.0",
#     "pillow>=10.0.0",
#     "google-genai>=1.0.0",
# ]
# ///
"""
使用 Gemini 模型生成或编辑图片，支持自定义第三方 API 端点。

用法：
    uv run generate_image.py --prompt "图片描述" --filename "output.png"
    uv run generate_image.py --prompt "编辑指令" --filename "edited.png" -i input.png
    uv run generate_image.py --prompt "合成指令" --filename "out.png" -i a.png -i b.png
"""

import argparse
import base64
import json
import os
import re
import sys
import time
from datetime import datetime
from io import BytesIO
from pathlib import Path

MAX_RETRIES = 3
RETRY_DELAYS = [10, 20, 40]  # 秒

VALID_ASPECT_RATIOS = ["1:1", "16:9", "9:16", "4:3", "3:4", "3:2", "2:3"]


# ---------------------------------------------------------------------------
# 配置加载（CLI > 环境变量，环境变量由 openclaw.json skills.entries.env 注入）
# ---------------------------------------------------------------------------

def _load_openclaw_apikey() -> str | None:
    """从 ~/.openclaw/openclaw.json 读取 apiKey 作为兜底"""
    try:
        cfg_path = Path.home() / ".openclaw" / "openclaw.json"
        if not cfg_path.exists():
            return None
        import json as _json
        with open(cfg_path) as f:
            cfg = _json.load(f)
        return (cfg.get("skills", {})
                   .get("entries", {})
                   .get("gemini-image-generator", {})
                   .get("apiKey"))
    except Exception:
        return None


def get_config(args) -> dict:
    """合并配置：CLI 参数 > 环境变量 > openclaw.json apiKey"""
    return {
        "api_key": (args.api_key
                    or os.environ.get("GEMINI_API_KEY")
                    or _load_openclaw_apikey()),
        "base_url": args.base_url or os.environ.get("GEMINI_BASE_URL"),
        "model": (
            args.model
            or os.environ.get("GEMINI_MODEL", "gemini-3-pro-preview")
        ),
        "api_format": (
            args.api_format
            or os.environ.get("GEMINI_API_FORMAT", "openai")
        ),
        "timeout": (
            args.timeout
            or (int(t) if (t := os.environ.get("GEMINI_TIMEOUT")) else 0)
            or 300
        ),
        "resolution": args.resolution or os.environ.get("GEMINI_RESOLUTION", "1K"),
        "output_dir": args.output_dir or os.environ.get("GEMINI_OUTPUT_DIR", "images"),
    }


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------

def make_timestamped_filename(filename: str) -> str:
    """为文件名添加时间戳前缀：yyyy-mm-dd-hh-mm-ss-name.ext"""
    ts = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    return f"{ts}-{filename}"


def truncate_base64_in_text(text: str, max_b64_len: int = 60) -> str:
    """截断文本中的 base64 数据，避免 verbose 输出过长"""
    def _replace(m):
        full = m.group(0)
        if len(full) > max_b64_len:
            return full[:max_b64_len] + f"...({len(full)} chars)"
        return full
    # 匹配 data:image URL 中的 base64 部分
    text = re.sub(r'data:image/[^;]+;base64,[A-Za-z0-9+/=]+', lambda m: (
        m.group(0)[:60] + f"...({len(m.group(0))} chars)" if len(m.group(0)) > 80 else m.group(0)
    ), text)
    # 匹配独立的长 base64 字符串（至少 200 字符）
    text = re.sub(r'(?<![A-Za-z0-9+/])[A-Za-z0-9+/=]{200,}', _replace, text)
    return text


def get_save_format(filename: str) -> str:
    """根据文件名后缀决定保存格式"""
    ext = Path(filename).suffix.lower()
    if ext in (".jpg", ".jpeg"):
        return "JPEG"
    return "PNG"


def build_prompt_hints(prompt: str, resolution: str, quality: str,
                       style: str, aspect_ratio: str | None) -> str:
    """构建增强提示词，追加分辨率/质量/风格/宽高比标记"""
    hints = []
    if resolution != "1K":
        hints.append(f"[Resolution: {resolution}]")
    if quality == "hd":
        hints.append("[Quality: high detail]")
    if style == "vivid":
        hints.append("[Style: vivid, vibrant colors]")
    if aspect_ratio:
        hints.append(f"[Aspect ratio: {aspect_ratio}]")
    if hints:
        return prompt + "\n" + "\n".join(hints)
    return prompt


# ---------------------------------------------------------------------------
# OpenAI 兼容格式
# ---------------------------------------------------------------------------

def generate_openai(config: dict, prompt: str, input_images: list[bytes],
                    resolution: str, verbose: bool = False) -> tuple:
    """通过 OpenAI 兼容 API 生成图片，返回 (image_bytes, image_url)"""
    import httpx

    base_url = config["base_url"].rstrip("/")
    url = f"{base_url}/chat/completions"

    # 构建消息内容
    if input_images:
        content = []
        for img_data in input_images:
            b64 = base64.b64encode(img_data).decode()
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{b64}"}
            })
        content.append({"type": "text", "text": prompt})
    else:
        content = prompt

    payload = {
        "model": config["model"],
        "messages": [{"role": "user", "content": content}],
        "max_tokens": 4096,
        "temperature": 1.0,
    }

    headers = {
        "Authorization": f"Bearer {config['api_key']}",
        "Content-Type": "application/json",
    }

    if verbose:
        print(f"请求地址：{url}")
        print(f"模型：{config['model']}")
        print(f"超时：{config['timeout']}s")
    sys.stdout.flush()

    # 带重试的请求
    for attempt in range(MAX_RETRIES + 1):
        try:
            response = httpx.post(url, json=payload, headers=headers,
                                  timeout=config["timeout"])
        except httpx.ReadTimeout:
            if attempt < MAX_RETRIES:
                delay = RETRY_DELAYS[attempt]
                print(f"请求超时（{config['timeout']}s），{delay}s 后重试（第 {attempt + 1}/{MAX_RETRIES} 次）...")
                sys.stdout.flush()
                time.sleep(delay)
                continue
            else:
                print(f"错误：请求超时，已重试 {MAX_RETRIES} 次。建议增加 --timeout 值。",
                      file=sys.stderr)
                sys.exit(1)
        except httpx.ConnectError as e:
            print(f"错误：无法连接到 API 端点: {e}", file=sys.stderr)
            sys.exit(1)

        if response.status_code == 429:
            if attempt < MAX_RETRIES:
                delay = RETRY_DELAYS[attempt]
                print(f"限流 (429)，{delay}s 后重试（第 {attempt + 1}/{MAX_RETRIES} 次）...")
                sys.stdout.flush()
                time.sleep(delay)
                continue
            else:
                print(f"API 限流，已重试 {MAX_RETRIES} 次仍失败: {response.text}",
                      file=sys.stderr)
                sys.exit(1)

        if response.status_code != 200:
            print(f"API 错误 ({response.status_code}): {response.text}",
                  file=sys.stderr)
            sys.exit(1)

        break

    data = response.json()

    if verbose:
        debug = json.dumps(data, indent=2, ensure_ascii=False)
        debug = truncate_base64_in_text(debug)
        print(f"响应结构：{debug[:3000]}{'...' if len(debug) > 3000 else ''}")

    return _extract_image(data)


def _extract_image(data: dict) -> tuple:
    """从多种 OpenAI 兼容响应格式中提取图片数据"""
    text_parts: list[str] = []

    try:
        msg = data["choices"][0]["message"]
    except (KeyError, IndexError):
        msg = {}

    # --- 格式 A: message.images 数组 ---
    if "images" in msg and isinstance(msg["images"], list):
        for img in msg["images"]:
            if img.get("type") == "image_url":
                url = img.get("image_url", {}).get("url", "")
                if url.startswith("data:"):
                    b64 = url.split(",", 1)[1]
                    return base64.b64decode(b64), None
            if "base64" in img:
                return base64.b64decode(img["base64"]), None
            if "url" in img:
                return None, img["url"]

    # --- 格式 B/C: message.content 数组或字符串 ---
    content = msg.get("content")
    if isinstance(content, list):
        for part in content:
            ptype = part.get("type", "")

            if ptype == "image_url":
                url = part.get("image_url", {}).get("url", "")
                if url.startswith("data:"):
                    b64 = url.split(",", 1)[1]
                    return base64.b64decode(b64), None

            if ptype == "image":
                img = part.get("image", {})
                if "base64" in img:
                    return base64.b64decode(img["base64"]), None
                if "url" in img:
                    return None, img["url"]

            if ptype == "text":
                t = part.get("text", "")
                if t:
                    text_parts.append(t)

    elif isinstance(content, str):
        if content.startswith("data:image"):
            b64 = content.split(",", 1)[1]
            return base64.b64decode(b64), None
        text_parts.append(content)

    # --- 格式 D: data[].b64_json (DALL-E) ---
    try:
        for item in data.get("data", []):
            if "b64_json" in item:
                return base64.b64decode(item["b64_json"]), None
            if "url" in item:
                return None, item["url"]
    except (KeyError, IndexError):
        pass

    for t in text_parts:
        print(f"模型响应：{t}")

    return None, None


# ---------------------------------------------------------------------------
# Google 原生格式
# ---------------------------------------------------------------------------

def generate_google(config: dict, prompt: str, input_images_pil: list,
                    resolution: str, verbose: bool = False):
    """通过 Google 原生 API 生成图片，返回 image_bytes"""
    from google import genai
    from google.genai import types

    http_options = {}
    if config["base_url"]:
        http_options["base_url"] = config["base_url"]

    client = genai.Client(
        api_key=config["api_key"],
        http_options=http_options if http_options else None,
    )

    contents = [*input_images_pil, prompt] if input_images_pil else prompt

    if verbose:
        print(f"模型：{config['model']}")
        print(f"分辨率：{resolution}")
        if http_options:
            print(f"自定义端点：{http_options['base_url']}")

    # 带重试的请求
    for attempt in range(MAX_RETRIES + 1):
        try:
            response = client.models.generate_content(
                model=config["model"],
                contents=contents,
                config=types.GenerateContentConfig(
                    response_modalities=["TEXT", "IMAGE"],
                    image_config=types.ImageConfig(image_size=resolution),
                ),
            )
            break
        except Exception as e:
            err_str = str(e)
            is_retryable = any(k in err_str.lower() for k in
                               ["429", "rate", "timeout", "503", "overloaded"])
            if is_retryable and attempt < MAX_RETRIES:
                delay = RETRY_DELAYS[attempt]
                print(f"请求失败（{err_str[:100]}），{delay}s 后重试（第 {attempt + 1}/{MAX_RETRIES} 次）...")
                sys.stdout.flush()
                time.sleep(delay)
                continue
            else:
                raise

    for part in response.parts:
        if part.text is not None:
            print(f"模型响应：{part.text}")
        elif part.inline_data is not None:
            image_data = part.inline_data.data
            if isinstance(image_data, str):
                image_data = base64.b64decode(image_data)
            return image_data

    return None


# ---------------------------------------------------------------------------
# 图片保存
# ---------------------------------------------------------------------------

def save_image(image_data: bytes, output_path: Path):
    """将图片数据保存为 PNG 或 JPEG（根据文件后缀）"""
    from PIL import Image as PILImage

    fmt = get_save_format(output_path.name)
    image = PILImage.open(BytesIO(image_data))

    if fmt == "JPEG":
        # JPEG 不支持 alpha 通道
        if image.mode in ("RGBA", "LA", "P"):
            rgb = PILImage.new("RGB", image.size, (255, 255, 255))
            if image.mode == "P":
                image = image.convert("RGBA")
            rgb.paste(image, mask=image.split()[-1] if "A" in image.mode else None)
            image = rgb
        elif image.mode != "RGB":
            image = image.convert("RGB")
        image.save(str(output_path), "JPEG", quality=95)
    else:
        if image.mode == "RGBA":
            rgb = PILImage.new("RGB", image.size, (255, 255, 255))
            rgb.paste(image, mask=image.split()[3])
            rgb.save(str(output_path), "PNG")
        elif image.mode == "RGB":
            image.save(str(output_path), "PNG")
        else:
            image.convert("RGB").save(str(output_path), "PNG")


def download_and_save(url: str, output_path: Path, timeout: int):
    """从 URL 下载图片并保存"""
    import httpx

    resp = httpx.get(url, timeout=timeout, follow_redirects=True)
    if resp.status_code != 200:
        print(f"错误：下载图片失败 ({resp.status_code})", file=sys.stderr)
        sys.exit(1)
    save_image(resp.content, output_path)


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="使用 Gemini 模型生成或编辑图片，支持自定义第三方 API 端点",
    )
    parser.add_argument("--prompt", "-p", required=True, help="图片描述或编辑指令")
    parser.add_argument("--filename", "-f", required=True, help="输出文件名")
    parser.add_argument(
        "--input-image", "-i", action="append", dest="input_images",
        metavar="IMAGE", help="输入图片路径（可重复，最多 14 张）",
    )
    parser.add_argument(
        "--resolution", "-r", choices=["1K", "2K", "4K"], help="分辨率（默认 1K）",
    )
    parser.add_argument(
        "--aspect-ratio", "-a", choices=VALID_ASPECT_RATIOS,
        help="宽高比（如 1:1、16:9、9:16、4:3、3:4）",
    )
    parser.add_argument("--api-key", "-k", help="API 密钥")
    parser.add_argument("--base-url", "-b", help="API 端点 URL")
    parser.add_argument("--model", "-m", help="模型名称")
    parser.add_argument(
        "--api-format", "-F", choices=["openai", "google"], help="API 格式（默认 openai）",
    )
    parser.add_argument("--timeout", "-t", type=int, help="超时秒数")
    parser.add_argument("--output-dir", "-o", help="输出目录（默认 images）")
    parser.add_argument(
        "--quality", choices=["standard", "hd"], default="standard", help="图片质量",
    )
    parser.add_argument(
        "--style", choices=["natural", "vivid"], default="natural", help="风格提示",
    )
    parser.add_argument(
        "--no-timestamp", action="store_true",
        help="不自动添加时间戳前缀",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="详细调试输出")

    args = parser.parse_args()
    config = get_config(args)

    # ---- 校验 ----
    if not config["api_key"]:
        print("错误：未提供 API 密钥。", file=sys.stderr)
        print("配置方式：", file=sys.stderr)
        print("  1. --api-key 参数", file=sys.stderr)
        print("  2. GEMINI_API_KEY 环境变量", file=sys.stderr)
        print("  3. ~/.openclaw/openclaw.json → skills.entries.gemini-image-generator.apiKey",
              file=sys.stderr)
        print("     (通过 primaryEnv 自动注入为 GEMINI_API_KEY)", file=sys.stderr)
        sys.exit(1)

    if not config["base_url"]:
        print("错误：未提供 API 端点 URL。", file=sys.stderr)
        print("配置方式：--base-url / GEMINI_BASE_URL / openclaw.json",
              file=sys.stderr)
        sys.exit(1)

    from PIL import Image as PILImage

    # ---- 加载输入图片 ----
    input_images_raw: list[bytes] = []
    input_images_pil = []
    resolution = config["resolution"]

    if args.input_images:
        if len(args.input_images) > 14:
            print(f"错误：输入图片数量（{len(args.input_images)}）超过上限 14 张。",
                  file=sys.stderr)
            sys.exit(1)

        max_dim = 0
        for img_path in args.input_images:
            try:
                img = PILImage.open(img_path)
                input_images_pil.append(img)
                buf = BytesIO()
                img.save(buf, format="PNG")
                input_images_raw.append(buf.getvalue())
                w, h = img.size
                max_dim = max(max_dim, w, h)
                print(f"已加载输入图片：{img_path} ({w}×{h})")
            except Exception as e:
                print(f"错误：无法加载图片 '{img_path}': {e}", file=sys.stderr)
                sys.exit(1)

        # 自动推断分辨率
        if not args.resolution and max_dim > 0:
            if max_dim >= 3000:
                resolution = "4K"
            elif max_dim >= 1500:
                resolution = "2K"
            else:
                resolution = "1K"
            print(f"自动检测分辨率：{resolution}（最大维度 {max_dim}）")

    # ---- 增强提示词 ----
    enhanced_prompt = build_prompt_hints(
        args.prompt, resolution, args.quality, args.style, args.aspect_ratio,
    )

    # ---- 输出路径（自动添加时间戳前缀） ----
    output_dir = Path(config.get("output_dir", "images"))
    if args.no_timestamp:
        final_filename = args.filename
    else:
        final_filename = make_timestamped_filename(args.filename)
    output_path = output_dir / final_filename
    output_path.parent.mkdir(parents=True, exist_ok=True)

    n = len(input_images_raw)
    if n:
        print(f"处理 {n} 张图片，分辨率 {resolution}...")
    else:
        print(f"生成图片，分辨率 {resolution}...")
    sys.stdout.flush()

    # ---- 调用 API ----
    if config["api_format"] == "google":
        image_data = generate_google(
            config, enhanced_prompt, input_images_pil, resolution, args.verbose,
        )
        if not image_data:
            print("错误：模型未生成图片。", file=sys.stderr)
            sys.exit(1)
        save_image(image_data, output_path)
    else:
        image_data, image_url = generate_openai(
            config, enhanced_prompt, input_images_raw, resolution, args.verbose,
        )
        if image_data:
            save_image(image_data, output_path)
        elif image_url:
            download_and_save(image_url, output_path, config["timeout"])
        else:
            print("错误：模型未生成图片。请检查 API 响应格式。", file=sys.stderr)
            print("提示：使用 --verbose 查看详细响应内容。", file=sys.stderr)
            sys.exit(1)

    print(f"\n图片已保存：{output_path}")
    print(f"MEDIA: {output_path}")


if __name__ == "__main__":
    main()
