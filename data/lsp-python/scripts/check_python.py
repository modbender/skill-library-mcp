#!/usr/bin/env python3
"""
Python 代码质量检查工具 - 批量检查并生成报告

用法:
    python check_python.py [文件或目录...]
    python check_python.py --auto-fix [文件或目录...]
"""

import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime

def find_python_files(paths):
    """查找所有 Python 文件"""
    py_files = []
    for path in paths:
        p = Path(path)
        if p.is_file() and p.suffix == '.py':
            py_files.append(str(p))
        elif p.is_dir():
            py_files.extend([str(f) for f in p.rglob('*.py')])
    return py_files

def check_file(filepath):
    """检查单个文件"""
    script = Path(__file__).parent / 'scripts' / 'lsp-service.py'
    result = subprocess.run(
        [sys.executable, str(script), 'check', filepath],
        capture_output=True, text=True
    )
    return result.stdout.strip()

def fix_file(filepath):
    """自动修复文件"""
    print(f"🔧 修复 {filepath}...")
    
    # 1. 清理导入
    subprocess.run(
        ['autoflake', '--remove-all-unused-imports', '--in-place', filepath],
        capture_output=True
    )
    
    # 2. 格式化
    subprocess.run(['black', '-q', filepath], capture_output=True)
    
    # 3. 重新检查
    return check_file(filepath)

def generate_report(results):
    """生成检查报告"""
    report = []
    report.append("# Python 代码质量检查报告")
    report.append(f"\n检查时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"\n检查文件数：{len(results)}\n")
    
    passed = sum(1 for r in results if '✅' in r['result'] or not r['result'].strip())
    failed = len(results) - passed
    
    report.append("## 统计\n")
    report.append(f"- ✅ 通过：{passed}")
    report.append(f"- ⚠️  有问题：{failed}\n")
    
    if failed > 0:
        report.append("## 问题详情\n")
        for r in results:
            if '✅' not in r['result'] and r['result'].strip():
                report.append(f"### {r['file']}\n")
                report.append(r['result'])
                report.append("")
    
    return '\n'.join(report)

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    auto_fix = '--auto-fix' in sys.argv
    paths = [a for a in sys.argv[1:] if not a.startswith('--')]
    
    if not paths:
        paths = ['.']
    
    py_files = find_python_files(paths)
    
    if not py_files:
        print("❌ 未找到 Python 文件")
        sys.exit(1)
    
    print(f"📋 找到 {len(py_files)} 个 Python 文件\n")
    
    results = []
    for filepath in py_files:
        print(f"检查 {filepath}...")
        
        if auto_fix:
            result = fix_file(filepath)
        else:
            result = check_file(filepath)
        
        results.append({'file': filepath, 'result': result})
        
        # 显示简要结果
        if '✅' in result:
            print(f"  ✅ 通过")
        else:
            issues = len([l for l in result.split('\n') if l.startswith('⚠️') or l.startswith('❌')])
            print(f"  ⚠️  发现 {issues} 个问题")
    
    # 生成报告
    report = generate_report(results)
    
    # 保存报告
    report_file = f"lsp-check-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📄 报告已保存到：{report_file}")
    
    # 返回状态码
    failed = sum(1 for r in results if '✅' not in r['result'] and r['result'].strip())
    if failed > 0:
        print(f"\n❌ {failed} 个文件有问题需要修复")
        if not auto_fix:
            print("💡 提示：使用 --auto-fix 自动修复")
        sys.exit(1)
    else:
        print("\n✅ 所有文件通过检查!")
        sys.exit(0)

if __name__ == "__main__":
    main()
