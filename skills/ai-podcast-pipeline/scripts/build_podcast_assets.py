#!/usr/bin/env python3
"""
Build podcast packaging assets from a QuickView source.
Outputs:
- thumbnail_bg.png (generated via nano-banana-pro skill script)
- thumbnail_final.png (subtitle-style overlays composited)
- telegram_preview_card.png (text-composited card)
- telegram_preview.mp4 (<=20MB target)
- youtube_title_options.txt
- youtube_description.txt
- topics.txt
- source_used.txt
"""

import argparse
import datetime as dt
import os
import re
import subprocess
from pathlib import Path
from urllib.parse import unquote, urlparse

from PIL import Image, ImageDraw, ImageFont

SKILL_DIR = Path(__file__).resolve().parents[1]
WORKSPACE_DIR = SKILL_DIR.parents[1]

# Prefer explicit env override, then common local defaults.
QUARTZ_ROOT = Path(
    os.environ.get(
        'QUARTZ_ROOT',
        '/home/tw2/Documents/n8n/data/shared/syn/8.quartz',
    )
)
NANO_SCRIPT = WORKSPACE_DIR / 'skills/nano-banana-pro/scripts/generate_image.py'
FONT_BOLD = WORKSPACE_DIR / 'skills/youtube-editor/assets/fonts/Paperlogy-ExtraBold.ttf'
TG_MAX_BYTES = 20 * 1024 * 1024


def resolve_source(src: str) -> Path:
    # Only allow HTTPS URLs (block http://)
    if src.startswith('http://'):
        raise ValueError(f"Insecure HTTP not allowed. Use HTTPS: {src}")
    if src.startswith('https://'):
        u = urlparse(src)
        slug = unquote(u.path).strip('/')
        p = QUARTZ_ROOT / f"{slug}.md"
        if p.exists():
            return p
        raise FileNotFoundError(f'Cannot map URL to local md: {src} -> {p}')
    p = Path(src)
    if p.exists():
        return p
    raise FileNotFoundError(src)


def extract_topics(text: str, n: int = 6):
    topics = []
    for line in text.splitlines():
        s = line.strip()
        if s.startswith('### '):
            t = s[4:].strip()
            if any(k in t for k in ['TOP 3', '한줄 요약']):
                continue
            t = re.sub(r'^[0-9]+[.)]?\s*', '', t)
            t = re.sub(r'^[0-9️⃣]+\s*', '', t)
            topics.append(t)
    seen, out = set(), []
    for t in topics:
        k = t.lower()
        if k in seen:
            continue
        seen.add(k)
        out.append(t)
    return out[:n]


def week_label_from_filename(name: str) -> str:
    m = re.search(r'QuickView[-_](\d{2})(\d{2})[-_](\d+)주', name)
    if not m:
        return '이번 주'
    yy, mm, wk = m.groups()
    return f"20{yy}년 {int(mm)}월 {int(wk)}주"


def make_youtube_copy(week_label: str, topics: list[str]):
    core = topics[0] if topics else '이번 주 AI 핵심 이슈'
    titles = [
        f"{week_label} AI 딥다이브 | 바쁜 직장인용 20분 실전 적용",
        f"{core}부터 실행법까지: {week_label} AI 팟캐스트",
        f"캘리 박사 x 닉 교수 | {week_label} AI 뉴스, 오늘 바로 적용",
    ]

    stamps = []
    for i, t in enumerate(topics[:5], 1):
        mm = (i - 1) * 3
        stamps.append(f"{mm:02d}:00 {t}")

    desc = []
    desc.append(f"이번 에피소드는 {week_label} AI 이슈를 '바쁜 직장인 실무' 관점으로 재해석합니다.")
    desc.append("캘리 박사(심리/정신과) x 닉 교수(정보통신/AI) 듀엣 토론으로, 1번 듣고 바로 적용 가능한 액션을 제시합니다.")
    desc.append('')
    desc.append('⏱️ 타임라인')
    desc.extend(stamps or ['00:00 이번 주 핵심 브리핑'])
    desc.append('')
    desc.append('✅ 오늘의 실전 체크리스트')
    desc.append('- 업무를 아이디어/정리/검수 3단계로 분리')
    desc.append('- 3-2-1 검증 루틴으로 오답 리스크 차단')
    desc.append('- 하루 20분(5분x4칸) 실행 루틴 도입')
    desc.append('')
    desc.append('#AI뉴스 #직장인AI #NotebookLM #AI자동화 #생산성')
    return titles, '\n'.join(desc)


def generate_bg_with_skill(prompt: str, out_path: Path, resolution: str = '1K'):
    api_key = os.environ.get('GEMINI_API_KEY') or os.environ.get('NANO_BANANA_KEY')
    if not api_key:
        raise RuntimeError('Set GEMINI_API_KEY or NANO_BANANA_KEY')
    if not NANO_SCRIPT.exists():
        raise FileNotFoundError(f'NANO script missing: {NANO_SCRIPT}')

    # Security hardening: provide API key via environment, not CLI args
    # (prevents exposure via process listings).
    env = os.environ.copy()
    env['GEMINI_API_KEY'] = api_key

    cmd = [
        'uv', 'run', str(NANO_SCRIPT),
        '--prompt', prompt,
        '--filename', str(out_path),
        '--resolution', resolution,
    ]
    subprocess.run(cmd, check=True, env=env, timeout=600)


def _fonts():
    if FONT_BOLD.exists():
        return (
            ImageFont.truetype(str(FONT_BOLD), 74),
            ImageFont.truetype(str(FONT_BOLD), 46),
            ImageFont.truetype(str(FONT_BOLD), 34),
            ImageFont.truetype(str(FONT_BOLD), 28),
        )
    d = ImageFont.load_default()
    return d, d, d, d


def compose_thumbnail(bg: Path, out_path: Path, week_label: str, topics: list[str]):
    img = Image.open(bg).convert('RGB').resize((1280, 720))
    overlay = Image.new('RGBA', (1280, 720), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)

    for y in range(720):
        a = int(180 * (y / 720))
        d.line([(0, y), (1280, y)], fill=(0, 0, 0, a))

    f1, f2, f3, f4 = _fonts()

    d.text((56, 42), '일하는 AI : AI DEEP DIVE', font=f2, fill=(255, 255, 255, 235))
    d.text((56, 360), '바쁜 직장인, 오늘 바로 적용', font=f1, fill=(255, 255, 255, 255))
    d.text((56, 455), f'{week_label} · 캘리 박사 × 닉 교수', font=f3, fill=(180, 255, 220, 255))

    key_caps = [t.strip('🎬🚨🗽💥🚀📊💼🌍🤖🐰💰📉🏢 ').strip() for t in topics[:2]]
    y = 530
    for cap in key_caps:
        cap = cap[:42]
        d.rounded_rectangle((56, y, 1220, y + 56), radius=16, fill=(0, 0, 0, 160))
        d.text((78, y + 12), f'• {cap}', font=f4, fill=(255, 255, 255, 245))
        y += 66

    final = Image.alpha_composite(img.convert('RGBA'), overlay)
    final.convert('RGB').save(out_path)


def compose_telegram_card(bg: Path, out_path: Path, week_label: str, title: str, topics: list[str]):
    img = Image.open(bg).convert('RGB').resize((1280, 720))
    overlay = Image.new('RGBA', (1280, 720), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)

    # darker card area
    d.rounded_rectangle((40, 40, 1240, 680), radius=26, fill=(0, 0, 0, 130))

    f1, f2, f3, f4 = _fonts()
    d.text((72, 74), '일하는 AI : AI DEEP DIVE', font=f3, fill=(190, 255, 230, 255))
    d.text((72, 124), title[:38], font=f2, fill=(255, 255, 255, 255))
    d.text((72, 188), f'{week_label} · 캘리 박사 × 닉 교수', font=f4, fill=(230, 230, 230, 255))

    y = 258
    for t in topics[:4]:
        txt = t.strip('🎬🚨🗽💥🚀📊💼🌍🤖🐰💰📉🏢 ').strip()[:54]
        d.rounded_rectangle((72, y, 1190, y + 74), radius=14, fill=(0, 0, 0, 130))
        d.text((94, y + 19), f'• {txt}', font=f4, fill=(255, 255, 255, 245))
        y += 88

    d.text((72, 636), '요약+핵심포인트 영상 (텔레그램 20MB 이하)', font=f4, fill=(180, 220, 255, 255))

    final = Image.alpha_composite(img.convert('RGBA'), overlay)
    final.convert('RGB').save(out_path)


def encode_mp4_from_image(image_path: Path, out_mp4: Path, duration_sec: int = 16, crf: int = 31, scale: str = '1280:720'):
    cmd = [
        'ffmpeg', '-y',
        '-loop', '1',
        '-i', str(image_path),
        '-t', str(duration_sec),
        '-vf', f'scale={scale},format=yuv420p',
        '-c:v', 'libx264',
        '-preset', 'veryfast',
        '-crf', str(crf),
        '-pix_fmt', 'yuv420p',
        '-movflags', '+faststart',
        str(out_mp4),
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=600)


def build_telegram_preview_mp4(card_png: Path, out_mp4: Path):
    # pass 1
    encode_mp4_from_image(card_png, out_mp4, duration_sec=16, crf=31, scale='1280:720')
    if out_mp4.stat().st_size <= TG_MAX_BYTES:
        return

    # pass 2 fallback (smaller)
    encode_mp4_from_image(card_png, out_mp4, duration_sec=14, crf=36, scale='960:540')
    if out_mp4.stat().st_size <= TG_MAX_BYTES:
        return

    # pass 3 hard fallback
    encode_mp4_from_image(card_png, out_mp4, duration_sec=12, crf=40, scale='854:480')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', required=True, help='QuickView md path or wk URL')
    ap.add_argument('--outdir', default='', help='output directory')
    ap.add_argument('--no-image', action='store_true', help='skip thumbnail/video generation')
    args = ap.parse_args()

    src = resolve_source(args.source)
    text = src.read_text(encoding='utf-8', errors='ignore')

    ts = dt.datetime.now().strftime('%Y%m%d_%H%M%S')
    outdir = Path(args.outdir) if args.outdir else WORKSPACE_DIR / 'media_work' / f'podcast_pkg_{ts}'
    outdir.mkdir(parents=True, exist_ok=True)

    week_label = week_label_from_filename(src.name)
    topics = extract_topics(text)
    titles, description = make_youtube_copy(week_label, topics)

    (outdir / 'source_used.txt').write_text(str(src), encoding='utf-8')
    (outdir / 'topics.txt').write_text('\n'.join(topics), encoding='utf-8')
    (outdir / 'youtube_title_options.txt').write_text('\n'.join([f'{i+1}. {t}' for i, t in enumerate(titles)]), encoding='utf-8')
    (outdir / 'youtube_description.txt').write_text(description, encoding='utf-8')

    if not args.no_image:
        bg = outdir / 'thumbnail_bg.png'
        final = outdir / 'thumbnail_final.png'
        card = outdir / 'telegram_preview_card.png'
        preview_mp4 = outdir / 'telegram_preview.mp4'

        prompt = (
            'YouTube thumbnail background, Korean AI discussion show, '
            'futuristic newsroom + warm studio lighting, two host silhouettes in conversation, '
            'high contrast, cinematic, clean composition, no text, no logo, 16:9'
        )
        generate_bg_with_skill(prompt, bg, resolution='1K')
        compose_thumbnail(bg, final, week_label, topics)
        compose_telegram_card(bg, card, week_label, titles[0], topics)
        build_telegram_preview_mp4(card, preview_mp4)

        size_mb = round(preview_mp4.stat().st_size / (1024 * 1024), 2)
        (outdir / 'telegram_preview_meta.txt').write_text(
            f'file={preview_mp4}\nsize_mb={size_mb}\nmax_mb=20\n',
            encoding='utf-8',
        )

    print(f'OUTPUT_DIR={outdir}')


if __name__ == '__main__':
    main()
