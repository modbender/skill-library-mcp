#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置加载模块
从config.yaml读取配置
"""

import yaml
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

def load_config():
    """加载配置文件"""
    config_file = PROJECT_ROOT / 'config.yaml'
    
    if not config_file.exists():
        raise FileNotFoundError(
            f"配置文件不存在: {config_file}\n"
            f"请复制 config.yaml.example 并修改配置"
        )
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    return config

def get_api_config():
    """获取API配置"""
    config = load_config()
    return {
        'api_key': config['api']['api_key'],
        'base_url': config['api']['base_url'],
        'model': config['api']['model'],
    }

def get_feishu_config():
    """获取飞书配置"""
    config = load_config()
    return {
        'enabled': config['feishu']['enabled'],
        'target': config['feishu']['target'],
    }

def get_research_config():
    """获取研究配置"""
    config = load_config()
    return {
        'topic': config['research']['topic'],
        'description': config['research']['description'],
        'max_papers': config['research']['max_papers'],
    }

def get_journal_config():
    """获取期刊配置"""
    config = load_config()
    return {
        'use_rss': config['journals']['use_rss'],
        'use_pubmed': config['journals']['use_pubmed'],
        'custom_journals': config['journals']['custom_journals'],
    }

def get_keyword_config():
    """获取关键词配置"""
    config = load_config()
    return {
        'custom_core_keywords': config['keywords']['custom_core_keywords'],
        'custom_exclude_keywords': config['keywords']['custom_exclude_keywords'],
    }

if __name__ == '__main__':
    # 测试配置加载
    print("测试配置加载...")
    
    try:
        api_config = get_api_config()
        print(f"✅ API配置: {api_config['model']}")
        
        feishu_config = get_feishu_config()
        print(f"✅ 飞书配置: {feishu_config['target']}")
        
        research_config = get_research_config()
        print(f"✅ 研究主题: {research_config['topic']}")
        
    except FileNotFoundError as e:
        print(f"❌ {e}")
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")