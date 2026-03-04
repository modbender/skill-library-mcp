#!/usr/bin/env python3
"""
Abby Browser - 数据提取

封装 openclaw browser snapshot 命令
"""

import subprocess
import sys
import json


def snapshot(format: str = 'ai', limit: int = 200) -> dict:
    """
    获取页面快照
    
    Args:
        format: 格式 ('ai' 或 'aria')
        limit: 最大字符数
    
    Returns:
        dict: 结果 {'success': bool, 'message': str, 'content': str}
    """
    cmd = ['openclaw', 'browser', 'snapshot']
    
    if format == 'aria':
        cmd.append('--format')
        cmd.append('aria')
    
    if limit:
        cmd.append('--limit')
        cmd.append(str(limit))
    
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
                'message': '✅ 页面快照已获取',
                'content': result.stdout
            }
        else:
            return {
                'success': False,
                'message': f'获取失败: {result.stderr}',
                'content': None
            }
    
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'message': '获取超时',
            'content': None
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'错误: {str(e)}',
            'content': None
        }


def extract_text(selector: str = None) -> dict:
    """
    提取文本内容
    
    Args:
        selector: CSS 选择器
    
    Returns:
        dict: 结果
    """
    if selector:
        # 使用 evaluate 执行 JavaScript
        js = f'document.querySelector("{selector}").innerText'
        cmd = ['openclaw', 'browser', 'evaluate', '--fn', js]
    else:
        # 获取整个页面的文本
        cmd = ['openclaw', 'browser', 'evaluate', '--fn', 'document.body.innerText']
    
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
                'message': '✅ 文本已提取',
                'content': result.stdout.strip()
            }
        else:
            return {
                'success': False,
                'message': f'提取失败: {result.stderr}',
                'content': None
            }
    
    except Exception as e:
        return {
            'success': False,
            'message': f'错误: {str(e)}',
            'content': None
        }


def main():
    """命令行入口"""
    action = sys.argv[1] if len(sys.argv) > 1 else 'snapshot'
    
    if action == 'snapshot':
        result = snapshot()
    elif action == 'text':
        selector = sys.argv[2] if len(sys.argv) > 2 else None
        result = extract_text(selector)
    else:
        print(f"未知操作: {action}")
        sys.exit(1)
    
    if result['success']:
        print(f"✅ {result['message']}")
        if result.get('content'):
            print(f"\n{result['content'][:500]}...")
    else:
        print(f"❌ {result['message']}")
        sys.exit(1)


if __name__ == '__main__':
    main()
