#!/usr/bin/env python3
"""股价查询 + PDF生成脚本"""
import subprocess, re, sys, os, tempfile, json

def get_stock_prices(codes):
    """批量获取股价，codes为列表如 ['usNVDA','sz000338']"""
    if not codes:
        return {}
    query = ','.join(codes)
    raw = subprocess.run(
        ['curl', '-s', f'http://qt.gtimg.cn/q={query}'],
        capture_output=True
    ).stdout.decode('gbk', errors='ignore')
    result = {}
    for line in raw.split('\n'):
        m = re.search(r'v_(\w+)="([^"]+)"', line)
        if m:
            f = m.group(2).split('~')
            if len(f) > 34:
                result[m.group(1)] = {
                    'name': f[1], 'price': f[3], 'prev': f[4],
                    'change': f[31], 'pct': f[32],
                    'high': f[33], 'low': f[34]
                }
    return result

def md_to_pdf(md_text, output_path):
    with tempfile.NamedTemporaryFile(suffix='.md', mode='w', delete=False, encoding='utf-8') as f:
        f.write(md_text)
        md_path = f.name
    try:
        for engine in [['pandoc', md_path, '-o', output_path, '--pdf-engine=weasyprint'],
                       ['pandoc', md_path, '-o', output_path]]:
            r = subprocess.run(engine, capture_output=True)
            if r.returncode == 0:
                return output_path
        return None
    finally:
        os.unlink(md_path)

if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'prices'
    
    if cmd == 'prices':
        # 用法: python3 report.py prices usNVDA,sz000338,sh603019
        codes = sys.argv[2].split(',') if len(sys.argv) > 2 else []
        print(json.dumps(get_stock_prices(codes), ensure_ascii=False))
    
    elif cmd == 'pdf':
        # 用法: echo "markdown内容" | python3 report.py pdf /tmp/report.pdf
        md = sys.stdin.read()
        out = sys.argv[2] if len(sys.argv) > 2 else '/tmp/tech-invest-report.pdf'
        result = md_to_pdf(md, out)
        print(result or 'ERROR')
