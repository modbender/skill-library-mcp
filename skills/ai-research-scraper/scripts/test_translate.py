#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from scraper import translate_text

def test_translation():
    # 测试翻译功能
    test_text = "This is a test sentence to translate to Chinese."
    result = translate_text(test_text)
    print(f"原文: {test_text}")
    print(f"译文: {result}")

test_translation()