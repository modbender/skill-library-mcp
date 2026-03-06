#!/usr/bin/env python3
"""
Gemini Nano Image Generator
Generates ultra-realistic images using Gemini 2.0 Flash Experimental.
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("❌ google-genai not installed. Run: pip install google-genai")
    sys.exit(1)


def generate_image(prompt: str, output_dir: str = None, api_key: str = None) -> str:
    """
    Generate an ultra-realistic image using Gemini.
    
    Args:
        prompt: Image description/prompt
        output_dir: Where to save the image (default: current dir)
        api_key: Gemini API key (optional, falls back to GEMINI_API_KEY env var)
    
    Returns:
        Path to the generated image
    """
    
    # API Key
    api_key = api_key or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "No API key provided. Set GEMINI_API_KEY env var or pass --api-key"
        )
    
    # Initialize client
    client = genai.Client(api_key=api_key)
    
    # Enhance prompt for ultra-realistic style
    enhanced_prompt = f"""Create an ultra-realistic, high-quality photograph: {prompt}

Style requirements:
- Photorealistic, 8K quality
- Professional photography lighting
- Sharp details, natural colors
- Cinematic composition
- No watermarks, text, or logos
- Suitable for social media/Instagram
"""
    
    print(f"🎨 Generating image...")
    print(f"📝 Prompt: {prompt[:80]}...")
    
    # Generate with Gemini 2.5 Flash Image
    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=enhanced_prompt,
        config=types.GenerateContentConfig(
            response_modalities=["Text", "Image"]
        ),
    )
    
    # Extract image from response
    image_data = None
    for part in response.candidates[0].content.parts:
        if hasattr(part, 'inline_data') and part.inline_data:
            image_data = part.inline_data.data
            mime_type = part.inline_data.mime_type
            break
    
    if not image_data:
        raise RuntimeError("No image generated. Response: " + str(response))
    
    # Determine file extension from mime type
    ext = ".png"
    if "jpeg" in mime_type or "jpg" in mime_type:
        ext = ".jpg"
    elif "webp" in mime_type:
        ext = ".webp"
    
    # Create output path
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_prompt = "".join(c if c.isalnum() else "_" for c in prompt[:30])
    filename = f"gemini_{timestamp}_{safe_prompt}{ext}"
    
    if output_dir:
        output_path = Path(output_dir) / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        output_path = Path(filename)
    
    # Save image
    with open(output_path, "wb") as f:
        f.write(image_data)
    
    print(f"✅ Image saved: {output_path}")
    print(f"📊 Size: {len(image_data) / 1024:.1f} KB")
    
    return str(output_path)


def main():
    parser = argparse.ArgumentParser(
        description="Generate ultra-realistic images with Gemini"
    )
    parser.add_argument(
        "prompt",
        help="Image description/prompt"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output directory (default: current directory)"
    )
    parser.add_argument(
        "-k", "--api-key",
        help="Gemini API key (or set GEMINI_API_KEY env var)"
    )
    parser.add_argument(
        "--style",
        choices=["realistic", "artistic", "minimal"],
        default="realistic",
        help="Image style preset"
    )
    
    args = parser.parse_args()
    
    try:
        image_path = generate_image(
            prompt=args.prompt,
            output_dir=args.output,
            api_key=args.api_key
        )
        print(f"\n🎯 Ready for Instagram: {image_path}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
