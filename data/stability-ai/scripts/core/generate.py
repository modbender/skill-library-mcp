#!/usr/bin/env python3
import requests
import os
import argparse
import sys
import base64
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
from PIL import Image
import io

load_dotenv()

API_HOST = os.getenv('API_HOST', 'https://api.stability.ai')
API_KEY = os.getenv("STABILITY_API_KEY")

if not API_KEY:
    print("Error: STABILITY_API_KEY environment variable not set.")
    print("Tip: Check your .env file or export the variable.")
    sys.exit(1)

ASPECT_RATIO_MAP = {
    "1:1": (1024, 1024),
    "16:9": (1216, 832),
    "9:16": (832, 1216),
    "21:9": (1344, 768),
    "4:3": (1152, 896),
    "3:4": (896, 1152),
}

STYLE_PRESETS = [
    "enhance", "anime", "photographic", "digital-art", "comic-book",
    "fantasy-art", "line-art", "analog-film", "neon-punk", "isometric",
    "low-poly", "origami", "modeling-compound", "cinematic", "3d-model",
    "pixel-art", "tile-texture"
]

def generate_image(
    prompt: str,
    output_dir: str,
    negative_prompt: Optional[str] = None,
    model: str = "stable-diffusion-xl-1024-v1-0",
    aspect_ratio: str = "1:1",
    steps: int = 40,
    cfg_scale: float = 5.0,
    seed: Optional[int] = None,
    style_preset: Optional[str] = None,
    output_format: str = "png",
    use_v2: bool = False
) -> List[str]:
    if use_v2:
        return _generate_v2(prompt, output_dir, negative_prompt, model, aspect_ratio, 
                          steps, cfg_scale, seed, style_preset, output_format)
    else:
        return _generate_v1(prompt, output_dir, negative_prompt, model, aspect_ratio,
                          steps, cfg_scale, seed, style_preset, output_format)

def _generate_v1(
    prompt: str,
    output_dir: str,
    negative_prompt: Optional[str],
    model: str,
    aspect_ratio: str,
    steps: int,
    cfg_scale: float,
    seed: Optional[int],
    style_preset: Optional[str],
    output_format: str
) -> List[str]:
    url = f"{API_HOST}/v1/generation/{model}/text-to-image"
    
    width, height = ASPECT_RATIO_MAP.get(aspect_ratio, ASPECT_RATIO_MAP["1:1"])
    
    body: Dict[str, Any] = {
        "steps": steps,
        "width": width,
        "height": height,
        "cfg_scale": cfg_scale,
        "samples": 1,
        "text_prompts": [
            {
                "text": prompt,
                "weight": 1
            }
        ],
    }
    
    if seed is not None:
        body["seed"] = seed
    
    if style_preset:
        body["style_preset"] = style_preset

    if negative_prompt:
        body["text_prompts"].append({
            "text": negative_prompt,
            "weight": -1
        })

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }

    print(f"Generating: '{prompt}'")
    if negative_prompt:
        print(f"Negative:   '{negative_prompt}'")
    print(f"Model:      {model} | Steps: {steps} | CFG: {cfg_scale} | Ratio: {aspect_ratio}")
    if seed is not None:
        print(f"Seed:       {seed}")
    if style_preset:
        print(f"Style:      {style_preset}")

    try:
        response = requests.post(url, headers=headers, json=body, timeout=120)
        
        if response.status_code == 401:
            print("Error: Invalid API key. Check your STABILITY_API_KEY.")
            sys.exit(1)
        elif response.status_code == 402:
            print("Error: Insufficient credits. Please check your account balance.")
            sys.exit(1)
        elif response.status_code != 200:
            error_data = response.text
            try:
                error_json = response.json()
                if "message" in error_json:
                    error_data = error_json["message"]
            except:
                pass
            print(f"Error ({response.status_code}): {error_data}")
            sys.exit(1)

        data = response.json()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        paths = []
        
        for i, image in enumerate(data.get("artifacts", [])):
            image_data = base64.b64decode(image["base64"])
            
            base_filename = f"{timestamp}_{i}"
            filepath = _save_image(image_data, output_dir, base_filename, output_format)
            
            metadata = {
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "model": model,
                "aspect_ratio": aspect_ratio,
                "width": width,
                "height": height,
                "steps": steps,
                "cfg_scale": cfg_scale,
                "seed": seed if seed is not None else "random",
                "style_preset": style_preset,
                "output_format": output_format,
                "generated_at": datetime.now().isoformat(),
                "api_version": "v1"
            }
            
            metadata_path = _save_metadata(metadata, output_dir, base_filename)
            
            print(f"Saved: {filepath}")
            if metadata_path:
                print(f"Metadata: {metadata_path}")
            
            paths.append(filepath)
        
        _cleanup_old_files(output_dir, output_format)
        
        return paths
        
    except requests.exceptions.Timeout:
        print("Error: Request timed out. The generation may take longer than expected.")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Error: Network request failed: {e}")
        sys.exit(1)

def _generate_v2(
    prompt: str,
    output_dir: str,
    negative_prompt: Optional[str],
    model: str,
    aspect_ratio: str,
    steps: int,
    cfg_scale: float,
    seed: Optional[int],
    style_preset: Optional[str],
    output_format: str
) -> List[str]:
    url = f"{API_HOST}/v2beta/stable-image/generate/core"
    
    width, height = ASPECT_RATIO_MAP.get(aspect_ratio, ASPECT_RATIO_MAP["1:1"])
    
    files = {
        "prompt": (None, prompt),
    }
    
    data = {
        "aspect_ratio": aspect_ratio,
        "output_format": output_format,
        "mode": "text-to-image",
    }
    
    if negative_prompt:
        data["negative_prompt"] = negative_prompt
    
    if seed is not None:
        data["seed"] = str(seed)
    
    if style_preset:
        data["style_preset"] = style_preset
    
    if steps:
        data["steps"] = str(steps)
    
    if cfg_scale:
        data["cfg_scale"] = str(cfg_scale)
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
    }

    print(f"Generating (V2): '{prompt}'")
    if negative_prompt:
        print(f"Negative:   '{negative_prompt}'")
    print(f"Model:      {model} | Steps: {steps} | CFG: {cfg_scale} | Ratio: {aspect_ratio}")
    if seed is not None:
        print(f"Seed:       {seed}")
    if style_preset:
        print(f"Style:      {style_preset}")

    try:
        response = requests.post(url, headers=headers, files=files, data=data, timeout=120)
        
        if response.status_code == 401:
            print("Error: Invalid API key. Check your STABILITY_API_KEY.")
            sys.exit(1)
        elif response.status_code == 402:
            print("Error: Insufficient credits. Please check your account balance.")
            sys.exit(1)
        elif response.status_code != 200:
            error_data = response.text
            try:
                error_json = response.json()
                if "message" in error_json:
                    error_data = error_json["message"]
            except:
                pass
            print(f"Error ({response.status_code}): {error_data}")
            sys.exit(1)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        paths = []
        
        image_data = response.content
        base_filename = f"{timestamp}_0"
        filepath = _save_image(image_data, output_dir, base_filename, output_format)
        
        metadata = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "model": model,
            "aspect_ratio": aspect_ratio,
            "width": width,
            "height": height,
            "steps": steps,
            "cfg_scale": cfg_scale,
            "seed": seed if seed is not None else "random",
            "style_preset": style_preset,
            "output_format": output_format,
            "generated_at": datetime.now().isoformat(),
            "api_version": "v2beta"
        }
        
        metadata_path = _save_metadata(metadata, output_dir, base_filename)
        
        print(f"Saved: {filepath}")
        if metadata_path:
            print(f"Metadata: {metadata_path}")
        
        paths.append(filepath)
        
        _cleanup_old_files(output_dir, output_format)
        
        return paths
        
    except requests.exceptions.Timeout:
        print("Error: Request timed out. The generation may take longer than expected.")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Error: Network request failed: {e}")
        sys.exit(1)

def _save_image(image_data: bytes, output_dir: str, base_filename: str, output_format: str) -> str:
    ext_map = {"png": "png", "jpg": "jpg", "jpeg": "jpg", "webp": "webp"}
    ext = ext_map.get(output_format.lower(), "png")
    filename = f"{base_filename}.{ext}"
    filepath = os.path.join(output_dir, filename)
    
    if output_format.lower() in ["jpg", "jpeg"]:
        img = Image.open(io.BytesIO(image_data))
        if img.mode == "RGBA":
            background = Image.new("RGB", img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])
            img = background
        img.save(filepath, "JPEG", quality=95)
    elif output_format.lower() == "webp":
        img = Image.open(io.BytesIO(image_data))
        img.save(filepath, "WEBP", quality=95)
    else:
        with open(filepath, "wb") as f:
            f.write(image_data)
    
    return filepath

def _save_metadata(metadata: Dict[str, Any], output_dir: str, base_filename: str) -> Optional[str]:
    try:
        metadata_path = os.path.join(output_dir, f"{base_filename}.json")
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)
        return metadata_path
    except Exception as e:
        print(f"Warning: Could not save metadata: {e}")
        return None

def _cleanup_old_files(output_dir: str, output_format: str) -> None:
    try:
        extensions = ["png", "jpg", "jpeg", "webp"]
        files = [os.path.join(output_dir, f) for f in os.listdir(output_dir) 
                if any(f.endswith(f".{ext}") for ext in extensions)]
        files.sort(key=os.path.getmtime)
        
        retention_limit = 20
        if len(files) > retention_limit:
            removed = files[:len(files) - retention_limit]
            for f in removed:
                os.remove(f)
                json_file = f.replace(os.path.splitext(f)[1], ".json")
                if os.path.exists(json_file):
                    os.remove(json_file)
                print(f"Auto-Clean: Removed old file {os.path.basename(f)}")
    except Exception as e:
        print(f"Cleanup warning: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate images via Stability AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Available style presets: {', '.join(STYLE_PRESETS)}
Available aspect ratios: {', '.join(ASPECT_RATIO_MAP.keys())}
        """
    )
    parser.add_argument("prompt", help="Text description of the image")
    parser.add_argument("--output", default="./assets/generated", help="Output directory")
    parser.add_argument("--negative", help="Negative prompt (things to avoid)")
    parser.add_argument("--ratio", default="1:1", 
                       choices=list(ASPECT_RATIO_MAP.keys()),
                       help="Aspect Ratio")
    parser.add_argument("--steps", type=int, default=40, 
                       help="Generation steps (30-50)")
    parser.add_argument("--cfg", type=float, default=5.0, 
                       help="CFG Scale (Prompt adherence, 1-35)")
    parser.add_argument("--seed", type=int, default=None,
                       help="Seed for reproducible results (omit for random)")
    parser.add_argument("--style", choices=STYLE_PRESETS, default=None,
                       help="Style preset to apply")
    parser.add_argument("--format", choices=["png", "jpg", "jpeg", "webp"], 
                       default="png", help="Output image format")
    parser.add_argument("--model", default="stable-diffusion-xl-1024-v1-0",
                       help="Model to use")
    parser.add_argument("--v2", action="store_true",
                       help="Use V2 Stable Image API (experimental)")
    
    args = parser.parse_args()
    
    os.makedirs(args.output, exist_ok=True)
    generate_image(
        args.prompt, 
        args.output, 
        negative_prompt=args.negative,
        model=args.model,
        aspect_ratio=args.ratio,
        steps=args.steps,
        cfg_scale=args.cfg,
        seed=args.seed,
        style_preset=args.style,
        output_format=args.format,
        use_v2=args.v2
    )
