#!/usr/bin/env python3
"""
Create publishing strategy for an account
"""

import argparse
from pathlib import Path
from datetime import datetime

def create_strategy_template(platform: str, account_name: str) -> str:
    """Generate strategy template"""
    
    template = f"""---
platform: {platform}
account: {account_name}
created_at: {datetime.now().strftime('%Y-%m-%d')}
updated_at: {datetime.now().strftime('%Y-%m-%d')}
---

# {account_name} - {platform} 运营策略

## 账号定位
- **人设**: 
- **目标受众**: 
- **内容调性**: 
- **差异化卖点**: 

## 内容规划

### 发布频率
- 每日发布: [ ] 篇
- 每周发布: [ ] 篇
- 最佳发布时间: [ ]

### 内容比例
| 类型 | 占比 | 说明 |
|------|------|------|
| 干货教程 | 40% | 实用技巧、教程 |
| 生活分享 | 30% | 日常、体验 |
| 产品种草 | 20% | 推荐、测评 |
| 互动话题 | 10% | 提问、讨论 |

### 选题方向
- [ ] 选题1: 
- [ ] 选题2: 
- [ ] 选题3: 

## 平台特定策略

### {platform} 特性
- 算法偏好: 
- 热门标签: 
- 互动技巧: 

## 跨平台分发策略

### 小红书 → Reddit
- Subreddit 选择: 
- 内容适配: [翻译/改编/重写]
- 发布频率: 

### 小红书 → Pinterest  
- Board 分类: 
- 图片要求: 
- 描述格式: 

### 小红书 → Discord
- 频道选择: 
- 内容形式: [完整/摘要/链接]

## KPI 目标
- 月度粉丝增长: [ ] 人
- 月度互动率: [ ]%
- 内容发布完成率: [ ]%

## 竞品参考
- 竞品1: [链接] - 学习点: 
- 竞品2: [链接] - 学习点: 

## 备注
"""
    return template

def main():
    parser = argparse.ArgumentParser(description='Create publishing strategy')
    parser.add_argument('platform', help='Platform name')
    parser.add_argument('account_name', help='Account name')
    parser.add_argument('--workspace', default='content-ops-workspace',
                       help='Workspace directory')
    
    args = parser.parse_args()
    
    workspace = Path(args.workspace)
    strategies_dir = workspace / "strategies"
    strategies_dir.mkdir(parents=True, exist_ok=True)
    
    filename = f"{args.platform}-{args.account_name}-strategy.md"
    filepath = strategies_dir / filename
    
    content = create_strategy_template(args.platform, args.account_name)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 运营策略已创建: {filepath}")
    print(f"\n💡 请填写以下内容:")
    print(f"   1. 账号定位和人设")
    print(f"   2. 内容规划和选题方向")
    print(f"   3. 跨平台分发策略")
    print(f"   4. KPI 目标")

if __name__ == '__main__':
    main()
