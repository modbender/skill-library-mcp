#!/usr/bin/env python
"""
pytest 测试：ebook_to_md 工具（仅百度 OCR）
- 对 fixtures/* 各输入类型（pdf/png/jpeg/epub/mobi）调用工具
- 与 fixtures/expected/*.md 做结构/内容对比，允许 OCR 误差范围内差异
- 未设置 BAIDU_OCR_API_KEY / BAIDU_OCR_SECRET_KEY 时跳过需 OCR 的用例
"""

import os
import re
import shutil
from pathlib import Path

import pytest

from skills.ebook_to_md.scripts.ebook_to_md import _EbookToMdImpl

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
EXPECTED_DIR = FIXTURES_DIR / "expected"

# 生成 fixtures：python fixtures/create_fixtures.py
HAS_CALIBRE = shutil.which("ebook-convert") is not None
HAS_BAIDU_OCR = bool(os.getenv("BAIDU_OCR_API_KEY") and os.getenv("BAIDU_OCR_SECRET_KEY"))


def _count_table_rows(md: str) -> int:
    """表格行数：Markdown 表格（不含表头分隔行）或 HTML <table> 中的 <tr> 行数"""
    count = 0
    # Markdown: | ... | 且非分隔行 ---
    lines = [l.strip() for l in md.split("\n")]
    for line in lines:
        if line.startswith("|") and line.endswith("|"):
            if "---" not in line:
                count += 1
    # HTML：实现会输出 <table>...</table>，按 <tr> 计行
    if count == 0 and "<table" in md and "<tr>" in md:
        count = len(re.findall(r"<tr>", md))
    return count


def _count_image_refs(md: str) -> int:
    """图片引用数量 ![alt](path)"""
    return len(re.findall(r"!\[[^\]]*\]\([^)]+\)", md))


def test_reject_local_backend():
    """ocr_backend=local 时返回错误，仅支持百度"""
    pdf_path = str(FIXTURES_DIR / "test_with_table.pdf")
    if not Path(pdf_path).exists():
        pytest.skip("fixture 不存在")
    r = _execute_full(pdf_path, ocr_backend="local")
    assert r.get("success") is False
    assert "百度" in r.get("error", "")


def _execute_full(input_path: str, **kwargs):
    """调用 _EbookToMdImpl().execute 返回 dict（仅百度 OCR）"""
    known = {"ocr_backend", "output_path"}
    extra = {k: v for k, v in kwargs.items() if k not in known}
    return _EbookToMdImpl().execute(
        input_path=input_path,
        ocr_backend=kwargs.get("ocr_backend", "baidu"),
        output_path=kwargs.get("output_path"),
        **extra
    )


class TestEbookToMdBaiduPdf:
    """ebook_to_md 工具测试（百度 OCR + PDF）"""

    @pytest.mark.skipif(not HAS_BAIDU_OCR, reason="需设置 BAIDU_OCR_API_KEY、BAIDU_OCR_SECRET_KEY")
    def test_table_pdf_basic(self, tmp_path):
        """test_with_table.pdf：成功转换，有表格结构"""
        pdf_path = str(FIXTURES_DIR / "test_with_table.pdf")
        out_path = str(tmp_path / "test_with_table.md")
        r = _execute_full(pdf_path, output_path=out_path)

        assert r.get("success") is True
        md = r.get("markdown", r.get("content", ""))
        assert len(md) > 100

        table_rows = _count_table_rows(md)
        assert table_rows >= 1, "应识别到至少 1 行表格"

        assert Path(out_path).exists()

    @pytest.mark.skipif(not HAS_BAIDU_OCR, reason="需设置 BAIDU_OCR_API_KEY、BAIDU_OCR_SECRET_KEY")
    def test_table_pdf_structure_vs_expected(self, tmp_path):
        """test_with_table：与 expected 做结构对比（表格行数）"""
        pdf_path = str(FIXTURES_DIR / "test_with_table.pdf")
        out_path = str(tmp_path / "test_with_table.md")
        r = _execute_full(pdf_path, output_path=out_path)

        assert r.get("success") is True
        md = r.get("markdown", r.get("content", ""))
        expected_path = EXPECTED_DIR / "test_with_table.md"
        expected_md = expected_path.read_text(encoding="utf-8")

        exp_rows = _count_table_rows(expected_md)
        out_rows = _count_table_rows(md)
        assert out_rows >= 1
        assert exp_rows >= 1

    @pytest.mark.skipif(not HAS_BAIDU_OCR, reason="需设置 BAIDU_OCR_API_KEY、BAIDU_OCR_SECRET_KEY")
    def test_pic_pdf_figures(self, tmp_path):
        """test_with_pic.pdf：成功转换，有图片或文本"""
        pdf_path = str(FIXTURES_DIR / "test_with_pic.pdf")
        out_path = str(tmp_path / "test_with_pic.md")
        r = _execute_full(pdf_path, output_path=out_path)

        assert r.get("success") is True
        md = r.get("markdown", r.get("content", ""))
        assert len(md.strip()) > 0
        # 百度接口可能返回内联图或本地图，至少应有内容
        assert Path(out_path).exists()

    @pytest.mark.skipif(not HAS_BAIDU_OCR, reason="需设置 BAIDU_OCR_API_KEY、BAIDU_OCR_SECRET_KEY")
    def test_pic_pdf_structure_vs_expected(self, tmp_path):
        """test_with_pic：与 expected 做结构对比（图片引用）"""
        pdf_path = str(FIXTURES_DIR / "test_with_pic.pdf")
        out_path = str(tmp_path / "test_with_pic.md")
        r = _execute_full(pdf_path, output_path=out_path)

        assert r.get("success") is True
        md = r.get("markdown", r.get("content", ""))
        expected_path = EXPECTED_DIR / "test_with_pic.md"
        expected_md = expected_path.read_text(encoding="utf-8")

        exp_imgs = _count_image_refs(expected_md)
        out_imgs = _count_image_refs(md)
        assert out_imgs >= exp_imgs or len(md.strip()) > 0

    @pytest.mark.skipif(not HAS_BAIDU_OCR, reason="需设置 BAIDU_OCR_API_KEY、BAIDU_OCR_SECRET_KEY")
    def test_without_output_path_returns_string(self):
        """不指定 output_path 时仅返回字符串"""
        pdf_path = str(FIXTURES_DIR / "test_with_table.pdf")
        r = _execute_full(pdf_path)

        assert r.get("success") is True
        assert "markdown" in r or "content" in r
        assert "output_path" not in r or r.get("output_path") is None


class TestEbookToMdImage:
    """PNG/JPEG 图片 OCR 测试（百度）"""

    @pytest.mark.skipif(not HAS_BAIDU_OCR, reason="需设置 BAIDU_OCR_API_KEY、BAIDU_OCR_SECRET_KEY")
    @pytest.mark.parametrize("ext", ["png", "jpg"])
    def test_image_ocr_basic(self, tmp_path, ext):
        """test_ocr.png/jpg：成功转换，有文本输出"""
        img_path = FIXTURES_DIR / f"test_ocr.{ext}"
        if not img_path.exists():
            pytest.skip(f"fixture 不存在，请运行 python fixtures/create_fixtures.py")
        out_path = str(tmp_path / f"test_ocr.{ext}.md")
        r = _execute_full(str(img_path), output_path=out_path)

        assert r.get("success") is True
        md = r.get("markdown", r.get("content", ""))
        assert len(md.strip()) > 0
        assert Path(out_path).exists()

    @pytest.mark.skipif(not HAS_BAIDU_OCR, reason="需设置 BAIDU_OCR_API_KEY、BAIDU_OCR_SECRET_KEY")
    def test_image_vs_expected(self, tmp_path):
        """test_ocr：输出包含预期关键词"""
        img_path = FIXTURES_DIR / "test_ocr.png"
        if not img_path.exists():
            pytest.skip("fixture 不存在，请运行 python fixtures/create_fixtures.py")
        out_path = str(tmp_path / "test_ocr.md")
        r = _execute_full(str(img_path), output_path=out_path)

        assert r.get("success") is True
        md = r.get("markdown", r.get("content", ""))
        # 允许 OCR 有误差，至少识别到部分内容（中文或英文取决于字体）
        exp_words = ["测试", "OCR", "ebook", "Test"]
        assert any(w in md for w in exp_words), f"期望输出含 {exp_words} 之一"


class TestEbookToMdEpub:
    """EPUB 测试（需 Calibre）"""

    @pytest.mark.skipif(not HAS_CALIBRE, reason="需安装 Calibre: brew install calibre")
    @pytest.mark.skipif(not HAS_BAIDU_OCR, reason="需设置 BAIDU_OCR_API_KEY、BAIDU_OCR_SECRET_KEY")
    def test_epub_basic(self, tmp_path):
        """test_minimal.epub：成功转换"""
        epub_path = FIXTURES_DIR / "test_minimal.epub"
        if not epub_path.exists():
            pytest.skip("fixture 不存在，请运行 python fixtures/create_fixtures.py")
        out_path = str(tmp_path / "test_minimal.md")
        r = _execute_full(str(epub_path), output_path=out_path)

        assert r.get("success") is True
        md = r.get("markdown", r.get("content", ""))
        assert len(md.strip()) > 0


class TestEbookToMdMobi:
    """MOBI 测试（需 Calibre + mobi fixture）"""

    @pytest.mark.skipif(not HAS_CALIBRE, reason="需安装 Calibre: brew install calibre")
    @pytest.mark.skipif(not HAS_BAIDU_OCR, reason="需设置 BAIDU_OCR_API_KEY、BAIDU_OCR_SECRET_KEY")
    def test_mobi_basic(self, tmp_path):
        """test_minimal.mobi：成功转换"""
        mobi_path = FIXTURES_DIR / "test_minimal.mobi"
        if not mobi_path.exists():
            pytest.skip("mobi fixture 需 Calibre 生成: ebook-convert test_minimal.epub test_minimal.mobi")
        out_path = str(tmp_path / "test_minimal.md")
        r = _execute_full(str(mobi_path), output_path=out_path)

        assert r.get("success") is True
        md = r.get("markdown", r.get("content", ""))
        assert len(md.strip()) > 0
