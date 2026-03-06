#!/usr/bin/env python3
"""
MISO Progress GIF Generator
Issue #2: 21フレームアニメーションGIF生成

仕様:
- GIF: 21フレーム（0%-100% 5%刻み）
- サイズ: 400x40px
- 配色: オレンジ/黄色グラデーション (#FF8C42 → #FFD700)
- 背景: ダークグレー (#1A1A1A)
- 配置先: assets/progress/progress.gif
"""

from PIL import Image, ImageDraw
import os

# ===== 設定 =====
WIDTH = 400
HEIGHT = 40
BG_COLOR = (26, 26, 26)        # #1A1A1A ダークグレー
COLOR_START = (255, 140, 66)   # #FF8C42 オレンジ
COLOR_END = (255, 215, 0)      # #FFD700 イエロー
FRAME_DURATION = 120           # ms per frame
BAR_PADDING = 4                # px padding around bar
BAR_HEIGHT = HEIGHT - BAR_PADDING * 2
BAR_RADIUS = 4                 # rounded corner radius

OUTPUT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "assets", "progress", "progress.gif"
)


def lerp_color(c1, c2, t):
    """2色間を線形補間"""
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def draw_rounded_rect(draw, xy, radius, fill):
    """角丸矩形を描画"""
    x0, y0, x1, y1 = xy
    draw.rectangle([x0 + radius, y0, x1 - radius, y1], fill=fill)
    draw.rectangle([x0, y0 + radius, x1, y1 - radius], fill=fill)
    draw.ellipse([x0, y0, x0 + radius * 2, y0 + radius * 2], fill=fill)
    draw.ellipse([x1 - radius * 2, y0, x1, y0 + radius * 2], fill=fill)
    draw.ellipse([x0, y1 - radius * 2, x0 + radius * 2, y1], fill=fill)
    draw.ellipse([x1 - radius * 2, y1 - radius * 2, x1, y1], fill=fill)


def create_frame(progress: float) -> Image.Image:
    """
    1フレームを生成

    Args:
        progress: 0.0〜1.0 の進捗率

    Returns:
        PIL Image (RGB)
    """
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    if progress > 0:
        bar_width = int((WIDTH - BAR_PADDING * 2) * progress)
        if bar_width > 0:
            x0 = BAR_PADDING
            y0 = BAR_PADDING
            x1 = x0 + bar_width
            y1 = y0 + BAR_HEIGHT

            # グラデーション（ピクセル列ごとに色補間）
            for x in range(x0, x1):
                t = (x - x0) / max(bar_width - 1, 1)
                color = lerp_color(COLOR_START, COLOR_END, t)
                draw.line([(x, y0), (x, y1)], fill=color)

    return img


def generate_gif():
    """21フレームのアニメーションGIFを生成"""
    frames = []
    percentages = list(range(0, 101, 5))  # 0, 5, 10, ..., 100

    print(f"Generating {len(percentages)} frames...")
    for pct in percentages:
        progress = pct / 100.0
        frame = create_frame(progress)
        frames.append(frame)
        print(f"  Frame {pct:3d}%: bar_width={int((WIDTH - BAR_PADDING * 2) * progress)}px")

    # GIF保存
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    frames[0].save(
        OUTPUT_PATH,
        save_all=True,
        append_images=frames[1:],
        duration=FRAME_DURATION,
        loop=0,
        optimize=False,
    )

    size_kb = os.path.getsize(OUTPUT_PATH) / 1024
    print(f"\n✅ GIF generated: {OUTPUT_PATH}")
    print(f"   Frames: {len(frames)}")
    print(f"   Size: {WIDTH}x{HEIGHT}px")
    print(f"   File size: {size_kb:.1f} KB")
    print(f"   Duration: {FRAME_DURATION * len(frames)}ms ({FRAME_DURATION}ms/frame)")


if __name__ == "__main__":
    generate_gif()
