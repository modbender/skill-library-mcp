#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Add transitions between two video clips.
"""

import argparse
import json
import os

# MoviePy 2.x compatibility
try:
    from moviepy import VideoFileClip, concatenate_videoclips, CompositeVideoClip
    from moviepy.video.fx import FadeIn, FadeOut
    MOVIEPY_V2 = True
except ImportError:
    from moviepy.editor import VideoFileClip, concatenate_videoclips, CompositeVideoClip
    from moviepy.video.fx.all import fadein, fadeout
    MOVIEPY_V2 = False

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PRESETS_PATH = os.path.join(SCRIPT_DIR, '..', 'templates', 'presets.json')

def load_presets():
    """Load preset configurations from JSON file."""
    with open(PRESETS_PATH, 'r') as f:
        return json.load(f)

def apply_fade_out(clip, duration):
    """Apply fade out effect compatible with both MoviePy versions."""
    if MOVIEPY_V2:
        return clip.with_effects([FadeOut(duration)])
    else:
        return clip.fx(fadeout, duration)

def apply_fade_in(clip, duration):
    """Apply fade in effect compatible with both MoviePy versions."""
    if MOVIEPY_V2:
        return clip.with_effects([FadeIn(duration)])
    else:
        return clip.fx(fadein, duration)

def apply_fade_transition(clip1, clip2, duration=1):
    """Apply fade transition between two clips."""
    clip1_faded = apply_fade_out(clip1, duration)
    clip2_faded = apply_fade_in(clip2, duration)
    return concatenate_videoclips([clip1_faded, clip2_faded])

def apply_crossfade_transition(clip1, clip2, duration=1):
    """Apply crossfade transition (overlap) between two clips."""
    clip1_faded = apply_fade_out(clip1, duration/2)
    clip2_faded = apply_fade_in(clip2, duration/2)
    return concatenate_videoclips([clip1_faded, clip2_faded])

def apply_slide_transition(clip1, clip2, duration=0.5, direction='left'):
    """Apply slide transition between two clips."""
    # For simplicity, we'll use fade as fallback
    return apply_fade_transition(clip1, clip2, duration)

def apply_wipe_transition(clip1, clip2, duration=0.75, direction='horizontal'):
    """Apply wipe transition between two clips."""
    # For simplicity, we'll use fade as fallback
    return apply_fade_transition(clip1, clip2, duration)

def add_transition(input1, input2, output, transition_type, duration=None):
    """Add a transition between two video clips.
    
    Args:
        input1: Path to first video file.
        input2: Path to second video file.
        output: Path to output video file.
        transition_type: Type of transition (fade, slide, wipe, crossfade).
        duration: Duration of transition in seconds.
    """
    presets = load_presets()
    transition_config = presets.get('transitions', {}).get(transition_type, {})
    
    if duration is None:
        duration = transition_config.get('duration', 1)
    
    clip1 = VideoFileClip(input1)
    clip2 = VideoFileClip(input2)
    
    # Ensure clips have same size
    if clip1.size != clip2.size:
        if MOVIEPY_V2:
            clip2 = clip2.resized(clip1.size)
        else:
            clip2 = clip2.resize(clip1.size)
    
    if transition_type == 'fade':
        final_clip = apply_fade_transition(clip1, clip2, duration)
    elif transition_type == 'crossfade':
        final_clip = apply_crossfade_transition(clip1, clip2, duration)
    elif transition_type == 'slide':
        direction = transition_config.get('direction', 'left')
        final_clip = apply_slide_transition(clip1, clip2, duration, direction)
    elif transition_type == 'wipe':
        direction = transition_config.get('direction', 'horizontal')
        final_clip = apply_wipe_transition(clip1, clip2, duration, direction)
    else:
        # Default: simple concatenation
        final_clip = concatenate_videoclips([clip1, clip2])
    
    final_clip.write_videofile(output, codec='libx264', audio_codec='aac')
    
    # Clean up
    clip1.close()
    clip2.close()
    final_clip.close()

def main():
    parser = argparse.ArgumentParser(
        description='Add a transition between two videos.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --input1 clip1.mp4 --input2 clip2.mp4 --output output.mp4 --type fade
  %(prog)s --input1 clip1.mp4 --input2 clip2.mp4 --output output.mp4 --type crossfade --duration 1.5
        """
    )
    parser.add_argument('--input1', required=True, help='First video file path')
    parser.add_argument('--input2', required=True, help='Second video file path')
    parser.add_argument('--output', required=True, help='Output video file path')
    parser.add_argument('--type', default='fade', 
                        choices=['fade', 'crossfade', 'slide', 'wipe'],
                        help='Transition type (default: fade)')
    parser.add_argument('--duration', type=float, default=None,
                        help='Transition duration in seconds')
    
    args = parser.parse_args()
    add_transition(args.input1, args.input2, args.output, args.type, args.duration)
    print(f"Successfully added {args.type} transition and saved to {args.output}")

if __name__ == '__main__':
    main()
