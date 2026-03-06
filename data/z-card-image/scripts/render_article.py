#!/usr/bin/env python3
"""
render_article.py — 将文本渲染成单张 article-3-4 卡片图

LLM 负责分页逻辑，每页单独调用本脚本。

用法（单页模式，推荐）:
  python3 render_article.py \
    --title "文章标题" \
    --text "该页正文（段落间空行分隔）" \
    --page-num 1 \
    --page-total 3 \
    --out /path/to/workspace/tmp/card_01.png \
    [--highlight "#22a854"] \
    [--bg "#e6f5ef"] \
    [--footer "公众号 · 早早集市"]

用法（批量模式，兼容保留）:
  python3 render_article.py \
    --title "文章标题" \
    --text "全文..." \
    --out-dir /path/to/output \
    [--chars-per-page 280]
"""

import argparse, shutil, subprocess, sys, tempfile, re
from html import escape
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
TEMPLATE_PATH = SKILL_DIR / "assets" / "templates" / "article-3-4.html"
MD_CSS_PATH = SKILL_DIR / "assets" / "styles" / "md.css"
ICONS_DIR = SKILL_DIR / "assets" / "icons"
FONTS_DIR = SKILL_DIR / "assets" / "fonts"

CHROME_PATHS = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "google-chrome",
    "chromium",
]

W, H = 900, 1200
CHARS_PER_PAGE = 280


def find_chrome():
    for p in CHROME_PATHS:
        if Path(p).exists() or shutil.which(p):
            return p
    return None


def split_at_sentence_boundary(text: str, limit: int) -> tuple:
    """
    在 limit 字符以内，找最后一个句子结束符（。！？…）处截断。
    宁少勿多：找不到就在最后一个逗号/分号处截，再找不到就硬截到 limit*0.85。
    返回 (taken, rest)
    """
    if len(text) <= limit:
        return text, ''

    # 在 limit 范围内从后往前找强句末
    strong_ends = set('。！？…\n')
    weak_ends = set('，；,.;')

    candidate = -1
    for i in range(min(limit, len(text)) - 1, max(limit // 2, 0) - 1, -1):
        if text[i] in strong_ends:
            candidate = i + 1
            break

    if candidate == -1:
        # 找弱分隔符
        for i in range(min(limit, len(text)) - 1, max(limit // 2, 0) - 1, -1):
            if text[i] in weak_ends:
                candidate = i + 1
                break

    if candidate == -1:
        # 实在没有，保守截到 85%
        candidate = int(limit * 0.85)

    return text[:candidate].strip(), text[candidate:].strip()


def split_text_into_pages(text: str, chars_per_page: int) -> list:
    """
    按段落优先、句子边界兜底的分页逻辑。
    宁少勿多：每页预留 10% buffer，不塞满。
    """
    safe_limit = int(chars_per_page * 0.9)  # 保守上限
    paragraphs = [p.strip() for p in re.split(r'\n{2,}', text.strip()) if p.strip()]

    pages = []
    current_chunks = []
    current_len = 0

    for para in paragraphs:
        # 超长段落先按句子边界切碎
        while len(para) > safe_limit:
            taken, para = split_at_sentence_boundary(para, safe_limit)
            if current_chunks:
                pages.append(current_chunks)
                current_chunks = []
                current_len = 0
            pages.append([taken])

        if not para:
            continue

        # 加入当前页会不会超限
        if current_len + len(para) > safe_limit and current_chunks:
            pages.append(current_chunks)
            current_chunks = []
            current_len = 0

        current_chunks.append(para)
        current_len += len(para)

    if current_chunks:
        pages.append(current_chunks)

    return pages


def text_to_html(text: str) -> str:
    """把文本整体交给 markdown 渲染，支持完整 MD 语法"""
    try:
        import markdown as md_lib
    except ImportError:
        sys.exit('需要安装 markdown 库：pip install markdown')
    return md_lib.markdown(text, extensions=['fenced_code', 'tables', 'nl2br'])


def md_to_html(text: str) -> str:
    """把 Markdown 转成 HTML 片段，需要 pip install markdown"""
    try:
        import markdown
        return markdown.markdown(text, extensions=['fenced_code', 'tables', 'nl2br'])
    except ImportError:
        sys.exit('需要安装 markdown 库：pip install markdown')


def render_page(chrome, tpl, out_path, title, content_html, page_label, bottom_tip,
                highlight, bg, footer, icon_path, avatar_path, font_path, md_css_path=''):
    html = tpl
    replacements = {
        '{{MD_CSS_PATH}}': str(md_css_path) if md_css_path else '',
        '{{TITLE}}': escape(title),
        '{{CONTENT_HTML}}': content_html,
        '{{PAGE_LABEL}}': escape(page_label),
        '{{BOTTOM_TIP}}': escape(bottom_tip),
        '{{HIGHLIGHT_COLOR}}': highlight,
        '{{BG_COLOR}}': bg,
        '{{FOOTER_TEXT}}': escape(footer),
        '{{ICON_PATH}}': icon_path,
        '{{AVATAR_PATH}}': avatar_path,
        '{{FONT_PATH}}': font_path,
    }
    for k, v in replacements.items():
        html = html.replace(k, v)

    with tempfile.NamedTemporaryFile(suffix='.html', delete=False, mode='w', encoding='utf-8') as f:
        f.write(html)
        tmp_html = f.name

    cmd = [
        chrome, '--headless', '--disable-gpu', '--no-sandbox',
        f'--screenshot={out_path}',
        f'--window-size={W},{H}',
        f'file://{tmp_html}',
    ]
    result = subprocess.run(cmd, capture_output=True)
    Path(tmp_html).unlink(missing_ok=True)
    if result.returncode != 0:
        sys.exit(f'Chrome failed:\n{result.stderr.decode()}')
    print(f'✅ {out_path}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--title', required=True)
    ap.add_argument('--text', default='')
    ap.add_argument('--text-file', default='')
    # 单页模式
    ap.add_argument('--page-num', type=int, default=0)
    ap.add_argument('--page-total', type=int, default=0)
    ap.add_argument('--out', default='')
    # 批量模式
    ap.add_argument('--out-dir', default='')
    ap.add_argument('--chars-per-page', type=int, default=CHARS_PER_PAGE)
    ap.add_argument('--md', action='store_true', help='输入为 Markdown，自动转 HTML 渲染')
    # 样式
    ap.add_argument('--highlight', default='#3d6b4f')
    ap.add_argument('--bg', default='#f9fcfa')
    ap.add_argument('--footer', default='公众号 · 早早集市')
    ap.add_argument('--icon', default='')
    args = ap.parse_args()

    if args.text_file:
        text = Path(args.text_file).read_text(encoding='utf-8')
    elif args.text:
        text = args.text
    else:
        sys.exit('需要 --text 或 --text-file')

    chrome = find_chrome()
    if not chrome:
        sys.exit('Chrome/Chromium not found')

    # MD 和纯文本共用同一模板，都走 markdown 渲染
    tpl = TEMPLATE_PATH.read_text(encoding='utf-8')
    icon_path = args.icon or str(ICONS_DIR / 'zzclub-logo-gray.svg')
    avatar_path = str(ICONS_DIR / 'avatar_jinx_cartoon.jpg')
    font_path = str(FONTS_DIR / 'AlimamaShuHeiTi-Bold.ttf')
    md_css_path = str(MD_CSS_PATH)

    def to_content_html(t: str) -> str:
        return text_to_html(t)  # text_to_html 已内置 markdown 渲染

    # 单页模式
    if args.page_num > 0 and args.out:
        page_total = args.page_total if args.page_total > 0 else args.page_num
        page_label = f'{args.page_num} / {page_total}'
        bottom_tip = '· 全文完' if args.page_num == page_total else '← 滑动查看更多'
        render_page(
            chrome=chrome, tpl=tpl, out_path=Path(args.out),
            title=args.title, content_html=to_content_html(text),
            page_label=page_label, bottom_tip=bottom_tip,
            highlight=args.highlight, bg=args.bg, footer=args.footer,
            icon_path=icon_path, avatar_path=avatar_path, font_path=font_path,
            md_css_path=md_css_path,
        )
        return

    # 批量模式
    if not args.out_dir:
        sys.exit('需要 --out (单页模式) 或 --out-dir (批量模式)')

    pages = split_text_into_pages(text, args.chars_per_page)
    total = len(pages)
    print(f'共 {total} 页')
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for i, chunks in enumerate(pages, 1):
        parts = []
        for chunk in chunks:
            c = escape(chunk)
            c = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', c)
            parts.append(f'<p>{c}</p>')
        content_html = '\n'.join(parts)
        page_label = f'{i} / {total}'
        bottom_tip = '· 全文完' if i == total else '← 滑动查看更多'
        render_page(
            chrome=chrome, tpl=tpl, out_path=out_dir / f'card_{i:02d}.png',
            title=args.title, content_html=content_html,
            page_label=page_label, bottom_tip=bottom_tip,
            highlight=args.highlight, bg=args.bg, footer=args.footer,
            icon_path=icon_path, avatar_path=avatar_path, font_path=font_path,
        )
    print(f'\n🎉 完成，共输出 {total} 张图到 {out_dir}')


if __name__ == '__main__':
    main()
