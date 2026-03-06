#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Add lower third title bar to a video.
"""

import argparse
import json
import os

# MoviePy 2.x compatibility
try:
    from moviepy import VideoFileClip, TextClip, CompositeVideoClip, ColorClip
    from moviepy.video.fx import FadeIn, FadeOut
    MOVIEPY_V2 = True
except ImportError:
    from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, ColorClip
    from moviepy.video.fx.all import fadein, fadeout
    MOVIEPY_V2 = False

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PRESETS_PATH = os.path.join(SCRIPT_DIR, '..', 'templates', 'presets.json')

def load_presets():
    """Load preset configurations from JSON file."""
    with open(PRESETS_PATH, 'r') as f:
        return json.load(f)

def apply_fade(clip, fade_in=True, duration=0.3):
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

def create_lower_third(title, subtitle, template_config, video_size, start_time=2, duration=None):
    """Create a lower third composite clip.
    
    Args:
        title: Main title text.
        subtitle: Subtitle text.
        template_config: Template configuration dict.
        video_size: Tuple of (width, height).
        start_time: When to start showing the lower third.
        duration: How long to show the lower third.
    """
    vw, vh = video_size
    
    bar_color = template_config.get('bar_color', [0, 0, 0, 180])
    title_fontsize = template_config.get('title_fontsize', 40)
    subtitle_fontsize = template_config.get('subtitle_fontsize', 30)
    title_color = template_config.get('title_color', 'white')
    subtitle_color = template_config.get('subtitle_color', '#cccccc')
    clip_duration = duration or template_config.get('duration', 5)
    animation = template_config.get('animation', 'slide_in')
    
    # Create background bar
    bar_height = 100
    if len(bar_color) == 4:
        rgb = tuple(bar_color[:3])
        opacity = bar_color[3] / 255
    else:
        rgb = tuple(bar_color)
        opacity = 1.0
    
    if MOVIEPY_V2:
        bar = ColorClip(size=(vw, bar_height), color=rgb, duration=clip_duration)
        bar = bar.with_opacity(opacity)
        bar = bar.with_start(start_time)
        bar = bar.with_position(('center', vh - bar_height))
        
        # Create title clip
        title_clip = TextClip(
            text=title, 
            font_size=title_fontsize, 
            color=title_color, 
            font='DejaVu-Sans-Bold',
            duration=clip_duration
        )
        title_clip = title_clip.with_start(start_time)
        title_clip = title_clip.with_position((50, vh - bar_height + 15))
        
        # Create subtitle clip
        subtitle_clip = TextClip(
            text=subtitle, 
            font_size=subtitle_fontsize, 
            color=subtitle_color, 
            font='DejaVu-Sans',
            duration=clip_duration
        )
        subtitle_clip = subtitle_clip.with_start(start_time)
        subtitle_clip = subtitle_clip.with_position((50, vh - bar_height + 55))
    else:
        bar = ColorClip(size=(vw, bar_height), color=rgb)
        bar = bar.set_opacity(opacity)
        bar = bar.set_duration(clip_duration)
        bar = bar.set_start(start_time)
        bar = bar.set_pos(('center', vh - bar_height))
        
        # Create title clip
        title_clip = TextClip(title, fontsize=title_fontsize, color=title_color, font='DejaVu-Sans-Bold')
        title_clip = title_clip.set_duration(clip_duration)
        title_clip = title_clip.set_start(start_time)
        title_clip = title_clip.set_pos((50, vh - bar_height + 15))
        
        # Create subtitle clip
        subtitle_clip = TextClip(subtitle, fontsize=subtitle_fontsize, color=subtitle_color, font='DejaVu-Sans')
        subtitle_clip = subtitle_clip.set_duration(clip_duration)
        subtitle_clip = subtitle_clip.set_start(start_time)
        subtitle_clip = subtitle_clip.set_pos((50, vh - bar_height + 55))
    
    # Apply animation
    if animation in ['fade', 'slide_in']:
        bar = apply_fade(bar, fade_in=True, duration=0.3)
        bar = apply_fade(bar, fade_in=False, duration=0.3)
        title_clip = apply_fade(title_clip, fade_in=True, duration=0.3)
        title_clip = apply_fade(title_clip, fade_in=False, duration=0.3)
        subtitle_clip = apply_fade(subtitle_clip, fade_in=True, duration=0.3)
        subtitle_clip = apply_fade(subtitle_clip, fade_in=False, duration=0.3)
    
    return [bar, title_clip, subtitle_clip]

def add_lower_third(input_video, output_video, title, subtitle, template, start_time=2, duration=None):
    """Add a lower third to a video.
    
    Args:
        input_video: Path to input video file.
        output_video: Path to output video file.
        title: Main title text.
        subtitle: Subtitle text.
        template: Template name (business, cartoon, tech).
        start_time: When to start showing the lower third.
        duration: How long to show the lower third.
    """
    presets = load_presets()
    template_config = presets.get('lower_thirds', {}).get(template, presets['lower_thirds']['business'])
    
    video_clip = VideoFileClip(input_video)
    
    lower_third_clips = create_lower_third(
        title, subtitle, template_config, video_clip.size, start_time, duration
    )
    
    final_clip = CompositeVideoClip([video_clip] + lower_third_clips)
    final_clip.write_videofile(output_video, codec='libx264', audio_codec='aac')
    
    # Clean up
    video_clip.close()
    final_clip.close()

def main():
    parser = argparse.ArgumentParser(
        description='Add a lower third title bar to a video.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --input video.mp4 --output output.mp4 --title "John Doe" --subtitle "CEO, Company Inc."
  %(prog)s --input video.mp4 --output output.mp4 --title "Speaker" --subtitle "Topic" --template tech --start 5
        """
    )
    parser.add_argument('--input', required=True, help='Input video file path')
    parser.add_argument('--output', required=True, help='Output video file path')
    parser.add_argument('--title', required=True, help='Main title text')
    parser.add_argument('--subtitle', required=True, help='Subtitle text')
    parser.add_argument('--template', default='business',
                        choices=['business', 'cartoon', 'tech'],
                        help='Lower third template (default: business)')
    parser.add_argument('--start', type=float, default=2,
                        help='Start time in seconds (default: 2)')
    parser.add_argument('--duration', type=float, default=None,
                        help='Duration in seconds (default: from template)')
    
    args = parser.parse_args()
    add_lower_third(args.input, args.output, args.title, args.subtitle, 
                    args.template, args.start, args.duration)
    print(f"Successfully added lower third and saved to {args.output}")

if __name__ == '__main__':
    main()
