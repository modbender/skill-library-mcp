#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Add subtitles or titles to a video with various styles.
"""

import argparse
import json
import os

# MoviePy 2.x compatibility
try:
    from moviepy import VideoFileClip, TextClip, CompositeVideoClip
    MOVIEPY_V2 = True
except ImportError:
    from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
    MOVIEPY_V2 = False

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PRESETS_PATH = os.path.join(SCRIPT_DIR, '..', 'templates', 'presets.json')

def load_presets():
    """Load preset configurations from JSON file."""
    with open(PRESETS_PATH, 'r') as f:
        return json.load(f)

def time_to_seconds(time_str):
    """Convert HH:MM:SS format to seconds."""
    parts = time_str.split(':')
    if len(parts) == 3:
        h, m, s = map(float, parts)
        return h * 3600 + m * 60 + s
    elif len(parts) == 2:
        m, s = map(float, parts)
        return m * 60 + s
    else:
        return float(time_str)

def add_subtitles(input_video, output_video, text, start_time, end_time, style):
    """Add subtitles to a video.
    
    Args:
        input_video: Path to input video file.
        output_video: Path to output video file.
        text: Subtitle text to display.
        start_time: Start time in seconds.
        end_time: End time in seconds.
        style: Style name (simple, animated, karaoke).
    """
    presets = load_presets()
    style_config = presets.get('subtitles', {}).get(style, presets['subtitles']['simple'])
    
    video_clip = VideoFileClip(input_video)
    
    fontsize = style_config.get('fontsize', 50)
    color = style_config.get('color', 'yellow')
    bg_color = style_config.get('bg_color', 'black')
    position = style_config.get('position', 'bottom')
    
    duration = end_time - start_time
    
    # Create text clip
    if MOVIEPY_V2:
        txt_clip = TextClip(
            text=text, 
            font_size=fontsize, 
            color=color,
            bg_color=bg_color if bg_color != 'transparent' else None,
            font='DejaVu-Sans',
            duration=duration
        )
        txt_clip = txt_clip.with_start(start_time)
        
        # Set position
        if position == 'bottom':
            txt_clip = txt_clip.with_position(('center', 0.85), relative=True)
        elif position == 'top':
            txt_clip = txt_clip.with_position(('center', 0.1), relative=True)
        else:
            txt_clip = txt_clip.with_position('center')
    else:
        txt_clip = TextClip(
            text, 
            fontsize=fontsize, 
            color=color,
            bg_color=bg_color if bg_color != 'transparent' else None,
            font='DejaVu-Sans',
            method='caption',
            size=(int(video_clip.w * 0.9), None)
        )
        txt_clip = txt_clip.set_duration(duration)
        txt_clip = txt_clip.set_start(start_time)
        
        # Set position
        if position == 'bottom':
            txt_clip = txt_clip.set_pos(('center', 0.85), relative=True)
        elif position == 'top':
            txt_clip = txt_clip.set_pos(('center', 0.1), relative=True)
        else:
            txt_clip = txt_clip.set_pos('center')
    
    final_clip = CompositeVideoClip([video_clip, txt_clip])
    final_clip.write_videofile(output_video, codec='libx264', audio_codec='aac')
    
    # Clean up
    video_clip.close()
    final_clip.close()

def main():
    parser = argparse.ArgumentParser(
        description='Add subtitles to a video.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --input video.mp4 --output output.mp4 --text "Hello World" --start 00:00:05 --end 00:00:10
  %(prog)s --input video.mp4 --output output.mp4 --text "Welcome" --start 0 --end 5 --style animated
        """
    )
    parser.add_argument('--input', required=True, help='Input video file path')
    parser.add_argument('--output', required=True, help='Output video file path')
    parser.add_argument('--text', required=True, help='Subtitle text')
    parser.add_argument('--start', required=True, help='Start time (HH:MM:SS or seconds)')
    parser.add_argument('--end', required=True, help='End time (HH:MM:SS or seconds)')
    parser.add_argument('--style', default='simple', 
                        choices=['simple', 'animated', 'karaoke'],
                        help='Subtitle style (default: simple)')
    
    args = parser.parse_args()
    
    start_seconds = time_to_seconds(args.start)
    end_seconds = time_to_seconds(args.end)
    
    add_subtitles(args.input, args.output, args.text, start_seconds, end_seconds, args.style)
    print(f"Successfully added subtitles and saved to {args.output}")

if __name__ == '__main__':
    main()
