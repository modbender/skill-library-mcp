#!/usr/bin/env python3
import argparse
import base64
import datetime as dt
import hashlib
import json
import mimetypes
import os
import re
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request

INLINE_STYLES = {
    "section": "font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; color: #1f2328; font-size: 16px; line-height: 1.7;",
    "p": "margin: 0 0 14px 0;",
    "h1": "margin: 24px 0 16px 0; font-size: 26px; line-height: 1.3;",
    "h2": "margin: 20px 0 12px 0; font-size: 22px; line-height: 1.35;",
    "h3": "margin: 18px 0 10px 0; font-size: 18px; line-height: 1.4;",
    "ul": "padding-left: 22px; margin: 0 0 14px 0;",
    "ol": "padding-left: 22px; margin: 0 0 14px 0;",
    "li": "margin: 6px 0;",
    "blockquote": "margin: 12px 0; padding: 8px 12px; background: #f6f8fa; border-left: 3px solid #d0d7de;",
}

IMG_SRC_RE = re.compile(r"(<img\\b[^>]*?\\bsrc\\s*=\\s*)(['\"]?)([^'\"\\s>]+)\\2", re.I)
H1_RE = re.compile(r"<h1\\b[^>]*>(.*?)</h1>", re.I | re.S)


def _slugify(name: str) -> str:
    name = re.sub(r"[^a-zA-Z0-9._-]+", "-", name).strip("-")
    return name or "asset"


def _unique_path(path: str) -> str:
    if not os.path.exists(path):
        return path
    base, ext = os.path.splitext(path)
    i = 1
    while True:
        cand = f"{base}-{i}{ext}"
        if not os.path.exists(cand):
            return cand
        i += 1


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def _run_pandoc(input_path: str) -> str:
    try:
        result = subprocess.run(
            ["pandoc", input_path, "-f", "docx", "-t", "html"],
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        raise RuntimeError("pandoc not found in PATH; install pandoc to convert .docx")
    return result.stdout


def _simple_markdown_to_html(md: str) -> str:
    lines = md.splitlines()
    html_lines = []
    in_ul = False
    in_ol = False

    def close_lists():
        nonlocal in_ul, in_ol
        if in_ul:
            html_lines.append("</ul>")
            in_ul = False
        if in_ol:
            html_lines.append("</ol>")
            in_ol = False

    for raw in lines:
        line = raw.rstrip()
        if not line.strip():
            close_lists()
            html_lines.append("")
            continue

        if line.startswith("### "):
            close_lists()
            html_lines.append(f"<h3>{line[4:]}</h3>")
            continue
        if line.startswith("## "):
            close_lists()
            html_lines.append(f"<h2>{line[3:]}</h2>")
            continue
        if line.startswith("# "):
            close_lists()
            html_lines.append(f"<h1>{line[2:]}</h1>")
            continue

        if re.match(r"^[-*] ", line):
            if not in_ul:
                close_lists()
                html_lines.append("<ul>")
                in_ul = True
            html_lines.append(f"<li>{line[2:]}</li>")
            continue
        if re.match(r"^\\d+\\. ", line):
            if not in_ol:
                close_lists()
                html_lines.append("<ol>")
                in_ol = True
            item = re.sub(r"^\\d+\\. ", "", line)
            html_lines.append(f"<li>{item}</li>")
            continue

        close_lists()
        html_lines.append(f"<p>{line}</p>")

    close_lists()
    return "\n".join(html_lines)


def _markdown_to_html(md: str) -> str:
    try:
        import markdown  # type: ignore

        return markdown.markdown(md, extensions=["extra"])
    except Exception:
        return _simple_markdown_to_html(md)


def _apply_inline_styles(html: str) -> str:
    for tag, style in INLINE_STYLES.items():
        pattern = re.compile(rf"<{tag}(?![^>]*\\bstyle=)([^>]*)>", re.I)
        html = pattern.sub(rf"<{tag} style=\"{style}\"\\1>", html)
    return html


def _guess_ext_from_content_type(content_type: str) -> str:
    if not content_type:
        return ""
    mime = content_type.split(";")[0].strip().lower()
    return mimetypes.guess_extension(mime) or ""


def _download_url(url: str, dest_dir: str) -> str:
    _ensure_dir(dest_dir)
    req = urllib.request.Request(url, headers={"User-Agent": "wechat-pack/1.0"})
    with urllib.request.urlopen(req) as resp:
        data = resp.read()
        ext = _guess_ext_from_content_type(resp.headers.get("Content-Type", ""))
    base = _slugify(os.path.basename(urllib.parse.urlparse(url).path))
    if not os.path.splitext(base)[1] and ext:
        base = f"{base}{ext}"
    filename = _unique_path(os.path.join(dest_dir, base))
    with open(filename, "wb") as f:
        f.write(data)
    return filename


def _write_data_image(data_url: str, dest_dir: str) -> str:
    _ensure_dir(dest_dir)
    header, b64 = data_url.split(",", 1)
    m = re.match(r"data:image/([a-zA-Z0-9+.-]+);base64", header)
    ext = ".png"
    if m:
        ext = f".{m.group(1).lower()}"
    digest = hashlib.sha1(b64.encode("utf-8")).hexdigest()[:12]
    filename = _unique_path(os.path.join(dest_dir, f"image-{digest}{ext}"))
    with open(filename, "wb") as f:
        f.write(base64.b64decode(b64))
    return filename


def _rewrite_images(html: str, assets_dir: str, input_dir: str) -> str:
    def repl(match: re.Match) -> str:
        prefix, quote, src = match.group(1), match.group(2), match.group(3)
        new_src = src
        try:
            if src.startswith("http://") or src.startswith("https://"):
                local_path = _download_url(src, assets_dir)
                new_src = os.path.relpath(local_path, os.path.join(assets_dir, "..", "wechat"))
            elif src.startswith("data:image/"):
                local_path = _write_data_image(src, assets_dir)
                new_src = os.path.relpath(local_path, os.path.join(assets_dir, "..", "wechat"))
            else:
                # relative or absolute file path
                candidate = src
                if not os.path.isabs(candidate):
                    candidate = os.path.join(input_dir, candidate)
                if os.path.exists(candidate):
                    base = _slugify(os.path.basename(candidate))
                    dest = _unique_path(os.path.join(assets_dir, base))
                    shutil.copy2(candidate, dest)
                    new_src = os.path.relpath(dest, os.path.join(assets_dir, "..", "wechat"))
        except Exception:
            new_src = src
        return f"{prefix}{quote}{new_src}{quote}"

    return IMG_SRC_RE.sub(repl, html)


def _ensure_title(html: str, title: str) -> str:
    if not title:
        return html
    if re.search(r"<h1\\b", html, re.I):
        return html
    return f"<h1>{title}</h1>\n{html}"


def _extract_title(html: str) -> str:
    m = H1_RE.search(html)
    if not m:
        return ""
    title = re.sub(r"<[^>]+>", "", m.group(1)).strip()
    return title


def _center_crop(img, target_w, target_h):
    w, h = img.size
    target_ratio = target_w / target_h
    cur_ratio = w / h
    if cur_ratio > target_ratio:
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        box = (left, 0, left + new_w, h)
    else:
        new_h = int(w / target_ratio)
        top = (h - new_h) // 2
        box = (0, top, w, top + new_h)
    return img.crop(box).resize((target_w, target_h))


def _generate_cover_variants(cover_path: str, cover_dir: str) -> dict:
    variants = {}
    try:
        from PIL import Image  # type: ignore
    except Exception:
        return variants

    try:
        img = Image.open(cover_path)
    except Exception:
        return variants

    sizes = {
        "cover-wide-2.35x1.jpg": (900, 383),
        "cover-square-1x1.jpg": (600, 600),
    }

    for name, (w, h) in sizes.items():
        try:
            out_path = os.path.join(cover_dir, name)
            cropped = _center_crop(img, w, h)
            cropped.save(out_path, format="JPEG", quality=92)
            variants[name] = out_path
        except Exception:
            continue
    return variants


def build_output_dir(input_path: str, out_dir: str = None) -> str:
    base = os.path.splitext(os.path.basename(input_path))[0]
    if out_dir:
        target = out_dir
    else:
        target = f"{base}-wechat"
    target = os.path.abspath(target)
    if os.path.exists(target):
        target = _unique_path(target)
    _ensure_dir(target)
    for sub in ("source", "assets", "cover", "wechat"):
        _ensure_dir(os.path.join(target, sub))
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description="Package docx/markdown into WeChat-ready HTML")
    parser.add_argument("input", help="Input .docx/.md/.html file")
    parser.add_argument("--out", help="Output directory")
    parser.add_argument("--title", help="Insert title if missing")
    parser.add_argument("--cover", help="Cover image path or URL")
    args = parser.parse_args()

    input_path = os.path.abspath(args.input)
    if not os.path.exists(input_path):
        print(f"Input not found: {input_path}", file=sys.stderr)
        return 2

    ext = os.path.splitext(input_path)[1].lower()
    if ext not in (".docx", ".md", ".markdown", ".html", ".htm"):
        print("Unsupported input. Use .docx, .md/.markdown, or .html/.htm", file=sys.stderr)
        return 2

    out_dir = build_output_dir(input_path, args.out)
    source_dir = os.path.join(out_dir, "source")
    assets_dir = os.path.join(out_dir, "assets")
    cover_dir = os.path.join(out_dir, "cover")
    wechat_dir = os.path.join(out_dir, "wechat")

    shutil.copy2(input_path, os.path.join(source_dir, os.path.basename(input_path)))

    input_dir = os.path.dirname(input_path)
    if ext == ".docx":
        html_body = _run_pandoc(input_path)
    elif ext in (".md", ".markdown"):
        with open(input_path, "r", encoding="utf-8") as f:
            md = f.read()
        html_body = _markdown_to_html(md)
    else:
        with open(input_path, "r", encoding="utf-8") as f:
            html_body = f.read()

    html_body = _rewrite_images(html_body, assets_dir, input_dir)
    html_body = _ensure_title(html_body, args.title or "")
    html_body = _apply_inline_styles(html_body)

    wrapped = f"<section style=\"{INLINE_STYLES['section']}\">\n{html_body}\n</section>\n"

    article_path = os.path.join(wechat_dir, "article.html")
    with open(article_path, "w", encoding="utf-8") as f:
        f.write(wrapped)

    cover_main = ""
    cover_variants = {}
    if args.cover:
        try:
            if args.cover.startswith("http://") or args.cover.startswith("https://"):
                cover_path = _download_url(args.cover, cover_dir)
            else:
                base = _slugify(os.path.basename(args.cover))
                dest = _unique_path(os.path.join(cover_dir, base))
                shutil.copy2(args.cover, dest)
                cover_path = dest
            cover_main = cover_path
            cover_variants = _generate_cover_variants(cover_path, cover_dir)
        except Exception as exc:
            print(f"Cover download/copy failed: {exc}", file=sys.stderr)

    meta = {
        "title": _extract_title(html_body),
        "source_file": input_path,
        "output_dir": out_dir,
        "created_at": dt.datetime.now().isoformat(timespec="seconds"),
        "wechat_html": article_path,
        "assets_dir": assets_dir,
        "assets_count": len([f for f in os.listdir(assets_dir) if os.path.isfile(os.path.join(assets_dir, f))]),
        "cover_main": cover_main,
        "cover_variants": {k: v for k, v in cover_variants.items()},
    }
    meta_path = os.path.join(out_dir, "meta.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
