#!/usr/bin/env python3
"""
Abby Browser - 表单填写

封装 openclaw browser fill 命令
"""

import subprocess
import sys
import json


def fill(fields: list, submit: bool = False) -> dict:
    """
    填写表单
    
    Args:
        fields: 字段列表 [{'ref': '1', 'value': 'xxx'}, ...]
        submit: 是否提交
    
    Returns:
        dict: 结果 {'success': bool, 'message': str}
    """
    # 构建字段 JSON
    fields_json = json.dumps(fields)
    
    cmd = ['openclaw', 'browser', 'fill', '--fields', fields_json]
    
    if submit:
        cmd.append('--submit')
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            return {
                'success': True,
                'message': f'✅ 已填写 {len(fields)} 个字段'
            }
        else:
            return {
                'success': False,
                'message': f'填写失败: {result.stderr}'
            }
    
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'message': '填写超时'
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'错误: {str(e)}'
        }


def type_text(ref: str, text: str, submit: bool = False) -> dict:
    """
    输入文字
    
    Args:
        ref: 元素引用编号
        text: 要输入的文字
        submit: 是否提交
    
    Returns:
        dict: 结果 {'success': bool, 'message': str}
    """
    cmd = ['openclaw', 'browser', 'type', ref, text]
    
    if submit:
        cmd.append('--submit')
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            return {
                'success': True,
                'message': f'✅ 已输入: {text}'
            }
        else:
            return {
                'success': False,
                'message': f'输入失败: {result.stderr}'
            }
    
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'message': '输入超时'
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'错误: {str(e)}'
        }


def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("用法:")
        print("  python form.py fill '<json>'")
        print("  python form.py type <ref> <text>")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == 'fill':
        if len(sys.argv) < 3:
            print("用法: python form.py fill '<json>'")
            sys.exit(1)
        
        fields = json.loads(sys.argv[2])
        result = fill(fields)
    
    elif action == 'type':
        if len(sys.argv) < 4:
            print("用法: python form.py type <ref> <text>")
            sys.exit(1)
        
        ref = sys.argv[2]
        text = sys.argv[3]
        result = type_text(ref, text)
    
    else:
        print(f"未知操作: {action}")
        sys.exit(1)
    
    if result['success']:
        print(f"✅ {result['message']}")
    else:
        print(f"❌ {result['message']}")
        sys.exit(1)


if __name__ == '__main__':
    main()
