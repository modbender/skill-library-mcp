#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from scraper import translate_text

def test_translation():
    # 测试翻译功能
    test_texts = [
        "AI enhances product development by speeding up innovation, reducing time-to-market, and lowering costs through data-driven insights and predictive analytics.",
        "AI-driven product development revolutionizes the process of creating digital solutions.",
        "Generative AI is changing how product teams operate."
    ]
    
    for text in test_texts:
        translated = translate_text(text)
        print(f"英文: {text}")
        print(f"中文: {translated}")
        print()

test_translation()