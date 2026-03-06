#!/usr/bin/env python3
"""
Abby Browser - 点击元素

封装 openclaw browser click 命令
"""

import subprocess
import sys


def click(ref: str, double: bool = False) -> dict:
    """
    点击元素
    
    Args:
        ref: 元素引用编号
        double: 是否双击
    
    Returns:
        dict: 结果 {'success': bool, 'message': str}
    """
    cmd = ['openclaw', 'browser', 'click', ref]
    
    if double:
        cmd.append('--double')
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            action = '双击' if double else '点击'
            return {
                'success': True,
                'message': f'✅ 已{action}元素 {ref}'
            }
        else:
            return {
                'success': False,
                'message': f'点击失败: {result.stderr}'
            }
    
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'message': '点击超时'
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'错误: {str(e)}'
        }


def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("用法: python click.py <ref> [--double]")
        sys.exit(1)
    
    ref = sys.argv[1]
    double = '--double' in sys.argv
    
    result = click(ref, double=double)
    
    if result['success']:
        print(f"✅ {result['message']}")
    else:
        print(f"❌ {result['message']}")
        sys.exit(1)


if __name__ == '__main__':
    main()
