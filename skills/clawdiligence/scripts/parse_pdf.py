#!/usr/bin/env python3
"""PDF からテキストを抽出する (ページ番号付き).

Usage:
    python3 parse_pdf.py --input report.pdf
    python3 parse_pdf.py --input report.pdf --output extracted.txt
    python3 parse_pdf.py --input report.pdf --pages 1-5

Output:
    ページ番号付きのテキストを stdout (または --output ファイル) に出力。

    --- Page 1 ---
    テキスト内容...

    --- Page 2 ---
    テキスト内容...

Environment:
    特に不要。pdfplumber がインストール済みであること。
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    import pdfplumber
except ImportError:
    print("ERROR: pdfplumber が必要です。`uv pip install pdfplumber` を実行してください。", file=sys.stderr)
    sys.exit(1)


def extract_text(pdf_path: Path, page_range: tuple[int, int] | None = None) -> str:
    """PDF からページ番号付きテキストを抽出."""
    output_lines: list[str] = []

    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        print(f"PDF: {pdf_path.name} ({total_pages} ページ)", file=sys.stderr)

        if page_range:
            start, end = page_range
            pages = pdf.pages[start - 1 : end]  # 1-indexed → 0-indexed
            page_offset = start
        else:
            pages = pdf.pages
            page_offset = 1

        for i, page in enumerate(pages):
            page_num = i + page_offset
            text = page.extract_text()

            output_lines.append(f"--- Page {page_num} ---")
            if text and text.strip():
                output_lines.append(text)
            else:
                output_lines.append("[テキストなし — 画像ベースのページです。OCR が必要です。]")
            output_lines.append("")

        # テーブル抽出を試みる
        for i, page in enumerate(pages):
            page_num = i + page_offset
            tables = page.extract_tables()
            if tables:
                output_lines.append(f"--- Page {page_num} Tables ---")
                for t_idx, table in enumerate(tables):
                    output_lines.append(f"[Table {t_idx + 1}]")
                    for row in table:
                        cells = [str(c).strip() if c else "" for c in row]
                        output_lines.append(" | ".join(cells))
                    output_lines.append("")

    return "\n".join(output_lines)


def parse_page_range(s: str) -> tuple[int, int]:
    """'1-5' → (1, 5), '3' → (3, 3)."""
    if "-" in s:
        parts = s.split("-", 1)
        return int(parts[0]), int(parts[1])
    else:
        n = int(s)
        return n, n


def main() -> None:
    parser = argparse.ArgumentParser(description="PDF テキスト抽出 (ページ番号付き)")
    parser.add_argument("--input", required=True, help="入力 PDF ファイルパス")
    parser.add_argument("--output", help="出力テキストファイルパス (未指定時は stdout)")
    parser.add_argument("--pages", help="ページ範囲 (例: 1-5, 3)")
    args = parser.parse_args()

    pdf_path = Path(args.input)
    if not pdf_path.exists():
        print(f"ERROR: ファイルが見つかりません: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    page_range = parse_page_range(args.pages) if args.pages else None
    result = extract_text(pdf_path, page_range)

    if args.output:
        out = Path(args.output)
        out.write_text(result, encoding="utf-8")
        print(f"✓ テキスト出力: {out} ({len(result)} 文字)", file=sys.stderr)
        print(str(out))
    else:
        print(result)


if __name__ == "__main__":
    main()
