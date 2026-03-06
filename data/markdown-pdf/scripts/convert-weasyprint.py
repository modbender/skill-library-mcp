#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown 转 PDF (WeasyPrint 方案)
支持完美中文显示、代码高亮、表格样式
修复：数字间距问题
"""

import sys
import re
import markdown
from weasyprint import HTML, CSS
from pathlib import Path

def convert_markdown_to_pdf(input_file, output_file):
    """将 Markdown 文件转换为 PDF"""

    # 读取 Markdown 文件
    md_path = Path(input_file)
    if not md_path.exists():
        raise FileNotFoundError(f"输入文件不存在: {input_file}")

    md_content = md_path.read_text(encoding='utf-8')

    # 预处理：在列表项中的 emoji 后添加空格
    md_content = re.sub(
        r'^(\s*[-*+]\s+)([\U0001F300-\U0001F9FF])([^\s])',
        r'\1\2 \3',
        md_content,
        flags=re.MULTILINE
    )

    # 转换为 HTML
    html_content = markdown.markdown(
        md_content,
        extensions=[
            'tables',
            'fenced_code',
            'nl2br',
            'sane_lists',
            'codehilite',
            'toc'
        ]
    )

    # 创建完整的 HTML 文档
    full_html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{md_path.stem}</title>
    <style>
        @page {{
            size: A4;
            margin: 2cm;
        }}
        body {{
            font-family: "Noto Sans CJK SC", "Microsoft YaHei", "PingFang SC", sans-serif;
            font-size: 11pt;
            line-height: 1.6;
            color: #333;
            font-variant-numeric: tabular-nums;
            letter-spacing: normal;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            font-size: 24pt;
            margin-top: 0;
            page-break-after: avoid;
            letter-spacing: normal;
        }}
        h2 {{
            color: #2c3e50;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 8px;
            font-size: 18pt;
            margin-top: 30pt;
            page-break-after: avoid;
            letter-spacing: normal;
        }}
        h3 {{
            color: #34495e;
            font-size: 14pt;
            margin-top: 20pt;
            page-break-after: avoid;
            letter-spacing: normal;
        }}
        h4, h5, h6 {{
            color: #34495e;
            font-size: 12pt;
            margin-top: 15pt;
            page-break-after: avoid;
            letter-spacing: normal;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
            page-break-inside: avoid;
            font-variant-numeric: tabular-nums;
            letter-spacing: normal;
        }}
        th {{
            background-color: #3498db;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: bold;
            border: 1px solid #2980b9;
            letter-spacing: normal;
        }}
        td {{
            padding: 12px;
            border: 1px solid #ddd;
            font-variant-numeric: tabular-nums;
            letter-spacing: normal;
        }}
        tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}
        code {{
            background-color: #f8f9fa;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: "Courier New", monospace;
            font-size: 0.9em;
            color: #e74c3c;
            font-variant-numeric: tabular-nums;
            letter-spacing: normal;
        }}
        pre {{
            background-color: #2c3e50;
            color: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            border: 1px solid #34495e;
            page-break-inside: avoid;
        }}
        pre code {{
            background: none;
            padding: 0;
            color: inherit;
        }}
        blockquote {{
            border-left: 4px solid #3498db;
            margin: 20px 0;
            padding-left: 20px;
            color: #7f8c8d;
            background-color: #f8f9fa;
            padding: 15px 20px;
            border-radius: 0 5px 5px 0;
            page-break-inside: avoid;
        }}
        ul, ol {{
            margin: 10px 0;
            padding-left: 30px;
            list-style-position: outside;
        }}
        li {{
            margin: 5px 0;
            line-height: 1.6;
        }}
        ul li {{
            list-style-type: disc;
        }}
        ul ul li {{
            list-style-type: circle;
        }}
        ul ul ul li {{
            list-style-type: square;
        }}
        ol li {{
            list-style-type: decimal;
        }}
        hr {{
            border: none;
            border-top: 2px solid #ecf0f1;
            margin: 30px 0;
        }}
        strong {{
            color: #2c3e50;
            font-weight: bold;
        }}
        em {{
            font-style: italic;
        }}
        a {{
            color: #3498db;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        img {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 20px auto;
        }}
    </style>
</head>
<body>
    {html_content}
</body>
</html>
"""

    # 生成 PDF
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    HTML(string=full_html).write_pdf(str(output_path))

    return str(output_path)

def main():
    if len(sys.argv) < 2:
        print("用法: python3 convert-weasyprint.py <输入.md> [输出.pdf]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else str(Path(input_file).with_suffix('.pdf'))

    try:
        result = convert_markdown_to_pdf(input_file, output_file)
        print(f"✅ PDF 生成成功: {result}")
    except Exception as e:
        print(f"❌ 转换失败: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
