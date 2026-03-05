#!/usr/bin/env python3
"""
render_card.py — 用模板渲染卡片图，Chrome headless 截图输出 PNG

用法:
  python3 render_card.py \
    --template poster-3-4 \
    --out /tmp/card.png \
    --line1 "OpenClaw" \
    --line2 "有两层" \
    --line3 "model 配置" \
    --highlight "#22a854" \
    --bg "#e6f5ef" \
    --footer "公众号 · 早早集市"

模板位于 assets/templates/<template>.html（相对于本脚本所在的 skills/z-card-image/）
"""

import argparse, shutil, subprocess, sys, tempfile
from html import escape
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
TEMPLATES_DIR = SKILL_DIR / "assets" / "templates"

CHROME_PATHS = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "google-chrome",
    "chromium",
]

def find_chrome():
    for p in CHROME_PATHS:
        if Path(p).exists() or shutil.which(p):
            return p
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--template", default="poster-3-4")
    ap.add_argument("--out", required=True)
    ap.add_argument("--line1", default="")
    ap.add_argument("--line2", default="")
    ap.add_argument("--line3", default="")
    ap.add_argument("--hl1", action="store_true", help="第一行高亮")
    ap.add_argument("--hl2", action="store_true", help="第二行高亮")
    ap.add_argument("--hl3", action="store_true", help="第三行高亮")
    ap.add_argument("--highlight", default="#22a854")
    ap.add_argument("--bg", default="#e6f5ef")
    ap.add_argument("--footer", default="公众号 · 早早集市")
    ap.add_argument("--icon", default=None, help="顶部图标路径，不传则自动判断")
    ap.add_argument("--highlight-words", default="", help="要高亮的词，逗号分隔，如 '测试,openclaw'")
    args = ap.parse_args()

    # 自动选图标
    ICONS_DIR = SKILL_DIR / "assets" / "icons"
    if args.icon:
        icon_path = args.icon
    else:
        texts = " ".join([args.line1, args.line2, args.line3]).lower()
        if "openclaw" in texts:
            icon_path = str(ICONS_DIR / "openclaw-logo.svg")
        else:
            icon_path = str(ICONS_DIR / "zzclub-logo-gray.svg")

    tpl_path = TEMPLATES_DIR / f"{args.template}.html"
    if not tpl_path.exists():
        sys.exit(f"Template not found: {tpl_path}")

    html = tpl_path.read_text(encoding="utf-8")
    replacements = {
        "{{MAIN_TEXT_LINE1}}": escape(args.line1),
        "{{MAIN_TEXT_LINE2}}": escape(args.line2),
        "{{MAIN_TEXT_LINE3}}": escape(args.line3),
        "{{LINE1_CLASS}}": "highlight" if args.hl1 else "",
        "{{LINE2_CLASS}}": "highlight" if args.hl2 else "",
        "{{LINE3_CLASS}}": "highlight" if args.hl3 else "",
        "{{HIGHLIGHT_COLOR}}": args.highlight,
        "{{BG_COLOR}}": args.bg,
        "{{FOOTER_TEXT}}": escape(args.footer),
        "{{ICON_PATH}}": icon_path,
        "{{FONT_PATH}}": str(SKILL_DIR / "assets" / "fonts" / "AlimamaShuHeiTi-Bold.ttf"),
        "{{AVATAR_PATH}}": str(SKILL_DIR / "assets" / "icons" / "avatar_jinx_cartoon.jpg"),
    }
    for k, v in replacements.items():
        html = html.replace(k, v)

    # 词级高亮：把指定词用 <span class="highlight"> 包起来
    # 注意：line 内容已经被 html.escape，所以匹配时用转义后的词
    if args.highlight_words:
        import re
        words = [w.strip() for w in args.highlight_words.split(",") if w.strip()]
        for word in words:
            escaped_word = escape(word)
            html = re.sub(
                re.escape(escaped_word),
                f'<span class="highlight">{escaped_word}</span>',
                html
            )

    # 判断尺寸
    size_map = {
        "poster-3-4": (900, 1200),
    }
    w, h = size_map.get(args.template, (900, 1200))

    chrome = find_chrome()
    if not chrome:
        sys.exit("Chrome/Chromium not found")

    with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w", encoding="utf-8") as f:
        f.write(html)
        tmp_html = f.name

    # 输出路径统一用 workspace/tmp/，不要用 /tmp/（飞书无法上传系统临时目录）
    out = Path(args.out)
    cmd = [
        chrome,
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--disable-web-security=false",
        f"--screenshot={out}",
        f"--window-size={w},{h}",
        f"file://{tmp_html}",
    ]
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        sys.exit(f"Chrome failed:\n{result.stderr.decode()}")

    Path(tmp_html).unlink(missing_ok=True)
    print(f"✅ Saved to {out}")

if __name__ == "__main__":
    main()
