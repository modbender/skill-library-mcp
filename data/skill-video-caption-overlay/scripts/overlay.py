#!/usr/bin/env python3
"""
TikTok-style animated pill caption overlay for short-form videos.

Usage:
  uv run --with moviepy --with pillow overlay.py \
    --video base.mp4 \
    --audio music.mp3 \
    --output final.mp4 \
    --captions captions.json

captions.json format: see --help or README in SKILL.md

Dependencies (auto-installed by uv):
  moviepy, pillow
"""
import argparse, json, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import VideoFileClip, AudioFileClip, CompositeVideoClip, VideoClip


# ── Core pill renderer ──────────────────────────────────────────────────────

def pill(draw: ImageDraw.Draw, text: str, font_path: str, size: int,
         cx: int, y: int, bg: tuple, fg: tuple,
         px: int = 26, py: int = 13, r: int = 18) -> int:
    """
    Render a rounded pill with perfectly centered text.

    PIL's textbbox() returns a non-zero y-offset (typically 7–15px depending on
    font size) which causes text to draw outside the pill if not compensated.
    This function accounts for exact (x0, y0) offsets from textbbox.

    Args:
        draw:      PIL ImageDraw instance
        text:      Text to render
        font_path: Absolute path to .ttf font file
        size:      Font size in px
        cx:        Horizontal center of the pill
        y:         TOP of the pill's visual content area (not baseline)
        bg:        Background RGBA tuple
        fg:        Foreground (text) RGBA tuple
        px:        Horizontal padding
        py:        Vertical padding
        r:         Border radius

    Returns:
        Total height consumed (pill height + 10px gap) — add to y for next pill
    """
    font  = ImageFont.truetype(font_path, size)
    bb    = draw.textbbox((0, 0), text, font=font)
    x_off, y_off = bb[0], bb[1]
    vis_w = bb[2] - bb[0]
    vis_h = bb[3] - bb[1]

    pill_x0 = cx - vis_w // 2 - px
    pill_y0 = y - py
    pill_x1 = cx + vis_w // 2 + (vis_w % 2) + px
    pill_y1 = y + vis_h + py
    draw.rounded_rectangle([pill_x0, pill_y0, pill_x1, pill_y1], radius=r, fill=bg)

    tx = cx - vis_w // 2 - x_off
    ty = y - y_off
    draw.text((tx, ty), text, font=font, fill=fg)

    return vis_h + py * 2 + 10


# ── Alpha animation ─────────────────────────────────────────────────────────

def alpha(t: float, start: float, end: float, fade: float = 0.3) -> int:
    """Fade in/out alpha value (0–255) for a caption phase."""
    fade_in  = min(1.0, (t - start) / fade) if t > start else 0.0
    fade_out = 1.0 - min(1.0, (t - (end - fade)) / fade) if t > (end - fade) else 1.0
    return int(255 * max(0.0, min(fade_in, fade_out)))


# ── Frame renderer ──────────────────────────────────────────────────────────

def make_overlay_frame(t: float, captions: list, w: int, h: int,
                       font_black: str, font_bold: str) -> np.ndarray:
    """
    Generate a single RGBA overlay frame for time t.

    captions: list of phase dicts (see captions.json format in SKILL.md)
    """
    img  = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx   = w // 2

    for phase in captions:
        start = phase['start']
        end   = phase['end']

        if not (start - 0.05 <= t < end + 0.05):
            continue

        a   = alpha(t, start, end)
        y   = int(h * phase.get('y_frac', 0.06))
        gap = phase.get('gap', 10)

        for line in phase['lines']:
            text     = line['text']
            fsize    = line.get('size', 50)
            bold     = line.get('bold', False)
            fpath    = font_bold if bold else font_black
            bg_color = tuple(line.get('bg', [255, 255, 255]))
            fg_color = tuple(line.get('fg', [0, 0, 0]))
            bg_alpha = int(a * line.get('bg_opacity', 0.93))
            fg_alpha = a
            px       = line.get('px', 26)
            py_pad   = line.get('py', 13)
            radius   = line.get('r', 18)

            consumed = pill(
                draw, text, fpath, fsize, cx, y,
                bg=(*bg_color, bg_alpha),
                fg=(*fg_color, fg_alpha),
                px=px, py=py_pad, r=radius
            )
            y += consumed

    return np.array(img)


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='TikTok pill caption overlay')
    parser.add_argument('--video',    required=True, help='Input video path')
    parser.add_argument('--output',   required=True, help='Output video path')
    parser.add_argument('--captions', required=True, help='Captions JSON file path')
    parser.add_argument('--audio',    default=None,  help='Background audio path (optional)')
    parser.add_argument('--audio-start', type=float, default=0, help='Audio clip start (seconds)')
    parser.add_argument('--audio-vol',   type=float, default=0.5, help='Audio volume (0–1)')
    parser.add_argument('--font-black',  default=None, help='Path to heavy/black font .ttf')
    parser.add_argument('--font-bold',   default=None, help='Path to bold font .ttf')
    args = parser.parse_args()

    # Font defaults — override with --font-black / --font-bold
    font_black = args.font_black or '/home/aladdin/.local/share/fonts/Montserrat-Black.ttf'
    font_bold  = args.font_bold  or '/home/aladdin/.local/share/fonts/Montserrat-Bold.ttf'

    with open(args.captions) as f:
        captions = json.load(f)

    video  = VideoFileClip(args.video)
    w, h   = video.size
    dur    = video.duration

    if args.audio:
        clip_end = args.audio_start + dur
        audio = AudioFileClip(args.audio).subclipped(args.audio_start, clip_end)
        audio = audio.with_volume_scaled(args.audio_vol)
        video = video.with_audio(audio)

    overlay = VideoClip(
        lambda t: make_overlay_frame(t, captions, w, h, font_black, font_bold),
        duration=dur
    ).with_fps(video.fps)

    final = CompositeVideoClip([video, overlay])
    final.write_videofile(args.output, codec='libx264', audio_codec='aac',
                          fps=video.fps, logger=None)
    print(f'Done → {args.output}')


if __name__ == '__main__':
    main()
