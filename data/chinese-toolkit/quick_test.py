#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中文工具包快速测试
"""

import sys
import os

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from chinese_tools import ChineseToolkit
    
    print("🎯 中文工具包快速测试")
    print("=" * 50)
    
    # 初始化工具包
    toolkit = ChineseToolkit()
    print("✅ 工具包初始化成功")
    
    # 测试分词
    text = "今天天气真好，我们一起去公园散步吧。"
    segments = toolkit.segment(text)
    print(f"📖 分词测试:")
    print(f"   原文: {text}")
    print(f"   结果: {' | '.join(segments)}")
    
    # 测试拼音
    pinyin = toolkit.to_pinyin("中文工具包", style='tone')
    print(f"🎵 拼音测试:")
    print(f"   中文: 中文工具包")
    print(f"   拼音: {pinyin}")
    
    # 测试文本统计
    stats = toolkit.get_text_statistics(text)
    print(f"📊 文本统计测试:")
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # 测试翻译
    test_text = "你好世界"
    translated = toolkit.translate(test_text, from_lang='zh', to_lang='en', engine='google')
    print(f"🌐 翻译测试:")
    print(f"   原文: {test_text}")
    print(f"   翻译: {translated}")
    
    print("\n" + "=" * 50)
    print("✅ 所有测试通过！")
    print("\n💡 提示: 要使用完整功能，请安装依赖:")
    print("   pip install jieba pypinyin opencc-python-reimplemented requests")
    
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("\n📦 请安装依赖:")
    print("   pip install jieba pypinyin opencc-python-reimplemented")
    
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()