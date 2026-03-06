"""
Nano Banana 2 Image Generation Module
Author: Tim (sales@dageno.ai)

This module handles image generation using Nano Banana 2 (Google Gemini 2.5 Flash Image)
Real implementation using Google Gemini API for native image generation.
"""

import os
import json
import time
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    from PIL import Image
    from io import BytesIO
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

from .config import NANO_BANANA_CONFIG, IMAGE_STYLES, get_google_api_key


class NanoBanana2:
    """
    Nano Banana 2 Image Generator
    Uses Google Gemini 2.5 Flash Image for native image generation
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Nano Banana 2 generator

        Args:
            api_key: Google API Key (if None, reads from GOOGLE_API_KEY or GEMINI_API_KEY env var)
        """
        self.api_key = api_key or get_google_api_key()
        self.model_name = NANO_BANANA_CONFIG["model"]
        self.output_dir = Path(NANO_BANANA_CONFIG["output_dir"])

        # Create output directory if not exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize Gemini client if available
        self.client = None
        if GEMINI_AVAILABLE and self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
                print(f"[INFO] Nano Banana 2 initialized with model: {self.model_name}")
            except Exception as e:
                print(f"[WARNING] Failed to initialize Gemini client: {e}")
                self.client = None
        else:
            if not GEMINI_AVAILABLE:
                print("[WARNING] google-genai package not installed. Image generation will fail.")
            if not self.api_key:
                print("[WARNING] No Google API Key provided. Image generation will not work.")

    def _enhance_prompt(self, base_prompt: str, style: str) -> str:
        """
        Enhance prompt with style-specific suffixes

        Args:
            base_prompt: Base prompt from opportunity analysis
            style: Image style (white_info, lifestyle, hero)

        Returns:
            Enhanced prompt with style modifiers
        """
        if style not in IMAGE_STYLES:
            style = "white_info"

        style_config = IMAGE_STYLES[style]
        enhanced = f"{base_prompt}, {style_config['suffix']}"

        return enhanced

    def _generate_filename(self, opportunity_id: str, style: str) -> str:
        """
        Generate unique filename for image

        Args:
            opportunity_id: Opportunity identifier
            style: Image style

        Returns:
            Filename string
        """
        timestamp = int(time.time())
        hash_suffix = hashlib.md5(f"{opportunity_id}_{style}".encode()).hexdigest()[:6]
        return f"{opportunity_id}_{style}_{hash_suffix}.png"

    def generate_image(
        self,
        prompt: str,
        opportunity_id: str,
        style: str = "white_info"
    ) -> Dict[str, Any]:
        """
        Generate single image using Nano Banana 2 (Gemini 2.5 Flash Image)

        Args:
            prompt: Image generation prompt
            opportunity_id: Associated opportunity ID
            style: Image style (white_info, lifestyle, hero)

        Returns:
            Dictionary containing generation result
        """
        # Enhance prompt with style
        enhanced_prompt = self._enhance_prompt(prompt, style)

        # Generate filename
        filename = self._generate_filename(opportunity_id, style)
        output_path = self.output_dir / filename

        result = {
            "opportunity_id": opportunity_id,
            "image_type": style,
            "image_url": str(output_path),
            "generation_status": "pending",
            "prompt_used": enhanced_prompt,
            "timestamp": datetime.now().isoformat()
        }

        # Check if client is available
        if not self.client:
            result["generation_status"] = "failed"
            result["error"] = "Gemini client not initialized - no API key or package not installed"
            print(f"[ERROR] Cannot generate image: {result['error']}")
            return result

        # Check PIL availability
        if not PIL_AVAILABLE:
            result["generation_status"] = "failed"
            result["error"] = "Pillow package not installed"
            print(f"[ERROR] Cannot save image: {result['error']}")
            return result

        try:
            # Call Gemini API for real image generation
            print(f"[INFO] Generating {style} image for {opportunity_id}...")
            print(f"[PROMPT] {enhanced_prompt[:100]}...")

            # Generate content with image using Gemini 2.5 Flash Image
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[enhanced_prompt]
            )

            # Process response to extract image
            image_saved = False
            caption_text = None

            for part in response.candidates[0].content.parts:
                if part.text is not None:
                    caption_text = part.text
                    print(f"[CAPTION] {caption_text[:100]}...")
                elif part.inline_data is not None:
                    # Save the image
                    image_data = part.inline_data.data
                    image = Image.open(BytesIO(image_data))
                    image.save(output_path)
                    image_saved = True
                    print(f"[SUCCESS] Image saved to: {output_path}")

            if image_saved:
                result["generation_status"] = "success"
                result["message"] = "Image generated successfully"
                if caption_text:
                    result["caption"] = caption_text
            else:
                result["generation_status"] = "failed"
                result["error"] = "No image in response"
                print(f"[ERROR] No image in API response")

        except Exception as e:
            result["generation_status"] = "failed"
            result["error"] = str(e)
            print(f"[ERROR] Failed to generate {style} image: {str(e)}")

        return result

    def generate_batch(
        self,
        prompts: List[Dict[str, Any]],
        opportunity_id: str
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple images for an opportunity

        Args:
            prompts: List of prompt dictionaries with style
            opportunity_id: Associated opportunity ID

        Returns:
            List of generation results
        """
        results = []

        for prompt_item in prompts:
            style = prompt_item.get("style", "white_info")
            prompt_text = prompt_item.get("prompt", "")

            if not prompt_text:
                continue

            result = self.generate_image(
                prompt=prompt_text,
                opportunity_id=opportunity_id,
                style=style
            )

            results.append(result)

        return results


def generate_images_from_prompts(
    prompts_data: List[Dict],
    api_key: Optional[str] = None
) -> List[Dict]:
    """
    Convenience function to generate images from prompts

    Args:
        prompts_data: List of prompt dictionaries
        api_key: Google API Key

    Returns:
        List of generated image results
    """
    generator = NanoBanana2(api_key=api_key)

    all_results = []
    for prompt_group in prompts_data:
        opportunity_id = prompt_group.get("opportunity_id", "unknown")
        image_prompts = prompt_group.get("prompts", [])

        # Convert to list format
        prompt_list = []
        for img_type in ["white_info", "lifestyle", "hero"]:
            if img_type in image_prompts:
                prompt_list.append({
                    "style": img_type,
                    "prompt": image_prompts[img_type].get("prompt", "")
                })

        results = generator.generate_batch(prompt_list, opportunity_id)
        all_results.extend(results)

    return all_results


# Example usage
if __name__ == "__main__":
    # Test the generator
    api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")

    if api_key:
        print("Testing Nano Banana 2 Image Generation...")
        print(f"Model: {NANO_BANANA_CONFIG['model']}")
        generator = NanoBanana2(api_key=api_key)

        # Generate a test image
        result = generator.generate_image(
            prompt="A modern wireless bluetooth headphone on white background, professional product photography",
            opportunity_id="test_001",
            style="white_info"
        )

        print(f"\nResult: {result}")
    else:
        print("No API key found. Set GOOGLE_API_KEY or GEMINI_API_KEY environment variable.")
