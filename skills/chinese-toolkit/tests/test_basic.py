#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw中文工具包基础测试
"""

import sys
import os
import unittest

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chinese_tools import ChineseToolkit

class TestChineseToolkit(unittest.TestCase):
    """中文工具包测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.toolkit = ChineseToolkit()
        self.test_text = "今天天气真好，我们一起去公园散步吧。"
    
    def test_segment(self):
        """测试分词"""
        segments = self.toolkit.segment(self.test_text)
        self.assertIsInstance(segments, list)
        self.assertGreater(len(segments), 0)
        print(f"分词测试通过: {segments}")
    
    def test_extract_keywords(self):
        """测试关键词提取"""
        keywords = self.toolkit.extract_keywords(self.test_text, top_k=3)
        self.assertIsInstance(keywords, list)
        self.assertLessEqual(len(keywords), 3)
        print(f"关键词提取测试通过: {keywords}")
    
    def test_to_pinyin(self):
        """测试拼音转换"""
        pinyin = self.toolkit.to_pinyin("中文", style='normal')
        self.assertIsInstance(pinyin, str)
        self.assertGreater(len(pinyin), 0)
        print(f"拼音转换测试通过: {pinyin}")
    
    def test_convert_traditional(self):
        """测试简繁转换"""
        # 简转繁
        traditional = self.toolkit.convert_traditional("中文", direction='s2t')
        self.assertIsInstance(traditional, str)
        
        # 繁转简
        simplified = self.toolkit.convert_traditional(traditional, direction='t2s')
        self.assertIsInstance(simplified, str)
        
        print(f"简繁转换测试通过: 简->繁={traditional}, 繁->简={simplified}")
    
    def test_get_text_statistics(self):
        """测试文本统计"""
        stats = self.toolkit.get_text_statistics(self.test_text)
        self.assertIsInstance(stats, dict)
        self.assertIn('length', stats)
        self.assertIn('char_count', stats)
        print(f"文本统计测试通过: {stats}")
    
    def test_text_summary(self):
        """测试文本摘要"""
        long_text = self.test_text * 5
        summary = self.toolkit.text_summary(long_text, max_length=50)
        self.assertIsInstance(summary, str)
        self.assertLessEqual(len(summary), 53)  # 允许有省略号
        print(f"文本摘要测试通过: {summary}")
    
    def test_translate(self):
        """测试翻译"""
        # 测试本地翻译
        translated = self.toolkit.translate("你好", from_lang='zh', to_lang='en', engine='local')
        self.assertIsInstance(translated, str)
        print(f"本地翻译测试通过: 你好 -> {translated}")
        
        # 测试谷歌翻译（可能受网络影响）
        try:
            translated = self.toolkit.translate("世界", from_lang='zh', to_lang='en', engine='google')
            self.assertIsInstance(translated, str)
            print(f"谷歌翻译测试通过: 世界 -> {translated}")
        except Exception as e:
            print(f"谷歌翻译测试跳过（网络问题）: {e}")
    
    def test_cached_functions(self):
        """测试缓存功能"""
        # 测试带缓存的分词
        segments1 = self.toolkit._cached_segment(self.test_text, False, False)
        segments2 = self.toolkit._cached_segment(self.test_text, False, False)
        self.assertEqual(segments1, segments2)
        print("缓存分词测试通过")
        
        # 测试带缓存的翻译
        trans1 = self.toolkit._cached_translate("测试", 'zh', 'en', 'local')
        trans2 = self.toolkit._cached_translate("测试", 'zh', 'en', 'local')
        self.assertEqual(trans1, trans2)
        print("缓存翻译测试通过")

class TestChineseToolkitAdvanced(unittest.TestCase):
    """高级功能测试"""
    
    def setUp(self):
        self.toolkit = ChineseToolkit()
    
    def test_multiple_languages(self):
        """测试多语言支持"""
        test_cases = [
            ("中文测试", "zh"),
            ("English test", "en"),
            ("测试123", "mixed"),
            ("Hello 世界", "mixed")
        ]
        
        for text, expected_type in test_cases:
            stats = self.toolkit.get_text_statistics(text)
            print(f"多语言测试: '{text}' -> {stats}")
    
    def test_error_handling(self):
        """测试错误处理"""
        # 测试空文本
        segments = self.toolkit.segment("")
        self.assertEqual(segments, [])
        
        # 测试无效输入
        stats = self.toolkit.get_text_statistics("")
        self.assertEqual(stats['length'], 0)
        
        print("错误处理测试通过")

def run_tests():
    """运行所有测试"""
    print("🧪 开始运行OpenClaw中文工具包测试...")
    print("=" * 50)
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(TestChineseToolkit))
    suite.addTests(loader.loadTestsFromTestCase(TestChineseToolkitAdvanced))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("=" * 50)
    print(f"📊 测试结果:")
    print(f"  运行测试: {result.testsRun}")
    print(f"  失败: {len(result.failures)}")
    print(f"  错误: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("✅ 所有测试通过！")
        return 0
    else:
        print("❌ 测试失败！")
        return 1

if __name__ == '__main__':
    sys.exit(run_tests())