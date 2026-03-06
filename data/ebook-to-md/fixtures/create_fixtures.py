#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
生成 ebook_to_md 各输入类型的测试样例：
- PNG/JPEG: 含中文的 OCR 测试图
- EPUB: 最小合法 EPUB 结构
- MOBI: 需 Calibre，运行 ebook-convert epub mobi 生成
"""
import zipfile
from pathlib import Path
from typing import Optional

try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

FIXTURES_DIR = Path(__file__).resolve().parent


def _find_chinese_font() -> Optional[Path]:
    candidates = [
        Path("/System/Library/Fonts/PingFang.ttc"),  # macOS
        Path("/System/Library/Fonts/Supplemental/Songti.ttc"),
        Path("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"),  # Linux
        Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
    ]
    for p in candidates:
        if p.exists():
            return p
    return None


def create_image_fixtures() -> None:
    """创建 PNG、JPEG 测试图（含中文 OCR 文本）"""
    if not HAS_PIL:
        print("跳过图片: 需 Pillow (pip install Pillow)")
        return
    font_path = _find_chinese_font()
    if font_path:
        font = ImageFont.truetype(str(font_path), 32)
        text = "ebook_to_md 测试\nOCR 识别样例"
    else:
        font = ImageFont.load_default()
        text = "ebook_to_md OCR Test"

    img = Image.new("RGB", (400, 120), color="white")
    draw = ImageDraw.Draw(img)
    draw.text((20, 30), text, fill="black", font=font)
    img.save(FIXTURES_DIR / "test_ocr.png")
    img.save(FIXTURES_DIR / "test_ocr.jpg", quality=90)
    print("已生成: test_ocr.png, test_ocr.jpg")


def create_epub_fixture() -> None:
    """创建最小合法 EPUB 3 测试文件"""
    epub_path = FIXTURES_DIR / "test_minimal.epub"
    mimetype = b"application/epub+zip"
    container_xml = b"""<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
"""
    content_opf = """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:title>测试书籍</dc:title>
    <dc:identifier id="uid">urn:uuid:test-minimal-001</dc:identifier>
    <dc:language>zh-CN</dc:language>
  </metadata>
  <manifest>
    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
    <item id="item1" href="chapter1.xhtml" media-type="application/xhtml+xml"/>
  </manifest>
  <spine>
    <itemref idref="item1"/>
  </spine>
</package>
""".encode("utf-8")
    chapter1 = """<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" lang="zh-CN">
<head><title>第一章</title></head>
<body>
  <h1>第一章 测试内容</h1>
  <p>这是 ebook_to_md 的 EPUB 测试样例。用于验证 MOBI/EPUB 转 Markdown 流程。</p>
  <p>Minimal valid EPUB 3.</p>
</body>
</html>
""".encode("utf-8")
    nav_xhtml = """<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="zh-CN">
<head><title>目录</title></head>
<body>
  <nav epub:type="toc">
    <ol><li><a href="chapter1.xhtml">第一章 测试内容</a></li></ol>
  </nav>
</body>
</html>
""".encode("utf-8")

    with zipfile.ZipFile(epub_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zi = zipfile.ZipInfo("mimetype")
        zi.compress_type = zipfile.ZIP_STORED
        zf.writestr(zi, mimetype)
        zf.writestr("META-INF/container.xml", container_xml)
        zf.writestr("OEBPS/content.opf", content_opf)
        zf.writestr("OEBPS/chapter1.xhtml", chapter1)
        zf.writestr("OEBPS/nav.xhtml", nav_xhtml)
    print("已生成: test_minimal.epub")


def create_mobi_fixture() -> None:
    """若存在 Calibre，由 EPUB 生成 MOBI"""
    import subprocess
    epub = FIXTURES_DIR / "test_minimal.epub"
    mobi = FIXTURES_DIR / "test_minimal.mobi"
    if not epub.exists():
        print("请先运行 create_epub_fixture()")
        return
    try:
        subprocess.run(
            ["ebook-convert", str(epub), str(mobi)],
            capture_output=True, text=True, timeout=30
        )
        if mobi.exists():
            print("已生成: test_minimal.mobi")
        else:
            print("MOBI 生成失败")
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        print("跳过 MOBI: 需 Calibre (brew install calibre),", e)


def main() -> None:
    create_image_fixtures()
    create_epub_fixture()
    create_mobi_fixture()


if __name__ == "__main__":
    main()
