#!/usr/bin/env python3
"""
Initialize content-ops workspace directory structure
"""

import argparse
from pathlib import Path

def init_workspace(workspace_path: Path):
    """Create directory structure"""
    
    dirs = [
        "accounts",
        "strategies", 
        "corpus/raw",
        "corpus/curated",
        "corpus/published",
        "corpus/_archived_raw",
        "schedules",
        "reports"
    ]
    
    for dir_path in dirs:
        (workspace_path / dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✅ 创建目录: {dir_path}")
    
    # Create .gitkeep files
    for dir_path in dirs:
        gitkeep = workspace_path / dir_path / ".gitkeep"
        gitkeep.touch()
    
    print(f"\n✅ 工作空间初始化完成: {workspace_path}")
    print(f"\n📁 目录结构:")
    print("""
content-ops-workspace/
├── accounts/           # 账号档案
├── strategies/         # 运营策略
├── corpus/
│   ├── raw/           # 原始抓取语料
│   ├── curated/       # 人工确认后的语料
│   ├── published/     # 已发布内容
│   └── _archived_raw/ # 已归档的原始语料
├── schedules/         # 发布计划和每日任务
└── reports/           # 数据报告
""")

def main():
    parser = argparse.ArgumentParser(description='Initialize content-ops workspace')
    parser.add_argument('--path', default='content-ops-workspace',
                       help='Workspace path')
    
    args = parser.parse_args()
    
    workspace = Path(args.path)
    workspace.mkdir(parents=True, exist_ok=True)
    
    init_workspace(workspace)

if __name__ == '__main__':
    main()
