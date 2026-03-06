#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["moviepy>=2.0", "pillow>=10.0", "numpy"]
# ///
"""TikTok Overlay Engine v3 — Context-aware timing, keep Veo native audio."""

import argparse, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import VideoFileClip, CompositeVideoClip, VideoClip

import os as _os
F_BLACK = _os.path.expanduser("~/.local/share/fonts/Montserrat-Black.ttf")
F_BOLD  = _os.path.expanduser("~/.local/share/fonts/Montserrat-Bold.ttf")
F_DEJA  = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def get_font(path, size):
    try: return ImageFont.truetype(path, size)
    except: return ImageFont.truetype(F_DEJA, size)

def phrase_duration(text, min_dur=0.9, wps=2.8):
    """Auto-calculate how long a phrase should stay on screen."""
    words = len(text.split())
    return max(min_dur, words / wps)

def al(t, s, e, f=0.18):
    fi = min(1.0,(t-s)/f) if t>s else 0.0
    fo = 1.0-min(1.0,(t-(e-f))/f) if t>(e-f) else 1.0
    return int(255*max(0.0,min(fi,fo)))

def pill(draw, text, font, cx, y, bg, fg, px=24, py=12, r=16):
    bb = draw.textbbox((0,0),text,font=font)
    xo,yo=bb[0],bb[1]; vw=bb[2]-bb[0]; vh=bb[3]-bb[1]
    draw.rounded_rectangle([cx-vw//2-px,y-py,cx+vw//2+(vw%2)+px,y+vh+py],radius=r,fill=bg)
    draw.text((cx-vw//2-xo,y-yo),text,font=font,fill=fg)
    return vh+py*2+8

def stroke_text(draw, text, font, cx, y, fg, sw=4, max_w=None, img_w=720):
    """Auto-scale font down if text would overflow safe zone."""
    safe_w = max_w or int(img_w * 0.88)
    # Measure and scale down if needed
    actual_font = font
    bb = draw.textbbox((0,0), text, font=actual_font)
    vw = bb[2]-bb[0]
    if vw > safe_w:
        # Estimate new size
        scale = safe_w / vw
        new_size = max(28, int(actual_font.size * scale))
        actual_font = get_font(actual_font.path if hasattr(actual_font, "path") else F_BLACK, new_size)
        bb = draw.textbbox((0,0), text, font=actual_font)
    xo,yo=bb[0],bb[1]; vw=bb[2]-bb[0]; vh=bb[3]-bb[1]
    x = cx-vw//2-xo
    draw.text((x,y-yo),text,font=actual_font,fill=(0,0,0,fg[3]),stroke_width=sw,stroke_fill=(0,0,0,fg[3]))
    draw.text((x,y-yo),text,font=actual_font,fill=fg)
    return vh

# ── Product scripts ─────────────────────────────────────────────────────────
# Durations are now AUTO-CALCULATED from word count — no hardcoding

def make_script(phrases_with_size, accent):
    """phrases_with_size = list of (text, font_size)"""
    return [(text, phrase_duration(text), size) for text, size in phrases_with_size]

PRODUCTS = {
    'rain_cloud': {
        'accent': (140,180,255),
        'cta': '129 AED',
        'hook': [
            ("your room feels like a desert.", 72),   # 6 words = 2.1s
            ("we fixed that.", 80),                    # 3 words = 1.1s
        ],
        'claim': [
            ("rain cloud humidifier.", 54),            # 3 words
            ("soft mist. cozy vibes.", 62),            # 4 words
            ("every single night.", 72),               # 3 words
        ],
    },
    'hydro_bottle': {
        'accent': (0,200,255),
        'cta': '149 AED',
        'hook': [
            ("i said i'd drink more water.", 68),      # 7 words = 2.5s
            ("i lied.", 90),                           # 2 words = SHORT = punch
        ],
        'claim': [
            ("then i got hydrogen water.", 64),        # 5 words
            ("3 liters a day now.", 72),               # 5 words
            ("no more excuses.", 80),                  # 3 words
        ],
    },
    'mini_cam': {
        'accent': (255,100,60),
        'cta': '89 AED',
        'hook': [
            ("your phone camera is mid.", 72),         # 5 words = 1.8s
            ("this one isn't.", 82),                   # 3 words = 1.1s
        ],
        'claim': [
            ("mini clip cam.", 74),                    # 3 words
            ("fits in your pocket.", 66),              # 4 words
            ("content that actually slaps.", 64),      # 4 words
        ],
    },
}

# ── STYLE: Phrase Slam ───────────────────────────────────────────────────────
def style_phrase_slam(t, w, h, hook, claim, cta, accent, duration):
    img = Image.new('RGBA',(w,h),(0,0,0,0))
    draw = ImageDraw.Draw(img)
    cx = w//2; cy = int(h*0.44)

    cta_start = duration - 2.8
    content = hook + claim
    cursor = 0.0

    for text, dur, size in content:
        end = cursor + dur
        if cursor - 0.05 <= t < end + 0.12 and t < cta_start:
            a = al(t, cursor, end + 0.1, f=0.15)
            # Pop scale on entry only
            elapsed = t - cursor
            scale = max(1.0, 1.1 - elapsed * 0.8) if elapsed < 0.13 else 1.0
            fsize = int(size * scale)
            f = get_font(F_BLACK, fsize)
            stroke_text(draw, text, f, cx, cy, (*accent, a), sw=4, img_w=w)
        cursor += dur
        if cursor >= cta_start: break

    if t >= cta_start:
        a = al(t, cta_start, duration)
        y = int(h*0.76)
        y += pill(draw, cta, get_font(F_BLACK,56), cx, y, (255,210,0,int(a*.97)), (0,0,0,a), px=30,py=14,r=20)
        y += pill(draw, "Free delivery UAE", get_font(F_BOLD,30), cx, y, (20,20,20,int(a*.9)), (255,255,255,a))
        pill(draw, "Link in bio", get_font(F_BOLD,30), cx, y, (255,210,0,int(a*.9)), (0,0,0,a))

    return np.array(img)

# ── STYLE: Subtitle Talk ────────────────────────────────────────────────────
def style_subtitle_talk(t, w, h, hook, claim, cta, accent, duration):
    img = Image.new('RGBA',(w,h),(0,0,0,0))
    draw = ImageDraw.Draw(img)
    cx = w//2; bar_y = int(h*0.79)
    cta_start = duration - 2.8
    content = hook + claim
    cursor = 0.0

    for text, dur, size in content:
        end = cursor + dur
        if cursor - 0.05 <= t < end + 0.15 and t < cta_start:
            a = al(t, cursor, end + 0.12, f=0.18)
            f = get_font(F_BLACK, size)
            bb = draw.textbbox((0,0), text.lower(), font=f)
            xo,yo=bb[0],bb[1]; vw=bb[2]-bb[0]; vh=bb[3]-bb[1]
            pad = 18
            draw.rectangle([0, bar_y-pad, w, bar_y+vh+pad], fill=(0,0,0,int(a*0.78)))
            draw.text((cx-vw//2-xo, bar_y-yo), text.lower(), font=f, fill=(255,255,255,a))
        cursor += dur
        if cursor >= cta_start: break

    if t >= cta_start:
        a = al(t, cta_start, duration)
        y = int(h*0.06)
        y += pill(draw, cta, get_font(F_BLACK,56), cx, y, (255,210,0,int(a*.97)), (0,0,0,a), px=30,py=14,r=20)
        y += pill(draw,"Free delivery UAE",get_font(F_BOLD,30),cx,y,(20,20,20,int(a*.9)),(255,255,255,a))
        pill(draw,"Link in bio",get_font(F_BOLD,30),cx,y,(255,210,0,int(a*.9)),(0,0,0,a))

    return np.array(img)

# ── STYLE: Big Center ───────────────────────────────────────────────────────
def style_big_center(t, w, h, hook, claim, cta, accent, duration):
    """Large centered text with price bar at top. Best for bold product reveals."""
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx = w // 2
    cy = int(h * 0.50)

    # ── Top price bar (always visible) ──────────────────────────────────────
    bar_h = 70
    draw.rectangle([0, 0, w, bar_h], fill=(15, 15, 15, 220))
    price_font = get_font(F_BLACK, 38)
    bb = draw.textbbox((0, 0), cta, font=price_font)
    pw = bb[2] - bb[0]; ph = bb[3] - bb[1]
    draw.text(
        (cx - pw // 2 - bb[0], (bar_h - ph) // 2 - bb[1]),
        cta, font=price_font, fill=(255, 215, 0, 230)
    )

    # ── Centered phrases with timing ─────────────────────────────────────────
    content = hook + claim
    cursor = 0.0
    for text, dur, size in content:
        end = cursor + dur
        if cursor - 0.05 <= t < end + 0.12:
            a = al(t, cursor, end + 0.1, f=0.16)
            elapsed = t - cursor
            scale = max(1.0, 1.08 - elapsed * 0.7) if elapsed < 0.15 else 1.0
            fsize = int(size * scale)
            f = get_font(F_BLACK, fsize)
            bb2 = draw.textbbox((0, 0), text, font=f)
            xo, yo = bb2[0], bb2[1]
            vw = bb2[2] - bb2[0]; vh = bb2[3] - bb2[1]
            x = cx - vw // 2 - xo
            y = cy - vh // 2 - yo
            draw.text((x, y), text, font=f,
                      fill=(0, 0, 0, a), stroke_width=4, stroke_fill=(0, 0, 0, a))
            draw.text((x, y), text, font=f, fill=(*accent, a))
        cursor += dur

    return np.array(img)

STYLES = {
    'phrase_slam':   style_phrase_slam,
    'subtitle_talk': style_subtitle_talk,
    'big_center':    style_big_center,
}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--video',   required=True)
    ap.add_argument('--output',  required=True)
    ap.add_argument('--product', required=True, choices=list(PRODUCTS.keys()))
    ap.add_argument('--style',   default='random', choices=list(STYLES.keys()) + ['random'])
    args = ap.parse_args()

    p = PRODUCTS[args.product]
    hook  = make_script(p['hook'],  p['accent'])
    claim = make_script(p['claim'], p['accent'])
    cta   = p['cta']
    accent = p['accent']

    style_name = random.choice(list(STYLES.keys())) if args.style=='random' else args.style
    style_fn   = STYLES[style_name]
    print(f"Style: {style_name} | Product: {args.product}")

    # Keep Veo native audio — no override
    video = VideoFileClip(args.video)
    w,h   = video.size
    dur   = video.duration

    total_content = sum(d for _,d,_ in hook+claim) + 2.8
    print(f"Script duration: {total_content:.1f}s | Video: {dur:.1f}s")
    # Auto-compress: if script longer than video, scale phrase durations down
    available = dur - 2.8  # time for phrases (CTA takes 2.8s)
    phrase_total = sum(d for _,d,_ in hook+claim)
    if phrase_total > available:
        ratio = available / phrase_total
        hook  = [(t, d*ratio, s) for t,d,s in hook]
        claim = [(t, d*ratio, s) for t,d,s in claim]
        print(f"  Compressed to fit: ratio={ratio:.2f}")

    def make_frame(t):
        return style_fn(t, w, h, hook, claim, cta, accent, dur)

    overlay = VideoClip(make_frame, duration=dur).with_fps(video.fps)
    final   = CompositeVideoClip([video, overlay])
    final.write_videofile(args.output, codec='libx264', audio_codec='aac', fps=video.fps, logger=None)
    print(f"Done! → {args.output}")

if __name__ == '__main__':
    main()
