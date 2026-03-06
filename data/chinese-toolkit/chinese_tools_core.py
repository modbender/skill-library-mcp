#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw中文工具包核心模块
提供中文文本处理、翻译、OCR等功能
"""

import os
import sys
import json
import logging
from typing import Dict, List, Optional, Union, Any
from pathlib import Path

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ChineseToolkit:
    """中文工具包核心类"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化中文工具包
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self._init_components()
        logger.info("中文工具包初始化完成")
    
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """加载配置文件"""
        default_config = {
            "api_keys": {
                "baidu_translate": {
                    "app_id": os.getenv("BAIDU_TRANSLATE_APP_ID", ""),
                    "app_key": os.getenv("BAIDU_TRANSLATE_APP_KEY", "")
                }
            },
            "local_services": {
                "ocr_enabled": True,
                "translation_enabled": True,
                "speech_enabled": False
            },
            "cache": {
                "enabled": True,
                "ttl": 3600,
                "max_size": 1000
            },
            "performance": {
                "max_workers": 4,
                "timeout": 30
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    # 合并配置
                    self._merge_config(default_config, user_config)
            except Exception as e:
                logger.warning(f"加载配置文件失败: {e}")
        
        return default_config
    
    def _merge_config(self, base: Dict, update: Dict) -> None:
        """递归合并配置"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value
    
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
    
    def segment(self, text: str, cut_all: bool = False, use_paddle: bool = False) -> List[str]:
        """
        中文分词
        
        Args:
            text: 中文文本
            cut_all: 是否全模式分词
            use_paddle: 是否使用paddle模式
            
        Returns:
            分词结果列表
        """
        if 'segment' not in self.components:
            raise ImportError("jieba未安装，无法进行分词")
        
        try:
            if use_paddle:
                # 尝试使用paddle模式
                self.components['segment'].enable_paddle()
            
            if cut_all:
                segments = self.components['segment'].cut(text, cut_all=True)
            else:
                segments = self.components['segment'].cut(text)
            
            return list(segments)
        except Exception as e:
            logger.error(f"分词失败: {e}")
            # 回退到简单空格分割
            return text.split()
    
    def extract_keywords(self, text: str, top_k: int = 10, with_weight: bool = False) -> List:
        """
        提取关键词
        
        Args:
            text: 中文文本
            top_k: 返回关键词数量
            with_weight: 是否返回权重
            
        Returns:
            关键词列表
        """
        if 'segment' not in self.components:
            raise ImportError("jieba未安装，无法提取关键词")
        
        try:
            import jieba.analyse
            if with_weight:
                return jieba.analyse.extract_tags(text, topK=top_k, withWeight=True)
            else:
                return jieba.analyse.extract_tags(text, topK=top_k)
        except Exception as e:
            logger.error(f"提取关键词失败: {e}")
            return []
    
    def to_pinyin(self, text: str, style: str = 'normal') -> str:
        """
        转换为拼音
        
        Args:
            text: 中文文本
            style: 拼音风格 ('normal', 'tone', 'tone2', 'initial', 'first_letter')
            
        Returns:
            拼音字符串
        """
        if 'pinyin' not in self.components:
            raise ImportError("pypinyin未安装，无法转换拼音")
        
        style_map = {
            'normal': self.components['pinyin_style'].NORMAL,
            'tone': self.components['pinyin_style'].TONE,
            'tone2': self.components['pinyin_style'].TONE2,
            'initial': self.components['pinyin_style'].INITIALS,
            'first_letter': self.components['pinyin_style'].FIRST_LETTER
        }
        
        selected_style = style_map.get(style, self.components['pinyin_style'].NORMAL)
        
        try:
            pinyin_list = self.components['pinyin'](text, style=selected_style)
            return ' '.join(pinyin_list)
        except Exception as e:
            logger.error(f"拼音转换失败: {e}")
            return text
    
    def get_text_statistics(self, text: str) -> Dict[str, Any]:
        """
        获取文本统计信息
        
        Args:
            text: 中文文本
            
        Returns:
            统计信息字典
        """
        stats = {
            'length': len(text),
            'char_count': len([c for c in text if not c.isspace()]),
            'word_count': len(self.segment(text)) if 'segment' in self.components else 0,
            'line_count': len(text.splitlines()),
            'has_chinese': any('\u4e00' <= c <= '\u9fff' for c in text),
            'has_english': any('a' <= c.lower() <= 'z' for c in text),
            'has_digits': any(c.isdigit() for c in text)
        }
        
        return stats
    
    def text_summary(self, text: str, max_length: int = 200) -> str:
        """
        文本摘要（简单实现）
        
        Args:
            text: 文本
            max_length: 摘要最大长度
            
        Returns:
            摘要文本
        """
        # 简单实现：取前N个字符
        if len(text) <= max_length:
            return text
        
        # 尝试在句子边界截断
        sentences = text.split('。')
        summary = []
        current_length = 0
        
        for sentence in sentences:
            if current_length + len(sentence) <= max_length:
                summary.append(sentence)
                current_length += len(sentence) + 1  # +1 for the period
            else:
                break
        
        result = '。'.join(summary) + '。'
        
        # 如果还是太长，直接截断
        if len(result) > max_length:
            result = text[:max_length] + '...'
        
        return result
    
    def translate(self, text: str, from_lang: str = 'zh', to_lang: str = 'en', 
                  engine: str = 'baidu') -> str:
        """
        文本翻译
        
        Args:
            text: 待翻译文本
            from_lang: 源语言
            to_lang: 目标语言
            engine: 翻译引擎 ('baidu', 'google', 'local')
            
        Returns:
            翻译结果
        """
        if engine == 'baidu':
            return self._translate_baidu(text, from_lang, to_lang)
        elif engine == 'google':
            return self._translate_google(text, from_lang, to_lang)
        elif engine == 'local':
            return self._translate_local(text, from_lang, to_lang)
        else:
            raise ValueError(f"不支持的翻译引擎: {engine}")
    
    def _translate_baidu(self, text: str, from_lang: str, to_lang: str) -> str:
        """百度翻译"""
        app_id = self.config['api_keys']['baidu_translate']['app_id']
        app_key = self.config['api_keys']['baidu_translate']['app_key']
        
        if not app_id or not app_key:
            logger.warning("百度翻译API密钥未配置")
            return text
        
        try:
            import hashlib
            import random
            import requests
            
            # 生成签名
            salt = str(random.randint(32768, 65536))
            sign_str = app_id + text + salt + app_key
            sign = hashlib.md5(sign_str.encode('utf-8')).hexdigest()
            
            # 构建请求
            url = "https://fanyi-api.baidu.com/api/trans/vip/translate"
            params = {
                'q': text,
                'from': from_lang,
                'to': to_lang,
                'appid': app_id,
                'salt': salt,
                'sign': sign
            }
            
            response = requests.get(url, params=params, timeout=10)
            result = response.json()
            
            if 'trans_result' in result:
                return result['trans_result'][0]['dst']
            else:
                logger.error(f"百度翻译失败: {result}")
                return text
                
        except Exception as e:
            logger.error(f"百度翻译请求失败: {e}")
            return text
    
    def _translate_google(self, text: str, from_lang: str, to_lang: str) -> str:
        """谷歌翻译（免费版）"""
        try:
            import requests
            
            url = "https://translate.googleapis.com/translate_a/single"
            params = {
                'client': 'gtx',
                'sl': from_lang,
                'tl': to_lang,
                'dt': 't',
                'q': text
            }
            
            response = requests.get(url, params=params, timeout=10)
            result = response.json()
            
            if result and len(result) > 0:
                # 提取翻译结果
                translated_parts = []
                for item in result[0]:
                    if item[0]:
                        translated_parts.append(item[0])
                return ''.join(translated_parts)
            else:
                return text
                
        except Exception as e:
            logger.error(f"谷歌翻译失败: {e}")
            return text
    
    def _translate_local(self, text: str, from_lang: str, to_lang: str) -> str:
        """本地翻译（简单实现）"""
        # 这是一个简单的示例，实际应该使用本地翻译模型
        logger.info("使用本地简单翻译（示例）")
        
        # 简单的中英互译词典
        simple_dict = {
            'zh-en': {
                '你好': 'Hello',
                '世界': 'World',
                '今天': 'Today',
                '天气': 'Weather',
                '很好': 'Very good'
            },
            'en-zh': {
                'Hello': '你好',
                'World': '世界',
                'Today': '今天',
                'Weather': '天气',
                'Very good': '很好'
            }
        }
        
        key = f"{from_lang}-{to_lang}"
        if key in simple_dict:
            return simple_dict[key].get(text, text)
        else:
            return text

def main():
    """命令行入口点"""
    import argparse
    
    parser = argparse.ArgumentParser(description='OpenClaw中文工具包')
    subparsers = parser.add_subparsers(dest='command', help='子命令')
    
    # 分词命令
    parser_segment = subparsers.add_parser('segment', help='中文分词')
    parser_segment.add_argument('text', help='要分词的文本')
    parser_segment.add_argument('--cut-all', action='store_true', help='全模式分词')
    parser_segment.add_argument('--use-paddle', action='store_true', help='使用paddle模式')
    
    # 翻译命令
    parser_translate = subparsers.add_parser('translate', help='文本翻译')
    parser_translate.add_argument('text', help='要翻译的文本')
    parser_translate.add_argument('--from', dest='from_lang', default='zh', help='源语言')
    parser_translate.add_argument('--to', dest='to_lang', default='en', help='目标语言')
    parser_translate.add_argument('--engine', choices=['baidu', 'google', 'local'], default='baidu', help='翻译引擎')
    
    # 拼音命令
    parser_pinyin = subparsers.add_parser('pinyin', help='转换为拼音')
    parser_pinyin.add_argument('text', help='要转换的文本')
    parser_pinyin.add_argument('--style', choices=['normal', 'tone', 'tone2', 'initial', 'first_letter'], 
                              default='normal', help='拼音风格')
    
    # 统计命令
    parser_stats = subparsers.add_parser('stats', help='文本统计')
    parser_stats.add_argument('text', help='要统计的文本')
    
    args = parser.parse_args()
    
    # 初始化工具包
    toolkit = ChineseToolkit()
    
    # 执行命令
    if args.command == 'segment':
        result = toolkit.segment(args.text, args.cut_all, args.use_paddle)
        print("分词结果:", ' | '.join(result))
        
    elif args.command == 'translate':
        result = toolkit.translate(args.text, args.from_lang, args.to_lang, args.engine)
        print(f"翻译结果 ({args.from_lang}→{args.to_lang}):", result)
        
    elif args.command == 'pinyin':
        result = toolkit.to_pinyin(args.text, args.style)
        print("拼音结果:", result)
        
    elif args.command == 'stats':
        stats = toolkit.get_text_statistics(args.text)
        print("文本统计:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
    else:
        parser.print_help()

if __name__ == '__main__':
    main()