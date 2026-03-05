#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Add watermark or border to a video.
"""

import argparse
import json
import os

# MoviePy 2.x compatibility
try:
    from moviepy import VideoFileClip, ImageClip, CompositeVideoClip, ColorClip
    MOVIEPY_V2 = True
except ImportError:
    from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip, ColorClip
    MOVIEPY_V2 = False

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PRESETS_PATH = os.path.join(SCRIPT_DIR, '..', 'templates', 'presets.json')

def load_presets():
    """Load preset configurations from JSON file."""
    with open(PRESETS_PATH, 'r') as f:
        return json.load(f)

def get_position(position_name, video_size, watermark_size, margin=10):
    """Calculate position based on position name."""
    vw, vh = video_size
    ww, wh = watermark_size
    
    positions = {
        'top-left': (margin, margin),
        'top-right': (vw - ww - margin, margin),
        'bottom-left': (margin, vh - wh - margin),
        'bottom-right': (vw - ww - margin, vh - wh - margin),
        'center': ((vw - ww) // 2, (vh - wh) // 2)
    }
    
    return positions.get(position_name, positions['bottom-right'])

def add_watermark(input_video, output_video, image_path, position, opacity=0.7, scale=None):
    """Add a watermark to a video.
    
    Args:
        input_video: Path to input video file.
        output_video: Path to output video file.
        image_path: Path to watermark image.
        position: Position name (top-left, top-right, bottom-left, bottom-right, center).
        opacity: Watermark opacity (0-1).
        scale: Scale factor for watermark size.
    """
    video_clip = VideoFileClip(input_video)
    watermark = ImageClip(image_path)
    
    if MOVIEPY_V2:
        # Scale watermark if specified
        if scale:
            watermark = watermark.resized(scale)
        
        # Set opacity and duration
        watermark = watermark.with_opacity(opacity)
        watermark = watermark.with_duration(video_clip.duration)
        
        # Calculate and set position
        pos = get_position(position, video_clip.size, watermark.size)
        watermark = watermark.with_position(pos)
    else:
        # Scale watermark if specified
        if scale:
            watermark = watermark.resize(scale)
        
        # Set opacity
        watermark = watermark.set_opacity(opacity)
        
        # Set duration
        watermark = watermark.set_duration(video_clip.duration)
        
        # Calculate and set position
        pos = get_position(position, video_clip.size, watermark.size)
        watermark = watermark.set_pos(pos)
    
    final_clip = CompositeVideoClip([video_clip, watermark])
    final_clip.write_videofile(output_video, codec='libx264', audio_codec='aac')
    
    # Clean up
    video_clip.close()
    final_clip.close()

def add_border(input_video, output_video, border_color, border_width=10):
    """Add a border to a video.
    
    Args:
        input_video: Path to input video file.
        output_video: Path to output video file.
        border_color: Border color (name or hex).
        border_width: Border width in pixels.
    """
    video_clip = VideoFileClip(input_video)
    vw, vh = video_clip.size
    
    # Parse color
    if border_color.startswith('#'):
        hex_color = border_color.lstrip('#')
        color = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    else:
        color_map = {
            'white': (255, 255, 255),
            'black': (0, 0, 0),
            'red': (255, 0, 0),
            'green': (0, 255, 0),
            'blue': (0, 0, 255)
        }
        color = color_map.get(border_color.lower(), (255, 255, 255))
    
    # Create border frame
    new_size = (vw + 2 * border_width, vh + 2 * border_width)
    
    if MOVIEPY_V2:
        border_clip = ColorClip(size=new_size, color=color, duration=video_clip.duration)
        video_clip = video_clip.with_position((border_width, border_width))
    else:
        border_clip = ColorClip(size=new_size, color=color)
        border_clip = border_clip.set_duration(video_clip.duration)
        video_clip = video_clip.set_pos((border_width, border_width))
    
    final_clip = CompositeVideoClip([border_clip, video_clip], size=new_size)
    final_clip.write_videofile(output_video, codec='libx264', audio_codec='aac')
    
    # Clean up
    video_clip.close()
    final_clip.close()

def main():
    parser = argparse.ArgumentParser(
        description='Add a watermark or border to a video.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --input video.mp4 --output output.mp4 --image logo.png --position bottom-right
  %(prog)s --input video.mp4 --output output.mp4 --image logo.png --position center --opacity 0.5
  %(prog)s --input video.mp4 --output output.mp4 --border-color white --border-width 20
        """
    )
    parser.add_argument('--input', required=True, help='Input video file path')
    parser.add_argument('--output', required=True, help='Output video file path')
    parser.add_argument('--image', help='Watermark image file path')
    parser.add_argument('--position', default='bottom-right',
                        choices=['top-left', 'top-right', 'bottom-left', 'bottom-right', 'center'],
                        help='Watermark position (default: bottom-right)')
    parser.add_argument('--opacity', type=float, default=0.7,
                        help='Watermark opacity 0-1 (default: 0.7)')
    parser.add_argument('--scale', type=float, default=None,
                        help='Scale factor for watermark')
    parser.add_argument('--border-color', help='Border color (name or hex)')
    parser.add_argument('--border-width', type=int, default=10,
                        help='Border width in pixels (default: 10)')
    
    args = parser.parse_args()
    
    if args.image:
        add_watermark(args.input, args.output, args.image, args.position, args.opacity, args.scale)
        print(f"Successfully added watermark and saved to {args.output}")
    elif args.border_color:
        add_border(args.input, args.output, args.border_color, args.border_width)
        print(f"Successfully added border and saved to {args.output}")
    else:
        print("Error: Please specify either --image for watermark or --border-color for border")

if __name__ == '__main__':
    main()
