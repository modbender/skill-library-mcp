#!/usr/bin/env python3
"""
JSON2Video Pinterest Video Generator
Creates vertical videos optimized for Pinterest from images and voiceover.
"""

import argparse
import json
import os
import sys
import time
import requests
from typing import Optional, List, Dict, Any
from pathlib import Path

# API Configuration
API_BASE = "https://api.json2video.com/v2"


def get_api_key() -> str:
    """Get API key from environment variable."""
    api_key = os.environ.get("JSON2VIDEO_API_KEY")
    if not api_key:
        raise ValueError(
            "JSON2VIDEO_API_KEY environment variable not set. "
            "Set it with: export JSON2VIDEO_API_KEY='your_key_here'"
        )
    return api_key


def create_movie(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new movie render job."""
    api_key = get_api_key()
    url = f"{API_BASE}/movies"
    
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()


def check_status(project_id: str) -> Dict[str, Any]:
    """Check the status of a movie render job."""
    api_key = get_api_key()
    url = f"{API_BASE}/movies?project={project_id}"
    
    headers = {"x-api-key": api_key}
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def wait_for_completion(project_id: str, poll_interval: int = 10, timeout: int = 600) -> Dict[str, Any]:
    """Poll for movie completion."""
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        status = check_status(project_id)
        movie = status.get("movie", {})
        current_status = movie.get("status", "unknown")
        
        print(f"Status: {current_status}")
        
        if current_status == "done":
            print(f"✓ Video ready: {movie.get('url')}")
            return status
        elif current_status == "error":
            raise RuntimeError(f"Render failed: {movie.get('message', 'Unknown error')}")
        
        time.sleep(poll_interval)
    
    raise TimeoutError(f"Render timed out after {timeout} seconds")


def build_image_element(
    image_source: str,
    duration: float,
    width: int = 1080,
    height: int = 1920,
    zoom_effect: bool = False,
    ai_provider: Optional[str] = None,
    ai_prompt: Optional[str] = None,
    aspect_ratio: str = "vertical"
) -> Dict[str, Any]:
    """
    Build an image element.
    
    Args:
        image_source: Either "ai" for AI generation or a URL
        duration: Duration in seconds
        width: Element width
        height: Element height
        zoom_effect: Whether to add Ken Burns zoom effect
        ai_provider: AI provider (flux-pro, flux-schnell, freepik-classic)
        ai_prompt: Prompt for AI image generation
        aspect_ratio: Aspect ratio for AI generation (horizontal, vertical, squared)
    """
    element = {
        "type": "image",
        "duration": duration,
        "width": width,
        "height": height,
        "x": 0,
        "y": 0
    }
    
    # AI-generated image
    if image_source == "ai":
        if not ai_prompt:
            raise ValueError("ai_prompt required when image_source is 'ai'")
        element["provider"] = ai_provider or "flux-schnell"
        element["prompt"] = ai_prompt
        element["aspect-ratio"] = aspect_ratio
    else:
        # URL-based image
        element["src"] = image_source
    
    # Add zoom animation if requested
    if zoom_effect:
        # Start slightly zoomed in, then zoom out slowly (Ken Burns effect)
        element["animations"] = [
            {
                "type": "scale",
                "start": 1.15,
                "end": 1.0,
                "easing": "ease-out",
                "duration": duration
            }
        ]
    
    return element


def build_text_element(
    text: str,
    duration: float,
    style: Optional[Dict[str, Any]] = None,
    vertical_position: str = "bottom",
    horizontal_position: str = "center"
) -> Dict[str, Any]:
    """Build a text overlay element."""
    default_style = {
        "font-family": "Montserrat",
        "font-size": "42px",
        "color": "#ffffff",
        "text-align": "center",
        "text-shadow": "2px 2px 4px rgba(0,0,0,0.7)",
        "font-weight": "bold"
    }
    
    if style:
        default_style.update(style)
    
    return {
        "type": "text",
        "text": text,
        "duration": duration,
        "settings": default_style,
        "vertical-position": vertical_position,
        "horizontal-position": horizontal_position,
        "width": 1000,
        "height": 200,
        "x": 40,
        "y": 1600
    }


def build_voice_element(
    voice_source: str,
    duration: float,
    voice_id: Optional[str] = None,
    text: Optional[str] = None,
    model: str = "azure",
    language: str = "en"
) -> Dict[str, Any]:
    """
    Build a voice element.
    
    Args:
        voice_source: "generated" for AI TTS or a URL to audio file
        duration: Duration (-1 for auto)
        voice_id: Voice ID for AI generation (Azure: "en-US-EmmaMultilingualNeural", ElevenLabs: "Bella")
        text: Text to speak (for generated voice)
        model: TTS model ("azure" - free, "elevenlabs" or "elevenlabs-flash-v2-5" - consumes credits)
        language: Language code
    """
    if voice_source == "generated":
        if not text:
            raise ValueError("text required when voice_source is 'generated'")
        return {
            "type": "voice",
            "text": text,
            "voice": voice_id or "en-US-EmmaMultilingualNeural",
            "model": model,
            "duration": -1  # Auto duration based on speech length
        }
    else:
        # External audio file
        return {
            "type": "audio",
            "src": voice_source,
            "duration": -1,
            "volume": 1.0
        }


def build_movie_subtitles(
    enabled: bool = True,
    style: Optional[Dict[str, Any]] = None,
    language: str = "en"
) -> Optional[Dict[str, Any]]:
    """
    Build a movie-level subtitle element.
    Note: Subtitles MUST be at movie level, NOT inside scenes.
    """
    if not enabled:
        return None
    
    # Subtitle settings use different property names than text elements
    default_style = {
        "font-family": "Montserrat",
        "font-size": 100,
        "style": "classic",
        "position": "bottom-center",
        "box-color": "#000000",
        "word-color": "#FFFF00",
        "line-color": "#FFFFFF",
        "outline-color": "#000000",
        "outline-width": 2
    }
    
    if style:
        default_style.update(style)
    
    return {
        "type": "subtitles",
        "language": language,
        "settings": default_style
    }


def build_scene(
    image_config: Dict[str, Any],
    voice_config: Dict[str, Any],
    text_overlay: Optional[str] = None,
    zoom_effect: bool = False,
    scene_duration: Optional[float] = None
) -> Dict[str, Any]:
    """
    Build a complete scene with image, voice, and optional text overlay.
    Note: Subtitles are handled at movie level, not per-scene.
    
    Args:
        image_config: Config for image (source, ai params, etc.)
        voice_config: Config for voice (source, text, voice_id, etc.)
        text_overlay: Optional text to display on scene
        zoom_effect: Whether to add zoom effect to image
        scene_duration: Override scene duration (auto-calculated if None)
    """
    elements = []
    
    # Build image element
    image_element = build_image_element(
        image_source=image_config.get("source", "ai"),
        duration=scene_duration or -2,  # -2 = match container
        ai_provider=image_config.get("ai_provider", "flux-schnell"),
        ai_prompt=image_config.get("ai_prompt"),
        zoom_effect=zoom_effect
    )
    elements.append(image_element)
    
    # Build voice element
    voice_element = build_voice_element(
        voice_source=voice_config.get("source", "generated"),
        duration=-1,
        voice_id=voice_config.get("voice_id"),
        text=voice_config.get("text"),
        model=voice_config.get("model", "azure"),
        language=voice_config.get("language", "en")
    )
    elements.append(voice_element)
    
    # Add text overlay if provided
    if text_overlay:
        text_element = build_text_element(
            text=text_overlay,
            duration=-2
        )
        elements.append(text_element)
    
    return {
        "elements": elements,
        "duration": scene_duration or -1  # -1 = auto from elements
    }


def create_pinterest_video(
    scenes_config: List[Dict[str, Any]],
    resolution: str = "instagram-story",  # 1080x1920 vertical
    quality: str = "high",
    cache: bool = True,
    subtitles: bool = True,
    subtitle_style: Optional[Dict[str, Any]] = None,
    wait: bool = True
) -> str:
    """
    Create a Pinterest-optimized vertical video.
    
    Args:
        scenes_config: List of scene configurations
        resolution: Video resolution preset
        quality: Rendering quality
        cache: Use caching
        subtitles: Enable movie-level subtitles
        subtitle_style: Custom subtitle styling
        wait: Wait for completion
    
    Returns:
        Project ID or video URL (if wait=True)
    """
    # Build movie payload
    movie = {
        "resolution": resolution,
        "quality": quality,
        "cache": cache,
        "scenes": [],
        "elements": []  # For movie-level elements like subtitles
    }
    
    # Build scenes
    for scene_config in scenes_config:
        scene = build_scene(
            image_config=scene_config.get("image", {"source": "ai", "ai_prompt": "Abstract background"}),
            voice_config=scene_config.get("voice", {"source": "generated", "text": "Welcome"}),
            text_overlay=scene_config.get("text_overlay"),
            zoom_effect=scene_config.get("zoom_effect", False),
            scene_duration=scene_config.get("duration")
        )
        movie["scenes"].append(scene)
    
    # Add subtitles at movie level (not per-scene)
    if subtitles:
        subtitle_element = build_movie_subtitles(
            enabled=True,
            style=subtitle_style,
            language=scenes_config[0].get("voice", {}).get("language", "en") if scenes_config else "en"
        )
        if subtitle_element:
            movie["elements"].append(subtitle_element)
    
    # Create the movie
    print("Creating video...")
    print(f"Payload preview: {json.dumps(movie, indent=2)[:500]}...")
    result = create_movie(movie)
    
    if not result.get("success"):
        raise RuntimeError(f"Failed to create movie: {result}")
    
    project_id = result.get("project")
    print(f"Project ID: {project_id}")
    
    if wait:
        final = wait_for_completion(project_id)
        return final.get("movie", {}).get("url", "")
    
    return project_id


def create_video_from_json(config_path: str, wait: bool = True) -> str:
    """Create video from a JSON configuration file."""
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Check if any scene has subtitles disabled
    scenes = config.get("scenes", [])
    subtitles_enabled = all(scene.get("subtitles", True) for scene in scenes) if scenes else True
    
    return create_pinterest_video(
        scenes_config=scenes,
        resolution=config.get("resolution", "instagram-story"),
        quality=config.get("quality", "high"),
        cache=config.get("cache", True),
        subtitles=subtitles_enabled,
        subtitle_style=config.get("subtitle_style"),
        wait=wait
    )


def main():
    parser = argparse.ArgumentParser(description="JSON2Video Pinterest Video Generator")
    parser.add_argument("--config", "-c", help="Path to JSON config file")
    parser.add_argument("--project-id", "-p", help="Check status of existing project")
    parser.add_argument("--wait", "-w", action="store_true", default=True, help="Wait for completion")
    parser.add_argument("--no-wait", dest="wait", action="store_false", help="Don't wait for completion")
    
    args = parser.parse_args()
    
    try:
        if args.project_id:
            # Check status
            status = check_status(args.project_id)
            print(json.dumps(status, indent=2))
        elif args.config:
            # Create video from config
            result = create_video_from_json(args.config, wait=args.wait)
            print(f"Result: {result}")
        else:
            parser.print_help()
            sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
