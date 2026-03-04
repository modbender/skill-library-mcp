#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
思维模型增强器 - 初始化脚本
Thinking Model Enhancer - Initialization Script

初始化记忆目录和配置
"""

import os
from pathlib import Path
from datetime import datetime


def initialize_thinking_enhancer():
    """初始化思维模型增强器"""
    base_dir = Path.home() / ".claude" / "thinking_models"
    
    # 创建目录结构
    directories = [
        base_dir,  # 根目录
        base_dir / "memory",  # 记忆存储
        base_dir / "cache",  # 缓存
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✅ 创建目录: {directory}")
    
    # 创建示例配置文件
    config_file = base_dir / "config.json"
    if not config_file.exists():
        config = {
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "settings": {
                "auto_store_results": True,
                "max_history_days": 90,
                "default_model": "generic_pipeline",
                "confidence_threshold": 0.6
            },
            "enabled_models": [
                "research_mode",
                "diagnostic_mode",
                "generic_pipeline"
            ]
        }
        
        with open(config_file, 'w', encoding='utf-8') as f:
            import json
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 创建配置文件: {config_file}")
    
    print(f"\n🎉 思维模型增强器初始化完成！")
    print(f"📁 主目录: {base_dir}")
    
    return str(base_dir)


if __name__ == "__main__":
    initialize_thinking_enhancer()
