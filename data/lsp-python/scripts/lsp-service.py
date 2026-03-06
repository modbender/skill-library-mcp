#!/usr/bin/env python3
"""
LSP Python 服务封装 - 提供简洁的 LSP 调用接口

用法:
    python lsp-service.py <command> <args...>

Commands:
    check <file>              - 检查文件错误/警告
    complete <file> <line> <char> - 代码补全
    info <file> <line> <char> - 获取符号信息 (hover)
    goto <file> <line> <char> - 跳转到定义
"""

import subprocess
import json
import sys
import os
from pathlib import Path

def run_lsp(command, args):
    """调用 lsp-python.py 并解析结果"""
    script_path = Path(__file__).parent / "lsp-python.py"
    cmd = [sys.executable, str(script_path), command] + args
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=10
    )
    
    if result.returncode != 0:
        return {"error": result.stderr}
    
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"raw": result.stdout}

def format_diagnostics(result):
    """格式化诊断结果"""
    if "error" in result:
        return f"❌ 错误：{result['error']}"
    
    params = result.get("params", {})
    diagnostics = params.get("diagnostics", [])
    
    if not diagnostics:
        return "✅ 没有发现问题"
    
    lines = []
    for diag in diagnostics:
        source = diag.get("source", "unknown")
        message = diag.get("message", "")
        severity = diag.get("severity", 2)
        line = diag.get("range", {}).get("start", {}).get("line", 0) + 1
        
        icon = {1: "❌", 2: "⚠️", 3: "ℹ️", 4: "💡"}.get(severity, "•")
        lines.append(f"{icon} 第{line}行 [{source}]: {message}")
    
    return "\n".join(lines)

def format_completions(result):
    """格式化补全结果"""
    if "error" in result:
        return f"❌ 错误：{result['error']}"
    
    items = result.get("result", {}).get("items", [])
    
    if not items:
        return "没有补全建议"
    
    lines = ["补全建议:"]
    for item in items[:10]:  # 最多显示 10 个
        label = item.get("label", "")
        kind = item.get("kind", 0)
        kind_names = {
            1: "文本", 2: "方法", 3: "函数", 4: "构造器", 5: "字段",
            6: "变量", 7: "类", 8: "接口", 9: "模块", 10: "属性"
        }
        kind_name = kind_names.get(kind, "其他")
        lines.append(f"  • {label} ({kind_name})")
    
    if len(items) > 10:
        lines.append(f"  ... 还有 {len(items) - 10} 个建议")
    
    return "\n".join(lines)

def format_hover(result):
    """格式化悬停信息"""
    if "error" in result:
        return f"❌ 错误：{result['error']}"
    
    contents = result.get("result", {})
    if isinstance(contents, dict):
        value = contents.get("value", "")
        # 清理 markdown 格式
        value = value.replace("```python", "").replace("```", "").strip()
        return value if value else "无信息"
    return str(contents)

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    command = sys.argv[1]
    args = sys.argv[2:]
    
    if command == "check":
        if not args:
            print("用法：lsp-service.py check <file>")
            sys.exit(1)
        result = run_lsp("diagnostics", [os.path.abspath(args[0])])
        print(format_diagnostics(result))
    
    elif command == "complete":
        if len(args) < 3:
            print("用法：lsp-service.py complete <file> <line> <char>")
            sys.exit(1)
        result = run_lsp("completion", [os.path.abspath(args[0]), args[1], args[2]])
        print(format_completions(result))
    
    elif command == "info":
        if len(args) < 3:
            print("用法：lsp-service.py info <file> <line> <char>")
            sys.exit(1)
        result = run_lsp("hover", [os.path.abspath(args[0]), args[1], args[2]])
        print(format_hover(result))
    
    elif command == "goto":
        if len(args) < 3:
            print("用法：lsp-service.py goto <file> <line> <char>")
            sys.exit(1)
        result = run_lsp("definition", [os.path.abspath(args[0]), args[1], args[2]])
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    else:
        print(f"未知命令：{command}")
        print(__doc__)
        sys.exit(1)

if __name__ == "__main__":
    main()
