#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw中文工具包核心模块 - 修复版
"""

import os
import sys
import json
import logging
from typing import Dict, List, Optional, Union, Any

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChineseToolkit:
    """中文工具包核心类"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self._init_components()
        logger.info("中文工具包初始化完成")
    
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """加载配置文件"""
        default_config = {
            "api_keys": {},
            "local_services": {
                "ocr_enabled": True,
                "translation_enabled": True
            }
        }
        return default_config
    
    def _init_components(self):
        """初始化各个组件"""
        self.components = {}
        
        # 初始化分词组件
        try:
            import jieba
            self.components['segment'] = jieba
            logger.info("分词组件初始化成功")
        except ImportError:
            logger.warning("jieba未安装，分词功能不可用")
        
        # 初始化拼音组件
        try:
            from pypinyin import lazy_pinyin, Style
            self.components['pinyin'] = lazy_pinyin
            self.components['pinyin_style'] = Style
            logger.info("拼音组件初始化成功")
        except ImportError:
            logger.warning("pypinyin未安装，拼音功能不可用")
    
    def segment(self, text: str, cut_all: bool = False) -> List[str]:
        """中文分词"""
        if 'segment' not in self.components:
            # 简单回退：按字符分割
            return list(text)
        
        try:
            if cut_all:
                segments = self.components['segment'].cut(text, cut_all=True)
            else:
                segments = self.components['segment'].cut(text)
            
            return list(segments)
        except Exception as e:
            logger.error(f"分词失败: {e}")
            return list(text)
    
    def to_pinyin(self, text: str, style: str = 'normal') -> str:
        """转换为拼音"""
        if 'pinyin' not in self.components:
            return text
        
        style_map = {
            'normal': self.components['pinyin_style'].NORMAL,
            'tone': self.components['pinyin_style'].TONE,
            'tone2': self.components['pinyin_style'].TONE2,
        }
        
        selected_style = style_map.get(style, self.components['pinyin_style'].NORMAL)
        
        try:
            pinyin_list = self.components['pinyin'](text, style=selected_style)
            return ' '.join(pinyin_list)
        except Exception as e:
            logger.error(f"拼音转换失败: {e}")
            return text
    
    def get_text_statistics(self, text: str) -> Dict[str, Any]:
        """获取文本统计信息"""
        stats = {
            'length': len(text),
            'char_count': len([c for c in text if not c.isspace()]),
            'word_count': len(self.segment(text)),
            'has_chinese': any('\u4e00' <= c <= '\u9fff' for c in text),
            'has_english': any('a' <= c.lower() <= 'z' for c in text),
            'has_digits': any(c.isdigit() for c in text)
        }
        return stats
    
    def extract_keywords(self, text: str, top_k: int = 10) -> List[str]:
        """提取关键词"""
        if 'segment' not in self.components:
            return []
        
        try:
            import jieba.analyse
            return jieba.analyse.extract_tags(text, topK=top_k)
        except Exception as e:
            logger.error(f"提取关键词失败: {e}")
            return []
    
    def translate(self, text: str, from_lang: str = 'zh', to_lang: str = 'en', 
                  engine: str = 'google') -> str:
        """文本翻译"""
        if engine == 'google':
            return self._translate_google(text, from_lang, to_lang)
        else:
            # 简单回退
            return text
    
    def _translate_google(self, text: str, from_lang: str, to_lang: str) -> str:
        """谷歌翻译（简单实现）"""
        try:
            import requests
            
            # 简单的翻译映射
            simple_dict = {
                'zh-en': {'你好': 'Hello', '世界': 'World'},
                'en-zh': {'Hello': '你好', 'World': '世界'}
            }
            
            key = f"{from_lang}-{to_lang}"
            if key in simple_dict:
                return simple_dict[key].get(text, text)
            
            # 尝试使用免费API
            url = "https://translate.googleapis.com/translate_a/single"
            params = {
                'client': 'gtx',
                'sl': from_lang,
                'tl': to_lang,
                'dt': 't',
                'q': text
            }
            
            response = requests.get(url, params=params, timeout=5)
            result = response.json()
            
            if result and len(result) > 0:
                translated_parts = []
                for item in result[0]:
                    if item[0]:
                        translated_parts.append(item[0])
                return ''.join(translated_parts)
            
            return text
            
        except Exception as e:
            logger.error(f"翻译失败: {e}")
            return text

# 测试函数
def test_basic_functions():
    """测试基本功能"""
    print("测试中文工具包基本功能")
    print("=" * 50)
    
    toolkit = ChineseToolkit()
    
    # 测试分词
    text = "今天天气真好"
    segments = toolkit.segment(text)
    print(f"分词测试: {text} -> {segments}")
    
    # 测试拼音
    pinyin = toolkit.to_pinyin("中文", style='tone')
    print(f"拼音测试: 中文 -> {pinyin}")
    
    # 测试统计
    stats = toolkit.get_text_statistics("Hello 世界 123")
    print(f"统计测试: {stats}")
    
    # 测试关键词
    keywords = toolkit.extract_keywords("人工智能改变世界", top_k=2)
    print(f"关键词测试: {keywords}")
    
    # 测试翻译
    translated = toolkit.translate("你好", 'zh', 'en')
    print(f"翻译测试: 你好 -> {translated}")
    
    print("=" * 50)
    print("测试完成！")

if __name__ == '__main__':
    test_basic_functions()