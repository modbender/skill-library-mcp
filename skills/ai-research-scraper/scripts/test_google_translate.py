#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import urllib.parse

def test_google_translate():
    text = "This is a test sentence to translate to Chinese."
    target_lang = "zh-CN"
    
    try:
        # 使用Google Cloud Translation API（免费版）
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl={target_lang}&dt=t&q={urllib.parse.quote(text)}"
        response = requests.get(url, timeout=30)
        data = response.json()
        
        # 提取翻译结果
        translated = "".join([item[0] for item in data[0]])
        print(f"原文: {text}")
        print(f"译文: {translated}")
    except Exception as e:
        print(f"翻译错误: {str(e)}")
        return text

test_google_translate()