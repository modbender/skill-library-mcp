"""
Generate and analyze images using google-genai SDK.
Requires GEMINI_API_KEY in environment.

Usage:
  python scripts/genai_media.py generate -p "a prompt" -i assets/base.png
  python scripts/genai_media.py generate -s style_name
  python scripts/genai_media.py analyze <image_path> [style_name]
"""

import argparse
import io
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from google import genai
from google.genai import types
from PIL import Image

SCRIPT_DIR = Path(__file__).parent
ROOT_DIR = SCRIPT_DIR.parent
OUTPUT_DIR = ROOT_DIR / "output"
STYLES_DIR = ROOT_DIR / "styles"
ANALYSIS_PROMPT_FILE = ROOT_DIR / "ANALYSIS_PROMPT.md"

DEFAULT_MODEL = "gemini-3-pro-image-preview"
FUSION_MODEL = "gemini-3-flash-preview"
DEFAULT_PROMPT = "A photorealistic portrait of the same person in a natural setting."
IDENTITY_PREFIX = (
    "Based on the reference image, keep the same person and facial identity, "
    "then add or adjust the following details: "
)


def get_api_key() -> str:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        sys.exit("Error: GEMINI_API_KEY is missing.")
    return api_key


def build_image_part(image_path: str):
    path = Path(image_path)
    if not path.exists():
        return None

    img = Image.open(path)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    buf = io.BytesIO()
    img.save(buf, "PNG")
    buf.seek(0)
    return types.Part.from_bytes(mime_type="image/png", data=buf.getvalue())


def send_media(channel: str | None, target: str | None, file_path: str | None = None, message: str | None = None) -> None:
    if not channel or not target:
        return
    if not file_path and not message:
        return

    cmd = ["openclaw", "message", "send", "--channel", channel, "--target", target]
    if file_path:
        cmd += ["--media", file_path]
    if message:
        cmd += ["--message", message]

    try:
        subprocess.run(cmd, check=True)
        print("Sent via OpenClaw.")
    except subprocess.CalledProcessError as exc:
        print(f"Failed to send media: {exc}")


def extract_first_text(response) -> str:
    if not hasattr(response, "candidates") or not response.candidates:
        return ""

    parts = response.candidates[0].content.parts
    for part in parts:
        if getattr(part, "text", None):
            return part.text.strip()
    return ""


def sanitize_style_name(raw_name: str) -> str:
    lowered = raw_name.strip().lower()
    lowered = re.sub(r"[^a-z0-9]+", "_", lowered)
    lowered = re.sub(r"_+", "_", lowered).strip("_")
    return lowered[:60]


def extract_style_name_and_body(text: str) -> tuple[str, str]:
    pattern = re.compile(r"(?im)^\s*Style\s*Name\s*:\s*(.+?)\s*$")
    match = pattern.search(text)
    if not match:
        return "", text.strip()

    generated_name = match.group(1).strip()
    body = pattern.sub("", text, count=1).strip()
    return generated_name, body


def resolve_style_name(manual_name: str | None, generated_name: str) -> str:
    if manual_name:
        manual = sanitize_style_name(manual_name)
        if manual:
            return manual

    generated = sanitize_style_name(generated_name)
    if generated:
        return generated

    return "style_" + datetime.now().strftime("%Y%m%d_%H%M%S")


def ensure_unique_style_name(base_name: str) -> str:
    candidate = base_name
    idx = 2
    while (STYLES_DIR / f"{candidate}.md").exists():
        candidate = f"{base_name}_{idx}"
        idx += 1
    return candidate


def save_images_from_response(response) -> list[str]:
    files: list[str] = []
    if not hasattr(response, "candidates") or not response.candidates:
        return files

    for part in response.candidates[0].content.parts:
        inline_data = getattr(part, "inline_data", None)
        if not inline_data:
            continue

        filename = f"ellya_{os.getpid()}_{len(files)}.png"
        file_path = OUTPUT_DIR / filename
        with open(file_path, "wb") as f:
            f.write(inline_data.data)
        files.append(str(file_path))
        print(f"Saved image: {file_path}")

    return files


def load_style_prompt(style_name: str) -> str:
    style_file = STYLES_DIR / f"{style_name}.md"
    if not style_file.exists():
        print(f"Style not found, skip: {style_name}")
        return ""

    with open(style_file, "r", encoding="utf-8") as f:
        content = f.read().strip()

    if not content:
        print(f"Style is empty, skip: {style_name}")
    return content


def fuse_style_prompts(style_prompts: list[str], api_key: str) -> str:
    if not style_prompts:
        return ""
    if len(style_prompts) == 1:
        return style_prompts[0]

    client = genai.Client(api_key=api_key)
    instruction = "Merge these style descriptions into one concise image generation prompt."
    response = client.models.generate_content(
        model=FUSION_MODEL,
        contents=[instruction] + style_prompts,
    )
    return extract_first_text(response)


def resolve_final_prompt(prompt: str | None, styles: list[str] | None, api_key: str) -> str:
    if styles:
        selected = styles[:3]
        loaded = [load_style_prompt(name) for name in selected]
        loaded = [s for s in loaded if s]

        if loaded:
            fused = fuse_style_prompts(loaded, api_key).strip()
            return fused or DEFAULT_PROMPT

        print("No valid style content found. Falling back to default prompt.")
        return DEFAULT_PROMPT

    return (prompt or "").strip() or DEFAULT_PROMPT


def build_generation_prompt(prompt: str) -> str:
    text = (prompt or "").strip() or DEFAULT_PROMPT
    return f"{IDENTITY_PREFIX}{text}"


def do_generate(prompt: str, input_images: list[str] | None, channel: str | None, target: str | None, message: str | None) -> None:
    api_key = get_api_key()
    client = genai.Client(api_key=api_key)

    OUTPUT_DIR.mkdir(exist_ok=True)

    image_parts = []
    for image_path in input_images or []:
        part = build_image_part(image_path)
        if part:
            image_parts.append(part)
            print(f"Loaded reference image: {image_path}")
        else:
            print(f"Reference image not found, skip: {image_path}")

    if not image_parts:
        print("No valid reference image. Falling back to default prompt.")
        prompt = DEFAULT_PROMPT

    final_prompt = build_generation_prompt(prompt)
    print(f"Final prompt: {final_prompt}")
    print("Calling model API...")

    try:
        response = client.models.generate_content(
            model=DEFAULT_MODEL,
            contents=[*image_parts, final_prompt],
        )
    except Exception as exc:
        print(f"Generation error: {exc}")
        return

    saved_files = save_images_from_response(response)
    if not saved_files:
        print("No image data returned by model.")

    for file_path in saved_files:
        send_media(channel, target, file_path, message)

    if not saved_files and message:
        send_media(channel, target, None, message)


def generate_main() -> None:
    parser = argparse.ArgumentParser(description="Generate selfie image")
    parser.add_argument("-i", "--input-images", action="append", help="Reference image path")
    parser.add_argument("-p", "--prompt", help="Generation prompt")
    parser.add_argument("-s", "--styles", action="append", help="Style names (max 3)")
    parser.add_argument("-c", "--channel", help="OpenClaw channel")
    parser.add_argument("-t", "--target", help="OpenClaw target")
    parser.add_argument("-msg", "--message", help="Optional message to send")

    args = parser.parse_args()
    api_key = get_api_key()
    final_prompt = resolve_final_prompt(args.prompt, args.styles, api_key)
    do_generate(final_prompt, args.input_images, args.channel, args.target, args.message)


def analyze_main() -> None:
    parser = argparse.ArgumentParser(description="Analyze image and store style prompt")
    parser.add_argument("image_path", help="Image path")
    parser.add_argument("style_name", nargs="?", help="Optional style name override")
    parser.add_argument("-c", "--channel", help="OpenClaw channel")
    parser.add_argument("-t", "--target", help="OpenClaw target")
    args = parser.parse_args()

    api_key = get_api_key()

    if not ANALYSIS_PROMPT_FILE.exists():
        sys.exit(f"Error: analysis prompt file not found: {ANALYSIS_PROMPT_FILE}")

    with open(ANALYSIS_PROMPT_FILE, "r", encoding="utf-8") as f:
        instruction = f.read().strip()

    part = build_image_part(args.image_path)
    if not part:
        sys.exit(f"Error: image not found: {args.image_path}")

    print(f"Analyzing image: {args.image_path}")

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=DEFAULT_MODEL,
            contents=[part, instruction],
        )
        text = extract_first_text(response)
    except Exception as exc:
        print(f"Analyze error: {exc}")
        return

    if not text:
        print("Empty analysis result. Style file will not be saved.")
        return

    generated_name, body = extract_style_name_and_body(text)
    final_name = resolve_style_name(args.style_name, generated_name)
    final_name = ensure_unique_style_name(final_name)
    final_body = (body or text).strip()
    if not final_body:
        print("Empty analysis body. Style file will not be saved.")
        return

    STYLES_DIR.mkdir(exist_ok=True)
    style_file = STYLES_DIR / f"{final_name}.md"
    with open(style_file, "w", encoding="utf-8") as f:
        f.write(final_body)

    print(f"Saved style prompt: {style_file}")

    if args.channel and args.target:
        send_media(args.channel, args.target, None, f"Saved style: {final_name}")


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "analyze":
        sys.argv.pop(1)
        analyze_main()
        return

    if len(sys.argv) > 1 and sys.argv[1] == "generate":
        sys.argv.pop(1)
        generate_main()
        return

    generate_main()


if __name__ == "__main__":
    main()
