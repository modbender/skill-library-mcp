#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置验证脚本
检查配置文件格式和必填字段
"""

import sys
import yaml
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

def validate_config():
    """验证配置文件"""
    print("=" * 50)
    print("配置文件验证")
    print("=" * 50)
    
    config_file = PROJECT_ROOT / 'config.yaml'
    
    # 检查文件是否存在
    if not config_file.exists():
        print("❌ 配置文件不存在: config.yaml")
        print("请复制 config.yaml.example 并修改：")
        print("  cp config.yaml.example config.yaml")
        return False
    
    print(f"✅ 配置文件存在: {config_file}")
    
    # 读取配置
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        print("✅ 配置文件格式正确")
    except Exception as e:
        print(f"❌ 配置文件格式错误: {e}")
        return False
    
    # 验证必填字段
    print("\n验证必填字段：")
    all_valid = True
    
    # API配置
    print("\n1. API配置：")
    api_config = config.get('api', {})
    
    api_key = api_config.get('api_key', '')
    if api_key == 'YOUR_API_KEY_HERE' or not api_key:
        print("  ❌ api_key: 未配置")
        all_valid = False
    elif len(api_key) < 10:
        print("  ⚠️  api_key: 格式可能不正确")
        all_valid = False
    else:
        print("  ✅ api_key: 已配置")
    
    base_url = api_config.get('base_url', '')
    if base_url:
        print(f"  ✅ base_url: {base_url}")
    else:
        print("  ⚠️  base_url: 使用默认值")
    
    model = api_config.get('model', '')
    if model:
        print(f"  ✅ model: {model}")
    else:
        print("  ⚠️  model: 使用默认值")
    
    # 飞书配置（可选）
    print("\n2. 飞书配置（可选）：")
    feishu_config = config.get('feishu', {})
    
    feishu_enabled = feishu_config.get('enabled', False)
    if feishu_enabled:
        print(f"  ✅ enabled: {feishu_enabled}")
        
        feishu_target = feishu_config.get('target', '')
        if feishu_target == 'YOUR_USER_ID_HERE' or not feishu_target:
            print("  ⚠️  target: 未配置，推送功能将不可用")
        else:
            print(f"  ✅ target: 已配置")
    else:
        print(f"  ℹ️  飞书推送未启用")
    
    # 研究配置
    print("\n3. 研究配置：")
    research_config = config.get('research', {})
    
    topic = research_config.get('topic', '')
    if topic and topic != '你的研究领域':
        print(f"  ✅ topic: {topic}")
    else:
        print("  ⚠️  topic: 未配置或使用默认值")
    
    max_papers = research_config.get('max_papers', 5)
    print(f"  ✅ max_papers: {max_papers}")
    
    # 总结
    print("\n" + "=" * 50)
    if all_valid:
        print("✅ 配置验证通过！")
        print("\n下一步：")
        print("  python3 scripts/fetch_papers.py")
    else:
        print("⚠️  配置验证未完全通过，请检查上述警告。")
        print("\n必需配置：")
        print("  - api.api_key: 你的LLM API Key")
        print("\n可选配置：")
        print("  - feishu.target: 你的飞书用户ID")
    
    return all_valid

if __name__ == '__main__':
    success = validate_config()
    sys.exit(0 if success else 1)