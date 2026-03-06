import os
import requests
from PIL import Image, ImageDraw, ImageFont
import openai
from typing import List, Optional
from pathlib import Path


# Simple utility helpers for image generation and overlay
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    # don't raise here; higher-level code can warn
    OPENAI_API_KEY = None

client = openai.OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


def generate_image(prompt: str, output_path: str, size: str = "1024x1536") -> str:
    """Generate a single image using the OpenAI images API and save to output_path.

    This function assumes the openai client is configured via env var.
    It will fall back to a placeholder image when no API key is available.
    """
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    if client is None:
        # create a simple placeholder image so local tests don't fail
        img = Image.new("RGB", (768, 1152), color=(30, 30, 30))
        draw = ImageDraw.Draw(img)
        draw.text((20, 20), "PLACEHOLDER IMAGE\n" + prompt[:200], fill=(255, 255, 255))
        img.save(out)
        return str(out)

    response = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size=size,
        n=1,
    )
    # response format: depending on client, may return a URL or b64; support common patterns
    image_url = None
    if hasattr(response, 'data') and response.data:
        item = response.data[0]
        image_url = getattr(item, 'url', None) or item.get('url') if isinstance(item, dict) else None
    if not image_url and isinstance(response, dict):
        # try known keys
        data = response.get('data')
        if data and isinstance(data, list) and data[0].get('url'):
            image_url = data[0]['url']

    if image_url:
        image_data = requests.get(image_url).content
        with open(out, 'wb') as f:
            f.write(image_data)
        return str(out)

    # If we reach here, create placeholder
    img = Image.new("RGB", (768, 1152), color=(30, 30, 30))
    draw = ImageDraw.Draw(img)
    draw.text((20, 20), "PLACEHOLDER (no url returned)" + prompt[:200], fill=(255, 255, 255))
    img.save(out)
    return str(out)


def add_text_overlay(image_path: str, text: str, output_path: str, font_size_percent: float = 0.065) -> str:
    """Add centered wrapped text over an image and save result.

    Keeps text away from top/bottom 10% to avoid UI elements.
    """
    img = Image.open(image_path).convert('RGBA')
    draw = ImageDraw.Draw(img)
    width, height = img.size

    font_size = int(height * font_size_percent)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", font_size)
    except Exception:
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except Exception:
            font = ImageFont.load_default()

    # simple wrap
    words = text.split()
    lines = []
    cur = []
    for w in words:
        cur.append(w)
        sample = " ".join(cur)
        bbox = draw.textbbox((0, 0), sample, font=font)
        if bbox[2] - bbox[0] > width * 0.8:
            cur.pop()
            lines.append(" ".join(cur))
            cur = [w]
    if cur:
        lines.append(" ".join(cur))

    y_text = int(height * 0.35)
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_w = bbox[2] - bbox[0]
        line_h = bbox[3] - bbox[1]
        x = (width - line_w) // 2
        draw.text((x, y_text), line, font=font, fill=(255, 255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0))
        y_text += line_h + 6

    # Save as PNG
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.convert('RGB').save(out)
    return str(out)


def generate_slides(hook: str, locked_architecture: str, out_dir: str = "images", slides: int = 6, style_hint: Optional[str] = None) -> List[str]:
    """Generate `slides` images and overlay text on the first slide.

    Returns list of saved file paths.
    """
    out_dir_p = Path(out_dir)
    out_dir_p.mkdir(parents=True, exist_ok=True)
    saved = []
    for i in range(1, slides + 1):
        prompt = f"{locked_architecture}\n\nStyle hints: {style_hint or 'iPhone photo, natural lighting, realistic'}\nSlide {i} of {slides}."
        img_path = str(out_dir_p / f"slide_{i}.png")
        final_path = str(out_dir_p / f"final_slide_{i}.png")
        generate_image(prompt, img_path)
        if i == 1:
            add_text_overlay(img_path, hook, final_path)
            saved.append(final_path)
        else:
            # For other slides, keep as-is or lightly process
            Path(img_path).rename(final_path)
            saved.append(final_path)
    return saved


def simple_hook_generator(topic: str, persona: Optional[str] = None) -> str:
    """Return a short 'hook' for a TikTok carousel. This is a placeholder
    implementation; integrate with a text model for production.
    """
    if persona:
        return f"{persona} tried this with {topic} — you won't believe the result."
    return f"I tried {topic} one week and this happened..."


def generate(topic: str, out_dir: str = "images", slides: int = 6, persona: Optional[str] = None, style_hint: Optional[str] = None):
    """High-level orchestrator: create hook, locked architecture, slides and caption.

    Returns dict with paths and caption.
    """
    hook = simple_hook_generator(topic, persona)
    locked = f"A realistic photo series about {topic}. Keep camera: iPhone, natural lighting, shallow depth of field."
    images = generate_slides(hook, locked, out_dir=out_dir, slides=slides, style_hint=style_hint)
    caption = f"{hook} Read the full story in the comments. #ai #tiktok"
    # save caption
    Path(out_dir).joinpath('caption.txt').write_text(caption, encoding='utf-8')
    return {"hook": hook, "locked_architecture": locked, "images": images, "caption": caption}


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Generate TikTok carousel slides locally')
    parser.add_argument('topic')
    parser.add_argument('--out', default='images')
    parser.add_argument('--slides', type=int, default=6)
    parser.add_argument('--persona', default=None)
    args = parser.parse_args()
    result = generate(args.topic, out_dir=args.out, slides=args.slides, persona=args.persona)
    print('Generated:', result)
