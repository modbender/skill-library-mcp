#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw中文工具包基础使用示例
"""

import sys
import os

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chinese_tools import ChineseToolkit

def main():
    """主函数"""
    print("🎯 OpenClaw中文工具包基础使用示例")
    print("=" * 50)
    
    # 初始化工具包
    print("🔧 初始化中文工具包...")
    toolkit = ChineseToolkit()
    
    # 示例文本
    sample_text = "今天天气真好，我们一起去公园散步吧。人工智能正在改变世界。"
    
    print(f"\n📝 示例文本: {sample_text}")
    print("=" * 50)
    
    # 1. 中文分词
    print("\n1. 📖 中文分词:")
    segments = toolkit.segment(sample_text)
    print(f"   分词结果: {' | '.join(segments)}")
    
    # 2. 关键词提取
    print("\n2. 🔑 关键词提取:")
    keywords = toolkit.extract_keywords(sample_text, top_k=5)
    print(f"   关键词: {', '.join(keywords)}")
    
    # 3. 拼音转换
    print("\n3. 🎵 拼音转换:")
    pinyin = toolkit.to_pinyin("中文工具包", style='tone')
    print(f"   拼音: {pinyin}")
    
    # 4. 简繁转换
    print("\n4. 🔄 简繁转换:")
    traditional = toolkit.convert_traditional("中文工具包", direction='s2t')
    simplified = toolkit.convert_traditional(traditional, direction='t2s')
    print(f"   简体→繁体: {traditional}")
    print(f"   繁体→简体: {simplified}")
    
    # 5. 文本统计
    print("\n5. 📊 文本统计:")
    stats = toolkit.get_text_statistics(sample_text)
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # 6. 文本摘要
    print("\n6. 📋 文本摘要:")
    summary = toolkit.text_summary(sample_text * 3, max_length=50)
    print(f"   摘要: {summary}")
    
    # 7. 翻译示例（需要配置API）
    print("\n7. 🌐 翻译示例:")
    test_text = "你好，世界"
    
    # 尝试百度翻译（需要配置API）
    translated = toolkit.translate(test_text, from_lang='zh', to_lang='en', engine='baidu')
    print(f"   百度翻译: {test_text} → {translated}")
    
    # 谷歌翻译
    translated = toolkit.translate(test_text, from_lang='zh', to_lang='en', engine='google')
    print(f"   谷歌翻译: {test_text} → {translated}")
    
    # 本地简单翻译
    translated = toolkit.translate(test_text, from_lang='zh', to_lang='en', engine='local')
    print(f"   本地翻译: {test_text} → {translated}")
    
    print("\n" + "=" * 50)
    print("✅ 示例运行完成！")
    print("\n💡 提示:")
    print("  - 配置百度翻译API以获得更好的翻译效果")
    print("  - 查看SKILL.md获取完整功能说明")
    print("  - 运行命令行工具: python chinese_tools.py --help")

if __name__ == '__main__':
    main()