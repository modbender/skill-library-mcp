#!/usr/bin/env python3
"""
Abby Browser - 打开网页

封装 openclaw browser open 命令
"""

import subprocess
import sys
from typing import Optional


def open_url(url: str, new_tab: bool = True) -> dict:
    """
    打开网页
    
    Args:
        url: 网页URL
        new_tab: 是否在新标签页打开
    
    Returns:
        dict: 结果 {'success': bool, 'message': str}
    """
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    cmd = ['openclaw', 'browser']
    
    if new_tab:
        cmd.append('open')
    else:
        cmd.append('navigate')
    
    cmd.append(url)
    
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
                'message': f'已打开: {url}',
                'url': url
            }
        else:
            return {
                'success': False,
                'message': f'打开失败: {result.stderr}',
                'url': url
            }
    
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'message': '打开超时',
            'url': url
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'错误: {str(e)}',
            'url': url
        }


def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("用法: python open.py <URL>")
        sys.exit(1)
    
    url = sys.argv[1]
    result = open_url(url)
    
    if result['success']:
        print(f"✅ {result['message']}")
    else:
        print(f"❌ {result['message']}")
        sys.exit(1)


if __name__ == '__main__':
    main()
