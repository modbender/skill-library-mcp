#!/usr/bin/env python3
import sys
import markdown
from weasyprint import HTML, CSS

def md_to_pdf(md_text, output_path):
    html_body = markdown.markdown(md_text, extensions=['tables', 'nl2br'])
    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
@font-face {{ font-family: 'NotoSans'; src: url('/tmp/NotoSansCJK.ttf'); }}
body {{ font-family: 'NotoSans', sans-serif; font-size: 11pt; color: #222; }}
h1 {{ font-size: 18pt; color: #1f497d; border-bottom: 2px solid #1f497d; padding-bottom: 4px; }}
h2 {{ font-size: 14pt; color: #1f497d; margin-top: 16px; }}
h3 {{ font-size: 12pt; color: #333; }}
table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
th {{ background: #4472c4; color: white; padding: 6px 8px; border: 1px solid #ccc; }}
td {{ padding: 5px 8px; border: 1px solid #ccc; }}
tr:nth-child(even) td {{ background: #eef2ff; }}
hr {{ border: none; border-top: 1px solid #ccc; margin: 12px 0; }}
p {{ margin: 6px 0; line-height: 1.6; }}
ul {{ margin: 4px 0; padding-left: 20px; }} li {{ margin: 3px 0; }}
</style>
</head><body>{html_body}</body></html>"""
    HTML(string=html).write_pdf(output_path, stylesheets=[CSS(string='@page { margin: 1.5cm; }')])
    return output_path

if __name__ == '__main__':
    md = sys.stdin.read()
    out = sys.argv[1] if len(sys.argv) > 1 else '/tmp/tech-invest-report.pdf'
    print(md_to_pdf(md, out))
