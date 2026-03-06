#!/usr/bin/env python3
"""
Joplin API 统一入口

根据 Joplin 官方 API 文档:
https://joplinapp.org/help/api/references/rest_api

用法:
    python3 joplin.py <command> [参数]

命令:
    ping            测试连接
    stats           查看统计
    recent          最近笔记
    list            列出笔记/笔记本/标签
    get             获取笔记详情
    create          创建笔记
    update          更新笔记
    delete          删除笔记
    search          搜索笔记
    move            移动笔记
    export          导出笔记
    import          导入笔记
    folders         笔记本管理
    tags            标签管理
"""
import sys
import subprocess
import os

# 获取脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def run_script(script_name, args):
    """运行子脚本"""
    script_path = os.path.join(SCRIPT_DIR, f'joplin_{script_name}.py')
    if not os.path.exists(script_path):
        print(f"❌ 未知命令：{script_name}")
        print(f"   脚本不存在：{script_path}")
        sys.exit(1)
    
    cmd = [sys.executable, script_path] + args
    try:
        result = subprocess.run(cmd, cwd=SCRIPT_DIR, check=True)
        return result.returncode
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    command = sys.argv[1]
    args = sys.argv[2:]
    
    # 命令别名映射
    commands = {
        'ping': 'ping',
        'stats': 'stats',
        'recent': 'recent',
        'list': 'list',
        'get': 'get',
        'create': 'create',
        'update': 'update',
        'delete': 'delete',
        'search': 'search',
        'move': 'move',
        'export': 'export',
        'import': 'import',
        'folders': 'folders',
        'tags': 'tags',
        'folder-notes': 'folder_notes',
    }
    
    if command not in commands:
        print(f"❌ 未知命令：{command}")
        print(f"\n可用命令：{', '.join(commands.keys())}")
        sys.exit(1)
    
    sys.exit(run_script(commands[command], args))
