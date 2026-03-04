#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Add intro or outro to a video with various templates and animations.
"""

import argparse
import json
import os

# MoviePy 2.x compatibility
try:
    from moviepy import (
        VideoFileClip, TextClip, CompositeVideoClip, ColorClip, concatenate_videoclips
    )
    from moviepy.video.fx import FadeIn, FadeOut
    MOVIEPY_V2 = True
except ImportError:
    from moviepy.editor import (
        VideoFileClip, TextClip, CompositeVideoClip, ColorClip, concatenate_videoclips
    )
    from moviepy.video.fx.all import fadein, fadeout
    MOVIEPY_V2 = False

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PRESETS_PATH = os.path.join(SCRIPT_DIR, '..', 'templates', 'presets.json')

def load_presets():
    """Load preset configurations from JSON file."""
    with open(PRESETS_PATH, 'r') as f:
        return json.load(f)

def apply_fade(clip, fade_in=True, duration=0.5):
    """Apply fade effect compatible with both MoviePy versions."""
    if MOVIEPY_V2:
        if fade_in:
            return clip.with_effects([FadeIn(duration)])
        else:
            return clip.with_effects([FadeOut(duration)])
    else:
        if fade_in:
            return clip.fx(fadein, duration)
        else:
            return clip.fx(fadeout, duration)

def create_intro_outro_clip(text, template_config, video_size, duration=None):
    """Create an intro/outro clip based on template configuration."""
    fontsize = template_config.get('fontsize', 70)
    color = template_config.get('color', 'white')
    bg_color = template_config.get('bg_color', 'black')
    clip_duration = duration or template_config.get('duration', 3)
    animation = template_config.get('animation', 'fade')
    
    # Parse background color
    if isinstance(bg_color, str) and bg_color.startswith('#'):
        hex_color = bg_color.lstrip('#')
        bg_color = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    elif isinstance(bg_color, str):
        color_map = {'black': (0, 0, 0), 'white': (255, 255, 255)}
        bg_color = color_map.get(bg_color, (0, 0, 0))
    
    # Create background
    if MOVIEPY_V2:
        bg_clip = ColorClip(size=video_size, color=bg_color, duration=clip_duration)
    else:
        bg_clip = ColorClip(size=video_size, color=bg_color)
        bg_clip = bg_clip.set_duration(clip_duration)
    
    # Create text
    if MOVIEPY_V2:
        txt_clip = TextClip(
            text=text, 
            font_size=fontsize, 
            color=color,
            font='DejaVu-Sans',
            duration=clip_duration
        )
        txt_clip = txt_clip.with_position('center')
    else:
        txt_clip = TextClip(text, fontsize=fontsize, color=color, font='DejaVu-Sans')
        txt_clip = txt_clip.set_duration(clip_duration)
        txt_clip = txt_clip.set_pos('center')
    
    # Apply animation
    if animation == 'fade':
        txt_clip = apply_fade(txt_clip, fade_in=True, duration=0.5)
        txt_clip = apply_fade(txt_clip, fade_in=False, duration=0.5)
    
    # Composite
    if MOVIEPY_V2:
        intro_clip = CompositeVideoClip([bg_clip, txt_clip], size=video_size)
    else:
        intro_clip = CompositeVideoClip([bg_clip, txt_clip], size=video_size)
        intro_clip = intro_clip.set_duration(clip_duration)
    
    return intro_clip

def add_intro_outro(input_video, output_video, text, position, template):
    """Add an intro or outro to a video.
    
    Args:
        input_video: Path to input video file.
        output_video: Path to output video file.
        text: Text to display in intro/outro.
        position: 'intro' or 'outro'.
        template: Template name (modern, cyberpunk, business, cartoon).
    """
    presets = load_presets()
    template_config = presets.get('intro_outro', {}).get(template, presets['intro_outro']['modern'])
    
    video_clip = VideoFileClip(input_video)
    intro_outro_clip = create_intro_outro_clip(text, template_config, video_clip.size)
    
    if position == 'intro':
        final_clip = concatenate_videoclips([intro_outro_clip, video_clip])
    else:  # outro
        final_clip = concatenate_videoclips([video_clip, intro_outro_clip])
    
    final_clip.write_videofile(output_video, codec='libx264', audio_codec='aac')
    
    # Clean up
    video_clip.close()
    final_clip.close()

def main():
    parser = argparse.ArgumentParser(
        description='Add an intro or outro to a video.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --input video.mp4 --output output.mp4 --type intro --text "Welcome!" --template modern
  %(prog)s --input video.mp4 --output output.mp4 --type outro --text "Thanks for watching" --template cyberpunk
        """
    )
    parser.add_argument('--input', required=True, help='Input video file path')
    parser.add_argument('--output', required=True, help='Output video file path')
    parser.add_argument('--type', required=True, choices=['intro', 'outro'], 
                        help='Specify intro or outro')
    parser.add_argument('--text', required=True, help='Text to display')
    parser.add_argument('--template', default='modern', 
                        choices=['modern', 'cyberpunk', 'business', 'cartoon'],
                        help='Template for the intro/outro (default: modern)')
    
    args = parser.parse_args()
    add_intro_outro(args.input, args.output, args.text, args.type, args.template)
    print(f"Successfully created {args.type} and saved to {args.output}")

if __name__ == '__main__':
    main()
