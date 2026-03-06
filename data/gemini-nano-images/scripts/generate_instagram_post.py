#!/usr/bin/env python3
"""
Instagram Content Generator
Generates image + caption for Instagram posts.
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


def generate_instagram_content(
    topic: str,
    mood: str = "inspiring",
    output_dir: str = None,
    api_key: str = None
) -> dict:
    """
    Generate Instagram-ready content: image + caption.
    
    Args:
        topic: Content topic/theme
        mood: Post mood (inspiring, cozy, energetic, calm)
        output_dir: Where to save files
        api_key: Gemini API key
    
    Returns:
        Dict with image_path and caption
    """
    
    api_key = api_key or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Set GEMINI_API_KEY env var or pass --api-key")
    
    client = genai.Client(api_key=api_key)
    
    # Mood presets
    mood_presets = {
        "inspiring": "uplifting, motivational, golden hour lighting",
        "cozy": "warm, comfortable, soft lighting, homey feeling",
        "energetic": "vibrant, dynamic, bright colors, action",
        "calm": "peaceful, serene, soft pastels, relaxing",
        "family": "loving family moment, candid, natural interaction",
        "productive": "organized, clean aesthetic, modern workspace"
    }
    
    style = mood_presets.get(mood, mood_presets["inspiring"])
    
    # Generate image
    image_prompt = f"""Ultra-realistic photograph for Instagram: {topic}

Mood: {style}
Style: Professional photography, 8K quality, Instagram-worthy composition
No text, no watermarks, no logos in the image
"""
    
    print(f"🎨 Generating image for: {topic}")
    print(f"🎭 Mood: {mood}")
    
    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=image_prompt,
        config=types.GenerateContentConfig(
            response_modalities=["Text", "Image"]
        ),
    )
    
    # Extract image
    image_data = None
    for part in response.candidates[0].content.parts:
        if hasattr(part, 'inline_data') and part.inline_data:
            image_data = part.inline_data.data
            break
    
    if not image_data:
        raise RuntimeError("No image generated")
    
    # Save image
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_topic = "".join(c if c.isalnum() else "_" for c in topic[:25])
    filename = f"ig_{timestamp}_{safe_topic}.png"
    
    if output_dir:
        output_path = Path(output_dir) / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        output_path = Path(filename)
    
    with open(output_path, "wb") as f:
        f.write(image_data)
    
    print(f"✅ Image saved: {output_path}")
    
    # Generate caption
    caption_prompt = f"""Write an engaging Instagram caption about: {topic}

Tone: {mood}, authentic, relatable for parents/families
Style: Personal, conversational, NOT promotional
Length: 3-5 sentences
Include: One thought-provoking question at the end
NO hashtags in the caption text
NO emojis at the start
NO "Paragraph 1" or formatting labels
Just the caption text, nothing else
"""
    
    caption_response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=caption_prompt,
    )
    
    caption = caption_response.text.strip()
    # Remove markdown formatting if present
    caption = caption.replace("**", "").replace("*", "")
    
    print(f"✅ Caption generated ({len(caption)} chars)")
    
    return {
        "image_path": str(output_path),
        "caption": caption,
        "topic": topic,
        "mood": mood
    }


def main():
    parser = argparse.ArgumentParser(
        description="Generate Instagram image + caption"
    )
    parser.add_argument(
        "topic",
        help="Content topic/theme"
    )
    parser.add_argument(
        "-m", "--mood",
        choices=["inspiring", "cozy", "energetic", "calm", "family", "productive"],
        default="inspiring",
        help="Post mood/style"
    )
    parser.add_argument(
        "-o", "--output",
        default="~/.openclaw/workspace/assets",
        help="Output directory"
    )
    parser.add_argument(
        "-k", "--api-key",
        help="Gemini API key"
    )
    
    args = parser.parse_args()
    
    try:
        result = generate_instagram_content(
            topic=args.topic,
            mood=args.mood,
            output_dir=os.path.expanduser(args.output),
            api_key=args.api_key
        )
        
        print(f"\n" + "="*50)
        print(f"📸 INSTAGRAM CONTENT READY")
        print(f"="*50)
        print(f"📁 Image: {result['image_path']}")
        print(f"\n📝 Caption:\n{result['caption']}")
        print(f"="*50)
        
        # Save caption to file
        caption_file = Path(result['image_path']).with_suffix('.txt')
        with open(caption_file, 'w') as f:
            f.write(result['caption'])
        print(f"💾 Caption saved: {caption_file}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
